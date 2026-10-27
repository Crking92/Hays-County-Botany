#!/usr/bin/env python3
"""Lane5 actual Bromus lanceolatus licensed anatomical and field habit photo archive.
Individually verifies same exact taxon research grade observation, photo cc-by,
creator, image bytes and JPEG. No false roots, tiny ligule or glume nervation.
"""
import csv,hashlib,io,json,pathlib,re,time,urllib.request,urllib.error
from PIL import Image,ImageOps
ROOT=pathlib.Path("content/taxa/Poaceae/Bromus/bromus-lanceolatus")
CARD=ROOT/"species.json";LEDGER=ROOT/"image-sources.csv"
REPORT=pathlib.Path("reports/lane5-bromus-lanceolatus-licensed-texas-four-20261027.json")
CANDIDATES=[
{"obs":40865149,"id":64786436,"credit":"Tyler Cannon","role":"Whole live flowering branch: several large green, multi-flowered, lance-shaped spikelets attached in a branching panicle amid other vegetation; plant roots hidden",
 "title":"LIVE GREEN PANICLE — Texas lanceolate brome spikelets attached in the field",
 "caption":"Austin source-identified lanceolate brome with several long, many-flowered green spikelets attached to an open upper panicle. The source image includes other green vegetation, so do not attribute every background blade to the target plant. Roots, inner ligule, physical scale and individual glume veins are not visible.",
 "why":"A real in-habitat flowering plant complements the previous detached-looking panicle and French dry-macro image.", "tiles":[0,4]},
{"obs":115574351,"id":195058582,"credit":"River Ahlquist","role":"Late-season tan, drooping mature flowering panicle attached to brown-green leafy upper culm in dry grass litter, lower root crown concealed",
 "title":"DRY FIELD STAGE — mature tawny spikelets on flowering culm",
 "caption":"Actual source-identified Texas lanceolate brome at the drying stage. Long awned spikelets and the surrounding tan foliage show the plant's appearance later in the season. The crowded debris hides connected roots and does not expose the inner blade–sheath membrane or measurable florets.",
 "why":"Shows how dry introduced brome heads differ in field appearance from the green flowering photos and the isolated spikelet macro.", "tiles":[0,1]},
{"obs":220918622,"id":391179324,"credit":"Jared Shorma","role":"Close-up source-labeled green many-flowered spikelet with long divergent awns and attached flowering axis (same plant photograph), no glume/lemma dissection",
 "title":"ACTUAL GREEN SPIKELET — crowded florets and projecting awns",
 "caption":"Photographed flowering specimen held between fingers on Devil's Waterhole Nature Trail near Burnet. Notice tightly overlapping green florets and long thin awns. Individual 3–5-veined lower and 5–7-veined upper glumes are NOT isolated here; the exact fertile lemma bifid tip and its awn insertion remain hidden by overlapping bracts.",
 "why":"Bridges the green whole head and Yves Bas's dried close-up with a closer real Texas green spikelet.", "tiles":[0,2,3]},
{"obs":275022465,"id":494284843,"credit":"Jane Weeden","role":"Lower part of true live Texas lanceolate brome flowering culm held between fingers with attached basal blade and overlapping lower sheaths visible above dry soil; roots underground and inner collar unopened",
 "title":"LOWER SHOOT ABOVE SOIL — true leaves and enclosing sheaths (roots hidden)",
 "caption":"A San Antonio source-identified flowering shoot is held near the dry ground. A narrow grass leaf runs along the culm and lower sheath tissue surrounds it. This is a lower-shoot context photo, NOT an extracted fibrous-rooted crown; the actual inner free ligule is not face-on and cannot be measured.",
 "why":"Adds a real Texas lower shoot with leaf and sheath context rather than only detached flowering spikelets.", "tiles":[1]}
]
rep={"species":"Bromus lanceolatus","date":"2026-10-27","photos":[],"holds":[],"new_arrows":0,
"not_claimed":["Attached roots/crown","True 1–2mm inside membranous ligule","Separated/vein-counted glumes","Detached mature bifid fertile lemma with a continuous subapical awn"]}
def get(url):
 for n in range(4):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyExactLicensedGrassArchive/1.0 (educational field identification)"})
   with urllib.request.urlopen(req,timeout=45) as f:b=f.read(16000000)
   if len(b)>15500000:raise ValueError("Image/API response too large")
   return b
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or n==3:raise
   time.sleep(2*(n+1))
data=json.loads(CARD.read_text());assert data["id"]=="bromus-lanceolatus"
obs={}
newrows=[]
for spec in CANDIDATES:
 oid=spec["obs"];pid=spec["id"];rec={"observation_id":oid,"photo_id":pid}
 try:
  if oid not in obs:
   j=json.loads(get(f"https://api.inaturalist.org/v1/observations/{oid}"))
   obs[oid]=next(iter(j.get("results",[])),None)
  o=obs[oid]
  if not o or (o.get("taxon") or {}).get("name")!="Bromus lanceolatus" or o.get("quality_grade")!="research":
   raise ValueError("Exact source species or research grade not confirmed")
  place=o.get("place_guess") or ""
  if not re.search(r"(Texas|TX\b|Austin|San Antonio|Burnet)",place,re.I):raise ValueError("Texas place unverified")
  p=next((p for p in o.get("photos",[]) if p.get("id")==pid),None)
  if not p:raise ValueError("Exact image missing from current observation")
  lic=(p.get("license_code") or "").lower().replace("_","-")
  if lic!="cc-by":raise ValueError("Image-specific rights not CC BY: "+repr(lic))
  artist=p.get("attribution") or ""
  if spec["credit"].lower() not in artist.lower():raise ValueError("Creator metadata mismatch")
  source=f"https://www.inaturalist.org/photos/{pid}"
  rel=f"images/tx-lanceolate-brome-{pid}.jpg"
  if any(im.get("file")==rel or im.get("source_page")==source for im in data["images"]):
   raise ValueError("Previously installed, duplicate prohibited")
  image_url=re.sub(r"/(?:square|small|medium|thumb|large)\.(jpe?g|png)",r"/original.\1",p.get("url") or "")
  if not image_url.startswith("https://") or "/original." not in image_url:raise ValueError("Unexpected photo CDN URL")
  binary=get(image_url)
  with Image.open(io.BytesIO(binary)) as im:im.verify()
  with Image.open(io.BytesIO(binary)) as im:
   im=ImageOps.exif_transpose(im).convert("RGB")
   if min(im.size)<650:raise ValueError("Source image resolution too small")
   im.thumbnail((2000,2000));pixels=list(im.size)
   out=io.BytesIO();im.save(out,"JPEG",quality=90,optimize=True);photo=out.getvalue()
  dest=ROOT/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(photo)
  with Image.open(dest) as im:im.verify()
  sha=hashlib.sha256(photo).hexdigest()
  data["images"].append({"file":rel,"role":spec["role"],"creator":spec["credit"],
    "license":"CC BY","license_code_exact":"cc-by","license_source_page":source,
    "source_page":source,"source_observation":f"https://www.inaturalist.org/observations/{oid}",
    "photo_id":pid,"source_taxon":"Bromus lanceolatus, research-grade observation on checked date",
    "source_region":place,"modifications":"Source original re-encoded JPEG with EXIF/GPS stripped; no anatomical arrows",
    "public_reuse":"Individual photo CC BY license and creator checked live via iNaturalist observation API",
    "sha256":sha,"pixels":pixels,"photo_status":"Source-verified real Texas habitat anatomy only, no microscopic lengths counted"})
  idx=len(data["visual_comparison"]["items"])
  data["visual_comparison"]["items"].append({"label":spec["title"],"scientific_name":"Bromus lanceolatus",
    "image_url":str(dest),"image_fit":"contain","image_role":spec["role"],"caption":spec["caption"],
    "why_it_matters":spec["why"],"creator":spec["credit"],"license":"CC BY",
    "source_page":source,"markers":[],
    "photo_status":"Individually verified CC BY and species observation, visible anatomy checked with contact sheet; no fabricated glume/ligule/root labels"})
  for i in spec["tiles"]:
   if idx not in data["field_id_short_tiles"][i]["photo_panel_indices"]:
    data["field_id_short_tiles"][i]["photo_panel_indices"].append(idx)
  rec.update({"status":"archived","path":str(dest),"gallery_index":idx,"dimensions":pixels,"sha256":sha,"source":source})
  newrows.append((pathlib.Path(rel).name,spec["role"],spec["credit"],source,oid,pid,image_url))
 except Exception as e:rec.update({"status":"HELD","reason":str(e)})
 rep["photos" if rec["status"]=="archived" else "holds"].append(rec)
if rep["photos"]:
 data["curation_status"]["photo_metadata_count"]=len(data["images"])
 data["curation_status"]["photo_files_present"]=len(data["images"])
 data["curation_status"]["visual_finish"]="FIELD_READY_PHOTO_GAPS — genuine Texas in-situ green/dry flowering shoots, lower culm/sheath exterior and attached large awned spikelet close-up archived. Roots, true exposed calibrated ligule, backlit glumes and isolated lemma still missing."
 data.setdefault("learner_visual_status",{})["image_count"]=len(data["images"])
 data["lane5_lanceolatus_texas_20261027"]={"stage":"FIELD_READY_PHOTO_GAPS",
   "source_verified_photos":rep["photos"],"new_unverified_arrows":0,
   "still_missing":rep["not_claimed"]}
 CARD.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n")
 if LEDGER.exists():
  with LEDGER.open(newline="") as f:reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
  for filename,role,credit,url,oid,pid,original in newrows:
   if any(x.get("file_name")==filename for x in rows):continue
   row=dict.fromkeys(fields,"")
   for col,val in {"file_name":filename,"role":role,"creator":credit,"license":"CC BY",
       "source_page":url,"direct_url":original,"study_use":"verified research-grade botanical ID",
       "public_reuse":"Verified individual iNaturalist CC BY image licence","observation_id":str(oid),"photo_id":str(pid)}.items():
    if col in row:row[col]=val
   rows.append(row)
  with LEDGER.open("w",newline="") as f:wr=csv.DictWriter(f,fieldnames=fields);wr.writeheader();wr.writerows(rows)
REPORT.parent.mkdir(exist_ok=True);REPORT.write_text(json.dumps(rep,indent=2)+"\n")
print(json.dumps(rep))
