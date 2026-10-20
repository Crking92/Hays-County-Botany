#!/usr/bin/env python3
import argparse,json
from pathlib import Path
parser=argparse.ArgumentParser()
parser.add_argument("--site-dir",required=True)
args=parser.parse_args()
base=Path(args.site_dir).resolve()
assert base.name=="dist"
folder=base/"content/taxa/Euphorbiaceae/Euphorbia/euphorbia-heterophylla"
record=folder/"species.json"
card=json.loads(record.read_text())
assert card["scientific_name"]=="Euphorbia heterophylla"
assert len(card["images"])==4
photo="images/02-cyathia-closeup.jpg"
matched=[x for x in card["images"] if x["file"]==photo]
assert len(matched)==1
assert matched[0]["taxon_photo_review"].startswith("TAXON_ID_HOLD")
genus=json.loads((base/"content/taxa/Euphorbiaceae/Euphorbia/genus.json").read_text())
assert all(not x.get("image_url","").endswith(photo) for x in genus["visual_comparison"]["items"])
(folder/photo).unlink()
card["images"]=[x for x in card["images"] if x["file"]!=photo]
assert len(card["images"])==3
card["curation_status"]["photo_files_present"]=3
card["curation_status"]["photo_metadata_count"]=3
card["curation_status"]["photo_id_review_hold"]=1
card["learner_visual_status"]["image_count"]=3
record.write_text(json.dumps(card,indent=2,ensure_ascii=False)+"\n")
print("Reviewed gallery staged: 3 images, 1 taxon-ID pending source omitted from public preview")
