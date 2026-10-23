#!/usr/bin/env python3
"""Rights-gated attempt to add Urochloa reptans photographs (not herbarium stand-ins)."""
import json,io,pathlib,time,urllib.parse,urllib.request,urllib.error,re,html,hashlib
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Urochloa/urochloa-reptans");path=base/"species.json";d=json.loads(path.read_text());assert d["id"]=="urochloa-reptans"
def fetch(url):
 for attempt in range(4):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotany/1.0 (public botanical teaching archive)"}),timeout=60) as f:return f.read()
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or attempt==3: raise
   time.sleep(25*(attempt+1))
def query(params):
 return json.loads(fetch("https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(params)))
category="Category:Urochloa reptans"
report={"category":category,"added":[],"held":[],"policy":"Only exact species and public-reusable photographs, exclude herbarium sheets"}
try:
 print("Beginning Urochloa reptans source rights review",flush=True)
 members=query({"action":"query","list":"categorymembers","cmtitle":category,"cmtype":"file","cmlimit":50,"format":"json"})["query"]["categorymembers"]
 print("Exact taxon files found:",len(members),flush=True)
 for item in members:
  if len(report["added"])>=2:break
  title=item["title"]
  if "herbarium" in title.lower() or "(AM AK" in title:continue
  try:
   info=next(iter(query({"action":"query","prop":"imageinfo","iiprop":"url|extmetadata","titles":title,"format":"json"})["query"]["pages"].values()))["imageinfo"][0]
   md=info["extmetadata"];license=md.get("LicenseShortName",{}).get("value","");normalized=license.upper().replace(" ","").replace("-","")
   assert normalized in ("CC0","PUBLICDOMAIN","CCBY2.0","CCBY3.0","CCBY3.0US","CCBY4.0","CCBYSA2.0","CCBYSA3.0","CCBYSA4.0"),"Ineligible license: "+license
   author=html.unescape(re.sub("<[^>]*>","",md.get("Artist",{}).get("value",""))).strip()
   assert author,"No creator identified"
   raw=fetch(info["url"]);assert 12000<len(raw)<20000000
   photo=Image.open(io.BytesIO(raw));photo.verify();photo=Image.open(io.BytesIO(raw)).convert("RGB")
   assert min(photo.size)>=500
   name="commons-"+hashlib.sha256(title.encode()).hexdigest()[:12]+".jpg"
   page="https://commons.wikimedia.org/wiki/"+urllib.parse.quote(title.replace(" ","_"))
   if any(x.get("file")=="images/"+name or x.get("source_page")==page for x in d["images"]):continue
   out=base/"images"/name;out.parent.mkdir(parents=True,exist_ok=True);photo.save(out,"JPEG",quality=91,optimize=True)
   d["images"].append({"file":"images/"+name,"role":"Species-labelled Urochloa reptans living plant reference; anatomy requires visual confirmation","creator":author,"license":license,"source_page":page,"photo_status":"PROVISIONAL — species attribution and anatomical arrow review outstanding","public_reuse":"Commons image-level rights checked"})
   report["added"].append(title)
  except Exception as ex:report["held"].append({"title":title,"reason":str(ex)})
except Exception as ex:report["held"].append({"category":category,"reason":str(ex)})
if report["added"]:
 d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
 d.setdefault("curation_status",{})["photo_metadata_count"]=len(d["images"])
 path.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n")
report["gallery_count"]=len(d["images"])
dest=pathlib.Path("reports/urochloa-reptans-one-photo-recovery.json");dest.parent.mkdir(exist_ok=True);dest.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
