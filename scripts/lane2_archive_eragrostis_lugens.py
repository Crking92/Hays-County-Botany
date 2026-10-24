#!/usr/bin/env python3
"""Lane 2: archive existing rights-cleared Eragrostis lugens source photographs."""
import io,json,pathlib,urllib.parse,urllib.request,hashlib
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Eragrostis/eragrostis-lugens")
p=base/"species.json"; d=json.loads(p.read_text())
assert d["id"]=="eragrostis-lugens"
targets=[("File:Eragrostis lugens plant2 (7324868794).jpg","harry-rose-lugens-leaf-sheath.jpg","Narrow blades and leaf sheaths, not a proven true-ligule macro"),
("File:Eragrostis lugens seeds.jpg","usda-lugens-seeds.jpg","USDA seed/caryopsis image; not a dissected mature spikelet")]
report={"species":d["id"],"results":[]}
def get(url):
 with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"HaysBotanyID/1.0 (educational grass photo archives)"}),timeout=75) as r:return r.read()
for title,name,role in targets:
 source="https://commons.wikimedia.org/wiki/"+title.replace(" ","_")
 item={"source":source,"target":name,"status":"HOLD"}
 try:
  api="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","prop":"imageinfo","iiprop":"url|extmetadata","titles":title,"format":"json"})
  info=next(iter(json.loads(get(api))["query"]["pages"].values()))["imageinfo"][0]
  meta=info["extmetadata"]["LicenseShortName"]["value"]
  if "plant2" in title:assert "BY 2.0" in meta.upper(),meta
  else:assert "PUBLIC DOMAIN" in meta.upper() or "PD" in meta.upper(),meta
  original=get(info["url"]);assert 10000<len(original)<20000000
  Image.open(io.BytesIO(original)).verify()
  image=Image.open(io.BytesIO(original)).convert("RGB")
  assert min(image.size)>400
  dst=base/"images"/name;dst.parent.mkdir(exist_ok=True,parents=True);image.save(dst,"JPEG",quality=91,optimize=True)
  rec=next(x for x in d["images"] if x["source_page"]==source)
  rec["original_external_file"]=rec["file"];rec["file"]="images/"+name
  rec["modifications"]="RGB JPEG re-encode; EXIF/GPS removed"
  rec["photo_status"]="Locally archived; individual organ anatomy not independently pixel verified"
  if not any(v.get("source_page")==source for v in d["visual_comparison"]["items"]):
   d["visual_comparison"]["items"].insert(2,{"label":"Mourning lovegrass — "+("leaf/sheath" if "plant2" in title else "USDA seeds"),"scientific_name":"Eragrostis lugens","image_url":str(dst),"image_fit":"contain","image_role":role,"caption":"Source-labelled specimen photograph, useful for comparison but not proof of natural fresh leaf rolling, true ligule, or dissected spikelet.","why_it_matters":"A second botanical view complements the archived herbarium specimens.","creator":rec["creator"],"license":rec["license"],"source_page":source,"markers":[],"photo_status":"PROVISIONAL — USER PHOTO REVIEW PENDING"})
  item.update(status="ARCHIVED",sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),dimensions=list(image.size))
 except Exception as e:item["error"]=str(e)
 report["results"].append(item)
if any(x["status"]=="ARCHIVED" for x in report["results"]):
 d["curation_status"]["photo_files_present"]=sum(v["file"].startswith("images/") for v in d["images"])
 d["field_photo_quickcheck"]["featured_photo_indices"]=[i for i,v in enumerate(d["images"]) if v["file"].startswith("images/")]
 p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
out=pathlib.Path("reports/lane2-eragrostis-lugens-archive-20261023.json");out.parent.mkdir(exist_ok=True,parents=True);out.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
