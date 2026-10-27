#!/usr/bin/env python3
"""Add authentic CC0 close-up blue grama flowering combs, strict public CC rights.

Visible flowering branches and projected awns only. Not a dissected lemma,
true inner ligule, ruler, rooted plant, or certified bare distal rachis.
"""
import json,io,hashlib,urllib.request,time,pathlib
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Bouteloua/bouteloua-gracilis")
card=base/"species.json"
fname="patrick-alexander-blue-grama-actual-curved-mature-combs-cc0.jpg"
dst=base/"images"/fname
source_page="https://commons.wikimedia.org/wiki/File:Bouteloua_gracilis_-_Flickr_-_aspidoscelis_(4).jpg"
source="https://upload.wikimedia.org/wikipedia/commons/9/9b/Bouteloua_gracilis_-_Flickr_-_aspidoscelis_%284%29.jpg"
sp=json.loads(card.read_text(encoding="utf-8"))
assert sp["id"]=="bouteloua-gracilis"
if not any(p.get("file")=="images/"+fname for p in sp.get("images",[])):
 assert not dst.exists() and not any(p.get("source_page")==source_page for p in sp.get("images",[])),"duplicate sources"
 raw=None
 for k in range(4):
  try:
   req=urllib.request.Request(source,headers={"User-Agent":"HaysCountyBotanyCrewLearner/1.0 CC0 source-credited plant archive"})
   with urllib.request.urlopen(req,timeout=45) as resp:raw=resp.read()
   break
  except Exception as e:
   print("fetch retry",k,str(e),flush=True)
   if k==3:raise
   time.sleep(5*(k+1))
 assert raw and 180000<len(raw)<2200000,"bad raw payload"
 im=Image.open(io.BytesIO(raw));im.load()
 assert im.format=="JPEG" and im.size==(1800,1200),"unexpected file variant"
 dst.parent.mkdir(parents=True,exist_ok=True)
 im.convert("RGB").save(dst,"JPEG",quality=94,optimize=True)
 photo={
  "file":"images/"+fname,
  "role":"Actual close species-determined mature Bouteloua gracilis flowering branches with multiple recurved eyelash-like combs and prominently projecting fine pale awns/spikelet fragments, attached to a grass stem. Internal lower/upper glume, lemma base, true ligule, crown and bare tip not isolated.",
  "creator":"Patrick Alexander","license":"CC0 1.0","license_url":"https://creativecommons.org/publicdomain/zero/1.0/",
  "source_page":source_page,"source_original":source,
  "source_flickr_photo":"https://www.flickr.com/photos/aspidoscelis/49949820683/",
  "source_taxon_name":"Bouteloua gracilis","source_region":"Organ Mountains, Doña Ana County, New Mexico, 2008-01-10. Not Texas.",
  "public_reuse":"CC0 image-specific Commons/FlickrReviewR verified; photographer voluntarily credited.",
  "photo_review":"Source actual 1800x1200 JPEG visually reviewed: large bowed white mature upper comb, a second upright strongly awned spikelet-bearing branch and several out-of-focus neighboring combs. Do not claim microscopic origin of individual awns, glume arrangement or a naked rachis tip.",
  "image_dimensions":[1800,1200],
  "image_sha256":hashlib.sha256(dst.read_bytes()).hexdigest(),
  "modifications":"No crop, GPS/EXIF stripped RGB JPEG."
 }
 sp.setdefault("images",[]).append(photo)
else: assert dst.exists(),"Record present without file"
p=sp.setdefault("visual_comparison",{}).setdefault("items",[])
url="content/taxa/Poaceae/Bouteloua/bouteloua-gracilis/images/"+fname
if not any(x.get("image_url")==url for x in p):
 panel={
  "label":"ACTUAL MATURE BLUE GRAMA BRANCHES — fine spikelet projections on curved eyebrows (Patrick Alexander CC0)",
  "scientific_name":"Bouteloua gracilis",
  "image_url":url,"image_fit":"contain","creator":"Patrick Alexander","license":"CC0 1.0",
  "license_url":"https://creativecommons.org/publicdomain/zero/1.0/","source_page":source_page,
  "image_role":"Authentic single plant source-labelled blue grama photographed at close range; mature curved comb with many pale outward-projecting spikelets/awns, not dissected pieces.",
  "caption":"Real blue grama mature flowering branches in the Organ Mountains, New Mexico. Follow the long arcuate upper comb and its hundreds of fine pale projections, then compare the narrower upright branch in front. Their curvature is useful; a single branch is not a mm-level spikelet, ligule or glume dissection.",
  "why_it_matters":"An actual sharp mature comb close-up with visible outward structures, replacing reliance on NC Joey Santore research photos in the public teaching gallery.",
  "markers":[
   {"label":"Curved one-sided mature flowering comb","label_x":1,"label_y":11,"target_x":54,"target_y":24},
   {"label":"Fine awnlike projections on attached comb","label_x":1,"label_y":84,"target_x":44,"target_y":52}
  ],
  "photo_status":"Two arrows on obvious foreground mature flowering structures in the original pixels, no inferred glume/lemma/ligule; mobile arrow layout QA pending."
 }
 idx=next((i for i,x in enumerate(p) if x.get("scientific_name")!="Bouteloua gracilis"),len(p))
 p.insert(idx,panel)
holds=[]
for item in sp["images"]:
 if "CC BY-NC" in (item.get("license") or ""):
  item["public_gallery_eligibility"]="HOLD_CC_BY_NC"
  item["public_reuse"]="Private/research noncommercial-only image retained with photographer attribution, not eligible for unrestricted public Learner"
  holds.append({"file":item["file"],"license":item["license"],"source_page":item.get("source_page")})
for item in p:
 if "CC BY-NC" in (item.get("license") or ""):
  item["public_gallery_eligibility"]="HOLD_CC_BY_NC"
sp["visual_comparison"]["rights_hold_public_gallery_20261027"]=holds
sp["visual_comparison"]["subtitle"]="New genuine CC0 mature blue grama comb macro is archived; retain authentic Matt Lavin public-licensed hair/collar view and real whole-plant context. Three historical CC BY-NC same-species photos remain retained but excluded from public Learner. True free ligule, measured glume/lemma and rooted base remain incomplete."
sp.setdefault("curation_status",{})["photo_files_present"]=len(sp["images"])
sp["curation_status"]["lane1_blue_grama_cc0_mature_combs_rights_20261027"]="ONE_NEW_REAL_CC0_MATURE_COMB_MACRO_TWO_GROSS_ARROWS_THREE_CC_BY_NC_RESEARCH_PHOTOS_HELD";
sp.setdefault("learner_visual_status",{})["image_count"]=len(sp["images"])
sp["learner_visual_status"]["note"]="Eight photo records total; three CC BY-NC historical research photos held from public display, five open-licensed records including Matt Lavin actual collar/sheath and Patrick Alexander source-verifiable mature curved comb; exact free ligule and rooted system unphotographed.";
q=sp.get("field_photo_quickcheck")
if q:
 q["featured_photo_indices"]=[len(sp["images"])-1,6,0,1]
 q["steps"]=[
 "PUBLIC PHOTO FIRST: Patrick Alexander's CC0 original photographs mature long, one-sided curved eyebrow-shaped flowering branches and their fine awnlike projections. It is actual blue grama, not a generic grass or a different species.",
 "SECOND: Matt Lavin's archived real species-labelled photo documents hairy blade/sheath and collar REGION, but the exact free inner ligule edge and mm scale cannot yet be verified. Do not relabel the visible sheath hairs as the true ligule.",
 "OTHER PUBLIC PHOTOS show the low bunched habit and an actual detached mature comb; those identify the gross posture but do not explain precise glume and lemma insertions.",
 "Compare to hairy grama Bouteloua hirsuta: both have combs; to distinguish them examine genuine comb rachis tip and actual swollen-base hair placement, not just head curvature alone.",
 "MISSING ABOVEGROUND MACRO: fully open the true inner blade/sheath junction and photograph the fringe ligule separately with 1-mm reference; isolate actual mature branch spikelets and awn origin with a millimeter scale.",
 "LATER ROOT PHOTO: a connected fibrous rooted crown from a source-verified living bunch; no leaf-stem picture can certify root structure.",
 "PUBLIC DISPLAY RIGHTS: three old CC BY-NC photos are intentionally held from public Learner pending explicitly transferable permission, not deleted from archive."
 ]
 q["warning"]="Eight species photo records including five public-eligible and three CC BY-NC research holds. Curved real seedhead, attached awns and hairy collar-region now photographed, but no verified TRUE free ligule edge, mm-dissected glumes or living rooted crown. Mobile overlay and Pages QA pending.";
sp["photo_note"]=(sp.get("photo_note") or "")+" 2026-10-27: source-verified Patrick Alexander CC0 genuine curled ripe blue grama head detail added, two gross arrows, three older CC BY-NC research images withheld from unrestricted public Learner. No false ligule/rhizome/dissected spikelet completion.";
card.write_text(json.dumps(sp,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"result":"CC0_BLUE_GRAMA_IMPORTED","photos":len(sp["images"]),"held":len(holds),"panels":len(p),"bytes":dst.stat().st_size}))
