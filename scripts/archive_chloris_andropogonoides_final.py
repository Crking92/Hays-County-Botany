#!/usr/bin/env python3
"""Source-gated, image-level licensed Chloris andropogonoides archive."""
import json, pathlib, urllib.parse, urllib.request, urllib.error, time, io, re, html, hashlib
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Chloris/chloris-andropogonoides")
p=base/"species.json";d=json.loads(p.read_text());assert d["id"]=="chloris-andropogonoides"
report={"added":[],"holds":[],"candidates":[]}
def load(url):
 for n in range(5):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotany/1.0 (educational botany archive)"}),timeout=65) as resp:return resp.read()
  except urllib.error.HTTPError as exc:
   if exc.code not in (429,500,502,503,504) or n==4:raise
   time.sleep(20*(n+1))
def commons(args):return json.loads(load("https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(args)))
try:
 # Commons indexes multiple possible sources under this exact taxon category.
 members=commons({"action":"query","list":"categorymembers","cmtitle":"Category:Chloris andropogonoides","cmtype":"file","cmlimit":50,"format":"json"}).get("query",{}).get("categorymembers",[])
 for member in members:
  if len(report["added"])>=2:break
  title=member["title"];report["candidates"].append(title)
  try:
   q=commons({"action":"query","prop":"imageinfo","iiprop":"url|extmetadata","titles":title,"format":"json"})
   info=next(iter(q["query"]["pages"].values()))["imageinfo"][0]
   md=info["extmetadata"];lic=md.get("LicenseShortName",{}).get("value","")
   norm=lic.upper().replace("-","").replace(" ","")
   assert norm in ("CC0","PUBLICDOMAIN","PDM","NORESTRICTIONS","CCBY2.0","CCBY3.0","CCBY3.0US","CCBY4.0","CCBYSA2.0","CCBYSA3.0","CCBYSA4.0"),"License not suitable: "+lic
   artist=html.unescape(re.sub("<[^>]*>","",md.get("Artist",{}).get("value",""))).strip()
   assert artist or norm in ("PUBLICDOMAIN","PDM","NORESTRICTIONS"),"Missing creator credit"
   raw=load(info["url"]);assert 10000<len(raw)<20000000
   img=Image.open(io.BytesIO(raw));img.verify()
   img=Image.open(io.BytesIO(raw)).convert("RGB");assert min(img.size)>=450
   name="commons-"+hashlib.sha256(title.encode()).hexdigest()[:12]+".jpg"
   url="https://commons.wikimedia.org/wiki/"+urllib.parse.quote(title.replace(" ","_"))
   if any(x.get("file")=="images/"+name or x.get("source_page")==url for x in d["images"]):continue
   dest=base/"images"/name;dest.parent.mkdir(parents=True,exist_ok=True);img.save(dest,"JPEG",quality=91,optimize=True)
   role="Historical source illustration, anatomy awaiting review" if any(w in title.lower() for w in ("manual","flora","plate","herbarium")) else "Exact-taxon photographic recognition reference; spikelet/lemma identity requires pixel review"
   d["images"].append({"file":"images/"+name,"role":role,"creator":artist or "Historic source (see Commons)","license":lic,"source_page":url,"photo_status":"PROVISIONAL — do not assert diagnostic anatomy or add arrows without review","public_reuse":"Image-level open license checked; credit and SA preserved"})
   report["added"].append(title)
  except Exception as exc:report["holds"].append({"file":title,"reason":str(exc)})
except Exception as exc:report["holds"].append({"category":"Chloris andropogonoides","reason":str(exc)})
if report["added"]:
 d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
 d.setdefault("curation_status",{})["photo_metadata_count"]=len(d["images"])
 p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
report["gallery_count"]=len(d["images"])
r=pathlib.Path("reports/chloris-andropogonoides-final-recovery.json");r.parent.mkdir(exist_ok=True);r.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
