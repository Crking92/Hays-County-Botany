#!/usr/bin/env python3
"""Archive TWO genuinely new A. virginicum anatomy photos by Harry Rose, CC BY 2.0.
Do not duplicate the already archived Harry Rose seed1 or racemes photo.
Only botanical photographed reproductive structures, no hidden ligule/root claims.
"""
import io,json,hashlib,time
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime,timezone
import requests
from PIL import Image,ImageOps

B=Path("content/taxa/Poaceae/Anatherum")
SP=B/"anatherum-virginicum/species.json"
GP=B/"genus.json"
REPORT=Path("reports/lane3-broomsedge-harry-rose-spikelet-photos-20261027.json")
HOLD=Path("reports/lane3-broomsedge-harry-rose-source-holds-20261027.json")
REL=Path("workflow/field-id-publication/2026-10-27-broomsedge-harry-rose-real-anatomy.json")
LIC="https://creativecommons.org/licenses/by/2.0/"
PHOTOS=[
dict(id="6966375226",file="harry-rose-broomsedge-spikelet-pair-ccby2.jpg",
 src="https://upload.wikimedia.org/wikipedia/commons/2/21/Andropogon_virginicus_spikelets10_%286966375226%29_%282%29.jpg",
 page="https://commons.wikimedia.org/wiki/File:Andropogon_virginicus_spikelets10_(6966375226)_(2).jpg",
 size=(2048,1536),role="MATURE PAIRED SPIKELET MACRO — source identified Andropogon virginicus; long awn and hairy reduced stalked structures visible",
 label="ACTUAL REPRODUCTIVE MICRO — awned fertile spikelet, silky stalked partner",
 caption="Genuine Harry Rose photographed spikelet unit: the central elongated fertile unit bears a long fine awn; curved lateral hairy stalks and reduced sterile partners radiate either side. Actual structures clearly visible. NO printed millimeter reference in frame; do not label exact lemma veins or lengths. Photographer sampled this species in Australia, where it is introduced, NOT a local Texas voucher."),
dict(id="7117321563",file="harry-rose-broomsedge-spathe-emerging-raceme-ccby2.jpg",
 src="https://upload.wikimedia.org/wikipedia/commons/8/86/Andropogon_virginicus_head_branch1_%287117321563%29_%282%29.jpg",
 page="https://commons.wikimedia.org/wiki/File:Andropogon_virginicus_head_branch1_(7117321563)_(2).jpg",
 size=(3000,4000),role="ATTACHED FLOWERING RACEME — source identified A. virginicum, hair-bearing spikelets emerging beside reddish enclosing spathe",
 label="REAL SPATHE ARCHITECTURE — flowering raceme emerging from sheath",
 caption="Photographed hair-bearing raceme with individual green/brown spikelets immediately beside a long reddish green spathe. Distinct from the separate already stored mature seed and gross flowering head photographs; macro structure visible, ligule NOT shown. Original is Australian field material, not a Hays County rooted voucher."),
]
def save(path,obj):
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
def get(sess,photo):
 errors=[]
 for link in [photo["src"],"https://commons.wikimedia.org/wiki/Special:Redirect/file/"+photo["page"].split("File:")[1]]:
  for attempt in range(2):
   try:
    r=sess.get(link,timeout=35,headers={"Accept":"image/jpeg,image/*"},allow_redirects=True)
    r.raise_for_status()
    if urlparse(r.url).hostname not in ("upload.wikimedia.org","commons.wikimedia.org"):
     raise ValueError("Unexpected file source origin")
    raw=r.content
    if len(raw)<20000 or len(raw)>12_000_000 or raw[:3]!=b"\xff\xd8\xff":
     raise ValueError("Nonmatching original JPEG bytes")
    with Image.open(io.BytesIO(raw)) as im:
     im.load()
     if im.format!="JPEG" or im.size!=photo["size"]:
      raise ValueError(f"Unexpected actual original dimensions {im.size}")
     im=ImageOps.exif_transpose(im).convert("RGB")
     # Keep source pixels with no crop; resize to 2200px for lighter field learner.
     if max(im.size)>2200: im.thumbnail((2200,2200),Image.Resampling.LANCZOS)
     savedsize=list(im.size)
     out=io.BytesIO()
     im.save(out,"JPEG",quality=93,optimize=True)
    bs=out.getvalue()
    with Image.open(io.BytesIO(bs)) as im2:
     assert im2.format=="JPEG" and not im2.getexif().get(34853)
     im2.verify()
    return {"blob":bs,"original_sha256":hashlib.sha256(raw).hexdigest(),
            "stored_sha256":hashlib.sha256(bs).hexdigest(),
            "source_dimensions":list(photo["size"]),"stored_dimensions":savedsize,
            "downloaded_from":r.url}
   except Exception as exc:
    errors.append(type(exc).__name__+": "+str(exc)[:160])
    time.sleep(attempt+1)
 return {"error":" | ".join(errors[-4:])}
def main():
 s=json.loads(SP.read_text(encoding="utf8"))
 g=json.loads(GP.read_text(encoding="utf8"))
 assert s["id"]=="anatherum-virginicum" and g["name"]=="Anatherum"
 # Require previous Harry Rose source already archived; avoid redundant shots.
 assert any("seed1_(6948584315)" in str(x.get("source_page","")) for x in s["images"])
 session=requests.Session()
 session.headers["User-Agent"]="HaysBotanyLane3-GitHubPhotoArchive/1.0 (non-commercial botanical education; credits retained)"
 incoming=[];fails=[]
 for p in PHOTOS:
  if any(x.get("source_page")==p["page"] for x in s["images"]):
   continue
  local=SP.parent/"images"/p["file"]
  if local.exists(): raise RuntimeError("Filename conflict no matching metadata: "+str(local))
  result=get(session,p)
  if "error" in result:
   fails.append({"source_id":p["id"],"error":result["error"]})
   continue
  local.parent.mkdir(parents=True,exist_ok=True)
  local.write_bytes(result["blob"])
  metadata={
    "file":"images/"+p["file"],"role":p["role"],"creator":"Harry Rose",
    "license":"CC BY 2.0","license_url":LIC,"source_page":p["page"],
    "source_image":p["src"],"source_taxon_name":"Andropogon virginicus",
    "accepted_taxon_name":"Anatherum virginicum","source_photo_id":p["id"],
    "source_locality":"South West Rocks, Australia; introduced species photographed there",
    "public_reuse":"CC BY 2.0 (attribution required; no noncommercial restriction)",
    "photo_status":"ACTUAL_SOURCE_JPEG_GITHUB_ARCHIVED_PHOTOGRAPH_NOT_ILLUSTRATION",
    "modifications":"Resized if larger than 2200px; RGB JPEG saved without EXIF/GPS, no crop or labels",
    **{k:v for k,v in result.items() if k!="blob"}
  }
  s["images"].append(metadata)
  panel={
    "label":p["label"],"scientific_name":"Anatherum virginicum",
    "image_url":str(local),"image_fit":"contain","image_role":p["role"],
    "caption":p["caption"],
    "why_it_matters":"Real paired fertile + stalked sterile spikelets and enclosed spathe structure for new field botany learners.",
    "creator":"Harry Rose","license":"CC BY 2.0","license_url":LIC,
    "source_page":p["page"],"source_image":p["src"],
    "source_photo_id":p["id"],"source_taxon_name":"Andropogon virginicus",
    "accepted_taxon_name":"Anatherum virginicum","markers":[],
    "photo_status":"Verified real source-specific CC BY original locally archived, photo pixels not illustrated; microscopic details without scale remain unmeasured"
  }
  for o in (s,g):
   if any(x.get("source_page")==p["page"] for x in o["visual_comparison"]["items"]):
    raise RuntimeError("Duplicate panel source conflicts")
   o["visual_comparison"]["items"].append(dict(panel))
  incoming.append({"id":p["id"],"file":str(local),"source_page":p["page"],
    "sha256":result["stored_sha256"],"original_sha256":result["original_sha256"],
    "source_dimensions":result["source_dimensions"],"saved_dimensions":result["stored_dimensions"]})
  print("ARCHIVED",p["id"],flush=True)
 if not incoming:
  save(HOLD,{"date_utc":datetime.now(timezone.utc).isoformat(),"status":"NO_NEW_VERIFIED_ARCHIVES","failures":fails})
  return
 s["curation_status"]["photo_files_present"]=sum(1 for x in s["images"] if
    str(x.get("file","")).startswith("images/") and (SP.parent/x["file"]).is_file())
 s["curation_status"]["photo_metadata_count"]=len(s["images"])
 s["curation_status"]["lane3_harry_rose_real_paired_spikelet_macro_20261027"]=(
   f"{len(incoming)} source-verified photo JPEG(s) of paired awned spikelets and flowering raceme in spathe, copyright CC BY 2.0. "
   "True inner ligule with scale and connected rooted Texas bunch remain unfilled."
 )
 s["learner_visual_status"]["status"]="FIELD_READY_PHOTO_GAPS"
 s["learner_visual_status"]["image_count"]=len(s["images"])
 save(SP,s);save(GP,g)
 save(REPORT,{"created_utc":datetime.now(timezone.utc).isoformat(),
   "result":"BROOMSEDGE_REAL_SPIKELET_PHOTOS_PHYSICALLY_ARCHIVED",
   "added":len(incoming),"records":incoming,"holds":fails,
   "photo_count":s["curation_status"]["photo_files_present"],
   "teaching_panels":len(s["visual_comparison"]["items"]),
   "source_rights":"Harry Rose CC BY 2.0 checked per source on Wikimedia Commons",
   "remaining":"Exposed true inner membranous ligule; fresh planted root crown with mature reproductive head; calibrated measurements of glume/lemma of same voucher",
   "publication":"GitHub commit request only; verify rights-filtered Pages separately"})
 save(REL,{"species":"anatherum-virginicum","created_utc":datetime.now(timezone.utc).isoformat(),
   "report":str(REPORT),"status":"physical source JPEGS verified; public Pages rights build/readback still required"})
 print("COMPLETE",len(incoming),flush=True)
if __name__=="__main__":main()
