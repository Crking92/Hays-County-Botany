#!/usr/bin/env python3
"""Install a precisely credited source-identified E. heterophylla var. heterophylla
cyathium and developing-fruit photo from SAplants, with source license retained.
Does NOT silently change the identity of the previously flagged pink-bracted photo.
"""
import hashlib,io,json,time
from pathlib import Path
from urllib.parse import quote
import requests
from PIL import Image, ImageOps

BASE=Path("content/taxa/Euphorbiaceae/Euphorbia/euphorbia-heterophylla")
CARD=BASE/"species.json"
FILE="images/04-saplants-heterophylla-cyathia.jpg"
OUTPUT=BASE/FILE
REPORT=Path("reports/euphorbia-heterophylla-saplants-install-20261020.json")
NAME="Euphorbia_heterophylla_var._heterophylla_1DS-II_1-7120-01.jpg"
SOURCE="https://commons.wikimedia.org/wiki/File:"+NAME
LICENSE_URL="https://creativecommons.org/licenses/by-sa/4.0/"
def download():
 md5=hashlib.md5(NAME.encode("utf8")).hexdigest()
 direct="https://upload.wikimedia.org/wikipedia/commons/"+md5[0]+"/"+md5[:2]+"/"+quote(NAME,safe="._-")
 alt="https://commons.wikimedia.org/wiki/Special:Redirect/file/"+quote(NAME,safe="._-")+"?width=1600"
 session=requests.Session()
 session.headers["User-Agent"]="HaysCountyBotanyLearner/1.0 (https://github.com/Crking92/Hays-County-Botany)"
 errors=[]
 for url in [alt,direct]:
  try:
   res=session.get(url,timeout=95)
   res.raise_for_status()
   assert 15000 < len(res.content) < 22000000
   with Image.open(io.BytesIO(res.content)) as im:
    im.load()
    assert im.format in ("JPEG","PNG")
    orig=list(im.size)
    pic=ImageOps.exif_transpose(im).convert("RGB")
   assert min(pic.size)>=700
   sha=hashlib.sha256(res.content).hexdigest()
   pic.thumbnail((1750,1750),Image.Resampling.LANCZOS)
   dest=io.BytesIO();pic.save(dest,"JPEG",quality=91,optimize=True)
   data=dest.getvalue()
   with Image.open(io.BytesIO(data)) as verify:verify.verify()
   assert len(data)>17000
   return data,url,res.url,sha,orig,list(pic.size)
  except Exception as exc:
   errors.append((url,str(exc)[:170]))
 raise RuntimeError("No trustworthy image downloaded: "+repr(errors))
def main():
 card=json.loads(CARD.read_text(encoding="utf-8"))
 assert card["scientific_name"]=="Euphorbia heterophylla"
 assert card["project_inclusion"]["target_zone_status"]=="COMPARISON"
 assert card["field_id_finalization"]["stage"]=="PASS_IN_PROGRESS"
 if any(x["file"]==FILE for x in card["images"]):
  assert OUTPUT.exists() and OUTPUT.stat().st_size>17000
  print("Already present, no-op");return
 assert len(card["images"])==3
 assert card["images"][1]["taxon_photo_review"].startswith("TAXON_ID_HOLD")
 assert not OUTPUT.exists()
 raw,url,final,sha,original_dims,processed_dims=download()
 OUTPUT.parent.mkdir(exist_ok=True,parents=True)
 OUTPUT.write_bytes(raw)
 card["images"].append({
  "file":FILE,
  "role":"Source-labelled Euphorbia heterophylla var. heterophylla close-up of true tiny cyathia and developing 3-lobed fruits from a non-red-bracted specimen; examine actual saved pixels before adding anatomy arrows.",
  "creator":"SAplants (Wikimedia Commons)",
  "license":"CC BY-SA 4.0",
  "license_url":LICENSE_URL,
  "source_page":SOURCE,
  "source_platform":"Wikimedia Commons (originally labelled E. heterophylla var. heterophylla, garden weed in South Africa)",
  "downloaded_from":final,
  "original_image_sha256":sha,
  "original_image_dimensions":original_dims,
  "image_dimensions":processed_dims,
  "public_reuse":"yes",
  "study_use":"public educational botanical field lessons, attribution and share-alike",
  "modifications":"Resized and re-encoded EXIF-free JPEG; arrows not applied yet.",
  "anatomy_arrows":"none; pixel inspection needed for small gland and fruit details",
  "photo_review":"Source is specifically named variety heterophylla, photographed at Lowveld Botanical Garden South Africa. CC BY-SA 4.0, creator SAplants. Photo resolves developing capsules; true circular gland aperture/annular rim to verify by inspecting saved JPEG, do not infer.",
 })
 card["curation_status"]["photo_metadata_count"]=len(card["images"])
 card["curation_status"]["photo_files_present"]=len(card["images"])
 card["curation_status"]["saplants_verified_photo_added"]="2026-10-20"
 card["learner_visual_status"]["image_count"]=len(card["images"])
 card["learner_visual_status"]["note"]+=" An exact-name SAplants CC BY-SA 4.0 close macro is physically installed; pink-bracted older Psumuseum photo remains taxon ID HOLD. New anatomy arrow check pending saved JPEG inspection."
 card["field_id_finalization"]["photo_review"]+=" One additional named var. heterophylla Commons close-up is installed with explicit author/license, pending actual pixel arrow QA. Taxon-ID hold of previously published salmon-bracted photo remains."
 CARD.write_text(json.dumps(card,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 REPORT.parent.mkdir(exist_ok=True,parents=True)
 REPORT.write_text(json.dumps({
  "taxon":"Euphorbia heterophylla var. heterophylla","source":SOURCE,
  "source_creator":"SAplants","license":"CC BY-SA 4.0","license_url":LICENSE_URL,
  "saved_file":str(OUTPUT),"url_requested":url,"url_reached":final,
  "source_sha256":sha,"source_dimensions":original_dims,
  "processed_dimensions":processed_dims,
  "photo_anatomy_status":"needs direct inspection of actual new local JPEG",
  "held_photo":"euphorbia-heterophylla/images/02-cyathia-closeup.jpg; pink bracts conflicting with FNA key",
  "native_status_unchanged":"COMPARISON"
 },indent=2)+"\n",encoding="utf-8")
 print("PASS added one CC BY-SA 4.0 named var. heterophylla source photo",OUTPUT)
if __name__=="__main__":main()
