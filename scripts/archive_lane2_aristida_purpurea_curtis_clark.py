#!/usr/bin/env python3
import json,io,pathlib,urllib.request,urllib.parse,hashlib
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Aristida/aristida-purpurea")
p=base/"species.json"
source="https://commons.wikimedia.org/wiki/File:Aristida_purpurea_fruits_with_awns_2003-07-03.jpg"
title="File:Aristida purpurea fruits with awns 2003-07-03.jpg"
report={"source":source,"status":"HOLD"}
try:
 api="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","prop":"imageinfo","iiprop":"url|extmetadata","titles":title,"format":"json"})
 def fetch(url):
  with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"HaysBotanyID/1.0 (educational licensed image archival)"}),timeout=65) as f:return f.read()
 info=next(iter(json.loads(fetch(api))["query"]["pages"].values()))["imageinfo"][0]
 metadata=info["extmetadata"]
 assert "BY-SA" in metadata["LicenseShortName"]["value"].upper()
 assert "2.5" in metadata["LicenseShortName"]["value"]
 b=fetch(info["url"])
 assert 50000<len(b)<12000000
 im=Image.open(io.BytesIO(b));im.verify()
 im=Image.open(io.BytesIO(b)).convert("RGB")
 assert im.width>=1800 and im.height>=1200
 dest=base/"images/curtis-clark-threeawn-fruits-awns.jpg"
 dest.parent.mkdir(parents=True,exist_ok=True)
 im.save(dest,"JPEG",quality=90,optimize=True)
 data=json.loads(p.read_text())
 assert data["id"]=="aristida-purpurea"
 rec={"file":"images/"+dest.name,"role":"Separate source-identified mature fruits and three-awn visual reference; no glumes/ligule asserted without pixel inspection","creator":"Curtis Clark","license":"CC BY-SA 2.5","license_url":"https://creativecommons.org/licenses/by-sa/2.5/","source_page":source,"public_reuse":"Attribution, ShareAlike, note JPEG re-encoding; preserve creator","photo_status":"PROVISIONAL — USER PHOTO REVIEW PENDING; awn attachment arrows withheld pending actual pixel verification","modifications":"Metadata-stripped RGB JPEG re-encode"}
 if not any(x.get("source_page")==source for x in data["images"]):data["images"].append(rec)
 if "field_photo_quickcheck" in data:
  i=next(i for i,x in enumerate(data["images"]) if x.get("source_page")==source)
  inds=data["field_photo_quickcheck"].setdefault("featured_photo_indices",[])
  if i not in inds:inds.append(i)
 data["visual_comparison"]["items"].append({"label":"PURPLE THREEAWN — fruits and spreading awns (Curtis Clark)","scientific_name":"Aristida purpurea","image_url":str(dest),"image_fit":"contain","image_role":"Mature fruit and awn review photo, source-determined; specific microscopic parts not yet verified","caption":"Curtis Clark's photographed fruits and awns. Compare spreading awn form with the already archived fingertip photograph; glume venation, ligule and same-plant roots remain undocumented.","why_it_matters":"Provides a separate mature-fruit view without borrowing a look-alike species.","creator":"Curtis Clark","license":"CC BY-SA 2.5","license_url":"https://creativecommons.org/licenses/by-sa/2.5/","source_page":source,"markers":[],"photo_status":"PROVISIONAL — photo for public review; no new anatomy arrows"})
 data["curation_status"]["photo_metadata_count"]=len(data["images"])
 data["curation_status"]["photo_files_present"]=len(data["images"])
 p.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n")
 report.update(status="ARCHIVED",file=str(dest),dimensions=list(im.size),sha256=hashlib.sha256(dest.read_bytes()).hexdigest())
except Exception as exc:report["error"]=str(exc)
out=pathlib.Path("reports/lane2-aristida-purpurea-curtis-clark-20261023.json");out.parent.mkdir(exist_ok=True,parents=True);out.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
