#!/usr/bin/env python3
"""Archive only John Kava's source-labelled Hilaria belangeri hairy-node photo.

Yavapai Extension explicitly permits educational use of its own photos with
photographer/site credit. That is a narrow educational permission, NOT CC.
The image demonstrates a WHITE-HAIRED CULM NODE, NOT a rooting stolon node.
Fail closed for unverified original attribution, rights, redirects or bad image.
"""
import base64
import hashlib
import html
import io
import json
import os
import re
import time
from urllib.parse import urlparse, quote

import requests
from PIL import Image, ImageOps

REPO = os.environ["GITHUB_REPOSITORY"]
TOKEN = os.environ["GITHUB_TOKEN"]
BRANCH = os.environ.get("GITHUB_REF_NAME", "main")
PAGE = "https://yavapaiplants.extension.arizona.edu/hilaria-belangeri"
RIGHTS = "https://yavapaiplants.extension.arizona.edu/about-website"
PHOTONAME = "Hilaria_belangeri_FNodewithtuft_20"
SOURCE_URLS = [
    "https://yavapaiplants.extension.arizona.edu/sites/default/files/Grasses/Images/" + PHOTONAME + ".jpg",
    "https://yavapaiplants.extension.arizona.edu/sites/default/files/styles/yp_card_image/public/Grasses/Images/" + PHOTONAME + ".jpg.webp?itok=YPeUfHjl",
]
BASE = "content/taxa/Poaceae/Hilaria/hilaria-belangeri/"
FILENAME = "john-kava-curlymesquite-hairy-node-educational.jpg"
REL = "images/" + FILENAME
PHOTO_PATH = BASE + REL
CARD = BASE + "species.json"
PERMISSION_ID = "YAVAPAI_JOHN_KAVA_HIBE_NODE_EDUCATIONAL_20261026"
LICENSE = "© John Kava — educational-use permission with credit (NOT Creative Commons)"

s = requests.Session()
s.headers.update({"User-Agent": "HaysBotany-SourceSpecificEducationalPhotoValidation/1.0"})
page_resp = s.get(PAGE, timeout=45)
page_resp.raise_for_status()
rights_resp = s.get(RIGHTS, timeout=45)
rights_resp.raise_for_status()
page_text = " ".join(html.unescape(re.sub(r"<[^>]*>", " ", page_resp.text)).lower().split())
rights_text = " ".join(html.unescape(re.sub(r"<[^>]*>", " ", rights_resp.text)).lower().split())
required_page = ("hilaria belangeri", "node with hairs", "john kava")
if not all(v in page_text for v in required_page):
    raise SystemExit("Exact species/node/photographer claim absent from original UArizona page")
if PHOTONAME.lower() not in page_resp.text.lower():
    raise SystemExit("Named original hairy-node photo no longer linked on species page")
if "images on this website may be freely used for educational purposes" not in rights_text:
    raise SystemExit("Exact source educational permission absent")
if "please credit their name" not in rights_text:
    raise SystemExit("Photographer credit terms could not be verified")
if "john kava" not in rights_text:
    raise SystemExit("Original photographer not identified on site contributing-photographers page")

raw_source = None
used_url = None
for url in SOURCE_URLS:
    try:
        q = s.get(url, timeout=65, allow_redirects=True)
        if q.status_code != 200:
            continue
        dest = urlparse(q.url)
        if dest.scheme != "https" or dest.hostname != "yavapaiplants.extension.arizona.edu":
            raise SystemExit("Untrusted image redirect")
        if not 10000 < len(q.content) < 15000000:
            continue
        candidate = Image.open(io.BytesIO(q.content))
        candidate.verify()
        im = Image.open(io.BytesIO(q.content))
        im = ImageOps.exif_transpose(im).convert("RGB")
        if min(im.size) < 350:
            continue
        if im.width * 3 != im.height * 4:  # Require inspected 4:3 frame for arrow placement.
            continue
        raw_source = im
        used_url = q.url
        break
    except (requests.RequestException, OSError):
        continue
if raw_source is None:
    raise SystemExit("No usable linked original or inspected exact-photo fallback; upload aborted")

raw_source.thumbnail((2600, 2600), Image.Resampling.LANCZOS)
out = io.BytesIO()
raw_source.save(out, "JPEG", quality=91, optimize=True)
raw = out.getvalue()
digest = hashlib.sha256(raw).hexdigest()
print("EXACT_IMAGE_AND_EDUCATIONAL_RIGHTS_VALID", raw_source.size, used_url, digest)

s.headers.update({
    "Authorization": "Bearer " + TOKEN,
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
})
API = "https://api.github.com/repos/" + REPO + "/contents/"

def get(path):
    result = s.get(API + quote(path, safe="/"), params={"ref": BRANCH}, timeout=45)
    if result.status_code == 404:
        return None
    result.raise_for_status()
    return result.json()

def put(path, payload, sha, message):
    data = {
        "message": message,
        "content": base64.b64encode(payload).decode("ascii"),
        "branch": BRANCH,
    }
    if sha:
        data["sha"] = sha
    response = s.put(API + quote(path, safe="/"), json=data, timeout=95)
    if response.status_code in (409, 422):
        return False
    response.raise_for_status()
    return True

old = get(PHOTO_PATH)
if old:
    if old.get("size") != len(raw):
        raise SystemExit("Existing archive has differing bytes; do not overwrite")
else:
    if not put(PHOTO_PATH, raw, None, "Lane 1 archive John Kava Yavapai curlymesquite hairy-node anatomy"):
        old = get(PHOTO_PATH)
        if not old or old.get("size") != len(raw):
            raise SystemExit("Concurrent archive path conflict; no overwrite")

common = {
    "creator": "John Kava",
    "license": LICENSE,
    "license_url": RIGHTS,
    "site_specific_public_permission": PERMISSION_ID,
    "source_permission_page": RIGHTS,
    "source_page": PAGE,
    "source_original": used_url,
    "source_taxon_name": "Hilaria belangeri",
    "source_photo_id": PHOTONAME,
    "public_reuse": "Educational use with photographer and Arizona Cooperative Extension site credit only; not Creative Commons, no downstream sublicense",
}
record = {
    "file": REL,
    "role": "ACTUAL HAIRY ABOVEGROUND STEM NODE, photographed with a tuft of white hairs at a reddish joint. Rooting at this node NOT shown; true ligule NOT shown.",
    **common,
    "source_locality": "Rimrock, Verde Valley, Arizona (NOT Hays County)",
    "modifications": "JPEG re-encoding from original or displayed source, orientation corrected, embedded EXIF/GPS stripped; no subject crop",
    "image_sha256": digest,
    "image_dimensions": list(raw_source.size),
    "photo_review": "2026-10-26 inspected 4:3 original webpage display image; pale tufts arise at one reddish culm node near x=63%, y=49%. No roots, no attached collar/ligule and no complete vegetative stolon chain visible.",
}
panel = {
    "label": "HAIRY NODE MACRO — true curlymesquite white node hairs (John Kava)",
    "scientific_name": "Hilaria belangeri",
    "image_url": PHOTO_PATH,
    "image_fit": "contain",
    **common,
    "image_role": "Actual pale hair tuft at a reddish grass culm node; NOT a rooted node or ligule view.",
    "caption": "John Kava's curlymesquite photograph shows a knot-like red culm node with a small ring of white hairs. Arrow marks these real hairs, not soil roots. In the previous Sue Carnahan photograph the connected surface stolons are visible, but these two photographs do NOT jointly prove that a pictured node has rooted in soil. Arizona locality, not Hays County.",
    "why_it_matters": "Adds the missing hairy-node anatomy and teaches the crew to examine a stem JOINT rather than confuse leaf-blade hairs or collar hairs with a rooting node.",
    "markers": [{
        "label": "White hairs at actual stem node",
        "label_x": 71, "label_y": 23,
        "target_x": 64, "target_y": 49,
    }],
    "photo_status": "Original source and site-specific educational use checked; physical GPS-free JPEG installed; arrow targets visually matched to webpage image at 4:3. Live Pages overlay QA pending. Roots NOT shown.",
}
for attempt in range(6):
    card = get(CARD)
    if not card:
        raise SystemExit("Curlymesquite canonical species card absent")
    doc = json.loads(base64.b64decode(card["content"]))
    if doc.get("id") != "hilaria-belangeri":
        raise SystemExit("Incorrect canonical taxon card")
    images = doc.setdefault("images", [])
    comp = doc.setdefault("visual_comparison", {})
    panels = comp.setdefault("items", [])
    seen_img = [x for x in images if x.get("file") == REL]
    seen_panel = [x for x in panels if x.get("image_url") == PHOTO_PATH]
    if len(seen_img) == len(seen_panel) == 1:
        print("ALREADY_PRESENT", PHOTO_PATH)
        break
    if seen_img or seen_panel:
        raise SystemExit("Half-installed/duplicate photo. Preserve and ask for review")
    images.append(record)
    index = next((i for i, x in enumerate(panels) if x.get("scientific_name") != "Hilaria belangeri"), len(panels))
    panels.insert(index, panel)
    doc.setdefault("curation_status", {})["photo_files_present"] = sum(
        str(x.get("file", "")).startswith("images/") for x in images
    )
    doc["curation_status"]["lane1_kava_hairy_node_20261026"] = "HAIRY_NODE_VISIBLE_ROOTED_NODE_AND_TRUE_LIGULE_PHOTO_GAPS"
    # Preserve FIELD_READY_PHOTO_GAPS and all previously inspected annotations.
    content = (json.dumps(doc, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    if put(CARD, content, card["sha"], "Lane 1 teach source-verified curlymesquite hairy culm node with arrow"):
        print("ARCHIVED_AND_GALLERY_COMMITTED", PHOTO_PATH, digest)
        break
    time.sleep(attempt + 1)
else:
    raise SystemExit("Six concurrent canonical revisions, archive preserved; gallery needs follow-up")
