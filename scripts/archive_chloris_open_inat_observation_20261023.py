#!/usr/bin/env python3
"""Search exact-species iNaturalist observations for reusable, verified photo metadata."""
import json, urllib.request, urllib.parse, pathlib, io, hashlib
from PIL import Image, ImageOps
root=pathlib.Path("content/taxa/Poaceae/Chloris/chloris-andropogonoides")
card=root/"species.json"; report=pathlib.Path("reports/chloris-inat-open-search-20261023.json")
d=json.loads(card.read_text()); assert d["id"]=="chloris-andropogonoides"
out={"added":[],"holds":[],"scanned":0,"strategy":"iNat observations API; taxon 160518; individual photo CC-BY/CC-BY-SA/CC0 rights"}
def fetch(url):
 req=urllib.request.Request(url,headers={"User-Agent":"Hays-County-Botany/1.0 (attributed open photo research)","Accept":"application/json,image/*"})
 with urllib.request.urlopen(req,timeout=40) as r:
  b=r.read(16000001)
 if len(b)>16000000:raise ValueError("Oversized response")
 return b
try:
 for page in range(1,5):
  if out["added"]: break
  query=urllib.parse.urlencode({"taxon_id":160518,"quality_grade":"research","photos":"true","per_page":40,"page":page,"order_by":"observed_on","order":"desc"})
  rows=json.loads(fetch("https://api.inaturalist.org/v1/observations?"+query))["results"]
  for ob in rows:
   out["scanned"]+=1
   tax=ob.get("taxon") or {}
   if tax.get("id")!=160518 or tax.get("rank")!="species":continue
   for entry in ob.get("photos",[]):
    code=(entry.get("license_code") or "").lower()
    if code not in ("cc-by","cc-by-sa","cc0"):continue
    image_id=entry.get("id")
    if not image_id:continue
    source="https://www.inaturalist.org/photos/"+str(image_id)
    if any(x.get("source_page")==source for x in d["images"]):continue
    url=entry.get("url") or ""
    if not url.startswith("https://"):continue
    photo_url=url.replace("/square.","/large.").replace("/medium.","/large.")
    try:
     raw=fetch(photo_url)
     with Image.open(io.BytesIO(raw)) as im: im.verify()
     with Image.open(io.BytesIO(raw)) as im:
      im=ImageOps.exif_transpose(im).convert("RGB")
      if min(im.size)<450:continue
      im.thumbnail((1600,1600));buf=io.BytesIO();im.save(buf,"JPEG",quality=86,optimize=True)
      data=buf.getvalue()
     creator=entry.get("attribution") or (ob.get("user") or {}).get("login") or "iNaturalist credited source"
     filename="inat-open-"+str(image_id)+".jpg";dest=root/"images"/filename
     dest.parent.mkdir(exist_ok=True);dest.write_bytes(data)
     with Image.open(dest) as im:im.verify()
     d["images"].append({"file":"images/"+filename,"role":"Research-grade exact-taxon field recognition photo; reproductive characters not independently measured","creator":creator,"license":code.upper(),"source_page":source,"observation_page":"https://www.inaturalist.org/observations/"+str(ob["id"]),"source_determination":"Chloris andropogonoides, iNaturalist research grade","public_reuse":"Individual photo Creative Commons license; source and author retained","modifications":"Resized and embedded metadata removed","sha256":hashlib.sha256(data).hexdigest(),"photo_status":"ARCHIVED_OPEN_LICENSE_PROVISIONAL_IDENTIFICATION"})
     out["added"].append({"file":str(dest),"observation":ob["id"],"photo":image_id,"license":code})
     break
    except Exception as e:out["holds"].append({"photo":image_id,"reason":str(e)[:180]})
   if out["added"]:break
 if out["added"]:
  d.setdefault("curation_status",{})["photo_files_present"]=len(d["images"])
  d["curation_status"]["photo_metadata_count"]=len(d["images"])
  d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
  card.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
except Exception as e:out["holds"].append({"search_error":str(e)[:300]})
report.write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps(out))
