#!/usr/bin/env python3
"""Lane 2: archive three visually selected original species photos, preserve licensing."""
import json,io,pathlib,urllib.request,urllib.parse,hashlib
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Eragrostis/eragrostis-hirsuta")
p=base/"species.json";j=json.loads(p.read_text());assert j["id"]=="eragrostis-hirsuta"
selected=[(1,"douglas-goldman-hairy-sheath.jpg","Clearly photographed dense pale hairs on sheath at mouth below protruding blade; true ligule not individually resolved"),
(2,"douglas-goldman-bearded-panicle-axil.jpg","Distinct tufted branch axil hairs at true primary panicle branch junction, plus attached spikelets"),
(3,"douglas-goldman-single-spikelet.jpg","Single laterally flattened small spikelet on thin pedicel, no measurement ruler")]
report={"taxon":j["id"],"results":[]}
def get(u):
 with urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"HaysCountyBotanyLearner/1.0 (CC BY-SA archival)"}),timeout=65) as f:return f.read()
for n,name,role in selected:
 title=f"File:Eragrostis hirsuta{n}.jpg";src="https://commons.wikimedia.org/wiki/"+title.replace(" ","_")
 record={"source":src,"status":"HOLD"}
 try:
  api="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","prop":"imageinfo","iiprop":"url|extmetadata","titles":title,"format":"json"})
  inf=next(iter(json.loads(get(api))["query"]["pages"].values()))["imageinfo"][0]
  assert "BY-SA 4.0" in inf["extmetadata"]["LicenseShortName"]["value"].upper()
  raw=get(inf["url"]);assert 30000<len(raw)<12000000
  im=Image.open(io.BytesIO(raw));im.verify();im=Image.open(io.BytesIO(raw)).convert("RGB");assert min(im.size)>1000
  dest=base/"images"/name;dest.parent.mkdir(parents=True,exist_ok=True);im.save(dest,"JPEG",quality=91,optimize=True)
  if not any(v.get("source_page")==src for v in j["images"]):
   j["images"].append({"file":"images/"+name,"role":role,"creator":"Douglas Goldman","license":"CC BY-SA 4.0","license_url":"https://creativecommons.org/licenses/by-sa/4.0/","source_page":src,"public_reuse":"CC BY-SA 4.0: attribution, indicate RGB JPEG conversion, ShareAlike","modifications":"Re-encoded original into EXIF/GPS-free RGB JPEG","photo_status":"VISUALLY REVIEWED from seven-source contact sheet; exact microscopic label arrows withheld"})
  if not any(v.get("source_page")==src for v in j["visual_comparison"]["items"]):
   j["visual_comparison"]["items"].insert(n-1,{"label":{1:"TRUE SHEATH MOUTH · long dense hairs",2:"BEARDED PANICLE BRANCH AXIL · real hair tuft",3:"ISOLATED ATTACHED SPIKELET · actual reproductive unit"}[n],"scientific_name":"Eragrostis hirsuta","image_url":str(dest),"image_fit":"contain","image_role":role,"caption":role+". Douglas Goldman, original exact-species CC BY-SA 4.0 photograph. Do not label the tiny ligule, gland or floret number from these unscaled pictures.","why_it_matters":{1:"See hairs along the real sheath mouth and body, not an imaginary ligule.",2:"Panicle axil beard is a real important species-level clue.",3:"See one isolated spikelet on a fine stalk without guessing dimensions."}[n],"creator":"Douglas Goldman","license":"CC BY-SA 4.0","license_url":"https://creativecommons.org/licenses/by-sa/4.0/","source_page":src,"markers":[],"photo_status":"PIXEL REVIEWED on photo contact sheet 2026-10-23; no unverified arrow coordinate."})
  record.update(status="ARCHIVED",path=str(dest),dimensions=list(im.size),sha256=hashlib.sha256(dest.read_bytes()).hexdigest())
 except Exception as ex: record["error"]=str(ex)
 report["results"].append(record)
if any(v["status"]=="ARCHIVED" for v in report["results"]):
 j["field_photo_quickcheck"]["featured_photo_indices"]=list(range(len(j["images"])))
 j["field_photo_quickcheck"]["warning"]="New Douglas Goldman exact-species CC BY-SA photographs visually screened for sheath hairs, true bearded panicle branch axil, and attached single spikelet; do not infer short inner ligule margin or calibrated florets. All markers withheld pending full-resolution precise pixel placement."
 j["field_id_finish_pass"]["lane2_photo_finish_20261023"]={"status":"FIELD_READY_PHOTO_GAPS","archived_candidates":sum(v["status"]=="ARCHIVED" for v in report["results"]),"exact_morphology":["sheath-mouth hairs","bearded primary panicle axil","isolated attached spikelet"],"remaining":["actual true short hair-fringe ligule at true inner collar with mm scale","single mature 2-4 mm spikelet dissection with floret count and ruler","precisely positioned new pixel markers and Pages QA"],"pages":"NOT_VERIFIED"}
 p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+"\n")
out=pathlib.Path("reports/lane2-eragrostis-hirsuta-selected-20261023.json");out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
