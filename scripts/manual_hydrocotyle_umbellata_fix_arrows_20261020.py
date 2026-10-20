#!/usr/bin/env python3
"""Regenerate only one reviewed CC BY Hydrocotyle photo to correct both actual arrow
targets; verify original upstream hash and retain all other original JPEGs unchanged."""
import runpy,json,csv
from pathlib import Path
ROOT=Path("content/taxa/Araliaceae/Hydrocotyle/hydrocotyle-umbellata")
FILE=ROOT/"species.json"
card=json.loads(FILE.read_text())
assert card["id"]=="hydrocotyle-umbellata" and len(card["images"])==6
name="sam-633285519-leaf-and-head-arrows.jpg"
entry=next(x for x in card["images"] if x["file"]=="images/"+name)
if entry.get("manual_arrow_review")=="2026-10-20-corrected-visual-readback":
 print("already corrected");raise SystemExit(0)
source=json.loads(Path("workflow/photo-library/reviews/hydrocotyle-umbellata-20261020/candidate-screen.json").read_text())
photo=next(x for x in source["candidates"] if str(x["photo_id"])=="633285519")
module=runpy.run_path("scripts/manual_hydrocotyle_umbellata_finished_photos_20261020.py")
corrected=[
 ("Scalloped leaf edge",(.770,.220),(.046,.049)),
 ("Flower umbel",(.465,.665),(.560,.895))
]
payload,sha,dims,url=module["obtain"](photo,corrected)
assert sha==entry["original_image_sha256"],"Upstream image changed; no unreviewed derivative allowed"
dest=ROOT/"images"/name
assert dest.exists()
dest.write_bytes(payload)
entry["role"]="Look closer · two anatomically inspected arrows: scalloped edge of right round leaf and dense manyflowered umbel held above finger. Top view reveals converging veins; underside petiole connection not shown."
entry["anatomy_arrows"]="2026-10-20 manually corrected after opening actual committed full-size JPEG. Arrow 1 targets right round-leaf scallop at (.770,.220), arrow 2 centers on real flower umbel at (.465,.665)."
entry["photo_review"]="Actual 1050x1400 gallery JPEG and 32-photo source sheet visually inspected; first arrows pointed toward background stem/hand and were corrected using original photo's unaltered bytes and SHA. Neither leaf underside nor ripe fruit shown."
entry["manual_arrow_review"]="2026-10-20-corrected-visual-readback"
card["curation_status"]["annotated_gallery_pixel_review"]="First install arrows failed full-frame review; regenerated from SHA-matched original, revised to visually inspected scalloped margin and terminal flower umbel. Pending final readback."
card["curation_status"]["required_to_finish"]=[s for s in card["curation_status"]["required_to_finish"] if not s.startswith("Manual pixel readback")]
card["curation_status"]["required_to_finish"].insert(0,"Read back corrected annotation against full committed JPEG and verify both arrowheads now point accurately")
card["learner_visual_status"]["note"]="Six source-licensed physical gallery photos. One two-arrow JPEG corrected to right scalloped leaf margin + dense flower umbel; leaf UNDERSIDE and mature ribbed mericarps still unverified."
card["photo_note"]+=" The first arrow JPEG failed pixel QA and was regenerated from SHA-verified upstream with corrected leaf-margin and umbel targets."
FILE.write_text(json.dumps(card,indent=2,ensure_ascii=False)+"\n")
ledger=ROOT/"image-sources.csv"
with ledger.open(newline="") as f:
 reader=csv.DictReader(f);cols=reader.fieldnames;rows=list(reader)
for row in rows:
 if row.get("file_name")==name:
  row["role"]=entry["role"]
  if "modifications" in cols: row["modifications"]="Resized/reencoded and EXIF stripped; anatomical arrows relocated after source-level visual confirmation"
with ledger.open("w",newline="") as f:
 writer=csv.DictWriter(f,fieldnames=cols,lineterminator="\n");writer.writeheader();writer.writerows(rows)
print("Corrected photo arrows and kept source copyright:",name,sha)
