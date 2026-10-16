#!/usr/bin/env python3
"""First-time Master Pool cards using license-verified research-grade iNaturalist photos.
Not a visual/diagnostic identification certification. Does not rely on Joey's inventory.
"""
import csv
import hashlib
import io
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
PLAN=ROOT/"workflow/master-pool-multisource-016-20261016.json"
MANIFEST=ROOT/"data/manifest.json"
PREFLIGHT=ROOT/"research-drafts/reconciliation/phase3-consolidated-card-workload-2026-10-15.json"
CLAIMS=ROOT/"workflow/work-claims.json"
STAGING=ROOT/"research-drafts/photo-imports/master-pool-multisource-016"
BATCH=ROOT/"curation-inbox/master-pool-multisource-016-20261016"
OUTPUT=ROOT/"reports/master-pool-multisource-016-installed.json"
ALLOWED={
 "cc0":("CC0","Public domain dedication; verify attribution"),
 "cc-by":("CC BY","Attribution required"),
 "cc-by-sa":("CC BY-SA","Attribution; ShareAlike requirements"),
 "cc-by-nc":("CC BY-NC","Attribution; noncommercial only"),
 "cc-by-nc-sa":("CC BY-NC-SA","Attribution; noncommercial and ShareAlike requirements")
}
UA={"User-Agent":"HaysBotanyPrivateEducationalFirstCard/1.0 (science photo curation)"}

def request(url, limit=3500000):
    last=None
    for attempt in range(3):
        try:
            with urlopen(Request(url,headers=UA),timeout=30) as rs:
                data=rs.read(limit+1)
            if len(data)>limit:raise ValueError("oversized response")
            return data
        except (HTTPError,URLError,TimeoutError) as e:
            last=e
            if isinstance(e,HTTPError) and e.code not in (429,500,502,503,504):
                raise
            time.sleep(2.5*(attempt+1))
    raise last

def api(route, params=None):
    url="https://api.inaturalist.org/v1/"+route
    if params:url+="?"+urlencode(params)
    return json.loads(request(url,5500000))

def exact_species_taxon(name):
    data=api("taxa/autocomplete",{"q":name,"per_page":20}).get("results",[])
    hits=[x for x in data if x.get("name")==name and x.get("rank")=="species"]
    if len(hits)!=1:raise ValueError("No unique exact accepted-rank species in live iNaturalist taxonomy")
    return hits[0]["id"]

def license_photo(name, taxon_id, issues):
    checked=0
    for page in (1,2,3,4):
        observations=api("observations",{
           "taxon_id":taxon_id,"quality_grade":"research",
           "photos":"true","per_page":12,"page":page,
           "order_by":"votes","order":"desc"
        }).get("results",[])
        if not observations:break
        for obs in observations:
            if (obs.get("taxon") or {}).get("name")!=name:continue
            if obs.get("quality_grade")!="research":continue
            for photo in obs.get("photos") or []:
                checked+=1
                code=(photo.get("license_code") or "").lower()
                if code not in ALLOWED:continue
                credit=photo.get("attribution") or ""
                if not credit or ("rights reserved" in credit.lower() and "some rights reserved" not in credit.lower()):
                    continue
                url=photo.get("url") or ""
                for sz in ("square","thumb","small","medium"):
                    url=url.replace("/"+sz+".","/large.")
                if not url.startswith("https://"):continue
                try:
                    imgbytes=request(url,12000000)
                    with Image.open(io.BytesIO(imgbytes)) as im:im.verify()
                    with Image.open(io.BytesIO(imgbytes)) as im:
                        if min(im.size)<350:raise ValueError("image below 350px")
                        resized=im.convert("RGB")
                        resized.thumbnail((1800,1800))
                        b=io.BytesIO()
                        resized.save(b,format="JPEG",quality=87,optimize=True)
                        payload=b.getvalue()
                    pid=str(photo["id"])
                    return {
                      "bytes":payload,"photo_id":pid,
                      "observation_id":str(obs["id"]),
                      "attribution":credit,"license_code":code,
                      "image_url":url,
                      "source_page":"https://www.inaturalist.org/photos/"+pid,
                      "observation_page":"https://www.inaturalist.org/observations/"+str(obs["id"]),
                      "width":resized.width,"height":resized.height,
                      "checked_candidates":checked
                    }
                except Exception as e:
                    issues.append("image "+str(photo.get("id"))+": "+str(e)[:130])
                if checked>=100:break
            if checked>=100:break
        if checked>=100:break
    return None

def read_state():
    manifest=json.loads(MANIFEST.read_text())
    canonical={e["id"] for e in manifest["species"]}
    active=set()
    for claim in json.loads(CLAIMS.read_text()).get("claims",[]):
        if claim.get("status")=="active":
            active.update(claim.get("taxa") or [])
    queued={x.get("id") for x in json.loads((ROOT/"research-queue.json").read_text()).get("items",[]) if x.get("status") in ("taxonomy_hold","identity_hold","held_identity","pending_taxon_concept")}
    return canonical,active,queued

def build():
    plan=json.loads(PLAN.read_text())
    allowed={p["accepted_working_name"]:{"slug":p["slug"],"caution":None} for p in json.loads(PREFLIGHT.read_text())["concepts"] if "phase2_preflight" in p.get("origins",[]) and "PREFLIGHT" in p.get("decisions",[])}
    installed,active,queued=read_state()
    if BATCH.exists() or OUTPUT.exists():raise RuntimeError("Batch or report exists, refusing overwrite")
    results=[]
    prepared=[]
    for item in plan["selected"]:
        name,slug=item["scientific_name"],item["slug"]
        result={"name":name,"slug":slug,"status":"PENDING","attempts":[]}
        results.append(result)
        if allowed.get(name,{}).get("slug")!=slug or allowed[name].get("caution"):
            result["status"]="HOLD_NOT_PREFLIGHT_CLEARED";continue
        if slug in installed or slug in active or slug in queued:
            result["status"]="SKIP_INSTALLED_CLAIMED_OR_HELD";continue
        if name!=item["genus"]+" "+item["epithet"] or slug!=name.lower().replace(" ","-"):
            result["status"]="HOLD_IDENTITY_OR_SLUG";continue
        try:
            tid=exact_species_taxon(name)
            result["iNaturalist_taxon_id"]=tid
            p=license_photo(name,tid,result["attempts"])
            if not p:
                result["status"]="NEEDS_FIRST_PHOTO";continue
            path=STAGING/slug/("inat-"+p["photo_id"]+".jpg")
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(p["bytes"])
            digest=hashlib.sha256(path.read_bytes()).hexdigest()
            with Image.open(path) as im:im.verify()
            result.update(photo_id=p["photo_id"],observation_id=p["observation_id"],source_page=p["source_page"],
                          license_code=p["license_code"],credit=p["attribution"],sha256=digest,width=p["width"],height=p["height"])
            folder=BATCH/"taxa"/item["family"]/item["genus"]/slug
            (folder/"images").mkdir(parents=True,exist_ok=True)
            shutil.copy2(path,folder/"images"/path.name)
            status=ALLOWED[p["license_code"]]
            row={
                "file_name":path.name,"role":"Provisional species recognition photograph; diagnostic anatomy not visually certified",
                "creator":p["attribution"],"license":status[0],"source_page":p["source_page"],
                "direct_url":p["image_url"],"study_use":"Noncommercial botanical education",
                "public_reuse":status[1],
                "observation_id":p["observation_id"],"photo_id":p["photo_id"],
            }
            with (folder/"image-sources.csv").open("w",newline="",encoding="utf-8") as f:
                w=csv.DictWriter(f,fieldnames=list(row))
                w.writeheader();w.writerow(row)
            species={
                "id":slug,"family":item["family"],"genus":item["genus"],"species":item["epithet"],
                "scientific_name":name,"common_name":item["common_name"],
                "look_here_first":item["look_here_first"],
                "curation_status":{"taxonomy_reviewed":False,"visual_reviewed":False,"photo_source_checked":True},
                "photo_note":"iNaturalist research-grade exact species observation; photo license and bytes confirmed. Independent image-anatomy review still pending.",
                "taxonomy_source":item["taxonomy_source"],
            }
            (folder/"species.json").write_text(json.dumps(species,indent=2)+"\n")
            (folder/"SOURCES.txt").write_text(
                "Approved Master Plant Pool preflight; accepted species: "+item["taxonomy_source"]+
                "\nSource research-grade observation: "+p["observation_page"]+
                "\nPhoto: "+p["source_page"]+
                "\nAttribution: "+p["attribution"]+
                "\nLicense: "+status[0]+"; "+status[1]+
                "\nDiagnostic photo appearance and look-alikes: further visual review required. Native county research deferred.\n"
            )
            result["status"]="PREPARED"
            prepared.append(slug)
        except Exception as e:
            result["status"]="NEEDS_FIRST_PHOTO_OR_SOURCE_CHECK"
            result["attempts"].append(str(e)[:250])
    STAGING.mkdir(parents=True,exist_ok=True)
    (STAGING/"stage-report.json").write_text(json.dumps({"batch":plan["batch_id"],"results":results},indent=2)+"\n")
    if prepared:
        (BATCH/"batch.json").write_text(json.dumps({"batch_id":BATCH.name,"mode":"install","require_exact_images":True,"visual_mode":"learner_fast_fill"},indent=2)+"\n")
        (BATCH/"READY").write_text("First photo physically saved and exact species & license checked; provisional diagnostic review.\n")
        subprocess.run([sys.executable,str(ROOT/"scripts/curation_pipeline.py"),"--apply"],cwd=ROOT,check=True)
    current={x["id"]:x for x in json.loads(MANIFEST.read_text())["species"]}
    verified=[]
    for slug in prepared:
        item=current.get(slug)
        if item is None:raise ValueError("Prepared species absent from canonical manifest: "+slug)
        spath=ROOT/item["path"]
        obj=json.loads(spath.read_text())
        imgs=obj.get("images") or []
        if len(imgs)<1:raise ValueError("New card missing physical image: "+slug)
        for img in imgs:
            path=spath.parent/img["file"]
            with Image.open(path) as im:im.verify()
        next(x for x in results if x["slug"]==slug)["status"]="INSTALLED"
        verified.append(slug)
    report={"batch":plan["batch_id"],"starting_count":len(installed),"manifest_count":len(current),
            "installed_count":len(verified),"installed":verified,"physically_installed_photos":len(verified),
            "blocked":[x for x in results if x["status"]!="INSTALLED"],
            "all_results":results,
            "note":"Physical photo and photo-specific license checked; source observation research grade and exact name. Photos provisional, independent anatomical review pending. County native-range research deferred."}
    OUTPUT.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"installed":verified,"manifest_count":len(current),"blocked_count":len(report["blocked"])}))
if __name__=="__main__":
    build()
