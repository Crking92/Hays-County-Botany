#!/usr/bin/env python3
"""Only archive the photographer-identified CC BY 2.0 Echinochloa crus-galli plant14 photograph.

A whole-plant/habit reference is not evidence of visible roots or Texas occurrence until
its archived pixels have been independently inspected. Never overwrite other workers.
"""
import base64
import hashlib
import json
import os
from pathlib import Path
import time
from urllib.parse import quote, urlparse
import requests

TITLE = "File:Echinochloa crusgalli plant14 HR - Flickr - Macleay Grass Man.jpg"
SPECIES = "content/taxa/Poaceae/Echinochloa/echinochloa-crus-galli/species.json"
IMAGE_NAME = "harry-rose-barnyardgrass-plant14-cc-by2.jpg"
RELATIVE = "images/" + IMAGE_NAME
IMAGE_PATH = "content/taxa/Poaceae/Echinochloa/echinochloa-crus-galli/" + RELATIVE
SOURCE_PAGE = "https://commons.wikimedia.org/wiki/File:Echinochloa_crusgalli_plant14_HR_-_Flickr_-_Macleay_Grass_Man.jpg"
SOURCE_FLICKR = "https://www.flickr.com/photos/macleaygrassman/23940789639/"
evidence = json.loads(Path("review_photo/evidence.json").read_text())
candidate = Path("review_photo/candidate.jpg").read_bytes()
if evidence.get("commons_file") != TITLE or evidence.get("taxon_proposed") != "Echinochloa crus-galli":
    raise SystemExit("Exact species and source title mismatch")
if evidence.get("license_short", "").strip().upper() != "CC BY 2.0":
    raise SystemExit("CC BY 2.0 source license required")
license_uri = urlparse(evidence.get("license_url", "").lower())
if license_uri.scheme not in ("http", "https") or license_uri.hostname != "creativecommons.org" or license_uri.path.rstrip("/") != "/licenses/by/2.0":
    raise SystemExit("Unexpected CC BY 2.0 license address")
if not evidence.get("gps_exif_removed") or not candidate.startswith(bytes.fromhex("ffd8")) or len(candidate) > 12_000_000:
    raise SystemExit("Image rejected: unsafe format, EXIF status, or excessive size")
if hashlib.sha256(candidate).hexdigest() != evidence.get("image_sha256"):
    raise SystemExit("Evidence checksum mismatch")
repo = os.environ["GITHUB_REPOSITORY"]
branch = os.getenv("GITHUB_REF_NAME", "main")
session = requests.Session()
session.headers.update({
    "Authorization": "Bearer " + os.environ["GITHUB_TOKEN"],
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "HaysBotany-Lane1-Barnyardgrass-Habit",
})
root = f"https://api.github.com/repos/{repo}/contents/"
def get(path):
    r = session.get(root + quote(path, safe="/"), params={"ref": branch}, timeout=35)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.json()
def put(path, data, sha, message):
    payload = {"branch": branch, "message": message,
               "content": base64.b64encode(data).decode("ascii")}
    if sha:
        payload["sha"] = sha
    r = session.put(root + quote(path, safe="/"), json=payload, timeout=90)
    if r.status_code in (409, 422):
        return False
    r.raise_for_status()
    return True
old = get(IMAGE_PATH)
if old:
    # Identical length alone is not an image identity guarantee: compare SHA-1 git blob,
    # which is calculated over 'blob LENGTH\0' and exact bytes.
    blob_sha1 = hashlib.sha1(("blob " + str(len(candidate))).encode() + bytes([0]) + candidate).hexdigest()
    if old.get("sha") != blob_sha1:
        raise SystemExit("Another image occupies archival filename; preserve it")
else:
    if not put(IMAGE_PATH, candidate, None, "Lane 1: archive CC BY 2.0 Harry Rose barnyardgrass plant view"):
        old = get(IMAGE_PATH)
        blob_sha1 = hashlib.sha1(("blob " + str(len(candidate))).encode() + bytes([0]) + candidate).hexdigest()
        if not old or old.get("sha") != blob_sha1:
            raise SystemExit("Concurrent photo changed; stop")
for attempt in range(6):
    cur = get(SPECIES)
    if cur is None:
        raise SystemExit("No canonical barnyardgrass record")
    j = json.loads(base64.b64decode(cur["content"]))
    gallery = j.setdefault("visual_comparison", {}).setdefault("items", [])
    images = j.setdefault("images", [])
    existing_gallery = [x for x in gallery if x.get("image_url") == IMAGE_PATH]
    existing_images = [x for x in images if x.get("file") == RELATIVE]
    if len(existing_gallery) == len(existing_images) == 1:
        print("ALREADY_INSTALLED", IMAGE_PATH)
        break
    if existing_gallery or existing_images:
        raise SystemExit("Partial preexisting image/gallery record; stop and preserve")
    images.append({
        "file": RELATIVE,
        "role": "Photographer-identified Echinochloa crus-galli whole plant view. Growth-base and roots NOT yet pixel certified.",
        "creator": "Harry Rose / Macleay Grass Man",
        "license": "CC BY 2.0",
        "license_url": "https://creativecommons.org/licenses/by/2.0/",
        "source_page": SOURCE_PAGE,
        "original_source_page": SOURCE_FLICKR,
        "source_locality": "Dungog, NSW, Australia — not a Central Texas voucher",
        "source_determination": "Author-identified Echinochloa crus-galli; local verification pending",
        "modifications": "Wikimedia source resized to JPEG; EXIF/GPS stripped; visible content unchanged",
        "public_reuse": "Yes — CC BY 2.0 with creator/source/license/adaptation attribution",
        "photo_review": "Physical image saved with independently verified source license; growth structures and precise arrows pending pixel inspection"
    })
    panel = {
        "label": "WHOLE-PLANT GROWTH — Australian barnyardgrass (root detail pending inspection)",
        "scientific_name": "Echinochloa crus-galli",
        "image_url": IMAGE_PATH,
        "image_fit": "contain",
        "image_role": "Exact-source-author plant habit photograph; roots or root crown not assumed present.",
        "caption": "An additional source-identified real barnyardgrass plant view. Do not infer a rooted basal crown from a habit photograph until the actual image is inspected.",
        "why_it_matters": "Adds an actual species habit lesson beyond separated seedheads and microscopic photographs.",
        "creator": "Harry Rose / Macleay Grass Man",
        "license": "CC BY 2.0",
        "license_url": "https://creativecommons.org/licenses/by/2.0/",
        "source_page": SOURCE_PAGE,
        "markers": [],
        "photo_status": "Physically archived CC BY 2.0 JPEG; pixel and mobile QA pending. Australia, not a local Texas voucher."
    }
    # Place near the start with habit photos, not in lookalike gallery.
    gallery.insert(1, panel)
    status = j.setdefault("curation_status", {})
    status["photo_files_present"] = sum(str(x.get("file", "")).startswith("images/") for x in images)
    status["lane1_barnyard_habit_import_20261026"] = "CC_BY_2_PHYSICAL_ARCHIVE_PIXEL_REVIEW_PENDING"
    payload = (json.dumps(j, indent=2, ensure_ascii=False) + "\n").encode()
    if put(SPECIES, payload, cur["sha"], "Lane 1: add source-verified archived barnyardgrass plant photo gallery panel"):
        print("ARCHIVED_AND_LINKED", IMAGE_PATH)
        break
    time.sleep(1 + attempt)
else:
    raise SystemExit("Concurrent edits prevented safe species JSON update; archive retained")
