#!/usr/bin/env python3
"""Archive Matt Lavin's actual Schizachyrium spikelet-pair close photo."""
import io,json,pathlib,hashlib,urllib.request,urllib.parse
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Schizachyrium/schizachyrium-scoparium")
source="https://commons.wikimedia.org/wiki/File:Andropogon_scoparius_(3904157742).jpg"
report={"source":source,"status":"HOLD"}
try:
 def get(url):
  with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotany/1.0 licensed-educational-photo-archiver"}),timeout=75) as f:return f.read()
 api="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","prop":"imageinfo","iiprop":"url|extmetadata","titles":"File:Andropogon scoparius (3904157742).jpg","format":"json"})
 info=next(iter(json.loads(get(api))["query"]["pages"].values()))["imageinfo"][0]
 assert "BY-SA 2.0" in info["extmetadata"]["LicenseShortName"]["value"].upper()
 raw=get(info["url"]); assert 10000<len(raw)<15000000
 im=Image.open(io.BytesIO(raw));im.verify();im=Image.open(io.BytesIO(raw)).convert("RGB")
 assert min(im.size)>=1000
 dest=base/"images/matt-lavin-linear-spikelet-pairs-3904157742.jpg"
 im.save(dest,"JPEG",quality=92,optimize=True)
 p=base/"species.json";j=json.loads(p.read_text());assert j["id"]=="schizachyrium-scoparium"
 if not any(x.get("source_page")==source for x in j["images"]):
  j["images"].append({"file":"images/"+dest.name,"role":"Matt Lavin exact-taxon photographed linear raceme with paired spikelets, reduced pedicellate unit; not a calibrated 1-mm same-voucher dissection","creator":"Matt Lavin","license":"CC BY-SA 2.0","license_url":"https://creativecommons.org/licenses/by-sa/2.0/","source_page":source,"source_taxon_name":"Andropogon scoparius (synonym of Schizachyrium scoparium)","public_reuse":"Public CC BY-SA 2.0 with original photo attribution and ShareAlike","modifications":"Re-encoded original RGB JPEG, EXIF and location metadata removed","photo_review":"Source caption documents reduced scale-like pedicellate spikelet; avoid unlabeled mm annotations or Texas-locality claim"})
 if not any(x.get("source_page")==source for x in j["visual_comparison"]["items"]):
  j["visual_comparison"]["items"].insert(5,{"label":"PAIRED SPIKELETS · close original real linear raceme","scientific_name":"Schizachyrium scoparium","image_url":str(dest),"image_fit":"contain","image_role":"Linear spikelet-bearing raceme and reduced pedicellate spikelet; not measured in mm","caption":"Matt Lavin's original photograph under the older synonym Andropogon scoparius. The author explicitly notes the reduced scale-like pedicellate member of the paired spikelets. This image offers genuine closer reproductive architecture; do not invent exact 1-mm organ dimensions or treat it as a Hays specimen.","why_it_matters":"Unlike fluffy mature whole-head photographs, the close view offers actual spikelet pair organization to compare with KR bluestem.","creator":"Matt Lavin","license":"CC BY-SA 2.0","license_url":"https://creativecommons.org/licenses/by-sa/2.0/","source_page":source,"markers":[],"photo_status":"Original copyright-verified CC BY-SA and archived; original-source species determination, anatomically exact new arrows pending full-resolution pixel review."})
 j["field_photo_quickcheck"]["featured_photo_indices"]=[i for i in [4,10,11,13,14,len(j["images"])-1,0,7] if 0<=i<len(j["images"])]
 j["field_id_finish_pass"]["lane2_close_detail_20261023"]={"status":"FIELD_READY_PHOTO_GAPS","additional_photograph":str(dest),"actual_subject":"close paired spikelet raceme under historical synonym","unresolved":["true fully opened ligule membrane with 1-mm ruler","one intact sessile and pedicelled spikelet attached to same measured voucher and then dissected","same-rooted Hays vouchered plant"],"new_arrows":0,"public_site_QA":"NOT VERIFIED"}
 p.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n")
 report.update(status="ARCHIVED",path=str(dest),sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),size=list(im.size))
except Exception as e:report["error"]=str(e)
q=pathlib.Path("reports/lane2-closeup-little-bluestem-20261023.json");q.parent.mkdir(parents=True,exist_ok=True);q.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
