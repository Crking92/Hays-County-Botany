#!/usr/bin/env python3
"""Install already validated Joey Santore photos as provisional supplementary galleries."""
import json,shutil,hashlib
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/"research-drafts/photo-imports/joey-batch003/import-report.json"
MANIFEST=ROOT/"data/manifest.json"
OUT=ROOT/"reports/joey-batch003-gallery-enrichment.json"
index={x["id"]:ROOT/x["path"] for x in json.loads(MANIFEST.read_text())["species"]}
results=[]
for rec in json.loads(REPORT.read_text())["records"]:
    slug=rec["name"].lower().replace(" ","-")
    good=[x for x in rec["photos"] if x.get("status")=="downloaded_pending_visual_review" and x.get("license")=="cc-by-nc" and "Joey Santore" in (x.get("photographer") or "")]
    result={"species":slug,"added":[],"held":[]}
    if slug not in index:
        result["held"].append("Species not in canonical manifest")
        results.append(result);continue
    specpath=index[slug]
    species=json.loads(specpath.read_text())
    imgs=species.setdefault("images",[])
    existing={str(x.get("photo_id") or "") for x in imgs}
    for p in good:
        photo_id=str(p["photo_id"])
        if photo_id in existing:
            result["held"].append("Duplicate photo "+photo_id)
            continue
        src=ROOT/p["file"]
        if not src.is_file():
            result["held"].append("Missing photo "+photo_id)
            continue
        if hashlib.sha256(src.read_bytes()).hexdigest()!=p["sha256"]:
            result["held"].append("Checksum mismatch "+photo_id)
            continue
        with Image.open(src) as im:im.verify()
        dest=specpath.parent/"images"/src.name
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(src,dest)
        imgs.append({"file":"images/"+src.name,"role":"Provisional complementary diagnostic view — requires visual botanical curation",
                     "photo_id":photo_id,"creator":"Joey Santore","license":"CC BY-NC 4.0",
                     "source_page":p["source_page"],"study_use":"noncommercial educational study",
                     "public_reuse":"noncommercial only; attribution required",
                     "review_status":"taxon and metadata checked; image diagnostic quality pending"})
        result["added"].append(photo_id)
    if result["added"]:
        status=species.setdefault("curation_status",{})
        status["photo_metadata_count"]=len(imgs)
        status["photo_files_present"]=sum((specpath.parent/x.get("file","")).is_file() for x in imgs)
        species["photo_note"]="Calvin King private-study photos plus Joey Santore CC BY-NC supplementary photos; diagnostic photo review pending."
        specpath.write_text(json.dumps(species,indent=2)+"\n")
    results.append(result)
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps({"results":results,"added_total":sum(len(r["added"]) for r in results),"note":"Rights checked from iNaturalist metadata; supplemental photos provisional pending human botanical assessment."},indent=2)+"\n")
print(OUT.read_text())
