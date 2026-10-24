#!/usr/bin/env python3
"""Archive source-identified CC BY-SA Virginia wildrye glume-base anatomy."""
import pathlib,json,urllib.request,urllib.parse,io,hashlib
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Elymus/elymus-virginicus")
title="File:Elymus virginicus (3923888937).jpg"
source="https://commons.wikimedia.org/wiki/File:Elymus_virginicus_(3923888937).jpg"
out={"source":source,"status":"HOLD"}
try:
 def get(url):
  with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Hays-County-Botany/1.0 (licensed educational photo archiver)"}),timeout=70) as f:return f.read()
 api="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","prop":"imageinfo","iiprop":"url|extmetadata","titles":title,"format":"json"})
 x=next(iter(json.loads(get(api))["query"]["pages"].values()))["imageinfo"][0]
 assert "BY-SA 2.0" in x["extmetadata"]["LicenseShortName"]["value"].upper()
 raw=get(x["url"]);assert 20000<len(raw)<15000000
 im=Image.open(io.BytesIO(raw));im.verify();im=Image.open(io.BytesIO(raw)).convert("RGB")
 assert min(im.size)>=500
 dest=base/"images/matt-lavin-virginia-glume-bases.jpg"
 dest.parent.mkdir(exist_ok=True,parents=True);im.save(dest,"JPEG",quality=92,optimize=True)
 path=base/"species.json";j=json.loads(path.read_text());assert j["id"]=="elymus-virginicus"
 if not any(v.get("source_page")==source for v in j["images"]):
  j["images"].append({"file":"images/"+dest.name,"role":"Source-identified paired glumes with conspicuous curved basal region, not a locally measured Hays specimen","creator":"Matt Lavin","license":"CC BY-SA 2.0","license_url":"https://creativecommons.org/licenses/by-sa/2.0/","source_page":source,"public_reuse":"Attribution + ShareAlike required","modifications":"Original RGB JPEG re-encoded to strip EXIF/GPS","photo_status":"PROVISIONAL — USER PHOTO REVIEW PENDING; existing original-photo overlay arrows carried forward without new ones"})
 for item in j["visual_comparison"]["items"]:
  if item.get("source_page")==source and item["scientific_name"]=="Elymus virginicus":
   item["image_url"]=str(dest)
   item["photo_status"]="ACTUAL ORIGINAL-SOURCE JPEG ARCHIVED LOCALLY with CC BY-SA 2.0; previously inspected two gross glume markers preserved. Species and county-level voucher/proof pending."
 j["curation_status"]["photo_metadata_count"]=len(j["images"]);j["curation_status"]["photo_files_present"]=sum(v["file"].startswith("images/") for v in j["images"])
 j["field_photo_quickcheck"]["featured_photo_indices"]=list(dict.fromkeys(j["field_photo_quickcheck"]["featured_photo_indices"]+[len(j["images"])-1]))
 path.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n")
 out.update(status="ARCHIVED",path=str(dest),sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),dimensions=list(im.size))
except Exception as e:out["error"]=str(e)
report=pathlib.Path("reports/lane2-virginia-wildrye-glume-photo-20261023.json");report.parent.mkdir(exist_ok=True,parents=True);report.write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps(out))
