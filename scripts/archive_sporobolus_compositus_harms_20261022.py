#!/usr/bin/env python3
"""Fail-closed archive of eight exact Bob Harms composite-dropseed originals.
Five photographed as var. drummondii, three as var. macer. Author-owned images
are permitted with credit for scientific/educational use, NOT Creative Commons.
Download and validate ALL before modifying canonical cards. No anatomy arrows.
"""
import csv
import hashlib
import io
import json
import time
from pathlib import Path

import requests
from PIL import Image, ImageOps

ROOT = Path(".")
BASE = ROOT / "content/taxa/Poaceae/Sporobolus"
SP = BASE / "sporobolus-compositus/species.json"
GN = BASE / "genus.json"
CSV = SP.parent / "image-sources.csv"
REPORT = ROOT / "reports/sporobolus-compositus-physical-harms-eight-20261022.json"
MARKER = ROOT / "workflow/field-id-publication/2026-10-22-sporobolus-compositus-eight-archived-harms.json"
SOURCE = "https://w3.biosci.utexas.edu/prc/Monocots/GrassHTML/data/"
LIC = "© Bob Harms — scientific/educational use with credit only (NOT Creative Commons)"
PERMISSION = "BOB_HARMS_SELECTED_MONOCOTS_EDU_WITH_CREDIT_20261022"
IDS = ("SPCOD3-b", "SPCOD3-i", "SPCOD3-J0", "SPCOD3-J1", "SPCOD3-v",
       "SPCOM-b", "SPCOM-j1", "SPCOM-8")


def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def verify_and_clean(session, url):
    errors = []
    for attempt in range(2):
        try:
            response = session.get(url, timeout=35, headers={"Accept": "image/jpeg,image/*"})
            response.raise_for_status()
            raw = response.content
            if not 8000 < len(raw) < 9_000_000 or not raw.startswith(b"\xff\xd8\xff"):
                raise RuntimeError("Unexpected source bytes")
            with Image.open(io.BytesIO(raw)) as original:
                original.load()
                w, h = original.size
                if original.format != "JPEG" or min(w, h) < 50 or max(w, h) > 8500 or w*h < 15000:
                    raise RuntimeError("Source pixels too small or unreadable: " + str((w, h)))
                clean = ImageOps.exif_transpose(original).convert("RGB")
            clean.thumbnail((2400, 2400), Image.Resampling.LANCZOS)
            dst = io.BytesIO()
            clean.save(dst, "JPEG", quality=91, optimize=True)
            encoded = dst.getvalue()
            if len(encoded) < 7000:
                raise RuntimeError("Archived JPEG too small")
            with Image.open(io.BytesIO(encoded)) as check:
                assert check.format == "JPEG" and not check.getexif().get(34853)
                check.verify()
            return raw, encoded, [w, h], list(clean.size), response.url
        except Exception as exc:
            errors.append(type(exc).__name__ + ": " + str(exc)[:150])
            if attempt == 0:
                time.sleep(2)
    raise RuntimeError("Download held, no partial files installed: " + url + " " + repr(errors))


def main():
    species = json.loads(SP.read_text(encoding="utf-8"))
    genus = json.loads(GN.read_text(encoding="utf-8"))
    assert species["id"] == "sporobolus-compositus" and genus["name"] == "Sporobolus"
    assert genus["project_scope"]["canonical_species_count"] == 3
    if (len(species["images"]), len(species["visual_comparison"]["items"]),
        len(genus["visual_comparison"]["items"])) != (10, 12, 33):
        raise RuntimeError("Concurrent species/genus edit; refetch before retry")
    protected = {k: json.dumps(species.get(k), sort_keys=True) for k in
        ("project_inclusion","county_occurrences_target_zone","native_target_zone_calculated",
         "target_zone_count","synonyms","taxonomic_note")}
    old_scope = json.dumps(genus["project_scope"], sort_keys=True)
    with CSV.open(newline="", encoding="utf-8") as fp:
        reader = csv.DictReader(fp)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    if "file_name" not in fields:
        raise RuntimeError("Source registry missing filename column")
    prepared = []
    session = requests.Session()
    session.headers.update({"User-Agent":"HaysBotanyExactOriginalEducationArchive/1.0"})
    for ident in IDS:
        source_url = SOURCE + "images/" + ident + ".jpg"
        page = SOURCE + "pages/" + ident + ".html"
        variety = ("Sporobolus compositus var. drummondii" if ident.startswith("SPCOD3-")
                   else "Sporobolus compositus var. macer")
        image_records = [x for x in species["images"] if x.get("file") == source_url
                         and x.get("source_page") == page]
        sp_panels = [x for x in species["visual_comparison"]["items"] if x.get("image_url") == source_url]
        gn_panels = [x for x in genus["visual_comparison"]["items"] if x.get("image_url") == source_url]
        if len(image_records) != 1 or len(sp_panels) != 1 or len(gn_panels) != 1:
            raise RuntimeError("Exact source/panels not present: " + ident)
        record = image_records[0]
        if (record.get("creator") != "Bob Harms" or record.get("license") != LIC
            or record.get("source_taxon") != variety
            or record.get("license_url") != "https://w3.biosci.utexas.edu/prc/Monocots/"):
            raise RuntimeError("Taxon/variety/photo rights mismatch: " + ident)
        target = SP.parent / "images" / ("bob-harms-" + ident.lower() + "-composite-dropseed.jpg")
        if target.exists() or any(row.get("file_name") == target.name for row in rows):
            raise RuntimeError("Would overwrite existing archive/registry photo: " + str(target))
        raw, encoded, original_size, stored_size, actual_url = verify_and_clean(session, source_url)
        prepared.append((ident, source_url, page, variety, target, record, sp_panels[0], gn_panels[0],
                         raw, encoded, original_size, stored_size, actual_url))
        print("VERIFIED", ident, original_size, len(encoded), flush=True)
    assert len(prepared) == 8
    archived = []
    for (ident, source_url, page, variety, target, record, sp_panel, gn_panel,
         raw, data, original_size, stored_size, actual_url) in prepared:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        record.update({
            "file":"images/" + target.name, "source_image":source_url,
            "source_taxon_name":"Sporobolus compositus", "source_variety":variety,
            "site_specific_public_permission":PERMISSION,
            "source_original_sha256":hashlib.sha256(raw).hexdigest(),
            "archived_sha256":hashlib.sha256(data).hexdigest(),
            "original_image_size":original_size,"archived_image_size":stored_size,
            "downloaded_from":actual_url,"archived_locally":True,
            "modifications":"Original author JPEG re-encoded RGB at <=2400px edge; EXIF/GPS removed; no anatomy arrows added.",
            "public_reuse":"Credited scientific/educational use of Bob Harms Selected Central Texas Monocots originals only; copyrighted, NOT CC."
        })
        for panel in (sp_panel, gn_panel):
            panel["image_url"] = str(target)
            panel["source_image"] = source_url
            panel["source_taxon_name"] = "Sporobolus compositus"
            panel["source_variety"] = variety
            panel["site_specific_public_permission"] = PERMISSION
            panel["photo_status"] = (
                "PHYSICALLY ARCHIVED credited original Bob Harms educational image. "
                "Taxon/variety sourced from author; provisional user anatomical review; "
                "no new pixel markers. Rhizomes in var. macer ONLY."
            )
        csv_data = {
            "file_name":target.name, "role":record["role"], "creator":"Bob Harms",
            "license":LIC,"license_url":record["license_url"],"source_page":page,
            "direct_url":actual_url,"study_use":"Noncommercial scientific/educational public learner",
            "public_reuse":record["public_reuse"],"modifications":record["modifications"]
        }
        rows.append({col:csv_data.get(col,"") for col in fields})
        archived.append({
            "source_photo_id":ident,"source_variety":variety,"image_path":str(target),
            "source_page":page,"source_original_sha256":record["source_original_sha256"],
            "archived_sha256":record["archived_sha256"],
            "original_dimensions":original_size,"archived_dimensions":stored_size
        })
    assert all(json.dumps(species.get(k),sort_keys=True) == old for k,old in protected.items())
    assert json.dumps(genus["project_scope"], sort_keys=True) == old_scope
    species["curation_status"]["photo_metadata_count"] = 10
    species["curation_status"]["photo_files_present"] = 10
    species["curation_status"]["sporobolus_compositus_photo_second_pass_20261022"]["newly_archived_binary_images"] = 8
    species["curation_status"]["sporobolus_compositus_photo_second_pass_20261022"]["physically_archived_and_source_verified"] = True
    species["curation_status"]["harms_compositus_eight_physical_20261022"] = (
        "Five var. drummondii plus three var. macer exact author originals stored. "
        "Only var. macer rhizome photo; no species-wide rhizome generalization."
    )
    species["field_id_finish_pass"]["stage"] = (
        "FIELD_READY_PHOTO_GAPS — eight physical author-credited composite dropseed photos "
        "show real varieties, flowering units and var. macer rhizome. Needs same-source "
        "1mm glume and lemma dissection, 0.1–0.5mm true ligule, timed mature grain wet pericarp "
        "reaction, 400x lemma cells and local Hays rooted flowering specimen."
    )
    species["field_id_finish_pass"]["physical_archive_20261022"] = {
        "new_real_JPEGs":8,"local_species_photos":10,"new_anatomy_arrows":0,
        "variety_specific_rights":True,"stage":"FIELD_READY_PHOTO_GAPS"
    }
    genus["curation_status"]["compositus_diagnostic_second_pass_20261022"]["newly_archived_binary_images"] = 8
    genus["curation_status"]["compositus_diagnostic_second_pass_20261022"]["photos_locally_archived_and_verified"] = True
    genus["visual_comparison"]["subtitle"] += (
        " Eight original composite-dropseed varietal photos are now physically archived, "
        "with variety-specific attribution and no invented macro arrows."
    )
    with CSV.open("w",newline="",encoding="utf-8") as fp:
        writer = csv.DictWriter(fp,fieldnames=fields,lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    save(SP,species)
    save(GN,genus)
    save(REPORT, {
        "result":"EIGHT_REAL_HARMS_COMPOSITE_DROPSEED_IMAGES_PHYSICALLY_ARCHIVED",
        "species":"Sporobolus compositus","files":archived,
        "physical_new_images":8,"local_species_photo_files":10,
        "species_panels":12,"genus_panels":33,
        "copyright":"Bob Harms original, credited science/education ONLY, NOT CC",
        "native_taxon_range_unchanged":True,"stage":"FIELD_READY_PHOTO_GAPS"
    })
    save(MARKER, {
        "date":"2026-10-22","taxon":"Sporobolus compositus","type":"manual_field_id_publication",
        "report":str(REPORT),"physical_new_images":8,"total_species_photos":10,
        "scope":"Five var. drummondii plus three var. macer credited Harms originals",
        "approval":"User reviews on ordinary public learner", "stage":"FIELD_READY_PHOTO_GAPS",
        "publish":"NORMAL_RIGHTS_FILTERED_GITHUB_PAGES"
    })
    print("SUCCESS eight true variety-specific composite dropseed JPEGs, stage PHOTO_GAPS")


if __name__ == "__main__":
    main()
