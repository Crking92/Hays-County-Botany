#!/usr/bin/env python3
"""Remove two source-rights-restricted Euphorbia davidii study photos from public Pages dist.
Only touches --site-dir dist; canonical research media stay in GitHub. Supports optional
verified public-domain USDA/Colorado SeedImages seed source if successfully installed.
"""
import argparse,json
from pathlib import Path
BASE=Path("content/taxa/Euphorbiaceae/Euphorbia/euphorbia-davidii")
RESTRICTED={"images/03-abaxial-hairs-private-study.jpg","images/04-seeds-private-study.jpg"}
PUBLIC={"images/01-jordan-river-habit.jpg","images/02-upper-plant-detail.jpg","images/seedimages-bat003312-davidii-seeds.jpg"}
def main():
 p=argparse.ArgumentParser();p.add_argument("--site-dir",required=True);args=p.parse_args()
 dist=Path(args.site_dir).resolve()
 assert dist.name=="dist", "Never modify original repository photo store"
 folder=dist/BASE;card=folder/"species.json"
 j=json.loads(card.read_text(encoding="utf-8"))
 assert j["scientific_name"]=="Euphorbia davidii"
 assert j["project_inclusion"]["native_metrics_excluded"] is True
 assert j["field_id_finalization"]["stage"]=="PASS_IN_PROGRESS"
 source=j["images"];files={x["file"] for x in source}
 assert RESTRICTED.issubset(files) and files.issubset(PUBLIC|RESTRICTED)
 assert {"images/01-jordan-river-habit.jpg","images/02-upper-plant-detail.jpg"}.issubset(files)
 retained=[x for x in source if x["file"] in PUBLIC]
 removed=[x for x in source if x["file"] in RESTRICTED]
 assert len(removed)==2 and len(retained) in (2,3)
 assert all(x["public_reuse"]=="review" and "copyrighted" in x["license"] for x in removed)
 assert all(x["file"].startswith("images/") and x.get("public_reuse")=="yes" for x in retained)
 for x in retained:
  f=folder/x["file"];assert f.is_file() and f.stat().st_size>10000,f
 for x in removed:
  f=folder/x["file"];assert f.is_file(),f;f.unlink()
 j["images"]=retained
 j["curation_status"]["photo_metadata_count"]=len(retained)
 j["curation_status"]["photo_files_present"]=len(retained)
 j["curation_status"]["public_gallery_restricted_study_photos_withheld"]=len(removed)
 j["learner_visual_status"]["image_count"]=len(retained)
 j["learner_visual_status"]["public_copy_rights_guard"]="Two restricted S.R. Turner microscopy images excluded from staged public copy; author originals unchanged."
 j["public_restricted_photo_references"]=[{"source_page":x["source_page"],"creator":x["creator"],"license":x["license"],"reason":"Research citation only; image withheld pending redistribution permission"} for x in removed]
 assert all((dist/Path(x["image_url"])).is_file() for x in j["visual_comparison"]["items"])
 card.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 assert all(not (folder/x).exists() for x in RESTRICTED)
 print(f"PASS public Euphorbia davidii: {len(retained)} open-rights gallery images, 2 restricted research-only images withheld in dist.")
if __name__=="__main__":main()
