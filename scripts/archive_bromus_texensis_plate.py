#!/usr/bin/env python3
"""Archive an exact-species Texas brome plate only after Commons rights validation."""
import io,json,pathlib,time,urllib.request,urllib.error,urllib.parse,html,re
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Bromus/bromus-texensis")
p=base/"species.json";d=json.loads(p.read_text());assert d["id"]=="bromus-texensis"
report={"added":[],"held":[]}
def get(url):
 for i in range(4):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotany/1.0 (public botanical education)"}),timeout=65) as response:return response.read()
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or i==3:raise
   time.sleep(25*(i+1))
def query(q):return json.loads(get("https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(q)))
try:
 category="Category:Bromus texensis - botanical illustrations"
 result=query({"action":"query","list":"categorymembers","cmtitle":category,"cmtype":"file","cmlimit":25,"format":"json"})
 files=result.get("query",{}).get("categorymembers",[])
 for file in files:
  title=file["title"]
  try:
   info=next(iter(query({"action":"query","prop":"imageinfo","iiprop":"url|extmetadata","titles":title,"format":"json"})["query"]["pages"].values()))["imageinfo"][0]
   md=info["extmetadata"];lic=md.get("LicenseShortName",{}).get("value","")
   norm=lic.upper().replace("-","").replace(" ","")
   assert norm in ("PUBLICDOMAIN","PDM","CC0","NORESTRICTIONS","CCBY4.0","CCBYSA4.0"),"Rights not cleared: "+lic
   raw=get(info["url"]);im=Image.open(io.BytesIO(raw));im.verify();im=Image.open(io.BytesIO(raw)).convert("RGB")
   assert min(im.size)>=500
   out=base/"images"/"historic-bromus-texensis-plate.jpg";out.parent.mkdir(parents=True,exist_ok=True);im.save(out,"JPEG",quality=92,optimize=True)
   creator=html.unescape(re.sub("<[^>]+>","",md.get("Artist",{}).get("value",""))).strip() or "Historic botanical illustration; see source page"
   page="https://commons.wikimedia.org/wiki/"+urllib.parse.quote(title.replace(" ","_"))
   entry={"file":"images/"+out.name,"role":"Exact-species historic botanical plate of Bromus texensis; illustration not a photograph","creator":creator,"license":lic,"source_page":page,"photo_status":"REFERENCE ILLUSTRATION — spikelet/lemma arrows require separate photo review","public_reuse":"Commons image-level license checked"}
   if not any(x.get("file")==entry["file"] for x in d["images"]):d["images"].append(entry)
   report["added"].append(title)
   break
  except Exception as e:report["held"].append({"file":title,"reason":str(e)})
except Exception as e:report["held"].append({"category":"Bromus texensis","reason":str(e)})
if report["added"]:
 d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"]);d.setdefault("curation_status",{})["photo_metadata_count"]=len(d["images"])
 p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
report["gallery_count"]=len(d["images"])
dest=pathlib.Path("reports/bromus-texensis-plate-archive.json");dest.parent.mkdir(exist_ok=True);dest.write_text(json.dumps(report,indent=2)+"\n")
