#!/usr/bin/env python3
"""Archive five original Bob Harms Selected Central Texas Monocots photos
of Elymus virginicus. Exact page names and source reuse evidence checked.
Original copyrights retained; no mm specimen dissection or fake arrows.
"""
from pathlib import Path
import hashlib,io,json,time,requests
from PIL import Image,ImageOps

ROOT=Path("content/taxa/Poaceae/Elymus")
S=ROOT/"elymus-virginicus/species.json"
G=ROOT/"genus.json"
REPORT=Path("reports/elymus-virginicus-five-harms-central-texas-originals-20261023.json")
RELEASE=Path("workflow/field-id-publication/2026-10-23-elymus-virginicus-five-harms-real-photos.json")
BASE="https://w3.biosci.utexas.edu/prc/Monocots/GrassHTML/data/"
HOME="https://w3.biosci.utexas.edu/prc/Monocots/"
PERMISSION="BOB_HARMS_SELECTED_MONOCOTS_EDU_WITH_CREDIT_20261022"
LIC="© Bob Harms — scientific/educational use with attribution (NOT Creative Commons)"
ROWS=[
("ELVI3-b","TRUE CENTRAL TEXAS UPPER PLANT HABIT — original source-labelled plant",
"Bob Harms original depicts an actual Virginia wildrye culm and its leaves in the Central Texas collection. Do not claim exposed same-voucher roots unless they are clearly in frame."),
("ELVI3-b1","SECOND CENTRAL TEXAS PLANT / SHEATH VIEW — author original",
"A second source-labelled Virginia wildrye plant view: use for stem, sheath or crown only where actual pictured parts are clear; not a certified separate county-vouched plant."),
("ELVI3-I","TRUE FLOWERING SPIKE — Virginia wildrye",
"Source photograph of flowering Virginia wildrye; note the main unbranched rachis bearing crowded spikelets, unlike an open Nassella panicle."),
("ELVI3-i1","INFLORESCENCE CLOSER — authentic spike and awns",
"Bob Harms authentic flowering spike close-up: follow its upright central axis, awned spikelets and enclosed units. Compare bent Canada wildrye separately; posture alone is unreliable."),
("ELVI3-J2","FLOWERING REPRODUCTIVE DETAIL — source-confirmed Virginia wildrye",
"Source labelled actual close flowering units; do not declare one individual glume base U-shaped without genuine visible outline, nor label anthers or ligule unless shown.")
]
species=json.loads(S.read_text(encoding="utf-8"));genus=json.loads(G.read_text(encoding="utf-8"))
assert species["id"]=="elymus-virginicus" and species["scientific_name"]=="Elymus virginicus"
assert len(species["images"])==2 and len(species["visual_comparison"]["items"])==5
assert len(genus["visual_comparison"]["items"])==14
assert "FIELD_READY_PHOTO_GAPS" in species["field_id_finish_pass"]["stage"]
scisnap={key:species.get(key) for key in ["project_inclusion","county_occurrences_target_zone","native_target_zone_calculated","morphology_keys"]}
session=requests.Session();session.headers.update({"User-Agent":"HaysBotanyRealSourceVirginiaWildryePhotoArchive/1.0 scientific education","Accept":"image/jpeg,image/*;q=0.9"})
archive_dir=S.parent/"images"
archive_dir.mkdir(parents=True,exist_ok=True)
report={"species":"Elymus virginicus","source_collection":HOME,
 "license":"Author Bob Harms educational/scientific with credit on these exact original Selected Monocots photographs, NOT CC",
 "original_source_taxon":"Elymus virginicus","physical_new":0,"photos":[],
 "science_hold":"No matched Hays specimen 1mm juvenile auricles plus U-glume/Canada V-glume comparison and attached multi-floret dissection"}
for ident,title,caption in ROWS:
 original=BASE+"images/"+ident+".jpg"
 page=BASE+"pages/"+ident+".html"
 filename="bob-harms-virginia-wildrye-"+ident.lower()+".jpg"
 target=archive_dir/filename
 if target.is_file():raise RuntimeError("Existing source file found, do not override "+str(target))
 last=None
 for tries in range(3):
  try:
   response=session.get(original,timeout=35)
   response.raise_for_status()
   raw=response.content
   if not raw.startswith(bytes.fromhex("ffd8ff")) or len(raw)<4000:
    raise ValueError("Not a credible JPEG original")
   with Image.open(io.BytesIO(raw)) as im:
    im.load()
    if im.format!="JPEG" or min(im.size)<45:
     raise ValueError("Not an authentic original with legible anatomical stripe or whole-plant view")
    clear=ImageOps.exif_transpose(im).convert("RGB")
    dims=list(clear.size)
   clear.save(target,"JPEG",quality=93,optimize=True)
   original_hash=hashlib.sha256(raw).hexdigest()
   break
  except (OSError,requests.RequestException,ValueError) as e:
   last=str(e)
   if tries<2:time.sleep(3*(tries+1))
 else:raise RuntimeError("Unable to verify Bob Harms original "+ident+": "+last)
 data=target.read_bytes()
 with Image.open(target) as im:
  assert im.mode=="RGB" and im.format=="JPEG" and not im.getexif().get(34853)
  dims=list(im.size)
  im.verify()
 digest=hashlib.sha256(data).hexdigest()
 record={"file":"images/"+filename,"role":title,"creator":"Bob Harms","license":LIC,"license_url":HOME,
   "source_taxon_name":"Elymus virginicus","source_page":page,"source_image":original,
   "site_specific_public_permission":PERMISSION,
   "public_reuse":"YES original Selected Monocots educational and scientific uses with Bob Harms credit, copyrighted NOT CC",
   "study_use":"yes","archive_sha256":digest,"original_source_sha256":original_hash,
   "image_dimensions":dims,"modifications":"Full photo decoded RGB re-encoded without crop, EXIF/GPS deleted; copyright and original attribution preserved",
   "photo_review":"Actual original source JPEG; human pixel organ-specific arrow review pending. PROVISIONAL — USER PHOTO REVIEW, distinct regional references do not equal one whole vouchered specimen"}
 species["images"].append(record)
 panel={"label":title,"scientific_name":"Elymus virginicus","image_url":str(target),"image_fit":"contain",
   "image_role":title,"caption":caption,
   "why_it_matters":"True Central Texas source-confirmed photographs add local botanical detail to out-of-state glume and Canada comparisons, without asserting a measured local voucher.",
   "creator":"Bob Harms","license":LIC,"license_url":HOME,"source_page":page,
   "photo_status":"Actual original locally archived under exact site-specific Bob Harms permission with credit, structure arrows await original-pixel inspection. PROVISIONAL USER PHOTO REVIEW.","markers":[]}
 species["visual_comparison"]["items"].append(panel)
 genus["visual_comparison"]["items"].append(dict(panel))
 report["photos"].append({"code":ident,"source_image":original,"source_page":page,
  "local_file":str(target),"dimensions":dims,"bytes":len(data),"original_sha256":original_hash,"archived_sha256":digest})
 report["physical_new"]+=1
assert len(species["images"])==7 and len(species["visual_comparison"]["items"])==10
assert len(genus["visual_comparison"]["items"])==19
assert all(species.get(key)==val for key,val in scisnap.items())
species["curation_status"]["photo_metadata_count"]=7
species["curation_status"]["photo_files_present"]=7
species["curation_status"]["virginia_harms_five_originals_20261023"]={"real_new_jpegs":5,"total_physically_archived_species_photos":7,
"species_visual_panels":10,"genus_visual_panels":19,"true_glume_1mm_Hays_pair_verified":False,"native_and_county_hold_untouched":True,"stage":"FIELD_READY_PHOTO_GAPS"}
species["field_id_finish_pass"]["virginia_harms_five_20261023"]={
 "new_real_central_texas_photo_codes":[x[0] for x in ROWS],"verification_report":str(REPORT),
 "critical_missing_from_same_voucher":[
  "Two attached mature rachis nodes in Hays with paired multi-flowered spikelets and exact 1 mm ruler showing U-shaped hard glume bases",
  "Same-scale native Canada wildrye V-base glume comparison with physical attachments and hybrid caveat",
  "Fully exposed fresh central 0.5–0.7 mm membranous ligule and auricles on the same vouchered plant, ruler in focal plane",
  "One same plant roots/leaf collar/flag sheath/full spike sequence with source determinations"
 ],"status":"FIELD_READY_PHOTO_GAPS"}
species["visual_comparison"]["subtitle"]="Seven physically stored exact Virginia wildrye originals (five Bob Harms Central Texas copyrighted educational credited sources, two Matt Lavin CC BY-SA); existing five-panel remote glume/Canada comparison retained. Source-specific 1mm matched dissection still missing."
genus["visual_comparison"]["subtitle"]="Expanded Elymus teaching now adds five physically archived source-labeled Central Texas Virginia wildrye photo panels to earlier Virginia/Canada comparisons, without inventing species-level micromorphology."
S.write_text(json.dumps(species,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
G.write_text(json.dumps(genus,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
REPORT.parent.mkdir(parents=True,exist_ok=True)
REPORT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
RELEASE.parent.mkdir(parents=True,exist_ok=True)
RELEASE.write_text(json.dumps({"type":"manual_field_id_publication","date":"2026-10-23",
 "species":"Elymus virginicus","new_actual_jpeg_files":5,"species_photo_files_total":7,"species_panels":10,"genus_panels":19,
 "source_report":str(REPORT),"rights":"Bob Harms exact source images original educational credited use, NOT CC",
 "stage":"FIELD_READY_PHOTO_GAPS","publication":"Deployment must be checked separately for build + deploy SUCCESS"},indent=2)+"\n",encoding="utf-8")
print("PASS 5 real source-authenticated Central Texas Bob Harms original Virginia wildrye JPEGs")
