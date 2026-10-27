#!/usr/bin/env python3
"""Archive exact Patrick Alexander CC0 Pleuraphis mutica photographed detached fascicles.
User's Lane 1 photo priority: aboveground ligule first, then flowering details, roots last.
Species synonym Pleuraphis mutica matches canonical Hilaria mutica; never invent sexed spikelet arrows.
"""
import base64
import hashlib
import html
import io
import json
import os
import re
import time
from urllib.parse import quote, urlparse
import requests
from PIL import Image, ImageOps

REPO=os.environ["GITHUB_REPOSITORY"]
TOKEN=os.environ["GITHUB_TOKEN"]
BRANCH=os.environ.get("GITHUB_REF_NAME","main")
PAGE="https://commons.wikimedia.org/wiki/File:Pleuraphis_mutica_-_Flickr_-_aspidoscelis.jpg"
ORIGINAL="https://upload.wikimedia.org/wikipedia/commons/b/b0/Pleuraphis_mutica_-_Flickr_-_aspidoscelis.jpg"
SOURCE_FLICKR="https://www.flickr.com/photos/aspidoscelis/49950304976/"
BASE="content/taxa/Poaceae/Hilaria/hilaria-mutica/"
NAME="patrick-alexander-tobosa-detached-flowering-clusters-cc0.jpg"
PHOTO=BASE+"images/"+NAME
CARD=BASE+"species.json"
LICENSE="https://creativecommons.org/publicdomain/zero/1.0/"

s=requests.Session()
s.headers.update({"User-Agent":"HaysBotany-ExactIndividualPhotoPublicLicenseVerifier/1.0"})
resp=s.get(PAGE,timeout=45)
resp.raise_for_status()
txt=" ".join(html.unescape(re.sub(r"<[^>]+>"," ",resp.text)).lower().split())
for term in ("pleuraphis mutica","patrick alexander","cc0 1.0 universal public domain dedication","flickreviewr 2","doña ana county","49950304976"):
    if term not in txt:
        raise SystemExit("Original Wikimedia species, photo ID, author or CC0 license verification failed: "+term)
if "Pleuraphis_mutica_-_Flickr_-_aspidoscelis.jpg" not in resp.text:
    raise SystemExit("Exact Commons file name not in photo source")
# Wikimedia CDN may rate-limit GitHub's shared runner IP (HTTP 429).
# This file's Commons structured data identifies the photographer's exact
# 49950304976 original at Flickr CDN; same image ID and source photographer.
# Never fall back to a search thumbnail or a different taxon.
FALLBACK="https://live.staticflickr.com/65535/49950304976_dcb6bb6cbd_o.jpg"
raw=None
used_original=None
for url,host in ((ORIGINAL,"upload.wikimedia.org"),(FALLBACK,"live.staticflickr.com")):
    try:
        response=s.get(url,timeout=85,allow_redirects=True)
        if response.status_code in (403,429,500,502,503,504):
            print("SOURCE_CDN_NOT_AVAILABLE",host,response.status_code)
            continue
        response.raise_for_status()
        u=urlparse(response.url)
        if u.scheme!="https" or u.hostname!=host:
            raise SystemExit("Unexpected original photo redirect host")
        if not response.content.startswith(b"\\xff\\xd8".decode("unicode_escape").encode("latin1")):
            raise SystemExit("Non-JPEG returned")
        raw=response.content
        used_original=url
        break
    except requests.RequestException as exc:
        print("SOURCE_CDN_REQUEST_ERROR",host,str(exc)[:160])
if raw is None:
    raise SystemExit("Both confirmed original photo hosts unavailable; no image published")
if not 50_000<len(raw)<8_000_000 or raw[:2]!=b"\xff\xd8":
    raise SystemExit("Missing or invalid original JPEG")
image=Image.open(io.BytesIO(raw));image.verify()
image=ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert("RGB")
if image.width!=1800 or image.height!=1200:
    raise SystemExit("Source pixel dimensions changed; arrow source review needs repeat")
buf=io.BytesIO()
image.save(buf,"JPEG",quality=90,optimize=True)
clean=buf.getvalue()
sha=hashlib.sha256(clean).hexdigest()
print("SOURCE_PHOTO_LICENSE_AND_IMAGE_VERIFIED",len(clean),image.size,sha)

s.headers.update({
 "Authorization":"Bearer "+TOKEN,
 "Accept":"application/vnd.github+json",
 "X-GitHub-Api-Version":"2022-11-28"
})
ROOT="https://api.github.com/repos/"+REPO+"/contents/"
def get(path):
    response=s.get(ROOT+quote(path,safe="/"),params={"ref":BRANCH},timeout=45)
    if response.status_code==404:return None
    response.raise_for_status()
    return response.json()
def put(path,data,existing_sha,message):
    payload={"message":message,"branch":BRANCH,"content":base64.b64encode(data).decode()}
    if existing_sha:payload["sha"]=existing_sha
    result=s.put(ROOT+quote(path,safe="/"),json=payload,timeout=95)
    if result.status_code in (409,422):return False
    result.raise_for_status()
    return True
old=get(PHOTO)
if old:
    if old.get("size")!=len(clean):
        raise SystemExit("Existing same-name photo has different bytes; don't overwrite")
elif not put(PHOTO,clean,None,"Lane 1 archive genuine CC0 tobosa detached mature flowering fascicles"):
    old=get(PHOTO)
    if not old or old.get("size")!=len(clean):
        raise SystemExit("Concurrent file conflict; preserve")
record={
 "file":"images/"+NAME,
 "role":"Genuine species-source detached Hilaria mutica / Pleuraphis mutica mature papery flowering clusters showing radiating bracts and basal hair tufts; NOT ligule and NOT true individually dissected central-vs-lateral spikelets.",
 "creator":"Patrick Alexander",
 "license":"CC0 1.0","license_url":LICENSE,"source_page":PAGE,"source_original":used_original,
 "source_flickr_photo":SOURCE_FLICKR,
 "source_taxon_name":"Pleuraphis mutica","canonical_taxon":"Hilaria mutica",
 "source_locality":"Jornada Experimental Range, Doña Ana County, New Mexico, 2011 (not Hays County)",
 "public_reuse":"Yes, source-specific CC0 1.0 reviewed on Wikimedia Commons via FlickrReviewR 2",
 "modifications":"JPEG re-encoded RGB with original composition and EXIF/GPS removed; no artificial anatomy or crop",
 "image_dimensions":list(image.size),"image_sha256":sha,
 "photo_review":"Source original pixel review: real detached branching flower units and silk/tuft hairs visible at macro scale, but exact three separate spikelet members, glume vs lemma, and 1-mm ligule are NOT demonstrable."
}
panel={
 "label":"MATURE TOBOSA FASCICLES — real detached papery flowering groups (CC0)",
 "scientific_name":"Hilaria mutica","image_url":PHOTO,"image_fit":"contain",
 "creator":"Patrick Alexander","license":"CC0 1.0","license_url":LICENSE,
 "source_page":PAGE,"source_original":ORIGINAL,
 "image_role":"Actual mature detached multi-part flowering clusters scattered on cracked soil, with basal tufts of white hair and separate papery pointed structures visible.",
 "caption":"Patrick Alexander's CC0 photograph of TOBOSA (= Pleuraphis mutica) shows several detached mature spikelet groups on the ground. Look at the radiating papery parts and tufts of hairs at their base. These are whole fascicles, NOT separate isolated glumes/lemmas, and the exact male vs fertile three-member positions are not proven without dissection. New Mexico locality, not a Texas voucher.",
 "why_it_matters":"Adds real photographed aboveground reproductive anatomy that the earlier whole-head and habitat photographs cannot provide. Complements curlymesquite's separate mature-cluster panel.",
 "markers":[
  {"label":"Detached papery flowering group","label_x":5,"label_y":6,"target_x":23,"target_y":45},
  {"label":"Another mature flowering group","label_x":65,"label_y":12,"target_x":53,"target_y":39}
 ],
 "photo_status":"Original source/CC0/photographer and 1800x1200 image checked; two arrows on conspicuous GROSS clusters only, microscopic anatomy and live mobile QA not verified."
}
for attempt in range(7):
    item=get(CARD)
    if item is None:raise SystemExit("Canonical tobosa card not found")
    d=json.loads(base64.b64decode(item["content"]))
    if d.get("id")!="hilaria-mutica":raise SystemExit("Wrong species id")
    im=d.setdefault("images",[])
    gal=d.setdefault("visual_comparison",{}).setdefault("items",[])
    a=[x for x in im if x.get("file")==record["file"]]
    b=[x for x in gal if x.get("image_url")==PHOTO]
    if len(a)==len(b)==1:
        print("ALREADY_INSTALLED",PHOTO);break
    if a or b:raise SystemExit("Partial/duplicate record; do not overwrite")
    im.append(record)
    index=next((i for i,x in enumerate(gal) if x.get("scientific_name")!="Hilaria mutica"),len(gal))
    gal.insert(index,panel)
    d.setdefault("curation_status",{})["photo_files_present"]=sum(str(x.get("file","")).startswith("images/") for x in im)
    d["curation_status"]["lane1_20261027_tobosa_cc0_flowering_closeshot"]="REPRODUCTIVE_MACRO_ARCHIVED_TRUE_LIGULE_AND_SEXED_TRIAD_STILL_MISSING"
    content=(json.dumps(d,indent=2,ensure_ascii=False)+"\n").encode()
    if put(CARD,content,item["sha"],"Lane 1 add source-verified CC0 real tobosa detached flowering groups to learner"):
        print("ARCHIVED_AND_ADDED_TO_CANONICAL_TOBOSA_GALLERY",PHOTO,sha)
        break
    time.sleep(attempt+1)
else: raise SystemExit("Concurrent edit collisions, photo archived but gallery needs review")
