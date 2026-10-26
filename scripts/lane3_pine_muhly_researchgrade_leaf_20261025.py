#!/usr/bin/env python3
"""Lane 3 pine muhly: independently verify one RG, CC-BY true leaf-detail photograph.
No 1-mm ligule / floret / provenance claims and no undocumented arrows.
"""
import io, json, pathlib, hashlib, urllib.request, urllib.error, time
from PIL import Image, ImageOps
root=pathlib.Path("content/taxa/Poaceae/Muhlenbergia/muhlenbergia-dubia")
species_file=root/"species.json"
species=json.loads(species_file.read_text())
assert species.get("id")=="muhlenbergia-dubia"
pid=237946166;obsid=139156693
rpt={"species":"muhlenbergia-dubia","added":[],"holds":[],"target_photo":pid,"target_observation":obsid}
def read(url):
 req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyVisualLearner/1.0 (source-credited conservation education; github.com/Crking92/Hays-County-Botany)"})
 for trial in range(3):
  try:
   with urllib.request.urlopen(req,timeout=40) as r:return r.read(13_000_001)
  except urllib.error.HTTPError as e:
   if e.code!=429 or trial==2:raise
   time.sleep(4*(trial+1))
try:
 data=json.loads(read(f"https://api.inaturalist.org/v1/observations/{obsid}"))
 obs=next((o for o in data.get("results",[]) if o.get("id")==obsid),None)
 if obs is None:raise ValueError("observation missing")
 if obs.get("taxon",{}).get("id")!=165548:raise ValueError("taxon ID changed; exclude")
 if obs.get("quality_grade")!="research":raise ValueError("no longer Research Grade")
 p=next((p for p in obs.get("photos",[]) if p.get("id")==pid),None)
 if p is None:raise ValueError("photo ID absent from exact observation")
 if p.get("license_code")!="cc-by":raise ValueError("photo license changed; hold")
 if "Wendy McCrady" not in p.get("attribution",""):raise ValueError("credit not verified")
 if any(x.get("photo_id")==pid for x in species["images"]):raise ValueError("duplicate photo ID")
 photo_url=p.get("url","").replace("square.","original.")
 if str(pid) not in photo_url:raise ValueError("original JPEG URL mismatch")
 original=read(photo_url)
 with Image.open(io.BytesIO(original)) as im: im.verify()
 with Image.open(io.BytesIO(original)) as im:
  im=ImageOps.exif_transpose(im).convert("RGB")
  if min(im.size)<750:raise ValueError("insufficient photo pixels")
  size=list(im.size)
  im.thumbnail((2000,2200))
  buffer=io.BytesIO();im.save(buffer,"JPEG",quality=91,optimize=True);blob=buffer.getvalue()
 rel="images/ccby-wendy-mccrady-237946166-narrow-leaf.jpg"
 dest=root/rel
 if dest.exists():raise ValueError("destination exists, no overwrite")
 dest.write_bytes(blob)
 record={"file":rel,
  "role":"True source-labelled narrow green grass BLADE held between fingers. Shows fine blade and visible longitudinal veins, but true free inner ligule NOT depicted/verified.",
  "creator":"Wendy McCrady","license":"CC BY 4.0","license_url":"https://creativecommons.org/licenses/by/4.0/",
  "source_page":f"https://www.inaturalist.org/photos/{pid}",
  "source_observation":f"https://www.inaturalist.org/observations/{obsid}",
  "source_photo_id":pid,"source_taxon_name":"Muhlenbergia dubia",
  "source_research_grade_on_import":True,"original_media_url":photo_url,
  "original_sha256":hashlib.sha256(original).hexdigest(),
  "archive_sha256":hashlib.sha256(blob).hexdigest(),"source_dimensions":size,
  "photo_status":"ORIGINAL_SOURCE_RGB_ARCHIVED__TRUE_BLADE_RECOGNITION_ONLY__LIGULE_AND_CROSS_SECTION_UNVERIFIED",
  "public_reuse":"CC BY original source photo. Photographer/URL and resize/EXIF-strip modification acknowledged.",
  "modifications":"Reencoded JPEG, resized if needed, EXIF/GPS stripped.",
  "photo_review":"Research-grade source identification checked against iNat API for exact observation and photo; blade orientation/fine texture source-image pre-screened. No measured ligule or certified blade cross-section."}
 species["images"].append(record)
 species["visual_comparison"]["items"].append({
  "label":"PINE MUHLY — fine real leaf blade held between fingers",
  "scientific_name":"Muhlenbergia dubia",
  "image_url":str(root/rel),"image_fit":"contain",
  "image_role":"Source-reported research-grade thin leaf blade view; NOT a free ligule, rolled-leaf cross-section or dissected spikelet.",
  "caption":"Wendy McCrady, CC BY 4.0, iNaturalist Research Grade observation 139156693. A useful source-photo blade-scale comparison. No inner membrane, mature glumes or lemma length demonstrated.",
  "why_it_matters":"Separates the blade recognition lesson from the uncertain leaf-collar candidate and makes the photo limitations explicit.",
  "creator":"Wendy McCrady","license":"CC BY 4.0",
  "source_page":f"https://www.inaturalist.org/photos/{pid}",
  "photo_status":"ORIGINAL_CC_BY_RESEARCH_GRADE_LEAF_ONLY__NO_MICRO_ANATOMY_ARROW",
  "markers":[]})
 species["curation_status"]["photo_files_present"]=sum(x.get("file","").startswith("images/") for x in species["images"])
 species["curation_status"]["photo_metadata_count"]=len(species["images"])
 species["learner_visual_status"]["image_count"]=len(species["images"])
 species["learner_visual_status"]["status"]="FIELD_READY_PHOTO_GAPS"
 species["learner_visual_status"]["note"]="Seven locally stored publicly reusable photos: includes a separately research-grade, source-labelled pine muhly blade view, provisional iNat leaf collar/reproductive photos and certified Smithsonian voucher. Exact calibrated free ligule and floret dissection still missing."
 species["lane3_leaf_detail_20261025"]={"source_photo":pid,"source_observation":obsid,"source_grade":"research","license":"CC BY 4.0","status":"LEAF_BLADE_REFERENCE_ONLY","holds":["No photograph measures 4–10 mm free membranous ligule","No photograph separates the two 2–3 mm glumes from fertile lemma under a metric scale","True inrolled blade cross section not independently resolved"],"arrows":0}
 species_file.write_text(json.dumps(species,ensure_ascii=False,indent=2)+"\n")
 rpt["added"].append({"file":str(dest),"bytes":len(blob),"sha256":record["archive_sha256"],"license":"CC BY 4.0","photo":pid,"role":record["role"]})
except Exception as e:rpt["holds"].append(str(e)[:350])
pathlib.Path("reports/lane3-pine-muhly-research-grade-blade-20261025.json").write_text(json.dumps(rpt,indent=2)+"\n")
print(json.dumps(rpt))
