#!/usr/bin/env python3
"""Physically archive one real Tridens flavus spikelet closeup from Commons.

Source scientific identification is photographer-labelled, NOT independently
vouchered local material. Never invent mm-scale, glume or nerve-hair arrows.
"""
from pathlib import Path
import io, hashlib, json, time, requests
from PIL import Image, ImageOps

ROOT=Path("content/taxa/Poaceae/Tridens")
SPECIES=ROOT/"tridens-flavus/species.json"
GENUS=ROOT/"genus.json"
REPORT=Path("reports/tridens-flavus-real-lavin-spikelet-20261022.json")
RELEASE=Path("workflow/field-id-publication/2026-10-22-tridens-flavus-lavin-spikelet.json")
SRC="https://commons.wikimedia.org/wiki/File:Tridens_flavus_(4120267818).jpg"
ORIGINAL="https://upload.wikimedia.org/wikipedia/commons/b/b5/Tridens_flavus_%284120267818%29.jpg"
ORIGINAL_BACKUP="https://commons.wikimedia.org/wiki/Special:Redirect/file/Tridens%20flavus%20%284120267818%29.jpg"
LIC_URL="https://creativecommons.org/licenses/by-sa/2.0/"
FILENAME="matt-lavin-4120267818-purpletop-real-spikelet-cc-by-sa-2.jpg"
DEST=SPECIES.parent/"images"/FILENAME
s=json.loads(SPECIES.read_text(encoding="utf-8"))
g=json.loads(GENUS.read_text(encoding="utf-8"))
assert s["id"]=="tridens-flavus" and s["scientific_name"]=="Tridens flavus"
assert len(s["images"])==2 and len(s["visual_comparison"]["items"])==6
assert len(g["visual_comparison"]["items"])==6
assert "FIELD_READY_PHOTO_GAPS" in s["field_id_finish_pass"]["stage"]
assert s["curation_status"]["range_reviewed"] is False

session=requests.Session()
session.headers.update({"User-Agent":"HaysBotany-CreditedPhotoArchive/1.0 (educational publicly reusable originals)","Accept":"image/jpeg,image/*;q=0.8"})
success=None
for remote in [ORIGINAL, ORIGINAL_BACKUP]:
  for i in range(2):
    try:
      res=session.get(remote,timeout=32)
      res.raise_for_status()
      raw=res.content
      if len(raw)<19000 or not raw.startswith(bytes.fromhex("ffd8ff")): raise ValueError("Not the actual source JPEG")
      with Image.open(io.BytesIO(raw)) as photo:
        photo.load()
        if photo.format!="JPEG" or photo.size!=(668,704): raise ValueError(f"Unexpected original dimensions: {photo.size}")
        rgb=ImageOps.exif_transpose(photo).convert("RGB")
      DEST.parent.mkdir(parents=True,exist_ok=True)
      rgb.save(DEST,"JPEG",quality=94,optimize=True)
      success={"url":remote,"source_sha256":hashlib.sha256(raw).hexdigest(),"source_bytes":len(raw)}
      break
    except (requests.RequestException,ValueError,OSError) as exc:
      if i<1: time.sleep(3)
  if success:break
if not success: raise RuntimeError("True Flickr/Commons CC BY-SA source could not be decoded; abort without incorrect photo assertions.")
by=DEST.read_bytes()
with Image.open(DEST) as ph:
  assert ph.mode=="RGB" and ph.format=="JPEG" and ph.size==(668,704)
  assert not ph.getexif().get(34853)
  ph.verify()
record={
  "file":"images/"+FILENAME,
  "role":"REAL Tridens flavus reproductive closeup: left and center separated spikelet structures and intact multifloret spikelet at right; exact glume/lemma relationships NOT proved by this image without specimen dissection",
  "creator":"Matt Lavin",
  "license":"CC BY-SA 2.0",
  "license_url":LIC_URL,
  "source_page":SRC,
  "source_image":ORIGINAL,
  "original_source_page":"https://www.flickr.com/photos/35478170@N08/4120267818",
  "study_use":"yes",
  "public_reuse":"yes",
  "image_dimensions":[668,704],
  "archive_sha256":hashlib.sha256(by).hexdigest(),
  "photo_review":"Original 668×704 JPEG observed at Commons source. Reviewer identified intact multiple florets and separated botanical pieces; isolated individual lemma/glume labels NOT independently checked against a specimen. PROVISIONAL — USER PHOTO REVIEW PENDING.",
  "image_status":"PHYSICALLY_ARCHIVED_REAL_EXACT_SPECIES_SOURCE_DETERMINATION_PROVISIONAL",
  "modifications":"Original CC BY-SA 2.0 source resized zero pixels (668x704); clean RGB JPEG metadata/GPS removed, no crop. Arrows are browser overlays, original attribution preserved."
}
s["images"].append(record)
panel={
  "label":"3 · SPIKELET MICRO — actual multi-flowered purpletop head and separated parts · PROVISIONAL REVIEW",
  "scientific_name":"Tridens flavus",
  "image_url":str(DEST),
  "image_fit":"contain",
  "image_role":"One real multi-flowered Tridens flavus spikelet at right; two detached components at left/center. No physical mm calibration and no unproven glume/lemma nerve-specific claim.",
  "caption":"Matt Lavin's 668×704 close-up has the entire purpletop spikelet with several nested florets on the RIGHT; LEFT and CENTER are detached parts. Source was labelled Tridens flavus. Without a measurement or attached pre-dissection sequence we cannot say which tiny individual part is the upper glume, lemma, or palea.",
  "why_it_matters":"Bridges the previously missing reproductive macro: crew can see what a Tridens multi-flowered spikelet looks like before collecting a ripe local sample for exact glume and 3-nerved lemma verification.",
  "creator":"Matt Lavin",
  "license":"CC BY-SA 2.0","license_url":LIC_URL,"source_page":SRC,
  "photo_status":"Original downloaded, physically integrity-checked, exact-source CC BY-SA 2.0 and author reviewed. PROVISIONAL — USER PHOTO REVIEW PENDING; no 1mm original ruler or same local voucher.",
  "markers":[
    {"label":"Intact spikelet — several florets","label_x":49,"label_y":11,"target_x":81,"target_y":46},
    {"label":"Isolated spikelet part; identity unconfirmed","label_x":6,"label_y":88,"target_x":43,"target_y":45}
  ]
}
for m in panel["markers"]:
 assert all(0<=m[k]<=100 for k in ("label_x","label_y","target_x","target_y"))
s["visual_comparison"]["items"].insert(2,panel)
g["visual_comparison"]["items"].insert(4,dict(panel,label="Purpletop REAL spikelet and separated parts — provisional",caption=panel["caption"]+" Compare this with the two other Tridens head shapes; never infer their nerve hairs from the broad photos."))
s["curation_status"]["photo_metadata_count"]=3
s["curation_status"]["photo_files_present"]=3
s["curation_status"]["tridens_lavin_spikelet_physical_second_pass_20261022"]={
  "original_new_jpeg_files":1,"actual_dimensions":[668,704],
  "species_teaching_panels":7,"genus_teaching_panels":7,
  "fine_anatomical_lemma_arrows_verified":0,
  "gross_spikelet_arrows_new":2,
  "photo_rights":"Matt Lavin exact individual Commons image CC BY-SA 2.0, proper creator/source/link and photographic alterations disclosed",
  "status":"FIELD_READY_PHOTO_GAPS"
}
s["field_id_finish_pass"]["real_purpletop_spikelet_photo_20261022"]={
  "saved_file":str(DEST),
  "verification_report":str(REPORT),
  "source":SRC,
  "two_true_broad_arrows":"Intact compound spikelet on right; detached unknown part in center; NOT glume/lemma identity labels.",
  "science_reference":"https://www.minnesotawildflowers.info/grass-sedge-rush/purpletop",
  "research_link_only":"Minnesota Wildflowers has true labeled mm-scale glumes/lemma/ligule macro; copyright permission to mirror NOT established, NOT downloaded into gallery.",
  "exact_last_mile_photo_needs":[
    "A mature purpletop whole rooted plant and panicle as one regionally verified individual",
    "Genuine 0.2–0.5 mm ciliate/membranous ligule and collar with millimeter ruler and physically attached same plant",
    "One same-plant mature spikelet with 1 mm scale and glumes, floret dissection, lemma 3 nerves and nerve hairs under 10–20×",
    "Matched local open-purpletop-versus-Texas-Tridens spikelet dissection, matching growth stage and scale"
  ],
  "status":"FIELD_READY_PHOTO_GAPS: reproductive structure now pictured but the precise fine anatomy is not physically measured"
}
s["field_photo_quickcheck"]["featured_photo_indices"]=[0,1,2]
s["field_photo_quickcheck"]["steps"].insert(2,
  "NEW ACTUAL MACRO: see intact multi-flowered purpletop spikelet at right of Matt Lavin's licensed photo, and separate pieces on left/center. These are real pixels, not proven labels for individual glumes/lemmas; compare real specimen under 10–20×.")
s["field_id_references"].append(SRC) if isinstance(s["field_id_references"],list) and SRC not in s["field_id_references"] else None
s["field_id_finish_pass"]["photo_limit"]="Now THREE real source-labelled physically archived purpletop JPEGs, including Matt Lavin spikelet macro, but still no calibrated ligand/glume/lemma-nerve hair photos or same-specimen local roots-to-spikelet series."
assert len(s["images"])==3 and len(s["visual_comparison"]["items"])==7 and len(g["visual_comparison"]["items"])==7
SPECIES.write_text(json.dumps(s,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
GENUS.write_text(json.dumps(g,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
REPORT.parent.mkdir(parents=True,exist_ok=True)
REPORT.write_text(json.dumps({
 "date":"2026-10-22","species":"Tridens flavus","source_photo":SRC,
 "creator":"Matt Lavin","license":"CC BY-SA 2.0","license_link":LIC_URL,
 "scientific_source_identity":"Original photographer labelled Tridens flavus",
 "image_source_verified_at":success,
 "archived_file":str(DEST),"archived_bytes":len(by),
 "dimensions":[668,704],"archived_sha256":hashlib.sha256(by).hexdigest(),
 "species_gallery_panels":7,"genus_gallery_panels":7,
 "known_no_same_voucher":True,"original_photo_unmodified_geometry":True,
 "last_mile_hold":"True 1mm ligule and original ripe glume/lemma nerve hairs on one Hays-verified mature plant"
},indent=2)+"\n",encoding="utf-8")
RELEASE.parent.mkdir(parents=True,exist_ok=True)
RELEASE.write_text(json.dumps({
  "date":"2026-10-22","type":"manual_field_id_publication",
  "species":"Tridens flavus","source_photographer":"Matt Lavin","photo_license":"CC BY-SA 2.0",
  "real_new_jpeg_files":1,"total_physically_archived_species_files":3,"photo_species_panels":7,"genus_panels":7,
  "report":str(REPORT),"right_filter":"normal public photo source/license filtering",
  "status":"FIELD_READY_PHOTO_GAPS","release_note":"GitHub Pages marker; do not claim deployed until SUCCESS"
},indent=2)+"\n",encoding="utf-8")
print("PASS: 1 REAL EXACT-SPECIES CC BY-SA multi-flowered spikelet photo, no invented glume lemma micro labels",flush=True)
