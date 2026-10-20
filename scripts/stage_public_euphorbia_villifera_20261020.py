#!/usr/bin/env python3
"""Make a strict public preview of E. villifera without changing source research files.

Keep CC BY images 04, 06 and 08. The seed-material reference (06) is
taxonomically ambiguous and expressly NOT diagnostic. University rights-unverified
images and all CC BY-NC files stay canonical, but out of public Pages distribution.
"""
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument("--site-dir",required=True)
args=p.parse_args()
dist=Path(args.site_dir).resolve()
assert dist.name=="dist","Only stage public site copy, never canonical"
root=dist/"content/taxa/Euphorbiaceae/Euphorbia/euphorbia-villifera"
card=root/"species.json"
j=json.loads(card.read_text(encoding="utf-8"))
assert j["scientific_name"]=="Euphorbia villifera"
assert j["project_inclusion"]["target_zone_status"]=="PROVISIONAL"
assert j["native_metrics_excluded"] is True
assert j["field_id_finalization"]["stage"]=="PASS_IN_PROGRESS"
assert len(j["images"])==9
keep={
 "images/04-villous-leaf-hairs.jpg",
 "images/06-separated-seeds-reference.jpg",
 "images/08-node-leaf-attachments.jpg"
}
assert len({x["file"] for x in j["images"]})==9
kept=[x for x in j["images"] if x["file"] in keep]
excluded=[x for x in j["images"] if x["file"] not in keep]
assert len(kept)==3 and len(excluded)==6
assert all(x["public_reuse"]=="yes" and x["license"].startswith("CC BY") and "-NC" not in x["license"] for x in kept)
assert all(x.get("public_reuse") in ("no","review") or "-NC" in x.get("license","") or "unverified" in x.get("license","") for x in excluded)
assert any(x["file"].startswith("images/06-") and "not confidently" in x["caption"].lower() for x in kept)
for x in j["images"]: assert (root/x["file"]).is_file(), x["file"]
for x in excluded: (root/x["file"]).unlink()
j["images"]=kept
j["curation_status"]["photo_metadata_count"]=3
j["curation_status"]["photo_files_present"]=3
j["curation_status"]["public_study_photos_rights_held"]=6
j["learner_visual_status"]["image_count"]=3
j["learner_visual_status"]["public_staged_notice"]="Only 2 confirmed diagnostic source images have overlays. A third CC BY image of loose reproductive material is kept as explicit caution, NOT evidence of mature seed ID."
j["research_only_photo_references"]=[{"source_page":x["source_page"],"creator":x["creator"],"license":x["license"],"reason":"Research citation only: redistribution rights not granted or independently verified"} for x in excluded]
assert len(j["visual_comparison"]["items"])==2
assert sum(len(x["markers"]) for x in j["visual_comparison"]["items"])==6
assert all((dist/x["image_url"]).is_file() for x in j["visual_comparison"]["items"])
card.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
assert all(not (root/x["file"]).exists() for x in excluded)
print("PASS E. villifera 3 public CC BY gallery files, 2 arrowed species photos, 6 restricted/rights-unverified files held from public dist.")
