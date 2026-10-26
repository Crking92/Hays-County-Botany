#!/usr/bin/env python3
"""Import ONLY the Matt Lavin Flickr 3796749425 original after verifying Commons
photo-level CC BY-SA 2.0 metadata. No general Flickr allowlist or other photo.
Wikimedia image CDN was replying 429; fail closed on any mismatch or failed download.
"""
import hashlib, io, json, pathlib, re
import requests
from PIL import Image, ImageOps

title="File:Bouteloua curtipendula (3796749425).jpg"
flickr_url="https://live.staticflickr.com/3453/3796749425_fc743fd170_o.jpg"
api="https://commons.wikimedia.org/w/api.php"
headers={"User-Agent":"HaysCountyBotanyLicensedImageResearch/1.0 (rights-check for noncommercial botany learner)"}
r=requests.get(api,params={
    "action":"query","format":"json","prop":"imageinfo","titles":title,
    "iiprop":"extmetadata|size"
},headers=headers,timeout=40)
r.raise_for_status()
pages=list(r.json()["query"]["pages"].values())
if len(pages)!=1 or "imageinfo" not in pages[0]:
    raise SystemExit("Commons metadata missing")
info=pages[0]["imageinfo"][0]
meta=info["extmetadata"]
clean=lambda k: re.sub("<[^>]+>"," ",meta.get(k,{}).get("value","")).strip()
if clean("LicenseShortName").upper()!="CC BY-SA 2.0":
    raise SystemExit("Exact Commons photo license mismatch")
lic=clean("LicenseUrl").lower().rstrip("/")
if lic not in ("https://creativecommons.org/licenses/by-sa/2.0",
               "http://creativecommons.org/licenses/by-sa/2.0"):
    raise SystemExit("CC BY-SA version URL mismatch")
if "matt lavin" not in clean("Artist").lower():
    raise SystemExit("Verified Commons creator name mismatch")
if info.get("width",0)<1400 or info.get("height",0)<1600:
    raise SystemExit("Commons source unexpectedly small")
source=requests.get(flickr_url,headers={**headers,"Referer":"https://www.flickr.com/"},
                    timeout=70,allow_redirects=True)
source.raise_for_status()
from urllib.parse import urlparse
if (urlparse(source.url).scheme!="https" or
    urlparse(source.url).hostname!="live.staticflickr.com"):
    raise SystemExit("Flickr file redirected outside exact approved CDN")
if len(source.content)>16000000 or len(source.content)<120000:
    raise SystemExit("Unexpected source image size")
im=Image.open(io.BytesIO(source.content))
im.verify()
im=Image.open(io.BytesIO(source.content))
im=ImageOps.exif_transpose(im).convert("RGB")
if min(im.size)<1200:
    raise SystemExit("Low resolution; no ligule macro")
im.thumbnail((2400,2400))
out=pathlib.Path("review_photo")
out.mkdir(exist_ok=True)
buf=io.BytesIO()
im.save(buf,"JPEG",quality=88,optimize=True)
data=buf.getvalue()
(out/"candidate.jpg").write_bytes(data)
evidence={
    "commons_file":title,
    "taxon_proposed":"Bouteloua curtipendula",
    "commons_page":pages[0]["title"],
    "original_url":"https://commons.wikimedia.org/wiki/File:Bouteloua_curtipendula_(3796749425).jpg",
    "actual_download_url":source.url,
    "source_photo":"https://www.flickr.com/photos/plant_diversity/3796749425/",
    "creator_unverified_html":clean("Artist"),
    "license_short":clean("LicenseShortName"),
    "license_url":clean("LicenseUrl"),
    "image_sha256":hashlib.sha256(data).hexdigest(),
    "image_dimensions":list(im.size),
    "gps_exif_removed":True,
    "manual_taxonomic_and_rights_review_required":True,
    "public_site_published":False,
    "original_license_modification_note":"Exact source resized/rotated based on EXIF and converted to EXIF-free JPEG; CC BY-SA 2.0 retained",
}
(out/"evidence.json").write_text(json.dumps(evidence,indent=2)+"\n")
print(json.dumps({"source":"Flickr original after Commons rights check","sha256":evidence["image_sha256"],"size":evidence["image_dimensions"],"review_only":True}))
