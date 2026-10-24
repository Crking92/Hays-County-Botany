#!/usr/bin/env python3
"""Lane 2: independently archive and credit the FEIS plains lovegrass habit photo."""
import json,pathlib,urllib.request,io,hashlib
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Eragrostis/eragrostis-intermedia")
p=base/"species.json";source="https://research.fs.usda.gov/feis/species-reviews/eraint"
url="https://research.fs.usda.gov/sites/default/files/2025-05/feis-eraint_habit.jpg"
report={"taxon":"Eragrostis intermedia","source":url,"status":"HOLD"}
try:
 req=urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotany/1.0 field education photo archiver"})
 with urllib.request.urlopen(req,timeout=70) as f:raw=f.read()
 assert 10000<len(raw)<12000000
 img=Image.open(io.BytesIO(raw));img.verify();img=Image.open(io.BytesIO(raw)).convert("RGB")
 assert min(img.size)>=500
 dst=base/"images/cecelia-alexander-plains-lovegrass-habit.jpg";dst.parent.mkdir(parents=True,exist_ok=True)
 img.save(dst,quality=91,optimize=True)
 j=json.loads(p.read_text());assert j["id"]=="eragrostis-intermedia"
 rec=next(x for x in j["images"] if x.get("file")==url)
 rec["original_external_file"]=rec["file"];rec["file"]="images/"+dst.name
 rec["photo_status"]="Archived original CC BY-SA source-labelled FEIS habit view, NOT same-voucher anatomical diagnosis"
 rec["modifications"]="Reencoded RGB JPEG with EXIF/GPS removed; attribution/ShareAlike preserved"
 if not any(x.get("source_page")==source and x.get("creator")=="Cecelia Alexander" for x in j["visual_comparison"]["items"]):
  j["visual_comparison"]["items"].insert(3,{"label":"PUBLIC-SAFE PLAINS LOVEGRASS · original rooted bunch photograph","scientific_name":"Eragrostis intermedia","image_url":str(dst),"image_fit":"contain","image_role":"Source-identified intact bunch growth on rocky substrate; NOT ligule or glume macro","caption":"Cecelia Alexander's USFS FEIS credited habit photograph shows source-labelled Eragrostis intermedia in rocky ground. Its open head and rooted growth habit are supporting field context only. Exact sheath hair insertion, ligule and floret measurements are unresolved.","why_it_matters":"Adds a credited publicly reusable exact-species habit view without misrepresenting an unlicensed photograph as public safe.","creator":"Cecelia Alexander","license":"CC BY-SA 4.0","license_url":"https://creativecommons.org/licenses/by-sa/4.0/","source_page":source,"markers":[],"photo_status":"PROVISIONAL — USER PHOTO REVIEW PENDING; no fine arrows"})
 j["field_photo_quickcheck"]["featured_photo_indices"]=list(dict.fromkeys(j["field_photo_quickcheck"]["featured_photo_indices"]+[0]))
 j["field_id_finish_pass"]["lane2_20261023"]={"new_public_safe_photo_locally_archived":1,"role":"source-identified whole bunch","source":source,"unresolved":["true blade/sheath collar showing measured hair fringe","lower branch-axil with actual hairs","mature measured glumes and lemmas","site QA"],"no_new_diagnostic_arrows":True,"status":"FIELD_READY_PHOTO_GAPS"}
 p.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n")
 report.update(status="ARCHIVED",local=str(dst),dimensions=list(img.size),sha256=hashlib.sha256(dst.read_bytes()).hexdigest())
except Exception as e:report["error"]=str(e)
audit=pathlib.Path("reports/lane2-eragrostis-intermedia-archive-20261023.json");audit.parent.mkdir(parents=True,exist_ok=True);audit.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
