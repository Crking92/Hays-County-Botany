#!/usr/bin/env python3
"""Install five provisional future learner cards from physically staged Joey photos."""
import csv,json,hashlib,shutil,subprocess,sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/"research-drafts/photo-imports/future-batch-004/report.json"
MANIFEST=ROOT/"data/manifest.json"
BATCH=ROOT/"curation-inbox/photo-first-future-004-20261016"
DEFINITIONS={"linaria-texana":("Plantaginaceae","Linaria","texana","Texas toadflax","Small upright herb with narrow leaves and spurred two-lipped flowers; inspect spur and calyx."),"paspalum-dilatatum":("Poaceae","Paspalum","dilatatum","Dallisgrass","Coarse grass with racemose spikelet branches; compare spikelets, sheaths and ligules."),"lindera-benzoin":("Lauraceae","Lindera","benzoin","Spicebush","Aromatic shrub with alternate simple leaves and clustered flowers; examine buds, leaf texture, and berries."),"schoenocaulon-texanum":("Melanthiaceae","Schoenocaulon","texanum","Texas feather-shank","Basal narrow leaves and upright spike of inconspicuous flowers; inspect inflorescence and flower parts."),"zephyranthes-drummondii":("Amaryllidaceae","Zephyranthes","drummondii","Drummond's rain-lily","Narrow basal leaves, solitary pale trumpetlike flower and long floral tube; inspect stamens and capsule.")}

def main():
    report=json.loads(INPUT.read_text())
    installed={x["id"] for x in json.loads(MANIFEST.read_text())["species"]}
    claims=json.loads((ROOT/"workflow/work-claims.json").read_text()).get("claims",[])
    active=set()
    for c in claims:
        if c.get("status")=="active":active.update(c.get("taxa") or [])
    if BATCH.exists():raise RuntimeError("Batch already exists; refusing overwrite")
    selected=[]
    for record in report["records"]:
        slug=record["slug"]
        if slug in installed or slug in active:continue
        family,genus,epithet,common,clue=DEFINITIONS[slug]
        if record["name"]!=f"{genus} {epithet}":raise ValueError("name mismatch")
        photos=[p for p in record["photos"] if p.get("status")=="STAGED_PENDING_BOTANICAL_REVIEW" and p.get("license")=="CC BY-NC"]
        if not photos:continue
        folder=BATCH/"taxa"/family/genus/slug
        (folder/"images").mkdir(parents=True,exist_ok=True)
        rows=[]
        for photo in photos:
            src=ROOT/photo["file"]
            if not src.exists() or hashlib.sha256(src.read_bytes()).hexdigest()!=photo["sha256"]:
                raise ValueError("Missing/corrupt staged image for "+slug)
            with Image.open(src) as im:im.verify()
            dest=folder/"images"/src.name
            shutil.copy2(src,dest)
            rows.append(dict(file_name=src.name,role="Provisional species recognition image; image-part diagnosis not yet reviewed",creator="Joey Santore",license="CC BY-NC",source_page=photo["source_page"],direct_url="https://inaturalist-open-data.s3.amazonaws.com/photos/"+str(photo["id"])+"/large.jpeg",study_use="Noncommercial botanical education",public_reuse="CC BY-NC only"))
        obj={"id":slug,"family":family,"genus":genus,"species":epithet,"scientific_name":record["name"],"common_name":common,"look_here_first":clue,"curation_status":{"visual_reviewed":False,"taxonomy_reviewed":False,"photo_source_checked":True},"photo_note":"Exact iNaturalist observation attribution/licensing verified; botanically diagnostic photo review pending."}
        (folder/"species.json").write_text(json.dumps(obj,indent=2)+"\n")
        (folder/"SOURCES.txt").write_text("Species ID from original iNaturalist research-grade observations; requires deeper botanical review.\nPhoto credit Joey Santore; CC BY-NC license; noncommercial use only.\n")
        with (folder/"image-sources.csv").open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
        selected.append(slug)
    if not selected:raise RuntimeError("No eligible species available")
    (BATCH/"batch.json").write_text(json.dumps({"batch_id":BATCH.name,"mode":"install","require_exact_images":True,"visual_mode":"learner_fast_fill"},indent=2)+"\n")
    (BATCH/"READY").write_text("Physically staged photo files and provenance verified; provisional learner coverage.\n")
    subprocess.run([sys.executable,str(ROOT/"scripts/curation_pipeline.py"),"--apply"],cwd=ROOT,check=True)
    canonical={x["id"]:ROOT/x["path"] for x in json.loads(MANIFEST.read_text())["species"]}
    for slug in selected:
        if slug not in canonical:raise ValueError("Missing new manifest entry "+slug)
        sp=json.loads(canonical[slug].read_text())
        for x in sp.get("images",[]):
            with Image.open(canonical[slug].parent/x["file"]) as im:im.verify()
    dest=ROOT/"reports/photo-first-future-batch-004-installed.json"
    dest.write_text(json.dumps({"installed":selected,"manifest_count":len(canonical),"note":"Photos provisional; original photographer and CC BY-NC preserved. Detailed diagnostic review remains pending."},indent=2)+"\n")
    print(dest.read_text())
if __name__=="__main__":main()
