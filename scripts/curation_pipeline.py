#!/usr/bin/env python3
"""
Hays Botany automated curation pipeline.

A batch is any folder directly under curation-inbox/ that contains batch.json.

Expected shape:
curation-inbox/<batch-id>/
  batch.json
  taxa/
    Family/
      family.json               (optional)
      Genus/
        genus.json              (optional)
        species-id/
          species.json          (required)
          SOURCES.txt           (required)
          image-sources.csv     (optional until exact images are selected)
          images/               (optional)

When --apply is supplied, validated packages are installed into content/taxa/,
exact-image rows with direct URLs are downloaded, data/manifest.json is rebuilt,
data/project.json species_count is updated, a report is written, and the batch is
moved to curation-archive/.
"""
from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INBOX = ROOT / "curation-inbox"
ARCHIVE = ROOT / "curation-archive"
CONTENT = ROOT / "content" / "taxa"
DATA = ROOT / "data"
REPORTS = ROOT / "reports"

REQUIRED_SPECIES_FIELDS = ("id", "family", "genus", "common_name")
IMAGE_URL_COLUMNS = ("direct_url", "direct_image_url", "image_url", "url")
IMAGE_ROLE_COLUMNS = ("role", "view", "image_role")
USER_AGENT = "HaysBotanyID-GitHubAction/1.0"
DOWNLOAD_DELAY_SECONDS = 15
RETRY_DELAY_SECONDS = 75


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")


def scientific_name(sp: dict) -> str:
    if sp.get("scientific_name"):
        return str(sp["scientific_name"])
    parts = [sp.get("genus"), sp.get("species")]
    if sp.get("subspecies"):
        parts += ["subsp.", sp["subspecies"]]
    if sp.get("variety"):
        parts += ["var.", sp["variety"]]
    return " ".join(str(x) for x in parts if x)


def validate_species_file(path: Path) -> tuple[dict, list[str]]:
    warnings: list[str] = []
    sp = load_json(path)
    missing = [k for k in REQUIRED_SPECIES_FIELDS if not sp.get(k)]
    if missing:
        raise ValueError(f"{path}: missing required field(s): {', '.join(missing)}")
    if not (sp.get("scientific_name") or sp.get("species")):
        raise ValueError(f"{path}: needs scientific_name or species")
    expected_folder = sp["id"]
    if path.parent.name != expected_folder:
        raise ValueError(
            f"{path}: folder '{path.parent.name}' does not match id '{expected_folder}'"
        )
    if not (path.parent / "SOURCES.txt").exists():
        raise ValueError(f"{path}: missing SOURCES.txt")
    if not (path.parent / "image-sources.csv").exists():
        warnings.append(f"{sp['id']}: image-sources.csv not present yet; photos remain pending")
    return sp, warnings


def merge_genus_json(src: Path, dst: Path) -> None:
    incoming = load_json(src)
    if not dst.exists():
        write_json(dst, incoming)
        return

    current = load_json(dst)
    merged = dict(current)

    # Incoming descriptive fields are allowed to refresh the genus entry.
    for key, value in incoming.items():
        if key != "project_scope":
            merged[key] = value

    cur_scope = dict(current.get("project_scope") or {})
    in_scope = dict(incoming.get("project_scope") or {})
    merged_scope = dict(cur_scope)
    merged_scope.update(in_scope)

    ids = []
    for source in (cur_scope.get("species_ids") or [], in_scope.get("species_ids") or []):
        for taxon_id in source:
            if taxon_id not in ids:
                ids.append(taxon_id)
    if ids:
        merged_scope["species_ids"] = ids
        merged_scope["species_count"] = len(ids)
    merged["project_scope"] = merged_scope
    write_json(dst, merged)


def first_nonempty(row: dict, names: tuple[str, ...]) -> str:
    for name in names:
        value = (row.get(name) or "").strip()
        if value:
            return value
    return ""


def download_one(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    last_error = None
    for attempt in (1, 2):
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                destination.write_bytes(response.read())
            return
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
            if attempt == 1:
                time.sleep(RETRY_DELAY_SECONDS)
    raise RuntimeError(f"failed to download {url}: {last_error}")


def optimize_image(path: Path) -> None:
    # Pillow is installed by the GitHub workflow. If unavailable, leave the source as-is.
    try:
        from PIL import Image, ImageOps
    except Exception:
        return
    try:
        with Image.open(path) as im:
            im = ImageOps.exif_transpose(im)
            im.thumbnail((1600, 1600))
            suffix = path.suffix.lower()
            if suffix in (".jpg", ".jpeg"):
                if im.mode not in ("RGB", "L"):
                    im = im.convert("RGB")
                im.save(path, quality=85, optimize=True, progressive=True)
            elif suffix == ".png":
                im.save(path, optimize=True)
    except Exception:
        # Never destroy a successfully downloaded source because optimization failed.
        return


def process_image_csv(species_dir: Path, require_exact_images: bool, report: dict) -> None:
    csv_path = species_dir / "image-sources.csv"
    if not csv_path.exists():
        if require_exact_images:
            raise ValueError(f"{species_dir.name}: exact images required but image-sources.csv is missing")
        return

    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        if require_exact_images:
            raise ValueError(f"{species_dir.name}: image-sources.csv is empty")
        return

    downloaded_any = False
    for index, row in enumerate(rows):
        file_name = (row.get("file_name") or "").strip()
        role = first_nonempty(row, IMAGE_ROLE_COLUMNS)
        creator = (row.get("creator") or row.get("photographer") or row.get("observer") or "").strip()
        license_value = (row.get("license") or "").strip()
        source_page = (row.get("source_page") or row.get("source_url") or "").strip()
        direct_url = first_nonempty(row, IMAGE_URL_COLUMNS)

        if not file_name:
            raise ValueError(f"{csv_path}: a row is missing file_name")
        if not role:
            report["warnings"].append(f"{species_dir.name}/{file_name}: image role is blank")
        if not creator:
            report["warnings"].append(f"{species_dir.name}/{file_name}: creator is blank")
        if not license_value:
            report["warnings"].append(f"{species_dir.name}/{file_name}: license is blank")
        if not source_page:
            report["warnings"].append(f"{species_dir.name}/{file_name}: source_page is blank")

        if not direct_url:
            msg = f"{species_dir.name}/{file_name}: exact direct image URL not recorded yet"
            if require_exact_images:
                raise ValueError(msg)
            report["warnings"].append(msg)
            continue

        out = species_dir / "images" / file_name
        if out.exists() and out.stat().st_size > 0:
            report["images_skipped_existing"].append(str(out.relative_to(ROOT)))
            continue

        if downloaded_any:
            time.sleep(DOWNLOAD_DELAY_SECONDS)
        download_one(direct_url, out)
        optimize_image(out)
        downloaded_any = True
        report["images_downloaded"].append(str(out.relative_to(ROOT)))


def copy_species_package(src_species_dir: Path, dst_species_dir: Path) -> None:
    dst_species_dir.mkdir(parents=True, exist_ok=True)
    for item in src_species_dir.iterdir():
        if item.name == "images":
            # Existing curated image files, if any, are copied. Placeholder README files are harmless.
            if item.is_dir():
                (dst_species_dir / "images").mkdir(parents=True, exist_ok=True)
                for img_item in item.iterdir():
                    if img_item.is_file() and img_item.name.lower() != "readme.txt":
                        shutil.copy2(img_item, dst_species_dir / "images" / img_item.name)
            continue
        if item.is_file():
            shutil.copy2(item, dst_species_dir / item.name)


def install_batch(batch_dir: Path, batch: dict, report: dict) -> None:
    taxa_root = batch_dir / "taxa"
    if not taxa_root.exists():
        raise ValueError(f"{batch_dir}: missing taxa/ folder")

    require_exact_images = bool(batch.get("require_exact_images", False))
    validated: list[tuple[Path, dict]] = []

    for species_json in sorted(taxa_root.glob("*/*/*/species.json")):
        sp, warnings = validate_species_file(species_json)
        report["warnings"].extend(warnings)
        validated.append((species_json, sp))

    if not validated:
        raise ValueError(f"{batch_dir}: no species.json files found under taxa/Family/Genus/species-id/")

    seen_ids = set()
    for _, sp in validated:
        if sp["id"] in seen_ids:
            raise ValueError(f"{batch_dir}: duplicate species id {sp['id']}")
        seen_ids.add(sp["id"])

    if batch.get("mode", "install") == "validate_only":
        report["validated_only"].extend(sorted(seen_ids))
        return

    # Family and genus metadata first.
    for family_dir in sorted(p for p in taxa_root.iterdir() if p.is_dir()):
        dst_family = CONTENT / family_dir.name
        dst_family.mkdir(parents=True, exist_ok=True)
        family_json = family_dir / "family.json"
        if family_json.exists() and not (dst_family / "family.json").exists():
            shutil.copy2(family_json, dst_family / "family.json")

        for genus_dir in sorted(p for p in family_dir.iterdir() if p.is_dir()):
            dst_genus = dst_family / genus_dir.name
            dst_genus.mkdir(parents=True, exist_ok=True)
            genus_json = genus_dir / "genus.json"
            if genus_json.exists():
                merge_genus_json(genus_json, dst_genus / "genus.json")

    # Species packages.
    for species_json, sp in validated:
        rel = species_json.parent.relative_to(taxa_root)
        dst_species = CONTENT / rel
        copy_species_package(species_json.parent, dst_species)
        process_image_csv(dst_species, require_exact_images, report)
        report["installed_species"].append(
            {"id": sp["id"], "scientific_name": scientific_name(sp), "path": str(dst_species.relative_to(ROOT))}
        )


def rebuild_manifest(report: dict) -> None:
    species_entries = []
    seen = set()
    for path in sorted(CONTENT.glob("*/*/*/species.json")):
        sp = load_json(path)
        taxon_id = sp.get("id")
        if not taxon_id:
            raise ValueError(f"{path}: missing id during manifest rebuild")
        if taxon_id in seen:
            raise ValueError(f"duplicate id in canonical content: {taxon_id}")
        seen.add(taxon_id)
        species_entries.append({"id": taxon_id, "path": str(path.relative_to(ROOT)).replace("\\", "/")})

    manifest_path = DATA / "manifest.json"
    manifest = load_json(manifest_path) if manifest_path.exists() else {}
    manifest["project"] = manifest.get("project", "data/project.json")
    manifest["terms"] = manifest.get("terms", [])
    manifest["species"] = species_entries
    write_json(manifest_path, manifest)

    project_path = DATA / "project.json"
    project = load_json(project_path) if project_path.exists() else {}
    project["species_count"] = len(species_entries)
    project["last_automated_manifest_update"] = datetime.now(timezone.utc).isoformat()
    write_json(project_path, project)
    report["canonical_species_count"] = len(species_entries)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="install validated batches")
    args = parser.parse_args()

    INBOX.mkdir(parents=True, exist_ok=True)
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    batch_dirs = sorted(
        p for p in INBOX.iterdir()
        if p.is_dir() and (p / "batch.json").exists()
    )

    report = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "apply": args.apply,
        "batches": [],
        "validated_only": [],
        "installed_species": [],
        "images_downloaded": [],
        "images_skipped_existing": [],
        "warnings": [],
    }

    for batch_dir in batch_dirs:
        batch = load_json(batch_dir / "batch.json")
        batch_id = batch.get("batch_id") or batch_dir.name
        report["batches"].append(batch_id)
        install_batch(batch_dir, batch, report)

        if args.apply and batch.get("mode", "install") != "validate_only":
            archive_dest = ARCHIVE / batch_dir.name
            if archive_dest.exists():
                shutil.rmtree(archive_dest)
            shutil.move(str(batch_dir), str(archive_dest))

    if args.apply:
        rebuild_manifest(report)

    report["finished_at"] = datetime.now(timezone.utc).isoformat()
    write_json(REPORTS / "last-curation-run.json", report)

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"CURATION PIPELINE FAILED: {exc}", file=sys.stderr)
        raise
