#!/usr/bin/env python3
"""Lane 3: recover ONE credited source-identified nimblewill flowering photo.

Do not label microscopic structures or add arrows without inspecting the actual pixels.
This is a strictly guarded upgrade of existing exact-photo-ID metadata, NOT taxonomy.
"""
import hashlib
import io
import json
import pathlib
import time
import urllib.request
from PIL import Image, ImageOps

ROOT = pathlib.Path("content/taxa/Poaceae/Muhlenbergia/muhlenbergia-schreberi")
CARD = ROOT / "species.json"
REPORT = pathlib.Path("reports/lane3-nimblewill-head-retry-20261026.json")
PHOTO_ID = 92218354
FILENAME = "nimblewill-emily-summerbell-92218354-ccby4.jpg"
PHOTO_PATH = ROOT / "images" / FILENAME
LOCAL = "images/" + FILENAME
WEB_PATH = str(ROOT / LOCAL)
COMMONS = "https://commons.wikimedia.org/wiki/File:Muhlenbergia_schreberi_iNat-92218354.jpg"
INAT = "https://www.inaturalist.org/photos/92218354"
LICENSE = "https://creativecommons.org/licenses/by/4.0/"
# Rights evidence: the exact Wikimedia Commons file page individually confirms
# Emily Summerbell, observation 57794694, photo 92218354, and CC BY 4.0.
# Prior 2026-10-23 import failed Wikimedia HTTP 429 (see original lane3 report).
# All endpoints below must resolve to this individual named photo, no search thumbnails.
SOURCES = [
  ("inat-open-data-original", "https://inaturalist-open-data.s3.amazonaws.com/photos/92218354/original.jpg"),
  ("inat-original", "https://static.inaturalist.org/photos/92218354/original.jpg"),
  ("commons-original", "https://upload.wikimedia.org/wikipedia/commons/2/22/Muhlenbergia_schreberi_iNat-92218354.jpg"),
]
report = {"id": "muhlenbergia-schreberi", "photo_id": PHOTO_ID,
          "commons_source": COMMONS, "rights": "Emily Summerbell, CC BY 4.0",
          "result": "HOLD", "attempts": []}

def get(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "HaysCountyBotany/1.0 (source-credited botanical photograph curation; github.com/Crking92/Hays-County-Botany)",
        "Accept": "image/jpeg,image/*;q=0.9",
    })
    with urllib.request.urlopen(req, timeout=40) as response:
        if "image" not in response.headers.get("content-type", "").lower():
            raise ValueError("Non-image MIME type")
        payload = response.read(12000001)
    if not 30000 < len(payload) < 12000001:
        raise ValueError("Unexpected downloaded byte size")
    return payload

d = json.loads(CARD.read_text(encoding="utf-8"))
assert d["id"] == "muhlenbergia-schreberi"
assert d["scientific_name"] == "Muhlenbergia schreberi"
matches = [x for x in d["images"] if str(x.get("inaturalist_photo_id", "")) == str(PHOTO_ID)]
assert len(matches) == 1, "The original exact photo-ID row must exist exactly once"
row = matches[0]
assert row.get("creator") == "Emily Summerbell" and row.get("license") == "CC BY 4.0"
assert row.get("source_page") == COMMONS and row.get("original_source_page") == INAT
assert row.get("observation_source") == "https://www.inaturalist.org/observations/57794694"
if PHOTO_PATH.exists():
    # Never overwrite previous edits; accept already archived exact photograph.
    with Image.open(PHOTO_PATH) as im:
        im.verify()
    report["attempts"].append("Already archived: preserving existing JPEG")
else:
    for source_type, url in SOURCES:
        try:
            source = get(url)
            with Image.open(io.BytesIO(source)) as im:
                assert im.format == "JPEG"
                im.verify()
            with Image.open(io.BytesIO(source)) as im:
                im = ImageOps.exif_transpose(im).convert("RGB")
                assert min(im.size) >= 600 and max(im.size) <= 12000
                original_size = [im.width, im.height]
                im.thumbnail((2000, 2000), Image.Resampling.LANCZOS)
                output = io.BytesIO()
                im.save(output, "JPEG", quality=89, optimize=True)
                processed = output.getvalue()
            with Image.open(io.BytesIO(processed)) as check:
                assert not check.getexif().get(34853), "GPS EXIF must be removed"
                check.verify()
            PHOTO_PATH.parent.mkdir(parents=True, exist_ok=True)
            PHOTO_PATH.write_bytes(processed)
            report["original_source_url"] = url
            report["source_type"] = source_type
            report["original_dimensions"] = original_size
            report["source_sha256"] = hashlib.sha256(source).hexdigest()
            break
        except Exception as exc:
            report["attempts"].append({"host": source_type, "error": str(exc)[:190]})
    if not PHOTO_PATH.exists():
        REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report))
        raise SystemExit("No verified photograph bytes: kept scientific and rights holds")

with Image.open(PHOTO_PATH) as chk:
    assert chk.format == "JPEG" and min(chk.size) >= 600
    dims = [chk.width, chk.height]
    assert not chk.getexif().get(34853)
    chk.verify()
sha256 = hashlib.sha256(PHOTO_PATH.read_bytes()).hexdigest()
row["file"] = LOCAL
row["physical_archive_sha256"] = sha256
row["photo_status"] = "PUBLIC_CC_BY_ARCHIVED; exact observation source; mature head fine-anatomy not visually certified"
row["license_url"] = LICENSE
row["source_image_original"] = report.get("original_source_url", row.get("source_image_original", ""))
row["modifications"] = "Resaved JPEG with EXIF/GPS removed; no drawn image-pixel arrows"
items = d["visual_comparison"]["items"]
existing = [p for p in items if str(PHOTO_ID) in p.get("image_url","") or p.get("source_page") == INAT]
if not existing:
    # Add genuine photograph, not speculative glume or ligule labeling.
    panel = {
        "label": "Nimblewill — real flowering-head photo (photo 92218354)",
        "scientific_name": "Muhlenbergia schreberi",
        "image_url": WEB_PATH,
        "image_fit": "contain",
        "image_role": "Exact observation-source flowering-head reference; mature spikelet detail not independently calibrated",
        "caption": "Source-identified nimblewill flowering view, by Emily Summerbell. Use to compare the narrow head with leaves and stems. Do not read individual glume or lemma measurements from this photograph.",
        "why_it_matters": "Adds a source-identified reproductive view to the largely vegetative gallery; does not prove rooted stolon nodes, membranous ligule length, or measured spikelet characters.",
        "creator": "Emily Summerbell",
        "license": "CC BY 4.0",
        "license_url": LICENSE,
        "source_page": INAT,
        "commons_source": COMMONS,
        "photo_status": "Physical JPEG archived and metadata verified; no uninspected anatomy arrows",
        "markers": []
    }
    index = next((i for i,p in enumerate(items) if p.get("scientific_name") != "Muhlenbergia schreberi"),len(items))
    items.insert(index,panel)
else:
    for p in existing:
        p["image_url"] = WEB_PATH
        p["markers"] = []  # photo was previously external; don't invent arrows
d["curation_status"]["photo_files_present"] = sum(1 for x in d["images"] if str(x.get("file","")).startswith("images/"))
d["curation_status"]["photo_metadata_count"] = len(d["images"])
d["learner_visual_status"]["image_count"] = len(d["images"])
d["learner_visual_status"]["status"] = "FIELD_READY_PHOTO_GAPS"
report.update({
   "result": "PHYSICALLY_ARCHIVED_UNANNOTATED_REPRODUCTIVE_SOURCE_PHOTO",
   "local_image": WEB_PATH, "sha256": sha256, "dimensions": dims,
   "species_image_records": len(d["images"]),
   "physical_species_image_files": d["curation_status"]["photo_files_present"],
   "species_gallery_panels": len(items),
   "arrows_added": 0,
   "remaining": "True stolon node WITH roots and millimeter scale; verified membranous ligule; true mature isolated spikelet with glume/lemma/awn scale; specimen identification audit",
})
CARD.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n",encoding="utf-8")
REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",encoding="utf-8")
print(json.dumps(report, indent=2))
