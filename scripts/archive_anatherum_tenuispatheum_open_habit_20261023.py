#!/usr/bin/env python3
"""Safely archive one CC-BY habit photo under historical A. glomeratus var. pumilus."""
import json,urllib.request,urllib.parse,io,pathlib,re,html,hashlib
from PIL import Image,ImageOps
p=pathlib.Path("content/taxa/Poaceae/Anatherum/anatherum-tenuispatheum/species.json")
d=json.loads(p.read_text());assert d["id"]=="anatherum-tenuispatheum"
title="File:Starr-150330-0402-Andropogon glomeratus var pumilus-habit-Parade Field Sand Island-Midway Atoll (40428508425).jpg"
query=urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo","iiprop":"url|extmetadata","titles":title})
def get(url):
 req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyOpenArchive/1.0 (educational grass reference)"})
 with urllib.request.urlopen(req,timeout=55) as resp:return resp.read(22000001)
info=next(iter(json.loads(get("https://commons.wikimedia.org/w/api.php?"+query))["query"]["pages"].values()))["imageinfo"][0]
md=info["extmetadata"]
license=html.unescape(re.sub("<[^>]*>","",md.get("LicenseShortName",{}).get("value",""))).strip()
assert license.upper().replace(" ","").replace("-","") in {"CCBY3.0US","CCBY3.0"},license
source="https://commons.wikimedia.org/wiki/"+urllib.parse.quote(title.replace(" ","_"))
report={"source_page":source,"license":license,"added":False}
if not any(x.get("source_page")==source for x in d["images"]):
 raw=get(info["url"]);assert 10000<len(raw)<22000000
 with Image.open(io.BytesIO(raw)) as img:img.verify()
 with Image.open(io.BytesIO(raw)) as img:
  img=ImageOps.exif_transpose(img).convert("RGB");assert min(img.size)>700
  img.thumbnail((1800,1800))
  out=io.BytesIO();img.save(out,"JPEG",quality=86,optimize=True);payload=out.getvalue()
 dest=p.parent/"images/starr-var-pumilus-habit-ccby3.jpg";dest.parent.mkdir(exist_ok=True)
 dest.write_bytes(payload)
 with Image.open(dest) as im:im.verify()
 d["images"].append({"file":"images/"+dest.name,"role":"Recognize: whole-plant habit under historical var. pumilus label; NOT independent voucher or fine anatomy","creator":"Forest & Kim Starr","license":license,"source_page":source,"historical_source_name":"Andropogon glomeratus var. pumilus","taxonomic_mapping":"Kew accepted Anatherum tenuispatheum","public_reuse":"CC BY with attribution and modification notice","modifications":"Resized, EXIF stripped","sha256":hashlib.sha256(payload).hexdigest(),"photo_status":"PHYSICALLY_ARCHIVED_PROVISIONAL_HABIT; not species-diagnostic"} )
 d["curation_status"]["photo_metadata_count"]=len(d["images"])
 d["curation_status"]["photo_files_present"]=len(d["images"])
 d["learner_visual_status"]["image_count"]=len(d["images"])
 p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
 report["added"]=True;report["physical_file"]=dest.as_posix()
out=pathlib.Path("reports/anatherum-open-habit-20261023.json");out.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
