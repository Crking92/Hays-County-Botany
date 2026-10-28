#!/usr/bin/env python3
"""Physically archive five species-specific Harry Rose Phalaris? NO: Dichanthium sericeum photos.

Five diagnostic photographic roles: true exposed membrane, sessile/pedicelled spikelet
structure, actual graduated reference scale and visibly dissected reproductive units.
Never claim Australian specimen is a Texas voucher or photograph a root not seen.
"""
import csv, hashlib, html, io, json, pathlib, re, urllib.parse, urllib.request
from PIL import Image, ImageOps
BASE=pathlib.Path("content/taxa/Poaceae/Dichanthium/dichanthium-sericeum")
CARD=BASE/"species.json"
LEDGER=BASE/"image-sources.csv"
REPORT=pathlib.Path("reports/lane5-dichanthium-sericeum-five-real-anatomy-20261027.json")
ROOT="https://commons.wikimedia.org/wiki/File:"
PHOTOS=[
  {
   "title":"Dichanthium sericeum ligule5 (14344423535).jpg",
   "file":"harry-rose-dichanthium-sericeum-true-exposed-ligule5.jpg",
   "role":"Actual opened inner grass leaf-sheath mouth shows short pale eciliate membranous ligule; free edge visible but no calibrated mm ruler; Australian original exact species.",
   "label":"ACTUAL INNER LIGULE — short pale membrane at the sheath mouth",
   "caption":"Real source-identified Australian silky bluestem: the green sheath has been separated from its blade and a short pale, uneven-edged membranous ligule projects at the opening. The pointed white collar edge is NOT the long hairy culm-node beard. No real millimeter ruler accompanies this photo.",
   "why":"The crew can finally SEE the true inner membrane instead of memorizing 'ligule' from text. It is much shorter than the long hairs around the culm node.",
   "markers":[{"label":"Actual pale membranous ligule","label_x":5,"label_y":40,"target_x":48,"target_y":55},{"label":"Leaf sheath below junction","label_x":67,"label_y":82,"target_x":53,"target_y":79}],
   "tiles":[1],"kind":"LIGULE_PHOTO_PARTIAL_WITHOUT_MM"},
  {
   "title":"Dichanthium sericeum spikelet pair1 (14359269421).jpg",
   "file":"harry-rose-dichanthium-sericeum-real-spikelet-pair1.jpg",
   "role":"Actual same-species close-up of source-described paired spikelets with overlapping green bracts, long white glume hairs and a long dark bent awn. Attachment subtleties need separate sessile/pedicelled size photos.",
   "label":"REAL SPIKELET PAIR — long dark awn and white glume hairs",
   "caption":"This is a real source-labelled silky bluestem spikelet-pair photograph, not a cropped whole seedhead. See overlapping green bracts, long pale hairs and a dark angled awn. The individual attachment of the pedicelled versus sessile units cannot safely be arrowed independently in this image.",
   "why":"Teaches the scale and hairy arrangement that makes the racemes look silky; check the two separate measured spikelet photos to compare sessile and pedicelled forms.",
   "markers":[{"label":"Dark angled awn","label_x":70,"label_y":12,"target_x":72,"target_y":19},{"label":"Long silky glume hairs","label_x":17,"label_y":26,"target_x":53,"target_y":40}],
   "tiles":[3,4],"kind":"PAIR_ATTACHMENT_REAL_MATURITY_PARTIAL"},
  {
   "title":"Dichanthium sericeum spikelet size sessile1 (14382762923).jpg",
   "file":"harry-rose-dichanthium-sericeum-sessile-spikelet-scale.jpg",
   "role":"Actual source-identified sessile spikelet close-up: multiple visible ribs/glume margins, long white hairs and the original photographed graduated reference scale; scale units not independently checked.",
   "label":"SESSILE SPIKELET — genuine individual structure beside a ruler",
   "caption":"Source-identified fertile sessile spikelet from an Australian plant. The outer glume, shining green longitudinal ribs and hairy margins are visible beside actual dark graduated scale ticks. The original scale is not independently calibrated here; do not publish a measured 4-mm assertion from these pixels alone.",
   "why":"Contrasts a directly photographed unstalked fertile unit with the pedicelled companion and introduces real glume ribbing/hair structure.",
   "markers":[{"label":"Ribbed outer spikelet bracts","label_x":5,"label_y":75,"target_x":48,"target_y":66},{"label":"Actual scale graduations","label_x":65,"label_y":16,"target_x":39,"target_y":25}],
   "tiles":[3,4],"kind":"SESSILE_SEPARATE_RULER_UNCALIBRATED"},
  {
   "title":"Dichanthium sericeum spikelet size stalked1 (14362578995).jpg",
   "file":"harry-rose-dichanthium-sericeum-pedicelled-spikelet-scale.jpg",
   "role":"Actual source-identified stalked companion spikelet, distinct from sessile fertile unit; ribbed green bract and long hairs beside original photographed graduated scale; individual tick units not independently confirmed.",
   "label":"PEDICELLED SPIKELET — matched companion close-up with ruler",
   "caption":"The actual stalked companion, photographed independently by Harry Rose. It has a slightly different shape and fine hairs from the sessile fertile spikelet. The tick markings are physically in the source photo, but their numerical spacing must not be assumed.",
   "why":"Paired spikelets are essential to field identification of silky bluestem. This makes the term pedicelled concrete rather than relying on the whole-head silhouette.",
   "markers":[{"label":"Ribbed pedicelled spikelet","label_x":61,"label_y":65,"target_x":52,"target_y":55},{"label":"Original graduated markings","label_x":5,"label_y":79,"target_x":39,"target_y":83}],
   "tiles":[3,4],"kind":"PEDICELLED_SEPARATE_RULER_UNCALIBRATED"},
  {
   "title":"Dichanthium sericeum spikelet fertile dissected (14339493376).jpg",
   "file":"harry-rose-dichanthium-sericeum-actual-dissected-reproductive-parts.jpg",
   "role":"Actual source-identified fertile silky bluestem spikelet macro composite showing visibly separated tiny reproductive pieces (left) and intact hairy spikelet/head structures (right); precise fertile lemma/palea/sterile lemma boundaries are not independently labelled.",
   "label":"REAL DISSECTION — separated reproductive units and hairy intact spikelet",
   "caption":"A real microscopic dissection from Harry Rose with individual tiny pieces deliberately separated on the left and the hairy spikelet assembly on the right. The three pieces are NOT arrow-certified as specific glumes, lemmas or paleas because the source caption does not identify each boundary in this crop.",
   "why":"A genuine anatomy demonstration beyond a flowering-head close-up. It shows how small the reproductive parts are and why they must be separated and photographed at scale.",
   "markers":[{"label":"Dissected and separated pieces","label_x":5,"label_y":82,"target_x":19,"target_y":48},{"label":"Hairy spikelet close-up","label_x":70,"label_y":88,"target_x":70,"target_y":40}],
   "tiles":[4],"kind":"REAL_REPRODUCTIVE_DISSECTION_ORGAN_BOUNDARIES_UNRESOLVED"}
]
def get(url):
  req=urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotanySilkyBluestemPhotos/1.0 (educational archive)"})
  with urllib.request.urlopen(req,timeout=60) as reply:return reply.read()
def striphtml(raw):return html.unescape(re.sub("<[^>]+>","",raw))
s=json.loads(CARD.read_text(encoding="utf-8"))
assert s["id"]=="dichanthium-sericeum"
assert len(s["images"])==5 and len(s["visual_comparison"]["items"])==5, "Concurrent species edit: stop and reconcile"
out=[]
for spec in PHOTOS:
  page=ROOT+urllib.parse.quote(spec["title"].replace(" ","_"),safe="()._-")
  api="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({
   "action":"query","prop":"imageinfo","iiprop":"url|extmetadata",
   "iiurlwidth":"2400","titles":"File:"+spec["title"],"format":"json"})
  obj=json.loads(get(api))
  info=next(iter(obj["query"]["pages"].values()))["imageinfo"][0]
  meta=info["extmetadata"]
  lic=striphtml(meta.get("LicenseShortName",{}).get("value",""))
  artist=striphtml(meta.get("Artist",{}).get("value",""))
  desc=striphtml(meta.get("ImageDescription",{}).get("value",""))
  assert re.sub(r"[^a-z0-9]","",lic.lower())=="ccby20", ("Rights hold",spec["title"],lic)
  assert "harry rose" in artist.lower(), ("Creator hold",spec["title"],artist)
  # Some original descriptions discuss grass morphology rather than repeating taxon;
  # the exact source-file title and Commons species category supply source-level ID.
  assert "dichanthium sericeum" in spec["title"].lower()
  raw=get(info.get("thumburl") or info["url"])
  with Image.open(io.BytesIO(raw)) as verify:verify.verify()
  with Image.open(io.BytesIO(raw)) as img:
    cleaned=ImageOps.exif_transpose(img).convert("RGB")
    assert min(cleaned.size)>=800, ("Pixel detail hold",spec["title"],cleaned.size)
    cleaned.thumbnail((2400,2400))
    buffer=io.BytesIO()
    cleaned.save(buffer,format="JPEG",quality=89,optimize=True)
    data=buffer.getvalue()
  with Image.open(io.BytesIO(data)) as verify:verify.verify()
  with Image.open(io.BytesIO(data)) as verify:
    assert not verify.getexif() and not verify.info.get("exif")
  dest=BASE/"images"/spec["file"]
  dest.write_bytes(data)
  thumb_name="images/"+spec["file"]
  record={
   "file":thumb_name,"role":spec["role"],"creator":"Harry Rose (Macleay Grass Man)",
   "license":"CC BY 2.0","license_url":"https://creativecommons.org/licenses/by/2.0/",
   "source_page":page,"source_original_url":info["url"],
   "source_taxon_name":"Dichanthium sericeum","source_location":"Australia, original collection",
   "photo_status":"SOURCE-LABELLED exact species, CC BY 2.0 photographer/license validated; real anatomy pixels reviewed against Commons preview before installation; no Texas voucher, no exact microscopic lengths certified.",
   "public_reuse":"Author attribution, link to CC BY 2.0 and note JPEG re-encoding/EXIF removal; public-site safe",
   "sha256":hashlib.sha256(data).hexdigest(),"dimensions":list(cleaned.size)}
  s["images"].append(record)
  pi=len(s["visual_comparison"]["items"])
  panel={
   "label":spec["label"],"scientific_name":"Dichanthium sericeum",
   "image_url":dest.as_posix(),"image_fit":"contain","image_role":spec["role"],
   "caption":spec["caption"],"why_it_matters":spec["why"],
   "creator":"Harry Rose (Macleay Grass Man)","license":"CC BY 2.0",
   "license_url":"https://creativecommons.org/licenses/by/2.0/",
   "source_page":page,"source_original_url":info["url"],
   "markers":spec["markers"],
   "modifications":"Wikimedia source compressed to optimized metadata-free RGB JPEG; anatomy marks are browser overlays only",
   "photo_status":"Exact source photo and image rights verified; ARROWS ONLY gross visible structures; Australian source, no Texas specimen/millimeter-scale claims."
  }
  s["visual_comparison"]["items"].append(panel)
  for tile_index in spec["tiles"]:
    indices=s["field_id_short_tiles"][tile_index].setdefault("photo_panel_indices",[])
    if pi not in indices:indices.append(pi)
  out.append({"photo_id":spec["title"],"file":thumb_name,"source_page":page,"source_original_url":info["url"],
     "photo_role":spec["kind"],"bytes":len(data),"pixels":list(cleaned.size),
     "sha256":hashlib.sha256(data).hexdigest(),"panel_index":pi,
     "arrows":len(spec["markers"]),"license":"CC BY 2.0"})
assert len(out)==5 and len(s["images"])==10 and len(s["visual_comparison"]["items"])==10
s["curation_status"]["photo_metadata_count"]=len(s["images"])
s["curation_status"]["photo_files_present"]=len(s["images"])
s["curation_status"]["visual_finish"]=(
 "FIELD_READY_PHOTO_GAPS — 10 exact-species archived photos; newly source-verified Australian TRUE pale membranous inner ligule, sessile/pedicelled photographed spikelets beside original scale marks, intact photographed pair and separately dissected floral parts. Genuine Texas rooted base, local taxon/subspecies confirmation, precise specimen-calibrated glume/lemma hairs and awn origin remain absent.")
s["learner_visual_status"]["image_count"]=len(s["images"])
s["learner_visual_status"]["mode"]="lane5_real_diagnostic_ligule_pair_dissected_20261027"
s["learner_visual_status"]["note"]=(
 "Ten source-identified physical JPEGs = nine CC BY 2.0 Harry Rose open public-use photos from Australia and one original iNaturalist noncommercial CC BY-NC conditional image NOT in public gallery. "
 "Ten Learner panels = nine EXACT silky-bluestem Australian photos, one clearly DIFFERENT Kleberg node comparison. Five new real licensed diagnostic photos added: ligule membrane, true paired reproductive units, independently shown sessile and pedicelled spikelets against original scale marks, and separated reproductive pieces. "
 "No unverified mm scale tick length or organ boundary; local Texas roots/subspecies and measured glume fringe/lemma insertion remain missing. Pages deployment not independently verified.")
s["field_id_short_tiles"][1]["status"]="TRUE INNER LIGULE MEMBRANE NOW PHOTOGRAPHED (panel 5), still no 1-mm reference or local Texas voucher"
s["field_id_short_tiles"][3]["status"]="SOURCE-IDENTIFIED SPIKELET PAIR + SEPARATE SESSILE/PEDICELLED REAL SCALE PHOTOS ADDED"
s["field_id_short_tiles"][4]["status"]="REAL DISSECTED REPRODUCTIVE UNIT ADDED; EXACT FERTILE LEMMA/AWN ORIGIN STILL UNLABELLED"
s["field_id_short_tiles"][5]["status"]="FIELD_READY_PHOTO_GAPS — NINE OPEN-LICENSE EXACT PHOTOS, ONE DIFFERENT-SPECIES COMPARISON, TX ROOTED CROWN STILL MISSING"
s["field_photo_quickcheck"]["featured_panel_indices"]=[5,6,7,8,9,0,4,1,2]
steps=s["field_photo_quickcheck"]["steps"]
steps[2]="3 · TRUE INNER LIGULE: NEW exact-species Harry Rose photograph (panel 5) exposes an actual short pale eciliate membrane at the blade/sheath mouth. It is NOT the white stem-node beard. No certified 1-mm ruler; measure on a collected verified Texas plant."
steps[5]="6 · REAL SPIKELET DISSECTION: NEW exact-species panels 6-9 show photographed reproductive pair, separately source-identified sessile and pedicelled spikelets beside original graduated marks, and an actual opened/dissected unit. The lower-glume transverse ciliary arch and precise lemma awn origin remain unverified in these source pixels."
steps[7]="8 · PUBLIC QA: 10 archived source-identified photo records (nine open CC BY 2.0, one research-only NC); 10 gallery panels, five newly installed exact-species anatomy views with only gross visible-only arrows; preserve source links and licenses and verify deployment/mobile rendering."
s["lane5_silky_five_true_anatomy_20261027"]={
 "status":"FIELD_READY_PHOTO_GAPS","real_new_photographs":out,"new_arrow_markers":sum(x["arrows"] for x in out),
 "source_license":"CC BY 2.0, individual Harry Rose Wikimedia Commons photo source/rights verified",
 "estimated_six_role_coverage":{"score":4.5,"max":6,"percent":75,"caution":"Practical six-role approximation; no complete fine reproductive or connected rooted local voucher"},
 "critical_holds":["No exposed rooted Texas same-voucher annual/perennial crown","Ligule visible but true scale millimeters not confirmed","Source-Australian plant, Texas subspecies identity not determined","Lower sessile glume cross fringe and separately identified fertile-lemma awn origin still unproven","Mobile public Pages release not yet verified"]}
CARD.write_text(json.dumps(s,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
with LEDGER.open(newline="",encoding="utf-8") as f:
 reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
existing={r.get("file_name") for r in rows}
for entry in out:
 name=pathlib.Path(entry["file"]).name
 if name in existing:continue
 row={k:"" for k in fields}
 for k,v in {"file_name":name,"role":entry["photo_role"],
  "creator":"Harry Rose (Macleay Grass Man)","license":"CC BY 2.0",
  "source_page":entry["source_page"],"direct_url":entry["source_original_url"],
  "study_use":"Exact-source original photographic botanical field ID",
  "public_reuse":"Wikimedia photo-specific CC BY 2.0; credit author, source, license; image resized/EXIF stripped"}.items():
  if k in row:row[k]=v
 rows.append(row);existing.add(name)
with LEDGER.open("w",newline="",encoding="utf-8") as f:
 writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
REPORT.write_text(json.dumps({"species":"Dichanthium sericeum","date":"2026-10-27","status":"FIELD_READY_PHOTO_GAPS",
 "before":{"archived":5,"gallery":5},"after":{"archived":len(s["images"]),"gallery":len(s["visual_comparison"]["items"])},
 "new_photo_results":out,"ledger_rows":len(rows),
 "new_arrows":sum(p["arrows"] for p in out),
 "six_role_estimate":s["lane5_silky_five_true_anatomy_20261027"]["estimated_six_role_coverage"],
 "holds":s["lane5_silky_five_true_anatomy_20261027"]["critical_holds"]},indent=2)+"\n")
print(json.dumps({"new_count":len(out),"photos":len(s["images"]),
 "panels":len(s["visual_comparison"]["items"]),"arrows":sum(x["arrows"] for x in out)}))
