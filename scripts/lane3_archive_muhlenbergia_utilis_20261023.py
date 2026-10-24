#!/usr/bin/env python3
"""Lane 3: archive credited Muhlenbergia utilis Commons image, preserving morphological holds."""
import json,pathlib,urllib.request,urllib.parse,io,hashlib,time
from PIL import Image,ImageOps
root=pathlib.Path("content/taxa/Poaceae/Muhlenbergia/muhlenbergia-utilis")
card=root/"species.json";data=json.loads(card.read_text())
assert data["id"]=="muhlenbergia-utilis"
report={"species":"muhlenbergia-utilis","added":[],"holds":[]}
def fetch(url):
 request=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyLearner/1.0 (credited CC botany photo curation; github.com/Crking92/Hays-County-Botany)"})
 with urllib.request.urlopen(request,timeout=40) as response:return response.read(18000001)
for img in data["images"]:
 if img.get("inaturalist_photo_id")!=14855736 or str(img.get("file","")).startswith("images/"):continue
 try:
  api="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo","iiprop":"url|extmetadata","titles":"File:Muhlenbergia utilis.jpg"})
  result=json.loads(fetch(api));info=next(iter(result["query"]["pages"].values()))["imageinfo"][0]
  meta=info["extmetadata"];lic=meta.get("LicenseShortName",{}).get("value","")
  artist=meta.get("Artist",{}).get("value","")
  if "CC BY-SA 4.0" not in lic:raise ValueError("license mismatch: "+lic)
  if "Romey Swanson" not in artist:raise ValueError("creator mismatch: "+artist[:100])
  raw=fetch(info["url"])
  if len(raw)>18000000:raise ValueError("oversized")
  with Image.open(io.BytesIO(raw)) as im:im.verify()
  with Image.open(io.BytesIO(raw)) as im:
   im=ImageOps.exif_transpose(im).convert("RGB")
   if min(im.size)<450:raise ValueError("insufficient resolution")
   im.thumbnail((2000,2000));out=io.BytesIO();im.save(out,"JPEG",quality=88,optimize=True);blob=out.getvalue()
  rel="images/muhlenbergia-utilis-romey-swanson-cc-by-sa4.jpg";dest=root/rel
  if dest.exists():raise ValueError("already installed; preserve")
  dest.write_bytes(blob)
  old=img["file"];img["file"]=rel;img["source_image_original"]=info["url"]
  img["physical_archive_sha256"]=hashlib.sha256(blob).hexdigest()
  img["photo_status"]="LOCAL_SOURCE_VERIFIED; ANATOMY_ARROWS_NOT_VERIFIED"
  for panel in data.get("visual_comparison",{}).get("items",[]):
   if panel.get("image_url")==old or "Muhlenbergia%20utilis.jpg" in str(panel.get("image_url","")):
    panel["image_url"]=str(root/rel)
  data.setdefault("learner_visual_status",{})["image_count"]=len(data["images"])
  data["learner_visual_status"]["status"]="FIELD_READY_PHOTO_GAPS"
  data["learner_visual_status"]["note"]="Three local photographs. Ligule, collar and scale-referenced mature spikelet microphotographs remain unverified."
  data.setdefault("curation_status",{})["photo_files_present"]=sum(x.get("file","").startswith("images/") for x in data["images"])
  card.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
  report["added"].append({"file":str(dest),"license":lic,"creator":"Romey Swanson","sha256":img["physical_archive_sha256"]})
 except Exception as exc:report["holds"].append(str(exc)[:250])
pathlib.Path("reports/lane3-muhlenbergia-utilis-20261023.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
