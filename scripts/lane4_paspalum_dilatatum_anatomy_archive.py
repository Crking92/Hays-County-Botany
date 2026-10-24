#!/usr/bin/env python3
"""Lane 4: archive two exact-species Commons Dallisgrass anatomical views."""
import json,pathlib,urllib.request,urllib.parse,io
from PIL import Image
p=pathlib.Path("content/taxa/Poaceae/Paspalum/paspalum-dilatatum/species.json")
d=json.loads(p.read_text());assert d["id"]=="paspalum-dilatatum"
files=[("Paspalum dilatatum sl8.jpg","stefan-lefnaer-dallisgrass-ligule.jpg","True blade sheath and membranous ligule reference — source-authenticated; anatomy arrow review pending","Stefan.lefnaer","ccbysa40"),("Paspalum dilatatum spikelets6 (7371038292).jpg","macleay-grass-man-dallisgrass-spikelets.jpg","Four rows of oval, long-haired spikelets on raceme — image measurements unverified","Macleay Grass Man","ccby20")]
report={"added":[],"held":[]}
def get(u):
 req=urllib.request.Request(u,headers={"User-Agent":"Hays-County-Botany/1.0 (noncommercial botanical teaching; GitHub: Crking92/Hays-County-Botany)"})
 with urllib.request.urlopen(req,timeout=60) as z:return z.read()
for title,name,role,creator,expected in files:
 try:
  q=urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":1400,"titles":"File:"+title})
  info=next(iter(json.loads(get("https://commons.wikimedia.org/w/api.php?"+q))["query"]["pages"].values()))["imageinfo"][0]
  license=info["extmetadata"]["LicenseShortName"]["value"];norm="".join(c for c in license.lower() if c.isalnum())
  assert norm==expected,"Unexpected license "+license
  raw=get(info.get("thumburl") or info["url"]);assert 15000<len(raw)<16000000
  x=Image.open(io.BytesIO(raw));x.verify()
  x=Image.open(io.BytesIO(raw)).convert("RGB");assert min(x.size)>=650
  destination=p.parent/"images"/name;destination.parent.mkdir(parents=True,exist_ok=True)
  x.save(destination,"JPEG",quality=92,optimize=True)
  page="https://commons.wikimedia.org/wiki/File:"+urllib.parse.quote(title.replace(" ","_"),safe="()")
  cc="CC BY-SA 4.0" if expected=="ccbysa40" else "CC BY 2.0"
  url="https://creativecommons.org/licenses/"+("by-sa/4.0" if expected=="ccbysa40" else "by/2.0")+"/"
  d["images"].append({"file":"images/"+name,"role":role,"creator":creator,"license":cc,"license_url":url,"source_page":page,"photo_status":"PHYSICALLY ARCHIVED — PROVISIONAL USER PHOTO REVIEW PENDING, no new arrows","modifications":"Resized Commons derivative re-encoded without EXIF"})
  d["visual_comparison"]["items"].append({"label":"DALLISGRASS — "+("TRUE LIGULE PHOTO" if "sl8" in title else "HAIRY SPIKELETS PHOTO"),"scientific_name":"Paspalum dilatatum","image_url":str(destination).replace("\\","/"),"image_fit":"contain","image_role":role,"caption":"Actual exact-source species photo; inspect visible structure and scale before assigning glume, lemma, or ligule measurement arrows. Not a Hays County voucher.","creator":creator,"license":cc,"license_url":url,"source_page":page,"markers":[],"photo_status":"PROVISIONAL — USER PHOTO REVIEW PENDING"})
  report["added"].append({"file":str(destination),"source":page,"license":cc,"dimensions":x.size})
 except Exception as e:report["held"].append({"file":title,"reason":str(e)})
if report["added"]:
 d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
 d.setdefault("field_id_finish_pass",{})["lane4_20261023"]={"status":"FIELD_READY_PHOTO_GAPS","new_photos":len(report["added"]),"new_arrows":0,"last_mile":["same-specimen rooted tuft and rhizome with ruler","3.5mm mature spikelet dorsal/side under microscope showing upper glume long silky margin","separated lower/upper glume and fertile lemma with scale","same-scale Paspalum urvillei comparison"],"pages_status":"not verified"}
 p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
out=pathlib.Path("reports/lane4-paspalum-dilatatum-anatomy-archive.json");out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
