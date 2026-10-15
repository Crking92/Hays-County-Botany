#!/usr/bin/env python3
"""Build permanent review-only photo archives and a discoverable metadata index.

No species.json, manifest, or installed learner image is ever edited.
Image bytes belong to private GitHub Release assets; CSV/JSON goes in git.
"""
import argparse
import collections
import csv
import datetime as dt
import hashlib
import json
import pathlib
import re
import shutil
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
LIB = ROOT / "workflow/photo-library"
BATCHES = LIB / "batches"
PHOTO_ID_FIELDS = ("canonical_id", "scientific_name", "source", "observation_id",
                   "photo_id", "image_url", "source_page", "creator", "license",
                   "license_basis", "photo_license_status", "organ", "location",
                   "identity_status", "candidate_status", "archive_tag",
                   "archive_file", "batch_id", "photo_key")
HEADERS = list(PHOTO_ID_FIELDS)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as fp:
        return list(csv.DictReader(fp))


def safe_csv(x):
    s = str(x or "")
    return "'" + s if s.startswith(("=", "+", "-", "@", "\t", "\r")) else s


def csv_write(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: safe_csv(row.get(key, "")) for key in fields})


def prepare(args):
    batch_id = args.batch_id
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{3,79}", batch_id):
        raise ValueError("Unsafe batch-id")
    source = pathlib.Path(args.input)
    candidates = source / "candidates.csv"
    summary = source / "summary.json"
    if not candidates.is_file() or not summary.is_file():
        raise FileNotFoundError("harvest CSV and summary must both exist")
    rows = read_csv(candidates)
    data = read_json(summary)
    dest = BATCHES / batch_id
    if dest.exists():
        raise FileExistsError("Refusing to overwrite durable photo batch: " + batch_id)
    dest.mkdir(parents=True)
    shutil.copy2(candidates, dest / "candidates.csv")
    shutil.copy2(summary, dest / "summary.json")
    selected = source / "selected-species.json"
    if selected.exists():
        shutil.copy2(selected, dest / "selected-species.json")
    else:
        # Older Actions artifacts did not include searched-but-empty species.
        unique = {r.get("canonical_id", ""): r.get("scientific_name", "") for r in rows}
        (dest / "selected-species.json").write_text(
            json.dumps({"species": [{"id": k, "scientific_name": v} for k, v in
                                    sorted(unique.items()) if k],
                        "historic_partial": True,
                        "note": "Zero-result searches were not recorded by the original harvester."},
                       indent=2) + "\n", encoding="utf-8")
    if data.get("canonical_species_modified", 0):
        raise ValueError("Harvest batch improperly marked canonical changes")
    # Store only verified-by-license-scheme provisional files; NOT identity-approved.
    staged_paths = {r.get("staged_file", "") for r in rows if r.get("staged_file")}
    file_hashes = {}
    for rel in sorted(staged_paths):
        target = (source / rel).resolve()
        if not target.is_relative_to(source.resolve()) or not target.is_file():
            raise FileNotFoundError("Referenced staged image is missing or unsafe")
        if target.suffix.lower() not in (".jpg", ".jpeg"):
            raise ValueError("Only normalized JPEGs supported")
        file_hashes[rel] = hashlib.sha256(target.read_bytes()).hexdigest()
    archive_dir = pathlib.Path(args.archive_dir)
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive_path = archive_dir / (batch_id + "-photos.zip")
    with zipfile.ZipFile(archive_path, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for name in ("candidates.csv", "summary.json", "selected-species.json"):
            z.write(dest / name, arcname=name)
        for rel in sorted(file_hashes):
            z.write(source / rel, arcname=rel)
        z.writestr("sha256-images.json", json.dumps(file_hashes, indent=2) + "\n")
    with zipfile.ZipFile(archive_path) as z:
        problem = z.testzip()
        if problem:
            raise ValueError("Corrupted release archive: " + problem)
    tag = "hays-photo-library-" + batch_id
    archive = {
        "format_version": 1,
        "batch_id": batch_id,
        "private_release_tag": tag,
        "asset_name": archive_path.name,
        "asset_sha256": hashlib.sha256(archive_path.read_bytes()).hexdigest(),
        "archive_size_bytes": archive_path.stat().st_size,
        "photo_file_count": len(file_hashes),
        "candidate_rows": len(rows),
        "source_harvested_at": data.get("generated_at"),
        "persistent_release": False,
        "note": "Set permanent true only once GitHub Release asset upload succeeds; unverified photos."
    }
    (dest / "archive.json").write_text(json.dumps(archive, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"batch_id": batch_id, "archive_path": str(archive_path),
                      "photo_files": len(file_hashes), "candidate_rows": len(rows),
                      "release_tag": tag}))


def mark_published(args):
    dest = BATCHES / args.batch_id / "archive.json"
    obj = read_json(dest)
    obj["persistent_release"] = True
    obj["published_at_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
    dest.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def rebuild(_args):
    # Batch-specific files are canonical evidence; index is an efficient derivative.
    rows_by_key = {}
    scans = collections.defaultdict(list)
    for batch in sorted(BATCHES.glob("*")):
        if not batch.is_dir():
            continue
        archived = batch / "archive.json"
        candidates = batch / "candidates.csv"
        selected = batch / "selected-species.json"
        if not archived.exists() or not candidates.exists():
            continue
        arc = read_json(archived)
        if not arc.get("persistent_release"):
            continue
        if selected.exists():
            for entry in read_json(selected).get("species", []):
                sid = entry if isinstance(entry, str) else entry.get("id", "")
                if sid and batch.name not in scans[sid]:
                    scans[sid].append(batch.name)
        for candidate in read_csv(candidates):
            sid = candidate.get("canonical_id", "")
            url = candidate.get("image_url", "")
            if not sid or not url:
                continue
            # Dedup across the general GBIF and Pl@ntNet-sourced GBIF inventories.
            key = hashlib.sha256((sid + "\n" + url).encode()).hexdigest()
            if key in rows_by_key:
                existing = rows_by_key[key]
                if not existing["archive_file"] and candidate.get("staged_file"):
                    existing["archive_tag"] = arc["private_release_tag"]
                    existing["archive_file"] = candidate["staged_file"]
                continue
            r = {name: candidate.get(name, "") for name in PHOTO_ID_FIELDS}
            r.update({"candidate_status":
                      "downloaded_provisional" if candidate.get("staged_file")
                      else "candidate_metadata",
                      "archive_tag": arc["private_release_tag"],
                      "archive_file": candidate.get("staged_file", ""),
                      "batch_id": batch.name, "photo_key": key[:20]})
            rows_by_key[key] = r
    rows = sorted(rows_by_key.values(), key=lambda r: (r["canonical_id"], r["source"], r["photo_key"]))
    csv_write(LIB / "catalog.csv", rows, HEADERS)
    groups = collections.defaultdict(lambda: {"candidates": 0, "stored_images": 0, "batches": []})
    for r in rows:
        g = groups[r["canonical_id"]]
        g["candidates"] += 1
        g["stored_images"] += bool(r["archive_file"])
        if r["batch_id"] not in g["batches"]:
            g["batches"].append(r["batch_id"])
    for sid, ids in scans.items():
        groups[sid]["scanned_batches"] = ids
    index = {"last_rebuilt_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
             "candidate_count": len(rows),
             "distinct_species_with_candidates": sum(bool(g["candidates"]) for g in groups.values()),
             "species_scanned": len(scans),
             "stored_images": sum(bool(r["archive_file"]) for r in rows),
             "species": dict(sorted(groups.items()))}
    (LIB / "species-index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: index[k] for k in ("candidate_count", "stored_images", "species_scanned")}))


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="action", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--input", required=True)
    p.add_argument("--batch-id", required=True)
    p.add_argument("--archive-dir", required=True)
    p = sub.add_parser("published")
    p.add_argument("--batch-id", required=True)
    sub.add_parser("rebuild")
    args = parser.parse_args()
    {"prepare": prepare, "published": mark_published, "rebuild": rebuild}[args.action](args)


if __name__ == "__main__":
    main()
