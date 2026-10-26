#!/usr/bin/env python3
"""Add individually source-licensed CC0 Muhlenbergia utilis collar and flowering views.
Exact-photo hash required; no microscopic claims or arrows before physical pixel review.
One-species atomic edit only; preserve county, taxonomy, unrelated media and rights fields.
"""
import hashlib,io,json,pathlib,urllib.request
from PIL import Image,ImageOps
BASE=pathlib.Path("content/taxa/Poaceae/Muhlenbergia/muhlenbergia-utilis")
CARD=BASE/"species.json"
EVID=pathlib.Path("reports/lane3-utilis-two-photo-scout-20261026.json")
REPORT=pathlib.Path("reports/lane3-utilis-two-diagnostics-installed-20261026.json")
FILE_ROLE=[
(410577695,"images/aparejo-collar-region-inat-410577695-cc0.jpg",
"Collar/leaf-sheath junction macro showing adjacent fine blade and pale exposed membranous-looking tissue",
"TRUE-PLANT COLLAR REGION — pale membrane near blade–sheath opening",
"Verified wild Uvalde County source photograph shows pale triangular sheath-mouth tissue beside a narrow green blade. This is a source photo of the region to examine; the short free ligule itself is NOT independently dissected or measured, and there is no 1-mm ruler. Treat as collar-region reference, NOT a measured ligule.",
"Real blade/sheath position teaches where to open a leaf to verify a 0.2–0.8-mm membranous ligule on a fresh identified specimen; no ruler or standalone membrane proof."),
(410577679,"images/aparejo-attached-flowering-inat-410577679-cc0.jpg",
"Actual flowering architecture; multiple narrow spikelets attached along a short one-sided/contracted panicle branch",
"TRUE APAREJO — attached narrow mature flowering head",
"Verified exact-source Uvalde County flowering photo shows a slender flowering axis and clearly separated slender attached spikelets. Recognize the narrow head; tiny parts inside each spikelet, glume/lemma/awn proportions and exact dimensions are NOT established from the photo.",
"Provides the missing true reproductive/attached flowering-head view rather than another general grassy patch.")
]
AGENT="HaysCountyBotany/1.0 (noncommercial exact-source licensed iNaturalist educational photo curation)"
def get(url):
 q=urllib.request.Request(url,headers={"User-Agent":AGENT,"Accept":"image/jpeg,application/json"})
 with urllib.request.urlopen(q,timeout=40) as r:
  data=r.read(14000001)
 if len(data)>14000000:raise ValueError("Image too large")
 return data
d=json.loads(CARD.read_text(encoding="utf-8"))
proof=json.loads(EVID.read_text(encoding="utf-8"))
assert d["id"]=="muhlenbergia-utilis" and d["scientific_name"]=="Muhlenbergia utilis"
assert proof["taxon"]=="Muhlenbergia utilis" and proof["source_quality"]=="research"
assert proof["observation_id"]==231187884 and not proof["errors"]
# Concurrent-friendly idempotency: another Lane 3 job may already have archived
# these exact two photo IDs. Verify the existing objects and preserve their
# correct pixel-reviewed arrows, photo rights, science holds, and captions.
existing_by_id={str(x.get("photo_source_id")):x for x in d["images"] if x.get("photo_source_id")}
if set(("410577695","410577679")).issubset(existing_by_id):
 files=[]
 for pid in (410577695,410577679):
  x=existing_by_id[str(pid)]
  evidence=next(z for z in proof["candidates"] if z["photo_id"]==pid)
  assert x["license"]=="CC0 1.0"
  assert x["original_sha256"]==evidence["sha256_original"]
  assert x["source_page"]==evidence["source_photo_page"]
  actual=BASE/x["file"]
  assert actual.is_file()
  digest=hashlib.sha256(actual.read_bytes()).hexdigest()
  assert digest==x["archive_sha256"],f"Unexpected concurrent archive mutation: {pid}"
  with Image.open(actual) as im:
   assert im.format=="JPEG" and not im.getexif().get(34853)
   im.verify()
  matching=[p for p in d["visual_comparison"]["items"] if p.get("image_url")==str(actual)]
  assert len(matching)==1 and matching[0]["scientific_name"]=="Muhlenbergia utilis"
  assert matching[0]["license"]=="CC0 1.0"
  for marker in matching[0].get("markers",[]):
   assert all(isinstance(marker.get(k), (int,float)) and 0<=marker[k]<=100 for k in ("target_x","target_y","label_x","label_y"))
  files.append({"id":pid,"saved_sha256":digest,"source_sha256":evidence["sha256_original"],"path":str(actual),
   "license":"CC0 1.0","source_page":evidence["source_photo_page"],
   "existing_pixel_reviewed_arrows":len(matching[0].get("markers",[]))})
 assert len(d["images"])==8 and len(d["visual_comparison"]["items"])==8
 assert d["visual_comparison"]["items"][-1]["scientific_name"]=="Muhlenbergia schreberi"
 REPORT.write_text(json.dumps({"status":"PHYSICALLY_ARCHIVED_TWO_CC0_DIAGNOSTIC_IMAGES",
  "species":"Muhlenbergia utilis","preexisting_concurrent_install_reconciled":True,
  "files":files,"new_image_files":0,"total_species_files":8,"gallery_panels":8,
  "new_arrow_count":0,"existing_arrow_count":sum(x["existing_pixel_reviewed_arrows"] for x in files),
  "remaining_photo_gaps":["Exposed connected underground rhizome/actual roots and shoots","Calibrated free inner membranous ligule"]},indent=2)+"\n")
 print(json.dumps({"result":"ALREADY_ARCHIVED_AND_VERIFIED_NO_DUPLICATES","ids":[410577695,410577679],"local_count":8}))
 raise SystemExit(0)
assert len(d["images"])==6 and len(d["visual_comparison"]["items"])==6
base_holds={k:json.dumps(d.get(k),sort_keys=True) for k in ("county_occurrences_target_zone","target_zone_count","native_target_zone_calculated","project_inclusion","morphology_keys")}
new_images=[]
new_panels=[]
blobs={}
audit=[]
for id,relative,role,label,caption,why in FILE_ROLE:
 info=next(x for x in proof["candidates"] if x["photo_id"]==id)
 assert info["license_code"]=="cc0" and info["valid_source_jpeg"]
 assert info["source_photo_page"]==f"https://www.inaturalist.org/photos/{id}"
 assert info["sha256_original"] and info["original_url"]
 assert str(id) not in json.dumps(d["images"]), "Avoid duplicate archived photo"
 original=get(info["original_url"])
 assert hashlib.sha256(original).hexdigest()==info["sha256_original"]
 with Image.open(io.BytesIO(original)) as im:
  assert im.format=="JPEG"
  im.verify()
 with Image.open(io.BytesIO(original)) as im:
  im=ImageOps.exif_transpose(im).convert("RGB")
  assert im.width>=300 and im.height>=240
  original_dims=[im.width,im.height]
  im.thumbnail((2000,2000),Image.Resampling.LANCZOS)
  b=io.BytesIO()
  im.save(b,"JPEG",quality=93,optimize=True)
  jpeg=b.getvalue()
 with Image.open(io.BytesIO(jpeg)) as im:
  assert im.format=="JPEG" and not im.getexif().get(34853)
  im.verify()
 path=BASE/relative
 if path.exists():raise ValueError("Original image already archived; do not overwrite")
 blobs[path]=jpeg
 sha=hashlib.sha256(jpeg).hexdigest()
 licurl="https://creativecommons.org/publicdomain/zero/1.0/"
 new_images.append({"file":relative,"role":role,"creator":"no rights reserved (original iNaturalist CC0 photographer not individually identified)",
 "license":"CC0 1.0","license_url":licurl,
 "source_page":info["source_photo_page"],"source_observation":"https://www.inaturalist.org/observations/231187884",
 "photo_source_id":id,"source_observation_id":231187884,
 "source_taxon":"Muhlenbergia utilis — Research Grade iNaturalist, species determination not independently voucher-certified",
 "source_place":"Uvalde County, TX, USA",
 "original_source_image":info["original_url"],"original_sha256":info["sha256_original"],
 "archive_sha256":sha,"original_dimensions":original_dims,"image_dimensions":original_dims,
 "public_reuse":"CC0, original exact-photo license_code and photo ID verified 2026-10-26",
 "modifications":"Resaved with EXIF/GPS removed; no crops, no arrows or pixel drawings.",
 "photo_status":"SOURCE_LICENSE_VERIFIED__LOCAL_JPEG_ARCHIVED__BROAD_STRUCTURE_ONLY; submillimeter true ligule and independently numbered spikelet bracts NOT certified"})
 new_panels.append({"label":label,"scientific_name":"Muhlenbergia utilis",
  "image_url":str(path),"image_fit":"contain","image_role":role,"caption":caption,
  "why_it_matters":why,"creator":"original iNaturalist CC0 photo (photographer unspecified in source attribution)",
  "license":"CC0 1.0","license_url":licurl,"source_page":info["source_photo_page"],
  "observation_source":"https://www.inaturalist.org/observations/231187884",
  "photo_status":"Actual source CC0 original physically archived. No new arrows until full saved JPEG reviewed. Collar/membrane not measured; head spikelets whole, not dissected.", "markers":[]})
 audit.append({"id":id,"source_sha256":info["sha256_original"],"saved_sha256":sha,
  "path":str(path),"original_dimensions":original_dims,"license":"CC0 1.0","source_page":info["source_photo_page"],"role":role})
panels=d["visual_comparison"]["items"]
assert panels[-1]["scientific_name"]=="Muhlenbergia schreberi"
d["images"].extend(new_images)
d["visual_comparison"]["items"]=panels[:-1]+new_panels+panels[-1:]
d["visual_comparison"]["title"]="Aparejo grass — natural creeping mats, true collar region and attached flowering head"
d["visual_comparison"]["subtitle"]="Eight species-local archived photos, including new source-authenticated CC0 leaf-sheath region and attached narrow panicle. NIMBLEWILL at the very end is a DIFFERENT-SPECIES comparison. Buried scaled rhizome and independently measured free ligule are still missing."
d["visual_comparison"]["memory_rule"]="Aparejo: very fine leaves + narrow little flowering head + BELOW-GROUND scaly rhizomes when actually exposed; do not infer buried rhizomes from an ordinary surface patch."
d["visual_comparison"]["overlay_note"]="2026-10-26 Lane 3: exactly two independently image-licensed CC0 photos, IDs 410577695 (collar region; 317×251) and 410577679 (short narrow flowering head; 540×510), restored into actual local image files and visual gallery. Original hashes verified, GPS/EXIF removed. No uninspected microscopic arrows. Existing 6 photos, source rights, comparison, taxonomy and county holds preserved. True collar membrane length and rhizome structures remain genuine missing photo roles."
q=d["field_photo_quickcheck"]
q["steps"]=[
 "Gallery image 1 is the WIDE fine grassy patch beside paving/shoes. Habitat/size only; its roots and single-stem identity are hidden.",
 "Gallery image 2 is Chet Burrier's real fine foliage against fingertips; use to see the short, threadlike, often inrolled leaf blades, not a true mm-scale section.",
 "Gallery image 3 is the wild Uvalde County whole plant patch beneath limestone. Real natural habit, but no excavated underground stems.",
 "Gallery image 4 is the Burnet County in-place leafy shoots. Follow their leaf attachment and check how many shoots occupy the same low patch; buried rhizomes remain unseen.",
 "Gallery image 5 is wild Uvalde fine foliage held beside a hand for general scale. Source-labelled grass intermixed with other stems, no confirmed roots.",
 "Gallery image 6 is an actual source-identified collar/leaf-sheath region. Pale tissue is visible at the blade opening, but the TRUE free inner membrane is not measured or separately dissected. Do not point to a fake 0.2–0.8 mm ligule.",
 "Gallery image 7 is a source-determined attached narrow flowering head with multiple intact spikelets (real reproductive structure). It is NOT a glume/lemma dissection; don't measure awns without a mm ruler.",
 "Gallery image 8 is a DIFFERENT species, nimblewill (M. schreberi). It shows surface leafy stem segments; do not mistake them for a confirmed rooted stolon or an aparejo rhizome.",
 "To finish the crucial ID step, gently expose an aparEjo grass SCALY belowground RHIZOME with actual nodes, attached vegetative shoots, roots and mm ruler. Then expose a fresh true membranous ligule with 1-mm scale. No currently archived photo proves either."
]
q["featured_photo_indices"]=[3,5,6,7]
q["field_rule"]="Use whole habit + real narrow attached head + very fine blade to suspect aparejo, then verify the true short membranous ligule and an actual underground scaly rhizome (against nimblewill's aboveground stolons). Do not infer a rhizome from grass in a sidewalk crack or from a description alone."
q["warning"]="FIELD_READY_PHOTO_GAPS. Eight species-local image files, seven same-species field panels and one other-species nimblewill comparison; collar region is photographed, but the free 0.2–0.8 mm membranous ligule is NOT separately resolved or scaled and actual underground rhizomes/root nodes are NOT visible. Preserve source-level rights and provisional science."
d["field_id_finish_pass"]["stage"]="FIELD_READY_PHOTO_GAPS — true attached mature panicle now locally photographed and true collar region shown; buried rhizome and free scaled ligule not yet documented."
d["field_id_finish_pass"]["lane3_two_cc0_diagnostic_import_20261026"]={
 "original_photo_ids":[410577695,410577679],"source_observation":231187884,
 "new_source_verified_jpegs":2,"total_local_jpegs":8,
 "same_species_panels":7,"different_species_panels":1,
 "photo_roles":{"true_collarlocation":"PARTIAL: pale tissue at blade/sheath, 317×251 source, no 1-mm scale or independent membrane length",
               "attached_whole_inflorescence":"PRESENT: actual narrow branched flowering axis with attached spikelets, 540×510",
               "rhizome":"ABSENT: underground scaly connected stem not excavated",
               "genuine_membranous_ligule":"NOT SCALED / UNCERTAIN exact free edge"},
 "copyright":"Both original individual photo-license code CC0 verified; previous CC BY and CC BY-SA unchanged",
 "remaining_field_photography":["Same rooted specimen, visible buried scaly rhizome nodes and attached shoots with scale","Opened inner true short membranous ligule with mm scale","Optional actual dissected ripe one-flowered spikelet at mm scale when needed to rule out look-alikes"],
 "no_fabricated_measurements":True
}
d["curation_status"]["photo_files_present"]=8
d["curation_status"]["photo_metadata_count"]=8
d["curation_status"]["lane3_utilis_two_diagnostics_20261026"]="Two source-verified real CC0 exact-species collar/flowering original JPEGs installed, correct 8-panel gallery and photo-index lesson; rhizome and true measured ligule missing."
d["learner_visual_status"]["image_count"]=8
d["learner_visual_status"]["status"]="FIELD_READY_PHOTO_GAPS"
assert all(json.dumps(d.get(k),sort_keys=True)==v for k,v in base_holds.items())
assert len(d["images"])==8 and len(d["visual_comparison"]["items"])==8
assert all(0<=i<8 for i in q["featured_photo_indices"])
for path,raw in blobs.items():path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
CARD.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
REPORT.write_text(json.dumps({"status":"PHYSICALLY_ARCHIVED_TWO_CC0_DIAGNOSTIC_IMAGES","species":"Muhlenbergia utilis","files":audit,
"new_image_files":2,"total_species_files":8,"gallery_panels":8,"new_arrow_count":0,
"remaining_photo_gaps":["Exposed scaly underground rhizome with actual connected roots/shoots and 1-mm scale","Free true membranous ligule at blade-sheath junction and 1-mm scale"]},indent=2)+"\n",encoding="utf-8")
print(json.dumps({"result":"PHYSICALLY_ARCHIVED_TWO_CC0_DIAGNOSTIC_IMAGES","photo_ids":[i[0] for i in FILE_ROLE],"gallery_panels":8,"species_photos":8}))
