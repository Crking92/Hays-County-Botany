#!/usr/bin/env python3
"""Archive three PUBLICLY reusable source-verified Chasmanthium field-role photographs.
Review approved 2026-10-26: #6 basal growth IN SOIL (not rhizome proof);
#11 actual leaf blade/sheath junction (membrane NOT visible);
#12 complete hanging inflorescence (individual flat spikelets).
Never alter existing Bob Harms educational-license photos or draw micro arrows.
"""
import hashlib,html,io,json,pathlib,re,time,urllib.parse,urllib.request,urllib.error
from PIL import Image
ROOT=pathlib.Path("content/taxa/Poaceae/Chasmanthium/chasmanthium-latifolium")
CARD=ROOT/"species.json"
SPECIES=json.loads(CARD.read_text())
BASE="https://commons.wikimedia.org/w/api.php?"
REPORT=pathlib.Path("reports/lane5-chasmanthium-practical-growth-collar-20261026.json")
DESIGNS=[
 {"name":"Chasmanthium latifolium6.jpg","filename":"douglas-goldman-woodoats-live-basal-growth.jpg",
  "label":"GROWTH BASE IN HABITAT — living basal green leaves from woodland litter",
  "role":"Real same-species living lower foliage and several basal shoots emerging amid leaf litter; underground roots and rhizomes NOT exposed.",
  "caption":"Douglas Goldman photographed actual living inland sea oats near ground level in a South Carolina bottomland woodland. Broad, slightly folded green blades emerge from overlapping basal sheaths among dead leaves. This records what the BASE looks like in habitat, NOT an exposed rhizome, connected underground runner or individually dissected rooted crown. For the true shallow rhizome, compare the separate Bob Harms anatomical view only under its credited educational-use permission.",
  "why":"Crew can see a living vegetative patch at ground level instead of only a head or detached specimen. Don't confuse green shoots grouped in leaf litter with demonstrated rhizome connections.",
  "markers":[{"label":"Broad basal green blade","label_x":5,"label_y":44,"target_x":22,"target_y":71}]},
 {"name":"Chasmanthium latifolium11.jpg","filename":"douglas-goldman-woodoats-blade-sheath-collar.jpg",
  "label":"ACTUAL LEAF COLLAR — blade joining the green sheath",
  "role":"Photographer-identified vegetative leaf blade–sheath junction on a live stem; 1-mm inner membranous ligule rim not shown at microscope scale.",
  "caption":"The broad green leaf blade angles away from a narrow upright grass culm. The actual BLADE–SHEATH junction lies where that blade attaches; the sheath continues down the stem below. We can point to the visible collar area. We CANNOT call the small pale surface a photographed true ligule membrane or measure its toothed margin from this photograph; a 10–20× inner-collar view with scale is still required.",
  "why":"Separates a real leafy collar site from a panicle branch node and tells the crew where to open the sheath to find the true ligule.",
  "markers":[{"label":"Leaf blade","label_x":5,"label_y":20,"target_x":30,"target_y":40},
             {"label":"Blade–sheath junction","label_x":75,"label_y":64,"target_x":55,"target_y":51}]},
 {"name":"Chasmanthium latifolium12.jpg","filename":"douglas-goldman-woodoats-complete-hanging-seedhead.jpg",
  "label":"COMPLETE HEAD — hanging flat spikelets on separate slender stalks",
  "role":"Whole pendulous flowering panicle with several distinct flat tan spikelets on thin pedicels, against dark backdrop.",
  "caption":"A genuine attached inland sea oats panicle. Follow the slender overhead arching flowering axis: many separate flat, fish-shaped SPIKELETS hang beneath it on fine stalks. Each 'fish' is one MANY-FLORETED spikelet—not a single seed or an individual floret. This clear whole-head photo is useful alongside its rooted green basal habit image.",
  "why":"Teaches full reproductive architecture in one frame and can be used without relying only on copyrighted, educationally permitted macro plates.",
  "markers":[{"label":"Arching flowering axis","label_x":4,"label_y":8,"target_x":57,"target_y":10},
             {"label":"One whole hanging spikelet","label_x":82,"label_y":78,"target_x":73,"target_y":64}]}
]
def get(url):
 req=urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotany/1.0 (licensed botanical field training)"})
 for attempt in range(5):
  try:
   with urllib.request.urlopen(req,timeout=50) as x:return x.read()
  except urllib.error.HTTPError as e:
   if e.code not in (429,502,503) or attempt==4:raise
   time.sleep(3*(attempt+1))
result={"species":"Chasmanthium latifolium","source":"Commons Douglas Goldman Congaree, SC series","rights":"CC BY-SA 4.0 individually verified and attribution retained; new JPEG RGB re-encode strips GPS/EXIF","photos":[],"warnings":[]}
for spec in DESIGNS:
 name=spec["name"];source="https://commons.wikimedia.org/wiki/File:"+name.replace(" ","_")
 dest=ROOT/"images"/spec["filename"];rel="images/"+spec["filename"]
 try:
  if dest.exists() and any(x.get("file")==rel for x in SPECIES["images"]) and any(p.get("image_url")==str(dest) for p in SPECIES["visual_comparison"]["items"]):
   result["photos"].append({"source":source,"path":str(dest),"status":"previously_archived"})
   continue
  query=urllib.parse.urlencode({"action":"query","prop":"imageinfo|categories","format":"json","iiprop":"url|extmetadata","cllimit":"max","iiurlwidth":"1800","titles":"File:"+name})
  page=next(iter(json.loads(get(BASE+query))["query"]["pages"].values()))
  info=page["imageinfo"][0];meta=info.get("extmetadata",{})
  license=re.sub(r"[^A-Z0-9]","",meta.get("LicenseShortName",{}).get("value","").upper())
  artist=html.unescape(re.sub(r"<[^>]+>"," ",meta.get("Artist",{}).get("value",""))).strip()
  if license!="CCBYSA40" or "Douglas" not in artist or "Category:Chasmanthium latifolium" not in [x["title"] for x in page.get("categories",[])]:
   raise ValueError("Individual license, creator, or source-taxonomy mismatch: "+license+" / "+artist)
  raw=get(info.get("thumburl") or info["url"])
  img=Image.open(io.BytesIO(raw));img.verify()
  img=Image.open(io.BytesIO(raw)).convert("RGB")
  if min(img.size)<650:raise ValueError("image resolution too low "+str(img.size))
  dest.parent.mkdir(parents=True,exist_ok=True)
  img.save(dest,"JPEG",quality=91,optimize=True)
  SPECIES["images"].append({
   "file":rel,"role":spec["role"],"creator":"Douglas Goldman","license":"CC BY-SA 4.0",
   "license_url":"https://creativecommons.org/licenses/by-sa/4.0/","source_page":source,
   "source_original_url":info["url"],"source_location":"Congaree River floodplain, Richland County, South Carolina — NOT a Hays voucher",
   "public_reuse":"Permitted under exact Commons CC BY-SA 4.0; credit, license link and re-encode changes recorded.",
   "modifications":"Recompressed RGB JPEG, original EXIF/GPS removed, digital arrows separate from source file.",
   "photo_status":"OPEN-LICENSE SOURCE VERIFIED; CREW GROWTH/LEAF/HEAD ROLE; tiny ligule membrane and underground rhizomes not resolved.",
   "pixels":list(img.size),"sha256":hashlib.sha256(dest.read_bytes()).hexdigest()})
  SPECIES["visual_comparison"]["items"].insert(0,{
   "label":spec["label"],"scientific_name":"Chasmanthium latifolium",
   "image_url":str(dest),"image_fit":"contain","image_role":spec["role"],
   "caption":spec["caption"],"why_it_matters":spec["why"],
   "creator":"Douglas Goldman","license":"CC BY-SA 4.0",
   "license_url":"https://creativecommons.org/licenses/by-sa/4.0/","source_page":source,
   "markers":spec["markers"],
   "photo_status":"Exact source pixel preview inspected before annotation 2026-10-26. Gross visible blade/junction/spikelet markers only. No true ligule, rhizome, or unseen lemma microcharacters arrowed. Final website/mobile alignment pending."
  })
  result["photos"].append({"source":source,"path":str(dest),"status":"archived",
   "pixels":list(img.size),"markers":len(spec["markers"]),"license":"CC BY-SA 4.0"})
 except Exception as e:
  result["photos"].append({"source":source,"status":"HELD","reason":str(e)[:250]})
if any(z["status"]=="archived" for z in result["photos"]):
 # Preserve core and preexisting records, including science holds and copyright statuses.
 SPECIES["field_id_finish_pass"]["lane5_practical_photo_finish_20261026"]={
  "stage":"FIELD_READY_PHOTO_GAPS",
  "rights_review":"This card has zero NC gallery panels, BUT one dormant archived CC BY-NC image record and multiple copyrighted Bob Harms originals. Do not relicense Bob photos or treat the limited external-display permission memo as blanket archival/derivative permission. Prior rights metadata preserved.",
  "new_cc_bysa_public_photos":result["photos"],
  "field_training_roles":"Living in-soil basal shoots, true blade-to-sheath collar location, complete attached arching flowering panicle; existing visible rhizome photo remains Bob Harms educational-rights/scope-limited.",
  "next_critical":["True inner short membranous ligule edge with actual 1-mm scale and anatomical confirmation","Author-permitted exact rhizome photo use in final public snapshot, or acquire replacement openly licensed actually exposed connected rhizome","Confirmed pixel marker positioning in live/mobile page and photo rights-filtered deploy check"],
  "diagnostic_exception":"Flat pendulous many-flowered spikelets are well documented already; extra detailed glume dissection is not top crew priority unless distinguishing Chasmanthium laxum/sessiliflorum.",
  "not_finished":"Source plant photos from South Carolina, no same-vouchered Hays plant with collar and rhizome; do not mark 100%."
 }
 CARD.write_text(json.dumps(SPECIES,ensure_ascii=False,indent=2)+"\n")
REPORT.write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result))
