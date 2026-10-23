#!/usr/bin/env python3
"""Download one Wikimedia Commons File: image into a review artifact; never publish directly."""
import argparse, io, json, pathlib, re, hashlib, urllib.parse
import requests
from PIL import Image, ImageOps
from xml.etree import ElementTree as ET

parser=argparse.ArgumentParser()
parser.add_argument("--file-title",required=True,help="Exact Wikimedia Commons File: title")
parser.add_argument("--taxon",required=True,help="Canonical scientific name for proposed match")
parser.add_argument("--output",default="review_photo")
a=parser.parse_args()
assert a.file_title.startswith("File:"), "Use an exact Commons File: title"
assert re.fullmatch(r"[A-Za-z× .'-]{4,120}",a.taxon), "Unexpected taxon syntax"
api="https://commons.wikimedia.org/w/api.php"
headers={"User-Agent":"HaysCountyBotanyPhotoReview/1.0 (manual educational photo rights audit)"}
r=requests.get(api,params={"action":"query","format":"json","prop":"imageinfo","titles":a.file_title,"iiprop":"url|extmetadata|size"},headers=headers,timeout=45)
r.raise_for_status()
pages=list(r.json()["query"]["pages"].values())
if len(pages)!=1 or "imageinfo" not in pages[0]:raise SystemExit("Commons file missing")
info=pages[0]["imageinfo"][0]
meta=info.get("extmetadata",{})
clean=lambda key: re.sub("<[^>]+>"," ",meta.get(key,{}).get("value","")).strip()
license_short=clean("LicenseShortName")
license_url=clean("LicenseUrl")
if not (re.search(r"\bCC0\b|\bCC BY\b|Public domain",license_short,re.I) or "creativecommons.org/licenses/by/" in license_url or "creativecommons.org/publicdomain/" in license_url):
    raise SystemExit("License not recognized as project-approved; no download")
url=info["url"]
if urllib.parse.urlparse(url).hostname not in ("upload.wikimedia.org","commons.wikimedia.org"):
    raise SystemExit("Unexpected download host")
image=requests.get(url,headers=headers,timeout=120)
image.raise_for_status()
if len(image.content)>35000000:raise SystemExit("File too large")
source=Image.open(io.BytesIO(image.content))
source.verify()
source=Image.open(io.BytesIO(image.content))
source=ImageOps.exif_transpose(source).convert("RGB")
source.thumbnail((2400,2400))
out=pathlib.Path(a.output)
out.mkdir(parents=True,exist_ok=True)
buf=io.BytesIO()
source.save(buf,"JPEG",quality=87,optimize=True)
data=buf.getvalue()
(out/"candidate.jpg").write_bytes(data)
record={"taxon_proposed":a.taxon,"commons_file":a.file_title,"commons_page":pages[0].get("title"),"original_url":url,"creator_unverified_html":clean("Artist"),"attribution_unverified_html":clean("Attribution"),"license_short":license_short,"license_url":license_url,"copyright_unverified_html":clean("Credit"),"image_sha256":hashlib.sha256(data).hexdigest(),"image_dimensions":list(source.size),"gps_exif_removed":True,"manual_taxonomic_and_rights_review_required":True,"public_site_published":False,"original_license_modification_note":"Resized and converted to JPEG; EXIF removed"}
(out/"evidence.json").write_text(json.dumps(record,indent=2)+"\n")
print(json.dumps({"sha256":record["image_sha256"],"size":record["image_dimensions"],"review_only":True}))
