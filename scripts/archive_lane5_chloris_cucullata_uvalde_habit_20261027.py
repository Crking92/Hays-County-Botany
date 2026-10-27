#!/usr/bin/env python3
"""Make the existing verified Uvalde Jim Conrad live Chloris cucullata panel local.
Preserve indices and arrows; no claims about unexposed roots/inner ligule.
"""
import hashlib,io,json,pathlib,urllib.request,urllib.error,time,re,html
from PIL import Image,ImageOps
ROOT=pathlib.Path("content/taxa/Poaceae/Chloris/chloris-cucullata")
CARD=ROOT/"species.json"
REPORT=pathlib.Path("reports/lane5-chloris-cucullata-uvalde-live-field-local-20261027.json")
SRC_PAGE="https://www.backyardnature.net/n/h/windmill.htm"
PHOTO="https://www.backyardnature.net/n/13/131103cl.jpg"
PD="https://www.backyardnature.net/j/copyrite.htm"
REL="images/jim-conrad-uvalde-live-flowering-tuft.jpg"
OUT={"species":"Chloris cucullata","source":SRC_PAGE,"photo":PHOTO,"rights_source":PD,
     "new_local_photos":[],"warnings":[],"new_arrows":0,
     "role":"Live flower-bearing tuft emerging above soil in northern Uvalde County, not exposed roots or ligule"}
def fetch(url):
 for n in range(4):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotanyPublicDomainPhotoArchive/1.0 (educational field photography)"})
   with urllib.request.urlopen(req,timeout=40) as r:
    data=r.read(9000000)
   if len(data)>=9000000:raise ValueError("Source too large")
   return data
  except urllib.error.HTTPError as e:
   if e.code not in (429,502,503,504) or n==3:raise
   time.sleep(3*(n+1))
try:
 page=html.unescape(fetch(SRC_PAGE).decode("utf-8"))
 rights=html.unescape(fetch(PD).decode("utf-8"))
 if not re.search(r"Chloris\s+cucullata",page,re.I):raise ValueError("Exact species not identified on source page")
 if "131103cl.jpg" not in page:raise ValueError("Exact image not embedded on exact species source page")
 if "Jim Conrad" not in page:raise ValueError("Source attribution unclear")
 if not re.search(r"Jim Conrad.{0,120}PUBLIC DOMAIN|PUBLIC DOMAIN.{0,120}all images produced by myself",rights,re.I|re.S):
  raise ValueError("Photographer public-domain dedication did not pass")
 raw=fetch(PHOTO)
 with Image.open(io.BytesIO(raw)) as im:im.verify()
 with Image.open(io.BytesIO(raw)) as im:
  im=ImageOps.exif_transpose(im).convert("RGB")
  if min(im.size)<450:raise ValueError("Insufficient live field habitat resolution "+str(im.size))
  buf=io.BytesIO();im.save(buf,"JPEG",quality=90,optimize=True)
  binary=buf.getvalue();pixels=list(im.size)
 s=json.loads(CARD.read_text())
 assert s["id"]=="chloris-cucullata"
 panels=s["visual_comparison"]["items"]
 matches=[i for i,v in enumerate(panels) if v.get("image_url")==PHOTO and v.get("scientific_name")=="Chloris cucullata"]
 if len(matches)!=1:raise ValueError("Expected one existing exact photo panel; no rewrite")
 idx=matches[0]
 if any(i.get("file")==REL for i in s["images"]):
  OUT["warnings"].append("Already archived, no duplicate added")
 else:
  dest=ROOT/REL;dest.parent.mkdir(exist_ok=True);dest.write_bytes(binary)
  with Image.open(dest) as im:im.verify()
  sha=hashlib.sha256(binary).hexdigest()
  s["images"].append({
   "file":REL,"role":"Genuine living source-labelled Uvalde flowering bunch in soil; roots NOT exposed",
   "creator":"Jim Conrad","license":"Public domain — express photographer dedication",
   "license_url":PD,"source_page":SRC_PAGE,"source_original_url":PHOTO,
   "source_context":"Northern Uvalde County, Texas; Jim Conrad field photograph, November 2013",
   "modifications":"Re-encoded RGB JPEG; metadata/EXIF/GPS stripped; no added anatomical arrows",
   "public_reuse":"Author photograph public-domain dedication confirmed on exact Backyard Nature source",
   "photo_status":"PHYSICAL OPEN-RIGHTS LIVE FIELD HABIT — no true ligule, root-crown or sterile hood claim",
   "sha256":sha,"pixels":pixels
  })
  panels[idx]["image_url"]=str(dest)
  panels[idx]["image_fit"]="contain"
  panels[idx]["photo_status"]="Locally hosted author-public-domain Uvalde photo; whole tuft and attached flowering heads are visible, but roots/inner ligule not exposed; no new arrows."
  s["lane5_local_uvalde_habit_20261027"]={"stage":"FIELD_READY_PHOTO_GAPS","photo_role":"Actual living in-soil flowering tufts (not uprooted or measured)","source":SRC_PAGE,"local_file":REL,"photo_index":idx,
   "unresolved":["Opened true membranous ligule at mm scale","Verified exposed roots and connected crown","Separately dissected, calibrated upper sterile hood and fertile awn"]}
  CARD.write_text(json.dumps(s,indent=2,ensure_ascii=False)+"\n")
  OUT["new_local_photos"].append({"file":str(dest),"bytes":len(binary),"pixels":pixels,"sha256":sha,"gallery_index":idx})
except Exception as ex:OUT["warnings"].append("HELD: "+str(ex))
REPORT.parent.mkdir(exist_ok=True)
REPORT.write_text(json.dumps(OUT,indent=2)+"\n")
print(json.dumps(OUT))
