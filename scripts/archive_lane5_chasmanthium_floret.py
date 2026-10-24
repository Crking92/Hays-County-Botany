#!/usr/bin/env python3
"""Rights-verify and locally archive the exact-species CC0 floret anatomy panel."""
import io,json,pathlib,urllib.parse,urllib.request,re,html
from PIL import Image
p=pathlib.Path("content/taxa/Poaceae/Chasmanthium/chasmanthium-latifolium/species.json")
s=json.loads(p.read_text())
source="https://commons.wikimedia.org/wiki/File:CHASMANTHIUM_LATIFOLIUM.jpg"
def get(u):
 req=urllib.request.Request(u,headers={"User-Agent":"HaysBotany/1.0 botanical CC0 image archiving"})
 with urllib.request.urlopen(req,timeout=45) as x:return x.read()
query=urllib.parse.urlencode({"action":"query","prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":"1600","titles":"File:CHASMANTHIUM LATIFOLIUM.jpg","format":"json"})
page=next(iter(json.loads(get("https://commons.wikimedia.org/w/api.php?"+query))["query"]["pages"].values()))
info=page["imageinfo"][0];md=info["extmetadata"]
license=re.sub("[^A-Z0-9]","",md.get("LicenseShortName",{}).get("value","").upper())
if license not in ("CC0","CC010","PUBLICDOMAIN"):raise RuntimeError("Image-level CC0/public-domain rights not confirmed: "+license)
artist=html.unescape(re.sub("<[^>]*>","",md.get("Artist",{}).get("value",""))).strip()
if not artist:raise RuntimeError("Creator credit unavailable")
im=Image.open(io.BytesIO(get(info.get("thumburl") or info["url"])));im.verify()
im=Image.open(io.BytesIO(get(info.get("thumburl") or info["url"]))).convert("RGB")
if min(im.size)<350:raise RuntimeError("Source resolution inadequate")
out=p.parent/"images"/"commons-cc0-chasmanthium-latifolium-glume-lemma.jpg"
im.save(out,"JPEG",quality=90,optimize=True)
for panel in s["visual_comparison"]["items"]:
 if panel.get("source_page")==source and not panel.get("image_url","").startswith("content/"):
  panel["original_external_image_url"]=panel["image_url"]
  panel["image_url"]=str(out)
  panel["creator"]=artist
  panel["photo_status"]="Original image-level CC0 checked; JPEG physically archived with EXIF removed; individual glume/lemma marker positions remain unverified."
if not any(z.get("file")=="images/"+out.name for z in s["images"]):
 s["images"].append({"file":"images/"+out.name,"role":"Real exact-species source-labelled compressed spikelet with original caption describing glumes, lemmas and paleas; glumes not detached and no measured true ligule","creator":artist,"license":"CC0 1.0","source_page":source,"modifications":"JPEG RGB re-encode; EXIF stripped","photo_status":"LOCAL ARCHIVE; separate microscopic arrows held"})
s["field_id_finish_pass"]["lane5_cc0_floret_20261023"]={"new_local_real_photo":1,"rights":"CC0 original image-level verified","local_file":"images/"+out.name,"stage":"FIELD_READY_PHOTO_GAPS","remaining":"Actual <=1mm membranous ligule tip with scale; isolated two basal glumes and lemma positions, single rooted Hays voucher, pixel verified arrows and mobile Pages QA"}
p.write_text(json.dumps(s,indent=2,ensure_ascii=False)+"\n")
pathlib.Path("reports/lane5-chasmanthium-cc0-floret-20261023.json").write_text(json.dumps({"source":source,"license":license,"creator":artist,"archive":str(out)},indent=2)+"\n")
print(str(out))
