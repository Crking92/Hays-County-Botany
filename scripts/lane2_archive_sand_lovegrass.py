#!/usr/bin/env python3
import json,io,urllib.request,urllib.parse,pathlib,hashlib
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Eragrostis/eragrostis-trichodes");p=base/"species.json"
title="File:Eragrostis trichodes 0776.jpg";source="https://commons.wikimedia.org/wiki/File:Eragrostis_trichodes_0776.jpg"
report={"species":"eragrostis-trichodes","source":source,"status":"HOLD"}
try:
 def get(u):
  with urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"HaysCountyBotany/1.0 botany educational archive"}),timeout=65) as r:return r.read()
 api="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","prop":"imageinfo","iiprop":"url|extmetadata","titles":title,"format":"json"})
 inf=next(iter(json.loads(get(api))["query"]["pages"].values()))["imageinfo"][0]
 lic=inf["extmetadata"]["LicenseShortName"]["value"].upper()
 assert "PUBLIC DOMAIN" in lic or "PD" in lic,lic
 raw=get(inf["url"]);assert 10000<len(raw)<9000000
 im=Image.open(io.BytesIO(raw));im.verify();im=Image.open(io.BytesIO(raw)).convert("RGB");assert min(im.size)>500
 dst=base/"images/usda-txpmc-sand-lovegrass-habit.jpg";dst.parent.mkdir(parents=True,exist_ok=True);im.save(dst,"JPEG",quality=93,optimize=True)
 j=json.loads(p.read_text());assert j["id"]=="eragrostis-trichodes"
 rec=next(x for x in j["images"] if x.get("source_page")==source)
 rec["original_remote_file"]=rec["file"];rec["file"]="images/"+dst.name;rec["photo_status"]="LOCAL archived USDA-NRCS source picture; habitat/whole grass not true ligule microscopy";rec["modifications"]="Metadata stripped / RGB JPEG re-encode"
 for item in j["visual_comparison"]["items"]:
  if item.get("scientific_name")=="Eragrostis trichodes" and "USDA" in item.get("label",""):item["image_url"]=str(dst);item["photo_status"]="LOCAL archived source image; no unverified anatomy arrows"
 j["field_photo_quickcheck"]["featured_photo_indices"]=[0,1,2]
 j["field_photo_quickcheck"]["warning"]="The original three photographed species images now include the USDA-NRCS Texas Plant Materials Center public-domain overview (if archive succeeded) and two field views. Public-domain broad habit is not evidence for true 0.4-mm ligule fringe or lower glume. Need 10-20× collar and spikelet dissection with physical ruler."
 j["field_id_finish_pass"]["lane2_photo_finish_20261023"]={"stage":"FIELD_READY_PHOTO_GAPS","new_public_domain_USDA_local_photo":1,"actual_anatomical_macro_added":0,"no_new_arrows":True,"critical_gaps":["Short 0.4-mm true hair-fringe ligule vs 4-5-mm long oral/collar hairs","True lower panicle branch axil 10-20x","Detached mature flattened spikelet/glume/lemma photographed with 1-mm ruler"],"pages":"NOT_VERIFIED"}
 p.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n")
 report.update(status="ARCHIVED",path=str(dst),dimensions=list(im.size),sha256=hashlib.sha256(dst.read_bytes()).hexdigest())
except Exception as e:report["error"]=str(e)
a=pathlib.Path("reports/lane2-sand-lovegrass-usda-photo-20261023.json");a.parent.mkdir(parents=True,exist_ok=True);a.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
