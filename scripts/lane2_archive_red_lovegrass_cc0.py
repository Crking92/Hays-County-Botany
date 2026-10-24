#!/usr/bin/env python3
"""Archive one verified CC0 red lovegrass specimen image to the ordinary learner."""
import pathlib,json,io,urllib.request,urllib.parse,hashlib
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Eragrostis/eragrostis-secundiflora")
p=base/"species.json"
title="File:Eragrostis secundiflora - Flickr - aspidoscelis (2).jpg"
source="https://commons.wikimedia.org/wiki/File:Eragrostis_secundiflora_-_Flickr_-_aspidoscelis_(2).jpg"
report={"taxon":"Eragrostis secundiflora","source":source,"status":"HOLD"}
try:
 api="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","prop":"imageinfo","iiprop":"url|extmetadata","titles":title,"format":"json"})
 def get(url):
  with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Hays-Botany-Field-Learner/1.0 (CC0 educational photo archive)"}),timeout=70) as r:return r.read()
 info=next(iter(json.loads(get(api))["query"]["pages"].values()))["imageinfo"][0]
 assert "CC0" in info["extmetadata"]["LicenseShortName"]["value"].upper()
 raw=get(info["url"]);assert 30000<len(raw)<12000000
 image=Image.open(io.BytesIO(raw));image.verify()
 image=Image.open(io.BytesIO(raw)).convert("RGB")
 assert image.size==(3600,2400),image.size
 dest=base/"images/patrick-alexander-eragrostis-secundiflora-2.jpg"
 dest.parent.mkdir(exist_ok=True,parents=True)
 image.save(dest,"JPEG",quality=90,optimize=True)
 data=json.loads(p.read_text())
 assert data["id"]=="eragrostis-secundiflora"
 if not any(x.get("source_page")==source for x in data["images"]):
  data["images"].append({"file":"images/"+dest.name,"role":"Species-labelled source photo, provisional visual review; anatomy to be assigned only after individual pixel review","creator":"Patrick Alexander","license":"CC0 1.0","license_url":"https://creativecommons.org/publicdomain/zero/1.0/","source_page":source,"public_reuse":"CC0; voluntary source and photographer credit","modifications":"RGB JPEG re-encoded without EXIF/GPS","photo_status":"PROVISIONAL — USER PHOTO REVIEW PENDING; no microstructure or subspecies identity inferred"})
 if not any(x.get("source_page")==source for x in data["visual_comparison"]["items"]):
  data["visual_comparison"]["items"].insert(2,{"label":"Red lovegrass — additional CC0 source photograph","scientific_name":"Eragrostis secundiflora","image_url":str(dest),"image_fit":"contain","image_role":"Separate species-labelled specimen view — individual anatomy review pending","caption":"Patrick Alexander's photograph of source-identified red lovegrass. Compare with the existing dense and dry flowering branches; do not infer individual ligule hairs, glume nerves or a particular subspecies from this image.","why_it_matters":"A further exact-species source view, held provisional for ordinary public visual review.","creator":"Patrick Alexander","license":"CC0 1.0","source_page":source,"markers":[],"photo_status":"PROVISIONAL — USER PHOTO REVIEW PENDING"})
 data["curation_status"]["photo_metadata_count"]=len(data["images"])
 data["curation_status"]["photo_files_present"]=sum(x["file"].startswith("images/") for x in data["images"])
 p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
 report.update(status="ARCHIVED",path=str(dest),sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),dimensions=list(image.size))
except Exception as e:report["error"]=str(e)
audit=pathlib.Path("reports/lane2-red-lovegrass-cc0-archive-20261023.json")
audit.parent.mkdir(parents=True,exist_ok=True)
audit.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
