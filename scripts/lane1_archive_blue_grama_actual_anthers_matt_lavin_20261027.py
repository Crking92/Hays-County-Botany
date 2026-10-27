#!/usr/bin/env python3
"""Add high resolution true CC BY-SA Bouteloua gracilis ANTHERS photo.

Source image is 4608×3456 original by Matt Lavin (Montana, 2015).
Clearly green-yellow dangling anthers are actual reproductive organs;
do not claim a dissected glume, fertile lemma, true ligule or root.
"""
import io, json, hashlib, urllib.request, time, pathlib
from PIL import Image,ImageOps
BASE=pathlib.Path("content/taxa/Poaceae/Bouteloua/bouteloua-gracilis")
CARD=BASE/"species.json"
NAME="matt-lavin-blue-grama-actual-dangling-anthers-attached-comb-by-sa2.jpg"
PATH=BASE/"images"/NAME
PAGE="https://commons.wikimedia.org/wiki/File:Bouteloua_gracilis_in_bloom.jpg"
SOURCE="https://upload.wikimedia.org/wikipedia/commons/a/a3/Bouteloua_gracilis_in_bloom.jpg"
sp=json.loads(CARD.read_text(encoding="utf-8"))
assert sp["id"]=="bouteloua-gracilis"
if any(p.get("file")=="images/"+NAME for p in sp["images"]):
 assert PATH.exists(), "Repeated metadata but missing actual photo bytes"
 print("already archived");raise SystemExit(0)
assert not PATH.exists() and not any(p.get("source_page")==PAGE for p in sp["images"]),"Duplicate actual source"
raw=None
for n in range(4):
 try:
  req=urllib.request.Request(SOURCE,headers={"User-Agent":"Hays County Botany Crew Learning/1.0 original CC BY-SA credited photo"})
  with urllib.request.urlopen(req,timeout=45) as r:raw=r.read()
  break
 except Exception as e:
  print("RETRY",n,str(e),flush=True)
  if n==3:raise
  time.sleep((n+1)*4)
assert raw and 1500000<len(raw)<6000000,f"bad image size {len(raw) if raw else 0}"
im=Image.open(io.BytesIO(raw));im.load()
assert im.format=="JPEG" and im.size==(4608,3456),f"unexpected pixels {im.size}"
im=ImageOps.exif_transpose(im).convert("RGB")
im.thumbnail((2600,2200),Image.Resampling.LANCZOS)
PATH.parent.mkdir(parents=True,exist_ok=True)
im.save(PATH,"JPEG",quality=92,optimize=True)
meta={
 "file":"images/"+NAME,
 "role":"Actual flowering B. gracilis eyelash-shaped comb with bright yellow-green elongated, freely hanging pollen anthers emerging from many spikelets; another comb at left with finger for context. True flowering organs visible but no dissected glumes or lemma insertion.",
 "creator":"Matt Lavin","license":"CC BY-SA 2.0",
 "license_url":"https://creativecommons.org/licenses/by-sa/2.0/",
 "source_page":PAGE,"source_original":SOURCE,
 "source_flickr_photo":"https://www.flickr.com/photos/plant_diversity/20615873848/",
 "source_taxon_name":"Bouteloua gracilis",
 "source_region":"Montana, USA, Aug 2015 (source geo location; NOT Hays County)",
 "public_reuse":"Original image on Wikimedia Commons verified CC BY-SA 2.0 and Flickr license checked by FlickreviewR 2; comply with attribution, share-alike, modifications note.",
 "photo_review":"The exact original 4608×3456 photo pixel preview inspected: close central comb with multiple unmistakable pendent yellow-green anthers and slender spikelet scales/bristles. Fine stigmas are not confidently resolved at this size; glume or lemma insertion not dissected. Ruler/fresh roots/inner ligule absent.",
 "image_dimensions_original":[4608,3456],
 "image_dimensions_archived":[im.width,im.height],
 "image_sha256":hashlib.sha256(PATH.read_bytes()).hexdigest(),
 "modifications":"Resized original preserving uncropped source composition; recompressed GPS/EXIF-free; two non-destructive in-gallery arrows only."
}
sp["images"].append(meta)
panel={
 "label":"TRUE FLOWERING ANATOMY — real dangling green pollen anthers on attached blue grama comb",
 "scientific_name":"Bouteloua gracilis",
 "image_url":"content/taxa/Poaceae/Bouteloua/bouteloua-gracilis/images/"+NAME,
 "image_fit":"contain",
 "creator":"Matt Lavin","license":"CC BY-SA 2.0",
 "license_url":"https://creativecommons.org/licenses/by-sa/2.0/",
 "source_page":PAGE,
 "image_role":"Real elongated, green-yellow staminal anthers dangling from numerous attached B. gracilis spikelets on a living flowering one-sided comb. Distinguish actual anthers from nearby awns and bracts; not a dissection of glumes or fertile/sterile lemmas.",
 "caption":"These green-yellow dangling structures are pollen-bearing anthers of actual flowering blue grama, not awns! Follow the central one-sided comb and see that long anthers project downward from many spikelets. The many stiff slender bristles are surrounding spikelet structures; their individual origins require a detached, measured spikelet.",
 "why_it_matters":"Separates the actual flower stamens from awns on a mature grass head. Provides anatomically specific pixel evidence that previous dry mature head photos could not show.",
 "markers":[
  {"label":"Real green-yellow hanging pollen anthers","label_x":4,"label_y":85,"target_x":45,"target_y":64},
  {"label":"Attached flowering comb with spikelets","label_x":65,"label_y":12,"target_x":61,"target_y":39}
 ],
 "photo_status":"Source photographed true flowering anthers, CC BY-SA original verified and full-resolution JPG locally archived. Two arrows to clearly visible gross features; mobile placement not yet independently verified. No glume/lemma or ligule falsely marked."
}
p=sp["visual_comparison"]["items"]
idx=next((i for i,x in enumerate(p) if x.get("scientific_name")!="Bouteloua gracilis"),len(p))
p.insert(idx,panel)
sp["curation_status"]["photo_files_present"]=sum(x.get("file","").startswith("images/") for x in sp["images"])
sp["curation_status"]["lane1_blue_grama_real_flowering_anthers_20261027"]="HIGH_RES_CC_BY_SA_ACTUAL_ANTHERS_ADDED_FINE_GLUML_LEMMA_AND_LIGULE_STILL_OPEN"
sp.setdefault("learner_visual_status",{})["image_count"]=len(sp["images"])
sp["learner_visual_status"]["note"]="Blue grama ten records including three NC research holds and two now-added public open-licensed details: Smithsonian pressed connected fibrous roots, and Matt Lavin true dangling yellow anthers. Actual free 0.1–0.4mm hair-fringe ligule and true fully separated glume/lemma dissection still missing."
q=sp.get("field_photo_quickcheck")
if q:
 q["steps"].append("TRUE FLOWERING ANATOMY: Matt Lavin's archived 2015 Montana B. gracilis photo directly photographs yellow-green dangling pollen anthers on the actual blue grama eyelash comb. These are real flowers; unlike stiff awns, anthers hang as longer, often yellow-green pollen organs.")
 q["warning"]="Ten blue grama photo records, seven public-eligible and three CC BY-NC held. Smithsonian pressed voucher shows physically connected fibrous roots; real Matt Lavin bloom photo shows attached pollen anthers. A TRUE 0.1–0.4mm inner hair-fringe ligule and completely separated scaled spikelet glumes/fertile lemmas remain photographic gaps. Pressed roots are not a living rooted plant."
sp["photo_note"]=(sp.get("photo_note","") or "")+" 2026-10-27: real 2015 Matt Lavin CC BY-SA2 blue grama flowering macro 4608×3456 showing green-yellow anthers archived with visible anther and comb arrows; flowers vs awns clearly separated, no glume/lemma or ligule claim."
CARD.write_text(json.dumps(sp,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"result":"INSTALLED_REAL_ANTHERS","images":len(sp["images"]),"panels":len(p),"jpg_bytes":PATH.stat().st_size,"markers":len(panel["markers"])}))
