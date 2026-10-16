#!/usr/bin/env python3
"""Safely stage exact Joey photo leads for future-card batch 005; no auto-publication."""
import hashlib,io,json
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
JOB=json.loads((ROOT/"workflow/photo-first-future-batch-005-20261016.json").read_text())
OUT=ROOT/"research-drafts/photo-imports/future-batch-005"
def fetch(url,limit=12000000):
    with urlopen(Request(url,headers={"User-Agent":"HaysBotanyResearchPhotoImporter/1.0"}),timeout=30) as res:
        data=res.read(limit+1)
    if len(data)>limit:raise ValueError("response oversized")
    return data
report={"status":"REVIEW_ONLY","records":[]}
for plant in JOB["selected"]:
    rec={"name":plant["scientific_name"],"slug":plant["slug"],"photos":[]}
    for lead in plant["joey_candidates"]:
        p={"id":lead["photo_id"],"observation_id":lead["observation_id"],"status":"BLOCKED"}
        try:
            obs=json.loads(fetch("https://api.inaturalist.org/v1/observations/"+lead["observation_id"],2000000))["results"][0]
            ph=next(x for x in obs.get("photos",[]) if str(x["id"])==lead["photo_id"])
            if (obs.get("taxon") or {}).get("name")!=plant["scientific_name"]:raise ValueError("observation name mismatch")
            if obs.get("quality_grade")!="research":raise ValueError("observation is not research grade")
            if (ph.get("license_code") or "").lower()!="cc-by-nc":raise ValueError("photo license mismatch")
            if "joey santore" not in (ph.get("attribution") or "").lower():raise ValueError("photo attribution mismatch")
            url=(ph.get("url") or "")
            for sz in ("square","thumb","small","medium"):url=url.replace("/"+sz+".","/large.")
            if not url.startswith("https://"):raise ValueError("invalid photo url")
            binary=fetch(url)
            with Image.open(io.BytesIO(binary)) as im: im.verify()
            im=Image.open(io.BytesIO(binary)).convert("RGB")
            if min(im.size)<300:raise ValueError("image under 300px")
            path=OUT/plant["slug"]/("joey-"+lead["photo_id"]+".jpg")
            path.parent.mkdir(parents=True,exist_ok=True)
            im.save(path,quality=87,optimize=True)
            p.update(status="STAGED_PENDING_BOTANICAL_REVIEW",file=str(path.relative_to(ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),creator="Joey Santore",license="CC BY-NC",source_page=lead["photo_page"])
        except Exception as err:p["reason"]=str(err)[:200]
        rec["photos"].append(p)
    report["records"].append(rec)
OUT.mkdir(parents=True,exist_ok=True)
(OUT/"report.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({"staged":sum(x["status"].startswith("STAGED") for r in report["records"] for x in r["photos"]),"blocked":sum(x["status"]=="BLOCKED" for r in report["records"] for x in r["photos"])}))
