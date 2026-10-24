#!/usr/bin/env python3
"""Lane 3: archive source-labelled Leersia oryzoides mature spikelets.

Only exact taxon, original creator CC BY-SA 4.0 and source-matched photographs.
Do not label fine-scale anatomy absent a calibrated and pixel-reviewed photograph.
"""
import json, io, hashlib, pathlib, urllib.parse, urllib.request, urllib.error, time
from PIL import Image,ImageOps

root=pathlib.Path("content/taxa/Poaceae/Leersia/leersia-oryzoides")
card=root/"species.json"
d=json.loads(card.read_text());assert d["id"]=="leersia-oryzoides"
report={"added":[],"holds":[],"source_audit":"reports/lane3-leersia-leafmargin-source-audit-20261024.json",
"finding":"Source captions sl27 and sl28 say Spikelets. None of 24 audited titles explicitly depicts blade margin; that gap stays held.","no_microscopic_arrows":True}
audit=json.loads(pathlib.Path(report["source_audit"]).read_text())
def get(url):
 req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyVisualLearner/1.0 (educational source photo attribution; github.com/Crking92/Hays-County-Botany)"})
 for attempt in range(3):
  try:
   with urllib.request.urlopen(req,timeout=40) as res:return res.read(17000001)
  except urllib.error.HTTPError as ex:
   if ex.code!=429 or attempt==2:raise
   time.sleep(8*(attempt+1))
for n in (27,28):
 filename=f"Leersia oryzoides sl{n}.jpg"
 source=f"https://commons.wikimedia.org/wiki/File:Leersia_oryzoides_sl{n}.jpg"
 try:
  if any(x.get("source_page")==source for x in d["images"]):raise ValueError("source already present; avoid duplicate")
  checked=next((x for x in audit["files"] if x["name"]=="File:"+filename),None)
  if checked is None or checked["description"].split(" Taxonym")[0]!="Spikelets" or "CC BY-SA 4.0" not in checked["license"] or "Stefan.lefnaer" not in checked["artist"]:
   raise ValueError("source metadata audit does not establish exact taxon/license/photo role")
  api="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo","iiprop":"url|extmetadata","titles":"File:"+filename})
  info=next(iter(json.loads(get(api))["query"]["pages"].values()))["imageinfo"][0]
  lic=info["extmetadata"].get("LicenseShortName",{}).get("value","")
  artist=info["extmetadata"].get("Artist",{}).get("value","")
  if "CC BY-SA 4.0" not in lic or "Stefan" not in artist:raise ValueError("fresh license/creator mismatch")
  raw=get(info["url"])
  with Image.open(io.BytesIO(raw)) as im: im.verify()
  with Image.open(io.BytesIO(raw)) as im:
   im=ImageOps.exif_transpose(im).convert("RGB")
   if min(im.size)<650:raise ValueError("source resolution below 650 px")
   im.thumbnail((2200,2200));buffer=io.BytesIO();im.save(buffer,"JPEG",quality=90,optimize=True);blob=buffer.getvalue()
  rel=f"images/stefan-lefnaer-sl{n}-spikelets-ccby-sa4.jpg";dest=root/rel
  if dest.exists():raise ValueError("destination already exists; no replacement")
  dest.write_bytes(blob)
  d["images"].append({"file":rel,"role":f"Exact-source rice cutgrass SPIKELETS photograph #{n}: additional real reproductive close-up; no detached glume/lemma or ruler-scale claims","creator":"Stefan.lefnaer","license":"CC BY-SA 4.0","license_url":"https://creativecommons.org/licenses/by-sa/4.0/","source_page":source,"source_locality":"Vienna, Austria river bank; not a Texas voucher","original_media_url":info["url"],"sha256":hashlib.sha256(blob).hexdigest(),"photo_status":"SOURCE-LABELLED SPIKELETS PROVISIONAL anatomical pixel review, no arrows","public_reuse":"CC BY-SA 4.0 attribution and share-alike conditions; JPEG reencoded EXIF/GPS stripped"})
  d["visual_comparison"]["items"].append({"label":f"RICE CUTGRASS — source-labeled spikelets view {n} · anatomy review pending","scientific_name":"Leersia oryzoides","image_url":str(root/rel),"image_fit":"contain","image_role":"Additional exact-taxon photographed rice-like spikelet form at source photographic resolution","caption":"Stefan.lefnaer, CC BY-SA 4.0. Source-labelled spikelets; do not annotate glumes, lemma hairs or exact millimeter size without a real calibrated dissection. Not a Hays County voucher.","why_it_matters":"Study multiple genuine spikelet faces alongside the opened floret; test narrow flattened forms, not pink/purple flowering color.","creator":"Stefan.lefnaer","license":"CC BY-SA 4.0","source_page":source,"photo_status":"LOCAL_EXACT_SPECIES_LICENSE_VERIFIED__MICRO_ANATOMY_NOT_VERIFIED","markers":[]})
  report["added"].append({"file":str(dest),"license":lic,"sha256":hashlib.sha256(blob).hexdigest(),"bytes":len(blob)})
 except Exception as e:report["holds"].append({"source":source,"reason":str(e)[:250]})
if report["added"]:
 d["curation_status"]["photo_files_present"]=sum(x.get("file","").startswith("images/") for x in d["images"])
 d["curation_status"]["photo_metadata_count"]=len(d["images"])
 d.setdefault("learner_visual_status",{})["status"]="FIELD_READY_PHOTO_GAPS"
 d["learner_visual_status"]["image_count"]=len(d["images"])
 d["learner_visual_status"]["note"]="Additional exact-taxoned CC BY-SA 4.0 spikelet photographs locally archived, license source retained. True ruler-scaled retrorse blade margin, spikelet lengths and rhizome still missing; noncommercial Joey frame not cleared for unrestricted publication."
 d["lane3_margin_source_audit_20261024"]={"inspected_titles":len(audit["files"]),"leaf_margin_labelled_reusable_candidates":0,"source_review_report":report["source_audit"],"hold":"No licensed blade-margin photograph found among 24 checked Stefan Commons files. Go Botany blade-margin reference cannot be mirrored under the site's Terms of Use without image-rights permission.","status":"PHOTO_GAP_NOT_CLEARED"}
 card.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n")
pathlib.Path("reports/lane3-leersia-spikelet-extra-20261024.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
