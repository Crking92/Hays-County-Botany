#!/usr/bin/env python3
"""Lane4 locally archive exact existing Heteropogon mature-tangle reference."""
import pathlib,json,urllib.parse,urllib.request,io
from PIL import Image
p=pathlib.Path("content/taxa/Poaceae/Heteropogon/heteropogon-contortus/species.json")
d=json.loads(p.read_text());page="https://commons.wikimedia.org/wiki/File:Spear_Grass_(Heteropogon_contortus)_intertwined_awns_(12818793383).jpg"
report={"archived":[],"held":[]}
try:
 params=urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":1280,"titles":"File:Spear Grass (Heteropogon contortus) intertwined awns (12818793383).jpg"})
 def fetch(u):
  with urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"HaysBotanyIDVisualLearner/1.0 (educational image audit)"}),timeout=50) as response:return response.read()
 info=next(iter(json.loads(fetch("https://commons.wikimedia.org/w/api.php?"+params))["query"]["pages"].values()))["imageinfo"][0]
 license=info["extmetadata"]["LicenseShortName"]["value"]
 assert "".join(c for c in license.lower() if c.isalnum())=="ccbysa20",license
 raw=fetch(info.get("thumburl") or info["url"])
 original=Image.open(io.BytesIO(raw));original.verify()
 image=Image.open(io.BytesIO(raw)).convert("RGB")
 assert min(image.size)>=600
 name="bernard-dupont-mature-intertwined-awns.jpg";out=p.parent/"images"/name;out.parent.mkdir(exist_ok=True,parents=True);image.save(out,"JPEG",quality=92,optimize=True)
 if not any(x.get("file")=="images/"+name for x in d["images"]):
  d["images"].append({"file":"images/"+name,"role":"Actual mature intertwined long awns in a source-labelled Heteropogon contortus flowering head, South African photographic reference","creator":"Bernard DUPONT","license":"CC BY-SA 2.0","license_url":"https://creativecommons.org/licenses/by-sa/2.0/","source_page":page,"photo_status":"SOURCE VERIFIED; mature awn tangle only; no new microscopic claims or arrows","modifications":"Wikimedia resized derivative; EXIF removed by JPEG re-encoding"})
 updated=0
 for panel in d.get("visual_comparison",{}).get("items",[]):
  if "12818793383" in panel.get("image_url",""):
   panel["image_url"]=str(out).replace("\\","/");panel["creator"]="Bernard DUPONT";panel["license"]="CC BY-SA 2.0";panel["license_url"]="https://creativecommons.org/licenses/by-sa/2.0/";panel["source_page"]=page;updated+=1
 d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
 d.setdefault("field_id_finish_pass",{})["lane4_20261023"]={"status":"FIELD_READY_PHOTO_GAPS","mature_awns_local_photo":str(out),"updated_gallery_panels":updated,"remaining":["paired fertile sessile/pedicellate mature spikelets with millimeter scale","sharp bearded callus base with actual scale","entire attached awn length along ruler","same Hays-site rooted crown and collar"],"new_anatomical_arrows":0,"live_pages_verified":False}
 p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
 report["archived"].append({"file":str(out),"gallery_panels_relinked":updated,"image_size":image.size,"source":page})
except Exception as e:report["held"].append({"source":page,"reason":str(e)})
dest=pathlib.Path("reports/lane4-heteropogon-mature-awn-archive.json");dest.parent.mkdir(exist_ok=True);dest.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
