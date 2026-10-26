#!/usr/bin/env python3
"""Archive exactly two Jim Conrad public-domain Panicum hallii images from Uvalde.
Confirm the owner's express PD policy and original species article.
Do not infer roots or label individual glumes; reconcile species.json SHA.
"""
import base64,hashlib,io,json,os,pathlib,time,urllib.parse
import requests
from PIL import Image,ImageOps
REPO=os.environ["GITHUB_REPOSITORY"]; TOKEN=os.environ["GITHUB_TOKEN"]
BRANCH=os.environ.get("GITHUB_REF_NAME","main")
PAGE="https://www.backyardnature.net/n/h/panic-2.htm"
RIGHTS="https://www.backyardnature.net/j/copyrite.htm"
BASE="content/taxa/Poaceae/Panicum/panicum-hallii/"
CARD=BASE+"species.json"
SOURCES=[
 ("https://www.backyardnature.net/n/14/140831pm.jpg","jim-conrad-hallii-edwards-limestone-tufts-public-domain.jpg",
  "Actual small perennial leafy clumps growing among Edwards Plateau limestone, panicles and dense basal curled leaves; crowns remain soil-covered, not excavated."),
 ("https://www.backyardnature.net/n/14/140831pp.jpg","jim-conrad-hallii-true-hairy-ligule-public-domain.jpg",
  "Actual attached leaf-sheath junction with source-described white tuft of TRUE ligule hairs projecting from sheath rim and smoother cylindrical sheath below; no millimeter scale.")
]
s=requests.Session()
s.headers.update({"User-Agent":"HaysCountyBotany-OriginalRightsCheckedPhotoImporter/1.0"})
rights=s.get(RIGHTS,timeout=40);rights.raise_for_status()
if "i, jim conrad, hereby place into the public domain all images produced by myself" not in rights.text.lower():
 raise SystemExit("Source owner public-domain promise missing")
pg=s.get(PAGE,timeout=40);pg.raise_for_status()
t=pg.text.lower()
if "jim conrad" not in t or "panicum hallii" not in t or "white fringe of hairs is the ligule" not in t:
 raise SystemExit("Hallii exact source article species/author/ligule mismatch")
for url,_,_ in SOURCES:
 if pathlib.PurePosixPath(urllib.parse.urlparse(url).path).name not in t:
  raise SystemExit("Pinned source image not in exact article")
s.headers.update({"Authorization":"Bearer "+TOKEN,"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"})
ROOT=f"https://api.github.com/repos/{REPO}/contents/"
def get(path):
 r=s.get(ROOT+urllib.parse.quote(path,safe="/"),params={"ref":BRANCH},timeout=40)
 if r.status_code==404:return None
 r.raise_for_status();return r.json()
def put(path,data,sha,msg):
 req={"message":msg,"content":base64.b64encode(data).decode(),"branch":BRANCH}
 if sha:req["sha"]=sha
 r=s.put(ROOT+urllib.parse.quote(path,safe="/"),json=req,timeout=80)
 if r.status_code in (409,422):return False
 r.raise_for_status();return True
for url,name,role in SOURCES:
 r=s.get(url,timeout=70);r.raise_for_status()
 if urllib.parse.urlparse(r.url).hostname not in ("www.backyardnature.net","backyardnature.net"):
  raise SystemExit("Original host redirected")
 if len(r.content)<8000 or len(r.content)>12000000 or not r.content.startswith(bytes.fromhex("ffd8")):
  raise SystemExit("Source bytes invalid")
 im=Image.open(io.BytesIO(r.content));im.verify()
 im=Image.open(io.BytesIO(r.content))
 im=ImageOps.exif_transpose(im).convert("RGB")
 if min(im.size)<220:raise SystemExit("Not enough detail for gross features")
 out=io.BytesIO();im.save(out,"JPEG",quality=92,optimize=True)
 raw=out.getvalue()
 filename=BASE+"images/"+name
 prior=get(filename)
 if not prior:
  if not put(filename,raw,None,"Lane 1 archive Jim Conrad public-domain Uvalde Panicum hallii "+name):
   prior=get(filename)
   if not prior or prior.get("size")!=len(raw):raise SystemExit("Concurrent photo upload differs; preserve")
 elif prior.get("size")!=len(raw):
  raise SystemExit("Existing name has different data, preserve")
 photo={"file":"images/"+name,"role":role,"creator":"Jim Conrad",
        "license":"Public domain — original photographer's express release",
        "license_url":RIGHTS,
        "source_page":PAGE,"source_original":url,
        "source_locality":"Frio Canyon, northern Uvalde County, Texas, Edwards Limestone",
        "public_reuse":"yes — Jim Conrad expressly dedicates own site images to public domain",
        "modifications":"Sanitized EXIF/GPS metadata and re-encoded RGB JPEG; no subject alteration",
        "image_sha256":hashlib.sha256(raw).hexdigest(),
        "image_dimensions":list(im.size),
        "photo_review":"Exact Uvalde source title and anatomy caption confirmed; annotation awaits physical archived pixel review. Roots are not exposed; ligule hairs cannot be measured."}
 panel={"label":"UVALDE PD — "+("actual ligule hair fringe, smooth sheath" if "ligule" in name else "rocky-habitat compact basal grass tufts"),
        "scientific_name":"Panicum hallii","image_url":filename,"image_fit":"contain",
        "creator":"Jim Conrad","license":"Public domain (author original)","license_url":RIGHTS,
        "source_page":PAGE,"source_original":url,
        "image_role":role,
        "caption":role+" These are source-identified Uvalde County photographs, not a local Hays voucher.",
        "why_it_matters":"A genuine source-labelled field clue absent from the previous Hall's panicgrass species gallery.",
        "markers":[],
        "photo_status":"Actual photographer-source PD JPEG saved locally with no metadata; anatomy arrow and mobile QA pending."}
 for attempt in range(6):
  c=get(CARD)
  if not c:raise SystemExit("Card absent")
  d=json.loads(base64.b64decode(c["content"]))
  images=d.setdefault("images",[]);items=d.setdefault("visual_comparison",{}).setdefault("items",[])
  a=[x for x in images if x.get("file")==photo["file"]]
  b=[x for x in items if x.get("image_url")==filename]
  if len(a)==len(b)==1:print("ALREADY_INSTALLED",filename);break
  if a or b:raise SystemExit("Half installed or duplicate record, manual review")
  images.append(photo)
  idx=next((i for i,x in enumerate(items) if x.get("scientific_name")!="Panicum hallii"),len(items))
  items.insert(idx,panel)
  d.setdefault("curation_status",{})["photo_files_present"]=sum(str(x.get("file","")).startswith("images/") for x in images)
  d["curation_status"]["lane1_hallii_conrad_original_pd_20261026"]="SOURCE_RIGHTS_AND_BYTES_ARCHIVED_PHOTO_PIXEL_REVIEW_PENDING"
  content=(json.dumps(d,ensure_ascii=False,indent=2)+"\n").encode()
  if put(CARD,content,c["sha"],"Lane 1 install Uvalde public-domain Hall's panicgrass "+name):
   print("ARCHIVED_GALLERY",filename,len(raw));break
  time.sleep(1+attempt)
 else:raise SystemExit("Card changed in six attempts; stored photo preserved")
