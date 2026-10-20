#!/usr/bin/env python3
"""One-off user-requested Hydrocotyle bonariensis learner installation.
Adds canonical card to manifest only after six real exact-species source-photo
CC-licensed JPEG bytes are downloaded and verified. Keeps BONAP county native
HOLD and the POWO triradiata/verticillata mismatch explicit. Not a scheduled worker.
"""
import csv, io, json, hashlib
from pathlib import Path
import requests
from PIL import Image,ImageOps
ROOT=Path(".")
DIR=ROOT/"content/taxa/Araliaceae/Hydrocotyle/hydrocotyle-bonariensis"
CARD=DIR/"species.json"
LEDGER=DIR/"image-sources.csv"
GENUS=ROOT/"content/taxa/Araliaceae/Hydrocotyle/genus.json"
MANIFEST=ROOT/"data/manifest.json"
SCREEN=ROOT/"workflow/photo-library/reviews/hydrocotyle-bonariensis-20261020/photo-screen.json"
REPORT=ROOT/"reports/hydrocotyle-bonariensis-photo-install-20261020.json"
# Real source previews of the individual photos examined by the reviewer before selection.
PICKS=[
 ("688462223","sunasak-688462223-low-mat.jpg",
  "Recognize it — damp-ground/grass mat of circular peltate leaves and young flower clusters; exact Texas source research-grade, rhizome nodes not visible."),
 ("666145212","williamkjones-666145212-primary-umbel-rays.jpg",
  "Look closer — near face-on primary COMPOUND-UMBBEL ray branching with crowded separate outer flowering groups; source-identified H. bonariensis, central node and rays visible. Full distal ray axis may be partially obstructed."),
 ("590221868","sam-590221868-compound-axis-hand-scale.jpg",
  "Confirm the comparison clue — hand-held stalk showing primary rays at a branchpoint with several separate secondary floral groups on fine distal stalks; complete secondary axis needs separate review."),
 ("517271319","andyjordan-517271319-flower-5-petal-macro.jpg",
  "Look closer — actual tiny cream five-petaled flowers with five stamens among green developing flowers/fruits; complete main branch architecture not in frame."),
 ("479454106","sandy-loam22-479454106-leaf-underside-petiole.jpg",
  "Look closer — angled underside and attachment region of a peltate leaf beside sand; the petiole/underside view is helpful, but exact penetration point still requires second-angle verification."),
 ("479454142","sandy-loam22-479454142-fruit-cluster.jpg",
  "Look closer — small pale flowers and developing ribbed green mericarp-like bodies within one branch; no measured ripe 2-mericarps or millimeter ruler in this frame."),
]
S=requests.Session()
S.headers.update({"User-Agent":"HaysBotanyPublicPhotoLicenseInstaller/1.0 (github.com/Crking92/Hays-County-Botany)"})
def fetch_photo(row):
 pid=str(row["photo_id"])
 url=row["photo_url"]
 urls=[url.replace("/large.","/original."),url,
       "https://inaturalist-open-data.s3.amazonaws.com/photos/"+pid+"/original.jpg",
       "https://inaturalist-open-data.s3.amazonaws.com/photos/"+pid+"/large.jpg"]
 for url in dict.fromkeys(urls):
  try:
   r=S.get(url,timeout=45);r.raise_for_status()
   if not 35000<len(r.content)<16000000:continue
   with Image.open(io.BytesIO(r.content)) as original:
    original.load();im=ImageOps.exif_transpose(original).convert("RGB")
   if min(im.size)<460:continue
   sha=hashlib.sha256(r.content).hexdigest()
   im.thumbnail((1450,1450),Image.Resampling.LANCZOS)
   buf=io.BytesIO();im.save(buf,format="JPEG",quality=90,optimize=True,progressive=True)
   payload=buf.getvalue()
   with Image.open(io.BytesIO(payload)) as verify:verify.verify()
   if len(payload)<26000:continue
   return payload,sha,list(im.size),url
  except Exception as exc:print("media fetch failed",pid,url,str(exc)[:150])
 raise RuntimeError("No valid full source for photo "+pid)
def main():
 manifest=json.loads(MANIFEST.read_text())
 species=manifest["species"]
 assert not any(x["id"]=="hydrocotyle-bonariensis" for x in species),"Species already in manifest; refuse duplicate installation"
 claims=json.loads((ROOT/"workflow/work-claims.json").read_text()).get("claims",[])
 assert not any("hydrocotyle-bonariensis" in (x.get("taxa") or []) and x.get("status") in ("active","claimed","in_progress") for x in claims),"Active claim"
 card=json.loads(CARD.read_text())
 assert card["id"]=="hydrocotyle-bonariensis" and card["scientific_name"]=="Hydrocotyle bonariensis" and len(card["images"])==0
 assert card["project_inclusion"]["target_zone_status"]=="UNRESOLVED" and card["project_inclusion"]["native_metrics_excluded"] is True
 screen=json.loads(SCREEN.read_text())
 assert screen["taxon"]=="Hydrocotyle bonariensis"
 by_id={str(x["photo_id"]):x for x in screen["candidates"]}
 assert len(PICKS)>=5
 prepared=[]
 for pid,fn,role in PICKS:
  info=by_id[pid]
  assert info["taxon"]=="Hydrocotyle bonariensis" and info["grade"]=="research"
  assert info["photo_license_code"] in ("cc-by","cc0","cc-by-sa")
  assert info.get("preview_sha256")
  assert not (DIR/"images"/fn).exists()
  prepared.append((pid,fn,role,info,*fetch_photo(info)))
 for pid,fn,role,info,payload,sha,dims,url in prepared:
  output=DIR/"images"/fn;output.parent.mkdir(parents=True,exist_ok=True);output.write_bytes(payload)
  lic={"cc-by":"CC BY","cc-by-sa":"CC BY-SA","cc0":"CC0"}[info["photo_license_code"]]
  card["images"].append({
   "file":"images/"+fn,"role":role,
   "creator":info["photo_attribution"] or info["user"],"license":lic,
   "license_version_note":"Individual iNaturalist photo object license_code="+info["photo_license_code"]+" checked 2026-10-20; specific version is not independently established by the returned code.",
   "source_platform":"iNaturalist individual photo (Texas, research-grade identification)",
   "source_page":info["photo_source_page"],"source_observation_page":info["observation_page"],
   "source_photo_id":pid,"downloaded_from":url,"source_sha256":sha,"image_dimensions":dims,
   "study_use":"Public attributed botanical education under individual Creative Commons source license",
   "public_reuse":"Photo-specific CC license permits use with credit and modification disclosure, ShareAlike when required.",
   "modifications":"Original JPEG resized/reencoded to max 1450 pixels and stripped of EXIF; no anatomical arrows before full-size final pixel review.",
   "anatomy_arrows":"none — anatomy source-image review precedes arrows",
   "photo_review":"Photo was visually screened from actual candidate contact sheet; exact source taxon research-grade but botanical branch diagnosis/voucher not independently confirmed. The whole photographed plant's accepted name may require further scrutiny under triradiata conflict."
  })
 card["curation_status"].update({
 "photo_metadata_count":len(card["images"]),"photo_files_present":len(card["images"]),"photo_source_checked":True,
 "visual_reviewed":False,"finished_field_id_pass":"PASS_IN_PROGRESS",
 "field_training_status":"READY_FOR_THREE_WAY_COMPARISON_PROVISIONAL_TAXONOMIC_REVIEW",
 "photo_install":"2026-10-20",
 "required_to_finish":[
  "Open actual installed full-size source JPEGs and check branchpoint/secondary rays; add carefully placed arrows only where structures visible",
  "Scientific voucher/taxon concept review under H. verticillata var. triradiata vs bonariensis accepted Kew synonym",
  "BONAP/NAPA county-target review remains UNRESOLVED and native metrics excluded",
  "Mature fruit cross-section/ribs with mm scale and unambiguous peltate underside if available"
 ]
 })
 card["learner_visual_status"].update({
  "status":"provisional_learner_ready","image_count":len(card["images"]),
  "mode":"six_source_photo_comparison_lesson_anatomy_taxon_hold",
  "note":"Six physically installed, credited individual-CC-license photos selected for whole habit, primary rays, flower, developing fruit and underside candidate. Flower branching and source determination remain provisional until expert and pixel review."
 })
 card["photo_note"]="2026-10-20 new manual user-requested comparison learner card installed with six photo-specific CC licensed TX research-grade images. All physically validated, copyright credits retained. Some show branch rays and small flowers; taxon concept vs older var. triradiata remains a scientific HOLD. Hays County native status NOT approved."
 CARD.write_text(json.dumps(card,indent=2,ensure_ascii=False)+"\n")
 # Append near the existing Hydrocotyle genus entries, keep manifest order stable.
 entry={"id":"hydrocotyle-bonariensis","path":str(CARD)}
 genus_i=next(i for i,x in enumerate(species) if x["id"]=="hydrocotyle-umbellata")
 species.insert(genus_i,entry)
 MANIFEST.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n")
 genus=json.loads(GENUS.read_text())
 assert genus["name"]=="Hydrocotyle"
 genus["species"]=sorted(set(genus["species"]+["Hydrocotyle bonariensis"]))
 genus["look_here_first"]="Flip round leaf to test peltate petiole attachment, then photograph the WHOLE reproductive axis: H. umbellata crowded terminal cluster; H. verticillata small spaced whorls on main axis; H. bonariensis main umbel rays split into secondary axes each with its own whorls. Old H. verticillata var. triradiata = H. bonariensis at Kew, verify voucher before species approval."
 genus["three_species_field_key_20261020"]=[
  {"species":"Hydrocotyle umbellata","photo_key":"One dense crowded terminal flower group; whole stalk normally simple"},
  {"species":"Hydrocotyle verticillata","photo_key":"Several small interrupted whorls along main flower axis; can rarely branch; taxon concept caution"},
  {"species":"Hydrocotyle bonariensis","photo_key":"COMPOUND umbel, with distinct primary rays each capable of carrying secondary whorls along their length; source-labeled reference images require voucher review"}
 ]
 genus["training_photo_three_way"]={
 "umbellata":{"species_id":"hydrocotyle-umbellata","image_index":3,"visible":"crowded flowering umbel; check original photo pixels"},
 "verticillata":{"species_id":"hydrocotyle-verticillata","image_index":2,"visible":"two manually arrowed, separated upper and lower flowering tiers, iNaturalist research-grade source identification"},
 "bonariensis":{"species_id":"hydrocotyle-bonariensis","image_index":1,"visible":"near-terminal branched primary umbel rays and clusters; exact compound distal axis pending fully confirmed source pixel review"},
 "caution":"Three-way comparison is a field observation teaching key, NOT a genus taxonomic revision, BONAP range approval, or accepted-voucher determination."
 }
 genus["curation_status"]["bonariensis_comparison_added"]="2026-10-20 manual requested; provisional taxon and county HOLD"
 GENUS.write_text(json.dumps(genus,indent=2,ensure_ascii=False)+"\n")
 with LEDGER.open("w",newline="") as f:
  head=["file_name","role","creator","license","source_page","direct_url","study_use","public_reuse"]
  w=csv.DictWriter(f,fieldnames=head,lineterminator="\n");w.writeheader()
  for pid,fn,role,info,payload,sha,dims,url in prepared:
   w.writerow({"file_name":fn,"role":role,"creator":info["photo_attribution"] or info["user"],
   "license":{"cc-by":"CC BY","cc-by-sa":"CC BY-SA","cc0":"CC0"}[info["photo_license_code"]],
   "source_page":info["photo_source_page"],"direct_url":url,"study_use":"Public educational",
   "public_reuse":"Individual CC photo permission, credit original creator"})
 REPORT.write_text(json.dumps({
  "species":"Hydrocotyle bonariensis","new_learner_species":True,"prior_photos":0,
  "installed_photos":len(prepared),"manifest_path":str(CARD),
  "photos":[{"id":pid,"file":fn,"sha256":sha} for pid,fn,_,_,_,sha,_,_ in prepared],
  "taxonomy":"Kew accepted H. bonariensis incl historical H. verticillata var. triradiata synonym; modern voucher comparison still unresolved",
  "county_nativity_status":"UNRESOLVED, no native metrics","public_site_published":False
 },indent=2)+"\n")
 print("VERIFIED user-requested new species",len(prepared),"photo files, manifest and genus.")
if __name__=="__main__":main()
