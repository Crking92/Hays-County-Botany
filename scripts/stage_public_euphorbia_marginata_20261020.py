#!/usr/bin/env python3
"""Public export policy: remove one original CC BY-NC image from staged website only.
The canonical GitHub source retains the Joey Santore photo and original credit."""
import argparse,json
from pathlib import Path
a=argparse.ArgumentParser()
a.add_argument("--site-dir",required=True)
args=a.parse_args()
dist=Path(args.site_dir).resolve()
assert dist.name=="dist"
folder=dist/"content/taxa/Euphorbiaceae/Euphorbia/euphorbia-marginata"
fp=folder/"species.json"
j=json.loads(fp.read_text(encoding="utf-8"))
assert j["scientific_name"]=="Euphorbia marginata"
assert j["project_inclusion"]["target_zone_status"]=="PASS"
assert len(j["images"])==4
held="images/joey-inat-428373451.jpg"
photo=[x for x in j["images"] if x["file"]==held]
assert len(photo)==1
assert photo[0]["license"]=="CC BY-NC 4.0"
assert photo[0]["creator"]=="Joey Santore"
assert (folder/held).is_file()
kept=[x for x in j["images"] if x["file"]!=held]
assert len(kept)==3
assert all(x.get("public_reuse")=="yes" for x in kept)
for x in kept:
    assert (folder/x["file"]).is_file(),x["file"]
assert all(x["image_url"]!="content/taxa/Euphorbiaceae/Euphorbia/euphorbia-marginata/"+held for x in j["visual_comparison"]["items"])
(folder/held).unlink()
j["images"]=kept
j["curation_status"]["photo_metadata_count"]=3
j["curation_status"]["photo_files_present"]=3
j["curation_status"]["public_noncommercial_photo_reference_withheld"]=1
j["learner_visual_status"]["image_count"]=3
j["learner_visual_status"]["public_licensing_notice"]="CC BY-NC research photo credited to Joey Santore remains available by source link, not distributed in strict public photo set."
j["research_only_photo_references"]=[{"creator":"Joey Santore","license":"CC BY-NC 4.0","source_page":photo[0]["source_page"]}]
fp.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
assert not (folder/held).exists()
print("PASS E. marginata: 3 open-license photos public, Joey noncommercial original preserved in repository")
