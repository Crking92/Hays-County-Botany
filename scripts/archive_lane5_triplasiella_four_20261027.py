#!/usr/bin/env python3
"""Lane5 Triplasiella eragrostoides photo archive. FOUR source-authenticated,
research-grade Central Texas photos: live green flowering head; dark mature
spikelets; true exterior blade/sheath junction; in-ground flowering context.
All from the EXACT current iNaturalist accepted taxon. Per-PHOTO CC BY gate.
No 1-mm ligule, 3-veined lemma or true root-crown arrow asserted.
"""
import csv,hashlib,io,json,pathlib,re,time,urllib.request,urllib.error
from PIL import Image,ImageOps
ROOT=pathlib.Path("content/taxa/Poaceae/Triplasiella/triplasiella-eragrostoides")
CARD=ROOT/"species.json";LEDGER=ROOT/"image-sources.csv"
OUT=pathlib.Path("reports/lane5-triplasiella-central-texas-four-20261027.json")
SPECIES="Triplasiella eragrostoides"
CANDIDATES=[
 {"obs":87425978,"id":144138787,
 "role":"True source-labelled fresh green flowering section; several open radiating panicle branches, attached small green spikelets and long thin culm. Not rooted or measured.",
 "label":"TEXAS GREEN FLOWERING HEAD — true branching and attached spikelets",
 "caption":"Real source-identified lovegrass tridens from Bexar County. Follow the thin panicle stem into its widely separated branches and several small green attached spikelets. Other grasses are present behind it. The fingers provide context, not a 1-mm scale or a microscopic lemma identification.",
 "why":"Adds fresh flowering architecture distinct from the old pale distant head and red dry head.","tiles":[0]},
 {"obs":102378815,"id":171120591,
 "role":"Source-labelled tight macro of mature reddish purple-brown compressed multiple individual spikelets on fine panicle branch in Texas. Internal 3-veined lemma/central midnerve origin not visible.",
 "label":"MATURE PURPLE-BROWN SPIKELETS — actual reproductive close view",
 "caption":"The source-labeled Texas target branch bears small dark burgundy compressed spikelets seen at closer range against a finger. The outlines and mature color are visible, but do not mistake the finger for a millimeter ruler or invent the species' 3-veined ~2–3-mm lemma and its central mucro from this undissected view.",
 "why":"Shows the smaller dark mature units with far less distracting background than the existing Cleveland Powell photo.","tiles":[0,2,5]},
 {"obs":156610866,"id":270915491,
 "role":"Actual external junction where a green linear leaf blade departs its enclosing green sheath on a source-identified Texas plant; inner membrane free edge and tiny 1–3mm ligule margin not exposed or measured.",
 "label":"REAL LEAF–SHEATH JUNCTION — outer blade and sheath; inner ligule still hidden",
 "caption":"A live Triplasiella shoot photographed in Bexar County shows a green blade emerging beside an encircling external sheath. The INNER free 1–3-mm membranous, possibly lacerate ligule is NOT pulled open or measured in this image. Do not arrow the exterior sheath rim as the diagnostic ligule.",
 "why":"Finally connects the published collar anatomy lesson to a real target-species leaf, without overclaiming ligule evidence.","tiles":[3,4]},
 {"obs":156610866,"id":270915506,
 "role":"In-situ lower leafy flowering shoots among other ground vegetation and shallow soil in Bexar County, source-identified as Triplasiella; roots and connected long-lived crown obscured.",
 "label":"REAL TEXAS HABITAT — narrow upright leafy shoots in ground vegetation",
 "caption":"Source-identified lovegrass tridens growing among a mixed native grass/forb community in Bexar County. The photo shows slender flowering shoots and leafy ground vicinity, but nearby plants may be OTHER species. It does not show attached exposed roots, the perennial crown, or genuine rhizomes; the Texas literature conflicts on rhizomatous bases.",
 "why":"Provides field-growing context absent from earlier handheld isolated seedhead photos; species identification applies to source focal plant, not surrounding weeds.","tiles":[0,4]}
]
def get(url):
 for a in range(4):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotanyIndividualLicensePhotoArchive/1.0 (educational field guide)"})
   with urllib.request.urlopen(req,timeout=47) as f:data=f.read(17500000)
   if len(data)>=17500000:raise ValueError("Response >17.5MB")
   return data
  except urllib.error.HTTPError as exc:
   if exc.code not in (429,500,502,503,504) or a==3:raise
   time.sleep(2*(a+1))
data=json.loads(CARD.read_text());assert data["id"]=="triplasiella-eragrostoides"
REPORT={"taxon":SPECIES,"date":"2026-10-27","source_verified":[],"holds":[],"new_arrows":0,
 "missing_real_anatomy":["1-3mm face-on lacerate free ligule with ruler","Same-voucher basal rooted perennial crown and rootstock morphology","Isolated mature 2-3mm 3-veined lemma with one centrally produced mucro","Calibrated basal glumes/palea paired with same voucher"],
 "source_category":"Open-licensed iNaturalist exact accepted species from Bexar/Texas; no other-species labels"}
OBS={};new=[]
for c in CANDIDATES:
 oid,pid=c["obs"],c["id"];rec={"observation":oid,"photo":pid}
 try:
  if oid not in OBS:
   obs=json.loads(get(f"https://api.inaturalist.org/v1/observations/{oid}"))
   OBS[oid]=next(iter(obs.get("results",[])),None)
  ob=OBS[oid]
  if not ob or (ob.get("taxon") or {}).get("name")!=SPECIES or ob.get("quality_grade")!="research":
   raise ValueError("Source species/research-grade gate failed")
  region=ob.get("place_guess") or ""
  if not re.search(r"Texas|TX\b|Bexar",region,re.I):raise ValueError("Source not explicitly in Texas")
  p=next((x for x in ob.get("photos",[]) if x.get("id")==pid),None)
  if not p or (p.get("license_code") or "").lower().replace("_","-")!="cc-by":
   raise ValueError("Individual source image missing or not CC BY")
  credit=p.get("attribution") or ""
  if "Cleveland Powell" not in credit:raise ValueError("Source individual creator mismatch")
  url=p.get("url") or ""
  orig=re.sub(r"/(?:square|small|medium|thumb|large)\.(jpe?g|png)",r"/original.\1",url)
  if orig==url or not orig.startswith("https://"):raise ValueError("Unexpected original image URL")
  source=f"https://www.inaturalist.org/photos/{pid}"
  rel=f"images/tx-triplasiella-{pid}.jpg"
  if any(z.get("file")==rel or z.get("source_page")==source for z in data["images"]):
   raise ValueError("Photo already archived, skip duplicate")
  raw=get(orig)
  with Image.open(io.BytesIO(raw)) as im:im.verify()
  with Image.open(io.BytesIO(raw)) as im:
   im=ImageOps.exif_transpose(im).convert("RGB")
   if min(im.size)<700:raise ValueError("Real source resolution insufficient")
   im.thumbnail((2000,2000));dims=list(im.size)
   b=io.BytesIO();im.save(b,"JPEG",quality=90,optimize=True);jpeg=b.getvalue()
  dest=ROOT/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(jpeg)
  with Image.open(dest) as im:im.verify()
  sha=hashlib.sha256(jpeg).hexdigest()
  data["images"].append({"file":rel,"role":c["role"],"creator":"Cleveland Powell","license":"CC BY 4.0",
     "license_code_exact":"cc-by","license_url":"https://creativecommons.org/licenses/by/4.0/",
     "source_page":source,"observation_url":f"https://www.inaturalist.org/observations/{oid}",
     "observation_id":str(oid),"photo_id":str(pid),"source_region":region,
     "source_taxon":SPECIES,"source_quality_grade":"research at archive time",
     "modifications":"Original reencoded RGB JPEG, EXIF/GPS removed; 0 new anatomical arrows",
     "sha256":sha,"pixels":dims,
     "public_reuse":"Individual CC BY image, exact taxonomy and author verified with source API at archive",
     "photo_status":"Real verified source photo. Only directly visible coarse roles documented; no microscopic anatomy proven."})
  idx=len(data["visual_comparison"]["items"])
  data["visual_comparison"]["items"].append({"label":c["label"],"scientific_name":SPECIES,
     "image_url":str(dest),"image_fit":"contain","image_role":c["role"],
     "caption":c["caption"],"why_it_matters":c["why"],
     "creator":"Cleveland Powell","license":"CC BY 4.0",
     "license_url":"https://creativecommons.org/licenses/by/4.0/",
     "source_page":source,"markers":[],
     "photo_status":"Source image and matching taxon visually reviewed at gross scale; license and JPEG validated; no 1mm data or inferred arrows"})
  for tile_index in c["tiles"]:
   if idx not in data["field_id_short_tiles"][tile_index]["photo_panel_indices"]:
    data["field_id_short_tiles"][tile_index]["photo_panel_indices"].append(idx)
  rec.update({"status":"archived","file":str(dest),"pixel_dimensions":dims,"sha256":sha,"gallery_panel":idx,"license":"CC BY 4.0"})
  new.append((dest.name,c["role"],source,orig,str(oid),str(pid)))
 except Exception as e:rec.update({"status":"HELD","reason":str(e)})
 REPORT["source_verified" if rec["status"]=="archived" else "holds"].append(rec)
if REPORT["source_verified"]:
 data["curation_status"]["photo_metadata_count"]=len(data["images"])
 data["curation_status"]["photo_files_present"]=len(data["images"])
 data["curation_status"]["visual_finish"]="FIELD_READY_PHOTO_GAPS — six actual licensed species photos including two earlier panicles plus new green flowerhead, dark spikelet macro, leaf-sheath EXTERIOR and Texas live-growing vicinity. Still missing actual inner measured ligule, exposed crown/rootstock and 3-veined midnerve-mucronate lemma dissection."
 data["learner_visual_status"]["image_count"]=len(data["images"])
 data["lane5_triplasiella_texas_four_20261027"]={
   "new_images":REPORT["source_verified"],"status":"FIELD_READY_PHOTO_GAPS",
   "unresolved":REPORT["missing_real_anatomy"],"new_arrows":0}
 CARD.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
 if LEDGER.exists():
  with LEDGER.open(newline="") as f:reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
  names={r["file_name"] for r in rows}
  for name,role,source,orig,oid,pid in new:
   if name in names:continue
   row=dict.fromkeys(fields,"")
   for col,value in {"file_name":name,"role":role,"creator":"Cleveland Powell","license":"CC BY 4.0",
     "license_url":"https://creativecommons.org/licenses/by/4.0/","source_page":source,
     "direct_url":orig,"observation_id":oid,"photo_id":pid,"study_use":"yes, with credits",
     "public_reuse":"yes, source-verified per-photo CC BY",
     "modifications":"JPEG re-encoded, EXIF and GPS removed, no marker overlays added"}.items():
    if col in row:row[col]=value
   rows.append(row)
  with LEDGER.open("w",newline="") as f:writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(REPORT,indent=2)+"\n")
print(json.dumps(REPORT))
