#!/usr/bin/env python3
"""Retrieve exact, research-grade, CC BY-NC Joey photos for first cards in approved master pool."""
import csv, hashlib, io, json
from pathlib import Path
from urllib.request import Request, urlopen
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
JOB=json.loads((ROOT/"workflow/untouched-first-card-008-20261016.json").read_text())
OUT=ROOT/"research-drafts/photo-imports/untouched-first-card-008"
INVENTORY=ROOT/"workflow/joey-texas-inat-photo-inventory/photo-candidates.csv"
def fetch(url,limit=12000000):
    with urlopen(Request(url,headers={"User-Agent":"HaysBotanyLearnerPhotoImporter/1.0"}),timeout=35) as response:
        b=response.read(limit+1)
    if len(b)>limit:raise ValueError("oversized")
    return b
def main():
    available={}
    with INVENTORY.open(newline="",encoding="utf-8-sig") as f:
        for p in csv.DictReader(f):
            if p.get("quality_grade")!="research":continue
            if (p.get("source_license") or "").lower()!="cc-by-nc":continue
            if "joey santore" not in (p.get("source_attribution") or "").lower():continue
            available.setdefault(p["scientific_name"],[]).append(p)
    preflight={p["name"]:p["slug"] for b in json.loads((ROOT/"workflow/INSTALLER_PREFLIGHT_QUEUE_2026-10-15.json").read_text())["batches"] for p in b["taxa"]}
    ids={x["id"] for x in json.loads((ROOT/"data/manifest.json").read_text())["species"]}
    claims=json.loads((ROOT/"workflow/work-claims.json").read_text()).get("claims",[])
    active={x for c in claims if c.get("status")=="active" for x in c.get("taxa",[])}
    observations={}
    report={"status":"STAGING_COMPLETE","records":[]}
    for plant in JOB["selected"]:
        name,slug=plant["name"],plant["slug"]
        record={"name":name,"slug":slug,"photos":[],"status":"PENDING"}
        report["records"].append(record)
        if preflight.get(name)!=slug or slug in ids or slug in active:
            record["status"]="SKIP_NOT_ELIGIBLE_OR_ALREADY_CLAIMED";continue
        leads=available.get(name,[])
        for lead in leads[:14]:
            if sum(x["status"]=="STAGED_PENDING_BOTANICAL_REVIEW" for x in record["photos"])>=2:break
            photo_id,obs_id=str(lead["photo_id"]),str(lead["observation_id"])
            p={"id":photo_id,"observation_id":obs_id,"status":"BLOCKED"}
            record["photos"].append(p)
            try:
                if obs_id not in observations:
                    found=json.loads(fetch("https://api.inaturalist.org/v1/observations/"+obs_id,1700000))["results"]
                    observations[obs_id]=found[0] if found else None
                obs=observations[obs_id]
                if not obs:raise ValueError("missing observation")
                if (obs.get("taxon") or {}).get("name")!=name:raise ValueError("exact live taxon mismatch")
                if obs.get("quality_grade")!="research":raise ValueError("not research grade")
                ph=next(x for x in obs.get("photos",[]) if str(x["id"])==photo_id)
                if (ph.get("license_code") or "").lower()!="cc-by-nc":raise ValueError("license mismatch")
                if "joey santore" not in (ph.get("attribution") or "").lower():raise ValueError("photographer mismatch")
                url=ph.get("url") or ""
                for size in ("square","thumb","small","medium"):url=url.replace("/"+size+".","/large.")
                if not url.startswith("https://"):raise ValueError("invalid image URL")
                data=fetch(url)
                with Image.open(io.BytesIO(data)) as im:im.verify()
                with Image.open(io.BytesIO(data)) as im:
                    im=im.convert("RGB")
                    if min(im.size)<300:raise ValueError("image under 300px")
                    path=OUT/slug/("joey-"+photo_id+".jpg")
                    path.parent.mkdir(parents=True,exist_ok=True)
                    im.save(path,quality=87,optimize=True)
                p.update(status="STAGED_PENDING_BOTANICAL_REVIEW",file=str(path.relative_to(ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),creator="Joey Santore",license="CC BY-NC",source_page=lead["photo_url"],direct_url=url)
            except Exception as e:p["reason"]=str(e)[:180]
        record["status"]="STAGED" if any(x["status"]=="STAGED_PENDING_BOTANICAL_REVIEW" for x in record["photos"]) else "BLOCKED_NO_VERIFIED_PHOTO"
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"species_staged":sum(x["status"]=="STAGED" for x in report["records"]),"photos_staged":sum(p["status"]=="STAGED_PENDING_BOTANICAL_REVIEW" for x in report["records"] for p in x["photos"]),"blocked_species":sum(x["status"]=="BLOCKED_NO_VERIFIED_PHOTO" for x in report["records"])}))
if __name__=="__main__":main()
