#!/usr/bin/env python3
"""Lane 3: archive only two photo-ID-confirmed Texas sixweeks fescue JPEGs.
Also reuse two existing CC BY Texas fescue diagnostic photos as other-species
comparators. Preserve current NC, BY-SA, Harms remote permissions and holds.
Photo source is iNaturalist Research Grade; no independent herbarium-voucher claim.
"""
import io,json,pathlib,hashlib,urllib.request
from PIL import Image,ImageOps
BASE=pathlib.Path("content/taxa/Poaceae/Festuca/festuca-octoflora")
CARD=BASE/"species.json"
REPORT=pathlib.Path("reports/lane3-sixweeks-texas-photo-install-20261026.json")
SCOUT=pathlib.Path("reports/lane3-festuca-octoflora-texas-scout-20261026.json")
COMPARE=pathlib.Path("content/taxa/Poaceae/Festuca/festuca-versuta/species.json")
PHOTOS=[
 (648906204,355831612,"Cleveland Powell","Comfort, Kendall County, Texas",
  "LIVE GREEN TEXAS — young attached awned spikelet branches",
  "Genuine green source-identified flowering shoot in Comfort, Texas, with slender upward-pointing spikelets and delicate projecting awns against a finger. Good LOCAL developmental recognition, not an actual exposed root crown, ligule, or glume dissection."),
 (636299182,348853031,"Eric Knight","Brady, McCulloch County, Texas",
  "MATURE TEXAS — crowded reddish awned flowering heads",
  "Genuine source-identified mature awned heads from Brady, Texas, held against a finger. Shows local older-season overlapping florets and terminal bristles, NOT a measured detached 1- versus 3-veined glume or linked annual root base.")
]
HEADERS={"User-Agent":"HaysCountyBotany/1.0 (noncommercial botany public CC license photo archival; github.com/Crking92/Hays-County-Botany)","Accept":"application/json,image/jpeg"}
def fetch(url):
 req=urllib.request.Request(url,headers=HEADERS)
 with urllib.request.urlopen(req,timeout=45) as f:
  b=f.read(16000001)
 if len(b)>16000000:raise ValueError("Source exceeded limit")
 return b
def api(url):return json.loads(fetch(url))
doc=json.loads(CARD.read_text())
scout=json.loads(SCOUT.read_text())
peer=json.loads(COMPARE.read_text())
assert doc["scientific_name"]=="Festuca octoflora" and peer["scientific_name"]=="Festuca versuta"
assert scout["inat_taxon_id"]==77141 and not scout["failures"] and len(scout["candidate_photos"])>=20
assert len(doc["images"])==8 and len(doc["visual_comparison"]["items"])==10
assert any(x.get("license")=="CC BY-NC" for x in doc["images"])
assert any(x.get("license")=="CC BY-SA 2.0" for x in doc["images"])
assert sum(x.get("creator")=="Bob Harms" for x in doc["visual_comparison"]["items"])==2
scientific={k:json.dumps(doc.get(k),sort_keys=True) for k in ("taxonomy_source","morphology_keys","comparisons","field_id_references")}
newimages=[];newpanels=[];files={};installed=[]
for pid,oid,creator,locality,label,caption in PHOTOS:
 rec=next(x for x in scout["candidate_photos"] if x["photo_id"]==pid and x["observation_id"]==oid)
 assert rec["license_code"]=="cc-by" and creator.lower() in (rec.get("attribution") or "").lower()
 assert rec["preview_status"]=="PHOTO_BYTES_READ_FOR_CONTACT_SHEET" and rec.get("source_sha256")
 assert ("Comfort" in rec["location_coarse"] if pid==648906204 else "Brady" in rec["location_coarse"])
 j=api(f"https://api.inaturalist.org/v1/observations/{oid}")
 assert len(j.get("results",[]))==1
 ob=j["results"][0]
 assert ob["id"]==oid and ob.get("quality_grade")=="research"
 assert ob["taxon"]["name"]=="Festuca octoflora" and ob["taxon"]["id"]==77141
 photo=next(x for x in ob.get("photos",[]) if x["id"]==pid)
 assert photo.get("license_code")=="cc-by" and creator.lower() in (photo.get("attribution") or "").lower()
 url=f"https://inaturalist-open-data.s3.amazonaws.com/photos/{pid}/original.jpg"
 source=fetch(url)
 assert hashlib.sha256(source).hexdigest()==rec["source_sha256"],"Source original differs from rights reviewed original"
 with Image.open(io.BytesIO(source)) as im:
  assert im.format=="JPEG"; im.verify()
 with Image.open(io.BytesIO(source)) as im:
  im=ImageOps.exif_transpose(im).convert("RGB")
  assert min(im.size)>=800
  srcsize=[im.width,im.height]
  im.thumbnail((1900,1900),Image.Resampling.LANCZOS)
  buf=io.BytesIO();im.save(buf,"JPEG",quality=89,optimize=True)
  out=buf.getvalue()
 with Image.open(io.BytesIO(out)) as im:
  assert im.format=="JPEG" and not im.getexif().get(34853);im.verify()
 rel=f"images/festuca-octoflora-texas-inat-{pid}-ccby.jpg"
 path=BASE/rel
 assert not path.exists() and all(str(pid) not in str(x.get("file","")) for x in doc["images"])
 files[path]=out
 sha=hashlib.sha256(out).hexdigest()
 srcpage=f"https://www.inaturalist.org/photos/{pid}"
 obsurl=f"https://www.inaturalist.org/observations/{oid}"
 newimages.append({"file":rel,"role":"Texas-source in-season attached panicle/spikelet comparison, native target-region context, not connected roots or true ligule",
  "creator":creator,"license":"CC BY","license_code":"cc-by",
  "license_url":"https://creativecommons.org/licenses/by/",
  "license_version_note":"Current iNaturalist photo-specific license code cc-by verified; precise numbered edition not established by short-code API",
  "source_page":srcpage,"source_observation":obsurl,"source_photo_id":pid,"source_observation_id":oid,
  "source_place":locality,"source_place_raw":rec["location_coarse"],
  "source_taxon":"iNaturalist Research Grade Festuca octoflora (Vulpia octoflora), source-determined; herbarium voucher unverified",
  "source_original_url":url,"source_original_sha256":rec["source_sha256"],"archive_sha256":sha,"source_dimensions":srcsize,
  "modifications":"Resized to fit within 1900 px and recompressed as JPEG; EXIF/GPS removed; no baked-in annotation arrows",
  "photo_status":"CC BY LICENSED EXACT-SOURCE TEXAS JPEG LOCAL; new gross-character arrows pending original pixel review; NOT ROOT/LIGULE PROOF"})
 newpanels.append({"label":label,"scientific_name":"Festuca octoflora",
  "image_url":str(path),"image_fit":"contain",
  "image_role":"Actual field-sourced narrow attached awned heads in native target zone; immature green versus mature rusty seasonal comparison",
  "caption":caption,"why_it_matters":"Locally relevant native-range source photos of fresh and mature attached awned reproductive architecture. Does not substitute for a connected fibrous crown, measured true ligule or dissected two glumes.",
  "creator":creator,"license":"CC BY","license_url":"https://creativecommons.org/licenses/by/",
  "source_page":srcpage,"observation_source":obsurl,"source_place":locality,
  "photo_status":"Original inspected on Texas CC BY source contact sheet, full downloaded file SHA preserved; no speculative glume/ligule/root arrows",
  "markers":[]})
 installed.append({"photo_id":pid,"observation_id":oid,"creator":creator,"license":"CC BY",
  "source_page":srcpage,"source_place":locality,"local_file":str(path),
  "source_sha256":rec["source_sha256"],"archived_sha256":sha})
peer_panel={}
for id,tag in [(654445773,"habit"),(367035946,"spikelet")]:
 x=next((p for p in peer["visual_comparison"]["items"] if str(id) in p.get("image_url","")),None)
 assert x and x["scientific_name"]=="Festuca versuta"
 assert x["license"]=="CC BY" and pathlib.Path(x["image_url"]).is_file()
 peer_panel[tag]=x
differents=[]
for tag,label,text in [
 ("habit","DIFFERENT SPECIES — perennial Texas fescue growing leaves",
  "Texas fescue photo from a research-grade exact-species source observation; a living clump with broader leaf blades. Actual perennial lifespan or deeply established crown CANNOT be proven by aboveground photographs alone. Compare with tiny sixweeks plant size and crowded flowering heads."),
 ("spikelet","DIFFERENT SPECIES — Texas fescue multi-flowered spikelet",
  "Texas fescue has shorter usually few-flowered spikelets in its published treatment, often without a long projecting awn, unlike sixweeks fescue's crowded often 5–17-flowered awned units. This source photograph is a whole spikelet, not a calibrated dissection or independently counted florets.")
]:
 q=peer_panel[tag]
 differents.append({"label":label,"scientific_name":"Festuca versuta",
  "image_url":q["image_url"],"image_fit":"contain",
  "image_role":"DIFFERENT SPECIES: same-lane Texas fescue comparative species ID, not sixweeks fescue plant",
  "caption":text,"why_it_matters":"Teaches difference in mature head, whole awned units and growth form; no falsely labeled ligule or roots.",
  "creator":q["creator"],"license":q["license"],"license_url":q["license_url"],"source_page":q["source_page"],
  "photo_status":"Existing exact-source image physically archived under F. versuta; photo reused by local reference only, no duplicate bytes, no newly invented anatomy arrows",
  "markers":[]})
old=doc["visual_comparison"]["items"]
doc["images"].extend(newimages)
doc["visual_comparison"]["items"]=newpanels+old+differents
doc["visual_comparison"]["title"]="Sixweeks fescue — TEXAS green-to-mature awned heads, living annual and perennial comparison"
doc["visual_comparison"]["subtitle"]="Two new physically archived CC BY target-range Texas photo IDs from Comfort and Brady lead eight older source photos; two further panels reuse exactly-credited perennial Texas fescue photographs for a genuine different-species comparison. Bob Harms source roots remain COPYRIGHT-RETAINED EXTERNAL-only; free membrane and locally attached exposed roots still missing."
doc["visual_comparison"]["memory_rule"]="Annual sixweeks: small one-season plant, narrowly crowded AWNED spikelets usually with multiple florets. Texas fescue: a perennial with a looser flowering panicle and relatively few florets, often lacking extended awns. A single dead tuft is not sufficient proof of life cycle."
doc["visual_comparison"]["overlay_note"]="2026-10-26 Lane 3: new native target zone Texas exact-source individually CC BY photo IDs 648906204 and 636299182, downloaded byte original hashes recorded, EXIF/GPS stripped and publicly archived. Two older F. versuta CC BY species photographs reused without binary duplication as explicit DIFFERENT SPECIES comparison panels. All ten original sixweeks panels/annotation coordinates preserved in original sequence +2; Bob Harms copyrighted photographs remain external educational-use only, source NC and BY-SA photos preserved. New gross-photo arrows await full file pixel QA. Root crown/short inner ligule remain not photographed."
tiles=doc["field_id_short_tiles"]
assert len(tiles)==6
for tile in tiles:
 tile["photo_panel_indices"]=[i+2 for i in tile["photo_panel_indices"]]
tiles[0]["photo_panel_indices"]=[0,1]+tiles[0]["photo_panel_indices"]
tiles[0]["details"]="NATIVE TARGET ZONE: gallery photo 1 Cleveland Powell's green source-identified attached flowering head from Comfort, Kendall County, photo 2 Eric Knight's ripe rust-tan tight heads from Brady, McCulloch County. Both are exact-source and individually CC BY. Gallery photo 3 has the original California tiny live aboveground tuft; photo 7 Matt Lavin's Utah standing plant; photo 11 is Bob Harms' credited external Central Texas collected dried annual with visible roots. Neither new Texas photo exposes roots or proves perennial-vs-annual anatomy.";
tiles[0]["status"]="TEXAS FLOWERING STAGES PHOTOGRAPHED; CONNECTED TRUE ROOT BASE STILL MISSING"
tiles[1]["photo_panel_indices"]=[0,1]+tiles[1]["photo_panel_indices"]
tiles[1]["details"]="Local Texas-source fresh and ripe sixweeks awned heads are now in panels 1–2, others in panels 4–5 and 8; compare with entirely DIFFERENT species Texas fescue (gallery 14) before counting and dissecting a mature 5–17-flowered sixweeks spikelet. Finger photos are NOT mm-calibrated floret measurements.";
tiles[4]["status"]="TRUE LIGULE STILL MISSING — no aboveground head, open shoot or comparable fescue photograph proves the free 0.5–1 mm membrane"
tiles[5]["photo_panel_indices"]=[0,1]+tiles[5]["photo_panel_indices"]+[12,13]
tiles[5]["details"]="GALLERY 1–2 show actual attached green and ripe sixweeks heads from Comfort and Brady (Texas). GALLERY 13–14 show DIFFERENT SPECIES perennial Texas fescue's living leafy tuft and single mature whole spikelet from existing canonical sources, not sixweeks fescue. Contrast sixweeks annual narrow many-flowered awned heads with Texas fescue open drooping panicle and few-flowered shorter-awns/awnless spikelet. Same-root annual-vs-perennial growth proof and measured dissection remain absent; NEVER count Texas fescue panels as sixweeks source anatomy.";
tiles[5]["status"]="REAL SIDE-BY-SIDE DIFFERENT-SPECIES CC BY PHOTO COMPARISON; ROOT AND LIGULE GAPS HELD"
for tile in tiles:
 assert all(isinstance(i,int) and 0<=i<14 for i in tile["photo_panel_indices"])
doc["field_id_finish_pass"]["lane3_texas_source_two_20261026"]={
 "texas_new_public_jpegs":2,"same_species_archived_files":10,"total_gallery_panels":14,
 "new_photo_ids":[648906204,636299182],"source_places":["Comfort, Kendall County, TX","Brady, McCulloch County, TX"],
 "source_rights":"Individual CC BY photographic codes verified immediately against live source observation IDs 355831612 and 348853031, creator matched; original source SHA matched earlier photo scout.",
 "lookalike":"Two credited physically archived Festuca versuta comparators linked without duplicate local files; clearly DIFFERENT SPECIES; no new arrows.",
 "only_clear_roles":["target-region actual green attached awned flowering head","target-region mature ripe crowding/awned head"],
 "still_missing":["A whole connected flowering Texas-rooted annual with actual exposed fibrous roots and no rhizome","A real short 0.5–1 mm eciliate free inner membranous ligule, opened against mm ruler","Dissected entire spikelet with 1-veined lower / 3-veined upper glume and measured 5-veined awned lemma"],
 "holds":"Original Lee NC and Matt Lavin ShareAlike copyright, Bob Harms exact-site educational remote images and all published taxon fields preserved. No native-by-county inference.",
 "status":"FIELD_READY_PHOTO_GAPS"}
doc["field_id_finish_pass"]["stage"]="FIELD_READY_PHOTO_GAPS — 10 physically archived exact-source sixweeks image records (2 new Texas region) and 14 gallery panels including 2 explicit different-species Texas fescue comparisons; genuine root exposure, opened true ligule and measured dissected glumes still missing."
doc["curation_status"]["photo_metadata_count"]=10
doc["curation_status"]["photo_files_present"]=10
doc["curation_status"]["lane3_texas_source_lesson_20261026"]="Two directly licensed true-species Texas photo source JPEGs archived; 10 local same-species photos and two credited different-species F. versuta panels; science/copyright holds and originals unchanged."
doc["learner_visual_status"]["image_count"]=10
doc["learner_visual_status"]["status"]="FIELD_READY_PHOTO_GAPS"
doc["learner_visual_status"]["note"]="10 real archived sixweeks fescue source JPEGs, including two target-region Texas flowering views, plus two no-duplicate Texas fescue comparison panels among 14 gallery views. Old caption counts were stale. No measured ligule, dissected glumes or actually exposed connected fine roots on a local live plant."
assert all(json.dumps(doc.get(k),sort_keys=True)==v for k,v in scientific.items())
assert len(doc["images"])==10 and len(doc["visual_comparison"]["items"])==14
assert sum(x.get("scientific_name")=="Festuca versuta" for x in doc["visual_comparison"]["items"])==2
assert sum(x.get("creator")=="Bob Harms" for x in doc["visual_comparison"]["items"])==2
for path,payload in files.items():
 path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(payload)
CARD.write_text(json.dumps(doc,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
REPORT.write_text(json.dumps({"result":"TWO_EXACT_TEXAS_CC_BY_SOURCE_JPEGS_ARCHIVED","species":"Festuca octoflora","images":installed,"same_species_local_files":10,"gallery_panels":14,"new_arrow_count":0,"different_species_panels":2,"status":"FIELD_READY_PHOTO_GAPS","holds":["Rooted actual Texas annual with roots showing","Measured true free inner membrane","Independent mature glume lemma cross-sections"]},indent=2)+"\n")
print(json.dumps({"result":"TWO_EXACT_TEXAS_CC_BY_SOURCE_JPEGS_ARCHIVED","photo_ids":[p[0] for p in PHOTOS],"local_count":10,"gallery":14}))
