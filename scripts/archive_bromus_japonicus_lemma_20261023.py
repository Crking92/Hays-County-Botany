#!/usr/bin/env python3
"""Archive one new Wikimedia exact-species lemma macro with image-level rights evidence."""
import io,json,pathlib,urllib.request,urllib.parse,hashlib,time,html,re
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Bromus/bromus-japonicus")
species_path=base/"species.json"
d=json.loads(species_path.read_text(encoding="utf-8"))
assert d["id"]=="bromus-japonicus"
title="File:Bromus japonicus sl25.jpg"
source="https://commons.wikimedia.org/wiki/File:Bromus_japonicus_sl25.jpg"
out=base/"images"/"stefan-lefnaer-bromus-japonicus-lemma-awn.jpg"
report={"source":source,"status":"HOLD","role":"Mature lemmas with membranous margins and attached awns (source-described; fine anatomy review pending)"}
def get(url):
 for i in range(4):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotany/1.0 botany education"})
   with urllib.request.urlopen(req,timeout=60) as f:return f.read()
  except Exception:
   if i==3:raise
   time.sleep(8*(i+1))
try:
 api="https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url%7Cextmetadata&format=json&titles="+urllib.parse.quote(title)
 inf=next(iter(json.loads(get(api))["query"]["pages"].values()))["imageinfo"][0]
 meta=inf["extmetadata"]
 license=html.unescape(re.sub("<[^>]+>","",meta["LicenseShortName"]["value"])).strip()
 assert license.replace("-","").replace(" ","").upper()=="CCBYSA4.0",license
 creator=html.unescape(re.sub("<[^>]+>","",meta.get("Artist",{}).get("value",""))).strip()
 assert "Stefan" in creator,creator
 raw=get(inf["url"])
 assert 20000<len(raw)<15000000
 img=Image.open(io.BytesIO(raw))
 img.verify()
 img=Image.open(io.BytesIO(raw)).convert("RGB")
 assert img.width>=900 and img.height>=900,img.size
 if not out.exists():
  out.parent.mkdir(exist_ok=True,parents=True)
  img.save(out,"JPEG",quality=88,optimize=True)  # no source EXIF/GPS
  existing=next((x for x in d["images"] if x.get("source_page")==source),None)
  new_record={"file":"images/"+out.name,"role":"Exact-species source-labelled mature lemmas with membranous margin and awn; source-photo anatomical placement provisional","creator":"Stefan.lefnaer","license":"CC BY-SA 4.0","license_url":"https://creativecommons.org/licenses/by-sa/4.0/","source_page":source,"photo_status":"PROVISIONAL — USER PHOTO REVIEW PENDING; no new anatomy arrows","public_reuse":"CC BY-SA 4.0 attribution, source and modified-JPEG indication required","modifications":"Converted to RGB and re-encoded with metadata/EXIF removed"}
  if existing is not None: existing.update(new_record)
  else: d["images"].append(new_record)
  d["learner_visual_status"]["image_count"]=len(d["images"])
  d["curation_status"]["photo_metadata_count"]=len(d["images"])
  species_path.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
  report.update(status="ARCHIVED",local_file=str(out),sha256=hashlib.sha256(out.read_bytes()).hexdigest(),size=out.stat().st_size,license=license)
 else:report["status"]="ALREADY_ARCHIVED"
except Exception as exc:report["error"]=str(exc)
dest=pathlib.Path("reports/bromus-japonicus-lemma-20261023.json")
dest.parent.mkdir(parents=True,exist_ok=True)
dest.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
