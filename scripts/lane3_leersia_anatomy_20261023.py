#!/usr/bin/env python3
"""Archive two previously reviewed public rice-cutgrass habit/panicle references.
Existing canonical species only. No inferred anatomical arrows or taxonomy changes.
"""
import json,io,pathlib,urllib.request,urllib.parse,hashlib
from PIL import Image,ImageOps
root=pathlib.Path("content/taxa/Poaceae/Leersia/leersia-oryzoides");path=root/"species.json";d=json.loads(path.read_text());assert d["id"]=="leersia-oryzoides"
report={"added":[],"holds":[],"note":"Joey Santore restricted study-only frame not republished; no anatomy arrows inferred"}
def get(url):
 req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyVisualLearner/1.0 (CC licensed reference archive; github.com/Crking92/Hays-County-Botany)"})
 with urllib.request.urlopen(req,timeout=40) as r:return r.read(18000001)
for n in (1,20):
 name=f"Leersia oryzoides sl{n}.jpg";source="https://commons.wikimedia.org/wiki/File:"+name.replace(" ","_")
 try:
  api="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo","iiprop":"url|extmetadata","titles":"File:"+name})
  info=next(iter(json.loads(get(api))["query"]["pages"].values()))["imageinfo"][0];meta=info["extmetadata"];license_name=meta.get("LicenseShortName",{}).get("value","");artist=meta.get("Artist",{}).get("value","")
  if "CC BY-SA 4.0" not in license_name or "Stefan" not in artist:raise ValueError("license/creator not verified: "+license_name+" / "+artist[:100])
  original=next((z for z in d["images"] if z.get("source_page")==source),None)
  if original is None:raise ValueError("canonical source record not found")
  if original.get("file","").startswith("images/"):
   report.setdefault("reused",[]).append({"source":source,"file":original["file"]})
   continue
  b=get(info["url"])
  source_sha256=hashlib.sha256(b).hexdigest()
  with Image.open(io.BytesIO(b)) as im:im.verify()
  with Image.open(io.BytesIO(b)) as im:
   im=ImageOps.exif_transpose(im).convert("RGB")
   if min(im.size)<400:raise ValueError("source too small")
   im.thumbnail((2000,2000));out=io.BytesIO();im.save(out,"JPEG",quality=88,optimize=True);blob=out.getvalue()
  dest=root/"images"/f"stefan-lefnaer-sl{n}-cc-by-sa4.jpg"
  if dest.exists():raise ValueError("already present; protect existing file")
  dest.write_bytes(blob);old=original["file"];original["file"]="images/"+dest.name;original["original_media_url"]=info["url"];original["sha256"]=hashlib.sha256(blob).hexdigest();original["original_sha256"]=source_sha256;original["source_bytes_verified"]=len(b);original["archived_bytes_verified"]=len(blob);original["source_license_checked"]="CC BY-SA 4.0; Stefan.lefnaer; reuse with attribution, source, license URL and ShareAlike adaptation notice";original["photo_review"]=("Exact-species wet-bank habit, not a connected rooted Hays specimen" if n==1 else "Exact-species open panicle with visible branching axis; lowest branches not independently counted or calibrated");original["annotation_pending"]="Do not add branch-count or anatomy arrows until full-resolution pixel review"
  for panel in d["visual_comparison"]["items"]:
   if panel.get("image_url")==old:panel["image_url"]=str(dest);panel["photo_status"]="LOCAL_CC_BY_SA_4__ANATOMY_SCALE_REVIEW_PENDING";panel["annotation_pending"]="No branch-count or precise node arrows until full-resolution pixel review"
  report["added"].append({"source":source,"file":str(dest),"creator":"Stefan.lefnaer","license":license_name,"source_bytes":len(b),"source_sha256":source_sha256,"archived_bytes":len(blob),"archived_sha256":original["sha256"],"anatomy_arrows":0})
 except Exception as exc:report["holds"].append({"source":source,"reason":str(exc)[:240]})
if report["added"]:
 d["curation_status"]["photo_files_present"]=sum(x.get("file","").startswith("images/") for x in d["images"])
 d["curation_status"]["photo_metadata_count"]=len(d["images"])
 d.setdefault("learner_visual_status",{})["status"]="FIELD_READY_PHOTO_GAPS"
 d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
 path.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n")
pathlib.Path("reports/lane3-leersia-anatomy-20261023.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
