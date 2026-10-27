#!/usr/bin/env python3
"""Archive two actual Bob Harms Panicum hallii anatomical originals.

Source owner explicitly licenses scientific/educational uses with credit,
NOT a Creative Commons unrestricted license. Keep this exact distinction.
Do not claim the photographed bracts are individually identified or
precisely measured without confidence in visible pixel boundaries.
"""
import io,urllib.request,time,re,html,json,hashlib,pathlib
from bs4 import BeautifulSoup
from PIL import Image,ImageOps
ROOT="https://w3.biosci.utexas.edu/prc/Monocots/"
PAGE="https://w3.biosci.utexas.edu/prc/Monocots/GrassHTML/data/Panicum-text.html"
BASE=pathlib.Path("content/taxa/Poaceae/Panicum/panicum-hallii")
CARD=BASE/"species.json"
def download(url):
 for k in range(4):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 HaysBotanyScientificEducationalLearner/1.0 (credit: Bob Harms)"})
   with urllib.request.urlopen(req,timeout=50) as resp: return resp.read()
  except Exception as e:
   print("Retry",k,str(e)[:160],flush=True)
   if k==3:raise
   time.sleep(4*(k+1))
def clean(b):return " ".join(html.unescape(BeautifulSoup(b,"html.parser").get_text(" ",strip=True)).split())
home=clean(download(ROOT))
assert "All Selected Monocots images and web pages are copyrighted by Bob Harms" in home,"Cannot prove original copyright"
assert "free for scientific and educational uses provided that Bob Harms is properly credited" in home,"Author's specific educational reuse grant absent"
cat=clean(download(PAGE))
assert "P. hallii (halls panicum) - Ligule/sheath" in cat and "P. hallii (halls panicum) - Spikelet detail" in cat,"P. hallii source IDs changed"
sp=json.loads(CARD.read_text(encoding="utf-8"))
assert sp["id"]=="panicum-hallii"
items=[
 {
  "id":"PAHA-L","file":"bob-harms-hallii-original-inner-ligule-sheath-scale-educational.jpg",
  "size":[226,600],
  "purpose":"REAL exact-species Panicum hallii upper leaf sheath and true inner ligule close-up by Bob Harms, with a source-mounted ruler at left. Individual pale ligule fringe near blade junction visible, and adjacent densely striped sheath below. Do not assert 1-mm length without verifiable ruler alignment.",
  "label":"TRUE INNER LIGULE — Bob Harms close-up, actual collar and ruled edge",
  "caption":"Panicum hallii photographed by Bob Harms: the pale ligule tissue sits precisely inside the green blade–sheath junction. White/pale tissue occurs at the junction and the lower green leaf sheath continues down the stem. The red and black ruled card is the photographer's size reference, but a precise ligule length has not been independently read from these pixels.",
  "why":"Closes a presentation clarity gap: the existing Jim Conrad photo shows a hair fringe, while this original shows where the fringe arises relative to sheath and blade, with original photographer scale.",
  "markers":[{"label":"Actual pale ligule at inner blade–sheath junction","label_x":3,"label_y":17,"target_x":60,"target_y":42}],
  "pixel_note":"Source-image PAHA-L 226x600 manually examined: inner collar whitish papery/hairy edge around y 230-290; blade above, striped sheath below; arrow target near x~135 y~252, not a sheath hair at base."
 },
 {
  "id":"PAHA-9","file":"bob-harms-hallii-separated-mature-spikelet-elements-educational.jpg",
  "size":[462,480],
  "purpose":"REAL multiple separated Panicum hallii spikelet-scale reproductive elements against dark background, source-labeled species and photographed beside original red-white scale marks. Clearly distinct folded papery bracts and hard smooth mature fruiting floret are shown; exact individual lower/upper glume and lemma label not proven from layout alone.",
  "label":"REAL SEPARATED REPRODUCTIVE ELEMENTS — Hall panicgrass original anatomy plate",
  "caption":"Bob Harms photographed true Panicum hallii reproductive structures physically separated from their flowering unit and arranged on a dark background next to an original scale. Notice the differing shapes: papery veined outer bracts and smaller hard smooth fertile components. Do not assign every structure a glume, lemma, or palea name from this unkeyed montage alone.",
  "why":"More anatomically informative than intact oval spikelets or papery fragments. Real photographed dissection is now present, but organ-by-organ expert labeling and calibrated measurement are still outstanding.",
  "markers":[],
  "pixel_note":"Original PAHA-9 462x480 manually examined: upper and lower fanned papery separated units and 2 shiny mature inner oval bodies; no overlaid arrow to an individual glume/lemma because image itself lacks keyed organ labels."
 }
]
added=[]
for it in items:
 src=ROOT+"GrassHTML/data/images/"+it["id"]+".jpg"
 rel="images/"+it["file"]; dst=BASE/rel
 if any(p.get("file")==rel for p in sp["images"]):
  assert dst.exists(),"Metadata without JPEG"
  print("EXISTS",rel,flush=True);continue
 assert not dst.exists() and not any(p.get("source_original")==src for p in sp["images"]), "Duplicated origin"
 raw=download(src)
 assert 14000<len(raw)<4500000,"Suspicious source bytes"
 im=Image.open(io.BytesIO(raw));im.load()
 print("SOURCE",src,im.format,im.size,len(raw),flush=True)
 assert im.format=="JPEG" and im.size==tuple(it["size"]),"Actual photo dimensions unexpected; abort for review"
 dst.parent.mkdir(parents=True,exist_ok=True)
 ImageOps.exif_transpose(im).convert("RGB").save(dst,"JPEG",quality=95,optimize=True)
 record={
 "file":rel,"role":it["purpose"],"creator":"Bob Harms",
 "license":"Copyright Bob Harms — free for scientific and educational use with credit (not CC)",
 "license_url":ROOT,"source_permission_page":ROOT,
 "source_page":PAGE,
 "source_detail_page":ROOT+"GrassHTML/data/pages/"+it["id"]+".html",
 "source_original":src,
 "source_taxon_name":"Panicum hallii",
 "public_reuse":"Explicit scientific and educational use authorized by original author provided proper credit; no general commercial/open-license permission implied.",
 "source_region":"Central Texas collection of Bob Harms, chiefly northern Hays and Travis counties; individual photo locality not established",
 "photo_review":it["pixel_note"],
 "image_dimensions":[im.width,im.height],
 "image_sha256":hashlib.sha256(dst.read_bytes()).hexdigest(),
 "modifications":"GPS/EXIF-stripped RGB JPEG of source image, no crop; text labels only on web overlay."
 }
 sp["images"].append(record)
 panel={
 "label":it["label"],"scientific_name":"Panicum hallii",
 "image_url":"content/taxa/Poaceae/Panicum/panicum-hallii/"+rel,
 "image_fit":"contain","creator":"Bob Harms","license":record["license"],"license_url":ROOT,
 "source_page":record["source_detail_page"],
 "image_role":it["purpose"],"caption":it["caption"],"why_it_matters":it["why"],
 "markers":it["markers"],
 "photo_status":"Educational-only reuse permission author quoted; actual original visually reviewed for gross structures. No unverified bract-specific labels or exact mm interpretation; mobile arrow overlay QA pending."
 }
 vc=sp["visual_comparison"]["items"]
 if not any(x.get("image_url")==panel["image_url"] for x in vc):
  idx=next((i for i,p in enumerate(vc) if p.get("scientific_name")!="Panicum hallii"),len(vc))
  vc.insert(idx,panel)
 added.append({"file":it["file"],"bytes":dst.stat().st_size})
sp["curation_status"]["photo_files_present"]=len(sp["images"])
sp["curation_status"]["lane1_hallii_bob_harms_true_ligule_dissection_20261027"]="TWO_EXACT_TAXON_SOURCE_BOB_HARMS_ANATOMY_ORIGINALS_ARCHIVED_EDUCATIONAL_PERMISSION_WITH_ATTRIBUTION_NOT_CC";
sp["learner_visual_status"]["image_count"]=len(sp["images"])
sp["learner_visual_status"]["note"]="Hall panicgrass: Uvalde real ligule and spikelets, USDA Blanco rooted pressed voucher, and Bob Harms Central Texas true inner collar and separated spikelet-elements photo now locally archived. Fine scale assignments and live crown still need final QA. Bob Harms educational reuse with credit is not CC.";
sp["photo_note"]=(sp.get("photo_note") or "")+" 2026-10-27: two authentic Bob Harms Panicum hallii anatomy photographs archived under author explicit educational/scientific use permission; leaf-inner ligule photograph and actual separated spikelet elements. Clear photographed tissue but exact mm labels / glume identity unverified.";
q=sp.get("field_photo_quickcheck")
if q:
 q["steps"].append("FINE ANATOMY ORIGINALS: Bob Harms's actual same-species inner ligule/sheath photo shows pale tissue at the junction and a ruler; his second photo shows separated mature reproductive bracts and smooth inner units. BOTH are true P. hallii, but don't claim every bract is a specific lemma/glume until keyed and measured.")
 q["warning"]="Eleven Hall's panicgrass exact-species archives: true Uvalde hairy ligule and flowering macros, USDA Blanco pressed connected roots, plus two Bob Harms real collar and separated reproductive plates under author-granted EDUCATIONAL use (not CC). Still need a living rooted crown, independently keyed scale-calibrated individual glumes and live mobile arrow QA."
CARD.write_text(json.dumps(sp,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"added":added,"photos":len(sp["images"]),"panels":len(sp["visual_comparison"]["items"]),"arrows":sum(len(p.get("markers",[])) for p in sp["visual_comparison"]["items"])}))
