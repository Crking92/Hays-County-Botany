#!/usr/bin/env python3
"""Install only five manually screened, independently photo-licensed Texas
Hydrocotyle verticillata research-grade photo references. All exact-species IDs
remain source-derived, NOT botanically certain under conflicting var. triradiata
concept. Keep true diagnostic uncertainty, existing CC BY-SA photo and nativity
hold. No writes to other species or automated queues."""
from pathlib import Path
import csv,io,json,hashlib,requests
from PIL import Image,ImageOps
ROOT=Path(".")
P=ROOT/"content/taxa/Araliaceae/Hydrocotyle/hydrocotyle-verticillata"
CARD=P/"species.json"
SCREEN=ROOT/"workflow/photo-library/reviews/hydrocotyle-verticillata-20261020/candidate-screen.json"
REPORT=ROOT/"reports/hydrocotyle-verticillata-finished-photo-20261020.json"
PICKS=[
 ("731566770","sam-731566770-habit-with-flowers.jpg","Recognize it · low mat of peltate circular leaves plus slender flowering stalks, exact source ID research-grade; whole stalk detail may be limited."),
 ("694125616","sam-694125616-full-whorled-axis.jpg","Look closer · near-complete slender flowering/fruiting axis alongside peltate rounded leaf and hand for scale; several separated tiny whorl tiers are visible."),
 ("713985492","sam-713985492-reproductive-axis-macro.jpg","Confirm the genus clue · close flowering or young-fruit stalk with small separate tiers; organ-level determination of var. triradiata vs bonariensis requires separate review."),
 ("660004908","pufferchung-660004908-creeping-wet-patch.jpg","Recognize it · moist ground patch with separate little white clusters and round peltate blades; partial stalks do not alone prove species."),
 ("578671870","ashleyrsteel-578671870-spaced-whorls.jpg","Look closer · greenish developing whorls along short reproductive axis beside leaf blades; source accepted taxon is not independently verified from voucher.")
]
s=requests.Session()
s.headers.update({"User-Agent":"HaysCountyBotanyEducationalPhotos/1.0 (github.com/Crking92/Hays-County-Botany)"})
def fetch(x):
 pid=str(x["photo_id"]);url=x["photo_url"]
 urls=[url.replace("/large.","/original."),url,
       "https://inaturalist-open-data.s3.amazonaws.com/photos/"+pid+"/original.jpg",
       "https://inaturalist-open-data.s3.amazonaws.com/photos/"+pid+"/large.jpg"]
 for url in dict.fromkeys(urls):
  try:
   r=s.get(url,timeout=38);r.raise_for_status()
   if not 35000<len(r.content)<16000000:continue
   with Image.open(io.BytesIO(r.content)) as source:
    source.load();im=ImageOps.exif_transpose(source).convert("RGB")
   if min(im.size)<400:continue
   sha=hashlib.sha256(r.content).hexdigest()
   im.thumbnail((1450,1450),Image.Resampling.LANCZOS)
   buf=io.BytesIO();im.save(buf,format="JPEG",quality=89,optimize=True,progressive=True)
   data=buf.getvalue()
   with Image.open(io.BytesIO(data)) as verify:verify.verify()
   return data,sha,list(im.size),url
  except Exception as e:print("Image fetch failed",pid,url,str(e)[:170])
 raise RuntimeError("No valid source photo "+pid)
def main():
 manifest=json.loads((ROOT/"data/manifest.json").read_text())
 assert {x["id"]:x["path"] for x in manifest["species"]}.get("hydrocotyle-verticillata")==str(CARD)
 claims=json.loads((ROOT/"workflow/work-claims.json").read_text()).get("claims",[])
 for claim in claims:
  if "hydrocotyle-verticillata" in (claim.get("taxa") or []) and claim.get("status") in ("active","claimed","in_progress"):
   raise RuntimeError("Conflicting species claim")
 card=json.loads(CARD.read_text())
 assert card["id"]=="hydrocotyle-verticillata" and card["scientific_name"]=="Hydrocotyle verticillata"
 if all(any(img["file"]=="images/"+fn for img in card["images"]) for _,fn,_ in PICKS):
  print("All photo entries already installed: no-op");return
 assert len(card["images"])==1 and card["images"][0]["file"]=="images/hydrocotyle-verticillata-ton-rulkens-leaves.jpg"
 assert card["project_inclusion"]["target_zone_status"]=="UNRESOLVED"
 assert card["curation_status"]["finished_field_id_pass"]=="PASS_IN_PROGRESS"
 report=json.loads(SCREEN.read_text());assert report["target"]=="Hydrocotyle verticillata Thunb."
 candidates={str(x["photo_id"]):x for x in report["candidates"]}
 prepared=[]
 for pid,fn,role in PICKS:
  photo=candidates[pid]
  assert photo["taxon"]=="Hydrocotyle verticillata" and photo["quality_grade"]=="research"
  assert photo["photo_license"] in ("cc-by","cc0","cc-by-sa") and photo.get("preview_sha256")
  assert not (P/"images"/fn).exists()
  prepared.append((pid,fn,role,photo,*fetch(photo)))
 for pid,fn,role,photo,data,sha,dims,url in prepared:
  p=P/"images"/fn;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
  code=photo["photo_license"]
  lic={"cc-by":"CC BY","cc-by-sa":"CC BY-SA","cc0":"CC0"}[code]
  record={"file":"images/"+fn,"role":role,
   "creator":photo["photo_attribution"] or photo["observer"],
   "license":lic,
   "license_version_note":"Individual source iNaturalist photo license_code="+code+" verified 2026-10-20; exact version was not independently confirmed from photo's media rights page.",
   "source_platform":"iNaturalist Texas research-grade exact-name source",
   "source_page":photo["photo_source"],"source_observation_page":photo["identification_source"],"source_photo_id":pid,
   "downloaded_from":url,"image_dimensions":dims,"original_image_sha256":sha,
   "study_use":"Attributed botanical education subject to exact photo license",
   "public_reuse":"Photo-specific CC license permits attributed public reuse with appropriate modification notice and ShareAlike if applicable",
   "modifications":"Downscaled, JPEG reencoded, EXIF removed; no arrows added without source-specific final pixel verification",
   "anatomy_arrows":"none, full-size organ-specific arrow pass still pending",
   "photo_review":"Visually screened real contact sheet of Texas research-grade Hydrocotyle verticillata label. Potential H. bonariensis / var. triradiata taxonomic overlap not resolved; do not treat source name as verified expert voucher."
  }
  card["images"].append(record)
 card["curation_status"].update({
  "photo_metadata_count":len(card["images"]),"photo_files_present":len(card["images"]),
  "photo_source_checked":True,"visual_reviewed":False,"finished_field_id_pass":"PASS_IN_PROGRESS",
  "manual_diagnostic_photo_additions":"2026-10-20",
  "required_to_finish":[
   "Inspect full-size installed spaced-tier photo(s) and annotate only verified flower/fruit whorls and peltate leaf vein hub",
   "Independent reproductive voucher comparison of H. verticillata sensu POWO versus H. bonariensis / older var. triradiata labels",
   "Show real leaf underside petiole insertion and mature ribbed 2-mericarp with mm reference",
   "BONAP native metrics exclusion remains unchanged pending county determination"
  ]})
 card["learner_visual_status"].update({
  "image_count":len(card["images"]),
  "mode":"species_detailed_text_six_real_photos_taxonomy_warning_reproductive_QA_pending",
  "note":"Six individual sources physically present, one prior Wikimedia CC BY-SA 2.0 + five Texas photo-licensed iNat research-grade. Flower and fruit whorls visually available, original accepted-taxon identification is not voucher-proven; anatomy labels pending full JPEG review."
 })
 card["photo_note"]="2026-10-20: Five additional original exact-name, photo-licensed Texas iNaturalist research-grade pictures installed after visual contact sheet. Prior Ton Rulkens CC BY-SA 2.0 picture retained. Photos represent habit, separated tiers and flower/fruit stages, but Kew/H. bonariensis triradiata taxonomic conflict remains explicitly unresolved; leaf and fruit ID confidence not upgraded."
 CARD.write_text(json.dumps(card,indent=2,ensure_ascii=False)+"\n")
 ledger=P/"image-sources.csv"
 with ledger.open(newline="") as f:
  reader=csv.DictReader(f);headers=reader.fieldnames;rows=list(reader)
 for pid,fn,role,photo,data,sha,dims,url in prepared:
  row={k:"" for k in headers}
  values={"file_name":fn,"role":role,"creator":photo["photo_attribution"] or photo["observer"],
   "license":{"cc-by":"CC BY","cc-by-sa":"CC BY-SA","cc0":"CC0"}[photo["photo_license"]],
   "source_page":photo["photo_source"],"direct_url":url,
   "study_use":"Attributed botanical education",
   "public_reuse":"Source individual public CC license; credit and alteration notice"}
  for k,v in values.items():
   if k in row:row[k]=v
  rows.append(row)
 with ledger.open("w",newline="") as f:
  writer=csv.DictWriter(f,fieldnames=headers,lineterminator="\n")
  writer.writeheader();writer.writerows(rows)
 result={"taxon":"Hydrocotyle verticillata","prior_photos":1,"new_photos":len(prepared),
  "total_photos":len(card["images"]),
  "new_files":[fn for pid,fn,*_ in prepared],
  "taxonomic_warning":"H. verticillata var. triradiata is Kew synonym of H. bonariensis; no photo accepted as reproductive voucher.",
  "source_photo_licensing":"iNaturalist individual photo license codes; exact versions for added images not independently confirmed",
  "original_preserved":True,"county_nativity_hold_preserved":True,
  "site_published":False}
 REPORT.write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps(result,indent=2))
if __name__=="__main__":main()
