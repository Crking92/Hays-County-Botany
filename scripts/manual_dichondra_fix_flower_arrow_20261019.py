#!/usr/bin/env python3
"""Fix one photo arrow after full-size manual visual inspection; never touch other species."""
import csv,json,runpy
from pathlib import Path
P=Path("content/taxa/Convolvulaceae/Dichondra/dichondra-carolinensis")
FILE=P/"species.json"
card=json.loads(FILE.read_text())
assert card["id"]=="dichondra-carolinensis" and len(card["images"])==6
target="images/alex-258349465-flower-face-arrows.jpg"
source=next(x for x in card["images"] if x["file"]==target)
if "corrected to a pale corolla lobe" in source.get("photo_review",""):
 print("Arrow already corrected; no-op")
 raise SystemExit(0)
mod=runpy.run_path("scripts/manual_dichondra_finished_photos_20261019.py")
old=next(x for x in mod["SOURCE"] if x["id"]=="258349465")
change=dict(old)
change["arrows"]=[("Cream corolla lobe",(0.62,0.36),(0.05,0.07))]
data,rawsha,dims,url=mod["get"](change)
assert rawsha==source["original_image_sha256"],"The original upstream photo changed; refuse relabel"
dest=P/target
assert dest.exists()
dest.write_bytes(data)
source["role"]="Look closer · a pale five-lobed fused corolla and surrounding hairy green sepals. Corrected yellow arrow points at one cream corolla lobe, not dark flower-center anthers."
source["anatomy_arrows"]="2026-10-19 manual full-frame correction: yellow arrow now targets actual creamy upper-right corolla lobe; no claim that the dark anthers are petals."
source["photo_review"]="Licensed exact-species photo visually inspected at installed resolution; arrow placement corrected to a pale corolla lobe in a separate full-image review. Five persistent green sepals separately visible. Species-level identification is source-based, not a voucher collection."
card["curation_status"]["annotated_gallery_anatomy_review"]="2026-10-19 all three installed yellow-arrow JPEGs opened at full display; corrected cream corolla lobe arrow on 258349465."
card["curation_status"]["required_to_finish"]=[
 "Acquire same-scale mature D. carolinensis versus D. recurvata fruiting pedicel + long calyx sepal macros",
 "Confirm exact CC BY-SA version of old Douglas Goldman source (original kept with previously documented CC BY-SA attribution)"
]
card["learner_visual_status"]["note"]="Six physical JPEGs, five Alex Abair CC BY 4.0 verified. Three anatomical arrow views physically opened for final pixel checks, including corrected pale petal lobe arrow, and remaining stalk-level species confirmation marked pending."
card["photo_note"] += " Full-resolution readback of all arrow photos performed; one incorrectly targeted corolla pointer corrected to a cream petal lobe and resaved with original photography and CC BY 4.0 source attribution preserved."
FILE.write_text(json.dumps(card,indent=2,ensure_ascii=False)+"\n")
ledger=P/"image-sources.csv"
with ledger.open(newline="") as f:
 reader=csv.DictReader(f);rows=list(reader);headers=reader.fieldnames
for row in rows:
 if row.get("file_name")=="alex-258349465-flower-face-arrows.jpg":
  row["role"]=source["role"]
  row["modifications"]="Resized JPEG, EXIF removed; anatomy arrow corrected to a creamy corolla lobe after full-scale inspection"
with ledger.open("w",newline="") as f:
 writer=csv.DictWriter(f,fieldnames=headers,lineterminator="\n")
 writer.writeheader();writer.writerows(rows)
print(json.dumps({"corrected":target,"new_dimensions":dims,"photo_count":len(card["images"]),"rights_unchanged":"CC BY 4.0 Alex Abair","other_photos_preserved":5},indent=2))
