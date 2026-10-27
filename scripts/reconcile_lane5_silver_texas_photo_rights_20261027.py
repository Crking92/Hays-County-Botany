#!/usr/bin/env python3
"""Lane 5 silver bluestem: reconcile TWO already downloaded Texas photo images.
Do NOT treat an observation's licence as the PHOTO's licence.
Only promote exact-taxon, per-photo CC0/CC BY/CC BY-SA images to PUBLIC gallery.
No rights laundering; hold NC/unknown/copyright-only photos and old metadata.
"""
import json,urllib.request,urllib.error,pathlib,re,io,hashlib,time
from PIL import Image,ImageOps
root=pathlib.Path("content/taxa/Poaceae/Bothriochloa/bothriochloa-torreyana")
card=root/"species.json";out=pathlib.Path("reports/lane5-silver-bluestem-texas-two-photo-rights-20261027.json")
CANDIDATES=[
 {"obs":248379064,"photo":443784118,"filename":"02-inflorescence-detail.jpeg","public_filename":"texas-isabelvleer-silver-bluestem-443784118.jpg",
  "label":"TEXAS SOURCE — silver seedheads in a native prairie lot, with hand scale",
  "role":"Real silvery narrow mature heads of exact-observation silver bluestem near hand in Mesquite TX; no free ligule, nodal hairs or spikelet pair visible."},
 {"obs":250145594,"photo":447307568,"filename":"03-seedhead-rames.jpeg","public_filename":"texas-mary-hogan-silver-bluestem-447307568.jpg",
  "label":"TEXAS SOURCE — silvery plume and short densely hairy rames",
  "role":"Actual Texas source-labelled silvery native bluestem narrow contracted panicle, no 1-mm paired spikelet anatomy."}
]
licenses={"cc0":("CC0 1.0","https://creativecommons.org/publicdomain/zero/1.0/"),
 "cc-by":("CC BY 4.0","https://creativecommons.org/licenses/by/4.0/"),
 "cc-by-sa":("CC BY-SA 4.0","https://creativecommons.org/licenses/by-sa/4.0/")}
rep={"date":"2026-10-27","species":"Bothriochloa torreyana","checked":[],"photos_archived":[],"rights_holds":[],
 "taxonomic_gate":"Bothriochloa torreyana or exact synonym Bothriochloa laguroides subsp. torreyana (NOT unqualified B. laguroides)",
 "no_microscopic_anatomy_promoted":True}
def get(url):
 for i in range(4):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyExactPhotoRightsCheck/1.0 (noncommercial educational project)","Accept":"application/json,image/jpeg,*/*"})
   with urllib.request.urlopen(req,timeout=45) as f:raw=f.read(11000001)
   if len(raw)>11000000:raise ValueError("Oversize API/image response")
   return raw
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or i==3:raise
   time.sleep(3*(i+1))
d=json.loads(card.read_text());assert d["id"]=="bothriochloa-torreyana"
for q in CANDIDATES:
 data={"observation":q["obs"],"photo":q["photo"]}
 try:
  api=f"https://api.inaturalist.org/v1/observations/{q['obs']}"
  obs=next(iter(json.loads(get(api)).get("results",[])),None)
  if not obs:raise ValueError("Observation API not accessible")
  tax=obs.get("taxon") or {};name=tax.get("name","")
  data["taxon"]=name
  # Be strict: a subspecies within B. laguroides qualifies only if the epithet torreyana remains.
  if name not in ("Bothriochloa torreyana","Bothriochloa laguroides subsp. torreyana","Bothriochloa laguroides var. torreyana"):
   raise ValueError("Current taxon is not exact torreyana/synonym: "+name)
  p=next((x for x in obs.get("photos",[]) if str(x.get("id"))==str(q["photo"])),None)
  if not p:raise ValueError("Photo ID not attached to current observation")
  lic=str(p.get("license_code") or "").lower().replace("_","-")
  data["license_code"]=lic
  data["attribution"]=p.get("attribution")
  data["quality_grade"]=obs.get("quality_grade")
  data["location"]=obs.get("place_guess")
  rep["checked"].append(data)
  if lic not in licenses:raise ValueError("Photo-specific license not cleared for permissive public reuse: "+repr(lic))
  attrib=p.get("attribution") or ""
  if not attrib.strip():raise ValueError("Attribution missing")
  # Verify original stored copy exists, replace with cleaned copy in NEW file, retain archival rights record untouched.
  original=root/"images"/q["filename"]
  if not original.is_file():raise ValueError("Original previously archived image absent")
  with Image.open(original) as im: im.verify()
  with Image.open(original) as im:
   im=ImageOps.exif_transpose(im).convert("RGB")
   if min(im.size)<650:raise ValueError("Stored source photo too small")
   b=io.BytesIO();im.save(b,"JPEG",quality=89,optimize=True)
   clean=b.getvalue();size=list(im.size)
  rel="images/"+q["public_filename"];dest=root/rel
  if any(x.get("file")==rel for x in d["images"]):
   rep["rights_holds"].append({"photo":q["photo"],"reason":"Already present in public gallery archive"});continue
  dest.write_bytes(clean)
  with Image.open(dest) as im:im.verify()
  sha=hashlib.sha256(clean).hexdigest()
  src=f"https://www.inaturalist.org/photos/{q['photo']}"
  d["images"].append({"file":rel,"role":q["role"],"creator":attrib,"license":licenses[lic][0],
    "license_url":licenses[lic][1],"source_page":src,"source_observation":f"https://www.inaturalist.org/observations/{q['obs']}",
    "source_taxon_identification":name,"modifications":"Re-encoded RGB JPEG and stripped EXIF/GPS, no arrows",
    "sha256":sha,"pixels":size,"public_reuse":"Actual image-level open license verified by iNaturalist API on 2026-10-27",
    "photo_status":"Licensed Texas original; no inferred root/collar/paired-spikelet macro."})
  idx=len(d["visual_comparison"]["items"])
  d["visual_comparison"]["items"].append({"label":q["label"],"scientific_name":"Bothriochloa torreyana",
     "image_url":str(dest),"image_fit":"contain","image_role":q["role"],"creator":attrib,
     "license":licenses[lic][0],"license_url":licenses[lic][1],"source_page":src,
     "caption":"Original source-identified Texas silver bluestem photograph of the silvery panicle in its regional growth context. The visible seedheads are NOT independently resolved to a measured sessile/pedicelled pair, ligule or true stem node; use the photo for field appearance.",
     "why_it_matters":"Gives crew actual Texas photos for recognizing the silver contracted flowering head rather than relying only on New Mexico research views.",
     "markers":[],"photo_status":"Image-specific open license, source taxon and actual stored pixels checked; no new arrows."})
  d["field_id_short_tiles"][0]["photo_panel_indices"].append(idx)
  rep["photos_archived"].append({"photo":q["photo"],"local_file":str(dest),"pixels":size,"sha256":sha,"gallery_index":idx})
 except Exception as e:rep["rights_holds"].append({"photo":q["photo"],"reason":str(e)[:300]})
if rep["photos_archived"]:
 d.setdefault("lane5_texas_two_rights_reconciliation_20261027",{}).update({
  "archived":rep["photos_archived"],"status":"FIELD_READY_PHOTO_GAPS",
  "stage":"Licensed local Texas recognition photographs; measured collar, node and paired spikelets still absent"})
 d["curation_status"]["photo_metadata_count"]=len(d["images"])
 d["curation_status"]["photo_files_present"]=len(d["images"])
 d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
 card.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n")
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(rep,indent=2)+"\n")
print(json.dumps(rep))
