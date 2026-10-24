#!/usr/bin/env python3
"""Lane 2 physically archive authenticated Commons stinkgrass anatomy; no speculative arrows."""
import json,io,urllib.request,urllib.parse,pathlib,hashlib
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Eragrostis/eragrostis-cilianensis")
f=base/"species.json";data=json.loads(f.read_text());assert data["id"]=="eragrostis-cilianensis"
targets=[
 ("File:Eragrostis cilianensis collar1 NWS - Flickr - Macleay Grass Man.jpg","harry-rose-collar-ligule.jpg","Leaf collar closeup; distinguish ligule from longer collar hairs only after pixel review"),
 ("File:Eragrostis cilianensis Dareton spikelets1 (8678012034).jpg","harry-rose-spikelets1.jpg","Flattened multi-flowered spikelet detail; gland pits not asserted")
]
report={"species":data["id"],"results":[]}
for title,filename,role in targets:
 source="https://commons.wikimedia.org/wiki/"+title.replace("File:","File:").replace(" ","_")
 entry={"file":filename,"source":source,"status":"HOLD"}
 try:
  api="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","prop":"imageinfo","iiprop":"url|extmetadata","titles":title,"format":"json"})
  def get(u):
   req=urllib.request.Request(u,headers={"User-Agent":"HaysBotanyID/1.0 (licensed grass closeup archive)"})
   with urllib.request.urlopen(req,timeout=70) as r:return r.read()
  inf=next(iter(json.loads(get(api))["query"]["pages"].values()))["imageinfo"][0]
  assert "BY 2.0" in inf["extmetadata"]["LicenseShortName"]["value"].upper()
  raw=get(inf["url"]);assert 30000<len(raw)<18000000
  im=Image.open(io.BytesIO(raw));im.verify();im=Image.open(io.BytesIO(raw)).convert("RGB")
  assert min(im.size)>=1000
  dst=base/"images"/filename;dst.parent.mkdir(parents=True,exist_ok=True);im.save(dst,"JPEG",quality=90,optimize=True)
  remote_index=next((i for i,v in enumerate(data["images"]) if v.get("source_page")==source or filename=="harry-rose-spikelets1.jpg" and "Dareton_spikelets1" in v.get("source_page","")),None)
  if remote_index is None:
   data["images"].append({"file":"images/"+filename,"role":role,"creator":"Harry Rose","license":"CC BY 2.0","license_url":"https://creativecommons.org/licenses/by/2.0/","source_page":source,"photo_status":"PROVISIONAL — HUMAN PIXEL/ARROW REVIEW PENDING","modifications":"RGB re-encode without EXIF/GPS"})
  else:
   rec=data["images"][remote_index];rec["remote_original"]=rec["file"];rec["file"]="images/"+filename;rec["photo_status"]="Archived locally; anatomy pixel review required";rec["modifications"]="RGB JPEG re-encode without EXIF/GPS"
  gallery=data["visual_comparison"]["items"]
  if not any(x.get("source_page")==source for x in gallery):
   gallery.insert(2,{"label":"Stinkgrass — "+("true collar source photograph" if "collar" in filename else "individual spikelets source photograph"),"scientific_name":"Eragrostis cilianensis","image_url":str(dst),"image_fit":"contain","image_role":role,"caption":"Exact-species Harry Rose photograph; useful anatomical reference but no gland pits or scale-calibrated ligule measurements certified yet.","why_it_matters":"Shows an original botanical structure rather than another distant flowering clump.","creator":"Harry Rose","license":"CC BY 2.0","license_url":"https://creativecommons.org/licenses/by/2.0/","source_page":source,"markers":[],"photo_status":"PROVISIONAL — USER PHOTO REVIEW PENDING"})
  entry.update(status="ARCHIVED",local=str(dst),sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),dimensions=list(im.size))
 except Exception as e:entry["error"]=str(e)
 report["results"].append(entry)
if any(x["status"]=="ARCHIVED" for x in report["results"]):
 data["curation_status"]["photo_metadata_count"]=len(data["images"])
 data["curation_status"]["photo_files_present"]=sum(x["file"].startswith("images/") for x in data["images"])
 f.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n")
p=pathlib.Path("reports/lane2-stinkgrass-anatomy-archive-20261023.json");p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
