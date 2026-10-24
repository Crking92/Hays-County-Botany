#!/usr/bin/env python3
"""Physically archive only already-cited exact-taxon CC BY Commons photos for nimblewill."""
import pathlib,json,urllib.request,urllib.parse,io,hashlib
from PIL import Image, ImageOps
root=pathlib.Path("content/taxa/Poaceae/Muhlenbergia/muhlenbergia-schreberi")
card=root/"species.json"; d=json.loads(card.read_text()); assert d["id"]=="muhlenbergia-schreberi"
report={"species":"muhlenbergia-schreberi","added":[],"holds":[]}
def get(url):
 req=urllib.request.Request(url,headers={"User-Agent":"HaysBotany/1.0 (public botanical photo curation; github.com/Crking92/Hays-County-Botany)"})
 with urllib.request.urlopen(req,timeout=40) as rsp:return rsp.read(18000001)
for row in d["images"]:
 url=row.get("file","")
 if "commons.wikimedia.org/wiki/Special:Redirect/file/Muhlenbergia" not in url:continue
 photo=row.get("inaturalist_photo_id")
 if not photo:continue
 try:
  filename="Muhlenbergia schreberi iNat-"+str(photo)+".jpg"
  api="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo","iiprop":"url|extmetadata","titles":"File:"+filename})
  page=next(iter(json.loads(get(api))["query"]["pages"].values()))
  inf=page["imageinfo"][0];meta=inf.get("extmetadata",{})
  license_name=meta.get("LicenseShortName",{}).get("value","")
  artist=meta.get("Artist",{}).get("value","")
  if "CC BY 4.0" not in license_name:raise ValueError("source license not CC BY 4.0: "+license_name)
  if "Emily Summerbell" not in artist:raise ValueError("photographer not verified")
  raw=get(inf["url"])
  if len(raw)>18000000:raise ValueError("oversized")
  with Image.open(io.BytesIO(raw)) as im: im.verify()
  with Image.open(io.BytesIO(raw)) as im:
   im=ImageOps.exif_transpose(im).convert("RGB")
   if min(im.size)<450:raise ValueError("insufficient photo resolution")
   im.thumbnail((2000,2000));buff=io.BytesIO();im.save(buff,format="JPEG",quality=87,optimize=True);blob=buff.getvalue()
  relative="images/nimblewill-emily-summerbell-"+str(photo)+"-ccby4.jpg"
  dest=root/relative
  if dest.exists():
   report["holds"].append({"photo":photo,"note":"Already exists; preserved"});continue
  dest.write_bytes(blob)
  row["file"]=relative;row["physical_archive_sha256"]=hashlib.sha256(blob).hexdigest()
  row["photo_status"]="LOCAL_JPEG_VERIFIED_SOURCE_ID; fine-anatomy markers pending pixel review"
  row["source_image_original"]=inf["url"]
  if "visual_comparison" in d:
   for panel in d["visual_comparison"].get("items",[]):
    if str(photo) in str(panel.get("image_url","")):panel["image_url"]=str(root/relative)
  report["added"].append({"photo":photo,"file":str(dest),"license":license_name,"sha256":row["physical_archive_sha256"]})
 except Exception as exc:report["holds"].append({"photo":photo,"reason":str(exc)[:220]})
if report["added"]:
 d["learner_visual_status"]["image_count"]=len(d["images"])
 d["learner_visual_status"]["status"]="FIELD_READY_PHOTO_GAPS"
 d["learner_visual_status"]["note"]="Local species-specific photographs archived. Inner collar/ligule and mature spikelet macro not confirmed; existing photo/source licenses preserved."
 d["curation_status"]["photo_files_present"]=sum(1 for row in d["images"] if row.get("file","").startswith("images/"))
 card.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
pathlib.Path("reports/lane3-nimblewill-commons-20261023.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
