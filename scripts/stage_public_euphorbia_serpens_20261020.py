#!/usr/bin/env python3
"""Omit restricted Nathan Taylor E. serpens node-root macro from public build ONLY.
Preserve the canonical study image, its source and creator in the repository.
"""
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument("--site-dir",required=True)
a=p.parse_args()
dist=Path(a.site_dir).resolve()
assert dist.name=="dist", "Never run on canonical source"
site=dist/"content/taxa/Euphorbiaceae/Euphorbia/euphorbia-serpens"
fp=site/"species.json"
j=json.loads(fp.read_text(encoding="utf-8"))
assert j["scientific_name"]=="Euphorbia serpens"
assert j["project_inclusion"]["target_zone_status"]=="PROVISIONAL"
assert j["native_metrics_excluded"] is True
assert len(j["images"])==5
held="images/05-node-rooting.jpg"
restricted=[x for x in j["images"] if x["file"]==held]
assert len(restricted)==1
assert restricted[0]["license"]=="CC BY-NC-SA"
assert restricted[0]["public_reuse"]=="no"
assert restricted[0]["creator"]=="Nathan Taylor"
assert (site/held).is_file()
kept=[x for x in j["images"] if x["file"]!=held]
assert len(kept)==4 and all(x["public_reuse"]=="yes" for x in kept)
assert all((site/x["file"]).is_file() for x in kept)
assert all(not x["image_url"].endswith("/"+held) for x in j["visual_comparison"]["items"])
genus=json.loads((dist/"content/taxa/Euphorbiaceae/Euphorbia/genus.json").read_text(encoding="utf-8"))
assert not any(i["image_url"].endswith("/"+held) for i in genus["visual_comparison"]["items"])
(site/held).unlink()
j["images"]=kept
j["curation_status"]["photo_metadata_count"]=4
j["curation_status"]["photo_files_present"]=4
j["curation_status"]["research_node_root_image_publicly_withheld"]=1
j["learner_visual_status"]["image_count"]=4
j["learner_visual_status"]["public_photo_rights_note"]="Rooting-node photo by Nathan Taylor is CC BY-NC-SA; available at source for reference but not publicly redistributed in this site's strict licensed media set."
j["source_only_photo_references"]=[{"creator":"Nathan Taylor","license":"CC BY-NC-SA","source_page":restricted[0]["source_page"],"reason":"Noncommercial share restrictions; research citation only"}]
fp.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
assert not (site/held).exists()
print("PASS 4 public-licensed E. serpens photos staged; restricted rooting-node original preserved in source repository.")
