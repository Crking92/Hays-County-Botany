#!/usr/bin/env python3
"""Lane5 genuine Bromus texensis Texas in-situ whole plant and OPEN INNER leaf
junction photos. Three research grade Eric Knight CC BY originals, individual
photo-license and taxon verification, exact image provenance, no invented arrows.
The translucent inner membrane is photographed, but free ligule boundary and
length remain UNCERTIFIED without microscopic section and real mm scale.
"""
import hashlib,io,json,pathlib,re,time,urllib.request,urllib.error,csv
from PIL import Image,ImageOps
BASE=pathlib.Path("content/taxa/Poaceae/Bromus/bromus-texensis")
CARD=BASE/"species.json";CSV=BASE/"image-sources.csv"
OUT=pathlib.Path("reports/lane5-bromus-texensis-new-braunfels-three-20261027.json")
OBS=154120544
CANDIDATES=[
{"id":266270462,"label":"ACTUAL ROCKY-SOIL GROWTH — flowering Texas brome shoots in place",
 "role":"In-situ full flowering shoot with leaves near rocky soil and nearby live tillers; roots not exposed; more whole-plant context than earlier hand-held spikelets.",
 "caption":"Actual wild Texas brome photographed growing on rocky ground near New Braunfels, with branching green flowering stems, leaves and basal vicinity. This is not an uprooted specimen: the roots and full connected annual crown remain beneath the rocks, so it cannot prove root anatomy.",
 "tile":[0,1]},
{"id":266270589,"label":"OPENED INNER BLADE–SHEATH JUNCTION — actual translucent membrane",
 "role":"Dissected/opened green sheath at base of a true leaf blade exposes broad thin translucent white inner junction tissue, consistent with a ligule membrane; free edge and mm height not calibrated.",
 "caption":"The photographer opened the REAL inside blade–sheath junction on a source-identified Texas brome shoot. A translucent pale tissue flap is visible at the collar. It is consistent with a membranous ligule, a much better anatomical view than an outer sheath alone; nevertheless the exact free edge, any tearing artifact, hair origins and 1–3 mm height are NOT established without a true ruler/section.",
 "tile":[1]},
{"id":266270645,"label":"TRUE COLLAR SIDE VIEW — pale inner membrane beside a green stem",
 "role":"Side/oblique view of pale transparent membrane protruding at attached blade/sheath junction; exact ligule free margin cannot be measured; real intact stem and sheath.",
 "caption":"Second angle of the true blade–sheath seam shows pale translucent collar tissue projecting at the green sheath opening as the culm rises. This supports the earlier opened-junction membrane observation, but the image lacks a physical 1-mm bar and is insufficient to measure membrane height or definitively distinguish tearing.",
 "tile":[1]}
]
def get(url):
 for n in range(4):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyTexasBromeRealCollarArchive/1.0 (licensed educational grass photography)"})
   with urllib.request.urlopen(req,timeout=46) as f:b=f.read(17000000)
   if len(b)>16500000:raise ValueError("Response too large")
   return b
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or n==3:raise
   time.sleep(2+n*3)
report={"species":"Bromus texensis","date":"2026-10-27","observation":OBS,"new_photos":[],"holds":[],"new_arrows":0,
 "key_advance":"real opened inner blade–sheath membrane and side collar photographed, yet 1mm measurement and free margin unresolved",
 "missing":["Photographed actual extracted connected fibrous roots","Anatomically measured, intact true ligule free edge with 1 mm ruler","Mature glume pair separated, dorsal/backlit 1 and 3 veins measured","Source specimen fully opened mature lemma apex and awn insertion"]}
data=json.loads(CARD.read_text());assert data["id"]=="bromus-texensis"
ob=next(iter(json.loads(get(f"https://api.inaturalist.org/v1/observations/{OBS}")).get("results",[])),None)
if not ob or (ob.get("taxon") or {}).get("name")!="Bromus texensis" or ob.get("quality_grade")!="research" or "New Braunfels" not in str(ob.get("place_guess")):
 raise SystemExit("Source plant taxon, grade or New Braunfels locality could not be reconfirmed")
source_rows=[]
for c in CANDIDATES:
 pid=c["id"];item={"id":pid};source=f"https://www.inaturalist.org/photos/{pid}";file=f"inat-eric-knight-tx-{pid}.jpg";rel="images/"+file
 try:
  p=next((x for x in ob.get("photos",[]) if x.get("id")==pid),None)
  if not p:raise ValueError("Individual photo missing from exact source observation")
  if (p.get("license_code") or "").lower()!="cc-by":raise ValueError("Photo license NOT individually CC BY")
  if "Eric Knight" not in (p.get("attribution") or ""):raise ValueError("Photographer credit mismatch")
  if any(x.get("file")==rel or x.get("source_page")==source for x in data["images"]):raise ValueError("Already archived, no duplication")
  orig=re.sub(r"/(?:square|small|medium|thumb|large)\.(jpe?g|png)",r"/original.\1",p.get("url") or "")
  if not orig.startswith("https://") or "/original." not in orig:raise ValueError("Original URL error")
  raw=get(orig)
  with Image.open(io.BytesIO(raw)) as im:im.verify()
  with Image.open(io.BytesIO(raw)) as im:
   im=ImageOps.exif_transpose(im).convert("RGB")
   if min(im.size)<750:raise ValueError("Image too small for anatomy")
   im.thumbnail((2000,2000))
   dims=list(im.size);b=io.BytesIO();im.save(b,"JPEG",quality=92,optimize=True);clean=b.getvalue()
  dest=BASE/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(clean)
  with Image.open(dest) as im:im.verify()
  digest=hashlib.sha256(clean).hexdigest()
  data["images"].append({"file":rel,"role":c["role"],"creator":"Eric Knight",
    "license":"CC BY","license_code_exact":"cc-by","license_url":"https://creativecommons.org/licenses/by/4.0/",
    "source_page":source,"source_observation":f"https://www.inaturalist.org/observations/{OBS}",
    "photo_id":pid,"source_taxon":"Bromus texensis (research grade when retrieved)",
    "source_region":str(ob.get("place_guess")),
    "modifications":"Original re-encoded RGB JPEG, GPS/EXIF stripped; no burned-in arrows",
    "sha256":digest,"pixels":dims,"public_reuse":"Individual photo CC BY and exact author/source verified live from iNaturalist",
    "photo_status":"Real source-verified in-situ or collar photograph; no unobserved root or metric ligule proof"})
  i=len(data["visual_comparison"]["items"])
  data["visual_comparison"]["items"].append({"label":c["label"],"scientific_name":"Bromus texensis",
   "image_url":str(dest),"image_fit":"contain","image_role":c["role"],
   "caption":c["caption"],"why_it_matters":"Real Texas specimen photos show vegetative structures, while keeping unmeasured internal diagnostic anatomy a research hold.",
   "creator":"Eric Knight","license":"CC BY","license_url":"https://creativecommons.org/licenses/by/4.0/",
   "source_page":source,"markers":[],
   "photo_status":"Source taxonomy/image-level license verified; visible anatomical tissue reviewed in contact sheet; no microscope-certified 1mm measurement or new arrows"})
  for ti in c["tile"]:
   if i not in data["field_id_short_tiles"][ti]["photo_panel_indices"]:
    data["field_id_short_tiles"][ti]["photo_panel_indices"].append(i)
  source_rows.append((file,c["role"],source,orig,pid))
  item.update({"status":"archived","local_path":str(dest),"bytes":len(clean),"pixels":dims,"sha256":digest,"gallery_index":i})
 except Exception as e:item.update({"status":"HELD","reason":str(e)})
 report["new_photos" if item["status"]=="archived" else "holds"].append(item)
if report["new_photos"]:
 data["curation_status"]["photo_metadata_count"]=len(data["images"])
 data["curation_status"]["photo_files_present"]=len(data["images"])
 data["curation_status"]["visual_finish"]="FIELD_READY_PHOTO_GAPS — real Texas rocky-ground live plant, culm node, opened inner sheath/membrane, flowering panicle and spikelet views; free membranous ligule height, fibrous roots, and measured glumes/lemmas remain missing."
 data.setdefault("learner_visual_status",{})["image_count"]=len(data["images"])
 data.setdefault("lane5_new_braunfels_collar_20261027",{}).update({
   "photos":report["new_photos"],"status":"FIELD_READY_PHOTO_GAPS",
   "partial_role":"True collar opened and translucent flap visible; tissue orientation/metric membrane validation pending",
   "what_cannot_be_claimed":report["missing"]})
 CARD.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n")
 if CSV.exists():
  with CSV.open(newline="") as f:reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
  names={r["file_name"] for r in rows}
  for file,role,source,orig,pid in source_rows:
   if file in names:continue
   row=dict.fromkeys(fields,"")
   for k,v in {"file_name":file,"role":role,"platform":"iNaturalist","observation_id":str(OBS),
    "photo_id":str(pid),"creator":"Eric Knight","license":"CC BY","source_page":source,
    "direct_image_url":orig,"study_use":"same-voucher educational botanical anatomy",
    "public_reuse":"Image-specific CC BY confirmed; source and photographer retained"}.items():
    if k in row:row[k]=v
   rows.append(row)
  with CSV.open("w",newline="") as f:writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
