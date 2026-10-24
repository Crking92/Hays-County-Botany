#!/usr/bin/env python3
"""Archive existing external Commons S. nutans habit/panicle photos, with individual license verification."""
import pathlib,json,urllib.parse,urllib.request,io
from PIL import Image
p=pathlib.Path("content/taxa/Poaceae/Sorghastrum/sorghastrum-nutans/species.json")
d=json.loads(p.read_text())
spec=[("Sorghastrum nutans 1zz.jpg","david-stang-whole-indiangrass.jpg","David J. Stang","ccbysa40","CC BY-SA 4.0","https://creativecommons.org/licenses/by-sa/4.0/"),("Sorghastrum nutans 566649681.jpg","alex-abair-indiangrass-panicle.jpg","Alex Abair","ccby40","CC BY 4.0","https://creativecommons.org/licenses/by/4.0/")]
report={"added":[],"held":[]}
def fetch(u):
 with urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"HaysCountyBotanyLearner/1.0 (photo rights evidence)"}),timeout=60) as f:return f.read()
for title,name,creator,license_key,license_name,license_url in spec:
 try:
  args=urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":1400,"titles":"File:"+title})
  meta=next(iter(json.loads(fetch("https://commons.wikimedia.org/w/api.php?"+args))["query"]["pages"].values()))["imageinfo"][0]
  lic=meta["extmetadata"]["LicenseShortName"]["value"];norm="".join(c for c in lic.lower() if c.isalnum())
  assert norm==license_key,"license check failed "+lic
  binary=fetch(meta.get("thumburl") or meta["url"])
  im=Image.open(io.BytesIO(binary));im.verify();im=Image.open(io.BytesIO(binary)).convert("RGB")
  assert min(im.size)>=650 and len(binary)>15000
  local="images/"+name;out=p.parent/local;out.parent.mkdir(exist_ok=True,parents=True);im.save(out,"JPEG",quality=91,optimize=True)
  page="https://commons.wikimedia.org/wiki/File:"+urllib.parse.quote(title.replace(" ","_"))
  if not any(x.get("file")==local for x in d["images"]):
   d["images"].append({"file":local,"role":"Source verified species habit/panicle reference, not fine anatomy","creator":creator,"license":license_name,"license_url":license_url,"source_page":page,"modifications":"1400px Wikimedia derivative re-encoded JPG; EXIF discarded","photo_status":"PHYSICAL ARCHIVE; no new microscopic arrows"})
  replaced=0
  for panel in d.get("visual_comparison",{}).get("items",[]):
   if (("1zz.jpg" in panel.get("image_url","") and "1zz" in title) or ("566649681" in panel.get("image_url","") and "566649681" in title)):
    panel["image_url"]=str(out).replace("\\","/");panel["creator"]=creator;panel["license"]=license_name;panel["license_url"]=license_url;panel["source_page"]=page;replaced+=1
  report["added"].append({"file":str(out),"panel_links_changed":replaced,"image_dimensions":im.size,"license":license_name})
 except Exception as e:report["held"].append({"source":title,"error":str(e)})
if report["added"]:
 d.setdefault("field_id_finish_pass",{})["lane4_20261023"]={"stage":"FIELD_READY_PHOTO_GAPS","new_locally_archived_species_photos":len(report["added"]),"new_pixel_arrows":0,"copyright_hold":"Existing original video screenshot remains PRIVATE STUDY ONLY and must NOT be displayed on public website","remaining":["same Texas verified roots-through-flowering panicle and ligule 1mm reference","fertile awned sessile spikelet and sterile naked pedicel with 1mm ruler","measured bent awns and comparison versus S. elliottii on matched voucher"],"live_pages":"NOT VERIFIED"}
 d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
 p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
out=pathlib.Path("reports/lane4-sorghastrum-nutans-habit-archive.json");out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
