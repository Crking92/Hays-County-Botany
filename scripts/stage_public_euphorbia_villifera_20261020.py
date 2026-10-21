#!/usr/bin/env python3
"""Stage Euphorbia villifera with individual photo rights intact.

Website context: the owner's stand-alone NONCOMMERCIAL educational public learner.
Seven correctly credited source images: 3 CC BY, 4 CC BY-NC; the four NC
images are conditional on continued genuinely noncommercial publication.
Keep two university reuse-rights-unverified images OUT of public dist.
Do not manufacture evidence for stipules, papillae, inner capsule tips or seed.
Canonical source photographs and records are unchanged.
"""
import argparse
import json
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument("--site-dir",required=True)
args=p.parse_args()
dist=Path(args.site_dir).resolve()
assert dist.name=="dist","Stage public site copy only, never canonical!"
root=dist/"content/taxa/Euphorbiaceae/Euphorbia/euphorbia-villifera"
card=root/"species.json"
j=json.loads(card.read_text(encoding="utf-8"))
assert j["scientific_name"]=="Euphorbia villifera"
assert j["project_inclusion"]["target_zone_status"]=="PROVISIONAL"
assert j["native_metrics_excluded"] is True
assert j["field_id_finalization"]["stage"]=="PASS_IN_PROGRESS"
assert len(j["images"])==9
keep={
 "images/03-capsule-pointed-lobes.jpg",
 "images/04-villous-leaf-hairs.jpg",
 "images/05-sparse-hairs-leaf-surface.jpg",
 "images/06-separated-seeds-reference.jpg",
 "images/07-leaf-surface-node-detail.jpg",
 "images/08-node-leaf-attachments.jpg",
 "images/09-joey-cyathium-leaves.jpg",
}
assert len({x["file"] for x in j["images"]})==9
kept=[x for x in j["images"] if x["file"] in keep]
excluded=[x for x in j["images"] if x["file"] not in keep]
assert len(kept)==7 and len(excluded)==2
assert set(x["file"] for x in kept)==keep
ccby=[x for x in kept if x["license"]=="CC BY"]
nc=[x for x in kept if x["license"]=="CC BY-NC"]
assert len(ccby)==3 and len(nc)==4
for x in kept:
 assert x["public_reuse"]=="yes" and x["creator"] and x["source_page"].startswith("https://")
 assert x["license_url"].startswith("https://creativecommons.org/licenses/")
 assert (root/x["file"]).is_file()
for x in nc:
 assert "noncommercial" in x["public_site_eligibility"]["scope"].lower()
 assert x["public_site_eligibility"]["retain_license_and_credit"] is True
assert all(x["license"]=="reuse rights unverified" and x["public_reuse"]=="review" for x in excluded)
assert any(x["file"].startswith("images/06-") and "not confidently" in x["caption"].lower() for x in kept)
for x in j["images"]:
 assert (root/x["file"]).is_file(),x["file"]
for x in excluded: (root/x["file"]).unlink()
j["images"]=kept
j["curation_status"]["photo_metadata_count"]=7
j["curation_status"]["photo_files_present"]=7
j["curation_status"]["public_site_policy_review"]="2026-10-20, NONCOMMERCIAL educational website only"
j["curation_status"]["unverified_university_reuse_images_withheld"]=2
j["learner_visual_status"]["image_count"]=7
j["learner_visual_status"]["public_staged_notice"]=(
 "Seven individually credited gallery images: 3 CC BY, 4 CC BY-NC conditional on a genuinely noncommercial site. "
 "Only two real photo overlays have six checked anatomy arrows. A third CC BY image contains ambiguous loose material, NOT an identified mature seed. "
 "Filiform stipules, papillae and internal capsule cavities are NOT proven by existing photos."
)
j["research_only_photo_references"]=[
 {"source_page":x["source_page"],"creator":x["creator"],"license":x["license"],"reason":"Rights not individually verified for public redistribution"}
 for x in excluded
]
assert len(j["visual_comparison"]["items"])==2
assert sum(len(x["markers"]) for x in j["visual_comparison"]["items"])==6
assert all((dist/x["image_url"]).is_file() for x in j["visual_comparison"]["items"])
card.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
assert all(not (root/x["file"]).exists() for x in excluded)
print("PASS E. villifera: 7 public gallery photos (3 CC BY + 4 CC BY-NC), 2 arrowed sources with 6 verified arrows, 2 university rights-unverified files withheld.")
