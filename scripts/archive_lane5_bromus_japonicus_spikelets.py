#!/usr/bin/env python3
"""Archive one exact Japanese brome reproductive photograph, with Commons rights validation."""
import io,json,pathlib,urllib.request,urllib.parse,html,re
from PIL import Image
p=pathlib.Path("content/taxa/Poaceae/Bromus/bromus-japonicus/species.json")
data=json.loads(p.read_text())
source="https://commons.wikimedia.org/wiki/File:Bromus_japonicus_(3920836312).jpg"
def get(u):
 req=urllib.request.Request(u,headers={"User-Agent":"HaysBotany/1.0 (licensed grass photography)"})
 with urllib.request.urlopen(req,timeout=50) as f:return f.read()
q=urllib.parse.urlencode({"action":"query","prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":"1500","titles":"File:Bromus japonicus (3920836312).jpg","format":"json"})
info=next(iter(json.loads(get("https://commons.wikimedia.org/w/api.php?"+q))["query"]["pages"].values()))["imageinfo"][0]
md=info["extmetadata"];lic=re.sub("[^A-Z0-9]","",md.get("LicenseShortName",{}).get("value","").upper())
artist=html.unescape(re.sub("<[^>]*>","",md.get("Artist",{}).get("value",""))).strip()
if lic!="CCBYSA20" or "Matt Lavin" not in artist:raise SystemExit("Rights/creator hold")
raw=get(info.get("thumburl") or info["url"]);im=Image.open(io.BytesIO(raw));im.verify()
im=Image.open(io.BytesIO(raw)).convert("RGB")
if min(im.size)<400:raise SystemExit("Image too small")
dest=p.parent/"images"/"matt-lavin-bromus-japonicus-spikelet-nervation.jpg"
im.save(dest,"JPEG",quality=90,optimize=True)
url=str(dest)
for item in data["visual_comparison"]["items"]:
 if item.get("source_page")==source:
  item["archived_original_image_url"]=item["image_url"];item["image_url"]=url
  item["photo_status"]="Physically stored licensed species spikelet reference; fine vein/awn arrows require pixel verification"
if not any(i.get("file")=="images/"+dest.name for i in data["images"]):
 data["images"].append({"file":"images/"+dest.name,"role":"Actual overlapping mature spikelets and awn-bearing lemmas; no calibrated isolated glumes","creator":"Matt Lavin","license":"CC BY-SA 2.0","source_page":source,"photo_status":"Locally archived; precise anatomical arrows not yet verified"})
data["visual_comparison"]["items"]=[x for x in data["visual_comparison"]["items"] if x.get("license")!="CC BY-NC"]
data.setdefault("field_id_finish_pass",{})["lane5_bromus_anatomy_archive_20261023"]={"new_species_photos":1,"archived_file":"images/"+dest.name,"restricted_gallery_panel_excluded":1,"stage":"FIELD_READY_PHOTO_GAPS","remaining":"True ligule/collar, vouchered measured glumes and sterile-floret structure, careful arrow inspection, Pages QA"}
p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
pathlib.Path("reports/lane5-bromus-japonicus-anatomy-20261023.json").write_text(json.dumps({"source":source,"license":"CC BY-SA 2.0","archived":url},indent=2)+"\n")
print("Archived",url)
