#!/usr/bin/env python3
"""Install five already downloaded, user-owned pilot photographs using existing curation pipeline."""
import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/"research-drafts/photo-imports/pilot-20261015/import-report.json"
MANIFEST=ROOT/"data/manifest.json"
CLAIMS=ROOT/"workflow/work-claims.json"
BATCH=ROOT/"curation-inbox/photo-first-five-20261015"
DEFINITIONS={
"palafoxia-callosa":("Asteraceae","Palafoxia","callosa","Small palafoxia","Look for slender branching stems and small pink-to-lavender heads with narrow ray-like outer florets; examine mature leaves and involucral bracts to separate related palafoxias."),
"phacelia-congesta":("Boraginaceae","Phacelia","congesta","Blue-curls","Check the strongly coiled scorpioid flower clusters and small blue-violet flowers; watch the arrangement of stamens and hairy foliage."),
"condalia-hookeri":("Rhamnaceae","Condalia","hookeri","Brasil / bluewood condalia","Woody shrub or small tree with stiff branchlets, small leaves and dark drupes; examine branching, armature and fruits against related Condalia and Ziziphus."),
"rhynchosia-senna":("Fabaceae","Rhynchosia","senna","Texas snoutbean","Check the three leaflets, papilionaceous yellow flowers and small legumes; compare leaflet shapes and fruit traits with other Rhynchosia."),
"hymenopappus-scabiosaeus":("Asteraceae","Hymenopappus","scabiosaeus","Carolina woollywhite","Look for divided leaves and flower heads dominated by tubular disc florets; inspect phyllaries, leaf segments and head arrangement to avoid confusion with similar composites.")
}
def main():
    report=json.loads(REPORT.read_text())
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
    target=ROOT/"reports/photo-first-five-install-20261015.json"
    target.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result))
if __name__=="__main__":main()
