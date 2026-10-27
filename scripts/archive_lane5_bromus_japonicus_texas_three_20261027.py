#!/usr/bin/env python3
"""Lane5 Japanese brome three actual Texas field and collar images.
Source-verifies accepted species, original research-grade observations, Texas
place, and individual photo CC BY author/license. Append distinct licensed
field and exterior collar panels only; NEVER assert a measured true ligule,
verified roots, or glume nerves from uncalibrated pixels.
"""
import csv,hashlib,io,json,pathlib,re,time,urllib.request,urllib.error
from PIL import Image,ImageOps
ROOT=pathlib.Path("content/taxa/Poaceae/Bromus/bromus-japonicus")
CARD=ROOT/"species.json";LEDGER=ROOT/"image-sources.csv";OUT=pathlib.Path("reports/lane5-bromus-japonicus-texas-base-collar-20261027.json")
SPECIES="Bromus japonicus"
TARGETS=[
 {"obs":280288867,"photo":503389265,"creator":"Sam Kieschnick",
  "filename":"texas-sam-kieschnick-japanese-brome-field-tuft-503389265.jpg",
  "label":"TEXAS LIVING FIELD HABIT — narrow grassy flowering plants in real pasture",
  "role":"Actual source-identified Japanese brome flowering shoot/leafy plant in Texas grassland, photographed in situ with nearby other grasses; fibrous roots hidden beneath soil, no continuous excavation.",
  "caption":"An actual Texas Japanese brome observation near Goldthwaite shows its cool-season grass habit among living surrounding plants and dry stems. This is useful for crew recognition of the plant growing outdoors. The photograph does NOT expose connected annual fibrous roots or confirm that every neighboring stem is the same individual; species identification belongs to the source focal grass.",
  "why":"Supplies a regional field-growth photo, absent from the original Japanese brome close-up and Austrian dissected imagery.",
  "tiles":[0,1,5]},
 {"obs":278531169,"photo":500116822,"creator":"Linda Jo Conn",
  "filename":"texas-linda-jo-conn-japanese-brome-sheath-500116822.jpg",
  "label":"ACTUAL TEXAS SHEATH EXTERIOR — fine hairs, leaf and culm",
  "role":"Living Texas Japanese brome blade/sheath closeup held between fingers. Actual external sheath lip and fine hairs visibly trace toward the culm, but inner true membranous ligule free edge does NOT have a calibrated ruler.",
  "caption":"A real Japanese brome grass blade and upper sheath are held apart in Rockdale, Milam County. Look at the narrow blade, the wrapping sheath edges and fine soft outer hairs. The WHITE STRIPES are not proof of a photographed 1–2 mm inner ligule free membrane: internal surface and true free edge are not separately isolated or measured.",
  "why":"Adds a genuine Texas vegetative close view that complements the two Austrian leaf-sheath macros, without substituting outer sheath hairs for the ligule.",
  "tiles":[1,5]},
 {"obs":280445707,"photo":503680257,"creator":"Linda Jo Conn",
  "filename":"texas-linda-jo-conn-japanese-brome-blade-collar-503680257.jpg",
  "label":"TRUE TEXAS BLADE–SHEATH JUNCTION — visible insertion, free ligule unverified",
  "role":"Actual Japanese brome leafy shoot and blade attachment from a separate Mills County Texas specimen: narrow green blade joins external sheath, fine sheath hair visible. No true inside free ligule with 1mm physical bar.",
  "caption":"The narrow blade of a source-confirmed Japanese brome specimen inserts at a sheath opening in Mills County, Texas. The green blade–sheath junction is real and clear enough to locate WHERE to search for the true membranous ligule. The little pale tissue at the opening is not confidently proved to be an intact free ligule or measured to 1–2 mm. This is an exterior collar-navigation photo, NOT a full diagnostic ligule close-up.",
  "why":"Gives the crew a second species-specific collar photo from a different Texas source observation; true inside margin remains a hold.",
  "tiles":[1,5]}
]
def get(url):
 for n in range(4):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyTexasJapaneseBromeVerifiedImageArchivist/1.0 (noncommercial CC BY educational reuse)"})
   with urllib.request.urlopen(req,timeout=50) as f:b=f.read(16500000)
   if len(b)>16000000:raise ValueError("Source response exceeds size cap")
   return b
  except urllib.error.HTTPError as ex:
   if ex.code not in (429,500,502,503,504) or n==3:raise
   time.sleep(2*(n+1))
d=json.loads(CARD.read_text());assert d.get("id")=="bromus-japonicus"
R={"date":"2026-10-27","species":SPECIES,"added":[],"held":[],"new_arrows":0,
 "not_verified":["A free 1–2.2mm inner ligule and its scale","Connected exposed annual fibrous roots","Independent vein counts for lower/upper glume pair"]}
obs_cache={}
for s in TARGETS:
 oid=s["obs"];pid=s["photo"];rec={"observation":oid,"photo":pid}
 try:
  if oid not in obs_cache:
   obs_cache[oid]=next(iter(json.loads(get(f"https://api.inaturalist.org/v1/observations/{oid}")).get("results",[])),None)
  ob=obs_cache[oid]
  if not ob or ob.get("quality_grade")!="research" or (ob.get("taxon") or {}).get("name")!=SPECIES:
   raise ValueError("Current exact taxon or grade no longer verified")
  place=ob.get("place_guess") or ""
  if not re.search(r"Texas|TX\b|Goldthwaite|Rockdale|Mills",place,re.I):
   raise ValueError("Texas photo provenance not confirmed")
  p=next((x for x in ob.get("photos",[]) if x.get("id")==pid),None)
  if p is None or (p.get("license_code") or "").lower().replace("_","-")!="cc-by":
   raise ValueError("Photo-specific license not CC BY")
  attribution=p.get("attribution") or ""
  if s["creator"].lower() not in attribution.lower():raise ValueError("Expected author source metadata mismatch")
  u=p.get("url") or ""
  original=re.sub(r"/(?:square|small|medium|thumb|large)\.(jpe?g|png)",r"/original.\1",u)
  if not original.startswith("https://") or "/original." not in original:raise ValueError("iNat image URL shape not recognized")
  src=f"https://www.inaturalist.org/photos/{pid}"
  rel="images/"+s["filename"]
  if any(x.get("file")==rel or x.get("source_page")==src for x in d["images"]):
   raise ValueError("Photo already present")
  raw=get(original)
  with Image.open(io.BytesIO(raw)) as im:im.verify()
  with Image.open(io.BytesIO(raw)) as im:
   im=ImageOps.exif_transpose(im).convert("RGB")
   if min(im.size)<650:raise ValueError("Too few pixels for source anatomy")
   im.thumbnail((2000,2000));dims=list(im.size);b=io.BytesIO();im.save(b,"JPEG",quality=90,optimize=True);clean=b.getvalue()
  dest=ROOT/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(clean)
  with Image.open(dest) as im:im.verify()
  sha=hashlib.sha256(clean).hexdigest()
  d["images"].append({"file":rel,"role":s["role"],"creator":s["creator"],"license":"CC BY",
   "license_code_exact":"cc-by","license_url":"https://creativecommons.org/licenses/by/4.0/",
   "source_page":src,"observation_url":f"https://www.inaturalist.org/observations/{oid}",
   "source_region":place,"taxon_determination":"Bromus japonicus, source research-grade observation",
   "modifications":"Source reencoded RGB JPEG, GPS and EXIF stripped, no new arrows",
   "sha256":sha,"image_dimensions":dims,"public_reuse":"Individual iNaturalist photo-level CC BY verified with creator and Texas source",
   "photo_status":"Real exact-source regional photo, excludes inference of free inner ligule or excavated roots"})
  idx=len(d["visual_comparison"]["items"])
  d["visual_comparison"]["items"].append({"label":s["label"],"scientific_name":SPECIES,
   "image_url":str(dest),"image_fit":"contain","image_role":s["role"],"caption":s["caption"],
   "why_it_matters":s["why"],"creator":s["creator"],"license":"CC BY",
   "license_url":"https://creativecommons.org/licenses/by/4.0/","source_page":src,"markers":[],
   "photo_status":"Checked exact photo license/species and original decoded pixels, visible features only; no root/ligule diagnostic certification."})
  for ti in s["tiles"]:
   a=d["field_id_short_tiles"][ti]["photo_panel_indices"]
   if idx not in a:a.append(idx)
  rec.update({"status":"archived","path":str(dest),"pixels":dims,"sha256":sha,"gallery":idx,"source":src})
 except Exception as e:rec.update({"status":"HELD","reason":str(e)})
 R["added" if rec["status"]=="archived" else "held"].append(rec)
if R["added"]:
 d["curation_status"]["photo_metadata_count"]=len(d["images"])
 d["curation_status"]["photo_files_present"]=len(d["images"])
 d["curation_status"]["visual_finish"]="FIELD_READY_PHOTO_GAPS — additional 3 regional exact-species Texas originals show grassland flowering habit and true exterior leaf-sheath/blade junction. Lower actual roots, free measured ligule and validated glume veins still missing."
 d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
 d["lane5_bromus_japonicus_texas_collar_20261027"]={"photos":R["added"],"stage":"FIELD_READY_PHOTO_GAPS",
  "features":"True Texas field habit, two distinct close external leaf/collar images. Actual measured INNER ligule not claimed.",
  "unproven":R["not_verified"],"new_unverified_arrows":0}
 CARD.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
 with LEDGER.open(newline="") as f:rd=csv.DictReader(f);cols=rd.fieldnames;rows=list(rd)
 for r in R["added"]:
  im=next(x for x in d["images"] if x["file"]==r["path"].split("content/taxa/Poaceae/Bromus/bromus-japonicus/")[1])
  fname=Path(r["path"]).name
  if any(x.get("file_name")==fname for x in rows):continue
  row=dict.fromkeys(cols,"")
  for k,v in {"file_name":fname,"role":im["role"],"creator":im["creator"],"license":"CC BY",
   "source_page":im["source_page"],"direct_url":"","study_use":"species-specific Texas grass photo education",
   "public_reuse":"Individual CC BY photo verified; creator and URL credited",
   "observation_id":str(next(x["observation"] for x in R["added"] if x["path"]==r["path"])),
   "photo_id":str(r["photo"])}.items():
   if k in row:row[k]=v
  rows.append(row)
 with LEDGER.open("w",newline="") as f:wr=csv.DictWriter(f,fieldnames=cols);wr.writeheader();wr.writerows(rows)
 R["ledger_rows"]=len(rows)
OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(R,indent=2)+"\n")
print(json.dumps(R))
