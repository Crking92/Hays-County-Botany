#!/usr/bin/env python3
"""Archive 6 exact-source original Bob Harms Ozarkgrass photos for credited
noncommercial educational site; retain taxonomy and county-review holds.
No invented mm measurements, unattested single voucher or microscopic arrows.
"""
import hashlib,io,json,time
from pathlib import Path
import requests
from PIL import Image,ImageOps

ROOT=Path("content/taxa/Poaceae/Limnodea")
SP=ROOT/"limnodea-arkansana/species.json"
GENUS=ROOT/"genus.json"
PHOTO=SP.parent/"images"
REPORT=Path("reports/limnodea-six-source-verified-harms-photos-20261023.json")
RELEASE=Path("workflow/field-id-publication/2026-10-23-limnodea-six-actual-harms-photos.json")
SRC="https://w3.biosci.utexas.edu/prc/Monocots/GrassHTML/data/"
HOME="https://w3.biosci.utexas.edu/prc/Monocots/"
PERMIT="BOB_HARMS_SELECTED_MONOCOTS_EDU_WITH_CREDIT_20261022"
LIC="© Bob Harms — scientific/educational use with attribution (NOT Creative Commons)"
DATA=[
 ("LIAR-b","1 · OZARKGRASS PLANT HABIT — Bob Harms real regional view",
  "A source-labelled original habit view of Ozarkgrass. Confirm rooted crown separately; a cut mature stem is not the same as a visible annual root system."),
 ("LIAR-i","2 · OZARKGRASS FLOWERING AXIS — original source photo",
  "The original source photograph shows Ozarkgrass reproductive architecture. A whole flowering branch is not an individual single-floret spikelet."),
 ("LIAR-J","3 · OZARKGRASS FLOWERING DETAIL — source photograph",
  "This is an author-identified true Ozarkgrass flowering detail. Observe the actual spikelet-bearing parts; do not infer a 3 mm glume measurement from uncalibrated pixels."),
 ("LIAR-s","4 · OZARKGRASS SPIKELET STRUCTURES — original specimen",
  "A regionally sourced true Ozarkgrass photograph of reproductive structures. Two subequal glumes protect a SINGLE fertile floret, but exact glume edges require pixel review before anatomy arrows."),
 ("LIAR-d","5 · OZARKGRASS DISARTICULATION — authentic separated parts",
  "The original closeup demonstrates separation of seed-bearing material. Do not assert any isolated photographed item belongs to the same collected plant as a different source photo."),
 ("LIAR-L","6 · OZARKGRASS COLLAR/LIGULE — real botanical tissue",
  "A real author-labelled leaf-sheath and ligule-zone photo. A measured FREE membrane margin with 1 mm calibrated ruler remains a separate strict finishing criterion.")
]
s=json.loads(SP.read_text(encoding="utf-8"))
g=json.loads(GENUS.read_text(encoding="utf-8"))
assert s["id"]=="limnodea-arkansana" and s["scientific_name"]=="Limnodea arkansana"
assert s["curation_status"]["taxonomy_reviewed"] is False
assert len(s["images"])==1
assert len(s["visual_comparison"]["items"])==4 and len(g["visual_comparison"]["items"])==4
assert "FIELD_READY_PHOTO_GAPS" in s["field_id_finish_pass"]["stage"]
prior_science={key:s.get(key) for key in ["morphology_keys","comparisons","taxonomy_source"]}
PHOTO.mkdir(parents=True,exist_ok=True)
session=requests.Session();session.headers.update({"User-Agent":"HaysBotanyEducationalCentralTexasArchive/1.0","Accept":"image/jpeg,image/*;q=0.8"})
report={"species":"Limnodea arkansana","source_collection":HOME,
"copyright":"Bob Harms own exact Selected Monocots original photographs educational/scientific with credited reuse ONLY; NOT CC",
"source_discovery_report":"reports/limnodea-harms-original-source-discovery-20261023.json",
"photos":[],"physically_archived_new":0,"all_same_voucher_proven":False}
for ident,title,caption in DATA:
 url=SRC+"images/"+ident+".jpg"
 page=SRC+"pages/"+ident+".html"
 fn="bob-harms-ozarkgrass-"+ident.lower()+".jpg"
 target=PHOTO/fn
 if target.exists():raise RuntimeError("Existing original needs separate review: "+str(target))
 last=None
 for attempt in range(3):
  try:
   response=session.get(url,timeout=35);response.raise_for_status()
   raw=response.content
   if len(raw)<4500 or not raw.startswith(bytes.fromhex("ffd8ff")):
    raise ValueError("Missing original JPEG")
   with Image.open(io.BytesIO(raw)) as img:
    img.load()
    if img.format!="JPEG" or min(img.size)<120:
     raise ValueError("Wrong source image or invalid dimensions")
    clean=ImageOps.exif_transpose(img).convert("RGB")
    dims=list(img.size)
   clean.save(target,"JPEG",quality=93,optimize=True)
   src_hash=hashlib.sha256(raw).hexdigest()
   report["physically_archived_new"]+=1
   break
  except (OSError,ValueError,requests.RequestException) as e:
   last=str(e)
   if attempt<2:time.sleep(3+2*attempt)
 else:raise RuntimeError("Cannot authenticate exact original "+url+" "+last)
 data=target.read_bytes()
 with Image.open(target) as im:
  if im.mode!="RGB" or im.format!="JPEG" or list(im.size)!=dims or im.getexif().get(34853):
   raise RuntimeError("Decoded file/GPS dimensions mismatch")
  im.verify()
 sha=hashlib.sha256(data).hexdigest()
 record={
  "file":"images/"+fn,
  "role":title,
  "creator":"Bob Harms",
  "license":LIC,
  "license_url":HOME,
  "source_page":page,
  "source_image":url,
  "source_taxon_name":"Limnodea arkansana",
  "site_specific_public_permission":PERMIT,
  "public_reuse":"YES attributed scientific/educational website use of these EXACT copyrighted original source photos only, NOT CC or general redistribution",
  "image_dimensions":dims,
  "archive_sha256":sha,
  "original_source_sha256":src_hash,
  "photo_review":"PROVISIONAL USER PHOTO REVIEW; true source identified, source-specific reuse, real RGB JPEG. Organ-specific micro labels only after original-pixel inspection. Not authenticated same local voucher.",
  "modifications":"Re-encoded without crop as clean RGB JPEG; EXIF/GPS discarded. Photographer and original educational-use terms retained."
 }
 panel={
 "label":title,
 "scientific_name":"Limnodea arkansana",
 "image_url":str(target),
 "image_fit":"contain",
 "image_role":"Original precisely photographed taxon; source photo identified by Bob Harms. Specific tiny organ labels pending individual image pixel review.",
 "caption":caption,
 "why_it_matters":"Regional photographic anatomy improves the crew's ability to locate structures and find the same parts with a 10-20x lens, rather than relying only on grass silhouettes.",
 "creator":"Bob Harms",
 "license":LIC,
 "license_url":HOME,
 "source_page":page,
 "markers":[],
 "photo_status":"REAL PHYSICALLY STORED credited copyrighted Selected Monocots original; no microscopic fake arrows; PROVISIONAL USER PHOTO REVIEW PENDING."
 }
 s["images"].append(record)
 s["visual_comparison"]["items"].append(panel)
 g["visual_comparison"]["items"].append(dict(panel))
 report["photos"].append({"original_id":ident,"source":url,"source_page":page,
   "physical_file":str(target),"source_sha256":src_hash,"archived_sha256":sha,"bytes":len(data),"dimensions":dims})
assert len(s["images"])==7 and len(s["visual_comparison"]["items"])==10
assert len(g["visual_comparison"]["items"])==10
assert all(s.get(key)==v for key,v in prior_science.items())
s["curation_status"]["photo_metadata_count"]=7
s["curation_status"]["photo_files_present"]=7
s["curation_status"]["limnodea_six_original_regional_20261023"]={
 "new_real_stored_images":6,"local_species_images":7,"species_panels":10,"genus_panels":10,
 "original_species_photo_retained":True,
 "fine_lemma_tooth_awn_origin_photo_verification":"PROVISIONAL, pixel checks pending",
 "taxonomy_native_flags_preserved":True,
 "stage":"FIELD_READY_PHOTO_GAPS"
}
s["field_id_finish_pass"]["regional_source_originals_20261023"]={
 "archived_photo_codes":[d[0] for d in DATA],
 "scientific_educational_reuse":HOME,
 "source_hash_report":str(REPORT),
 "target_photo_structure":"Look for 1 fertile floret, two stiff subequal glumes, lemma with TWO terminal teeth and ONE awn from the notch; compare exactly one lemma against the 3-limbed awn of Aristida.",
 "final_microscopy_holds":[
 "True locally vouchered fibrous-rooted mature annual with attached whole panicle and matched leaves",
 "One exact same-specimen 3–4 mm entire spikelet with 1-mm ruler; glumes and single floret independently arrowed",
 "One true dissected lemma showing BOTH terminal teeth and ONE awn exactly arising BETWEEN, 10–20× with 1 mm scale and source verified",
 "A true leaf collar closeup with one attached opened 1–2 mm membrane free edge calibrated on the original photo"
 ],
 "photo_status":"FIELD_READY_PHOTO_GAPS: substantial real species evidence, not complete provenance-matched micro photos"
}
s["visual_comparison"]["title"]="Ozarkgrass — real Central Texas anatomy and three look-alike grasses"
s["visual_comparison"]["subtitle"]="Seven original locally stored species JPEGs: one existing iNaturalist (CC BY-NC), six Bob Harms original scientific/educational credited photographs (copyrighted, NOT CC). Original authentic photographed scales preserved; no guessed mm measurements."
g["visual_comparison"]["title"]=s["visual_comparison"]["title"]
g["visual_comparison"]["subtitle"]=s["visual_comparison"]["subtitle"]
g["curation_status"]["limnodea_regional_photo_upgrade_20261023"]={
 "new_physically_archived_jpegs":6,"genus_panels":10,"fine_anatomy_1mm_gap_preserved":True,"county_native_evidence_unchanged":True}
SP.write_text(json.dumps(s,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
GENUS.write_text(json.dumps(g,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
REPORT.parent.mkdir(parents=True,exist_ok=True)
REPORT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
RELEASE.parent.mkdir(parents=True,exist_ok=True)
RELEASE.write_text(json.dumps({
"type":"manual_field_id_publication","species":"Limnodea arkansana","date":"2026-10-23",
"photo_report":str(REPORT),"new_original_files":6,"stored_total":7,
"species_panels":10,"genus_panels":10,
"rights":"6 exact Bob Harms Selected Monocots originals; credited scientific/educational use ONLY, not CC",
"status":"FIELD_READY_PHOTO_GAPS","publication":"GitHub Pages trigger; only later assert deployment if both site jobs success"
},indent=2)+"\n")
print("SUCCESS: exactly six authentic source-verified Bob Harms Ozarkgrass JPEGs",flush=True)
