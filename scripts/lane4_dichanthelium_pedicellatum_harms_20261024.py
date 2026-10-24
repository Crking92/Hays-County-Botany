#!/usr/bin/env python3
"""Lane 4 second pass — Bob Harms exact-source D. pedicellatum photo anatomy.
Source permits credited scientific/educational reuse only; do not relicense.
"""
import io,json,pathlib,hashlib,urllib.request,urllib.error,time
from PIL import Image,ImageOps
root=pathlib.Path("content/taxa/Poaceae/Dichanthelium/dichanthelium-pedicellatum")
p=root/"species.json"
card=json.loads(p.read_text());assert card["id"]=="dichanthelium-pedicellatum"
base="https://w3.biosci.utexas.edu/prc/Monocots/"
imagebase=base+"GrassHTML/data/images/"
pagebase=base+"GrassHTML/data/pages/"
specs=[
 ("DIPE4-b","entire upper flowering plant, leaves and panicles; ROOTS NOT VISIBLE","WHOLE SHOOT — authentic flowering stems and leaf blades"),
 ("DIPE4-I","branched terminal flowering panicles; scattered oval spikelets and exserted reddish floral parts","PANICLE — multiple connected spikelets"),
 ("DIPE4-J1","actual true obovoid spikelets on slender stalks with photographer's ruler","SPIKELETS — scaled attached oval reproductive units"),
 ("DIPE4-s","closer flowering spikelets and reproductive exserted parts against original ruler","FLOWERING MACRO — attached spikelets, not a complete dissection"),
 ("DIPE4-C","real culm, blade bases and long papilla-based hairs; LIGULE NOT MEASURED","SHEATH HAIRS — true source-pictured culm and leaf bases"),
 ("DIPE4-9","leaf sheath and blade attachment with long hairs and original scale; TRUE ligule edge not independently measured","COLLAR REGION — blade base, sheath, hair placement")
]
report={"species":"Dichanthelium pedicellatum","added":[],"held":[],"source_permission":"Bob Harms Selected Central Texas Monocots — only credited scientific/educational use; no CC or commercial relicensing","pixel_arrow_status":"No new coordinates until archive image pixels and gallery cropping individually QA"}
def fetch(u):
 for attempt in range(3):
  try:
   with urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"HaysCountyBotany/1.0 educational credited photo archive"}),timeout=55) as v:
    return v.read()
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or attempt==2:raise
   time.sleep(8*(attempt+1))
rights=fetch(base).decode("utf-8","replace")
assert "free for scientific and educational uses" in rights.lower() and "bob harms" in rights.lower(),"Selected Monocots educational grant not verified"
for code,role,label in specs:
 local="images/bob-harms-"+code.lower()+"-pedicellatum.jpg"
 if any(im.get("file")==local for im in card["images"]):continue
 try:
  page=pagebase+code+".html"
  html=fetch(page).decode("utf-8","replace").lower()
  assert "dichanthelium pedicellatum" in html and "bob harms" in html,"Individual page taxon/creator mismatch"
  imgurl=imagebase+code+".jpg"
  data=fetch(imgurl);assert 10000<len(data)<12000000
  image=Image.open(io.BytesIO(data));image.verify()
  image=Image.open(io.BytesIO(data))
  image=ImageOps.exif_transpose(image).convert("RGB")
  assert min(image.size)>=340,"Too small for teaching"
  path=root/local;path.parent.mkdir(parents=True,exist_ok=True)
  image.save(path,"JPEG",quality=91,optimize=True)
  sha=hashlib.sha256(path.read_bytes()).hexdigest()
  card["images"].append({"file":local,"role":role,"creator":"Bob Harms","license":"© Bob Harms — credited scientific and educational reuse only; NOT Creative Commons","license_url":base,"source_page":page,"source_image":imgurl,"source_taxon":"Dichanthelium pedicellatum","public_reuse":"Original photographer expressly permits scientific/educational use with proper credit; no generic CC grant","image_sha256":sha,"archived_dimensions":list(image.size),"modifications":"RGB JPEG re-encoded without EXIF/GPS","photo_status":"LOCAL AUTHOR-DOCUMENTED PHOTO; organ-level arrows pending pixel QA"})
  card.setdefault("visual_comparison",{}).setdefault("items",[]).append({"label":"CEDAR ROSETTE GRASS — "+label,"scientific_name":"Dichanthelium pedicellatum","image_url":str(path).replace("\\","/"),"image_fit":"contain","image_role":role,"caption":"Original Bob Harms Selected Central Texas Monocots exact species photograph. Credit Bob Harms. Rulers show original source scale where present; no new microstructure arrows. Species voucher location not certified Hays.","creator":"Bob Harms","license":"© Bob Harms — scientific/educational with credit (not CC)","license_url":base,"source_page":page,"markers":[],"photo_status":"Original visual photo inspected at source; hold on submillimeter scale/ligule and spikelet dissection"})
  report["added"].append({"source":page,"local":str(path),"sha256":sha,"dimensions":list(image.size),"role":role})
 except Exception as e:report["held"].append({"source":code,"reason":str(e)})
if report["added"]:
 card.setdefault("field_id_finish_pass",{})["lane4_secondpass_harms_anatomy_20261024"]={
   "status":"FIELD_READY_PHOTO_GAPS",
   "new_exact_species_photographs":len(report["added"]),
   "photo_source":"Bob Harms Selected Central Texas Monocots exact species photo plates DIPE4",
   "photo_permission":"Credited scientific educational use only, not CC",
   "verified_photographed_roles":["complete flowering upper culms with attached leaves","real separated-looking but attached blooming panicle spikelets","true blade/sheath/hair placement"],
   "not_proven":["one continuous rooted corm to flowering panicle","0.25–0.5 mm true hair-curtain ligule with calibrated micro reference","physically isolated 3–3.5 mm spikelet glumes, sterile lemma and fertile lemma with 1mm bar"],
   "arrow_additions":0,"pages":"Not independently verified"
 }
 card.setdefault("learner_visual_status",{})["image_count"]=len(card["images"])
 card.setdefault("curation_status",{})["photo_metadata_count"]=len(card["images"])
 p.write_text(json.dumps(card,indent=2,ensure_ascii=False)+"\n")
rp=pathlib.Path("reports/lane4-dichanthelium-pedicellatum-harms-anatomy-20261024.json")
rp.parent.mkdir(exist_ok=True)
rp.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
