#!/usr/bin/env python3
"""Archive TWO genuinely diagnostic and openly licensed nimblewill images.
Both exact CC BY 4.0 originals: Emily Summerbell, iNat observation 57794694.
NEITHER image proves roots emerging from nodes or the exposed true inner ligule.
Keep those photographic roles incomplete. Fail closed on mismatched sources.
"""
from pathlib import Path
from datetime import datetime,timezone
from urllib.parse import urlparse
import requests,io,time,json,hashlib
from PIL import Image,ImageOps

D=Path("content/taxa/Poaceae/Muhlenbergia")
SP=D/"muhlenbergia-schreberi/species.json"
GEN=D/"genus.json"
REPORT=Path("reports/lane3-nimblewill-ccby-collar-node-photos-20261027.json")
HOLD=Path("reports/lane3-nimblewill-ccby-collar-node-source-hold-20261027.json")
RELEASE=Path("workflow/field-id-publication/2026-10-27-nimblewill-ccby-collar-node-photos.json")
LICENSE="https://creativecommons.org/licenses/by/4.0/"
OBS="https://www.inaturalist.org/observations/57794694"
ITEMS=[
dict(id="92218291",
url="https://upload.wikimedia.org/wikipedia/commons/e/ea/Muhlenbergia_schreberi_iNat-92218291.jpg",
page="https://commons.wikimedia.org/wiki/File:Muhlenbergia_schreberi_iNat-92218291.jpg",
name="emily-summerbell-92218291-blade-sheath-collar-ccby4.jpg",size=(1536,2048),
label="NIMBLEWILL — REAL LEAF / SHEATH JUNCTION, pale collar tissue",
role="Real, source-identified leaf blade meeting ribbed sheath; membranous pale collar-zone tissue visible; free inner ligule tip NOT independently exposed",
caption="Exact M. schreberi CC BY photograph by Emily Summerbell. A short leaf blade connects to a narrow upright sheath. Pale membranous/collar-zone tissue is visible at the junction, but this viewpoint does NOT prove the full free inner ligule margin, its exact teeth, or a measured length. Do not mark outer hairs as the ligule.",
why="Real vegetative diagnostic reference, better than a generic picture; compare inner ligule cautiously with the hair-fringe collar of bermudagrass."),
dict(id="92218336",
url="https://upload.wikimedia.org/wikipedia/commons/8/84/Muhlenbergia_schreberi_iNat-92218336.jpg",
page="https://commons.wikimedia.org/wiki/File:Muhlenbergia_schreberi_iNat-92218336.jpg",
name="emily-summerbell-92218336-wiry-branching-stems-ccby4.jpg",size=(1536,2048),
label="NIMBLEWILL — real fine sprawling stems and branch nodes",
role="Actual wiry interlacing nimblewill stems and visible branching nodes held across a hand; NO exposed roots emerging from nodes",
caption="Exact M. schreberi CC BY 4.0 original showing slender branching stems, short leaves and stem nodes. The photographer is holding the above-ground stems; roots are NOT exposed. This teaches where to look for spreading nodes but CANNOT be scored as a rooted stolon macro.",
why="Bridges the tiny blade/sheath anatomy to the wiry mat-forming growth form seen along trails."),
]
def dump(p,obj):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
def get(item):
 failures=[]
 for link in [item["url"],"https://commons.wikimedia.org/wiki/Special:Redirect/file/Muhlenbergia%20schreberi%20iNat-"+item["id"]+".jpg"]:
  for retry in range(2):
   try:
    r=requests.get(link,timeout=35,headers={"User-Agent":"HaysBotanyVisualLearner/1.0 noncommercial botanical education; source attribution","Accept":"image/jpeg,image/*"})
    r.raise_for_status()
    if urlparse(r.url).hostname not in {"upload.wikimedia.org","commons.wikimedia.org"}:raise ValueError("Unsafe redirect")
    raw=r.content
    if len(raw)<20000 or len(raw)>5_000_000 or raw[:3]!=b"\xff\xd8\xff":raise ValueError("Unexpected original bytes")
    with Image.open(io.BytesIO(raw)) as im:
     im.load()
     if im.format!="JPEG" or im.size!=item["size"]:raise ValueError("Wrong original dimensions: "+str(im.size))
     im=ImageOps.exif_transpose(im).convert("RGB")
     if max(im.size)>2200:im.thumbnail((2200,2200),Image.Resampling.LANCZOS)
     dims=list(im.size)
     buffer=io.BytesIO()
     im.save(buffer,"JPEG",quality=93,optimize=True)
    data=buffer.getvalue()
    with Image.open(io.BytesIO(data)) as im:
     assert im.format=="JPEG" and not im.getexif().get(34853)
     im.verify()
    return dict(bytes=data,original_sha=hashlib.sha256(raw).hexdigest(),
       stored_sha=hashlib.sha256(data).hexdigest(),original_dimensions=list(item["size"]),
       stored_dimensions=dims,final_download_url=r.url)
   except Exception as e:
    failures.append(type(e).__name__+": "+str(e)[:130]);time.sleep(retry+1)
 return {"error":" | ".join(failures[-4:])}
def main():
 s=json.loads(SP.read_text());g=json.loads(GEN.read_text())
 if s.get("id")!="muhlenbergia-schreberi" or g.get("name")!="Muhlenbergia":raise ValueError("Canonical taxon changed")
 collected=[];holds=[]
 for item in ITEMS:
  if any(str(x.get("source_photo_id"))==item["id"] for x in s["images"]):
   print("Already physically referenced",item["id"]);continue
  if any(x.get("source_page")==item["page"] for x in s["images"]):
   raise ValueError("Already has source photo without exact identifier")
  f=SP.parent/"images"/item["name"]
  if f.exists():raise ValueError("Filename unexpectedly already exists")
  r=get(item)
  if "error" in r:
   holds.append({"photo_id":item["id"],"reason":r["error"]})
   print("SOURCE_HOLD",item["id"]);continue
  f.parent.mkdir(parents=True,exist_ok=True)
  f.write_bytes(r["bytes"])
  meta=dict(file="images/"+f.name,role=item["role"],creator="Emily Summerbell",
    license="CC BY 4.0",license_url=LICENSE,source_page=item["page"],
    source_image=item["url"],source_photo_id=item["id"],
    source_taxon_name="Muhlenbergia schreberi",observation_url=OBS,
    public_reuse="CC BY 4.0, attribution and modification disclosure required",
    modifications="JPEG resaved without EXIF/GPS; no crops, digital arrows or composites",
    photo_status="PHYSICALLY_ARCHIVED_AUTHENTIC_CC_BY; rooted node and inner true ligule roles STILL OPEN",
    original_sha256=r["original_sha"],archived_sha256=r["stored_sha"],
    original_dimensions=r["original_dimensions"],stored_dimensions=r["stored_dimensions"])
  s["images"].append(meta)
  panel=dict(label=item["label"],scientific_name="Muhlenbergia schreberi",
    image_url=str(f),image_fit="contain",image_role=item["role"],
    caption=item["caption"],why_it_matters=item["why"],creator="Emily Summerbell",
    license="CC BY 4.0",license_url=LICENSE,source_page=item["page"],
    source_image=item["url"],source_photo_id=item["id"],
    source_taxon_name="Muhlenbergia schreberi",markers=[],
    photo_status="Physical exact-source CC BY 4.0 photo; no roots or exact free ligule edge verified")
  for doc in (s,g):
   if any(p.get("source_page")==item["page"] for p in doc["visual_comparison"]["items"]):
    raise ValueError("Duplicate same-source gallery photo")
   doc["visual_comparison"]["items"].append(dict(panel))
  collected.append(dict(id=item["id"],file=str(f),source_page=item["page"],
      original_sha256=r["original_sha"],stored_sha256=r["stored_sha"],
      original_dimensions=r["original_dimensions"],stored_dimensions=r["stored_dimensions"]))
  print("ARCHIVED",item["id"],r["stored_dimensions"],flush=True)
 if not collected:
  dump(HOLD,{"checked":datetime.now(timezone.utc).isoformat(),"result":"NO_NEW_SOURCE_PHOTOS","holds":holds})
  return
 s["curation_status"]["photo_files_present"]=sum(1 for p in s["images"] if str(p.get("file","")).startswith("images/") and (SP.parent/p["file"]).is_file())
 s["curation_status"]["photo_metadata_count"]=len(s["images"])
 s["curation_status"]["nimblewill_true_collar_partial_node_photos_20261027"]=(
  f"{len(collected)} real CC BY collar and branching-node photos physically archived. Neither inner free ligule nor roots emerging from a node is clearly exposed; 6-role PHOTO gaps preserved.")
 s["learner_visual_status"]["image_count"]=len(s["images"])
 s["learner_visual_status"]["status"]="FIELD_READY_PHOTO_GAPS"
 s["learner_visual_status"]["note"]="New 92218291 actual pale collar, and 92218336 branching stems (not rooting proof). True inner ligule and rooted node still not photographed."
 dump(SP,s);dump(GEN,g)
 dump(REPORT,dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),
    result="NIMBLEWILL_REAL_COLLAR_AND_BRANCH_PHOTOS_STORED",added=len(collected),
    records=collected,holds=holds,local_photos=s["curation_status"]["photo_files_present"],
    teaching_panels=len(s["visual_comparison"]["items"]),
    photographer="Emily Summerbell",license="CC BY 4.0",source_observation=OBS,
    strict_holds=["Root visibly emerging at an attached stolon node","True inner freely exposed membranous ligule edge with mm scale","Oriented mature glume/lemma separation with measured macro"]))
 dump(RELEASE,dict(date="2026-10-27",taxon="muhlenbergia-schreberi",
    report=str(REPORT),rights="Exact CC BY 4.0 photos, author credited",
    public_status="GitHub commit pending successful independent Pages deployment"))
 print("TOTAL_NEW_PHOTOS",len(collected))
if __name__=="__main__":main()
