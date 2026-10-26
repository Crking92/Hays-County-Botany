#!/usr/bin/env python3
"""Archive two exact-taxon IRIIS photos with explicit noncommercial educational reuse.

IRIIS source terms require images used *unchanged*, with creator, organisation,
source and access date. No cropping, EXIF removal, resized derivative, arrows,
or presumed Creative Commons licence. Any EXIF/GPS metadata is a hard hold.
Never retry HTTP/permission denials by alternate route.
"""
import datetime
import hashlib
import io
import json
import pathlib
import urllib.request
from PIL import Image

ROOT = pathlib.Path("content/taxa/Poaceae/Leersia/leersia-oryzoides")
CARD = ROOT / "species.json"
REPORT = pathlib.Path("reports/leersia-iriis-photo-archive-20261026.json")
RIGHTS = "https://iriisphytoprotection.qc.ca/fr/credits-photos"
TERMS = "IRIIS site-specific permission: noncommercial educational digital reproduction, image unchanged; NOT a Creative Commons licence."
ITEMS = [
    {
        "node": "27296", "file": "images/romain-neron-iriis-rooted-base-4383.jpg",
        "url": "https://www.iriisphytoprotection.qc.ca/sites/default/files/2023-05/Testing1_4383.jpg",
        "creator": "Romain Néron",
        "role": "Exact-taxon excavated rice cutgrass base with attached culms, roots and rhizomes; NOT a Hays County voucher or flowering-to-root traced specimen.",
        "caption": "Rice cutgrass base with connected stems, fibrous roots and rhizomes, photographed by Romain Néron for IRIIS phytoprotection/MAPAQ. Source caption: Base d'un plant, rhizomes et racines. This is not a verified Hays County collection.",
        "diagnostic_roles": ["excavated connected root base", "rhizome context", "root-versus-rhizome comparison"],
    },
    {
        "node": "27301", "file": "images/vincent-coulombe-iriis-caryopsis-4388.jpg",
        "url": "https://www.iriisphytoprotection.qc.ca/sites/default/files/2023-05/Testing1_4388.jpg",
        "creator": "Vincent Coulombe",
        "role": "Exact-taxon mature rice cutgrass CARYOPSIS with source-printed 1-mm scale; NOT a glumeless spikelet, lemma or palea dissection.",
        "caption": "Mature rice cutgrass grains (caryopses), with original 1-mm scale. Photograph by Vincent Coulombe, IRIIS phytoprotection/MAPAQ. These are grains, NOT intact spikelets; the glume/lemma/palea measurement gap remains.",
        "diagnostic_roles": ["mature grain", "1-mm source scale", "fruit anatomy"],
    },
]
d = json.loads(CARD.read_text())
assert d["id"] == "leersia-oryzoides", "canonical species mismatch"
claims = json.loads(pathlib.Path("workflow/work-claims.json").read_text()).get("claims", [])
now = datetime.datetime.now(datetime.timezone.utc)
for c in claims:
    if "leersia-oryzoides" not in c.get("taxa", []):
        continue
    if c.get("status") != "active":
        continue
    try:
        expiry = datetime.datetime.fromisoformat(c["expires_at"].replace("Z", "+00:00"))
        if expiry > now:
            raise RuntimeError("Active overlapping claim: " + c.get("claim_id", "?"))
    except (KeyError, ValueError, TypeError):
        raise RuntimeError("Unresolved active claim: " + c.get("claim_id", "?"))
report = {
    "taxon": "Leersia oryzoides", "source": "IRIIS phytoprotection / MAPAQ",
    "rights": RIGHTS, "reuse": TERMS, "scope": "existing canonical species only",
    "installed": [], "already_present": [], "holds": [], "new_arrows": 0,
    "rights_condition": "Unchanged downloaded JPEG, source/creator attribution; strictly noncommercial education; no image edits",
}
for item in ITEMS:
    rel = item["file"]
    dest = ROOT / rel
    source_page = "https://www.iriisphytoprotection.qc.ca/fr/node/" + item["node"]
    try:
        if dest.exists():
            if any(i.get("file") == rel and i.get("source_page") == source_page for i in d["images"]):
                report["already_present"].append({"file": str(dest), "source": source_page})
                continue
            raise ValueError("Existing photo file without matching canonical source: hold")
        if any(i.get("file") == rel or i.get("source_page") == source_page for i in d["images"]):
            raise ValueError("Existing canonical image source or destination: hold")
        req = urllib.request.Request(item["url"], headers={
            "User-Agent": "HaysCountyBotany/1.0 (educational unchanged reproduction; github.com/Crking92/Hays-County-Botany)"
        })
        # No retry, alternate host, or workaround on HTTP denial.
        with urllib.request.urlopen(req, timeout=40) as response:
            ct = response.headers.get("Content-Type", "")
            original = response.read(12_000_001)
        if not (12000 <= len(original) <= 12_000_000):
            raise ValueError("Image bytes outside permitted size")
        if "image" not in ct.lower() and "octet-stream" not in ct.lower():
            raise ValueError("Non-image Content-Type: " + ct)
        if not (original[:2] == b"\\xff\\xd8" and original[-2:] == b"\\xff\\xd9"):
            raise ValueError("Not complete JPEG bytes")
        with Image.open(io.BytesIO(original)) as im:
            im.verify()
        with Image.open(io.BytesIO(original)) as im:
            dimensions = list(im.size)
            if min(dimensions) < 480:
                raise ValueError("Image too small for diagnostic photo")
            if im.getexif() or b"Exif\\x00\\x00" in original or b"http://ns.adobe.com/xap/1.0/" in original:
                raise ValueError("Original contains EXIF/XMP; cannot strip or publish unchanged under source terms")
        digest = hashlib.sha256(original).hexdigest()
        if any(x.get("sha256") == digest for x in d["images"]):
            raise ValueError("Duplicate image hash already archived")
        # Exact downloaded bytes: no resize, re-encode, crop, text or arrows.
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(original)
        source_credit = item["creator"] + " / Laboratoire d'expertise et de diagnostic en phytoprotection - MAPAQ"
        photo = {
            "file": rel, "role": item["role"], "caption": item["caption"],
            "diagnostic_roles": item["diagnostic_roles"], "creator": source_credit,
            "license": "IRIIS noncommercial educational unchanged-use permission (not CC)",
            "license_url": RIGHTS, "source_page": source_page, "media_source_url": item["url"],
            "source_platform": "IRIIS phytoprotection (MAPAQ)",
            "source_identification": "Leersia oryzoides — IRIIS original species image " + item["node"],
            "public_reuse": "Conditional: only unchanged image for noncommercial educational website; full source/creator/organization credit",
            "publicly_usable": True,
            "photo_status": "ARCHIVED_CONDITIONAL_NONCOMMERCIAL_UNMODIFIED; annotation_pending",
            "photo_review": "Original image/source caption examined for taxon and photographed organ. Bytes, JPEG integrity, dimensions, metadata and rights verified; no invented arrows.",
            "modifications": "None; exact source JPEG bytes unchanged; EXIF/XMP absent",
            "sha256": digest, "archive_bytes": len(original), "archive_dimensions": dimensions,
            "source_access_date": "2026-10-26",
        }
        panel = {
            "label": ("Rooted base, rhizomes and roots" if item["node"] == "27296" else "Mature caryopses — original 1-mm scale") + " — PROVISIONAL",
            "scientific_name": "Leersia oryzoides",
            "image_url": str(ROOT / rel), "image_fit": "contain",
            "image_role": item["role"], "caption": item["caption"],
            "why_it_matters": ("Shows underground stems versus fibrous roots; local traced specimen still needed." if item["node"] == "27296" else "Adds measured grain context; does not substitute for measured spikelet anatomy."),
            "creator": source_credit, "license": photo["license"], "license_url": RIGHTS,
            "source_page": source_page, "markers": [],
            "photo_status": "PUBLIC_EDUCATIONAL_NONCOMMERCIAL_UNMODIFIED; annotation_pending",
        }
        d["images"].append(photo)
        d["visual_comparison"]["items"].append(panel)
        report["installed"].append({"file": str(dest), "source_page": source_page,
                                    "source_url": item["url"], "creator": source_credit,
                                    "license": photo["license"], "sha256": digest,
                                    "bytes": len(original), "dimensions": dimensions,
                                    "verified_jpeg": True, "exif_xmp_absent": True,
                                    "arrows": 0})
    except Exception as e:
        report["holds"].append({"target": str(dest), "source": source_page, "creator": item["creator"],
                                 "license": TERMS, "verified_bytes": False,
                                 "error": type(e).__name__ + ": " + str(e),
                                 "annotation_pending": True})
if report["installed"]:
    d["curation_status"]["photo_files_present"] = sum(x.get("file", "").startswith("images/") for x in d["images"])
    d["curation_status"]["photo_metadata_count"] = len(d["images"])
    d["learner_visual_status"]["image_count"] = len(d["images"])
    d["learner_visual_status"]["status"] = "FIELD_READY_PHOTO_GAPS"
    d["curation_status"]["iriis_anatomy_20261026"] = {
        "status": "CONDITIONAL_UNMODIFIED_SOURCE_IMAGES_ARCHIVED; annotation_pending",
        "files": [x["file"] for x in report["installed"]],
        "reuse": TERMS,
        "NEEDS_PUBLIC_PHOTO": [
            "10–20x blade-MARGIN retrorse teeth with 1-mm ruler, not sheath prickles",
            "Hays-area same-plant rooted culm and flowering panicle with visible low branching node",
            "calibrated intact mature spikelet with glumeless base and lemma/palea",
            "calibrated attached membranous ligule and matched Leersia virginica"
        ],
        "annotation_pending": ["precise retrorse blade-margin tooth positions", "lowest panicle branch attachments", "glumeless base/lemma/palea metric arrows"],
    }
    CARD.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\\n")
REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\\n")
print(json.dumps(report, ensure_ascii=False))
