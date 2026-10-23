#!/usr/bin/env python3
"""Archive two existing public-domain USGS red lovegrass images."""
import io,json,pathlib,urllib.request,hashlib
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Eragrostis/eragrostis-secundiflora")
p=base/"species.json"
d=json.loads(p.read_text())
assert d["id"]=="eragrostis-secundiflora"
report={"species":d["id"],"results":[]}
for idx,name in [(0,"usgs-red-lovegrass-habit.jpg"),(1,"usgs-red-lovegrass-inflorescence.jpg")]:
 rec=d["images"][idx]
 original=rec["file"]
 status={"index":idx,"url":original,"status":"HOLD"}
 try:
  assert original.startswith("https://warcapps.usgs.gov/PlantID/Image/")
  assert rec["creator"]=="Larry Allain, U.S. Geological Survey"
  assert "Public Domain" in rec["license"]
  req=urllib.request.Request(original,headers={"User-Agent":"HaysCountyBotany/1.0"})
  with urllib.request.urlopen(req,timeout=55) as response:raw=response.read()
  assert 15000<len(raw)<15000000
  img=Image.open(io.BytesIO(raw));img.verify()
  img=Image.open(io.BytesIO(raw)).convert("RGB")
  assert min(img.size)>=500
  target=base/"images"/name
  target.parent.mkdir(parents=True,exist_ok=True)
  img.save(target,"JPEG",quality=90,optimize=True)
  rec["original_source_url"]=original
  rec["file"]="images/"+name
  rec["photo_status"]="PHYSICALLY ARCHIVED FROM USGS — field anatomy only, no counted florets or ligule"
  rec["modifications"]="Re-encoded RGB JPEG without metadata/EXIF"
  status.update(status="ARCHIVED",sha256=hashlib.sha256(target.read_bytes()).hexdigest(),size=target.stat().st_size)
 except Exception as exc:status["error"]=str(exc)
 report["results"].append(status)
if any(x["status"]=="ARCHIVED" for x in report["results"]):
 d["curation_status"]["photo_files_present"]=sum(im["file"].startswith("images/") for im in d["images"])
 p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
dest=pathlib.Path("reports/eragrostis-secundiflora-usgs-archive-20261023.json")
dest.parent.mkdir(exist_ok=True,parents=True)
dest.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
