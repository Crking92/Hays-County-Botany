#!/usr/bin/env python3
"""Archive ONLY five explicitly identified Jim Conrad eastern gamagrass JPEGs.

Runs in GitHub Actions where external source bytes can be retrieved. Do not
invent source permissions, pixel-scale anatomy or specimen continuity.
"""
import hashlib
import io
import json
import pathlib
import time
import requests
from PIL import Image

ROOT = pathlib.Path("content/taxa/Poaceae/Tripsacum")
SPECIES = ROOT / "tripsacum-dactyloides/species.json"
GENUS = ROOT / "genus.json"
IMAGES = ROOT / "tripsacum-dactyloides/images"
REPORT = pathlib.Path("reports/tripsacum-uvalde-conrad-five-physical-20261022.json")
RELEASE = pathlib.Path("workflow/field-id-publication/2026-10-22-tripsacum-five-uvalde-physical-release.json")
SRC = "https://www.backyardnature.net/n/h/gama.htm"
RIGHTS = "https://www.backyardnature.net/j/copyrite.htm"
ENTRIES = (
    ("140504tr.jpg", "jim-conrad-uvalde-2014-rooted-clump-public-domain.jpg", "rooted standing clump; roots not exposed"),
    ("140504ts.jpg", "jim-conrad-uvalde-2014-complete-flowering-spikes-public-domain.jpg", "whole intact inflorescence with multiple spikes"),
    ("140504tt.jpg", "jim-conrad-uvalde-2014-staminate-anthers-public-domain.jpg", "upper male anthers, not female stigmas"),
    ("140504tu.jpg", "jim-conrad-uvalde-2014-pistillate-stigmas-public-domain.jpg", "lower pistillate stigmas and immature joint"),
    ("140720tr.jpg", "jim-conrad-uvalde-2014-maturing-female-joints-public-domain.jpg", "attached maturing seed-bearing joints; no detached grain"),
)
s = json.loads(SPECIES.read_text(encoding="utf-8"))
g = json.loads(GENUS.read_text(encoding="utf-8"))
assert s["id"] == "tripsacum-dactyloides"
assert g["name"] == "Tripsacum"
assert s["project_inclusion"]["target_zone_status"] == "PASS"
assert len(s["visual_comparison"]["items"]) == 7
assert len(g["visual_comparison"]["items"]) == 5
assert len(s["images"]) == 10
assert s["curation_status"]["photo_files_present"] in (2,7)
session = requests.Session()
session.headers.update({"User-Agent": "HaysCountyBotanyPhotoArchive/1.0 (educational credited originals)", "Accept": "image/jpeg,image/*;q=0.9"})
report = {"species":"Tripsacum dactyloides", "date":"2026-10-22", "source_page":SRC, "rights_url":RIGHTS,
          "permission":"Jim Conrad's original Backyard Nature photos expressly released by author into public domain; original attribution retained",
          "files": [], "already_archived": [], "exact_new_physical_files":0,
          "excluded":"Third-party, uncredited, unvouchered, or unlicensed media excluded"}
IMAGES.mkdir(parents=True, exist_ok=True)

for original_name, filename, subject in ENTRIES:
    url = "https://www.backyardnature.net/n/14/" + original_name
    dst = IMAGES / filename
    original = next((p for p in s["images"] if p.get("source_image") == url and p.get("creator") == "Jim Conrad"), None)
    assert original is not None, ("Original Jim Conrad source record missing", url)
    assert original.get("source_page") == SRC and original.get("license_url") == RIGHTS
    assert "Public domain" in original.get("license","")
    if not dst.exists():
        last_error = None
        for attempt in range(3):
            try:
                response = session.get(url, timeout=35)
                response.raise_for_status()
                if not response.content.startswith(bytes.fromhex("ffd8ff")):
                    raise ValueError("Source is not original JPEG")
                if not (4000 < len(response.content) < 8000000):
                    raise ValueError("Unexpected downloaded image size")
                with Image.open(io.BytesIO(response.content)) as opened:
                    opened.load()
                    if opened.format != "JPEG" or min(opened.size) < 150:
                        raise ValueError("Not adequate original JPEG")
                    if opened.getexif().get(274, 1) != 1:
                        raise ValueError("Nontrivial EXIF orientation needs manual arrow recalibration")
                    pixels = opened.convert("RGB")
                    dims = opened.size
                pixels.save(dst, "JPEG", quality=92, optimize=True)
                break
            except (requests.RequestException, ValueError, OSError) as exc:
                last_error = str(exc)
                if attempt < 2: time.sleep(3 * (attempt+1))
        else:
            raise RuntimeError(f"Could not archive source {url}: {last_error}")
        report["exact_new_physical_files"] += 1
    else:
        report["already_archived"].append(str(dst))
        with Image.open(dst) as existing: dims = existing.size

    data = dst.read_bytes()
    if not data.startswith(bytes.fromhex("ffd8ff")) or len(data) < 3000:
        raise ValueError(f"Invalid archived file: {dst}")
    with Image.open(dst) as chk:
        if chk.format != "JPEG" or chk.mode != "RGB" or min(chk.size) < 150:
            raise ValueError(f"Failed JPEG pixel integrity: {dst}")
        if chk.getexif().get(34853):
            raise ValueError(f"GPS EXIF retained: {dst}")
        dims = chk.size
        chk.verify()
    local = "images/" + filename
    complete_path = str(dst)
    original["file"] = local
    original["image_dimensions"] = list(dims)
    original["archive_sha256"] = hashlib.sha256(data).hexdigest()
    original["image_status"] = "PHYSICALLY_ARCHIVED_SOURCE_VERIFIED_PROVISIONAL_USER_REVIEW"
    original["public_reuse"] = "yes"
    original["modifications"] = "Actual original Jim Conrad JPEG decoded and re-encoded RGB, GPS/EXIF stripped; no crop; original author/source/PD attribution preserved. Previous source URL remains in source_image."
    matches_species = [p for p in s["visual_comparison"]["items"] if p.get("image_url") == url]
    assert len(matches_species) == 1, (url, len(matches_species))
    for panel in matches_species:
        panel["image_url"] = complete_path
        panel["photo_status"] = "Original Uvalde source successfully physically archived with creator/PD terms; 1:1 aspect, no crop; PROVISIONAL — USER PHOTO REVIEW PENDING."
        for arrow in panel.get("markers", []):
            assert all(0 <= arrow[k] <= 100 for k in ("label_x","label_y","target_x","target_y"))
    for panel in g["visual_comparison"]["items"]:
        if panel.get("image_url") == url:
            panel["image_url"] = complete_path
            panel["photo_status"] = "Original public-domain Jim Conrad Uvalde source physically archived; visual anatomical arrows retain previous provisional source inspection."
    report["files"].append({"original_url":url, "local_file":complete_path, "role":subject,
                           "archived_sha256":original["archive_sha256"], "dimensions":list(dims),
                           "bytes":len(data), "creator":"Jim Conrad","rights_url":RIGHTS,
                           "species_panels":len(matches_species)})
assert len(report["files"]) == 5
assert sum(x["species_panels"] for x in report["files"]) == 5
assert sum(1 for p in s["images"] if str(p.get("file","")).startswith("images/")) == 7
assert len([p for p in s["visual_comparison"]["items"] if "backyardnature.net/n/14/" in p.get("image_url","")]) == 0
assert len([p for p in g["visual_comparison"]["items"] if "backyardnature.net/n/14/" in p.get("image_url","")]) == 0
s["curation_status"]["photo_files_present"] = 7
s["curation_status"]["manual_tripsacum_five_pd_originals_physically_archived_20261022"] = (
    "Five real credited Jim Conrad public-domain Uvalde photos permanently stored in canonical species images. "
    "Seven physically present teaching-gallery source photographs, species count 7, genus count 5; source and rights verified; arrows preserve original review status."
)
f = s["field_id_finish_pass"]
f["source_photo_status"] = (
    "Seven real locally archived source image files: two earlier Brittany Hamilton provisional CC0 files, "
    "five new actual Jim Conrad original public-domain Uvalde JPEGs; original author attribution and links preserved. "
    "Provisional photo-review labels remain; no known connected-voucher 1mm anatomy."
)
f["new_image_files"] = 5
f["archived_real_photo_files"] = 7
f["diagnostic_second_pass_20261022"]["new_archived_bytes"] = 5
f["diagnostic_second_pass_20261022"]["added_external_original_photos"] = 0
f["diagnostic_second_pass_20261022"]["original_external_links_now_physically_archived"] = 5
f["diagnostic_second_pass_20261022"]["archive_report"] = str(REPORT)
# Measurement values are source treatment descriptions, NOT drawn from unscaled images.
f["measured_description_only"] = {
    "true_ligule": "Tropical Forages describes an approximately 1–1.5 mm fringed membrane; neither broad habit nor spikes image resolves the TRUE free membrane at scale.",
    "ripe_pistillate_joint": "Tropical Forages describes ~7–10 mm detachable female rachis joint; Uvalde attached ripe segment photograph is NOT a 1mm-calibrated separated grain.",
    "reference": "https://tropicalforages.info/pdf/tripsacum_dactyloides.pdf",
    "status": "LITERATURE_MEASUREMENTS_NOT_PHOTOGRAPHIC_PIXEL_VERIFICATION"
}
s["field_photo_quickcheck"].setdefault("notes", [])
# Do not invent cross-source same-voucher identity or declare FINISHED.
assert "FIELD_READY_PHOTO_GAPS" in f["stage"]
SPECIES.write_text(json.dumps(s, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
GENUS.write_text(json.dumps(g, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
REPORT.parent.mkdir(exist_ok=True, parents=True)
REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n",encoding="utf-8")
RELEASE.parent.mkdir(exist_ok=True, parents=True)
RELEASE.write_text(json.dumps({
    "type":"manual_field_id_publication","date":"2026-10-22",
    "species":"Tripsacum dactyloides", "photo_source":"Jim Conrad Uvalde original public-domain images",
    "source_page":SRC,"rights_url":RIGHTS,"report":str(REPORT),
    "new_physical_photos":5,"total_actual_archived_species_photos":7,
    "species_photo_panels":7, "genus_photo_panels":5,
    "source_permission":"Author specifically releases his original Backyard Nature photos to public domain; no third-party photos silently included",
    "release":"normal rights-filtered GitHub Pages; not considered live until successful deployment",
    "status":"FIELD_READY_PHOTO_GAPS",
    "remaining_true_photo_gaps":[
      "1 mm calibrated true fringed membrane at collar on source-verified living specimen",
      "Measured single detached female joint exposing actual enclosed caryopsis",
      "Source-vouchered connected rhizome, leaf, male/female spike and same-spike macro"
    ],"county_status_untouched":True
},indent=2)+"\n",encoding="utf-8")
print("ARCHIVED FIVE JIM CONRAD UVALDE ORIGINALS; SIXTH/OTHER UNLICENSED IMAGES NOT TOUCHED", flush=True)
