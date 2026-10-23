#!/usr/bin/env python3
"""Read-only Poaceae photo publication integrity audit. Never edits source cards."""
import json,pathlib,datetime,collections,imghdr
root=pathlib.Path(".")
manifest=json.loads((root/"data/manifest.json").read_text())
grass=[x for x in manifest["species"] if "/Poaceae/" in x["path"]]
records=[];counts=collections.Counter()
for entry in grass:
 path=root/entry["path"];item={"id":entry["id"],"card":entry["path"],"missing":[],"broken":[],"external":[],"photos":0,"warnings":[]}
 try:
  card=json.loads(path.read_text())
  photos=card.get("images",[])
  item["photos"]=len(photos)
  if card.get("learner_visual_status",{}).get("image_count")!=len(photos):
   item["warnings"].append("stale learner_visual_status.image_count")
  for photo in photos:
   f=photo.get("file","")
   if f.startswith(("https://","http://")):
    item["external"].append(f);continue
   fp=path.parent/f
   if not fp.is_file():
    item["missing"].append(f);continue
   try:
    raw=fp.read_bytes()
    if len(raw)<2000 or imghdr.what(None,raw) not in ("jpeg","png","webp","gif"):
     item["broken"].append(f)
   except Exception: item["broken"].append(f)
 except Exception as exc:item["warnings"].append("species card unreadable: "+str(exc))
 counts["species"]+=1;counts["gallery_entries"]+=item["photos"]
 counts["missing"]+=len(item["missing"]);counts["broken"]+=len(item["broken"])
 counts["external"]+=len(item["external"])
 if item["photos"]==0:counts["zero_photo"]+=1
 if item["photos"]==1:counts["one_photo"]+=1
 if item["missing"] or item["broken"] or item["warnings"] or item["external"]:records.append(item)
out={"audit_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"scope":"All currently installed Poaceae species on main","checks":"Every canonical images[].file resolved relative to its species folder; image signature and size; gallery metadata count; external refs","summary":dict(counts),"issues":records,"public_rendering":"NOT_VERIFIED: file existence cannot establish Pages deployment, loaded image requests, or browser rendering"}
p=root/"reports/grass-photo-publish-integrity-audit.json";p.parent.mkdir(exist_ok=True);p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
print("Grass archive audit",json.dumps(out["summary"],indent=2))
for x in records:
 if x["missing"] or x["broken"]:print("FAIL",x["id"],"missing",x["missing"],"corrupt",x["broken"])
