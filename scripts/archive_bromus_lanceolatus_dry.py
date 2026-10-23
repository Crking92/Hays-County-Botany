#!/usr/bin/env python3
"""Archive exact-taxon CC BY 4.0 Bromus lanceolatus image by Yves Bas."""
import json,io,pathlib,time,urllib.request,urllib.error,urllib.parse
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Bromus/bromus-lanceolatus");p=base/"species.json";d=json.loads(p.read_text());assert d["id"]=="bromus-lanceolatus"
title="File:Bromus lanceolatus dry.jpg";hold=[]
def fetch(url):
 for n in range(5):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotany/1.0 (educational botanical photo archive)"}),timeout=65) as r:return r.read()
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or n==4:raise
   time.sleep(25*(n+1))
try:
 api="https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url%7Cextmetadata&format=json&titles="+urllib.parse.quote(title)
 info=next(iter(json.loads(fetch(api))["query"]["pages"].values()))["imageinfo"][0]
 license=info["extmetadata"]["LicenseShortName"]["value"]
 assert license.upper().replace("-","").replace(" ","")=="CCBY4.0",license
 raw=fetch(info["url"]);assert 15000<len(raw)<15000000
 im=Image.open(io.BytesIO(raw));im.verify();im=Image.open(io.BytesIO(raw)).convert("RGB");assert min(im.size)>=700
 out=base/"images"/"yves-bas-bromus-lanceolatus-dry.jpg";out.parent.mkdir(exist_ok=True,parents=True);im.save(out,"JPEG",quality=91,optimize=True)
 entry={"file":"images/"+out.name,"role":"Dried inflorescence and spikelets of exact-taxon Bromus lanceolatus; awn/lemma details to be inspected at native resolution","creator":"Yves Bas","license":"CC BY 4.0","license_url":"https://creativecommons.org/licenses/by/4.0/","source_page":"https://commons.wikimedia.org/wiki/File:Bromus_lanceolatus_dry.jpg","photo_status":"PROVISIONAL — photographic anatomy arrow placement pending review","public_reuse":"Attribution required"}
 if not any(x.get("file")==entry["file"] for x in d["images"]):d["images"].append(entry)
 d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
 d.setdefault("curation_status",{})["photo_metadata_count"]=len(d["images"])
 p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
 print("ARCHIVED",out)
except Exception as e:hold.append(str(e));print("HELD",e)
rp=pathlib.Path("reports/bromus-lanceolatus-dry-archive.json");rp.parent.mkdir(exist_ok=True);rp.write_text(json.dumps({"holds":hold,"gallery_count":len(d["images"])},indent=2)+"\n")
