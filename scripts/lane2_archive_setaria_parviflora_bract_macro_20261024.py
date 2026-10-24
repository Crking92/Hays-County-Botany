#!/usr/bin/env python3
"""Finish public-safe Setaria parviflora bristle and glume/lemma photo archive."""
import hashlib,io,json,pathlib,time,urllib.error,urllib.request
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Setaria/setaria-parviflora")
p=base/"species.json"
j=json.loads(p.read_text())
assert j["id"]=="setaria-parviflora"
selection=[
 {
 "tag":"sl24","filename":"stefan-lefnaer-bristle-base-sl24.jpg",
 "url":"https://upload.wikimedia.org/wikipedia/commons/9/94/Setaria_parviflora_sl24.jpg",
 "size":(3036,3053),
 "role":"SOURCE PHOTOGRAPH: two close views of actual spikelet with pale persistent bristles below, purple feathery stigmas and a real printed 3-mm scale",
 "label":"BRISTLE ANATOMY · persistent basal bristle vs purple stigmas · measured original",
 "caption":"Two photographs of the original source-labeled S. parviflora spikelet; pale stiff bristles project from the base and should NOT be confused with purple feathery stigmas emerging from the flower. The original photographer's 3-mm scale remains in the JPEG. The arrow to a bristle labels the visible SHAFT, not an unseen exact basal insertion.",
 "markers":[
 {"label":"Pale persistent bristle shaft","label_x":73,"label_y":9,"target_x":88,"target_y":34},
 {"label":"Purple flower stigmas, not bristles","label_x":4,"label_y":73,"target_x":33,"target_y":40}
 ],
 },
 {
 "tag":"sl29","filename":"stefan-lefnaer-glume-lemma-sl29.jpg",
 "url":"https://upload.wikimedia.org/wikipedia/commons/4/40/Setaria_parviflora_sl29.jpg",
 "size":(10573,2560),
 "role":"REAL SPIKELET DISSECTION: original labelled multi-angle upper/lower glumes and lemmas with printed 3-mm reference, photos 2026-09-20 Croatia",
 "label":"GLUME AND LEMMA DETAILS · photographer-labelled two glumes and two lemmas",
 "caption":"Original labelled eight-view true spikelet montage, with Glu' lower glume, Glu'' upper glume, Lem' lower lemma, Lem'' upper fertile lemma, original printed 3-mm ruler. Photographer identification from Unije, Croatia; no automatic Hays specimen claim. Do not add artificial fine-detail arrows atop the author labels.",
 "markers":[]
 }
]
report={"taxon":"setaria-parviflora","method":"Individual Commons original URLs, Commons file-page CC BY-SA 4.0 rights verified 2026-10-24, strict original pixel dimensions","results":[]}
for spec in selection:
 src="https://commons.wikimedia.org/wiki/File:Setaria_parviflora_"+spec["tag"]+".jpg"
 result={"source":src,"status":"HOLD"}
 try:
  original=None
  for attempt in range(5):
   try:
    req=urllib.request.Request(spec["url"],headers={"User-Agent":"HaysCountyBotanyVisualLearner/1.1 (educational CC BY-SA photo-archiving)","Accept":"image/jpeg"})
    with urllib.request.urlopen(req,timeout=85) as f: original=f.read()
    break
   except urllib.error.HTTPError as e:
    if e.code not in (429,502,503,504) or attempt==4: raise
    time.sleep([3,8,15,25,35][attempt])
  assert original is not None
  assert 20000<len(original)<13000000
  test=Image.open(io.BytesIO(original));test.verify()
  im=Image.open(io.BytesIO(original)).convert("RGB")
  assert im.size==spec["size"],("unexpected_source_dimensions",im.size,spec["size"])
  original_sha256=hashlib.sha256(original).hexdigest()
  if im.width>8000:
   im.thumbnail((8000,5000),Image.Resampling.LANCZOS)
  dst=base/"images"/spec["filename"];dst.parent.mkdir(parents=True,exist_ok=True)
  im.save(dst,quality=92,optimize=True,subsampling=0)
  rec=next(x for x in j["images"] if x.get("source_page")==src)
  rec.update({"original_remote_file":rec.get("original_remote_file",rec["file"]),"file":"images/"+spec["filename"],"role":spec["role"],"creator":"Stefan.lefnaer","license":"CC BY-SA 4.0","license_url":"https://creativecommons.org/licenses/by-sa/4.0/","public_reuse":"Public with original source credit and CC BY-SA 4.0 terms","modifications":"Original RGB reencoded JPEG stripped of EXIF/GPS"+("; width downscaled to 8000 preserving photographer's printed labels and millimeter bar" if spec["size"][0]>8000 else ""),"photo_review_status":"Original photo composition inspected 2026-10-24; source credit independently checked; annotated only gross visibly discernible structures, Croatia not Texas"})
  vis=next(x for x in j["visual_comparison"]["items"] if x.get("source_page")==src)
  vis.update({"label":spec["label"],"image_url":str(dst),"image_fit":"contain","image_role":spec["role"],"caption":spec["caption"],"why_it_matters":"Real photographer-measured diagnostic features, unlike a distant green bottlebrush head.","creator":"Stefan.lefnaer","license":"CC BY-SA 4.0","license_url":"https://creativecommons.org/licenses/by-sa/4.0/","markers":spec["markers"],"photo_status":"Verified copyright file page and original dimensions; JPEG physically installed by archival workflow, macro arrows placed only where rendered source supports them."})
  result.update(status="ARCHIVED",path=str(dst),original_sha256=original_sha256,archived_sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),original_dimensions=list(spec["size"]),archived_dimensions=list(im.size),arrows=len(spec["markers"]))
 except Exception as e:result["error"]=str(e)
 report["results"].append(result)
success=sum(x["status"]=="ARCHIVED" for x in report["results"])
if success:
 j["field_photo_quickcheck"]["featured_photo_indices"]=[i for i,x in enumerate(j["images"]) if x["file"].startswith("images/")]
 j["field_photo_quickcheck"]["warning"]="Original photographed Croatian S. parviflora bristles and glume/lemma labels now in local species images when ARCHIVED. Do not count near purple stigma appendages as basal bristles, or claim an unseen insertion. Still need one locally Texas vouchered same-root mature bristle count. Added two overlays ONLY on photographed sl24 visible bristle shaft and purple stigmas."
 f=j["field_id_finish_pass"].setdefault("lane2_close_detail_20261024",{})
 f.update({"stage":"FIELD_READY_PHOTO_GAPS","archive_verified_by_workflow":success,"new_bristle_and_glume_macros":success,"new_source_visible_arrow_count":sum(x.get("arrows",0) for x in report["results"]),"remaining":["Measured attached single Texas mature spikelet bristle origins and counts with 1mm scale","Same-voucher Texas rootstock+collar+reproduction identity","Live site/mobile arrow overlay verification"],"public_site":"NOT_VERIFIED"})
 p.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n")
out=pathlib.Path("reports/lane2-setaria-parviflora-bristle-glume-20261024.json")
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
