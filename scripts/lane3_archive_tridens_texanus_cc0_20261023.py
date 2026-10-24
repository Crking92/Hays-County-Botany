#!/usr/bin/env python3
"""Archive 3 source-labelled, CC0 Tridens texanus Wikimedia images, no speculative arrows."""
import io,json,pathlib,urllib.request,urllib.parse,hashlib
from PIL import Image,ImageOps
root=pathlib.Path("content/taxa/Poaceae/Tridens/tridens-texanus")
card=root/"species.json";d=json.loads(card.read_text());assert d["id"]=="tridens-texanus"
report={"species":"tridens-texanus","added":[],"holds":[]}
expected={"Tridens texanus (2).jpg":"texas-tridens-gaiacoyote-spikelets-cc0.jpg","Tridens texanus (4).jpg":"texas-tridens-gaiacoyote-ligule-cc0.jpg","Tridens texanus (5).jpg":"texas-tridens-gaiacoyote-habit-cc0.jpg"}
def get(url):
 req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyVisualLearner/1.0 (source credited Wikimedia taxon photo archival; github.com/Crking92/Hays-County-Botany)"})
 with urllib.request.urlopen(req,timeout=40) as r:return r.read(18000001)
for filename,local in expected.items():
 try:
  api="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo","iiprop":"url|extmetadata","titles":"File:"+filename})
  info=next(iter(json.loads(get(api))["query"]["pages"].values()))["imageinfo"][0];ext=info["extmetadata"]
  license_name=ext.get("LicenseShortName",{}).get("value","")
  assert "CC0" in license_name or "Public domain" in license_name, "rights not verified: "+license_name
  url=info["url"];match=next((im for im in d["images"] if im["file"]==url),None)
  assert match is not None, "original image URL not same as canonical source record"
  raw=get(url)
  with Image.open(io.BytesIO(raw)) as im:im.verify()
  with Image.open(io.BytesIO(raw)) as im:
   im=ImageOps.exif_transpose(im).convert("RGB")
   if min(im.size)<450:raise ValueError("image too small")
   im.thumbnail((2000,2000));buf=io.BytesIO();im.save(buf,"JPEG",quality=87,optimize=True);blob=buf.getvalue()
  dest=root/"images"/local
  if dest.exists():raise ValueError("already archived, existing file protected")
  dest.write_bytes(blob)
  original=match["file"];match["file"]="images/"+local
  match["original_media_url"]=url;match["physical_archive_sha256"]=hashlib.sha256(blob).hexdigest()
  match["photo_status"]="CC0 source-labelled local JPEG; submillimeter anatomy not certified"
  for panel in d.get("visual_comparison",{}).get("items",[]):
   if panel.get("image_url")==original:
    panel["image_url"]=str(root/match["file"])
    panel["photo_status"]="LOCALLY_ARCHIVED_CC0__STRUCTURE_ARROW_HOLD"
  report["added"].append({"source":filename,"file":str(dest),"sha256":match["physical_archive_sha256"],"license":license_name})
 except Exception as exc:report["holds"].append({"source":filename,"reason":str(exc)[:230]})
if report["added"]:
 d["learner_visual_status"]["status"]="FIELD_READY_PHOTO_GAPS"
 d["learner_visual_status"]["image_count"]=len(d["images"])
 d["learner_visual_status"]["note"]="Five species photo records; source-licensed reproductions being localized. Microscopic ligule dimensions, glume/lemma and nerve hairs not independently confirmed."
 d["curation_status"]["photo_files_present"]=sum(z.get("file","").startswith("images/") for z in d["images"])
 d["curation_status"]["photo_metadata_count"]=len(d["images"])
 card.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
pathlib.Path("reports/lane3-tridens-texanus-cc0-20261023.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
