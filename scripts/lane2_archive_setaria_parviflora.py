#!/usr/bin/env python3
"""Archive public CC BY-SA botanical anatomy images for knotroot bristlegrass."""
import json,io,pathlib,urllib.parse,urllib.request,hashlib
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Setaria/setaria-parviflora")
p=base/"species.json";j=json.loads(p.read_text());assert j["id"]=="setaria-parviflora"
target=[("sl13","stefan-lefnaer-knotty-rhizome.jpg"),("sl16","stefan-lefnaer-ligule.jpg"),("sl29","stefan-lefnaer-glume-lemma-montage.jpg")]
report={"taxon":j["id"],"results":[]}
def get(u):
 with urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"HaysCountyBotanyLearner/1.0 (educational CC BY-SA archive)"}),timeout=75) as r:return r.read()
for suffix,name in target:
 title=f"File:Setaria parviflora {suffix}.jpg";src=f"https://commons.wikimedia.org/wiki/File:Setaria_parviflora_{suffix}.jpg"
 item={"source":src,"status":"HOLD"}
 try:
  api="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","prop":"imageinfo","iiprop":"url|extmetadata","titles":title,"format":"json"})
  info=next(iter(json.loads(get(api))["query"]["pages"].values()))["imageinfo"][0]
  assert "BY-SA 4.0" in info["extmetadata"]["LicenseShortName"]["value"].upper()
  b=get(info["url"]);assert 10000<len(b)<14000000
  im=Image.open(io.BytesIO(b));im.verify();im=Image.open(io.BytesIO(b)).convert("RGB");assert min(im.size)>300
  dest=base/"images"/name;dest.parent.mkdir(parents=True,exist_ok=True);im.save(dest,"JPEG",quality=91,optimize=True)
  rec=next(x for x in j["images"] if x.get("source_page")==src)
  rec["original_remote_file"]=rec["file"];rec["file"]="images/"+name;rec["modifications"]="Original RGB JPEG re-encoded, EXIF/GPS stripped";rec["photo_review_status"]="Source-labelled, physically stored, original image annotations retained, no new speculative arrows"
  for panel in j["visual_comparison"]["items"]:
   if panel.get("source_page")==src:panel["image_url"]=str(dest);panel["photo_status"]="Local archived CC BY-SA 4.0; no new assistant microstructure arrow"
  item.update(status="ARCHIVED",dimensions=list(im.size),sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),local=str(dest))
 except Exception as e:item["error"]=str(e)
 report["results"].append(item)
if any(x["status"]=="ARCHIVED" for x in report["results"]):
 j["field_photo_quickcheck"]["featured_photo_indices"]=[i for i,v in enumerate(j["images"]) if v["file"].startswith("images/")]
 j["field_photo_quickcheck"]["warning"]="Photographer-labelled Croatian anatomy photos provide real rhizome, ligule and measured spikelet evidence but NOT Hays locality/voucher; original photographer labels are retained. Do not place new precise arrow targets without individual pixel inspection."
 j["field_id_finish_pass"]["lane2_20261023"]={"stage":"FIELD_READY_PHOTO_GAPS","new_local_diagnostic_photos":sum(x["status"]=="ARCHIVED" for x in report["results"]),"key": ["knotty rhizome","true short-hair ligule","labelled glumes and lemmas with scale"],"remaining":["same-root Hays voucher across reproductive and underground parts","bristles attached to one spikelet counted under 20x","exact arrow QA and public Pages check"],"new_arrows":0}
 p.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n")
out=pathlib.Path("reports/lane2-setaria-parviflora-anatomy-20261023.json");out.parent.mkdir(exist_ok=True,parents=True);out.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
