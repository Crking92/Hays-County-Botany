#!/usr/bin/env python3
"""Preserve 1906 public-domain, exact-taxon Festuca versuta illustration."""
import io,json,pathlib,time,urllib.request,urllib.error,urllib.parse
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Festuca/festuca-versuta");p=base/"species.json";d=json.loads(p.read_text());assert d["id"]=="festuca-versuta"
title="File:Contributions from the U.S. National Herbarium (1906) (20660168056).jpg"
# Source book labels this plate Festuca johnsoni, NOT Festuca versuta.
raise SystemExit("REJECTED: scanned plate XII explicitly depicts Festuca johnsoni; do not archive under Festuca versuta")
def get(url):
 for i in range(4):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotany/1.0 (public-domain botanical teaching plate)"}),timeout=60) as r:return r.read()
  except urllib.error.HTTPError as e:
   if e.code not in (429,502,503) or i==3:raise
   time.sleep(25*(i+1))
holds=[]
try:
 api="https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url%7Cextmetadata&format=json&titles="+urllib.parse.quote(title)
 info=next(iter(json.loads(get(api))["query"]["pages"].values()))["imageinfo"][0]
 meta=info["extmetadata"];license=meta.get("LicenseShortName",{}).get("value","").upper().replace("-","").replace(" ","")
 assert license in ("PUBLICDOMAIN","CC0","PDM"),"Rights hold: "+license
 data=get(info["url"]);image=Image.open(io.BytesIO(data));image.verify();image=Image.open(io.BytesIO(data)).convert("RGB")
 assert min(image.size)>550
 dest=base/"images"/"us-national-herbarium-festuca-versuta-1906.jpg";dest.parent.mkdir(exist_ok=True,parents=True);image.save(dest,"JPEG",quality=92,optimize=True)
 entry={"file":"images/"+dest.name,"role":"Historical botanical illustration labeled Festuca versuta, not a photograph; verify plate structures before annotations","creator":"Contributions from the United States National Herbarium (1906); digitized by Internet Archive","license":meta["LicenseShortName"]["value"],"source_page":"https://commons.wikimedia.org/wiki/"+urllib.parse.quote(title.replace(" ","_")),"photo_status":"REFERENCE ILLUSTRATION; not a diagnostic photo or visually certified arrow","public_reuse":"Public-domain status checked on source file"}
 if not any(x.get("file")==entry["file"] for x in d["images"]):d["images"].append(entry)
 print("ARCHIVED",dest)
except Exception as e:holds.append(str(e));print("HELD",str(e))
d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
d.setdefault("curation_status",{})["photo_metadata_count"]=len(d["images"])
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n")
r=pathlib.Path("reports/festuca-versuta-plate-archive.json");r.parent.mkdir(exist_ok=True);r.write_text(json.dumps({"holds":holds,"gallery_count":len(d["images"])},indent=2)+"\n")
