#!/usr/bin/env python3
"""Archive historical Chloris hybrid plate with explicit figure distinctions."""
import io,json,pathlib,time,urllib.parse,urllib.request,urllib.error
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Chloris/chloris-x-subdolichostachya")
path=base/"species.json";doc=json.loads(path.read_text());assert doc["id"]=="chloris-x-subdolichostachya"
title="File:Manual of the grasses of the United States (Page 529) BHL42021168.jpg"
outcome={"archive":"Chloris hybrid manual plate","added":False,"holds":[]}
def fetch(url):
 for attempt in range(4):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotany/1.0 (public botanical educational archive)"}),timeout=60) as resp:return resp.read()
  except urllib.error.HTTPError as err:
   if err.code not in (429,500,502,503,504) or attempt==3:raise
   time.sleep(25*(attempt+1))
try:
 api="https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url%7Cextmetadata&format=json&titles="+urllib.parse.quote(title)
 pages=json.loads(fetch(api))["query"]["pages"]
 info=next(iter(pages.values()))["imageinfo"][0]
 lic=info["extmetadata"]["LicenseShortName"]["value"]
 normalized=lic.upper().replace(" ","").replace("-","")
 assert normalized in ("PUBLICDOMAIN","PDM","NORESTRICTIONS","CC0"),"Not public domain: "+lic
 raw=fetch(info["url"]);assert 15000<len(raw)<22000000
 im=Image.open(io.BytesIO(raw));im.verify();im=Image.open(io.BytesIO(raw)).convert("RGB")
 assert min(im.size)>=700
 dest=base/"images"/"hitchcock-chase-chloris-hybrid-plate-p529.jpg"
 dest.parent.mkdir(parents=True,exist_ok=True);im.save(dest,"JPEG",quality=92,optimize=True)
 entry={"file":"images/"+dest.name,"role":"HISTORICAL COMPARISON PLATE: figure 768 illustrates Chloris subdolichostachya, while figure 770 illustrates DIFFERENT SPECIES C. cucullata; not a modern specimen photograph.","creator":"A. S. Hitchcock and A. Chase, Manual of the Grasses of the United States, p. 529","license":lic,"source_page":"https://commons.wikimedia.org/wiki/File:Manual_of_the_grasses_of_the_United_States_(Page_529)_BHL42021168.jpg","photo_status":"ILLUSTRATION — figures for multiple species, not authenticated hybrid field macro; no new arrows","public_reuse":"Historical public-domain image; preserve figure-level IDs and source credits"}
 if not any(z.get("file")==entry["file"] for z in doc["images"]):doc["images"].append(entry)
 doc.setdefault("curation_status",{})["photo_metadata_count"]=len(doc["images"])
 doc.setdefault("learner_visual_status",{})["image_count"]=len(doc["images"])
 path.write_text(json.dumps(doc,indent=2,ensure_ascii=False)+"\n")
 outcome["added"]=True
except Exception as exc:outcome["holds"].append(str(exc))
report=pathlib.Path("reports/chloris-hybrid-historical-plate-archive.json");report.parent.mkdir(exist_ok=True)
report.write_text(json.dumps(outcome,indent=2)+"\n")
print(json.dumps(outcome))
