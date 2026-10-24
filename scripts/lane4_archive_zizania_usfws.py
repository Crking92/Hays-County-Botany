#!/usr/bin/env python3
"""Lane 4: archive independently source-credited, public-domain USFWS Zizania texana media."""
import json,pathlib,urllib.request,urllib.parse,io,time,hashlib
from PIL import Image
p=pathlib.Path("content/taxa/Poaceae/Zizania/zizania-texana/species.json")
d=json.loads(p.read_text());assert d["id"]=="zizania-texana"
ids=["20539","20540","20562"]
report={"added":[],"held":[],"role_verification":"Whole plant/flower anatomy not certified until original pixels are inspected; no markers added"}
def get(u):
 for attempt in range(3):
  try:
   req=urllib.request.Request(u,headers={"User-Agent":"HaysBotanyEducationalArchive/1.0 (botanical photo learning)"})
   with urllib.request.urlopen(req,timeout=50) as r:return r.read()
  except Exception:
   if attempt==2:raise
   time.sleep(8*(attempt+1))
for fileid in ids:
 title="File:Zizania texana (Texas wild rice) FWS "+fileid+".jpg"
 page="https://commons.wikimedia.org/wiki/"+urllib.parse.quote(title.replace(" ","_"),safe=":/()")
 if any(z.get("source_page")==page for z in d["images"]):continue
 try:
  params=urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":"1600","titles":title})
  info=json.loads(get("https://commons.wikimedia.org/w/api.php?"+params))
  entry=next(iter(info["query"]["pages"].values()))["imageinfo"][0]
  metadata=entry.get("extmetadata",{})
  license=metadata.get("LicenseShortName",{}).get("value","")
  usage=metadata.get("UsageTerms",{}).get("value","")
  assert "public domain" in (license+" "+usage).lower() or "pd-" in license.lower(), "Permission not verified: "+license
  blob=get(entry.get("thumburl") or entry["url"])
  assert 15000<len(blob)<13000000
  original=Image.open(io.BytesIO(blob));original.verify()
  original=Image.open(io.BytesIO(blob)).convert("RGB");assert min(original.size)>=650
  file="usfws-hagerty-"+fileid+".jpg";dest=p.parent/"images"/file;dest.parent.mkdir(parents=True,exist_ok=True)
  original.save(dest,format="JPEG",quality=92,optimize=True)
  creator="Ryan Hagerty / U.S. Fish and Wildlife Service"
  d["images"].append({"file":"images/"+file,"role":"USFWS species-labelled Texas wild-rice reference photo; image anatomy pending human pixel review","creator":creator,"license":"Public domain — work of U.S. federal government","license_url":"https://www.usa.gov/government-works","source_page":page,"source_file_id":"FWS "+fileid,"modifications":"Resized to <=1600px by Wikimedia; re-encoded JPEG; EXIF removed","public_reuse":"USFWS original public-domain photograph","photo_status":"PHYSICALLY ARCHIVED; PROVISIONAL USER PHOTO REVIEW PENDING; no inferred morphology markers"})
  d.setdefault("visual_comparison",{}).setdefault("items",[]).append({"label":"Texas wild-rice — USFWS public-domain photograph "+fileid,"scientific_name":"Zizania texana","image_url":str(dest).replace("\\","/"),"image_fit":"contain","image_role":"Actual species-labelled public-domain USFWS photo; organ-level anatomy awaits pixel inspection","caption":"U.S. Fish and Wildlife Service photo of Texas wild-rice, used for noncontact educational recognition. Individual ligule, spikelets and female flowers have not been certified from these pixels. Protected species: do not collect or disturb.","why_it_matters":"Adds a source-authenticated public-domain image from species conservation work rather than an unrelated grass.","creator":creator,"license":"Public domain — US federal government work","source_page":page,"markers":[],"photo_status":"PROVISIONAL — USER PHOTO REVIEW PENDING"})
  report["added"].append({"id":fileid,"path":str(dest),"source":page,"size":original.size})
 except Exception as exc:report["held"].append({"id":fileid,"reason":str(exc)})
if report["added"]:
 d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
 d.setdefault("field_id_finish_pass",{})["lane4_usfws_20261023"]={"photos_added":len(report["added"]),"anatomical_arrows_added":0,"status":"FIELD_READY_PHOTO_GAPS","species_endangered_guardrail":"Keep noncontact observation only; no detailed site coordinates","pending":["Photograph true female spikelets and awn under calibrated scale","Actual inner ligule / collar and midrib","Noncontact submerged habit from verified distance"],"photo_permission":"USFWS public domain"}
 p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
dest=pathlib.Path("reports/lane4-zizania-texana-usfws-photo-archive.json");dest.parent.mkdir(exist_ok=True);dest.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
