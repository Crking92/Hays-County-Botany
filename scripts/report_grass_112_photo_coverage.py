#!/usr/bin/env python3
"""Build a complete 112-grass, per-species photo-count and anatomy coverage planning report."""
import json,pathlib,re,collections,datetime,csv
root=pathlib.Path(".")
manifest=json.loads((root/"data/manifest.json").read_text())
grasses=[v for v in manifest["species"] if "/Poaceae/" in v["path"]]
patterns={
 "whole_plant":r"whole plant|plant habit|habit|bunch|clump|growth form|turf|grass stand|field view|stolon|rhizome",
 "leaf_collar_ligule":r"ligule|collar|auricle|sheath|leaf blade|leaf base|leaf hairs|nodes?",
 "seedhead":r"seedhead|seed head|inflorescence|panicle|raceme|spike|flowering head|flower head|head architecture|seed head",
 "spikelet_floret":r"spikelet|floret|glume|lemma|palea|awn|anther|stigma|caryopsis|grain|floral unit",
 "lookalike":r"look.alike|comparison|different species|versus|vs\\.|side.by.side|contrast"
}
rows=[];total=collections.Counter()
for item in grasses:
 p=root/item["path"];card=json.loads(p.read_text());photos=card.get("images",[])
 views=collections.Counter();evidence={k:[] for k in patterns}
 for photo in photos:
  notes=" ".join(str(photo.get(x,"")) for x in ("role","caption","description","photo_review","photo_status","alt","source_type","file"))
  for k,regex in patterns.items():
   if re.search(regex,notes,re.I):views[k]+=1;evidence[k].append(str(photo.get("role",""))[:95])
 # Distinguish actual gallery photos from arrows and off-gallery text descriptions.
 local=sum(not x.get("file","").startswith(("http://","https://")) for x in photos)
 external=len(photos)-local
 historic=sum(bool(re.search("historic|illustration|plate|drawing", " ".join(str(x.get(z,"")) for z in ("role","photo_status","file")),re.I)) for x in photos)
 diagnostic=views["leaf_collar_ligule"]+views["spikelet_floret"]
 unknown=sum(not re.search("|".join(patterns.values()),str(x.get("role","")),re.I) for x in photos)
 if len(photos)<=1: priority="P0: zero/one image"
 elif diagnostic==0:priority="P1: no labeled anatomy"
 elif diagnostic<=2:priority="P2: thin anatomy"
 else:priority="P3: expand/verify"
 entry={
 "species":card.get("scientific_name") or item["id"],"common_name":card.get("common_name",""),
 "genus":card.get("genus",""),"id":item["id"],"photo_entries":len(photos),"local":local,"external":external,"historic_illustrations_est":historic,
 "whole_plant_est":views["whole_plant"],"leaf_collar_ligule_est":views["leaf_collar_ligule"],
 "flowering_seedhead_est":views["seedhead"],"spikelet_floret_awn_est":views["spikelet_floret"],
 "lookalike_labeled_photo_est":views["lookalike"],"unclassified_photo_roles_est":unknown,
 "priority":priority,
 "what_to_find_next":(
  "Source-verified photos: whole plant, collar/ligule, seedhead, magnified spikelets" if len(photos)<=1 else
  "Real scaled collar/ligule and spikelet/floret close-ups; keep source-verified views" if diagnostic==0 else
  "Add missing close-up leaf collar and spikelet/awn plus arrows; verify scale" if diagnostic<=2 else
  "Check anatomical arrows and local look-alike comparison; fill remaining exact-scale gaps"
 ),
 "sample_photo_roles":[str(x.get("role",""))[:120] for x in photos[:5]]
 }
 rows.append(entry);total[priority]+=1;total["photos"]+=len(photos);total["local"]+=local;total["external"]+=external
rows.sort(key=lambda x:(int(x["priority"][1]),x["photo_entries"],x["species"]))
out={"generated_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"method":"Heuristic keywords from canonical images[].role/caption; categories overlap and coverage is approximate, NOT visual/photo verification; photo entries may include historical plates, not just photos.","summary":{"species":len(rows),**dict(total)},"species":rows}
p=root/"reports/grass-112-photo-coverage-work-allocation.json";p.parent.mkdir(exist_ok=True);p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
csvp=root/"reports/grass-112-photo-coverage-work-allocation.csv"
with csvp.open("w",newline="") as f:
 writer=csv.DictWriter(f,fieldnames=[k for k in rows[0] if k!="sample_photo_roles"])
 writer.writeheader()
 for row in rows:writer.writerow({k:v for k,v in row.items() if k!="sample_photo_roles"})
print(json.dumps(out["summary"],indent=2))
