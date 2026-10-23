#!/usr/bin/env python3
"""Archive verified USDA public-domain seed close-up for Chloris cucullata."""
import io,json,pathlib,urllib.parse,urllib.request
from PIL import Image
card=pathlib.Path("content/taxa/Poaceae/Chloris/chloris-cucullata/species.json")
data=json.loads(card.read_text())
name="Chloriscucullata.jpg"
source="https://commons.wikimedia.org/wiki/File:Chloriscucullata.jpg"
query=urllib.parse.urlencode({"action":"query","prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":"1600","titles":"File:"+name,"format":"json"})
def get(url):
 req=urllib.request.Request(url,headers={"User-Agent":"HaysBotany/1.0 (botanical archive)"})
 with urllib.request.urlopen(req,timeout=60) as f:return f.read()
info=next(iter(json.loads(get("https://commons.wikimedia.org/w/api.php?"+query))["query"]["pages"].values()))["imageinfo"][0]
meta=info["extmetadata"]
license=meta.get("LicenseShortName",{}).get("value","").lower()
if not any(word in license for word in ("public domain","pd-usgov","pd-usda","cc0")):raise SystemExit("HOLD: Commons license not public domain: "+license)
raw=get(info.get("thumburl") or info["url"])
if not 10000<len(raw)<25000000:raise SystemExit("HOLD: file size outside bounds")
im=Image.open(io.BytesIO(raw));im.verify()
im=Image.open(io.BytesIO(raw)).convert("RGB")
if min(im.size)<400:raise SystemExit("HOLD: insufficient photo resolution")
dest=card.parent/"images"/"usda-chloris-cucullata-seeds-public-domain.jpg"
dest.parent.mkdir(exist_ok=True)
im.save(dest,"JPEG",quality=90,optimize=True)
url=str(dest).replace("\\","/")
if not any(x.get("file")=="images/"+dest.name for x in data["images"]):
 data["images"].append({"file":"images/"+dest.name,"role":"USDA source-labelled measured seeds/caryopses close-up; NOT dissected hood or ligule","creator":"Jose Hernandez / USDA Agricultural Research Service","license":"Public domain (U.S. federal work)","source_page":source,"archived_original_url":info["url"],"source_platform":"Wikimedia Commons / USDA ARS","photo_status":"REAL REPRODUCTIVE DETAIL — seed image, not hood/floret anatomy"})
if not any(x.get("image_url")==url for x in data["visual_comparison"]["items"]):
 data["visual_comparison"]["items"].insert(2,{"label":"HOODED WINDMILLGRASS — USDA measured seed photograph (not sterile lemma)","scientific_name":"Chloris cucullata","image_url":url,"image_fit":"contain","image_role":"Source-labelled USDA public-domain measured seeds close-up","caption":"USDA ARS photographed seeds of Chloris cucullata. This teaches reproductive size and shape but does NOT show the decisive swollen upper sterile lemma, glumes, ligule or attached spikelet anatomy.","why_it_matters":"Public-domain species-specific reproductive close-up complements the currently archived raceme photographs.","creator":"Jose Hernandez / USDA ARS","license":"Public domain","source_page":source,"markers":[],"photo_status":"Image-level Commons identity/license checked; no speculative arrows."})
data.setdefault("field_id_finish_pass",{})["usda_seed_closeup_20261023"]={"locally_archived":True,"source":source,"role":"Measured seeds/caryopses, not sterile-lemma hood","stage":"FIELD_READY_PHOTO_GAPS","need_next":"Dissected hood 1–1.5mm and collar/ligule with mm scale; review site and arrows"}
card.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n")
print("ARCHIVED",dest)
