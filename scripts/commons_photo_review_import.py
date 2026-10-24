#!/usr/bin/env python3
"""Download one Wikimedia Commons File: image into a review artifact; never publish directly."""
import argparse, io, json, pathlib, re, hashlib, urllib.parse, time
import requests
from PIL import Image, ImageOps
from xml.etree import ElementTree as ET

parser=argparse.ArgumentParser()
parser.add_argument("--file-title",required=True,help="Exact Wikimedia Commons File: title")
parser.add_argument("--taxon",required=True,help="Canonical scientific name for proposed match")
parser.add_argument("--output",default="review_photo")
parser.add_argument("--max-edge",type=int,default=2400,help="Longest output dimension; higher for labeled wide anatomy plates")
a=parser.parse_args()
if not 800<=a.max_edge<=12000:raise SystemExit("Invalid max edge")
assert a.file_title.startswith("File:"), "Use an exact Commons File: title"
assert re.fullmatch(r"[A-Za-z× .'-]{4,120}",a.taxon), "Unexpected taxon syntax"
api="https://commons.wikimedia.org/w/api.php"
headers={"User-Agent":"HaysCountyBotanyPhotoReview/1.0 (manual educational photo rights audit)"}
def fetch_with_limited_retry(url, *, params=None, timeout=45):
    """Retry at most twice on temporary upstream throttling; fail closed on rights or other HTTP errors."""
    for attempt in range(3):
        response=requests.get(url,params=params,headers=headers,timeout=timeout)
        if response.status_code not in (429,500,502,503,504):
            response.raise_for_status()
            return response
        if attempt==2:
            response.raise_for_status()
        pause=min(12, 2**attempt*3)
        retry_after=response.headers.get("Retry-After","")
        if retry_after.isdigit():pause=min(15,max(pause,int(retry_after)))
        time.sleep(pause)
    raise RuntimeError("Unreachable")
r=fetch_with_limited_retry(api,params={"action":"query","format":"json","prop":"imageinfo","titles":a.file_title,"iiprop":"url|extmetadata|size"},timeout=45)
pages=list(r.json()["query"]["pages"].values())
if len(pages)!=1 or "imageinfo" not in pages[0]:raise SystemExit("Commons file missing")
info=pages[0]["imageinfo"][0]
meta=info.get("extmetadata",{})
clean=lambda key: re.sub("<[^>]+>"," ",meta.get(key,{}).get("value","")).strip()
license_short=clean("LicenseShortName")
license_url=clean("LicenseUrl")
# A prefix search for "CC BY" accidentally accepts CC BY-NC / CC BY-ND.
# Fail closed: Commons short name must be an exact public-site-approved license.
normalized_license=re.sub(r"\\s+"," ",license_short).strip()
approved_license=bool(re.fullmatch(r"(?:CC0(?: 1\\.0)?|CC BY(?:-SA)? [1-9][0-9]*(?:\\.[0-9]+)?|Public domain)",normalized_license,re.I))
if not approved_license:
    raise SystemExit(f"License not project-approved: {normalized_license}; no download")
# Respect only unmodified attribution/share-alike licensing types; no NC/ND variants.
if re.search(r"\\b(?:NC|ND)\\b",normalized_license,re.I):
    raise SystemExit("Restricted NC/ND licensing is excluded from public-site photo importer")
url=info["url"]
if urllib.parse.urlparse(url).hostname not in ("upload.wikimedia.org","commons.wikimedia.org"):
    raise SystemExit("Unexpected download host")
image=fetch_with_limited_retry(url,timeout=120)
if len(image.content)>35000000:raise SystemExit("File too large")
source=Image.open(io.BytesIO(image.content))
source.verify()
source=Image.open(io.BytesIO(image.content))
source=ImageOps.exif_transpose(source).convert("RGB")
source.thumbnail((a.max_edge,a.max_edge))
out=pathlib.Path(a.output)
out.mkdir(parents=True,exist_ok=True)
buf=io.BytesIO()
source.save(buf,"JPEG",quality=87,optimize=True)
data=buf.getvalue()
(out/"candidate.jpg").write_bytes(data)
record={"taxon_proposed":a.taxon,"commons_file":a.file_title,"commons_page":pages[0].get("title"),"original_url":url,"creator_unverified_html":clean("Artist"),"attribution_unverified_html":clean("Attribution"),"license_short":license_short,"license_url":license_url,"copyright_unverified_html":clean("Credit"),"image_sha256":hashlib.sha256(data).hexdigest(),"image_dimensions":list(source.size),"gps_exif_removed":True,"manual_taxonomic_and_rights_review_required":True,"public_site_published":False,"original_license_modification_note":"Resized and converted to JPEG; EXIF removed"}
(out/"evidence.json").write_text(json.dumps(record,indent=2)+"\n")
print(json.dumps({"sha256":record["image_sha256"],"size":record["image_dimensions"],"review_only":True}))
