#!/usr/bin/env python3
"""Archive two original Matt Lavin CC BY-SA images already used in D. dubium gallery."""
import json,pathlib,urllib.parse,urllib.request,io,time
from PIL import Image
p=pathlib.Path("content/taxa/Poaceae/Disakisperma/disakisperma-dubium/species.json")
d=json.loads(p.read_text());assert d["id"]=="disakisperma-dubium"
targets={"Leptochloa_dubia_-_green_sprangletop_-_Flickr_-_Matt_Lavin_(1).jpg":"matt-lavin-sprangletop-1.jpg","Leptochloa_dubia_-_green_sprangletop_-_Flickr_-_Matt_Lavin_(7).jpg":"matt-lavin-sprangletop-7.jpg"}
report={"archived":[],"held":[]}
def fetch(u):
 req=urllib.request.Request(u,headers={"User-Agent":"HaysBotanyEducationalGallery/1.0 (contact via project GitHub repo)"})
 with urllib.request.urlopen(req,timeout=50) as r:return r.read()
for filename,local in targets.items():
 try:
  par=urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":1280,"titles":"File:"+filename})
  js=json.loads(fetch("https://commons.wikimedia.org/w/api.php?"+par))
  info=next(iter(js["query"]["pages"].values()))["imageinfo"][0]
  meta=info["extmetadata"];lic=meta["LicenseShortName"]["value"]
  norm="".join(c for c in lic.lower() if c.isalnum())
  assert norm=="ccbysa20","Unexpected image rights: "+lic
  source="https://commons.wikimedia.org/wiki/File:"+urllib.parse.quote(filename,safe="()")
  if any(im.get("file")=="images/"+local for im in d["images"]):continue
  content=fetch(info.get("thumburl") or info["url"])
  assert 15000<len(content)<12000000
  im=Image.open(io.BytesIO(content));im.verify()
  im=Image.open(io.BytesIO(content)).convert("RGB");assert min(im.size)>=650
  out=p.parent/"images"/local;out.parent.mkdir(parents=True,exist_ok=True)
  im.save(out,format="JPEG",quality=92,optimize=True)
  d["images"].append({"file":"images/"+local,"role":"Actual source-labelled green sprangletop habit and one-sided panicle photograph; anatomical claims limited to visible structures","creator":"Matt Lavin","license":"CC BY-SA 2.0","license_url":"https://creativecommons.org/licenses/by-sa/2.0/","source_page":source,"photo_status":"PHYSICALLY ARCHIVED — PROVISIONAL USER PHOTO REVIEW; no new arrows","modifications":"Wikimedia 1280px derivative, re-encoded EXIF-free JPEG"})
  targetprefix=filename.replace("_"," ").split("Flickr")[0]
  updated=0
  for panel in d.get("visual_comparison",{}).get("items",[]):
   u=panel.get("image_url","")
   if filename.replace("_","%20") in u or ("Matt_Lavin_"+filename.split("Matt_Lavin_")[1].split(".jpg")[0] in u):
    panel["image_url"]=str(out).replace("\\","/")
    panel["creator"]="Matt Lavin";panel["license"]="CC BY-SA 2.0";panel["license_url"]="https://creativecommons.org/licenses/by-sa/2.0/";panel["source_page"]=source
    updated+=1
  report["archived"].append({"file":str(out),"source":source,"panel_links_updated":updated,"dimensions":im.size})
 except Exception as e:report["held"].append({"source":filename,"error":str(e)})
if report["archived"]:
 d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
 d.setdefault("field_id_finish_pass",{})["lane4_matt_lavin_local_archive_20261023"]={"status":"FIELD_READY_PHOTO_GAPS","new_images":len(report["archived"]),"no_new_arrows":True,"last_mile":"Measured actual same-source rootstock, 1mm ligule, mature glume/lemma and concealed lower-sheath florets"}
 p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
out=pathlib.Path("reports/lane4-disakisperma-matt-lavin-archive.json");out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
