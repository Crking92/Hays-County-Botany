#!/usr/bin/env python3
"""Archive genuinely useful Sorghum bicolor collar and floral images with image-level license checking."""
import io,json,pathlib,time,urllib.request,urllib.parse,urllib.error,html,re
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Sorghum/sorghum-bicolor");path=base/"species.json"
data=json.loads(path.read_text());assert data["id"]=="sorghum-bicolor"
items=[("Sorghum bicolor ligule (03).jpg","Real blade/sheath ligule close-up; compare membranous portion and hair fringe","rasbak-sorghum-ligule-03.jpg"),("Sorghum bicolor flower (03).jpg","Source-labelled reproductive photograph; exact flower structures subject to pixel review","rasbak-sorghum-flower-03.jpg")]
holds=[]
def fetch(url):
 for attempt in range(5):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotany/1.0 (botanical field training)"}),timeout=70) as r:return r.read()
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or attempt==4:raise
   time.sleep(25*(attempt+1))
for filename,role,local in items:
 try:
  title="File:"+filename
  api="https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url%7Cextmetadata&format=json&titles="+urllib.parse.quote(title)
  info=next(iter(json.loads(fetch(api))["query"]["pages"].values()))["imageinfo"][0]
  meta=info["extmetadata"]
  short=meta.get("LicenseShortName",{}).get("value","").upper().replace(" ","").replace("-","")
  assert short in ("CCBYSA3.0","CCBYSA4.0","CCBYSA2.0","CCBY3.0","CCBY4.0","CCBY2.0"),short
  author=html.unescape(re.sub("<[^>]+>","",meta.get("Artist",{}).get("value",""))).strip()
  assert "Rasbak" in author,author
  raw=fetch(info["url"]);assert 15000<len(raw)<20000000
  image=Image.open(io.BytesIO(raw));image.verify();image=Image.open(io.BytesIO(raw)).convert("RGB")
  assert min(image.size)>=600
  dest=base/"images"/local;dest.parent.mkdir(parents=True,exist_ok=True);image.save(dest,"JPEG",quality=91,optimize=True)
  url="https://commons.wikimedia.org/wiki/"+urllib.parse.quote(title.replace(" ","_"))
  item={"file":"images/"+local,"role":role,"creator":"Rasbak","license":meta["LicenseShortName"]["value"],"source_page":url,"public_reuse":"Keep CC BY-SA creator credit and ShareAlike requirements","photo_status":"PROVISIONAL — no added anatomical arrows until pixel review"}
  if not any(z.get("file")==item["file"] or z.get("source_page")==url for z in data["images"]):data["images"].append(item)
  print("ARCHIVED",filename)
 except Exception as e:holds.append({"file":filename,"reason":str(e)});print("HELD",filename,e)
data.setdefault("learner_visual_status",{})["image_count"]=len(data["images"])
data.setdefault("curation_status",{})["photo_metadata_count"]=len(data["images"])
path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
report=pathlib.Path("reports/sorghum-bicolor-anatomy-archive.json");report.parent.mkdir(exist_ok=True);report.write_text(json.dumps({"holds":holds,"gallery_count":len(data["images"])},indent=2)+"\n")
