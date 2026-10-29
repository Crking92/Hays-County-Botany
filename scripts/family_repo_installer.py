#!/usr/bin/env python3
"""Plan/apply existing curated plant-card packages to *assigned family worktrees*.

This is NOT a photo downloader, publisher, or GitHub committer. It deliberately
fails closed instead of falling back to the legacy Hays-County-Botany tree.

Usage:
  python scripts/family_repo_installer.py my-cards.zip
  python scripts/family_repo_installer.py my-cards.zip --destination-root ..
  python scripts/family_repo_installer.py my-cards.zip --destination-root .. --apply

The destination root contains locally cloned Hays-Botany-* repositories, each
checked out at its exact active registry branch. Never auto-push or force merge.
No new photo sourcing, and no images copied from old ZIPs by this installer.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from resolve_new_plant_write import load_and_validate

SOURCE_REPO = "Hays-County-Botany"
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
GENUS = re.compile(r"^[A-Z][A-Za-z-]+$")
ALLOWED = {"species.json", "SOURCES.txt", "image-sources.csv"}
PHOTO_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".gif", ".heic"}


def fail(message: str):
    raise RuntimeError("FAMILY_ROUTING_BLOCKED: " + message)


def check_package_folder(root: Path):
    if (root / "taxa").is_dir():
        return root / "taxa"
    if (root / "content" / "taxa").is_dir():
        return root / "content" / "taxa"
    fail("package must have taxa/Family/Genus/species-id/ or content/taxa/... layout")


def safe_extract(archive: Path, dest: Path):
    with zipfile.ZipFile(archive) as zf:
        infos = zf.infolist()
        if len(infos) > 15000:
            fail("package exceeds safe 15,000-entry limit")
        for info in infos:
            name = info.filename.replace("\\", "/")
            p = Path(name)
            if (p.is_absolute() or ".." in p.parts or
                ":" in name or not name or name.startswith("/")):
                fail("unsafe archive path: " + name)
            if (info.external_attr >> 16) & 0o170000 == 0o120000:
                fail("symlink is not allowed: " + name)
        zf.extractall(dest)


def run_git(cwd: Path, *args: str):
    p = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if p.returncode != 0:
        fail(f"{cwd.name}: git {' '.join(args)}: {p.stderr.strip()[:300]}")
    return p.stdout.strip()


def ensure_worktree(root: Path, repo: str, branch: str):
    if repo == SOURCE_REPO or not repo.startswith("Hays-Botany-"):
        fail("invalid destination repository: " + repo)
    wd = (root / repo).resolve()
    if not (wd / ".git").exists():
        fail(f"{repo} must be cloned under --destination-root (no auto-cloning)")
    actual = run_git(wd, "branch", "--show-current")
    if actual != branch:
        fail(f"{repo} must be on {branch!r}; current branch {actual!r}")
    remote = run_git(wd, "remote", "get-url", "origin").rstrip("/")
    valid = (f"github.com/Crking92/{repo}", f"github.com:Crking92/{repo}")
    if not any(v in remote for v in valid):
        fail(f"{repo}: origin is not the approved GitHub collection: {remote}")
    if run_git(wd, "status", "--porcelain"):
        fail(f"{repo}: working tree is not clean; preserve parallel chat changes")
    return wd


def gather(taxa: Path, registry: dict):
    planned = []
    seen_ids = set()
    allowed_families = registry["family_to_repository"]
    for card in sorted(taxa.glob("*/*/*/species.json")):
        if card.is_symlink():
            fail("symlink species card: " + str(card))
        family, genus, sid = card.parts[-4:-1]
        if family not in allowed_families:
            fail("unknown family " + family + "; NO legacy hub fallback")
        if not GENUS.fullmatch(genus) or not SLUG.fullmatch(sid):
            fail("invalid genus or species slug: " + str(card))
        if sid in seen_ids:
            fail("duplicate ID in package: " + sid)
        seen_ids.add(sid)
        sp = json.loads(card.read_text(encoding="utf-8-sig"))
        if any(sp.get(k) != v for k, v in (("id", sid), ("family", family), ("genus", genus))):
            fail("species identity does not match its package path: " + sid)
        if not sp.get("scientific_name") and not sp.get("species"):
            fail("scientific name/epithet missing: " + sid)
        if not (card.parent / "SOURCES.txt").is_file():
            fail("source attribution missing: " + sid)
        # No automatic transfer of image binaries, nor species cards with unresolved
        # image file references. Such records require their own exact-media rights pass.
        for file in card.parent.rglob("*"):
            if file.is_symlink():
                fail("symlink in species package: " + str(file))
            if file.is_file() and (file.suffix.lower() in PHOTO_SUFFIXES or file.name not in ALLOWED):
                fail("image or unsupported sidecar needs individual family photo review: " + str(file))
        if any(isinstance(i, dict) and i.get("file") for i in (sp.get("images") or [])):
            fail(sid + ": source images[] has file references; route media by photo-specific review")
        repo = allowed_families[family]
        branch = registry["repository_write_branches"][repo]
        files = [(p, p.relative_to(taxa)) for p in sorted(card.parent.iterdir()) if p.is_file()]
        planned.append((repo, branch, family, genus, sid, sp, files))
    lessons = []
    lesson_paths = sorted(taxa.glob("*/family.json")) + sorted(taxa.glob("*/*/genus.json"))
    for lesson in lesson_paths:
        if lesson.is_symlink():
            fail("symlink lesson: " + str(lesson))
        parts = lesson.relative_to(taxa).parts
        family = parts[0]
        if family not in allowed_families:
            fail("unknown lesson family " + family + "; NO legacy hub fallback")
        if len(parts) == 3 and not GENUS.fullmatch(parts[1]):
            fail("invalid lesson genus: " + str(lesson))
        data = json.loads(lesson.read_text(encoding="utf-8-sig"))
        if not isinstance(data, dict):
            fail("lesson must be a JSON object: " + str(lesson))
        repo = allowed_families[family]
        lessons.append((repo, registry["repository_write_branches"][repo], lesson, lesson.relative_to(taxa)))
    if not planned and not lessons:
        fail("no correctly nested species cards or genus/family lesson files found")
    return planned, lessons


def main():
    p = argparse.ArgumentParser()
    p.add_argument("package", help="ZIP or directory with taxa/Family/Genus/species-id/")
    p.add_argument("--destination-root", type=Path, help="parent directory of cloned family repos")
    p.add_argument("--apply", action="store_true", help="write safely into family clones, never old hub")
    args = p.parse_args()
    if args.apply and not args.destination_root:
        p.error("--apply requires --destination-root and correct checked-out family branches")
    reg = load_and_validate()
    package = Path(args.package).expanduser().resolve()
    if not package.exists():
        fail("package is not available: " + str(package))
    with tempfile.TemporaryDirectory(prefix="hays-family-route-") as tmp:
        if package.is_file() and zipfile.is_zipfile(package):
            safe_extract(package, Path(tmp))
            root = Path(tmp)
        elif package.is_dir():
            root = package
        else:
            fail("expected a valid ZIP or extracted directory")
        plan, lessons = gather(check_package_folder(root), reg)
        destinations = {}
        if args.apply:
            dr = args.destination_root.expanduser().resolve()
            if dr.name == SOURCE_REPO:
                fail("the legacy original repository cannot be a destination root")
            for repo, branch in (
                [(item[0], item[1]) for item in plan] +
                [(item[0], item[1]) for item in lessons]
            ):
                if repo not in destinations:
                    destinations[repo] = ensure_worktree(dr, repo, branch)
        # Complete preflight: refuse non-identical existing cards, including the
        # derived collection indexes, rather than overwriting another chat's work.
        writes = []
        dirty_indexes = set()
        for repo, branch, fam, gen, sid, sp, files in plan:
            if args.apply:
                wd = destinations[repo]
                for src, rel in files:
                    target = wd / "content" / "taxa" / rel
                    if target.exists():
                        if target.read_bytes() != src.read_bytes():
                            fail(f"{repo}: {target} differs from staged payload; review/merge manually")
                    else:
                        writes.append((src, target))
                index = wd / "data" / "collection-index.json"
                if repo in destinations.setdefault("indexes", {}):
                    catalog = destinations["indexes"][repo][1]
                else:
                    if not index.exists() and repo == "Hays-Botany-Poaceae":
                        # Poaceae was transferred before grouped collections
                        # standardized data/collection-index.json. Derive its
                        # first local, NOT LIVE index from its actual cards.
                        existing = []
                        for oldcard in sorted((wd / "content" / "taxa" / "Poaceae").glob("*/*/species.json")):
                            card_data = json.loads(oldcard.read_text(encoding="utf-8"))
                            fam2, gen2, sid2 = oldcard.parts[-4:-1]
                            if fam2 != "Poaceae" or any(card_data.get(k) != v for k, v in
                                (("id", sid2), ("family", fam2), ("genus", gen2))):
                                fail("Poaceae source card identity mismatch: " + str(oldcard))
                            existing.append({
                                "id": sid2,
                                "scientific_name": card_data.get("scientific_name") or
                                    " ".join(x for x in (gen2, card_data.get("species")) if x),
                                "common_name": card_data.get("common_name", ""),
                                "family": fam2, "genus": gen2,
                                "path": "content/taxa/" + "/".join((fam2, gen2, sid2, "species.json")),
                                "photo_publication_status": "PUBLIC_RIGHTS_NOT_ASSESSED_BY_INDEX"
                            })
                        catalog = {
                            "schema_version": 1, "collection_id": "poaceae",
                            "authority": "STAGING_ONLY",
                            "entries": existing,
                            "note": "Index for future family edits only; no photo clearance or Pages release",
                        }
                    elif index.exists():
                        catalog = json.loads(index.read_text(encoding="utf-8"))
                    else:
                        fail(repo + ": collection index missing; refuse silent legacy manifest fallback")
                    destinations["indexes"][repo] = (index, catalog)
                entries = catalog.get("entries")
                if not isinstance(entries, list) or catalog.get("authority") != "STAGING_ONLY":
                    fail(repo + ": unexpected collection index authority/schema")
                if any(row.get("id") == sid for row in entries):
                    # Existing card update must be reviewed by an editor, not blindly replaced.
                    pass
                else:
                    entries.append({
                        "id": sid, "scientific_name": sp.get("scientific_name") or
                        " ".join(x for x in (gen, sp.get("species")) if x),
                        "common_name": sp.get("common_name", ""),
                        "family": fam, "genus": gen,
                        "path": f"content/taxa/{fam}/{gen}/{sid}/species.json",
                        "photo_publication_status": "PRIVATE_ONLY_HOLD"
                    })
                    dirty_indexes.add(repo)
                    # All rows for this repository share one cached catalog.
                    # Never reserialize existing indexes unless new IDs were added.
        if args.apply:
            for repo, branch, source, rel in lessons:
                target = destinations[repo] / "content" / "taxa" / rel
                if target.exists():
                    if target.read_bytes() != source.read_bytes():
                        fail(f"{repo}: existing genus/family lesson differs; merge manually: {target}")
                else:
                    writes.append((source, target))
        report = {
            "mode": "APPLY" if args.apply else "PLAN_ONLY",
            "legacy_hub_botanical_writes": False,
            "public_pages_deployed": False,
            "photo_downloads": 0,
            "items": [{"id": sid, "family": fam, "repository": "Crking92/" + repo,
                       "branch": branch} for repo, branch, fam, gen, sid, *_ in plan],
            "lessons": [{"file": str(rel), "repository": "Crking92/" + repo,
                         "branch": branch} for repo, branch, _src, rel in lessons],
        }
        if args.apply:
            for source, target in writes:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
            for repo, (index, catalog) in destinations.get("indexes", {}).items():
                if repo in dirty_indexes:
                    index.parent.mkdir(parents=True, exist_ok=True)
                    index.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            report["files_added"] = len(writes)
            report["note"] = "Changes are local and uncommitted; review and validate each family branch before manually committing."
        print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError, OSError, zipfile.BadZipFile) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(2)
