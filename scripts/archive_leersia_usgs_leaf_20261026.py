#!/usr/bin/env python3
"""One-photo exact-taxon USGS rice cutgrass leaf/collar archive.

No species admission, taxonomy, genus, site, Pages, schedule, or arrow changes.
No source substitution/retry on denial; fail closed with a precise hold.
"""
import hashlib
import io
import json
import pathlib
import urllib.error
import urllib.request
from PIL import Image, ImageOps

ROOT = pathlib.Path("content/taxa/Poaceae/Leersia/leersia-oryzoides")
CARD = ROOT / "species.json"
REPORT = pathlib.Path("reports/leersia-usgs-leaf-archive-20261026.json")
SOURCE_PAGE = "https://warcapps.usgs.gov/PlantID/Species/Details/1138"
RIGHTS_PAGE = "https://warcapps.usgs.gov/PlantID/Home/About"
IMAGE_URL = "https://warcapps.usgs.gov/PlantID/Image/GivenFile?file=Leersia+oryzoides+_0937.JPG&id=1138&size=w"
REL = "images/larry-allain-usgs-0937-collar-leaf.jpg"
DEST = ROOT / REL
report = {"taxon": "Leersia oryzoides", "source_page": SOURCE_PAGE,
          "rights_page": RIGHTS_PAGE, "original_image_url": IMAGE_URL,
          "creator": "Larry Allain, U.S. Geological Survey",
          "license": "Public domain (USGS Plants of Louisiana About page)",
          "status": "HOLD", "new_images": 0, "new_arrows": 0, "holds": []}
try:
    d = json.loads(CARD.read_text())
    assert d["id"] == "leersia-oryzoides"
    assert not DEST.exists(), "Existing photo file: refuse overwrite"
    assert not any(x.get("source_page") == SOURCE_PAGE and x.get("media_source_url") == IMAGE_URL for x in d["images"]), "Source already installed"
    assert not any(x.get("file") == REL for x in d["images"]), "Canonical photo entry already exists"
    req = urllib.request.Request(IMAGE_URL, headers={"User-Agent": "HaysCountyBotany/1.0 (USGS public-domain source; github.com/Crking92/Hays-County-Botany)"})
    with urllib.request.urlopen(req, timeout=45) as response:
        content_type = response.headers.get("Content-Type", "")
        blob = response.read(12_000_001)
    assert len(blob) < 12_000_000 and len(blob) > 12000, "Invalid download size"
    assert blob.startswith(b"\\xff\\xd8"), "Not JPEG bytes"
    assert "image" in content_type.lower() or "octet-stream" in content_type.lower(), "Unexpected Content-Type: " + content_type
    with Image.open(io.BytesIO(blob)) as im:
        im.verify()
    with Image.open(io.BytesIO(blob)) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
        original_size = list(im.size)
        assert min(original_size) >= 480, "Not enough pixels for leaf/collar context"
        im.thumbnail((2000, 2000))
        out = io.BytesIO()
        im.save(out, format="JPEG", quality=91, optimize=True)
        jpg = out.getvalue()
    assert jpg.startswith(b"\\xff\\xd8") and jpg.endswith(b"\\xff\\xd9"), "JPEG byte integrity failure"
    with Image.open(io.BytesIO(jpg)) as check:
        check.verify()
    newhash = hashlib.sha256(jpg).hexdigest()
    for existing in d["images"]:
        if existing.get("sha256") == newhash:
            raise ValueError("Duplicate JPEG hash; do not install")
    photo = {
        "file": REL,
        "role": "USGS source-labeled rice cutgrass leaf blade and sheath/collar junction; edge serrations visible at photo scale, tooth direction and 1-mm measurements NOT resolved.",
        "caption": "Rice cutgrass leaf blade beside the sheath/collar and a hairy stem node. Inspect the blade edge for roughness, but this image cannot prove backward-pointing teeth, measured ligule length, or same-plant underground rhizomes.",
        "diagnostic_roles": ["attached leaf blade", "blade edge", "sheath/collar region", "stem node context"],
        "creator": "Larry Allain, U.S. Geological Survey",
        "license": "Public Domain (USGS Plants of Louisiana)",
        "license_url": RIGHTS_PAGE,
        "source_page": SOURCE_PAGE,
        "media_source_url": IMAGE_URL,
        "source_platform": "USGS Plants of Louisiana",
        "public_reuse": True,
        "publicly_usable": True,
        "source_identification": "Leersia oryzoides — USGS species page 1138, image filename Leersia oryzoides _0937.JPG",
        "photo_status": "ARCHIVED_PUBLIC_DOMAIN_PROVISIONAL; annotation_pending",
        "photo_review": "Source image preview inspected for broad blade and collar; downloaded JPEG bytes and dimensions verified. Tooth orientation and measurements not established; no arrow placed.",
        "modifications": "Re-encoded JPEG with EXIF/GPS metadata removed; no anatomical marks burned in.",
        "sha256": newhash,
        "archive_bytes": len(jpg),
        "archive_dimensions": list(im.size),
        "source_dimensions": original_size,
    }
    panel = {
        "label": "USGS · Real rice cutgrass leaf edge and collar — PROVISIONAL",
        "scientific_name": "Leersia oryzoides",
        "image_url": str(ROOT / REL),
        "image_fit": "contain",
        "image_role": "Exact-source leaf-blade edge, collar and stem node context. Not a calibrated microscopic retrorse-teeth proof.",
        "caption": photo["caption"],
        "why_it_matters": "Shows the actual blade attached near the collar, helping locate the cutting margin. A separate 10–20× macro with a 1-mm ruler is still needed to verify backward-pointing teeth.",
        "creator": photo["creator"],
        "license": photo["license"],
        "license_url": RIGHTS_PAGE,
        "source_page": SOURCE_PAGE,
        "markers": [],
        "photo_status": "PUBLIC_DOMAIN_LOCAL_ARCHIVE; annotation_pending",
    }
    d["images"].append(photo)
    d["visual_comparison"]["items"].append(panel)
    d["curation_status"]["photo_files_present"] = sum(x.get("file", "").startswith("images/") for x in d["images"])
    d["curation_status"]["photo_metadata_count"] = len(d["images"])
    d["learner_visual_status"]["image_count"] = len(d["images"])
    d["learner_visual_status"]["status"] = "FIELD_READY_PHOTO_GAPS"
    d["curation_status"]["usgs_leaf_edge_20261026"] = {
        "status": "SOURCE_VERIFIED_ARCHIVED_PHOTO; annotation_pending",
        "local_file": REL,
        "sha256": newhash,
        "public_reuse": "USGS Plants of Louisiana public domain; credit Larry Allain",
        "remaining_need": "10–20× retrorse BLADE margin with 1-mm scale; this is collar-context, not decisive tooth-direction proof.",
    }
    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_bytes(jpg)
    CARD.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\\n")
    report.update(status="ARCHIVED", new_images=1, archive_file=str(DEST),
                  sha256=newhash, bytes=len(jpg), dimensions=list(im.size),
                  source_dimensions=original_size, verified_jpeg=True,
                  metadata_removed=True, annotation_pending=True)
except Exception as exc:
    report["holds"].append({"path": str(DEST), "error": type(exc).__name__ + ": " + str(exc),
                             "verified_bytes": False, "new_arrows": 0,
                             "NEEDS_PUBLIC_PHOTO": "Calibrated actual blade-margin retrorse teeth remain absent"})
REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\\n")
print(json.dumps(report, ensure_ascii=False))
