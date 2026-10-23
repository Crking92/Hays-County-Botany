#!/usr/bin/env python3
"""Archive two REAL exact-source Matt Lavin CC BY-SA 2.0 Elymus virginicus
photographs: existing diagnostic bowed bony glume base photo previously
external-only, and independent full-res second field/source closeup.
Preserves current Canadian/Hordeum comparisons and all native/county holds.
"""
from pathlib import Path
import hashlib,io,json,time
import requests
from PIL import Image,ImageOps

ROOT=Path("content/taxa/Poaceae/Elymus")
SPECIES=ROOT/"elymus-virginicus/species.json"
GENUS=ROOT/"genus.json"
REPORT=Path("reports/elymus-virginicus-two-commons-source-diagnostic-jpegs-20261023.json")
RELEASE=Path("workflow/field-id-publication/2026-10-23-elymus-virginicus-two-glume-macros.json")
LIC="CC BY-SA 2.0"
LICURL="https://creativecommons.org/licenses/by-sa/2.0/"
SOURCES=[
 {
 "id":"3923888937",
 "title":"File:Elymus virginicus_(3923888937).jpg",
 "source_page":"https://commons.wikimedia.org/wiki/File:Elymus_virginicus_(3923888937).jpg",
 "remote":"https://upload.wikimedia.org/wikipedia/commons/6/63/Elymus_virginicus_%283923888937%29.jpg",
 "dest":"matt-lavin-3923888937-virginia-wildrye-u-bowed-glumes.jpg",
 "actual_role":"Real detached/isolated paired glume bases displaying PALE hard, conspicuously outward-bowed U-like base, not matched same-voucher local plant",
 "dims":[544,1344],
 "panel_existing":True
 },
 {
 "id":"20829350870",
 "title":"File:Elymus virginicus_(20829350870).jpg",
 "source_page":"https://commons.wikimedia.org/wiki/File:Elymus_virginicus_(20829350870).jpg",
 "remote":"https://commons.wikimedia.org/wiki/Special:Redirect/file/Elymus%20virginicus%20%2820829350870%29.jpg",
 "dest":"matt-lavin-20829350870-virginia-wildrye-mature-macro.jpg",
 "actual_role":"Source-determined Virginia wildrye Montana plant, source explicitly describes pale, bony outward-curved glume bases vs E. glaucus; specific visible pixels and potential new arrows need post-download independent review",
 "dims":[3456,4608],
 "panel_existing":False
 }]
s=json.loads(SPECIES.read_text(encoding="utf-8"))
g=json.loads(GENUS.read_text(encoding="utf-8"))
assert s["scientific_name"]=="Elymus virginicus" and s["id"]=="elymus-virginicus"
assert len(s["images"])==2 and len(s["visual_comparison"]["items"])==5
assert len(g["visual_comparison"]["items"])==14
assert "FIELD_READY_PHOTO_GAPS" in s["field_id_finish_pass"]["stage"]
native_snapshot={key:s.get(key) for key in ("project_inclusion","county_occurrences_target_zone","native_target_zone_calculated","morphology_keys")}
session=requests.Session();session.headers.update({"User-Agent":"HaysBotanyVirginiaWildryeOriginalPhotoArchive/1.0 botanical educational source credit","Accept":"image/jpeg,image/*;q=0.8"})
report={"species":"Elymus virginicus","author":"Matt Lavin","license":"CC BY-SA 2.0 (attribution and share-alike for image adaptations)","lic_url":LICURL,
"exact_species_verified":"Matt Lavin original source description and independent Wikimedia Commons FlickreviewR copyright checks",
"new_physically_archived_images":0,"photos":[],"stage":"FIELD_READY_PHOTO_GAPS",
"unproven":"Matched Hays vouchered live mature spike 1mm U-glume vs Canada V-glume, true 1mm auricles and ligule, root-to-spike same accession"}
for entry in SOURCES:
 dest=SPECIES.parent/"images"/entry["dest"]
 if dest.exists():raise RuntimeError("Will not overwrite existing file "+str(dest))
 remote=entry["remote"]
 last=None
 for attempt in range(3):
  try:
   r=session.get(remote,timeout=42);r.raise_for_status()
   b=r.content
   if not b.startswith(bytes.fromhex("ffd8ff")) or len(b)<20000:raise ValueError("Wrong original file response")
   with Image.open(io.BytesIO(b)) as im:
    im.load()
    if im.format!="JPEG" or list(im.size)!=entry["dims"]:raise ValueError(f"Unexpected exact source dimensions {im.size}, expect {entry['dims']}")
    rgb=ImageOps.exif_transpose(im).convert("RGB")
   dest.parent.mkdir(parents=True,exist_ok=True)
   # Save exact pixel geometry, removing sensitive location metadata from original.
   rgb.save(dest,"JPEG",quality=92,optimize=True)
   originalhash=hashlib.sha256(b).hexdigest()
   break
  except (requests.RequestException,OSError,ValueError) as e:
   last=str(e)
   if attempt<2:time.sleep(4*(attempt+1))
 else:raise RuntimeError(f"Original source download not authenticated: {entry['id']} {last}")
 buf=dest.read_bytes()
 with Image.open(dest) as im:
  assert im.format=="JPEG" and im.mode=="RGB" and not im.getexif().get(34853)
  dimensions=list(im.size)
  im.verify()
 filehash=hashlib.sha256(buf).hexdigest()
 record={
  "file":"images/"+entry["dest"],"role":entry["actual_role"],
  "creator":"Matt Lavin","license":LIC,"license_url":LICURL,
  "source_page":entry["source_page"],"source_image":remote,
  "source_taxon_name":"Elymus virginicus","original_photo_id":entry["id"],
  "public_reuse":"YES: exact individual CC BY-SA 2.0 original source with credit/SA and modifications stated",
  "study_use":"yes","archive_sha256":filehash,"original_source_sha256":originalhash,
  "image_dimensions":dimensions,
  "modifications":"Full original decoded/re-encoded clean RGB JPEG with exact original pixel dimensions; EXIF including GPS stripped, no cropping. Attribution and SA requirements preserved.",
  "photo_review":"Source-verified exact photographed Montana accession, no proven same-specimen roots, paired mature node and local Hays ligule. PROVISIONAL USER PHOTO REVIEW."
 }
 s["images"].append(record)
 if entry["panel_existing"]:
  for row in (s["visual_comparison"]["items"],g["visual_comparison"]["items"]):
   match=[p for p in row if p.get("source_page")==entry["source_page"] and p.get("scientific_name")=="Elymus virginicus"]
   assert len(match)==1,("existing macro panel",len(match))
   assert len(match[0].get("markers",[]))==2, "Preserve two previously verified gross feature arrows"
   match[0]["image_url"]=str(dest)
   match[0]["photo_status"]="Real local source-authenticated 544x1344 Matt Lavin original now physically archived CC BY-SA with EXIF stripped. Two previous gross glume/U-base arrows preserved. NOT matched Hays measured specimen. PROVISIONAL USER REVIEW."
 else:
  panel={
   "label":"VIRGINIA — second original Matt Lavin high-resolution glume-base specimen (review arrows pending)",
   "scientific_name":"Elymus virginicus",
   "image_url":str(dest),"image_fit":"contain",
   "image_role":entry["actual_role"],
   "caption":"Second ORIGINAL high-resolution Matt Lavin Montana source-determined Virginia wildrye photograph. Source describes hard PALE glume bases that curve away from one another; inspect the original pixels and at least two mature attached nodes. This is NOT a local voucher and the photo has no 1-mm ruler calibration.",
   "why_it_matters":"Extra source-specific glume architecture perspective to teach the U-bowed Virginia versus often straighter Canada base; preserve potential hybrid uncertainty.",
   "creator":"Matt Lavin","license":LIC,"license_url":LICURL,
   "source_page":entry["source_page"],"markers":[],
   "photo_status":"3,456x4,608 real original physically archived under CC BY-SA 2.0. No new feature arrows until pixel-specific visual audit. PROVISIONAL USER PHOTO REVIEW."
  }
  s["visual_comparison"]["items"].insert(1,panel)
  g["visual_comparison"]["items"].insert(3,dict(panel))
 report["photos"].append({"id":entry["id"],"source":entry["source_page"],"original_url":remote,
 "file":str(dest),"dims":dimensions,"bytes":len(buf),"source_sha256":originalhash,"local_sha256":filehash})
 report["new_physically_archived_images"]+=1
assert report["new_physically_archived_images"]==2
assert len(s["images"])==4 and len(s["visual_comparison"]["items"])==6
assert len(g["visual_comparison"]["items"])==15
assert all(s.get(k)==v for k,v in native_snapshot.items())
s["curation_status"]["photo_metadata_count"]=4
s["curation_status"]["photo_files_present"]=4
s["curation_status"]["virginia_two_real_source_macros_20261023"]={
 "two_new_original_photo_files":2,"existing_external_glume_macro_now_local":True,
 "total_local_original_files":4,"species_panels":6,"genus_panels":15,
 "new_verified_fine_1mm_glume_dissection":False,"county_native_review_untouched":True,"stage":"FIELD_READY_PHOTO_GAPS"}
s["field_id_finish_pass"]["virginia_glume_macro_archive_20261023"]={
 "true_photos":2,"report":str(REPORT),"physically_archived_total":4,
 "critical_cue":"At several attached rachis nodes inspect the two spikelet groups and their source-documented pale hard U-bowed glume BASES; do not rely on head posture alone; Canada and hybrids may overlap.",
 "sources":[z["source_page"] for z in SOURCES],
 "not_complete":["1mm true matched Hays paired-node U vs V comparison with Canada wildrye","Attached fresh lemma/glume and rachis section with true scales and glume awn origins","Opened auricles and central true membranous ligule from same local plant"],
 "status":"FIELD_READY_PHOTO_GAPS"
}
s["visual_comparison"]["subtitle"]="Four original locally archived Matt Lavin CC BY-SA 2.0 Virginia wildrye photos, six teaching panels and Canada comparisons. High-contrast real pale U-bowed glume-base macro now lives in GitHub; exact mm-scale Hays specimen still missing."
g["visual_comparison"]["subtitle"]="Virginia + Canada wildrye comparison now has a second real archived Virginia macro; whole Hays same-voucher glume-base and auricle/ligule mm series remain photo holds."
SPECIES.write_text(json.dumps(s,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
GENUS.write_text(json.dumps(g,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
REPORT.parent.mkdir(parents=True,exist_ok=True)
REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
RELEASE.parent.mkdir(parents=True,exist_ok=True)
RELEASE.write_text(json.dumps({"type":"manual_field_id_publication","date":"2026-10-23","species":"Elymus virginicus",
"new_originals":2,"local_originals":4,"species_panels":6,"genus_panels":15,
"licenses":"2 exact CC BY-SA 2.0 source-verified Matt Lavin original files","photo_report":str(REPORT),
"status":"FIELD_READY_PHOTO_GAPS",
"release_note":"GitHub Pages publication marker; success requires separate build and deploy completion"},indent=2)+"\n",encoding="utf-8")
print("PASS: TWO exact CC BY-SA Virginia wildrye real original JPEGs, already annotated U-glume panel now LOCAL",flush=True)
