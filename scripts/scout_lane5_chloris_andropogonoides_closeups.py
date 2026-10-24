#!/usr/bin/env python3
"""Scout missing Chloris andropogonoides exact-voucher photographs, no site publish.
Stores small embedded contact previews for anatomy inspection before admission.
"""
import json, pathlib, urllib.request, io, base64, time, hashlib
from PIL import Image
OUT=pathlib.Path("reports/lane5-chloris-andropogonoides-scout-20261024.json")
OUT.parent.mkdir(parents=True,exist_ok=True)
def get(url):
 req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyVisualLearner/1.0 (educational photo and license research)","Accept":"application/json, image/jpeg"})
 with urllib.request.urlopen(req,timeout=35) as res:return res.read()
result={"taxon":"Chloris andropogonoides","observation_id":197976375,"photos":[],"errors":[],"policy":"Do not archive originals or annotate before inspecting actual pixels and verifying each photo license; research-grade source alone is not independent specimen confirmation"}
try:
 obs=json.loads(get("https://api.inaturalist.org/v1/observations/197976375"))["results"][0]
 result["observation_taxon"]=obs.get("taxon",{}).get("name")
 result["quality_grade"]=obs.get("quality_grade")
 if result["observation_taxon"]!="Chloris andropogonoides":raise ValueError("Observation taxon mismatch")
 for pic in obs.get("photos",[])[:12]:
  code=pic.get("license_code","")
  if code not in ("cc-by","cc-by-sa","cc0"):continue
  url=pic.get("url","").replace("/square.","/large.")
  if not url:continue
  entry={"id":pic.get("id"),"license":code,"attribution":pic.get("attribution"),"url":url,"observation_id":obs.get("id")}
  try:
   im=Image.open(io.BytesIO(get(url)));im.verify()
   im=Image.open(io.BytesIO(get(url))).convert("RGB")
   entry["size"]=list(im.size)
   im.thumbnail((300,300))
   buf=io.BytesIO();im.save(buf,format="JPEG",quality=62)
   entry["preview_base64"]=base64.b64encode(buf.getvalue()).decode("ascii")
   entry["image_bytes_sha256_preview"]=hashlib.sha256(buf.getvalue()).hexdigest()
  except Exception as e:entry["error"]=str(e)[:230]
  result["photos"].append(entry)
except Exception as e:result["errors"].append(str(e)[:300])
OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"taxon":result.get("observation_taxon"),"count":len(result["photos"]),"photos":[{k:v for k,v in p.items() if k!="preview_base64"} for p in result["photos"]],"errors":result["errors"]}))
