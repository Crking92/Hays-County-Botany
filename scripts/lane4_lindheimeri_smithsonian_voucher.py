#!/usr/bin/env python3
"""Archive Smithsonian CC0 Lindheimer panicgrass herbarium voucher, only after exact source checks."""
import json,pathlib,re,urllib.request,urllib.parse,io
from PIL import Image
p=pathlib.Path("content/taxa/Poaceae/Dichanthelium/dichanthelium-lindheimeri/species.json")
d=json.loads(p.read_text());report={"added":[],"held":[]}
url="https://www.si.edu/object/dichanthelium-acuminatum-var-lindheimeri-nash-gould-ca-clark:nmnhbotany_16018883"
def get(u):
 req=urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0 (educational botany photo archiving)"})
 with urllib.request.urlopen(req,timeout=60) as f:return f.read()
try:
 html=get(url).decode("utf-8","replace")
 assert "public domain" in html.lower() and ("lindheimeri" in html.lower()) and "nmnhbotany_16018883" in html
 candidates=re.findall(r'https?:[^"\s<>]+(?:iiif|manifest)[^"\s<>]*',html,re.I)
 candidates=[s.replace("&amp;","&").replace("\\/","/") for s in candidates]
 print("manifest candidates",candidates[:8])
 iiifimage=None
 for manifesturl in candidates:
  try:
   data=json.loads(get(manifesturl))
   imageinfo=[]
   if "items" in data:
    for canvas in data["items"]:
     for anno in canvas.get("items",[]):
      for item in anno.get("items",[]):
       body=item.get("body",{})
       imageinfo.extend(body.get("service",[]))
   for seq in data.get("sequences",[]):
    for canvas in seq.get("canvases",[]):
     for img in canvas.get("images",[]):
      imageinfo.extend(img.get("resource",{}).get("service",[]))
   if imageinfo:
    service=imageinfo[0].get("@id") or imageinfo[0].get("id")
    if service and service.startswith("https://"):
     iiifimage=service.rstrip("/")+"/full/1400,/0/default.jpg";break
  except Exception:continue
 assert iiifimage,"No verified Smithsonian IIIF image URL discovered; do not install"
 blob=get(iiifimage)
 image=Image.open(io.BytesIO(blob));image.verify()
 image=Image.open(io.BytesIO(blob)).convert("RGB");assert min(image.size)>700
 local="images/smithsonian-nmnh-16018883-herbarium-voucher.jpg";dest=p.parent/local;dest.parent.mkdir(exist_ok=True,parents=True)
 image.save(dest,"JPEG",quality=90,optimize=True)
 d["images"].append({"file":local,"role":"Dry pressed Smithsonian specimen, historical taxonomic combination D. acuminatum var. lindheimeri, NOT living ligule or native Hays specimen","creator":"Smithsonian National Museum of Natural History; collector Mary Agnes Chase","license":"Public domain / Smithsonian CC0 metadata","license_url":"https://creativecommons.org/publicdomain/zero/1.0/","source_page":url,"specimen_id":"nmnhbotany_16018883","source_taxon":"Dichanthelium acuminatum var. lindheimeri","photo_status":"Authentic herbarium voucher, morphological measurement/label pending inspection"})
 d.setdefault("visual_comparison",{}).setdefault("items",[]).append({"label":"SMITHSONIAN HERBARIUM — Lindheimer panicgrass historical combination","scientific_name":"Dichanthelium acuminatum var. lindheimeri","image_url":str(dest).replace("\\","/"),"image_fit":"contain","image_role":"Authentic voucher evidence; a dried specimen is not proof of true live leaf collar or measured spikelet size","caption":"Mary Agnes Chase, North Carolina specimen, 1906. Public-domain Smithsonian image. No morphological arrows placed.","creator":"Smithsonian NMNH","license":"Public domain (CC0 metadata)","source_page":url,"markers":[],"photo_status":"VOUCHER ONLY — NOT DIAGNOSTIC MACRO"})
 d.setdefault("field_id_finish_pass",{})["lane4_secondpass_20261023"]={"status":"FIELD_READY_PHOTO_GAPS","voucher_installed":True,"new_photo_count":1,"new_arrows":0,"still_missing":["living rooted plant / rosette","true hair-fringe ligule at 1mm scale","measured mature 1.3–1.6mm spikelet glumes, lemmas and stalk"],"no_county_or_taxon_audit":True}
 p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
 report["added"].append({"file":str(dest),"source":url,"image":iiifimage,"dimensions":image.size})
except Exception as e:report["held"].append({"source":url,"reason":str(e)})
out=pathlib.Path("reports/lane4-lindheimeri-smithsonian-voucher.json");out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
