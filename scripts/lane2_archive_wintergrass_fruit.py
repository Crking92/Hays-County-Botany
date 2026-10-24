#!/usr/bin/env python3
import json,io,pathlib,hashlib,urllib.request,urllib.parse
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Nassella/nassella-leucotricha")
p=base/"species.json";title="File:Nassella leucotricha.jpg";source="https://commons.wikimedia.org/wiki/File:Nassella_leucotricha.jpg"
record={"source":source,"status":"HOLD"}
try:
 def fetch(u):
  with urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"HaysCountyBotany/1.0 educational photo archiver"}),timeout=75) as r:return r.read()
 api="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","prop":"imageinfo","iiprop":"url|extmetadata","titles":title,"format":"json"})
 m=next(iter(json.loads(fetch(api))["query"]["pages"].values()))["imageinfo"][0]
 lic=m["extmetadata"]["LicenseShortName"]["value"].upper()
 assert "PUBLIC DOMAIN" in lic or "PD" in lic,lic
 raw=fetch(m["url"]);assert 20000<len(raw)<14000000
 image=Image.open(io.BytesIO(raw));image.verify();image=Image.open(io.BytesIO(raw)).convert("RGB")
 assert min(image.size)>300
 dst=base/"images/usda-ars-texas-wintergrass-fruit.jpg";dst.parent.mkdir(parents=True,exist_ok=True);image.save(dst,quality=92,optimize=True)
 j=json.loads(p.read_text());assert j["id"]=="nassella-leucotricha"
 old=next(x for x in j["images"] if x.get("source_page")==source)
 old["original_external_file"]=old["file"];old["file"]="images/"+dst.name
 old["modifications"]="RGB JPEG re-encoded without EXIF/GPS";old["photo_status"]="Physically archived USDA-ARS public domain fruit photo; previously existing broad callus/lemma/awn arrows retained"
 for x in j["visual_comparison"]["items"]:
  if x.get("source_page")==source:x["image_url"]=str(dst);x["photo_status"]="Physically archived U.S. government PD fruit photo; original reviewed broad anatomical annotations retained"
 j["field_id_finish_pass"]["lane2_photo_finish_20261023"]={"stage":"FIELD_READY_PHOTO_GAPS","new_public_domain_photo_archived":1,"macro_role":"hardened one-awed lemma, sharp basal callus","remaining":["true short ligule at 10-20x with physical mm scale","same-voucher Hays rooted clump and mature seedhead","measured corona/callus and comparative N. tenuissima fruit","Pages and mobile arrow QA"],"new_arrows":0}
 p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+"\n")
 record.update(status="ARCHIVED",local=str(dst),dimensions=list(image.size),sha256=hashlib.sha256(dst.read_bytes()).hexdigest())
except Exception as e:record["error"]=str(e)
out=pathlib.Path("reports/lane2-nassella-leucotricha-usda-20261023.json");out.parent.mkdir(exist_ok=True,parents=True);out.write_text(json.dumps(record,indent=2)+"\n")
print(json.dumps(record))
