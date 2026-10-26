#!/usr/bin/env python3
"""Archive only the Forest Service's photo-credit-verified Sue Carnahan
Hilaria belangeri stolons photograph (CC BY 4.0). Fail closed on source,
image metadata or concurrent edits; keep existing source labels and rights.
"""
import base64, hashlib, io, json, os, re, time, urllib.parse
import requests
from PIL import Image, ImageOps

REPO=os.environ["GITHUB_REPOSITORY"]
TOKEN=os.environ["GITHUB_TOKEN"]
BRANCH=os.environ.get("GITHUB_REF_NAME","main")
SOURCE="https://research.fs.usda.gov/feis/species-reviews/hilbel"
IMG="https://research.fs.usda.gov/sites/default/files/2025-06/feis-hilbel_stolons.jpeg"
LICENSE="https://creativecommons.org/licenses/by/4.0/"
BASE="content/taxa/Poaceae/Hilaria/hilaria-belangeri/"
PATH=BASE+"images/sue-carnahan-feis-curlymesquite-stolons-cc-by4.jpg"
CARD=BASE+"species.json"
ss=requests.Session()
ss.headers.update({"User-Agent":"HaysCountyBotany-Lane1-SourceAttributionReview/1.0"})
r=ss.get(SOURCE,timeout=50)
r.raise_for_status()
text=re.sub("<[^>]*>"," ",r.text)
text=" ".join(text.split()).lower()
if not all(x in text for x in ("hilaria belangeri","sue carnahan","cc by 4.0","curly mesquite with stolons")):
    raise SystemExit("USFS exact species, source photographer or CC BY 4.0 image credit mismatch")
if "feis-hilbel_stolons.jpeg" not in r.text:
    raise SystemExit("The credited USFS article does not link the requested image")
q=ss.get(IMG,timeout=90)
q.raise_for_status()
final=urllib.parse.urlparse(q.url)
if final.scheme!="https" or final.hostname!="research.fs.usda.gov":
    raise SystemExit("Unexpected image redirect host")
if not 20_000<len(q.content)<15_000_000 or not q.content.startswith(bytes.fromhex("ffd8")):
    raise SystemExit("Source photo invalid or too large")
im=Image.open(io.BytesIO(q.content));im.verify()
im=Image.open(io.BytesIO(q.content))
im=ImageOps.exif_transpose(im).convert("RGB")
if min(im.size)<350:raise SystemExit("Not a usable morphological image")
im.thumbnail((2600,2600))
buff=io.BytesIO()
im.save(buff,"JPEG",quality=88,optimize=True)
data=buff.getvalue()
digest=hashlib.sha256(data).hexdigest()
ss.headers.update({"Authorization":"Bearer "+TOKEN,"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"})
API=f"https://api.github.com/repos/{REPO}/contents/"
def get(path):
    a=ss.get(API+urllib.parse.quote(path,safe="/"),params={"ref":BRANCH},timeout=40)
    if a.status_code==404:return None
    a.raise_for_status();return a.json()
def put(path,body,sha,msg):
    payload={"message":msg,"branch":BRANCH,"content":base64.b64encode(body).decode()}
    if sha:payload["sha"]=sha
    w=ss.put(API+urllib.parse.quote(path,safe="/"),json=payload,timeout=90)
    if w.status_code in (409,422):return False
    w.raise_for_status();return True
old=get(PATH)
if old:
    if old.get("size")!=len(data):raise SystemExit("Existing image differs, do not overwrite")
elif not put(PATH,data,None,"Lane 1 physically archive Sue Carnahan CC BY 4.0 curlymesquite stolons"):
    old=get(PATH)
    if not old or old.get("size")!=len(data):raise SystemExit("Conflict after photo upload")
im_record={
  "file":"images/sue-carnahan-feis-curlymesquite-stolons-cc-by4.jpg",
  "role":"Several source-labelled aboveground curlymesquite stolons radiating from a lifted basal tuft, bending at shoot-bearing nodes. Do not infer root attachment at each distant node until pixels show it.",
  "creator":"Sue Carnahan",
  "license":"CC BY 4.0","license_url":LICENSE,
  "source_page":SOURCE,"source_original":IMG,
  "source_photo_credit":"USDA Forest Service FEIS credits 'Photo by Sue Carnahan, iNaturalist (CC BY 4.0). Curly mesquite with stolons.'",
  "source_taxon":"Hilaria belangeri",
  "public_reuse":"Allowed with CC BY 4.0 photographer and Forest Service photo source attribution",
  "modifications":"Resized, RGB re-encoding and EXIF/GPS stripped, original composition unchanged",
  "image_sha256":digest,"image_dimensions":list(im.size),
  "photo_review":"Source-authenticated gross stolon growth only; no scale, confirmed hairy node micro or independent local Hays voucher."
}
panel={
  "label":"REAL STOLONS — lifted curlymesquite with connected runner shoots (CC BY 4.0)",
  "scientific_name":"Hilaria belangeri","image_url":PATH,"image_fit":"contain",
  "creator":"Sue Carnahan","license":"CC BY 4.0","license_url":LICENSE,
  "source_page":SOURCE,"source_original":IMG,
  "image_role":"Several connected wiry aboveground stems (stolons) emerging from the basal tuft and bending at growing shoots; photograph explicitly credited by US Forest Service.",
  "caption":"USDA Forest Service credits Sue Carnahan's actual curlymesquite stolon photograph. Observe the long wiry outward runners linking the basal plant to leafy offshoots; no rooted hair-bearing node can be declared without close pixel verification. This is not a Texas voucher.",
  "why_it_matters":"Unlike tobosa's mainly scaly belowground rhizomes, curlymesquite can connect its short tufts via long aboveground stolons.",
  "markers":[],
  "photo_status":"Physically archived source-labelled CC BY 4.0 JPEG with EXIF/GPS stripped. Pixel arrow placement, rooted-node test and public site mobile QA pending."
}
for attempt in range(6):
  c=get(CARD)
  if not c:raise SystemExit("Missing target species")
  d=json.loads(base64.b64decode(c["content"]))
  a=d.setdefault("images",[]);b=d.setdefault("visual_comparison",{}).setdefault("items",[])
  ia=[x for x in a if x.get("file")==im_record["file"]]
  ib=[x for x in b if x.get("image_url")==PATH]
  if len(ia)==len(ib)==1:print("ALREADY_INSTALLED",PATH);break
  if ia or ib:raise SystemExit("Partial canonical record, do not duplicate")
  a.append(im_record)
  ix=next((i for i,x in enumerate(b) if x.get("scientific_name")!="Hilaria belangeri"),len(b))
  b.insert(ix,panel)
  d.setdefault("curation_status",{})["photo_files_present"]=sum(str(x.get("file","")).startswith("images/") for x in a)
  d["curation_status"]["lane1_sue_carnahan_stolon_feis_20261026"]="SOURCE_RIGHTS_AND_IMAGE_ARCHIVED_PIXEL_REVIEW_PENDING"
  raw=(json.dumps(d,ensure_ascii=False,indent=2)+"\n").encode()
  if put(CARD,raw,c["sha"],"Lane 1 include source-attributed Sue Carnahan true curlymesquite stolon photograph"):
    print("ARCHIVED_AND_VISIBLE",PATH,len(data),digest)
    break
  time.sleep(attempt+1)
else:raise SystemExit("Six concurrent edits; image remains safely archived, gallery needs review")
