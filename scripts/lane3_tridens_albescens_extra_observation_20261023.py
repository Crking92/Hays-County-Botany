#!/usr/bin/env python3
"""Archive additional licensed exact-observation white tridens photographs, no inferred anatomical arrows."""
import json,io,pathlib,urllib.request,hashlib
from PIL import Image,ImageOps
root=pathlib.Path("content/taxa/Poaceae/Tridens/tridens-albescens");card=root/"species.json"
d=json.loads(card.read_text());assert d["id"]=="tridens-albescens"
report={"species":"tridens-albescens","observation":408110125,"added":[],"holds":[]}
def get(url):
 req=urllib.request.Request(url,headers={"User-Agent":"HaysBotany/1.0 (botanical CC photo review; github.com/Crking92/Hays-County-Botany)"})
 with urllib.request.urlopen(req,timeout=40) as r:return r.read(16000001)
try:
 rows=json.loads(get("https://api.inaturalist.org/v1/observations/408110125"))["results"]
 assert len(rows)==1
 ob=rows[0]; assert (ob.get("taxon") or {}).get("name")=="Tridens albescens","species name does not match"
 assert ob.get("quality_grade")=="research","research grade check failed"
 for photo in ob.get("photos",[]):
  pid=photo.get("id");license=(photo.get("license_code") or "").lower()
  if not pid or license not in ("cc-by","cc-by-sa","cc0"):continue
  if any(str(pid) in str(x.get("source_page","")) for x in d["images"]):continue
  try:
   u=photo["url"].replace("/square.","/large.").replace("/medium.","/large.")
   raw=get(u)
   with Image.open(io.BytesIO(raw)) as im:im.verify()
   with Image.open(io.BytesIO(raw)) as im:
    im=ImageOps.exif_transpose(im).convert("RGB")
    if min(im.size)<450:raise ValueError("insufficient resolution")
    im.thumbnail((1600,1600));b=io.BytesIO();im.save(b,"JPEG",quality=88,optimize=True);data=b.getvalue()
   rel="images/inat-open-"+str(pid)+".jpg";target=root/rel
   if target.exists():continue
   target.write_bytes(data)
   credit=photo.get("attribution") or "iNaturalist source attribution"
   d["images"].append({"file":rel,"role":"Exact-taxon research-grade source observation, diagnostic organ unverified","creator":credit,"license":license.upper(),"source_page":"https://www.inaturalist.org/photos/"+str(pid),"observation_page":"https://www.inaturalist.org/observations/408110125","source_determination":"Tridens albescens, iNaturalist Research Grade","photo_status":"LOCAL_PUBLIC_LICENSE_PHOTO_ANATOMY_HOLD","sha256":hashlib.sha256(data).hexdigest(),"modifications":"Resized, EXIF removed"})
   d["visual_comparison"]["items"].append({"label":"White tridens — further source-observation photograph","scientific_name":"Tridens albescens","image_url":str(root/rel),"image_fit":"contain","image_role":"Source-identified real photo; microanatomy unverified","caption":"Additional same-observation source photo. Examine mature panicle and spikelet form; ligule and glume measurements not visually certified.","creator":credit,"license":license.upper(),"source_page":"https://www.inaturalist.org/photos/"+str(pid),"markers":[]})
   report["added"].append({"file":str(target),"photo":pid,"license":license})
  except Exception as e:report["holds"].append({"photo":pid,"reason":str(e)[:180]})
 if report["added"]:
  d["learner_visual_status"]["image_count"]=len(d["images"]);d["learner_visual_status"]["status"]="FIELD_READY_PHOTO_GAPS"
  d["curation_status"]["photo_metadata_count"]=len(d["images"]);d["curation_status"]["photo_files_present"]=len(d["images"])
  card.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
except Exception as e:report["holds"].append({"stage":"source","reason":str(e)[:250]})
pathlib.Path("reports/lane3-tridens-albescens-observation-20261023.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
