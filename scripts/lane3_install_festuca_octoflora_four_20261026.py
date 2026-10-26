#!/usr/bin/env python3
"""Lane 3: preserve old Festuca octoflora card and archive four exact-source CC BY photos.
The iNaturalist accepted taxon is Festuca octoflora, matching Kew; Vulpia is a synonym.
Archived photo roles deliberately avoid asserting roots, ligules or measured glume veins.
"""
import hashlib, io, json, pathlib, urllib.request
from PIL import Image,ImageOps
BASE=pathlib.Path("content/taxa/Poaceae/Festuca/festuca-octoflora")
CARD=BASE/"species.json"
EVID=pathlib.Path("reports/lane3-festuca-octoflora-photo-scout-20261026.json")
REPORT=pathlib.Path("reports/lane3-festuca-octoflora-four-installed-20261026.json")
# (exact iNaturalist photo id, observation id, author, caption, label, teaching role)
PICK=[
 (732815110,399420327,"LM Cunningham",
  "A small, source-identified flowering annual grass growing in the dry rocky soil. The narrow flowering branches remain attached to the visible low leaves; the hidden underground root crown cannot be certified from this in-place view.",
  "SIXWEEKS — living rocky-soil flowering tuft",
  "Whole plant in habitat, narrow flowering stems and visible low leafy growth; soil conceals roots"),
 (732815223,399420327,"LM Cunningham",
  "Source-identified plant gently held near the low stem/leaf base, with pale fine root-like strands against rocky soil. Confirm those strands are actual attached roots only on direct full-image inspection; no supposed perennial rhizome or measured ligule is asserted.",
  "SIXWEEKS — lower annual base close-up, fibers under review",
  "Close lower plant with possible visible fibrous roots and connected pale base, subject to full pixel review"),
 (732814759,399420152,"LM Cunningham",
  "Close flower-head photograph shows several pale-green to dry, overlapping, long-awned spikelets along attached narrow branches beside a fingertip. Finger is not a millimeter ruler; this is whole spikelet and projecting-awn recognition only.",
  "SIXWEEKS — attached awned spikelets beside fingertip",
  "Mature awned multi-flowered whole spikelets and terminal bristle-like awns"),
 (732814829,399420152,"LM Cunningham",
  "Source-linked small dry grass flowering unit photographed between fingertips. The visible pale overlapping bracts supply useful gross comparison, but their glume identity, 1-versus-3 veins and awn base are not resolved or measured without an actual mm scale.",
  "SIXWEEKS — small flower-unit macro, glumes NOT measured",
  "Whole small pale flowering part held for context; microscopic glume/lemma diagnosis still missing")
]
AGENT="HaysCountyBotany/1.0 (noncommercial CC BY source photography archival for crew botanical ID)"
def get(url):
 req=urllib.request.Request(url,headers={"User-Agent":AGENT,"Accept":"application/json,image/jpeg"})
 with urllib.request.urlopen(req,timeout=40) as response: payload=response.read(18_000_001)
 if len(payload)>18_000_000:raise ValueError("Oversized original image")
 return payload
def api(url):return json.loads(get(url))
card=json.loads(CARD.read_text(encoding="utf-8"))
e=json.loads(EVID.read_text(encoding="utf-8"))
assert card["id"]=="festuca-octoflora" and card["scientific_name"]=="Festuca octoflora" if "scientific_name" in card else card["id"]=="festuca-octoflora"
assert len(card["images"])==3 and len(card["visual_comparison"]["items"])==6
assert e["inat_taxon_id"]==77141 and e["canonical_name"]=="Festuca octoflora" and not e["failures"]
assert sum("NC" in x.get("license","") for x in card["images"])==1
old_images=card["images"];old_panels=card["visual_comparison"]["items"]
hold={k:json.dumps(card.get(k),sort_keys=True) for k in ("taxonomy_source","morphology_keys","field_id_references","comparisons")}
obs_cache={}
photo_records=[];panels=[];byte_files={};audit=[]
for pid,oid,author,caption,label,role in PICK:
 candidate=next(x for x in e["candidate_photos"] if x["photo_id"]==pid and x["observation_id"]==oid)
 assert candidate["license_code"]=="cc-by" and author.lower() in (candidate["attribution"] or "").lower()
 assert candidate.get("source_sha256")
 if oid not in obs_cache:
  reply=api(f"https://api.inaturalist.org/v1/observations/{oid}")
  assert len(reply.get("results",[]))==1
  o=reply["results"][0]
  assert o["id"]==oid and o["quality_grade"]=="research"
  assert o["taxon"]["id"]==77141 and o["taxon"]["name"]=="Festuca octoflora"
  obs_cache[oid]=o
 photo=next(p for p in obs_cache[oid]["photos"] if p["id"]==pid)
 assert photo.get("license_code")=="cc-by" and author.lower() in (photo.get("attribution") or "").lower()
 raw_url=f"https://inaturalist-open-data.s3.amazonaws.com/photos/{pid}/original.jpg"
 raw=get(raw_url)
 assert hashlib.sha256(raw).hexdigest()==candidate["source_sha256"],"Source content changed since license/contact review"
 with Image.open(io.BytesIO(raw)) as im:
  assert im.format=="JPEG"
  im.verify()
 with Image.open(io.BytesIO(raw)) as im:
  im=ImageOps.exif_transpose(im).convert("RGB")
  assert min(im.size)>=900
  dims=[im.width,im.height]
  im.thumbnail((1850,1850),Image.Resampling.LANCZOS)
  b=io.BytesIO();im.save(b,"JPEG",quality=90,optimize=True);processed=b.getvalue()
 with Image.open(io.BytesIO(processed)) as im:
  assert im.format=="JPEG" and not im.getexif().get(34853)
  im.verify()
 rel=f"images/festuca-octoflora-inat-{pid}-ccby.jpg"
 filename=BASE/rel
 assert not filename.exists()
 byte_files[filename]=processed
 digest=hashlib.sha256(processed).hexdigest()
 photo_url=f"https://www.inaturalist.org/photos/{pid}"
 observation_url=f"https://www.inaturalist.org/observations/{oid}"
 common={
  "creator":author,"license":"CC BY","license_url":"https://creativecommons.org/licenses/by/",
  "source_page":photo_url,"observation_source":observation_url,
  "source_recorded_attribution":photo.get("attribution"),
  "photo_source_id":pid,"source_observation_id":oid}
 photo_records.append(dict(common,**{"file":rel,"role":role,"source_taxon":"Festuca octoflora (synonym Vulpia octoflora), iNaturalist research-grade source determination; individual plant not independently herbarium-vouchered",
  "source_original_url":raw_url,"source_original_sha256":candidate["source_sha256"],
  "local_sha256":digest,"original_dimensions":dims,
  "photo_reuse":"CC BY photo-level checked 2026-10-26, version not independently verified from API short code",
  "modifications":"Re-encoded/resized JPEG, all EXIF/GPS removed, no baked-in arrows",
  "photo_status":"REAL CC BY SOURCE ORIGINAL ARCHIVED; gross visible roles screened on contact sheet; final anatomy arrow review pending"}))
 panels.append(dict(common,**{
  "label":label,"scientific_name":"Festuca octoflora",
  "image_url":str(filename),"image_fit":"contain","image_role":role,
  "caption":caption,"why_it_matters":"Real exact-source species photograph; use habitat and attached awned spikelet without claiming hidden or microscopic anatomy.",
  "photo_status":"Individual CC BY source and full JPEG archived, anatomy overlays pending actual full-resolution inspection",
  "markers":[]}))
 audit.append({"photo_id":pid,"observation_id":oid,"creator":author,
  "license":"CC BY","source_original_sha256":candidate["source_sha256"],
  "archived_sha256":digest,"file":str(filename),"dimensions":dims,"source_page":photo_url})
assert len(panels)==4
card["images"]=old_images+photo_records
card["visual_comparison"]["items"]=panels+old_panels
card["visual_comparison"]["title"]="Sixweeks fescue — living annual, fibrous-base context and awned spikelet ID"
card["visual_comparison"]["subtitle"]="Four newly archived source-identified CC BY dry-habitat plant/base/spikelet originals, then three prior local images and three prior licensed linked sources, including two copyrighted Bob Harms Central Texas references. Root/ligule microscopic verification remains open."
card["visual_comparison"]["overlay_note"]="2026-10-26 Lane 3: archived four accepted Festuca octoflora (Vulpia synonym) source-checked iNaturalist CC BY full originals, with verified source original SHA, photo author and observation IDs. No uninspected arrows. Previous 3 local image files, NC attribution, two CC BY-SA originals, all six original panels/arrows and two Bob Harms copyrighted external educational references preserved. Underground roots, measured true ligule and dissected 1-vs-3 glume veins remain explicit gaps."
tiles=card["field_id_short_tiles"]
assert len(tiles)==6
for t in tiles:
 t["photo_panel_indices"]=[i+4 for i in t.get("photo_panel_indices",[])]
tiles[0]["photo_panel_indices"]=[0,1,4,7,8]
tiles[0]["details"]="New real source-identified plant photographed growing in rocky ground (panel 1) and actual hand-held lower leafy/base view (panel 2) teach the very small annual bunch and possible fibrous root area; these do NOT independently prove attached excavated fibrous roots. Existing Matt Lavin living plant is now panel 5, existing Harms complete dry rooted whole plant is panel 9 and remains a credited REMOTE educational reference with no derivative rights claimed. A true native-range same-specimen rooted fresh annual remains desirable."
tiles[0]["status"]="NEW TRUE LIVING AND LOWER BASE PHOTOS; EXPOSED CONNECTED ROOTS STILL NEED VERIFICATION"
tiles[1]["photo_panel_indices"]=[2,6,9]
tiles[1]["details"]="New close head (panel 3) shows real narrow long-awned whole spikelets; existing true dry head (panel 7) and copyrighted Harms close-up (panel 10) help teach the clustered florets, but three source images cannot yet prove a measured 5–17-floret count."
tiles[2]["photo_panel_indices"]=[3,5,9]
tiles[2]["details"]="New tiny pale flowering-unit view (panel 4) is NOT sufficient to separately identify lower one-veined versus upper three-veined glume. Distinguish the slender terminal awn from pointed glume edges with fresh, dissected and backlit ripe spikelets at mm scale."
tiles[3]["photo_panel_indices"]=[2,3,5,6,9]
tiles[4]["photo_panel_indices"]=[]
tiles[5]["photo_panel_indices"]=[0,1,2,4,5,6,7]
card["field_id_finish_pass"]["stage"]="FIELD_READY_PHOTO_GAPS — four new genuine CC BY field/base and spikelet original photographs added and older educational Bob Harms roots reference retained. True same-plant exposed roots, calibrated free ligule and separated veined glumes NOT proven."
card["field_id_finish_pass"]["lane3_four_new_public_ccby_20261026"]={
 "new_real_archived_jpegs":4,"local_species_image_records":7,"species_gallery_panels":10,
 "rights":"Four individually source photo CC BY, old local CC BY-NC and CC BY-SA preserved; Bob Harms copyright-retained REMOTE educational sources unchanged",
 "true_roles":["source-identified small flowering plant in rocky habitat","lower leaf base with possible attached root fibers, needs full pixel inspection","mature awned whole spikelets","small whole reproductive-unit close-up"],
 "still_missing":["Rooted annual same individual with genuinely exposed connected fine roots and attached full flowering head","0.3–1 mm actual inner membranous ligule photographed and measured","Backlit dissected lower 1-veined and upper 3-veined glumes and 5-veined lemma with ruler"],
 "taxonomic_hold":"iNaturalist maps Vulpia octoflora name onto accepted Festuca octoflora source taxon id 77141; no duplicate admission; original native/range flags unchanged",
 "new_arrows":0}
card["curation_status"]["photo_metadata_count"]=7
card["curation_status"]["photo_files_present"]=7
card["curation_status"]["lane3_sixweeks_four_ccby_20261026"]="Four exact source original CC BY images locally archived and ten current gallery panels, roles pending pixel arrow verification, other source rights and science preserved."
if isinstance(card.get("learner_visual_status"),dict):
 card["learner_visual_status"]["image_count"]=7
 card["learner_visual_status"]["status"]="FIELD_READY_PHOTO_GAPS"
assert all(json.dumps(card.get(k),sort_keys=True)==v for k,v in hold.items())
assert len(card["images"])==7 and len(card["visual_comparison"]["items"])==10
assert all(all(isinstance(i,int) and 0<=i<10 for i in t.get("photo_panel_indices",[])) for t in tiles)
for filename,b in byte_files.items():
 filename.parent.mkdir(parents=True,exist_ok=True);filename.write_bytes(b)
CARD.write_text(json.dumps(card,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
REPORT.write_text(json.dumps({"result":"FOUR_REAL_SIXWEEKS_CC_BY_PHOTOS_INSTALLED","scientific_name":"Festuca octoflora","taxon_synonym":"Vulpia octoflora","photos":audit,"new_photo_files":4,"total_species_photo_files":7,"gallery_panels":10,"new_arrows":0,"remaining":["True connected roots","opened measured inner ligule","dissected glumes and lemma veins"],"status":"FIELD_READY_PHOTO_GAPS"},indent=2)+"\n")
print(json.dumps({"result":"FOUR_REAL_SIXWEEKS_CC_BY_PHOTOS_INSTALLED","photo_ids":[v[0] for v in PICK],"total":7}))
