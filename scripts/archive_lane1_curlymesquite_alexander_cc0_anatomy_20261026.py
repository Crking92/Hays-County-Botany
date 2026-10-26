#!/usr/bin/env python3
"""Strict source/CC0 importer for TWO distinct Patrick Alexander curlymesquite anatomy photos.
Physical pixels sourced from Wikimedia original JPEG; no location metadata retained.
These are Arizona/New Mexico photographer images (Hidalgo County, New Mexico), NOT Hays vouchers.
Do not claim each microscopic 3-member fascicle can be counted from these views.
"""
import base64, hashlib, io, json, os, re, time, urllib.parse, html
import requests
from PIL import Image, ImageOps

REPO=os.environ["GITHUB_REPOSITORY"]
TOKEN=os.environ["GITHUB_TOKEN"]
BRANCH=os.environ.get("GITHUB_REF_NAME","main")
ROOT=f"https://api.github.com/repos/{REPO}/contents/"
BASE="content/taxa/Poaceae/Hilaria/hilaria-belangeri/"
CARD=BASE+"species.json"
CC0="https://creativecommons.org/publicdomain/zero/1.0/"
SOURCES=[
  {
   "suffix":2,"id":"15902154802",
   "source_image":"https://upload.wikimedia.org/wikipedia/commons/4/47/Hilaria_belangeri_-_Flickr_-_aspidoscelis_%282%29.jpg",
   "name":"patrick-alexander-curlymesquite-mature-attached-head-cc0.jpg",
   "label":"MATURE ATTACHED HEAD — opened pale spikelet groups on zigzag axis (CC0)",
   "role":"Close-up of TWO authentic attached mature curlymesquite heads; dry glumelike pieces radiate from rachis, some areas of axis exposed. A whole head rather than detached individual spikelet.",
   "caption":"Patrick Alexander photographed two mature Hilaria belangeri flowering heads in Hidalgo County, New Mexico. Compare the compact left head with the more spread-out pale papery groups on the right. Pointed narrow parts and the rachis are visible, but their identity as specific glumes/lemmas and the exact 3-spikelet group boundaries are NOT established by this image alone.",
   "why":"Teaches mature flowering architecture while keeping non-visible microscopic boundaries unannotated.",
   "markers":[{"label":"Mature attached flowering head","label_x":3,"label_y":10,"target_x":24,"target_y":38},{"label":"Open papery flowering units","label_x":73,"label_y":8,"target_x":64,"target_y":29}],
  },
  {
   "suffix":3,"id":"15716751439",
   "source_image":"https://upload.wikimedia.org/wikipedia/commons/e/e0/Hilaria_belangeri_-_Flickr_-_aspidoscelis_%283%29.jpg",
   "name":"patrick-alexander-curlymesquite-detached-spikelet-clusters-cc0.jpg",
   "label":"DETACHED MATURE CLUSTERS — real papery Hilaria flowering units on palm (CC0)",
   "role":"Two detached intact pale mature spikelet clusters with sharply visible branching, awnlike projections and a person's hand for size. DO NOT identify exact lemma/glume/sterile-spikelet boundaries without expert dissection.",
   "caption":"Patrick Alexander's genuine Hilaria belangeri hand-scale close-up shows TWO detached, papery, multi-part mature units. Observe their stout attachment point, projecting narrow parts and apparent branches against the fingers. Photo resolves whole clusters, NOT the exact fertile-versus-staminate three-spikelet arrangement, and this is NOT a true extracted individual lemma close-up.",
   "why":"First strong locally archived visual lesson of detached curlymesquite flowering units, complementing the connected stolon and node-hair photographs.",
   "markers":[{"label":"Detached flowering cluster","label_x":1,"label_y":6,"target_x":38,"target_y":40},{"label":"Second detached cluster","label_x":82,"label_y":15,"target_x":75,"target_y":48}],
  },
]
ss=requests.Session()
ss.headers.update({"User-Agent":"HaysCountyBotany-ExactCommonsCC0ImageReview/1.0 (educational field identification)"})
for source in SOURCES:
    filename=f"Hilaria_belangeri_-_Flickr_-_aspidoscelis_({source['suffix']}).jpg"
    page="https://commons.wikimedia.org/wiki/File:"+urllib.parse.quote(filename, safe="()_-")
    response=ss.get(page,timeout=45)
    response.raise_for_status()
    visible=" ".join(html.unescape(re.sub(r"<[^>]+>"," ",response.text)).lower().split())
    for term in ("hilaria belangeri","patrick alexander","cc0 1.0 universal public domain dedication","flickreviewr 2","hidalgo county, new mexico",source["id"]):
        if term not in visible and term not in response.text.lower():
            raise SystemExit(f"Individual source verification failed: {source['suffix']} {term}")
    source["page"]=page
    response=ss.get(source["source_image"],timeout=95,allow_redirects=True)
    response.raise_for_status()
    dest=urllib.parse.urlparse(response.url)
    if dest.scheme!="https" or dest.hostname!="upload.wikimedia.org":
        raise SystemExit("Untrusted Commons original redirect")
    raw=response.content
    if not 50_000<len(raw)<10_000_000 or not raw.startswith(bytes.fromhex("ffd8")):
        raise SystemExit("Invalid or missing high-resolution original JPEG")
    im=Image.open(io.BytesIO(raw));im.verify()
    im=ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert("RGB")
    if min(im.size)<1100:
        raise SystemExit("High-resolution source too small for macro role")
    im.thumbnail((2800,2800),Image.Resampling.LANCZOS)
    clean=io.BytesIO()
    im.save(clean,"JPEG",quality=91,optimize=True)
    source["raw"]=clean.getvalue()
    source["dim"]=list(im.size)
    source["sha256"]=hashlib.sha256(source["raw"]).hexdigest()
    source["file"]="images/"+source["name"]
    source["path"]=BASE+source["file"]
    print("SOURCE_RIGHTS_PIXELS_CONFIRMED",source["suffix"],source["dim"],source["sha256"])
# Only after both image-level rights and ID checks, perform repo writes.
ss.headers.update({"Authorization":"Bearer "+TOKEN,"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"})
def get(path):
    q=ss.get(ROOT+urllib.parse.quote(path,safe="/"),params={"ref":BRANCH},timeout=45)
    if q.status_code==404:return None
    q.raise_for_status();return q.json()
def put(path,raw,sha,msg):
    body={"content":base64.b64encode(raw).decode(),"message":msg,"branch":BRANCH}
    if sha:body["sha"]=sha
    q=ss.put(ROOT+urllib.parse.quote(path,safe="/"),json=body,timeout=100)
    if q.status_code in (409,422):return False
    q.raise_for_status();return True

for source in SOURCES:
    prior=get(source["path"])
    if not prior:
        if not put(source["path"],source["raw"],None,"Lane 1 archive source-verified CC0 curlymesquite flowering anatomy "+str(source["suffix"])):
            prior=get(source["path"])
            if not prior or prior.get("size")!=len(source["raw"]):
                raise SystemExit("Image upload conflict")
    elif prior.get("size")!=len(source["raw"]):
        raise SystemExit("Existing same-name JPEG is different; never overwrite")

def record(source):
    return {
     "file":source["file"],"role":source["role"],"creator":"Patrick Alexander",
     "license":"CC0 1.0","license_url":CC0,
     "source_page":source["page"],"source_original":source["source_image"],
     "source_flickr_photo_id":source["id"],"source_taxon_name":"Hilaria belangeri",
     "source_locality":"Owl Canyon, Peloncillo Mountains, Hidalgo County, New Mexico (NOT Hays County)",
     "public_reuse":"yes — original Flickr CC0 checked via Wikimedia Commons individual file and FlickreviewR",
     "modifications":"Original JPEG orientation applied, resized only if >2800px, RGB reencoded, EXIF/GPS removed; no subject crop",
     "image_sha256":source["sha256"],"image_dimensions":source["dim"],
     "photo_review":"Authentic photographed structures; see panel role and cautious markers, no claimed isolated individual glume/lemma or countable fertile versus staminate triad."
    }
def panel(source):
    return {"label":source["label"],"scientific_name":"Hilaria belangeri",
      "image_url":source["path"],"image_fit":"contain","image_role":source["role"],
      "caption":source["caption"],"why_it_matters":source["why"],
      "creator":"Patrick Alexander","license":"CC0 1.0","license_url":CC0,
      "source_page":source["page"],"source_original":source["source_image"],
      "markers":source["markers"],
      "photo_status":"Physical source-verified CC0 macro archived; arrows on gross clearly visible structures only, 3-member microscopic anatomy and live mobile QA still pending."}
for attempt in range(7):
    current=get(CARD)
    if not current:raise SystemExit("Canonical Hilaria belangeri species.json absent")
    d=json.loads(base64.b64decode(current["content"]))
    if d.get("id")!="hilaria-belangeri":raise SystemExit("Wrong canonical species id")
    im=d.setdefault("images",[]); gallery=d.setdefault("visual_comparison",{}).setdefault("items",[])
    changed=False
    for s in SOURCES:
        mi=[x for x in im if x.get("file")==s["file"]]
        mg=[x for x in gallery if x.get("image_url")==s["path"]]
        if len(mi)==len(mg)==1:continue
        if mi or mg:raise SystemExit("Partial or duplicate macro/gallery state; no overwrite")
        im.append(record(s))
        idx=next((i for i,x in enumerate(gallery) if x.get("scientific_name")!="Hilaria belangeri"),len(gallery))
        gallery.insert(idx,panel(s))
        changed=True
    if not changed:
        print("TWO_AUTHENTIC_CC0_PANELS_ALREADY_PRESENT")
        break
    d.setdefault("curation_status",{})["photo_files_present"]=sum(str(x.get("file","")).startswith("images/") for x in im)
    d["curation_status"]["lane1_alexander_curlymesquite_anatomy_20261026"]="ATTACHED_HEAD_AND_DETACHED_GROUPS_CC0_ARCHIVED_ROOTED_NODE_LIGULE_TRIAD_DISSECTION_GAPS"
    # Intentional conservative status: NO invented anatomical completion.
    raw=(json.dumps(d,ensure_ascii=False,indent=2)+"\n").encode()
    if put(CARD,raw,current["sha"],"Lane 1 add two genuinely distinct CC0 curlymesquite head and detached cluster panels"):
        print("BOTH_CC0_MACROS_ARCHIVED_AND_CANONICAL_GALLERY_UPDATED")
        break
    time.sleep(attempt+1)
else:raise SystemExit("Seven concurrent canonical edit collisions; photos archived, retry gallery later")
