#!/usr/bin/env python3
"""Archive source-documented cane bluestem paired spikelets with photo-level rights check."""
import io,json,pathlib,urllib.parse,urllib.request,html,re
from PIL import Image
p=pathlib.Path("content/taxa/Poaceae/Bothriochloa/bothriochloa-barbinodis/species.json")
s=json.loads(p.read_text())
source="https://commons.wikimedia.org/wiki/File:J20160723-0003%E2%80%94Bothriochloa_barbinodis%E2%80%94RPBG_(28216315700).jpg"
def get(u):
 req=urllib.request.Request(u,headers={"User-Agent":"HaysBotany/1.0 (licensed specimen media)"})
 with urllib.request.urlopen(req,timeout=45) as f:return f.read()
name=urllib.parse.unquote(source.split("File:",1)[1]).replace("_"," ")
q=urllib.parse.urlencode({"action":"query","prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":"1500","titles":"File:"+name,"format":"json"})
info=next(iter(json.loads(get("https://commons.wikimedia.org/w/api.php?"+q))["query"]["pages"].values()))["imageinfo"][0]
md=info["extmetadata"]
license=re.sub("[^A-Z0-9]","",md.get("LicenseShortName",{}).get("value","").upper())
artist=html.unescape(re.sub("<[^>]*>","",md.get("Artist",{}).get("value",""))).strip()
if license!="CCBY20" or "John Rusk" not in artist:raise SystemExit("Hold: creator or license mismatch")
raw=get(info.get("thumburl") or info["url"]);im=Image.open(io.BytesIO(raw));im.verify()
im=Image.open(io.BytesIO(raw)).convert("RGB")
if min(im.size)<500:raise SystemExit("Hold: source image resolution")
dest=p.parent/"images"/"john-rusk-cane-bluestem-paired-spikelets.jpg";im.save(dest,"JPEG",quality=90,optimize=True)
for item in s["visual_comparison"]["items"]:
 if item.get("source_page")==source:
  item["former_external_url"]=item["image_url"]
  item["image_url"]=str(dest)
  item["image_role"]="Source-labelled real plant with photographed sessile and pedicellate spikelet pairs reported ~5 mm by photographer; individual glumes and awn insertion still require independent pixel verification."
  item["caption"]="John Rusk's authenticated source records sessile and pedicellate spikelets on cultivated cane bluestem, each about 5 mm. Silky branch architecture is visible. Do not infer actual glume veins, awn origins or node hairs from this view; cultivated California source, not a Texas voucher."
  item["photo_status"]="Licensed original Commons source photo now archived locally; original gross arrow coordinates retained; micromorphology requires review."
if not any(x.get("file")=="images/"+dest.name for x in s["images"]):
 s["images"].append({"file":"images/"+dest.name,"role":"True attached paired spikelets (source photographer approx 5 mm) and silky ramification, but no isolated glume or awn with calibrated scale","creator":"John Rusk","license":"CC BY 2.0","license_url":"https://creativecommons.org/licenses/by/2.0/","source_page":source,"modifications":"RGB reencode, EXIF removed","photo_status":"LOCALLY ARCHIVED; specimen source California cultivated"})
s["field_id_finish_pass"]["lane5_paired_spikelet_archive_20261023"]={"archived_file":"images/"+dest.name,"species_photo_count_locally_archived":3,"scope":"Actual source-described attached paired ~5mm spikelets; no independently measured glume anatomy or stem-node image","stage":"FIELD_READY_PHOTO_GAPS","next":"Real hairy culm node and matched KR node; detached sessile-pedicellate 1mm-rule comparison with glumes/awn origins; true ligule; Pages QA"}
p.write_text(json.dumps(s,indent=2,ensure_ascii=False)+"\n")
pathlib.Path("reports/lane5-bothriochloa-barbinodis-paired-spikelets-20261023.json").write_text(json.dumps({"source":source,"license":"CC BY 2.0","creator":"John Rusk","archived":str(dest)},indent=2)+"\n")
print("Archived",dest)
