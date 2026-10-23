#!/usr/bin/env python3
"""Targeted rights-gated recovery of a Bromus japonicus spikelet photograph."""
import io,json,pathlib,time,urllib.request,urllib.error,urllib.parse,hashlib,html,re
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Bromus/bromus-japonicus");p=base/"species.json";d=json.loads(p.read_text());assert d["id"]=="bromus-japonicus"
files=["Bromus japonicus (3860476601).jpg","Bromus japonicus (3920836312).jpg"]
report={"added":[],"holds":[]}
def get(url):
 for n in range(5):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotany/1.0 (public-grass-identification)"}),timeout=65) as f:return f.read()
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or n==4:raise
   time.sleep(25*(n+1))
for filename in files:
 if report["added"]:break
 try:
  title="File:"+filename
  api="https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url%7Cextmetadata&format=json&titles="+urllib.parse.quote(title)
  pages=json.loads(get(api))["query"]["pages"];info=next(iter(pages.values()))["imageinfo"][0];meta=info["extmetadata"]
  license=meta["LicenseShortName"]["value"];norm=license.upper().replace("-","").replace(" ","")
  assert norm in ("CCBYSA2.0","CCBYSA3.0","CCBYSA4.0","CCBY2.0","CCBY3.0","CCBY4.0"),license
  creator=html.unescape(re.sub("<[^>]+>","",meta.get("Artist",{}).get("value",""))).strip()
  assert creator,"Missing creator in Commons metadata"
  raw=get(info["url"]);assert 12000<len(raw)<16000000
  im=Image.open(io.BytesIO(raw));im.verify();im=Image.open(io.BytesIO(raw)).convert("RGB")
  assert min(im.size)>=400
  local="commons-bromus-japonicus-"+hashlib.sha256(filename.encode()).hexdigest()[:12]+".jpg"
  source="https://commons.wikimedia.org/wiki/"+urllib.parse.quote(title.replace(" ","_"))
  out=base/"images"/local;out.parent.mkdir(parents=True,exist_ok=True);im.save(out,"JPEG",quality=91,optimize=True)
  if not any(x.get("file")=="images/"+local or x.get("source_page")==source for x in d["images"]):
   d["images"].append({"file":"images/"+local,"role":"Exact-species Japanese brome inflorescence/spikelet detail; awn and lemma characters require close pixel review","creator":creator,"license":license,"source_page":source,"public_reuse":"Commons image-level rights checked; creator attribution and ShareAlike if applicable","photo_status":"PROVISIONAL — anatomy and arrow placement require visual check"})
  report["added"].append(filename)
 except Exception as e:report["holds"].append({"file":filename,"error":str(e)})
if report["added"]:
 d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
 d.setdefault("curation_status",{})["photo_metadata_count"]=len(d["images"])
 p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
report["gallery_count"]=len(d["images"])
dest=pathlib.Path("reports/bromus-japonicus-spikelet-recovery.json");dest.parent.mkdir(exist_ok=True);dest.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
