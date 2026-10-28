#!/usr/bin/env python3
"""Add a licensed REAL microscopic genus-level Phalaris anatomy model.

The photograph is P. arundinacea, NEVER P. caroliniana. Keep it outside
the P. caroliniana species-photo inventory so the completeness score cannot
be increased by this comparison.
"""
import hashlib, html, io, json, pathlib, re, urllib.parse, urllib.request
from PIL import Image, ImageOps

ROOT = pathlib.Path("content/taxa/Poaceae/Phalaris")
SCARD = ROOT/"phalaris-caroliniana"/"species.json"
GCARD = ROOT/"genus.json"
DST = ROOT/"anatomy-reference-images"/"phalaris-arundinacea-stefan-spikelet-sl13.jpg"
SOURCE = "https://commons.wikimedia.org/wiki/File:Phalaris_arundinacea_sl13.jpg"
CREATOR = "Stefan.lefnaer"
LICENSE = "CC BY-SA 4.0"
LICENSE_URL = "https://creativecommons.org/licenses/by-sa/4.0/"
REPORT = pathlib.Path("reports/lane5-phalaris-genus-real-spikelet-20261027.json")

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent":"HaysCountyBotanyGrassPhotos/1.0; Wikimedia attribution archive"})
    with urllib.request.urlopen(req, timeout=55) as r: return r.read()

api="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({
    "action":"query","prop":"imageinfo","iiprop":"url|extmetadata",
    "iiurlwidth":"2200","titles":"File:Phalaris arundinacea sl13.jpg","format":"json"})
pages=json.loads(fetch(api))["query"]["pages"]
inf=next(iter(pages.values()))["imageinfo"][0]
md=inf["extmetadata"]
def clean(s): return html.unescape(re.sub(r"<[^>]+>","",s))
lic=clean(md.get("LicenseShortName",{}).get("value",""))
author=clean(md.get("Artist",{}).get("value",""))
description=clean(md.get("ImageDescription",{}).get("value",""))
assert re.sub(r"[^a-z0-9]","",lic.lower())=="ccbysa40", ("Unexpected CC license",lic)
assert "stefan.lefnaer" in author.lower(), ("Unexpected photographer",author)
assert "phalaris arundinacea" in description.lower(), ("Exact DIFFERENT-species source identity could not be verified",description[:300])
with Image.open(io.BytesIO(fetch(inf.get("thumburl") or inf["url"]))) as im:
    im.verify()
with Image.open(io.BytesIO(fetch(inf.get("thumburl") or inf["url"]))) as im:
    pic=ImageOps.exif_transpose(im).convert("RGB")
    assert pic.width>=1000 and pic.height>=1000
    pic.thumbnail((2200,2200))
    output=io.BytesIO()
    pic.save(output,"JPEG",quality=90,optimize=True)
    data=output.getvalue()
with Image.open(io.BytesIO(data)) as im:
    im.verify()
with Image.open(io.BytesIO(data)) as im:
    assert not im.getexif() and not im.info.get("exif")
DST.parent.mkdir(parents=True,exist_ok=True)
if not DST.exists() or DST.read_bytes()!=data: DST.write_bytes(data)
h=hashlib.sha256(data).hexdigest()
sp=json.loads(SCARD.read_text(encoding="utf-8"))
gn=json.loads(GCARD.read_text(encoding="utf-8"))
assert sp["id"]=="phalaris-caroliniana" and gn["name"]=="Phalaris"
assert len(sp["images"])==8, "Target species photos changed: inspect before running; cannot count genus photo as species"
assert not any(x.get("source_page")==SOURCE for x in sp["images"]), "Wrongly inserted other species into P. caroliniana images[]!"
basepanel={
 "label":"DIFFERENT SPECIES · GENUS ANATOMY MODEL — two sterile lemmas in a real dissected spikelet",
 "scientific_name":"Phalaris arundinacea",
 "image_url":DST.as_posix(), "image_fit":"contain",
 "image_role":"REAL photo of a source-authenticated DIFFERENT species, Phalaris arundinacea. Already labelled by photographer with first/second glumes, two distinct reduced sterile lemmas, fertile lemma, palea and ORIGINAL 5-mm photo scale. Genus anatomy ONLY; does not certify P. caroliniana characters or its measured sterile lemmas.",
 "caption":"STUDY PHOTO OF REED CANARYGRASS — NOT CAROLINA CANARYGRASS. Follow the original printed abbreviations: Glu = paired glumes; Lem′ and Lem″ = first and second reduced sterile lemmas; Lem‴ = fertile lemma; Pal = palea. Real original 5-mm scale shown. Use this to understand where to look while dissecting a mature P. caroliniana spikelet; it cannot supply a species-specific sterile-lemma count or measurements.",
 "why_it_matters":"Shows the tiny inner pieces actually separated on a real photographed Phalaris spikelet, making the existing Carolina source-photo plate easier to understand. Compare the development of both reduced sterile lemmas; lesser canarygrass may have one developed lemma and one minute vestige.",
 "creator":CREATOR,"license":LICENSE,"license_url":LICENSE_URL,
 "source_page":SOURCE,"source_taxon_name":"Phalaris arundinacea",
 "source_location":"Lower Austria, Europe; not a Texas specimen",
 "modifications":"Source already contains text arrows and 5-mm scale; locally resized/re-encoded JPG with EXIF/GPS stripped; no extra arrows added",
 "photo_status":"GENUS PHOTO MODEL ONLY — source/rights and visible labelled scale verified; WRONG SPECIES if treated as P. caroliniana",
 "markers":[]
}
pidx=next((i for i,x in enumerate(sp["visual_comparison"]["items"]) if x.get("source_page")==SOURCE),None)
if pidx is None:
    pidx=len(sp["visual_comparison"]["items"])
    sp["visual_comparison"]["items"].append(dict(basepanel))
gidx=next((i for i,x in enumerate(gn["visual_comparison"]["items"]) if x.get("source_page")==SOURCE),None)
if gidx is None:
    gidx=len(gn["visual_comparison"]["items"])
    gn["visual_comparison"]["items"].append(dict(basepanel))
for i in (2,3,5):
    indices=sp["field_id_short_tiles"][i].setdefault("photo_panel_indices",[])
    if pidx not in indices:indices.append(pidx)
sp["field_id_short_tiles"][3]["details"] += (
 " EXTRA ACTUAL GENUS-LEVEL PHOTO MODEL (panel "+str(pidx)+"): a separately photographed, "
 "source-authenticated P. arundinacea spikelet has the two thin reduced sterile lemmas visibly "
 "separated with a real 5-mm scale. THIS IS NOT P. CAROLINIANA and does not fill our species-specific dissection hold."
)
sp["field_id_short_tiles"][3]["status"]="REAL OTHER-SPECIES ANATOMY TEACHING MODEL ADDED; EXACT P. CAROLINIANA TWO-LEMMA DISSECTION STILL MISSING"
sp["field_photo_quickcheck"]["featured_photo_panel_indices"].append(pidx) if pidx not in sp["field_photo_quickcheck"]["featured_photo_panel_indices"] else None
sp["field_photo_quickcheck"]["comparison_panel_count"]=2
sp["field_photo_quickcheck"]["photo_count"]=len(sp["visual_comparison"]["items"])
sp["curation_status"]["visual_photo_panels"]=len(sp["visual_comparison"]["items"])
sp["curation_status"]["visual_finish"]="FIELD_READY_PHOTO_GAPS — 8 exact-species archived photos with partial collar and existing opened glume composite; 9 gallery panels include two explicitly different-species comparisons. Source-verified CC BY-SA macro of P. arundinacea teaches TWO sterile lemmas by real photograph at original 5-mm scale but MUST NOT be scored as P. caroliniana proof. Exact species root, true measured ligule and separately dissected sterile lemmas remain missing."
sp["learner_visual_status"]["note"]=(
 "8 archived same-species JPEGs, 7 exact species teaching panels and 2 explicitly DIFFERENT species panels "
 "(9 total). New CC BY-SA 4.0 Phalaris arundinacea dissected spikelet is a genus-level photo model, NOT an additional exact species image. "
 "Original 5-mm scale and printed anatomical labels intact. Root system and isolated two P. caroliniana sterile lemmas remain missing. "
 "Source-local copyright status of existing Bob Harms images unaltered; Pages not independently verified.")
sp["lane5_phalaris_genus_dissected_photo_model_20261027"]={
 "status":"FIELD_READY_PHOTO_GAPS", "source":SOURCE,"creator":CREATOR,"license":LICENSE,
 "local_ref":DST.as_posix(), "sha256":h,
 "species_gallery_index":pidx,"genus_gallery_index":gidx,
 "source_taxon":"Phalaris arundinacea","target_taxon":"Phalaris caroliniana",
 "correct_label":"GENUS LEVEL DIFFERENT SPECIES ANATOMY", "new_exact_species_photos":0,
 "species_photo_roles_cleared":0, "new_markers":0, "printed_labels_and_mm_scale":True,
 "remaining":["P. caroliniana rooted attached flowering specimen","P. caroliniana measured inner ligule","P. caroliniana isolated both small sterile lemmas with calibrated scale"]}
gn["visual_status"]="FIELD_READY_PHOTO_GAPS — real open-license labeled 5-mm-scale Phalaris arundinacea dissections now available strictly for GENUS anatomy teaching. Species-specific P. caroliniana vs P. minor sterile-floret dissection unresolved."
SCARD.write_text(json.dumps(sp,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
GCARD.write_text(json.dumps(gn,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
manifest={"date":"2026-10-27","scope":"GENUS TEACHING REAL PHOTOGRAPH — NOT EXTRA SPECIES PHOTO",
 "source_page":SOURCE,"source_taxon":"Phalaris arundinacea","target_taxon":"Phalaris caroliniana",
 "photographer":CREATOR,"license":LICENSE,"license_url":LICENSE_URL,
 "local_image":DST.as_posix(),"source_url":inf["url"],"width":pic.width,"height":pic.height,
 "bytes":len(data),"sha256":h,
 "observed":"Original photographed dissection shows glumes, both narrow sterile lemmas, fertile lemma, palea, original 5-mm scale; no new arrows created",
 "same_species_photo_count":len(sp["images"]),"species_gallery_total":len(sp["visual_comparison"]["items"]),
 "species_gallery_index":pidx,"genus_gallery_index":gidx,"additional_species_photo_roles":0,
 "rights_caution":"CC BY-SA 4.0 credit/share-alike and modification notice required; original labels retained"}
REPORT.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
(DST.parent/"SOURCES.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps(manifest))
