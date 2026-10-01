#!/usr/bin/env python3
"""
One-time Hays Botany historical taxa ZIP backfill importer.

Purpose:
- Import the consolidated taxa.zip produced before the GitHub inbox workflow was adopted.
- Fully import Asteraceae packages (new backlog species + photos).
- Preserve newer canonical non-Asteraceae taxonomy/range/morphology files while backfilling
  their photo binaries and image-source logs.
- Skip the obsolete duplicate Conoclinium greggii package in favor of Conoclinium dissectum.
- Patch canonical species.json image arrays from image-sources.csv.
- Rebuild data/manifest.json and data/project.json species_count.
- Optionally commit and push the result.

This is intentionally a ONE-TIME migration tool. Future curation batches should go through
curation-inbox/ and the GitHub Action.
"""
from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content" / "taxa"
DATA = ROOT / "data"

SKIP_IDS = {"conoclinium-greggii"}
FULL_IMPORT_FAMILIES = {"Asteraceae"}
PHOTO_SIDE_FILES = {"image-sources.csv", "PHOTO-SET-NOTES.txt"}

def load_json(path: Path):
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)

def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")

def find_taxa_root(extracted: Path) -> Path:
    direct = extracted / "taxa"
    if direct.exists():
        return direct
    candidates = [p for p in extracted.rglob("taxa") if p.is_dir()]
    if len(candidates) == 1:
        return candidates[0]
    raise RuntimeError("Could not uniquely locate the taxa/ folder in the ZIP.")

def iter_species_dirs(taxa_root: Path):
    """
    Yield every species package in either the current
    taxa/Family/Genus/species-id/species.json layout or older flat
    taxa/Family/species-id/species.json layouts.
    """
    seen = set()
    candidates = list(taxa_root.glob("*/*/*/species.json"))
    candidates += list(taxa_root.glob("*/*/species.json"))
    for species_json in sorted(candidates):
        if species_json in seen:
            continue
        seen.add(species_json)
        yield species_json.parent, load_json(species_json)

def csv_value(row: dict, *keys: str) -> str:
    for key in keys:
        value = (row.get(key) or "").strip()
        if value:
            return value
    return ""

def public_reuse_from_license(license_text: str, attribution: str) -> str:
    text = f"{license_text} {attribution}".lower()
    if "all rights reserved" in text or "license not supplied" in text or not license_text.strip():
        return "no"
    if "cc0" in text or "public domain" in text:
        return "yes"
    if "cc-by" in text or "cc by" in text:
        return "review" if "-nc" in text or " by-nc" in text else "yes"
    return "review"

def image_records_from_csv(species_dir: Path):
    csv_path = species_dir / "image-sources.csv"
    images_dir = species_dir / "images"
    if not csv_path.exists():
        return None

    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    records = []
    for row in rows:
        file_name = csv_value(row, "file_name", "filename")
        if not file_name:
            continue
        local_file = images_dir / file_name
        if not local_file.exists():
            continue

        role = csv_value(row, "role", "view", "image_role") or "curated study image"
        creator = csv_value(row, "creator", "photographer", "observer", "attribution")
        license_text = csv_value(row, "license", "license_code")
        source_page = csv_value(row, "source_page", "observation_url", "source_url")
        direct_url = csv_value(row, "direct_image_url", "image_url", "direct_url")
        observation_id = csv_value(row, "observation_id")
        photo_id = csv_value(row, "photo_id")
        platform = csv_value(row, "platform")
        if not platform:
            if "inaturalist" in (source_page + direct_url).lower():
                platform = "iNaturalist"
            elif "wikimedia" in (source_page + direct_url).lower():
                platform = "Wikimedia Commons"

        records.append({
            "file": f"images/{file_name}",
            "role": role,
            "creator": creator,
            "license": license_text,
            "source_page": source_page,
            "direct_image_url": direct_url,
            "platform": platform,
            "observation_id": observation_id,
            "photo_id": photo_id,
            "study_use": "yes",
            "public_reuse": public_reuse_from_license(license_text, creator),
        })
    return records

def copy_tree_files(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.rglob("*"):
        if not item.is_file():
            continue
        rel = item.relative_to(src)
        out = dst / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, out)

def backfill_photos_only(src_species: Path, dst_species: Path) -> None:
    if not dst_species.exists():
        raise RuntimeError(
            f"Canonical species folder is missing for photo-only backfill: {dst_species}"
        )
    src_images = src_species / "images"
    if src_images.exists():
        dst_images = dst_species / "images"
        dst_images.mkdir(parents=True, exist_ok=True)
        for item in src_images.iterdir():
            if item.is_file() and item.name.lower() != "readme.txt":
                shutil.copy2(item, dst_images / item.name)

    for name in PHOTO_SIDE_FILES:
        src = src_species / name
        if src.exists():
            shutil.copy2(src, dst_species / name)

def patch_species_images(dst_species: Path) -> int:
    species_json = dst_species / "species.json"
    if not species_json.exists():
        return 0
    records = image_records_from_csv(dst_species)
    if records is None:
        return len(load_json(species_json).get("images") or [])
    sp = load_json(species_json)
    sp["images"] = records
    status = dict(sp.get("curation_status") or {})
    status["photo_metadata_count"] = len(records)
    status["photo_files_present"] = len(records)
    status["photo_backfill_source"] = "historical taxa.zip migration"
    sp["curation_status"] = status
    write_json(species_json, sp)
    return len(records)

def rebuild_manifest() -> int:
    entries = []
    seen = set()
    for path in sorted(CONTENT.glob("*/*/*/species.json")):
        sp = load_json(path)
        taxon_id = sp.get("id")
        if not taxon_id:
            raise RuntimeError(f"{path}: missing id")
        if taxon_id in seen:
            raise RuntimeError(f"Duplicate canonical species id: {taxon_id}")
        seen.add(taxon_id)
        entries.append({
            "id": taxon_id,
            "path": str(path.relative_to(ROOT)).replace("\\", "/")
        })

    manifest_path = DATA / "manifest.json"
    manifest = load_json(manifest_path)
    manifest["species"] = entries
    write_json(manifest_path, manifest)

    project_path = DATA / "project.json"
    project = load_json(project_path)
    project["species_count"] = len(entries)
    project["historical_photo_backfill"] = "taxa.zip migration completed"
    write_json(project_path, project)
    return len(entries)

def git(*args: str, check=True):
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        check=check,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("zip_path", nargs="?", default=str(ROOT / "taxa.zip"))
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--commit-push", action="store_true")
    args = parser.parse_args()

    zip_path = Path(args.zip_path).expanduser()
    if not zip_path.is_absolute():
        zip_path = (ROOT / zip_path).resolve()
    if not zip_path.exists():
        raise SystemExit(f"ZIP not found: {zip_path}")

    plan = []
    with tempfile.TemporaryDirectory(prefix="hays-botany-backfill-") as tmp:
        tmp_path = Path(tmp)
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(tmp_path)
        taxa_root = find_taxa_root(tmp_path)

        for src_species, sp in iter_species_dirs(taxa_root):
            taxon_id = sp.get("id")
            family = sp.get("family")
            genus = sp.get("genus")
            if not taxon_id or not family or not genus:
                raise RuntimeError(f"Invalid species package: {src_species}")
            if taxon_id in SKIP_IDS:
                plan.append(("SKIP obsolete duplicate", taxon_id, family, genus))
                continue

            dst_species = CONTENT / family / genus / taxon_id
            mode = "full package" if family in FULL_IMPORT_FAMILIES else "photos only"
            plan.append((mode, taxon_id, family, genus))

            if not args.apply:
                continue

            if family in FULL_IMPORT_FAMILIES:
                copy_tree_files(src_species, dst_species)
                possible_genus_files = [
                    src_species.parent / "genus.json",
                    src_species.parent.parent / "genus.json",
                ]
                dst_genus = dst_species.parent / "genus.json"
                for src_genus in possible_genus_files:
                    if src_genus.exists():
                        shutil.copy2(src_genus, dst_genus)
                        break

                possible_family_files = [
                    src_species.parent.parent / "family.json",
                    src_species.parent.parent.parent / "family.json",
                ]
                dst_family = dst_species.parent.parent / "family.json"
                for src_family in possible_family_files:
                    if src_family.exists() and not dst_family.exists():
                        shutil.copy2(src_family, dst_family)
                        break
            else:
                backfill_photos_only(src_species, dst_species)

            patch_species_images(dst_species)

    full_count = sum(1 for mode, *_ in plan if mode == "full package")
    photo_count = sum(1 for mode, *_ in plan if mode == "photos only")
    skip_count = sum(1 for mode, *_ in plan if mode.startswith("SKIP"))

    print(f"ZIP: {zip_path}")
    print(f"Plan: {full_count} full Asteraceae packages, {photo_count} photo-only backfills, {skip_count} skipped obsolete duplicate(s).")
    for row in plan:
        print(" -", " | ".join(row))

    if not args.apply:
        print("\nDRY RUN ONLY. Re-run with --apply to perform the migration.")
        return

    species_count = rebuild_manifest()
    print(f"\nCanonical manifest rebuilt: {species_count} taxa.")

    if args.commit_push:
        git("add", "content/taxa", "data/manifest.json", "data/project.json")
        diff = git("diff", "--cached", "--quiet", check=False)
        if diff.returncode == 0:
            print("No Git changes detected; nothing to commit.")
            return
        commit = git("commit", "-m", "Backfill curated taxa and photos from historical ZIP")
        print(commit.stdout)
        push = git("push", "origin", "main")
        print(push.stdout)
        print("Backfill committed and pushed to GitHub main.")
    else:
        print("Files updated locally. Review them, then commit/push when ready.")

if __name__ == "__main__":
    main()
