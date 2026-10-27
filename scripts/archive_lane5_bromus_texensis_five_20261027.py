#!/usr/bin/env python3
"""Lane 5 Texas brome. Archive five distinct, pixel-reviewed research grade Texas
Cleveland Powell field photographs. Per-photo license + exact observation taxon
must verify live. No glume veins or hidden ligule claimed; no unjustified arrows.
"""
import hashlib,io,json,pathlib,re,time,urllib.request,urllib.error,urllib.parse,csv
from PIL import Image,ImageOps
ROOT=pathlib.Path("content/taxa/Poaceae/Bromus/bromus-texensis")
CARD=ROOT/"species.json"
CSV=ROOT/"image-sources.csv"
REPORT=pathlib.Path("reports/lane5-bromus-texensis-five-anatomy-20261027.json")
CANDIDATES=[
{"id":68912641,"obs":43431687,"role":"True exterior split/open leaf sheath around upper culm with a narrow leaf blade diverging; inner ligule free membrane not shown",
 "label":"REAL OPEN SHEATH — blade and outer sheath, not inner ligule","tile":[1],
 "caption":"The actual source-labelled Texas brome leaf base is pulled aside to expose the green leaf/sheath edge around the stem. A true grass leaf sheath is visible. The translucent INSIDE free ligule edge and its 1–3 mm length are NOT measured or proven in this view; do not mistake the sheath edge for a ligule."},
{"id":68912716,"obs":43431687,"role":"Actual culm node at stem joint just above an attached leaf blade; rounded node band appears pale, but hair origin and root attachment not resolved",
 "label":"TRUE STEM NODE — grass joint, not a blade–sheath ligule","tile":[1],
 "caption":"This is the source-labelled actual grass STEM NODE, a paler ring across the upright culm above a leaf. Do not confuse the node ring with the leaf collar or infer rooted annual bases, nodal pubescence or ligule length."},
{"id":69047792,"obs":43520299,"role":"Living same-species flowering branch with multiple green narrow attached spikelets, each comprising overlapping awned florets",
 "label":"TEXAS FLOWERING BRANCH — multiple actual narrow awned spikelets","tile":[0,2],
 "caption":"An actual flowering branch has several distinct elongate green multi-flowered spikelets with awns radiating off a single panicle section. Finger is rough context only; no real millimeter ruler, true fibrous crown, or ligule is in view."},
{"id":69047839,"obs":43520299,"role":"In-hand intact green tapered multifloret spikelet at close field range with several overlapping florets and terminal awns",
 "label":"ATTACHED NARROW SPIKELET — green overlapping florets and awns","tile":[0,2,3],
 "caption":"A real source-labelled intact green Texas brome spikelet shows several overlapping flowering units, an awned tip, and narrow tapered form. The tiny two outer glumes, one-versus-three vein counts, exact tip shape and insertion of any individual lemma awn cannot be certified from this photo."},
{"id":69047894,"obs":43520299,"role":"Mature live-green source-identified field spikelet held upright between fingers; fine projecting straight awns and overlapping florets visible",
 "label":"MATURE-SHAPED GREEN SPIKELET — fine awns and packed florets","tile":[0,3],
 "caption":"This close-up shows a narrow source-identified brome spikelet with overlapping florets, projecting straight awns and natural upright position. The apparent points cannot establish whether the LEMMA apex is entire or bifid; keep the conflicting published descriptions explicit until a photographed measured dissection exists."}
]
def get(url):
 for attempt in range(4):
  try:
   request=urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotanySpeciesPhotoArchive/1.0 (educational open-licensed photos)"})
   with urllib.request.urlopen(request,timeout=50) as r: b=r.read(15000000)
   if len(b)>=15000000:raise ValueError("Oversize response")
   return b
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or attempt==3:raise
   time.sleep(2+attempt*3)
report={"date":"2026-10-27","species":"Bromus texensis","added":[],"holds":[],"new_arrows":0,
        "role_guardrails":["Sheath opening is NOT measured inner ligule","Culm node is NOT leaf collar","No single basal glume vein proved","No lemma apex/awn attachment proved","No fibrous rooted crown in new photos"],
        "regional_provenance":"Two source observations recorded as research grade and Texas"}
d=json.loads(CARD.read_text());assert d["id"]=="bromus-texensis"
obs_cache={}
source_records=[]
for c in CANDIDATES:
 rid=c["id"];oid=c["obs"];file="inat-texas-bromus-"+str(rid)+".jpg"
 rel="images/"+file;item={"photo_id":rid,"obs":oid}
 try:
  if oid not in obs_cache:
   j=json.loads(get(f"https://api.inaturalist.org/v1/observations/{oid}"))
   obs_cache[oid]=next(iter(j.get("results",[])),None)
  obs=obs_cache[oid]
  if not obs or (obs.get("taxon") or {}).get("name")!="Bromus texensis":raise ValueError("Observation exact species mismatch")
  if obs.get("quality_grade")!="research":raise ValueError("Not research grade at archive time")
  if not re.search(r"Texas|TX\b",obs.get("place_guess") or "",re.I):raise ValueError("Location not explicitly Texas")
  p=next((x for x in obs.get("photos",[]) if x.get("id")==rid),None)
  if not p:raise ValueError("Individual photo not in current observation")
  lic=(p.get("license_code") or "").lower().replace("_","-")
  if lic!="cc-by":raise ValueError("Individual image is not open CC BY: "+repr(lic))
  credit=p.get("attribution") or ""
  if "Cleveland Powell" not in credit:raise ValueError("Expected individual photo credit not returned")
  url=p.get("url") or ""
  uri=re.sub(r"/(?:square|small|medium|thumb|large)\.(jpe?g|png)",r"/original.\1",url)
  if uri==url or not uri.startswith("https://"):raise ValueError("Unrecognized original media URL")
  raw=get(uri)
  with Image.open(io.BytesIO(raw)) as im:im.verify()
  with Image.open(io.BytesIO(raw)) as im:
   im=ImageOps.exif_transpose(im).convert("RGB")
   if min(im.size)<600:raise ValueError("Original photo too small")
   im.thumbnail((1900,1900))
   dims=list(im.size);out=io.BytesIO();im.save(out,"JPEG",quality=91,optimize=True);b=out.getvalue()
  if any(x.get("file")==rel or x.get("source_page")==f"https://www.inaturalist.org/photos/{rid}" for x in d["images"]):
   raise ValueError("Already installed; no duplicate")
  dst=ROOT/rel;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(b)
  with Image.open(dst) as im:im.verify()
  hash_=hashlib.sha256(b).hexdigest()
  src=f"https://www.inaturalist.org/photos/{rid}"
  d["images"].append({"file":rel,"role":c["role"],"creator":"Cleveland Powell","license":"CC BY",
   "license_code":"cc-by","license_url":"https://creativecommons.org/licenses/by/4.0/",
   "source_page":src,"source_observation":f"https://www.inaturalist.org/observations/{oid}",
   "photo_id":rid,"source_taxon":"Bromus texensis, iNaturalist research grade at archive time",
   "source_region":obs.get("place_guess"),
   "modifications":"Original photo re-encoded RGB JPEG, EXIF/GPS removed; no new arrows",
   "public_reuse":"Live image-specific CC BY and creator checked from iNaturalist observation API",
   "sha256":hash_,"pixels":dims,
   "photo_status":"LICENSED REAL FIELD PHOTO — only coarse directly visible diagnostic structures certified"})
  ix=len(d["visual_comparison"]["items"])
  d["visual_comparison"]["items"].append({"label":c["label"],"scientific_name":"Bromus texensis",
   "image_url":str(dst),"image_fit":"contain","image_role":c["role"],
   "caption":c["caption"],"why_it_matters":"A documented real Texas brome anatomical view complements the original single photograph; inner ligule, roots and glume/lemma dissection still required.",
   "creator":"Cleveland Powell","license":"CC BY","license_url":"https://creativecommons.org/licenses/by/4.0/",
   "source_page":src,"markers":[],"photo_status":"Photographic role reviewed from actual source thumbnail/contact sheet, same observation/species/license checked on archive; no sub-mm arrows"})
  for ti in c["tile"]:
   if ix not in d["field_id_short_tiles"][ti]["photo_panel_indices"]:
    d["field_id_short_tiles"][ti]["photo_panel_indices"].append(ix)
  source_records.append((file,c["role"],credit,"CC BY",src,uri,oid,rid))
  item.update({"status":"archived","path":str(dst),"pixels":dims,"sha256":hash_,"panel_index":ix,"license":"CC BY"})
 except Exception as e:item.update({"status":"held","reason":str(e)})
 report["added" if item["status"]=="archived" else "holds"].append(item)
if report["added"]:
 d["curation_status"]["photo_metadata_count"]=len(d["images"])
 d["curation_status"]["photo_files_present"]=len(d["images"])
 d["curation_status"]["visual_finish"]="FIELD_READY_PHOTO_GAPS — actual Texas species-specific sheath, culm node, flowering branch and additional mature green spikelet photos now archived; ROOTED base, measured inner ligule, individually backlit glumes and lemma apex remain unphotographed."
 d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
 d["lane5_bromus_texensis_anatomy_20261027"]={
   "role":"5 new genuine source-checked Texas species photos (outer sheath/node/attached spikelets)",
   "photos":report["added"],"stage":"FIELD_READY_PHOTO_GAPS",
   "not_certified":report["role_guardrails"],
   "rights":"Individual photo CC BY, source photographer Cleveland Powell, both obs research grade as of 2026-10-27"}
 CARD.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
 if CSV.exists():
  with CSV.open(newline="") as f:reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
  existing={x.get("file_name") for x in rows}
  for file,role,credit,license_,source,uri,oid,rid in source_records:
   if file in existing:continue
   row=dict.fromkeys(fields,"")
   for key,val in {"file_name":file,"role":role,"platform":"iNaturalist","observation_id":str(oid),
    "photo_id":str(rid),"creator":"Cleveland Powell","license":license_,"source_page":source,
    "direct_image_url":uri,"study_use":"source-verified botanical identification",
    "public_reuse":"Image-level CC BY confirmed; creator/source retained"}.items():
    if key in row:row[key]=val
   rows.append(row)
  with CSV.open("w",newline="") as f:writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
pathlib.Path("reports").mkdir(exist_ok=True)
REPORT.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
