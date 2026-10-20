#!/usr/bin/env python3
"""Public-only site copy excludes CC BY-NC legacy E. maculata photograph.
Canonical source image and original credit never modified.
"""
from pathlib import Path
import argparse,json
p=argparse.ArgumentParser()
p.add_argument("--site-dir",required=True)
a=p.parse_args()
dist=Path(a.site_dir).resolve()
assert dist.name=="dist"
folder=dist/"content/taxa/Euphorbiaceae/Euphorbia/euphorbia-maculata"
path=folder/"species.json"
j=json.loads(path.read_text(encoding="utf8"))
assert j["scientific_name"]=="Euphorbia maculata"
assert len(j["images"])==5
held="images/inat-91881491.jpg"
old=j["images"][0]
assert old["file"]==held and old["license"]=="CC BY-NC"
kept=j["images"][1:]
assert len(kept)==4
assert all(x["public_reuse"]=="yes" and x["license"] in ("CC BY 2.0","CC BY-SA 4.0") for x in kept)
assert all((folder/x["file"]).is_file() for x in kept)
assert (folder/held).is_file()
assert all(not x["image_url"].endswith(held) for x in j["visual_comparison"]["items"])
genus=json.loads((dist/"content/taxa/Euphorbiaceae/Euphorbia/genus.json").read_text(encoding="utf8"))
assert all(not x["image_url"].endswith(held) for x in genus["visual_comparison"]["items"])
(folder/held).unlink()
j["images"]=kept
j["curation_status"]["photo_metadata_count"]=4
j["curation_status"]["photo_files_present"]=4
j["curation_status"]["public_noncommercial_image_withheld"]=1
j["learner_visual_status"]["image_count"]=4
j["research_only_photo_references"]=[{"creator":old["creator"],"license":old["license"],"source_page":old["source_page"],"reason":"Noncommercial reuse; retained in canonical source, not redistributed in public Pages build"}]
path.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
print("PASS maculata: four CC BY/CC BY-SA real source photos in public copy, old NC research image withheld")
