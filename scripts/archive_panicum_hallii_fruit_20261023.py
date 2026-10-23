#!/usr/bin/env python3
"""Archive CC0 Panicum hallii hardened mature fruit closeup; no anatomy arrow claims."""
import json,io,pathlib,urllib.request,urllib.parse,hashlib,time
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Panicum/panicum-hallii")
p=base/"species.json"; d=json.loads(p.read_text()); assert d["id"]=="panicum-hallii"
source="https://commons.wikimedia.org/wiki/File:Panicum_hallii_-_Flickr_-_aspidoscelis.jpg"
name="patrick-alexander-hallii-glossy-fruits.jpg"; dest=base/"images"/name
report={"source":source,"status":"HOLD"}
try:
 def get(url):
  for attempt in range(4):
   try:
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotany/1.0 (noncommercial botanical learner)"}),timeout=55) as response:return response.read()
   except Exception:
    if attempt==3:raise
    time.sleep(8*(attempt+1))
 api="https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url%7Cextmetadata&format=json&titles="+urllib.parse.quote("File:Panicum hallii - Flickr - aspidoscelis.jpg")
 inf=next(iter(json.loads(get(api))["query"]["pages"].values()))["imageinfo"][0]
 lic=inf["extmetadata"]["LicenseShortName"]["value"]
 assert "CC0" in lic.upper() or "CC-ZERO" in lic.upper(),lic
 raw=get(inf["url"]);assert 20000<len(raw)<15000000
 image=Image.open(io.BytesIO(raw));image.verify()
 image=Image.open(io.BytesIO(raw)).convert("RGB")
 assert image.width>=2000 and image.height>=1400,image.size
 if not dest.exists():
  dest.parent.mkdir(parents=True,exist_ok=True)
  image.save(dest,format="JPEG",quality=90,optimize=True)
 record={"file":"images/"+name,"role":"Close-up of separated glossy mature fruiting units; photograph source determined Panicum hallii, no scale or exposed glumes/ligule","creator":"Patrick Alexander","license":"CC0 1.0","source_page":source,"source_locality":"Grant County, New Mexico (not Hays-vouchered)","photo_status":"PROVISIONAL — USER PHOTO REVIEW PENDING; exact fertile unit anatomy not independently dissected","public_reuse":"CC0; voluntary creator/source credit","modifications":"Re-encoded RGB JPEG without EXIF/GPS","anatomy_limits":"Displays smooth glossy fruiting units; cannot show original glume venation, fertile lemma dissection, ligule, or measured millimeters."}
 existing=next((x for x in d["images"] if x.get("source_page")==source),None)
 if existing:existing.update(record)
 else:d["images"].append(record)
 d["learner_visual_status"]["image_count"]=len(d["images"])
 d["curation_status"]["photo_metadata_count"]=len(d["images"])
 quick=d.setdefault("field_photo_quickcheck",{})
 featured=quick.setdefault("featured_photo_indices",[])
 i=next(i for i,x in enumerate(d["images"]) if x["source_page"]==source)
 if i not in featured:featured.append(i)
 p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
 report.update(status="ARCHIVED",local_file=str(dest),sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),bytes=dest.stat().st_size,image_dimensions=list(image.size))
except Exception as e:report["error"]=str(e)
out=pathlib.Path("reports/panicum-hallii-glossy-fruit-20261023.json");out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
