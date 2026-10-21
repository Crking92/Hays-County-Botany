#!/usr/bin/env python3
"""One-time public-licensed physical photo install for existing Erigeron strigosus.
Sources are individually licensed Wikimedia Commons files, previously inspected
at 960px for anatomically honest marker coordinates. Abort on any failed download
or verification. Leave taxonomy, county status, automations, and other taxa alone.
"""
from __future__ import annotations
import csv
import hashlib
import io
import json
from pathlib import Path
from urllib.parse import urlencode

import requests
from PIL import Image, ImageOps

BASE = Path("content/taxa/Asteraceae/Erigeron")
CARD_PATH = BASE / "erigeron-strigosus/species.json"
GENUS_PATH = BASE / "genus.json"
CSV_PATH = BASE / "erigeron-strigosus/image-sources.csv"
REPORT = Path("reports/erigeron-strigosus-three-physical-commons-20261021.json")
FILE_INFO = [
    {
        "title": "Erigeron_strigosus_301327401.jpg",
        "filename": "commons-sandy-301327401-leaf-stem.jpg",
        "expected_license": "CC BY 4.0",
        "creator": "Sandy Wolkenberg",
        "role": "Narrow leaf blades and visible fine stem hairs. Direction of hairs and clasping state NOT demonstrable.",
        "source_page": "https://commons.wikimedia.org/wiki/File:Erigeron_strigosus_301327401.jpg",
        "linked": "https://thumb.wikimedia.org/wikipedia/commons/thumb/0/09/Erigeron_strigosus_301327401.jpg/960px-Erigeron_strigosus_301327401.jpg",
    },
    {
        "title": "Erigeron_strigosus_301327364.jpg",
        "filename": "commons-sandy-301327364-leafy-habit.jpg",
        "expected_license": "CC BY 4.0",
        "creator": "Sandy Wolkenberg",
        "role": "Multiple narrow-leaved shoots, vegetative habit. Same New Jersey observation as Sandy's other photo; roots not visible.",
        "source_page": "https://commons.wikimedia.org/wiki/File:Erigeron_strigosus_301327364.jpg",
        "linked": "https://thumb.wikimedia.org/wikipedia/commons/thumb/2/2a/Erigeron_strigosus_301327364.jpg/960px-Erigeron_strigosus_301327364.jpg",
    },
    {
        "title": "Erigeron_strigosus_(6295169491).jpg",
        "filename": "commons-dean-6295169491-pressed-voucher.jpg",
        "expected_license": "CC BY 2.0",
        "creator": "Dean Wm. Taylor",
        "role": "Pressed museum voucher with visible root area and printed scale. Collected British Columbia; no fresh flower color or Texas-provenance claim.",
        "source_page": "https://commons.wikimedia.org/wiki/File:Erigeron_strigosus_%286295169491%29.jpg",
        "linked": "https://thumb.wikimedia.org/wikipedia/commons/thumb/5/55/Erigeron_strigosus_%286295169491%29.jpg/960px-Erigeron_strigosus_%286295169491%29.jpg",
    },
]
S = requests.Session()
S.headers.update({"User-Agent": "HaysCountyBotanyPhotoInstall/1.0 (educational species imagery; GitHub Crking92/Hays-County-Botany)"})

def fetch(source):
    query = {
        "action": "query", "format": "json", "formatversion": "2",
        "titles": "File:" + source["title"],
        "prop": "imageinfo", "iiprop": "url|size|extmetadata",
        "iiurlwidth": "960",
    }
    r = S.get("https://commons.wikimedia.org/w/api.php", params=query, timeout=35)
    r.raise_for_status()
    pages = r.json()["query"]["pages"]
    assert len(pages) == 1 and "imageinfo" in pages[0], "Commons file metadata not found"
    inf = pages[0]["imageinfo"][0]
    short = inf.get("extmetadata", {}).get("LicenseShortName", {}).get("value", "")
    assert short.strip().upper() == source["expected_license"].upper(), (source["title"], short)
    url = inf.get("thumburl")
    assert url and url.startswith("https://") and ("wikimedia.org" in url), "Missing safe Commons thumbnail URL"
    rr = S.get(url, timeout=60)
    rr.raise_for_status()
    assert 19000 <= len(rr.content) <= 16_000_000, "Downloaded image size suspicious"
    with Image.open(io.BytesIO(rr.content)) as original:
        original.load()
        assert original.format in ("JPEG", "PNG"), original.format
        im = ImageOps.exif_transpose(original).convert("RGB")
    assert min(im.size) >= 320, "Insufficient resolution"
    im.thumbnail((1500, 1500), Image.Resampling.LANCZOS)
    out = io.BytesIO()
    im.save(out, "JPEG", quality=90, optimize=True, progressive=True)
    data = out.getvalue()
    assert len(data) > 19000
    with Image.open(io.BytesIO(data)) as chk: chk.verify()
    return data, hashlib.sha256(rr.content).hexdigest(), list(im.size), url

def main():
    man = json.loads(Path("data/manifest.json").read_text())
    assert sum(x.get("id") == "erigeron-strigosus" for x in man["species"]) == 1, "Canonical learner species not unique"
    claims = json.loads(Path("workflow/work-claims.json").read_text()).get("claims", [])
    assert not any("erigeron-strigosus" in (c.get("taxa") or []) and
                   c.get("status") in ("active", "claimed", "in_progress") for c in claims), "Active claim conflicts"
    card = json.loads(CARD_PATH.read_text())
    genus = json.loads(GENUS_PATH.read_text())
    assert card["id"] == "erigeron-strigosus" and card["scientific_name"] == "Erigeron strigosus"
    assert "erigeron-strigosus" in genus["project_scope"]["canonical_species_ids"]
    target_paths = [BASE / "erigeron-strigosus/images" / s["filename"] for s in FILE_INFO]
    if all(p.exists() for p in target_paths):
        assert len(card.get("images", [])) >= 4
        print("Already physically installed; no changes")
        return
    assert not any(p.exists() for p in target_paths), "Partial prior install; investigate, do not overwrite"
    assert len(card.get("images", [])) == 1, "Photo inventory changed since preparation"
    assert len(card.get("visual_comparison", {}).get("items", [])) == 6
    downloaded = [(s, *fetch(s)) for s in FILE_INFO]
    # No writes to repo until ALL three individual license/image verifications succeed.
    for s, data, _, _, _ in downloaded:
        p = BASE / "erigeron-strigosus/images" / s["filename"]
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    replacements = {s["linked"]: "content/taxa/Asteraceae/Erigeron/erigeron-strigosus/images/" + s["filename"] for s in FILE_INFO}
    for s, data, sha, dims, actual_url in downloaded:
        card["images"].append({
            "file": "images/" + s["filename"], "role": s["role"], "creator": s["creator"],
            "license": s["expected_license"],
            "license_url": "https://creativecommons.org/licenses/by/" + ("2.0/" if s["expected_license"] == "CC BY 2.0" else "4.0/"),
            "source_platform": "Wikimedia Commons verified same-species named file",
            "source_page": s["source_page"], "downloaded_from": actual_url,
            "downloaded_original_sha256": sha, "image_dimensions": dims,
            "study_use": "Attribution-based public learner field identification",
            "public_reuse": "CC BY license and creator credited per individual Commons page; alterations must be noted",
            "modifications": "960px Commons thumbnail physically downloaded, resized if needed, stripped EXIF, JPEG re-encoded",
            "photo_review": "Previously examined visible plant anatomy and existing marker coordinates; no claim of voucher-quality species diagnosis.",
        })
    for obj in (card, genus):
        for panel in obj.get("visual_comparison", {}).get("items", []):
            if panel.get("image_url") in replacements:
                panel["image_url"] = replacements[panel["image_url"]]
                panel["photo_status"] = "PHYSICAL_VERIFIED_2026-10-21: existing displayed photo + anatomy markers retained; mobile overlay signoff pending"
        for panel in obj.get("visual_comparison", {}).get("part_examples", []):
            if panel.get("image_url") in replacements:
                panel["image_url"] = replacements[panel["image_url"]]
                panel["status"] = "installed_photo_reference"
    card["visual_comparison"]["subtitle"] = (
        "Four physically installed E. strigosus photographs (the original iNaturalist field photo plus three "
        "Commons CC BY photographs), and two explicitly OTHER-species comparison panels. "
        "Fourteen visually inspected marker coordinates; root/collar/hair angles and ripe fruit macro still pending."
    )
    card["visual_comparison"]["annotation_status"] = (
        "Six panels and fourteen existing arrow overlays retained after replacing three external Commons image URLs "
        "with locally downloaded, physically checked source-identical image files. Phone overlay signoff pending."
    )
    card["curation_status"].update({
        "photo_metadata_count": len(card["images"]), "photo_files_present": len(card["images"]),
        "physical_commons_install": "2026-10-21", "last_reviewed": "2026-10-21",
        "visual_status": "FOUR physical source-credited same-species photos, two separate look-alike compare-only photos, 14 prior arrow markers. True measured diagnostic macros still needed.",
    })
    card["learner_visual_status"].update({
        "image_count": len(card["images"]), "status": "field_ready_four_physical_photos_diagnostic_gaps",
        "note": "Four original photo files now in repo; three previous Commons references installed as individually CC BY credited JPEGs, existing fourteen markers retained. Do not count other-species comparison photos as strigosus.",
    })
    card["photo_note"] = (
        "Four physical source-identified photos, including three individual CC BY Wikimedia Commons files "
        "installed 2026-10-21. Need intact clasping/node view, true stem-hair angle, fresh head with ruler, and cypsela macro."
    )
    genus["curation_status"]["physical_installer_status"] = (
        "Five canonical Erigeron cards. Three previously Commons-linked E. strigosus references now physically "
        "installed (four E. strigosus original JPEGs total). Other existing credited photos retained."
    )
    genus["curation_status"]["photo_review_note"] = (
        "Three new physical Wikimedia Commons E. strigosus sources replacing old linked references; keep all "
        "previously visually checked arrow overlays and rights metadata. Fine diagnostic morphology remains pending."
    )
    genus["curation_status"]["last_reviewed"] = "2026-10-21"
    genus["curation_status"]["version"] = "1.6-strigosus-physical-commons-20261021"
    genus["visual_comparison"]["subtitle"] = (
        "Ten genus photo panels including four exact-source E. strigosus photos locally stored, "
        "with previously inspected leaf and stem annotations; same-source license attributions retained."
    )
    # Preserve source attribution and all native-zone decisions unchanged.
    CARD_PATH.write_text(json.dumps(card, indent=2, ensure_ascii=False) + "\n")
    GENUS_PATH.write_text(json.dumps(genus, indent=2, ensure_ascii=False) + "\n")
    with CSV_PATH.open(newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        rows = list(reader)
    for s, data, sha, dims, url in downloaded:
        row = {k: "" for k in fields}
        info = {
            "file_name": s["filename"], "role": s["role"], "creator": s["creator"],
            "license": s["expected_license"], "source_page": s["source_page"],
            "direct_url": url, "study_use": "Credited CC BY educational photo use",
            "public_reuse": "Exact individual Commons CC BY license, with attribution and modifications noted",
        }
        row.update({k: v for k, v in info.items() if k in row})
        rows.append(row)
    with CSV_PATH.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({
        "species": "Erigeron strigosus", "date": "2026-10-21",
        "source_photo_count_before": 1, "downloaded_additional_physical": 3,
        "installed_physical_total": len(card["images"]),
        "files": [{"file": s["filename"], "licensed": s["expected_license"],
                   "sha256_remote": sha, "dimensions": dims} for s, data, sha, dims, url in downloaded],
        "arrows_preserved": 14, "source_license_checked_with_live_Commons_API": True,
        "remaining": "Fresh macro with ruler for phyllaries/leaf attachment/hairs/fruit and owner phone arrow QA.",
        "pages_deployment_confirmed": False,
    }, indent=2) + "\n")
    print("Physically installed 3 licensed Commons photographs; strigosus now 4 physical original images.")

if __name__ == "__main__":
    main()
