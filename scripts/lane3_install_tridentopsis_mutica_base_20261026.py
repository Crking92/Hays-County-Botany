#!/usr/bin/env python3
"""Lane 3: add four true source-licensed Tridentopsis mutica habit/base JPEGs.
Source observation taxon/quality and per-photo cc-by + original SHA mandatory.
Preserve existing two Joey CC BY-NC photographs, annotations, comparison and holds.
Never claim exposed rhizomes or true inner ligule from in-situ lower leaf bases.
"""
import hashlib, io, json, pathlib, urllib.request
from PIL import Image, ImageOps
BASE=pathlib.Path("content/taxa/Poaceae/Tridentopsis/tridentopsis-mutica")
CARD=BASE/"species.json"
EVID=pathlib.Path("reports/lane3-tridentopsis-mutica-photo-scout-20261026.json")
REPORT=pathlib.Path("reports/lane3-tridentopsis-mutica-base-install-20261026.json")
PICK=[
(737818961,401967788,"Trevor Van Loon","Field view of low green leafy shoots and narrow flowering culm held near a naturally rooted tuft","FIELD — fine basal shoots plus flowering culm","Source-identified living shoots emerging from a rocky soil-level bunch with nearby contracted flowering culm. This is in-place habitat and flowering context, not a detached/excavated rhizome or root system."),
(640981031,351263223,"Cody Stricker","Living lower tuft and thin stems alongside fingers","BASE — narrow basal blades and sheathing culms","Finger-size field view shows many narrow live grass blades and clustered basal culms in ground. Actual roots, rhizome, and short inner ligule are concealed."),
(640981141,351263223,"Cody Stricker","Close in-situ lower leaf blade and sheath region","BASE CLOSE-UP — true lower leaves and sheaths","A closer view of thin green leaves and their lower sheathing attachment beside a hand. It points to the region to inspect for a tiny ciliate ligule, but the free inner membrane is NOT visibly exposed or measured."),
(614203555,337823336,"Anders Hastings","Whole small grassy bunch in native rocky habitat","WHOLE PLANT — living tuft at rocky soil surface","In-situ perennial-looking bunch photographed beside a rock, showing upright dry culms and a central tuft of leaves. No excavated knotty root crown, rhizome, or proven stolon connection.")
]
AGENT="HaysCountyBotany/1.0 (noncommercial educational source-cited photograph curation)"
def get(url):
 req=urllib.request.Request(url,headers={"User-Agent":AGENT,"Accept":"application/json,image/jpeg"})
 with urllib.request.urlopen(req,timeout=38) as f: v=f.read(16_000_001)
 if len(v)>16_000_000:raise ValueError("Large source file")
 return v
def api(url):return json.loads(get(url))
d=json.loads(CARD.read_text(encoding="utf-8"))
e=json.loads(EVID.read_text(encoding="utf-8"))
assert d["id"]=="tridentopsis-mutica" and d["scientific_name"]=="Tridentopsis mutica"
assert len(d["images"])==3 and len(d["visual_comparison"]["items"])==5
assert e["inat_taxon_id"]==931204 and not e["failures"]
assert sum(x.get("license")=="CC BY-NC 4.0" and x.get("creator")=="Joey Santore" for x in d["images"])==2
preserve={k:json.dumps(d.get(k),sort_keys=True) for k in ("synonyms","taxonomic_note","county_occurrences_target_zone","target_zone_count","native_target_zone_calculated","native_metrics_excluded","project_inclusion")}
obs={}
newimages=[];newpanels=[];bytefiles={};records=[]
for pid,oid,creator,role,label,caption in PICK:
 rec=next(x for x in e["candidate_photos"] if x["photo_id"]==pid and x["observation_id"]==oid)
 assert rec["license_code"]=="cc-by" and creator.lower() in (rec.get("attribution") or "").lower()
 assert rec.get("source_sha256"), "Original source photo must have passed evidence screen"
 if oid not in obs:
  reply=api("https://api.inaturalist.org/v1/observations/"+str(oid))
  assert len(reply.get("results",[]))==1
  o=reply["results"][0]
  assert o["id"]==oid and o.get("quality_grade")=="research"
  assert o["taxon"]["name"]=="Tridentopsis mutica" and o["taxon"]["id"]==931204
  obs[oid]=o
 photograph=next(x for x in obs[oid]["photos"] if x["id"]==pid)
 assert photograph["license_code"]=="cc-by" and creator.lower() in (photograph.get("attribution") or "").lower()
 assert all(str(pid) not in str(x.get("file","")) for x in d["images"])
 url=f"https://inaturalist-open-data.s3.amazonaws.com/photos/{pid}/original.jpg"
 source=get(url)
 assert hashlib.sha256(source).hexdigest()==rec["source_sha256"], "Source original SHA mismatch"
 with Image.open(io.BytesIO(source)) as im:
  assert im.format=="JPEG"
  im.verify()
 with Image.open(io.BytesIO(source)) as im:
  im=ImageOps.exif_transpose(im).convert("RGB")
  assert min(im.size)>=800 and max(im.size)<=12000
  original_dimensions=[im.width,im.height]
  im.thumbnail((1850,1850),Image.Resampling.LANCZOS)
  output=io.BytesIO()
  im.save(output,"JPEG",quality=89,optimize=True)
  jpeg=output.getvalue()
 with Image.open(io.BytesIO(jpeg)) as im:
  assert im.format=="JPEG" and not im.getexif().get(34853)
  im.verify()
 rel=f"images/tridentopsis-mutica-inat-{pid}-ccby.jpg"
 actual=BASE/rel
 assert not actual.exists()
 bytefiles[actual]=jpeg
 sha=hashlib.sha256(jpeg).hexdigest()
 license_url="https://creativecommons.org/licenses/by/"
 photo_page=f"https://www.inaturalist.org/photos/{pid}"
 observation_page=f"https://www.inaturalist.org/observations/{oid}"
 newimages.append({"file":rel,"role":role,"creator":creator,"license":"CC BY","license_code":"cc-by",
  "license_url":license_url,"source_page":photo_page,"observation_url":observation_page,
  "source_recorded_photo_attribution":photograph.get("attribution"),
  "source_photo_id":pid,"source_observation_id":oid,
  "original_source_image":url,"original_sha256":rec["source_sha256"],"archive_sha256":sha,
  "original_dimensions":original_dimensions,"source_taxon":"Tridentopsis mutica Research Grade source-identification; botanical voucher independently unverified",
  "modifications":"Resized JPEG, EXIF/GPS removed. No photograph-pixel arrows.",
  "photo_status":"EXACT_IMAGE_CC_BY_VERIFIED__ARCHIVED__GROSS_CONTEXT_ONLY. Physical lower tuft and leaf sheaths visible; actual roots/rhizome and true free ligule NOT demonstrated."})
 newpanels.append({"label":label,"scientific_name":"Tridentopsis mutica","image_url":str(actual),
  "image_fit":"contain","image_role":role,"caption":caption,
  "why_it_matters":"Provides actual exact-species basal and entire-plant context where existing images were exclusively heads; avoid false ligament/rhizome identification.",
  "creator":creator,"license":"CC BY","license_url":license_url,"source_page":photo_page,
  "observation_source":observation_page,"markers":[],
  "photo_status":"True source-identified, individually CC BY licensed, locally archived; source original SHA verified. Original pixel anatomy markers pending, no underground crown or free inner ligule demonstrated."})
 records.append({"photo_id":pid,"observation_id":oid,"creator":creator,"license":"CC BY",
  "sha256":sha,"original_sha256":rec["source_sha256"],"file":str(actual),"source_page":photo_page})
old=d["visual_comparison"]["items"]
assert all(x["scientific_name"]=="Tridentopsis mutica" for x in old[:3])
assert all(x["scientific_name"]=="Tridentopsis buckleyana" for x in old[3:])
d["images"].extend(newimages)
d["visual_comparison"]["items"]=newpanels+old
d["visual_comparison"]["title"]="Slim tridens — actual living bunch, lower sheaths and contracted heads"
d["visual_comparison"]["subtitle"]="Four NEW source-authenticated living basal/whole-clump photographs followed by three original exact-species narrow flowering heads, then two labeled other-species Buckley comparisons. True underground anatomy and inner ligule not yet exposed."
d["visual_comparison"]["overlay_note"]="2026-10-26 Lane 3: 4 separate research-grade exact T. mutica source-photo IDs individually CC BY checked and physically archived with original SHA, 0 new arrows until full JPEG pixel inspection. Three old true mutica heads with Rachel and both Joey Santore CC BY-NC source credits/arrows, and two Buckley different-species comparison panels unchanged. Other editor contributions preserved."
q=d["field_photo_quickcheck"]
q["featured_photo_indices"]=[0,1,2,3,4,7]
q["steps"]=[
 "Gallery photos 1 and 4 are actual source-labeled living narrow grasses IN PLACE at rocky ground level. A tuft is visible; buried knotty rhizome, stolon rooting, and root crown are NOT excavated.",
 "Gallery photos 2 and 3 show source-identified fine green basal blades, sheath and culm attachments next to fingers. No peeled-open true 0.5–1 mm ciliate membrane, so the ligule remains UNPHOTOGRAPHED.",
 "Gallery photos 5–7 are three originally credited true slim-tridens upright contracted attached flowering-head views; real spikelets can be seen, not internally measured.",
 "Gallery photos 8–9 depict DIFFERENT SPECIES Buckley's tridens, whose flowering branches generally spread out rather than remaining appressed. Never present them as slim tridens root or ligule evidence.",
 "Photograph same confirmed flowering plant from full panicle through lower culm to actual attached base. Carefully expose the underground crown or rhizome, nodes and actual roots beside ruler; take true opened inner ligule picture with a millimeter scale.",
 "If contracted head versus Buckley remains ambiguous, count mature florets from THREE spikelets, and photograph detached dorsal three-veined lemma showing actual nerve hair distribution, with a 1-mm ruler."
]
q["warning"]="Only basal upper surface and leaf sheaths are newly photographed, no actual exposed rooted knotty crown/rhizome and NO unambiguous true inner 0.5–1 mm ligule. Four new CC BY, three older Rachel/Joey images (Joey CC BY-NC remains restricted), and two Buckley comparisons. Preserve source taxon and county holds."
ts=d["field_id_short_tiles"];assert len(ts)==6
ts[0]["photo_panel_indices"]=[0,3,4,5,6]
ts[0]["details"]="Source-identified wild plants (gallery 1 and 4) now actually show ground-level tufted grassy growth and flowering culms, followed by three original photographed narrow flowering heads (5–7). A narrow panicle favors slim tridens, but plant-base photos do not expose knotty roots or rhizomes; purple hue and silhouette alone do not determine the species."
ts[0]["status"]="TRUE LIVING BUNCH AND ATTACHED FLOWERING HEAD SOURCE PHOTOS; ACTUAL EXPOSED ROOT CROWN MISSING"
ts[1]["photo_panel_indices"]=[0,1,2,3]
ts[1]["details"]="Photos 1–4 show actual ground-level clusters of blades and lower sheathing parts beside fingers. These let the crew locate the true collar on a field plant but DO NOT document the opened free ciliate membrane (published 0.5–1 mm), true hair fringe, or connected belowground rhizome. In FNA the bases are knotty/shortly rhizomatous; other resources differ on stolons. Do not assert either from a photograph of in-situ leaf bases."
ts[1]["status"]="LIVING BASAL SHEATH VIEWS; TRUE LIGULE, CONNECTED ROOTS/RHIZOMES STILL MISSING"
ts[2]["photo_panel_indices"]=[4,6]
ts[3]["photo_panel_indices"]=[6]
ts[4]["photo_panel_indices"]=[4,5,7,8]
ts[4]["details"]="Slim = slender appressed upright contracted head (actual panels 5–7); Buckley = more open branching head (ACTUAL DIFFERENT-SPECIES panels 8–9). Floret count of five overlaps; only when growth/base/whole panicle fail to separate them, count 3 mature spikes and examine dorsal lemma nerve hair placement with 1-mm scale."
ts[5]["photo_panel_indices"]=[0,1,2,3,4,5,6,7,8]
ts[5]["details"]="Four real new exact-source CC BY tuft and lower-leaf originals physically added, plus original three exact species head JPEGs and two labeled Buckley comparisons. The new photos show living tuft/habitat and lower blades but NOT exposed roots, knotty rhizome, any proven rooting stolon, or an opened 0.5–1 mm ciliate ligule. Verify them on the same attached flowering specimen; microscopy is reserved for confusable overlap. Joey NC photos remain credited and noncommercial-only."
d["field_id_finish_pass"]["lane3_four_gross_base_photos_20261026"]={
 "new_source_photos":4,"total_species_archived_photos":7,"total_gallery_panels":9,
 "source_ids":[x[0] for x in PICK],"rights":"All new CC BY photo-level, exact observation source, source SHA and creator verified; old two Joey Santore NC and one Rachel BY untouched",
 "roles":{"living_in_place_bunch":"PRESENT; roots hidden","lower_basal_leaf_sheaths":"PRESENT, true free ligule hidden","complete_attached_head":"PRESENT existing Rachel and Joey; no exact mm scale","rooted_exposed_knotty_crown":"MISSING","real_free_ciliate_ligule":"MISSING"},
 "important_disagreement":"FNA short-knotty-rhizomatous base; other sources mention stoloniferous; neither independently photographically verified here",
 "remaining":["Same rooted flowering specimen with knotty base/rhizome AND roots actually exposed","0.5–1 mm inner ciliate membrane photographed beside ruler","Only if floret count overlaps Buckley: mature 3-spikelet count and dorsal lemma pilose nerves photographed"],
 "scientific_holds_unchanged":True
}
d["field_id_finish_pass"]["stage"]="FIELD_READY_PHOTO_GAPS — seven actual species source-photo files, including four real living tuft and lower sheaths, but exposed knotty rooted crown/rhizome and true opened ciliate ligule still absent."
d["curation_status"]["photo_metadata_count"]=7
d["curation_status"]["photo_files_present"]=7
d["curation_status"]["lane3_mutica_four_base_public_20261026"]="Four true exact species CC BY field photographs added; 7 local species images, 9 gallery panels incl 2 other-species Buckley comparisons; existing source rights and science preserved; root/inner ligule unverified."
d["learner_visual_status"]["image_count"]=7
d["learner_visual_status"]["status"]="FIELD_READY_PHOTO_GAPS"
assert all(json.dumps(d.get(k),sort_keys=True)==v for k,v in preserve.items())
assert len(d["images"])==7 and len(d["visual_comparison"]["items"])==9
assert all(all(isinstance(i,int) and 0<=i<9 for i in x.get("photo_panel_indices",[])) for x in ts)
for actual,jpeg in bytefiles.items():actual.parent.mkdir(parents=True,exist_ok=True);actual.write_bytes(jpeg)
CARD.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
REPORT.write_text(json.dumps({"result":"FOUR_REAL_CC_BY_MUTICA_BASE_PHOTOS_INSTALLED","species":"Tridentopsis mutica","photos":records,"archived_count":7,"gallery_panels":9,"new_arrows":0,"rights":"preserve existing Joey NC and other-source copyright metadata","status":"FIELD_READY_PHOTO_GAPS","remaining":["actual rooted knotty crown/short rhizome","actual free 0.5–1 mm ciliate inner ligule"]},indent=2)+"\n",encoding="utf-8")
print(json.dumps({"result":"FOUR_REAL_CC_BY_MUTICA_BASE_PHOTOS_INSTALLED","photo_ids":[x[0] for x in PICK],"total_local_images":7,"gallery_panels":9}))
