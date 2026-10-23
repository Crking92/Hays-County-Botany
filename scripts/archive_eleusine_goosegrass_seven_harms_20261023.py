#!/usr/bin/env python3
"""Install seven real, author permitted Eleusine indica scientific anatomy
originals into the public learner. Do not revise old CC BY-NC-SA grant.
No asserted root-to-floret one-voucher collection nor fake millimeter scales.
"""
from pathlib import Path
import hashlib,io,json,time,requests
from PIL import Image,ImageOps

ROOT=Path("content/taxa/Poaceae/Eleusine")
SP=ROOT/"eleusine-indica/species.json"
GP=ROOT/"genus.json"
REPORT=Path("reports/eleusine-indica-seven-harms-originals-20261023.json")
RELEASE=Path("workflow/field-id-publication/2026-10-23-eleusine-indica-seven-true-harms-anatomy.json")
BASE="https://w3.biosci.utexas.edu/prc/Monocots/GrassHTML/data/"
HOME="https://w3.biosci.utexas.edu/prc/Monocots/"
PERMIT="BOB_HARMS_SELECTED_MONOCOTS_EDU_WITH_CREDIT_20261022"
LIC="© Bob Harms — scientific/educational use with attribution (NOT Creative Commons)"
ROWS=[
 ("ELIN3-b","ROOT/CROWN RECOGNITION: original source-labelled whole goosegrass plant",
  "True original regional goosegrass plant; use the pale/flattened crown where visibly shown. Do not assume every basal tiller is demonstrably unrooted or connected to a root in this photograph."),
 ("ELIN3-I","FLOWERING STAGE: entire digitate goosegrass head",
  "Actual photographed goosegrass blooming inflorescence. Several rigid fingerlike branches make a radiating head; some lower branch positions may vary. Do not confuse ONE branch with ONE spikelet."),
 ("ELIN3-i1","RACEME CLOSEUP: flat zipper rows of awnless spikelets",
  "A close goosegrass source photo of reproductive branches. Many compressed awnless spikelets are pressed against a stout rachis, each with several florets within."),
 ("ELIN3-j1","FLOWERING CLOSE: real crowded awnless units",
  "Botanically source-verified goosegrass flowering detail. Any small pollen organs are teachable only where visibly and independently resolvable."),
 ("ELIN3-J2","FLOWERING MACRO: real attached spikelets and flower parts",
  "Original source-referenced attached flowering units; use for real floret/spikelet architecture rather than counting every awnless lemma as a separate spikelet."),
 ("ELIN3-9","SPIKELET DETAIL: original microscopic or dissected reproduction",
  "Original Bob Harms goosegrass spikelet detail, labelled and source-verified. One compressed spikelet contains several florets, protected by a pair of outer glumes. Any fine part arrows require later inspection of actual original pixels."),
 ("ELIN3-L","LEAF SHEATH & TRUE LIGULE: real collar macro",
  "Original botanically source-verified goosegrass collar and ligule region. A short membranous ligule, with sometimes jagged/notched edge, differs from bermudagrass's hair-fringe; do NOT confuse nearby longer hairs with the actual membrane. No one-voucher mm-scale true membrane measurement claimed.")
]
sp=json.loads(SP.read_text(encoding="utf-8"))
g=json.loads(GP.read_text(encoding="utf-8"))
assert sp["scientific_name"]=="Eleusine indica" and sp["id"]=="eleusine-indica"
assert len(sp["images"])==1 and sp["curation_status"]["photo_files_present"]==1
assert len(sp["visual_comparison"]["items"])==7 and len(g["visual_comparison"]["items"])==7
assert sp["images"][0]["license"]=="CC BY-NC-SA"
assert sp["public_photo_audit"] is not None
assert "FIELD_READY_PHOTO_GAPS" in sp["field_id_finish_pass"]["stage"]
SCIENTIFIC_FIELDS=["taxonomy_source","morphology_keys","comparisons","field_id_sources","public_photo_audit","learner_visual_status"]
snapshot={key:sp.get(key) for key in SCIENTIFIC_FIELDS}
old_panel=sp["visual_comparison"]["items"][0].copy()
old_genus_panel=g["visual_comparison"]["items"][0].copy()
session=requests.Session()
session.headers.update({"User-Agent":"HaysCountyBotany-CreditedCentralTexasEleusineOriginals/1.0","Accept":"image/jpeg,image/*;q=0.9"})
photos=SP.parent/"images";photos.mkdir(parents=True,exist_ok=True)
report={"species":"Eleusine indica","prior_local_jpegs":1,
 "legacy_image_hold":"Original image CC BY-NC-SA retained as historical study-only, not publicly authorized",
 "harms_license":"Seven exact Bob Harms author-photographed Central Texas original images, copyrighted educational/scientific with attribution; NOT CC",
 "source_collection":HOME,"new_originals":0,"images":[],"same_specimen_sequence":False}
for ident,title,caption in ROWS:
 url=BASE+"images/"+ident+".jpg"
 page=BASE+"pages/"+ident+".html"
 fn="bob-harms-goosegrass-"+ident.lower()+".jpg"
 path=photos/fn
 if path.exists():raise RuntimeError("Will not overwrite pre-existing image: "+str(path))
 last=None
 for attempt in range(3):
  try:
   r=session.get(url,timeout=38);r.raise_for_status()
   raw=r.content
   if len(raw)<4300 or not raw.startswith(bytes.fromhex("ffd8ff")):raise ValueError("Not original JPEG bytes")
   with Image.open(io.BytesIO(raw)) as im:
    im.load()
    if im.format!="JPEG" or min(im.size)<45:raise ValueError("Bad source image (some original microscopy JPEGs are narrow)")
    clear=ImageOps.exif_transpose(im).convert("RGB")
    dims=list(clear.size)
   clear.save(path,format="JPEG",quality=93,optimize=True)
   original_sha=hashlib.sha256(raw).hexdigest()
   report["new_originals"]+=1
   break
  except (OSError,requests.RequestException,ValueError) as error:
   last=str(error)
   if attempt<2:time.sleep(3*(attempt+1))
 else:raise RuntimeError("Cannot validate original "+ident+": "+last)
 data=path.read_bytes()
 with Image.open(path) as im:
  assert im.format=="JPEG" and im.mode=="RGB" and list(im.size)==dims and not im.getexif().get(34853)
  im.verify()
 sha=hashlib.sha256(data).hexdigest()
 record={
  "file":"images/"+fn,"role":title,
  "creator":"Bob Harms","license":LIC,"license_url":HOME,
  "source_page":page,"source_image":url,
  "source_taxon_name":"Eleusine indica",
  "site_specific_public_permission":PERMIT,
  "public_reuse":"YES, source-specific original copyrighted author educational/scientific permission WITH Bob Harms credit; NOT CC",
  "photo_review":"PROVISIONAL user photo review; true original source verified, 1mm organ-level arrow targets not yet independently certified; separate sources not necessarily same rooted plant",
  "archive_sha256":sha,"source_sha256":original_sha,"image_dimensions":dims,
  "modifications":"Original uncropped RGB pixels saved at source dimensions, re-encoded JPEG with all EXIF/GPS stripped; source photographer copyright and license preserved."
 }
 panel={
  "label":title,
  "scientific_name":"Eleusine indica",
  "image_url":str(path),"image_fit":"contain",
  "image_role":title,"caption":caption,
  "why_it_matters":"True Central Texas source-identified anatomy available directly on the website, complementing the three earlier externally linked Harry Rose CC BY photographs, with independent original verification.",
  "creator":"Bob Harms","license":LIC,"license_url":HOME,
  "source_page":page,
  "photo_status":"Physically archived genuine original under credited educational copyright permission; individual micro-arrows pending original-pixel inspection. PROVISIONAL USER PHOTO REVIEW.",
  "markers":[]
 }
 sp["images"].append(record)
 sp["visual_comparison"]["items"].insert(4,panel)
 g["visual_comparison"]["items"].insert(4,dict(panel))
 report["images"].append({"source_code":ident,"source_image":url,"source_page":page,
   "local_file":str(path),"source_sha256":original_sha,"sha256":sha,"dimensions":dims,"bytes":len(data)})
assert report["new_originals"]==7 and len(sp["images"])==8
assert len(sp["visual_comparison"]["items"])==14 and len(g["visual_comparison"]["items"])==14
assert sp["visual_comparison"]["items"][0]==old_panel and g["visual_comparison"]["items"][0]==old_genus_panel
assert all(sp.get(k)==v for k,v in snapshot.items()),"Taxonomy, comparisons, rights hold or other source records changed"
sp["curation_status"]["photo_metadata_count"]=8
sp["curation_status"]["photo_files_present"]=8
sp["curation_status"]["eleusine_harms_seven_20261023"]={
  "new_exact_species_real_jpegs":7,"local_total_including_legacy_hold":8,
  "new_public_eligible_exact_species_originals":7,"species_panels_total":14,"genus_panels_total":14,
  "old_legacy_nc_sa_photo_rights_unchanged":True,
  "new_image_originals_rights":"source-specific Bob Harms educational use with credit; NOT CC",
  "micro_anatomy_arrows_verified":False,"status":"FIELD_READY_PHOTO_GAPS"
 }
sp["field_id_finish_pass"]["harms_seven_actual_photos_20261023"]={
  "original_source_photo_ids":[x[0] for x in ROWS],"source_hash_report":str(REPORT),
  "micro_gaps":["One same-plant true rooted crown and folded bud section with ruler",
                "1mm actual opened free jagged ligule membrane with physical scale",
                "Measured ripe whole multi-floret goosegrass spikelet with individually confirmed two glumes, 3–9 florets and seed",
                "One verified local in-situ source voucher from crown/collar to paired flat racemes and dissected floret"],
  "photo_rights_note":"Seven new site-eligible author-permitted original photographs. Existing 1 NC-SA image is retained but NOT counted as public eligible and its hold is unchanged.",
  "stage":"FIELD_READY_PHOTO_GAPS"
 }
sp["visual_comparison"]["subtitle"]="EIGHT physically archived goosegrass originals, of which SEVEN new Bob Harms Central Texas images have credited educational reuse permission and the legacy CC BY-NC-SA has an unresolved public rights hold. Earlier three Harry Rose CC BY Commons references still externally linked. Three other-grass comparison panels remain clearly identified."
sp["visual_comparison"]["overlay_note"]="Genuine Eleusine panels: one older local CC BY-NC-SA historical study-only photo, three credited externally linked Harry Rose CC BY source references, seven NEW actually stored Bob Harms copyrighted educational-use-with-credit originals. Remaining three panels depict other species for comparison. No site-wide grant to republish the older NC-SA original inferred."
g["visual_comparison"]["subtitle"]=sp["visual_comparison"]["subtitle"]
g["visual_comparison"]["overlay_note"]=sp["visual_comparison"]["overlay_note"]
g["curation_status"]["eleusine_harms_seven_originals_20261023"]={
 "new_real_exact_species_images":7,"local_species_total":8,"panels_total":14,
 "old_nc_sa_rights_hold_preserved":True,"fine_mm_ligule_photo_hold":True,"status":"FIELD_READY_PHOTO_GAPS"
}
SP.write_text(json.dumps(sp,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
GP.write_text(json.dumps(g,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
REPORT.parent.mkdir(parents=True,exist_ok=True)
REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
RELEASE.parent.mkdir(parents=True,exist_ok=True)
RELEASE.write_text(json.dumps({
 "type":"manual_field_id_publication","date":"2026-10-23","species":"Eleusine indica",
 "new_photographs":7,"total_physically_stored_originals":8,
 "site_eligible_originals_new":7,"legacy_cc_by_nc_sa_public_hold":"UNCHANGED",
 "species_panels_total":14,"genus_panels_total":14,
 "photo_report":str(REPORT),"new_license":"Bob Harms exact originals attributed scientific/educational use NOT CC",
 "state":"FIELD_READY_PHOTO_GAPS","publication":"Requires explicit site build + deploy SUCCESS before live claim"
},indent=2)+"\n",encoding="utf-8")
print("PASS: 7 true source-authenticated copyrighted credited educational Eleusine originals, legacy NC-SA held",flush=True)
