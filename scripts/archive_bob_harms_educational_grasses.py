#!/usr/bin/env python3
"""Archive Bob Harms Selected Monocots scientific/educational photos with source credit.
Site-specific educational permission, NOT Creative Commons. No image substitutions.
"""
import json,pathlib,urllib.request,urllib.error,urllib.parse,io,time,hashlib
from PIL import Image
root=pathlib.Path(".")
m=json.loads((root/"data/manifest.json").read_text())["species"]
report={"permission":"Bob Harms Selected Monocots author permission for scientific and educational use with credit; https://w3.biosci.utexas.edu/prc/Monocots/","archived":[],"holds":[],"limits":"Credit mandatory; NOT Creative Commons or blanket redistribution permission"}
def fetch(u):
 for i in range(4):
  try:
   with urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Hays County Botany educational image archive/1.0"}),timeout=50) as f:return f.read()
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or i==3:raise
   time.sleep(20*(i+1))
def remap(o,mp):
 if isinstance(o,dict):return {k:remap(v,mp) for k,v in o.items()}
 if isinstance(o,list):return [remap(x,mp) for x in o]
 if isinstance(o,str):return mp.get(o,o)
 return o
for item in m:
 if "/Poaceae/" not in item["path"]:continue
 path=root/item["path"];d=json.loads(path.read_text())
 targets=[(ix,x) for ix,x in enumerate(d.get("images",[])) if x.get("file","").startswith("https://w3.biosci.utexas.edu/prc/Monocots/GrassHTML/data/images/")]
 if not targets:continue
 changed=False
 for ix,x in targets:
  url=x["file"]
  try:
   assert "Bob Harms" in x.get("creator",""),"Author not identified as Bob Harms"
   assert "Selected Monocots" in report["permission"]
   content=fetch(url);assert 5000<len(content)<24000000
   image=Image.open(io.BytesIO(content));image.verify();image=Image.open(io.BytesIO(content)).convert("RGB")
   assert min(image.size)>300,"Image too small"
   filename="bob-harms-ut-"+hashlib.sha256(url.encode()).hexdigest()[:14]+".jpg"
   dest=path.parent/"images"/filename;dest.parent.mkdir(exist_ok=True,parents=True);image.save(dest,"JPEG",quality=92,optimize=True)
   new="images/"+filename
   # Deep remap gallery visual panels but retain original source URLs and credits.
   original=url
   mp={original:str(dest).replace("\\","/")}
   d=remap(d,mp);x=d["images"][ix]
   x["file"]=new
   x["archived_original_url"]=original
   x["archive_license_basis"]="Author-permitted scientific/educational use with Bob Harms attribution; NOT CC"
   x["archive_status"]="LOCALLY_STORED_PROVISIONAL; retain original photo anatomy and scale"
   changed=True
   report["archived"].append({"species":item["id"],"original":original,"local":str(dest)})
  except Exception as e:report["holds"].append({"species":item["id"],"url":url,"reason":str(e)})
 if changed:
  d.setdefault("learner_visual_status",{})["image_count"]=len(d.get("images",[]))
  path.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
out=root/"reports"/"bob-harms-grass-education-photo-archive.json";out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
print("UT educational archive",len(report["archived"]),"holds",len(report["holds"]))
