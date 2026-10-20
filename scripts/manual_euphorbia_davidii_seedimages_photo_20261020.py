#!/usr/bin/env python3
"""Source-verified public-domain SeedImages Euphorbia davidii seed photo installer.
Uses the official exact species page; never substitutes an unverified taxon image.
Archived original remains untouched. Image labels are withheld until visual pixel QA.
"""
import hashlib,io,json,time
from pathlib import Path
import requests
from PIL import Image,ImageOps
BASE=Path("content/taxa/Euphorbiaceae/Euphorbia/euphorbia-davidii")
CARD=BASE/"species.json";REL="images/seedimages-bat003312-davidii-seeds.jpg";OUT=BASE/REL
NAME="BAT003312_IMG0089.jpg"
ROOT="https://idtools.org/seedimages/images/"
SOURCE="https://idtools.org/seedimages/index.cfm?entityID=61251&packageID=2289"
RIGHTS="https://idtools.org/seedimages/index.cfm?pageID=3760"
REPORT=Path("reports/euphorbia-davidii-seedimages-install-20261020.json")
CANDIDATES=[ROOT+p+NAME for p in ("full/","large/","", "thumbnails/")]
def fetch_image():
 s=requests.Session();s.headers.update({"User-Agent":"HaysBotanyLicensingReview/1.0 educational-reuse (https://github.com/Crking92/Hays-County-Botany)"})
 best=None;checks=[]
 for url in CANDIDATES:
  try:
   res=s.get(url,timeout=20);res.raise_for_status()
   raw=res.content
   assert len(raw)>2500 and len(raw)<10000000
   with Image.open(io.BytesIO(raw)) as img:
    img.load()
    assert img.format in ("JPEG","PNG")
    rgb=ImageOps.exif_transpose(img).convert("RGB")
   assert rgb.size[0]>=250 and rgb.size[1]>=170, "too few pixels"
   checks.append({"url":url,"size":list(rgb.size),"bytes":len(raw),"status":"valid"})
   if best is None or rgb.size[0]*rgb.size[1]>best[1].size[0]*best[1].size[1]:
    best=(url,rgb,raw)
  except Exception as err:checks.append({"url":url,"status":"skip","reason":str(err)[:130]})
 if not best:raise RuntimeError("No official exact-species seed photo could be downloaded. "+repr(checks))
 url,rgb,raw=best
 srcdim=list(rgb.size)
 if max(rgb.size)>1600:rgb.thumbnail((1600,1600),Image.Resampling.LANCZOS)
 buf=io.BytesIO();rgb.save(buf,format="JPEG",quality=92,optimize=True)
 data=buf.getvalue()
 with Image.open(io.BytesIO(data)) as verify:verify.verify()
 assert len(data)>2400
 return data,hashlib.sha256(raw).hexdigest(),url,srcdim,list(rgb.size),checks
def main():
 j=json.loads(CARD.read_text(encoding="utf-8"))
 assert j["scientific_name"]=="Euphorbia davidii"
 assert j["project_inclusion"]["native_metrics_excluded"] is True
 assert j["project_inclusion"]["target_zone_status"].startswith("AUTHORITY CONFLICT")
 assert j["field_id_finalization"]["stage"]=="PASS_IN_PROGRESS"
 if any(x["file"]==REL for x in j["images"]):
  assert OUT.is_file()
  print("ALREADY installed - no changes");return
 assert len(j["images"])==4 and not OUT.exists()
 assert j["images"][2]["license"]=="copyrighted / public reuse not granted"
 assert j["images"][3]["license"]=="copyrighted / public reuse not granted"
 raw,sha,url,srcdim,dim,checks=fetch_image()
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_bytes(raw)
 j["images"].append({
  "file":REL,
  "role":"CONFIRM SEED STRUCTURE — Exact source-labelled Euphorbia davidii multiple mature seeds with bumpy low tubercles; photographer credit CSU SeedImages/USDA ITP. Photo is NOT an E. dentata comparison nor an underside hair view.",
  "creator":"Pottorff, Larsen & Crowl / Colorado State University SeedImages; hosted by USDA-APHIS-PPQ ITP",
  "license":"Public domain (SeedImages site default; individual caption has no separate restricted credit)",
  "license_url":RIGHTS,
  "source_page":SOURCE,
  "source_platform":"SeedImages / CSU / USDA-APHIS-PPQ ITP",
  "downloaded_from":url,
  "original_image_sha256":sha,
  "original_image_dimensions":srcdim,
  "image_dimensions":dim,
  "public_reuse":"yes",
  "study_use":"Public botanical crew education with attribution and source-rights link",
  "modifications":"Re-encoded as JPEG without EXIF, original subject/scale not changed; no anatomy arrows added.",
  "photo_review":"SeedImages lists exact species E. davidii and corresponding photographic plate BAT003312_IMG0089. Copyright page says public domain except otherwise noted; no individual image notice on displayed caption. Source-pixel annotation needs independent visual readback.",
  "anatomy_arrows":"none; source photo pixel review required before marking seed tubercles",
 })
 j["curation_status"]["photo_metadata_count"]=len(j["images"])
 j["curation_status"]["photo_files_present"]=len(j["images"])
 j["curation_status"]["seedimages_exact_species_seed_installed"]="2026-10-20"
 j["curation_status"]["finished_field_id_pass"]="PASS_IN_PROGRESS"
 j["learner_visual_status"]["image_count"]=len(j["images"])
 j["learner_visual_status"]["note"]+=" Source-labelled USDA-supported SeedImages public-domain seed photo now locally stored; photo-level arrows pending saved pixels review."
 j["field_id_finalization"]["photo_review"]+=" An additional labelled E. davidii seed photograph is physically installed from CSU/USDA SeedImages (public-domain default); must review actual saved pixels before annotating; stiff underside hair macro still missing."
 j["field_id_finalization"]["missing"]=[x for x in j["field_id_finalization"]["missing"] if not x.startswith("Released ripe seed")] + [
  "Assess SeedImages photo's visible angular seed cross-section and irregular low bumps before claiming independently verified arrows",
  "Find equal-scale comparative E. dentata seed; seed photo alone does not prove paired-species traits"
 ]
 CARD.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 REPORT.parent.mkdir(parents=True,exist_ok=True)
 REPORT.write_text(json.dumps({
  "source":"CSU/USDA SeedImages","species":"Euphorbia davidii","filename":REL,
  "rights_page":RIGHTS,"exact_species_page":SOURCE,"license":"Public domain (default)",
  "source_sha256":sha,"source_url":url,"original_image_dimensions":srcdim,"processed_image_dimensions":dim,
  "retrieval_checks":checks,"photo_arrow_status":"manual pixel QA pending",
  "held":["Hair macro of abaxial leaf","Same-scale E. dentata seed"],
  "canonical_study_photos_unchanged":True
 },indent=2)+"\n")
 print("PASS Added seed photo",url,"source_size",srcdim,"total_gallery",len(j["images"]))
if __name__=="__main__":main()
