#!/usr/bin/env python3
"""Archive three licensed exact-species diagnostic photos for rice cutgrass."""
import json,io,pathlib,urllib.request,urllib.parse,hashlib
from PIL import Image,ImageOps
root=pathlib.Path("content/taxa/Poaceae/Leersia/leersia-oryzoides");path=root/"species.json";d=json.loads(path.read_text());assert d["id"]=="leersia-oryzoides"
report={"added":[],"holds":[],"note":"Joey Santore restricted study-only frame not republished; no anatomy arrows inferred"}
def get(url):
 req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyVisualLearner/1.0 (CC licensed reference archive; github.com/Crking92/Hays-County-Botany)"})
 with urllib.request.urlopen(req,timeout=40) as r:return r.read(18000001)
for n in (23,30,31):
 name=f"Leersia oryzoides sl{n}.jpg";source="https://commons.wikimedia.org/wiki/File:"+name.replace(" ","_")
 try:
  api="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo","iiprop":"url|extmetadata","titles":"File:"+name})
  info=next(iter(json.loads(get(api))["query"]["pages"].values()))["imageinfo"][0];meta=info["extmetadata"];license_name=meta.get("LicenseShortName",{}).get("value","");artist=meta.get("Artist",{}).get("value","")
  if "CC BY-SA 4.0" not in license_name or "Stefan" not in artist:raise ValueError("license/creator not verified: "+license_name+" / "+artist[:100])
  original=next((z for z in d["images"] if z.get("source_page")==source),None)
  if original is None:raise ValueError("canonical source record not found")
  b=get(info["url"])
  with Image.open(io.BytesIO(b)) as im:im.verify()
  with Image.open(io.BytesIO(b)) as im:
   im=ImageOps.exif_transpose(im).convert("RGB")
   if min(im.size)<400:raise ValueError("source too small")
   im.thumbnail((2000,2000));out=io.BytesIO();im.save(out,"JPEG",quality=88,optimize=True);blob=out.getvalue()
  dest=root/"images"/f"stefan-lefnaer-sl{n}-cc-by-sa4.jpg"
  if dest.exists():raise ValueError("already present; protect existing file")
  dest.write_bytes(blob);old=original["file"];original["file"]="images/"+dest.name;original["original_media_url"]=info["url"];original["sha256"]=hashlib.sha256(blob).hexdigest();original["photo_review"]="Locally archived exact-source photo; anatomy source-labelled, measurement and arrow pixels unverified"
  for panel in d["visual_comparison"]["items"]:
   if panel.get("image_url")==old:panel["image_url"]=str(dest);panel["photo_status"]="LOCAL_CC_BY_SA_4__ANATOMY_SCALE_REVIEW_PENDING"
  report["added"].append({"source":source,"file":str(dest),"license":license_name,"sha256":original["sha256"]})
 except Exception as exc:report["holds"].append({"source":source,"reason":str(exc)[:240]})
if report["added"]:
 d["curation_status"]["photo_files_present"]=sum(x.get("file","").startswith("images/") for x in d["images"])
 d["curation_status"]["photo_metadata_count"]=len(d["images"])
 d.setdefault("learner_visual_status",{})["status"]="FIELD_READY_PHOTO_GAPS"
 d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
 path.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n")
pathlib.Path("reports/lane3-leersia-anatomy-20261023.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
