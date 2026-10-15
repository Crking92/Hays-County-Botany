#!/usr/bin/env python3
"""Install next five candidate learner cards from owner-owned iNaturalist observations."""
import csv
import json
import shutil
import subprocess
import sys
import io
import hashlib
from urllib.request import Request, urlopen
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/"research-drafts/photo-imports/pilot-20261015-b003/import-report.json"
MANIFEST=ROOT/"data/manifest.json"
CLAIMS=ROOT/"workflow/work-claims.json"
BATCH=ROOT/"curation-inbox/photo-first-five-20261015-b003"
DEFINITIONS={
"erioneuron-pilosum":("Poaceae","Erioneuron","pilosum","Hairy tridens","A small tufted grass; examine the hairy spikelets, inflorescence branches and ligule to distinguish it from related shortgrasses."),
"gymnosperma-glutinosum":("Asteraceae","Gymnosperma","glutinosum","Tatalencho","Shrubby composite with sticky, resinous vegetation and small yellow flower heads; examine leaves and head structure."),
"melampodium-leucanthum":("Asteraceae","Melampodium","leucanthum","Blackfoot daisy","Low perennial with white ray florets surrounding yellow disc florets; check leaf arrangement and phyllaries."),
"zephyranthes-chlorosolen":("Amaryllidaceae","Zephyranthes","chlorosolen","Rain lily","Bulbous plant with narrow basal leaves and a pale trumpet-shaped flower on a leafless stalk; inspect floral tube and stamens."),
"euploca-tenella":("Boraginaceae","Euploca","tenella","Slender heliotrope","Small herb with tiny flowers and narrow foliage; check inflorescence form and fruit structures.")
}
OBSERVATIONS={
"erioneuron-pilosum":"352421299",
"gymnosperma-glutinosum":"259795546",
"melampodium-leucanthum":"377808107",
"zephyranthes-chlorosolen":"294883355",
"euploca-tenella":"365253933"
}

def download_candidates():
    if REPORT.exists():
        data=json.loads(REPORT.read_text())
        return data
    result={"date":"2026-10-15","records":[],"rights":"owner-owned images for private-study-only"}
    for slug, obsid in OBSERVATIONS.items():
        item={"slug":slug,"scientific_name":DEFINITIONS[slug][1]+" "+DEFINITIONS[slug][2],"photos":[]}
        try:
            url="https://api.inaturalist.org/v1/observations/"+obsid
            raw=urlopen(Request(url,headers={"User-Agent":"HaysBotanyPilotImporter/1.0"}),timeout=30).read(2000000)
            obs=json.loads(raw)["results"][0]
            if (obs.get("user") or {}).get("login","").lower()!="calvinking":
                raise ValueError("observation not owned by intended photographer")
            if (obs.get("taxon") or {}).get("name")!=item["scientific_name"]:
                raise ValueError("observation scientific identity mismatch")
            photos=obs.get("photos") or []
            if not photos:raise ValueError("no iNaturalist photo present")
            ph=photos[0]
            photoid=str(ph["id"])
            direct=(ph.get("url") or "").replace("/square.","/large.").replace("/thumb.","/large.").replace("/small.","/large.").replace("/medium.","/large.")
            if not direct.startswith("https://"):raise ValueError("no safe photo HTTPS source")
            image_bytes=urlopen(Request(direct,headers={"User-Agent":"HaysBotanyPilotImporter/1.0"}),timeout=30).read(12000001)
            if len(image_bytes)>12000000:raise ValueError("image too large")
            picture=Image.open(io.BytesIO(image_bytes));picture.verify()
            picture=Image.open(io.BytesIO(image_bytes)).convert("RGB")
            if min(picture.size)<300:raise ValueError("image too small")
            out=REPORT.parent/slug/("inat-"+photoid+".jpg")
            out.parent.mkdir(parents=True,exist_ok=True)
            picture.save(out,quality=88,optimize=True)
            item["photos"].append({"status":"downloaded_pending_visual_review","file":str(out.relative_to(ROOT)),"attribution":"(c) Calvin King, all rights reserved","observation_url":"https://www.inaturalist.org/observations/"+obsid,"photo_url":"https://www.inaturalist.org/photos/"+photoid,"image_source":direct,"license_code":ph.get("license_code") or "unspecified","sha256":hashlib.sha256(out.read_bytes()).hexdigest()})
        except Exception as exc:
            item["blocker"]=str(exc)[:250]
        result["records"].append(item)
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(result,indent=2)+"\\n")
    return result

def main():
    report=download_candidates()
    existing={x["id"] for x in json.loads(MANIFEST.read_text())["species"]}
    claims=json.loads(CLAIMS.read_text()).get("claims",[])
    busy=set()
    for claim in claims:
        if claim.get("status")=="active":busy.update(claim.get("taxa") or [])
    if BATCH.exists():
        raise RuntimeError("Existing batch folder: refusing overwrite")
    prepared=[]
    blocked=[]
    for record in report["records"]:
        taxon=record["slug"]
        if taxon in existing or taxon in busy:
            blocked.append({"taxon":taxon,"reason":"existing canonical or active claim"})
            continue
        meta=DEFINITIONS.get(taxon)
        if not meta or record["scientific_name"]!=f"{meta[1]} {meta[2]}":
            blocked.append({"taxon":taxon,"reason":"identity mismatch"})
            continue
        candidates=[x for x in record["photos"] if x.get("status")=="downloaded_pending_visual_review" and x.get("attribution","").startswith("(c) Calvin King")]
        if not candidates:
            blocked.append({"taxon":taxon,"reason":"no physically downloaded user-owned photo"})
            continue
        photo=candidates[0]
        source=ROOT/photo["file"]
        if not source.is_file():
            blocked.append({"taxon":taxon,"reason":"downloaded photo missing"})
            continue
        with Image.open(source) as im:
            im.verify()
        family,genus,epithet,common,recognition=meta
        folder=BATCH/"taxa"/family/genus/taxon
        folder.mkdir(parents=True,exist_ok=True)
        (folder/"images").mkdir()
        dest=folder/"images"/source.name
        shutil.copy2(source,dest)
        species={"id":taxon,"entry_type":"species","family":family,"genus":genus,"species":epithet,
                 "scientific_name":record["scientific_name"],"common_name":common,
                 "look_here_first":recognition,
                 "curation_status":{"taxonomy_reviewed":False,"morphology_reviewed":False,"visual_reviewed":False,"user_approved":True,"visual_status":"provisional_one_photo_pending_diagnostic_review"},
                 "project_inclusion":{"range_status":"deferred","source":"approved Master Plant Pool"},
                 "photo_note":"Personal private-study image; taxon shown follows original iNaturalist observation identification. Detailed diagnostic image review pending."}
        (folder/"species.json").write_text(json.dumps(species,indent=2)+"\n")
        (folder/"SOURCES.txt").write_text("Source: approved Master Plant Pool (learner inclusion only).\nObservation: "+photo["observation_url"]+"\nPhoto: "+photo["photo_url"]+"\nOriginal identification requires deeper review; county native status not asserted.\n")
        with (folder/"image-sources.csv").open("w",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=["file_name","role","creator","license","source_page","direct_url","study_use","public_reuse"])
            writer.writeheader()
            writer.writerow({"file_name":source.name,"role":"Provisional recognition/whole plant photo — diagnostic review pending",
                             "creator":"Calvin King","license":"All rights reserved — owner-authorized private study",
                             "source_page":photo["photo_url"],"direct_url":photo["image_source"],
                             "study_use":"private only","public_reuse":"no"})
        prepared.append(taxon)
    if not prepared:
        raise RuntimeError("No eligible photo-backed plants available")
    (BATCH/"batch.json").write_text(json.dumps({"batch_id":BATCH.name,"mode":"install","require_exact_images":True,"visual_mode":"learner_fast_fill"},indent=2)+"\n")
    (BATCH/"READY").write_text("Complete private-study pilot package; image bytes copied locally and verified.\n")
    subprocess.run([sys.executable,str(ROOT/"scripts/curation_pipeline.py"),"--apply"],cwd=ROOT,check=True)
    updated={x["id"] for x in json.loads(MANIFEST.read_text())["species"]}
    missing=set(prepared)-updated
    if missing:raise RuntimeError(f"Installed cards missing from manifest: {sorted(missing)}")
    for name in prepared:
        matches=list((ROOT/"content/taxa").glob(f"*/*/{name}/species.json"))
        if len(matches)!=1:raise RuntimeError(f"{name} not uniquely canonical")
        meta=json.loads(matches[0].read_text())
        local=matches[0].parent/meta["images"][0]["file"]
        with Image.open(local) as im:im.verify()
    result={"installed":prepared,"blocked":blocked,"previous_manifest_count":len(existing),"new_manifest_count":len(updated),
            "media_rights":"PRIVATE STUDY ONLY — do not republish photos without owner permission",
            "visual_status":"provisional unreviewed; keep deeper taxonomy/diagnostic checks separate"}
    target=ROOT/"reports/photo-first-five-install-20261015-b003.json"
    target.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result))
if __name__=="__main__":main()
