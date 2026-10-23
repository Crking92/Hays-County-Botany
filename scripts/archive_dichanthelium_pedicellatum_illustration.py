#!/usr/bin/env python3
"""Archive exact-species historical illustration, only when Commons rights verify."""
import io,json,pathlib,time,urllib.request,urllib.parse,urllib.error,re,html
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Dichanthelium/dichanthelium-pedicellatum")
p=base/"species.json"; d=json.loads(p.read_text()); assert d["id"]=="dichanthelium-pedicellatum"
fn="Dichanthelium pedicellatum (as Panicum pedicellatum) HC-1935.png"
def fetch(url):
 for attempt in range(4):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotany/1.0 (historical botany education)"}),timeout=60) as f:return f.read()
  except urllib.error.HTTPError as e:
   if e.code not in (429,503,502) or attempt==3:raise
   time.sleep(25*(attempt+1))
holds=[]
try:
 title="File:"+fn
 api="https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url%7Cextmetadata&format=json&titles="+urllib.parse.quote(title)
 item=next(iter(json.loads(fetch(api))["query"]["pages"].values()))
 info=item["imageinfo"][0]; metadata=info["extmetadata"]; lic=metadata.get("LicenseShortName",{}).get("value","").upper().replace(" ","").replace("-","")
 assert lic in ("PUBLICDOMAIN","CC0"),"Rights not established as public-domain: "+lic
 raw=fetch(info["url"]);assert 12000<len(raw)<15000000
 im=Image.open(io.BytesIO(raw));im.verify();im=Image.open(io.BytesIO(raw)).convert("RGB")
 assert im.width>=400 and im.height>=400
 dest=base/"images"/"hitchcock-chase-pedicellatum-1935.jpg"; dest.parent.mkdir(parents=True,exist_ok=True);im.save(dest,"JPEG",quality=93,optimize=True)
 page="https://commons.wikimedia.org/wiki/"+urllib.parse.quote(title.replace(" ","_"))
 entry={"file":"images/"+dest.name,"role":"Historical botanical illustration of Dichanthelium pedicellatum (as Panicum pedicellatum); teaching diagram, NOT a photograph","creator":"A. S. Hitchcock and A. Chase, Manual of the Grasses of the United States (1935)","license":metadata["LicenseShortName"]["value"],"source_page":page,"public_reuse":"Commons image-level public domain verified","photo_status":"Illustration, taxon-labelled; do not substitute for species-confirmed photographic anatomy"}
 if not any(x.get("file")==entry["file"] for x in d["images"]):d["images"].append(entry)
 print("ARCHIVED",fn)
except Exception as e:
 holds.append({"file":fn,"reason":str(e)});print("HELD",repr(e))
d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
d.setdefault("curation_status",{})["photo_metadata_count"]=len(d["images"])
p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
report=pathlib.Path("reports/dichanthelium-pedicellatum-illustration-archive.json");report.parent.mkdir(exist_ok=True);report.write_text(json.dumps({"holds":holds,"images":len(d["images"])},indent=2)+"\n")
