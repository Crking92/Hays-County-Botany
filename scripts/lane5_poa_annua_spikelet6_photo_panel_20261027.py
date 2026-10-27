#!/usr/bin/env python3
"""Lane 5 Poa annua: publish already-archived true anther photograph with source rights."""
import csv
import hashlib
import html
import io
import json
from pathlib import Path
import re
import urllib.parse
import urllib.request
from PIL import Image, ImageOps

BASE = Path("content/taxa/Poaceae/Poa/poa-annua")
CARD = BASE / "species.json"
LEDGER = BASE / "image-sources.csv"
PHOTO = BASE / "images/commons-6ded1426d00c.jpg"
REPORT = Path("reports/lane5-poa-annua-true-anthers-panel-20261027.json")
SRC = "https://commons.wikimedia.org/wiki/File:Poa_annua_spikelet6_(8038355821).jpg"
LIC = "https://creativecommons.org/licenses/by/2.0/"
assert PHOTO.is_file(), "Previously archived spikelet photograph not in canonical species directory"
card = json.loads(CARD.read_text(encoding="utf-8"))
assert card["id"] == "poa-annua", "Wrong canonical species"
image_record = next((x for x in card["images"] if x.get("file") == "images/commons-6ded1426d00c.jpg"), None)
assert image_record is not None, "No source photo record: stop rather than invent new provenance"
if any(x.get("source_page") == SRC for x in card["visual_comparison"]["items"]):
    print(json.dumps({"status": "ALREADY_INSTALLED", "source": SRC, "gallery": len(card["visual_comparison"]["items"])}))
    raise SystemExit(0)

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "HaysCountyBotanyFieldPhotos/1.0 (educational archive)"})
    with urllib.request.urlopen(req, timeout=55) as response:
        return response.read()

api = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
    "action": "query", "prop": "imageinfo", "iiprop": "url|extmetadata",
    "iiurlwidth": "2400", "titles": "File:Poa annua spikelet6 (8038355821).jpg", "format": "json"
})
payload = json.loads(fetch(api))
pages = list(payload["query"]["pages"].values())
assert len(pages) == 1 and pages[0].get("imageinfo"), "Exact original Commons image missing"
info = pages[0]["imageinfo"][0]
md = info["extmetadata"]
license_name = html.unescape(re.sub("<[^>]+>", "", md.get("LicenseShortName", {}).get("value", "")))
author = html.unescape(re.sub("<[^>]+>", "", md.get("Artist", {}).get("value", "")))
assert re.sub(r"[^a-z0-9]", "", license_name.lower()) == "ccby20", ("Rights changed", license_name)
assert "harry rose" in author.lower(), ("Author mismatch", author)
# Download the exact original-image thumb, not a web-page thumbnail or third-party photo.
source_url = info.get("thumburl") or info["url"]
data = fetch(source_url)
with Image.open(io.BytesIO(data)) as verify:
    verify.verify()
with Image.open(io.BytesIO(data)) as original:
    cleaned = ImageOps.exif_transpose(original).convert("RGB")
    assert cleaned.width >= 1600 and cleaned.height >= 1000, "Insufficient pixels for actual anthers"
    assert 1.45 <= cleaned.width / cleaned.height <= 1.56, "Unexpected crop/orientation"
    cleaned.thumbnail((2400, 2400))
    buff = io.BytesIO()
    cleaned.save(buff, format="JPEG", quality=91, optimize=True)
    clean_bytes = buff.getvalue()
with Image.open(io.BytesIO(clean_bytes)) as clean_check:
    clean_check.verify()
with Image.open(io.BytesIO(clean_bytes)) as clean_check:
    assert not clean_check.getexif() and not clean_check.info.get("exif"), "Source EXIF/GPS not stripped"
PHOTO.write_bytes(clean_bytes)
i = len(card["visual_comparison"]["items"])
role = ("Actual mature Poa annua spikelet macro with visually identifiable dangling yellow anthers "
        "and overlapping green and pale floret scales; no ruler, separated glumes, female organs or bisexuality visible.")
image_record.update({
    "role": role,
    "creator": "Harry Rose (Macleay Grass Man)", "license": "CC BY 2.0",
    "license_url": LIC, "source_page": SRC,
    "original_source_url": info["url"],
    "photo_status": "2026-10-27: Exact Commons image and individual license verified; visible yellow anthers and intact green spikelet scales reviewed; JPEG resized to 2400px and stripped of EXIF/GPS; no femaleness, exact glume/lemma or measured scale claimed.",
    "image_dimensions": list(cleaned.size),
    "sha256_sanitized": hashlib.sha256(clean_bytes).hexdigest(),
    "public_reuse": "CC BY 2.0 with photographer/source/license, note resized and re-encoded adaptation"
})
card["visual_comparison"]["items"].append({
    "label": "ANNUAL BLUEGRASS — REAL DANGLING YELLOW ANTHERS ON A SPIKELET",
    "scientific_name": "Poa annua",
    "image_url": PHOTO.as_posix(), "image_fit": "contain",
    "image_role": role,
    "caption": "An actual photographed spikelet: small yellow anthers protrude at left, beside overlapping green and pale pointed floret scales. Source is an Australian specimen (Harry Rose), not a Hays County specimen. The roughly 5-mm spikelet size comes from the photographer's description and is not measured by a ruler in this image.",
    "why_it_matters": "These are true male pollen-bearing organs. Learn to spot anthers, but this image does not also prove a stigma/ovary in the same floret, so it does not independently demonstrate bisexuality or identify each lemma, glume and palea.",
    "creator": "Harry Rose (Macleay Grass Man)",
    "license": "CC BY 2.0", "license_url": LIC, "source_page": SRC,
    "modifications": "2400px JPEG re-encoding from exact Commons source; original EXIF/GPS stripped; two browser-only arrow overlays.",
    "photo_status": "VISUAL SOURCE INSPECTED — two gross visible structures only; microscopic labels deliberately withheld.",
    "markers": [
        {"label": "Actual yellow anthers", "label_x": 4, "label_y": 44, "target_x": 38, "target_y": 54},
        {"label": "Overlapping floret scales — organs unresolved", "label_x": 66, "label_y": 75, "target_x": 54, "target_y": 50}
    ]
})
for ti in (2, 4, 5):
    tiles = card.get("field_id_short_tiles", [])
    if len(tiles) > ti:
        arr = tiles[ti].setdefault("photo_panel_indices", [])
        if i not in arr: arr.append(i)
featured = card.setdefault("field_photo_quickcheck", {}).setdefault("featured_photo_indices", [])
if i not in featured: featured.append(i)
card.setdefault("field_id_finish_pass", {})["lane5_annua_visual_anthers_20261027"] = {
    "status": "FIELD_READY_PHOTO_GAPS", "source": SRC, "gallery_index": i,
    "newly_visible_anthers": True, "new_accurate_gross_arrows": 2, "new_source_photo_files": 0,
    "previous_source_file_sanitized": True,
    "last_mile": "Calibrated floret dissection with separately visible female parts and glumes/lemmas/palea; local connected whole flowering/root specimen."
}
card["curation_status"]["visual_finish"] = (
    "FIELD_READY_PHOTO_GAPS — 6 locally stored exact-species open-licensed photos, now 6 teaching panels, "
    "including actual rooted crown, membranous collar, boat-shaped tip and true yellow anthers. "
    "Bisexual floret, separated glumes/lemmas/palea at scale and local root-to-head voucher still missing."
)
card["learner_visual_status"]["image_count"] = len(card["images"])
card["learner_visual_status"]["note"] = (
    "Six locally archived Poa annua photographs and six gallery teaching panels. Newly published original "
    "Harry Rose photographed anthers photo was already in GitHub but lacked a panel; now physically sanitized, "
    "license/reuse verified, with 2 gross-only arrows. Native Texas bluegrass comparison remains separate. "
    "Local connected voucher and true dissected microscopic anatomy still missing; live Pages not verified."
)
CARD.write_text(json.dumps(card, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

with LEDGER.open(newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f); fields = reader.fieldnames; rows = list(reader)
target = "commons-6ded1426d00c.jpg"
matching = [r for r in rows if r.get("file_name") == target]
assert len(matching) == 1, ("Expected exactly one existing ledger row", len(matching))
row = matching[0]
for k, val in {
    "role": role, "creator": "Harry Rose (Macleay Grass Man)", "license": "CC BY 2.0",
    "source_page": SRC, "direct_url": info["url"],
    "study_use": "Exact-source species macro in public educational learner; source credited",
    "public_reuse": "CC BY 2.0; preserve photographer, license link, source and transformation statement",
}.items():
    if k in row: row[k] = val
with LEDGER.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader(); writer.writerows(rows)
report = {
    "taxon": "Poa annua", "date": "2026-10-27", "status": "FIELD_READY_PHOTO_GAPS",
    "stored_exact_photos": len(card["images"]), "gallery_species_panels": len(card["visual_comparison"]["items"]),
    "new_photo_files": 0, "new_panel": i, "new_arrows": 2,
    "sanitized_photo_file": PHOTO.as_posix(), "sanitized_bytes": len(clean_bytes),
    "sha256": hashlib.sha256(clean_bytes).hexdigest(), "pixels": list(cleaned.size),
    "license": "CC BY 2.0", "creator": "Harry Rose", "source": SRC,
    "no_false_claims": ["sex of both floral organs in same floret", "mm ruler visible", "isolated glumes/lemmas/palea", "Texas provenance"],
    "ledger_rows": len(rows),
}
REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report))
