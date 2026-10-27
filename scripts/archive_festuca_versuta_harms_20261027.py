#!/usr/bin/env python3
"""Archive two real original Bob Harms Festuca versuta photos, NOT CC.
Selected Central Texas Monocots educational/scientific use with credit.
Never mark torn leaf/sheath as dissected entire ligule or detached lemma as
identified to veins when not visible; no photo arrows inferred.
"""
import io,json,hashlib,time
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime,timezone
import requests
from PIL import Image,ImageOps
D=Path("content/taxa/Poaceae/Festuca")
SP=D/"festuca-versuta/species.json"; GP=D/"genus.json"
RP=Path("reports/lane3-festuca-versuta-harms-collar-spikelets-20261027.json")
HOLD=Path("reports/lane3-festuca-versuta-harms-source-hold-20261027.json")
REL=Path("workflow/field-id-publication/2026-10-27-festuca-versuta-real-collar-spikelets.json")
BASE="https://w3.biosci.utexas.edu/prc/Monocots/GrassHTML/data/"
ALTERNATE="https://www.biosci.utexas.edu/prc/Monocots/GrassHTML/data/"
LIC="© Bob Harms — scientific/educational use with attribution (NOT Creative Commons)"
LICURL="https://w3.biosci.utexas.edu/prc/Monocots/"
PERM="BOB_HARMS_SELECTED_MONOCOTS_EDU_WITH_CREDIT_20261022"
PHOTOS=[
("FEVE-L","REAL FESCUE LEAF–SHEATH / COLLAR — microscopic ligule region",
 "Actual Festuca versuta leaves with brown torn basal sheath tops photographed next to green blades and calibrated physical scale; short inner free ligule tip is only partially distinguishable. Right panel is a stem node, not necessarily the inner ligule. Do not arrow a made-up ligule margin.",
 "Real folded blade and sheath texture at collar, not just generic grass."),
("FEVE-J","REAL MATURE FESCUE SPIKELETS — floret cluster and scale",
 "Bob Harms' actual F. versuta mature attached spikelets enlarged beside a printed metric reference. Several florets overlap and long sharply tipped lemma/bract parts are visible. The individual glumes, lemma veins and 1-mm structure measurements are not all independently separable in the source image.",
 "Multi-flowered units reveal reproductive differences from single-flowered muhly species.")
]
def write(p,obj):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
def fetch(pid):
 errs=[]
 for base in (BASE,ALTERNATE):
  for attempt in range(2):
   try:
    r=requests.get(base+"images/"+pid+".jpg",timeout=35,headers={"Accept":"image/jpeg,image/*","User-Agent":"HaysCountyBotanyAuthPhotoArchive/1.0 science/education with author credit"})
    r.raise_for_status()
    if urlparse(r.url).hostname not in ("w3.biosci.utexas.edu","www.biosci.utexas.edu"):raise ValueError("Unexpected image source")
    raw=r.content
    if raw[:3]!=b"\xff\xd8\xff" or not 2500<len(raw)<5_000_000:raise ValueError("Non-JPEG or invalid source bytes")
    with Image.open(io.BytesIO(raw)) as im:
     im.load()
     if im.format!="JPEG" or min(im.size)<150 or max(im.size)>6000:raise ValueError("Bad source image dimensions")
     dims=list(im.size)
     im=ImageOps.exif_transpose(im).convert("RGB")
     out=io.BytesIO(); im.save(out,"JPEG",quality=94,optimize=True)
    saved=out.getvalue()
    with Image.open(io.BytesIO(saved)) as im:
     assert im.format=="JPEG" and not im.getexif().get(34853)
     im.verify()
    return {"data":saved,"original_sha256":hashlib.sha256(raw).hexdigest(),
      "archive_sha256":hashlib.sha256(saved).hexdigest(),"original_dimensions":dims,
      "archive_dimensions":dims,"original_url":r.url}
   except Exception as exc:
    errs.append(type(exc).__name__+": "+str(exc)[:160])
    time.sleep(1+attempt)
 return {"error":" | ".join(errs[-4:])}
def main():
 sp=json.loads(SP.read_text());gen=json.loads(GP.read_text())
 assert sp["id"]=="festuca-versuta" and gen["name"]=="Festuca"
 added=[];held=[]
 for pid,title,caption,why in PHOTOS:
  page=BASE+"pages/"+pid+".html"
  if any(x.get("source_page")==page for x in sp["images"]):
   print("Existing original",pid);continue
  local=SP.parent/"images"/("bob-harms-"+pid.lower()+".jpg")
  if local.exists():raise RuntimeError("Untracked filename conflict")
  d=fetch(pid)
  if "error" in d:
   held.append({"id":pid,"reason":d["error"]});continue
  local.parent.mkdir(parents=True,exist_ok=True)
  local.write_bytes(d["data"])
  meta={"file":"images/"+local.name,"role":title,"creator":"Bob Harms","license":LIC,
     "license_url":LICURL,"source_page":page,"source_image":BASE+"images/"+pid+".jpg",
     "source_taxon_name":"Festuca versuta","source_photo_id":pid,
     "site_specific_public_permission":PERM,"public_reuse":"Copyrighted Bob Harms original: science/education use only with credit. NOT Creative Commons.",
     "modifications":"JPEG re-encoded RGB with EXIF/GPS removed, no crop or annotations",
     "archived_sha256":d["archive_sha256"],"original_sha256":d["original_sha256"],
     "original_dimensions":d["original_dimensions"],"archive_dimensions":d["archive_dimensions"],
     "photo_status":"EXACT_SOURCE_JPEG_ARCHIVED; no fully exposed individual ligule tip or glume vein labels inferred"}
  sp["images"].append(meta)
  panel={"label":title,"scientific_name":"Festuca versuta",
     "image_url":str(local),"image_fit":"contain","image_role":title,
     "caption":caption,"why_it_matters":why,
     "creator":"Bob Harms","license":LIC,"license_url":LICURL,
     "source_page":page,"source_image":meta["source_image"],"source_photo_id":pid,
     "source_taxon_name":"Festuca versuta","site_specific_public_permission":PERM,
     "markers":[],"photo_status":"Original species photographed anatomy saved in GitHub; copyright retained, credited scientific/educational use"}
  for doc in (sp,gen):
   if any(x.get("source_page")==page for x in doc["visual_comparison"]["items"]):
    raise RuntimeError("Would duplicate existing author source panel")
   doc["visual_comparison"]["items"].append(dict(panel))
  added.append({"id":pid,"file":str(local),"source_page":page,
       "sha256":d["archive_sha256"],"source_dimensions":d["original_dimensions"]})
  print("ARCHIVED",pid,d["original_dimensions"])
 if not added:
  write(HOLD,{"checked":datetime.now(timezone.utc).isoformat(),"state":"NO_NEW_PHOTOS","holds":held})
  return
 sp["curation_status"]["photo_files_present"]=sum(1 for x in sp["images"] if str(x.get("file","")).startswith("images/") and (SP.parent/x["file"]).is_file())
 sp["curation_status"]["photo_metadata_count"]=len(sp["images"])
 sp["curation_status"]["festuca_versuta_harms_anatomy_20261027"]=f"{len(added)} actual Harms Texas fescue photos (sheath/collar, mature multiflowered spikelets) archived. True inner fully exposed free ligule, dissected lemma veins/rooted crown remain open."
 sp["learner_visual_status"]["status"]="FIELD_READY_PHOTO_GAPS"
 sp["learner_visual_status"]["image_count"]=len(sp["images"])
 write(SP,sp);write(GP,gen)
 write(RP,{"date_utc":datetime.now(timezone.utc).isoformat(),
    "result":"VERIFIED_ACTUAL_FESTUCA_VERSUTA_ANATOMY_JPEGS_ARCHIVED",
    "photos_added":len(added),"records":added,"source_failures":held,
    "local_images":sp["curation_status"]["photo_files_present"],
    "teaching_panels":len(sp["visual_comparison"]["items"]),
    "rights":"Bob Harms source-specific original science/education with credit only; NOT CC",
    "hold":"Inner true ligule fully opened, rooted flowering crown, separately identified lemma nerves"})
 write(REL,{"species":"festuca-versuta","date":"2026-10-27",
    "report":str(RP),"publication":"Rights-filtered noncommercial Pages validation and live readback still required"})
 print("COMMITTED_SOURCE_BYTES",len(added))
if __name__=="__main__":main()
