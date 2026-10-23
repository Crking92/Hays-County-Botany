#!/usr/bin/env python3
"""Archive verified CC-BY iNaturalist Chloris photo; retain holds on license/identity failure."""
import json, pathlib, urllib.request, io, hashlib
from PIL import Image, ImageOps
base=pathlib.Path("content/taxa/Poaceae/Chloris/chloris-andropogonoides")
p=base/"species.json"
report={"source":"https://www.inaturalist.org/photos/348830581","added":[],"holds":[]}
def get(url):
 req=urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotany/1.0 (licensed educational archive)"})
 with urllib.request.urlopen(req,timeout=35) as resp: return resp.read(18000001)
try:
 j=json.loads(get("https://api.inaturalist.org/v1/observations/species_counts?taxon_id=62920&page=1&per_page=1")) if False else None
 photo=json.loads(get("https://api.inaturalist.org/v1/photos/348830581"))
 result=photo.get("results",[])
 if not result:raise ValueError("Original iNaturalist photo missing")
 x=result[0]
 license=x.get("license_code","")
 if license not in ("cc-by","cc-by-sa"):raise ValueError("Not a public CC BY/SA image: "+str(license))
 attribution=x.get("attribution","")
 if "Cleveland Powell" not in attribution:raise ValueError("Expected author not confirmed: "+attribution)
 photo_url=x.get("url","")
 if not photo_url:raise ValueError("No source image URL")
 photo_url=photo_url.replace("square.","original.").replace("medium.","original.").replace("large.","original.")
 raw=get(photo_url);assert 10000<len(raw)<18000000
 with Image.open(io.BytesIO(raw)) as im:im.verify()
 with Image.open(io.BytesIO(raw)) as im:
  im=ImageOps.exif_transpose(im).convert("RGB")
  if min(im.size)<500:raise ValueError("Image too small")
  im.thumbnail((1800,1800))
  b=io.BytesIO();im.save(b,"JPEG",quality=88,optimize=True);data=b.getvalue()
 dest=base/"images/chloris-andropogonoides-cleveland-powell-ccby.jpg"
 dest.parent.mkdir(exist_ok=True);dest.write_bytes(data)
 with Image.open(dest) as im:im.verify()
 species=json.loads(p.read_text());assert species["id"]=="chloris-andropogonoides"
 if not any(z.get("source_page")==report["source"] for z in species["images"]):
  species["images"].append({"file":"images/"+dest.name,"creator":"Cleveland Powell","license":license.upper(),"source_page":report["source"],"role":"Research-grade source-labelled recognition view; species anatomy not independently certified","photo_status":"ARCHIVED; anatomical annotation pending original-pixel review","public_reuse":"CC BY/SA credited, original source retained","modifications":"Resized and EXIF stripped","sha256":hashlib.sha256(data).hexdigest()})
  species["curation_status"]["photo_files_present"]=len(species["images"])
  species["curation_status"]["photo_metadata_count"]=len(species["images"])
  species["learner_visual_status"]["image_count"]=len(species["images"])
  p.write_text(json.dumps(species,indent=2,ensure_ascii=False)+"\n")
 report["added"].append(dest.as_posix())
except Exception as exc:
 report["holds"].append(str(exc))
pathlib.Path("reports/chloris-powell-ccby-20261023.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
