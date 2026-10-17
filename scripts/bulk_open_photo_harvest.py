#!/usr/bin/env python3
"""Manual, review-only licensed photo discovery for sparse Hays Botany cards.

Uses GBIF public occurrences and optional Pl@ntNet Darwin Core API.
Produces CSV, summary, and optionally staged JPEGs. NEVER edits canonical cards.
"""
import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import os
import pathlib
import re
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
COLUMNS = ("canonical_id scientific_name local_files gallery_records source observation_id "
           "source_page image_url photo_id organ creator license license_basis location "
           "identity_status photo_license_status staged_file").split()
UA = {"User-Agent": "HaysBotanyOpenPhoto/1.0 educational-review", "Accept": "application/json"}


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def license_status(value):
    s = str(value or "").lower().replace("_", "-").strip()
    if "by-nc" in s or "by-nd" in s or "all rights" in s:
        return s, "restricted"
    if "publicdomain/zero" in s or re.search(r"\bcc-?0\b", s):
        return "CC0", "supported"
    if ("creativecommons.org/licenses/by-sa/" in s or
            re.search(r"\bcc[ -]?by[ -]?sa(?:\b|\d)", s)):
        return "CC BY-SA", "supported"
    if ("creativecommons.org/licenses/by/" in s or
            re.search(r"\bcc[ -]?by(?:\b|[ -]?\d)", s)):
        return "CC BY", "supported"
    return s, "unknown"


def same_name(expected, observed):
    """Match scientific binomial/infra-rank exactly, allowing authority suffix."""
    a = [w.lower().rstrip(".") for w in str(expected).split()]
    b = [w.lower().rstrip(".") for w in str(observed).split()]
    if len(a) < 2 or len(b) < 2 or a[:2] != b[:2]:
        return False
    ranks = {"var", "subsp", "ssp", "f", "forma"}
    if len(a) >= 4 and a[2] in ranks:
        return (len(b) >= 4 and b[2] in ranks and b[3] == a[3]
                and (a[2] == b[2] or {a[2], b[2]} == {"subsp", "ssp"}))
    return len(a) == 2 and not (len(b) >= 4 and b[2] in ranks)


def busy_ids():
    claimed = set()
    now = dt.datetime.now(dt.timezone.utc)
    for c in load("workflow/work-claims.json").get("claims", []):
        if c.get("status") not in ("active", "queued", "blocked"):
            continue
        if c.get("status") == "active" and c.get("expires_at"):
            try:
                if dt.datetime.fromisoformat(c["expires_at"].replace("Z", "+00:00")) < now:
                    continue
            except ValueError:
                pass
        claimed.update(c.get("taxa") or [])
    return claimed


def select_taxa(limit, max_local, requested, exclude=None, allow_requested_any_gallery=False):
    coverage = load("reports/photo-coverage-latest.json")
    canonical = {s["id"] for s in load("data/manifest.json")["species"]}
    busy = busy_ids()
    exclude = exclude or set()
    # The numeric unresolved_taxon_source_concept_holds report field is a COUNT.
    # Actual held taxon IDs are listed in zero_gallery_items.
    holds = {
        entry.get("id", "")
        for entry in coverage.get("zero_gallery_items", [])
        if isinstance(entry, dict) and (
            "HOLD" in str(entry.get("status", "")).upper()
            or "HOLD" in str(entry.get("reason", "")).upper()
        )
    }
    # Explicit source-concept guardrail must survive report reshaping.
    holds.add("muhlenbergia-piniflora")
    out = []
    if allow_requested_any_gallery:
        # Explicit diagnostic-review requests may include species with 3+ installed
        # photos. They remain candidates; never edit those canonical galleries.
        by_id = {s["id"]: s for s in load("data/manifest.json")["species"]}
        for sid in sorted(requested):
            if sid not in by_id or sid in busy or sid in holds or sid in exclude:
                continue
            entry = by_id[sid]
            species_path = ROOT / entry["path"]
            taxon = json.loads(species_path.read_text(encoding="utf-8"))
            images = taxon.get("images") or []
            files = sum(bool(im.get("file")) and not str(im.get("file")).startswith(("https://", "http://"))
                        and (species_path.parent / str(im["file"])).is_file()
                        for im in images if isinstance(im, dict))
            name = taxon.get("scientific_name") or ""
            if name:
                out.append({"id": sid, "name": name, "files": files, "gallery": len(images)})
        out.sort(key=lambda x: (x["files"], x["gallery"], x["id"]))
        return out[:limit], len(out), coverage.get("generated_at_utc")
    for item in coverage["zero_one_two_photo_species"]:
        sid = item["id"]
        files = int(item.get("installed_local_files", 0))
        if (sid not in canonical or sid in busy or sid in holds or sid in exclude or files > max_local
                or (requested and sid not in requested)):
            continue
        name = item.get("scientific_name") or ""
        if not name:
            continue
        out.append({"id": sid, "name": name, "files": files,
                    "gallery": int(item.get("gallery_records", 0))})
    out.sort(key=lambda x: (x["files"], x["gallery"], x["id"]))
    return out[:limit], len(out), coverage.get("generated_at_utc")


def library_scanned_ids():
    scanned = set()
    batches = ROOT / "workflow/photo-library/batches"
    for record in batches.glob("*/selected-species.json"):
        try:
            payload = json.loads(record.read_text(encoding="utf-8"))
            for entry in payload.get("species", []):
                if isinstance(entry, str):
                    scanned.add(entry)
                elif isinstance(entry, dict) and entry.get("id"):
                    scanned.add(entry["id"])
        except (ValueError, OSError):
            continue
    return scanned


def get_json(endpoint, params):
    url = endpoint + "?" + urllib.parse.urlencode(params)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as err:
            if err.code not in (429, 500, 502, 503, 504) or attempt == 2:
                raise
        except (urllib.error.URLError, TimeoutError):
            if attempt == 2:
                raise
        time.sleep(2 * (attempt + 1))


def valid_url(value):
    p = urllib.parse.urlparse(str(value or ""))
    return str(value) if p.scheme == "https" and p.hostname and "." in p.hostname and not p.username else ""


def row(item, source, oid, page, url, photo_id, organ, creator, rights, basis, location):
    lic, status = license_status(rights)
    return {"canonical_id": item["id"], "scientific_name": item["name"],
            "local_files": item["files"], "gallery_records": item["gallery"],
            "source": source, "observation_id": oid, "source_page": page,
            "image_url": url, "photo_id": photo_id, "organ": organ, "creator": str(creator),
            "license": lic, "license_basis": basis, "location": location,
            "identity_status": "exact_name_metadata_only_review_image",
            "photo_license_status": status, "staged_file": ""}


PLANTNET_GBIF_DATASET = "7a3679ef-5582-4aaa-81f0-8c2545cafc81"

def gbif(item, count, plantnet_dataset=False):
    matches = []
    used = set()
    for texas in (True, False):
        if len(matches) >= count:
            break
        params = {"scientificName": item["name"], "mediaType": "StillImage", "limit": 80}
        if plantnet_dataset:
            params["datasetKey"] = PLANTNET_GBIF_DATASET
        if texas:
            params.update({"country": "US", "stateProvince": "Texas"})
        for occ in get_json("https://api.gbif.org/v1/occurrence/search", params).get("results", []):
            if not same_name(item["name"], occ.get("scientificName") or ""):
                continue
            oid = str(occ.get("key") or "")
            from_this_observation = 0
            for media in occ.get("media") or []:
                if len(matches) >= count or from_this_observation >= 2:
                    break
                if media.get("type") and str(media["type"]).lower() not in ("stillimage", "image"):
                    continue
                url = valid_url(media.get("identifier"))
                if not url or url in used:
                    continue
                used.add(url)
                creator = (media.get("creator") or media.get("rightsHolder") or
                           occ.get("rightsHolder") or occ.get("recordedBy"))
                if isinstance(creator, list):
                    creator = "; ".join(map(str, creator))
                if not creator:
                    continue
                individual = media.get("license") or media.get("rights")
                # Pl@ntNet's occurrence dataset is CC BY, but photos have separate
                # rights (usually CC BY-SA). Never inherit a dataset license as a photo license.
                rights = individual or ("" if plantnet_dataset else occ.get("license"))
                source = "Pl@ntNet via GBIF" if plantnet_dataset else "GBIF"
                r = row(item, source, oid, "https://www.gbif.org/occurrence/" + oid,
                        url, media.get("identifier"), "", creator, rights,
                        "media" if individual else "occurrence_only_review_media_license",
                        (occ.get("stateProvince") or "") + ", " + (occ.get("country") or ""))
                if r["photo_license_status"] != "restricted":
                    matches.append(r)
                    from_this_observation += 1
        time.sleep(.15)
    return matches


def plantnet(item, count, key):
    # Use the minimal documented query; name/verification filters can differ by plan.
    params = {"api-key": key, "scientificName": item["name"], "limit": 60}
    matches, used = [], set()
    # Never print exception text: URL may include API key.
    data = get_json("https://my-api.plantnet.org/v2/dwc/occurrence/search", params)
    for occ in data.get("results") or []:
        if not same_name(item["name"], occ.get("scientificName") or ""):
            continue
        creator = occ.get("rightsHolder")
        if not creator:
            continue
        for media in occ.get("media") or []:
            if len(matches) >= count:
                return matches
            url = valid_url(media.get("large_url") or media.get("medium_url"))
            if not url or url in used:
                continue
            used.add(url)
            lic = media.get("license") or occ.get("license")
            r = row(item, "Pl@ntNet", str(occ.get("id") or ""),
                    (occ.get("taxon") or {}).get("url") or "https://plantnet.org/",
                    url, media.get("identifier") or "", media.get("organ") or "",
                    creator, lic, "media" if media.get("license") else "plantnet_observation",
                    str(occ.get("country") or ""))
            if r["photo_license_status"] == "supported":
                matches.append(r)
    return matches


def stage(r, out):
    # GBIF dataset/occurrence rights alone are NOT rights to the media.
    if r["photo_license_status"] != "supported" or r["license_basis"].startswith("occurrence_only"):
        return ""
    url = valid_url(r["image_url"])
    if not url:
        return ""
    req = urllib.request.Request(url, headers={"User-Agent": UA["User-Agent"], "Accept": "image/*"})
    with urllib.request.urlopen(req, timeout=30) as response:
        kind = (response.headers.get("Content-Type") or "").split(";")[0].lower()
        if kind not in ("image/jpeg", "image/png", "image/webp", "application/octet-stream"):
            raise ValueError("Not an image response")
        data = response.read(14_000_001)
    if not 5000 <= len(data) <= 14_000_000:
        raise ValueError("Invalid image size")
    from PIL import Image, ImageOps
    with Image.open(io.BytesIO(data)) as image:
        image.load()
        rgb = ImageOps.exif_transpose(image).convert("RGB")
    if max(rgb.size) < 500:
        raise ValueError("Image resolution too small")
    rgb.thumbnail((1400, 1400), Image.Resampling.LANCZOS)
    directory = out / "staged_images" / r["canonical_id"]
    directory.mkdir(parents=True, exist_ok=True)
    source_slug = re.sub(r"[^a-z0-9]+", "-", r["source"].lower().replace("@", "a")).strip("-")
    filename = source_slug + "-" + hashlib.sha256(url.encode()).hexdigest()[:14] + ".jpg"
    dest = directory / filename
    rgb.save(dest, format="JPEG", quality=88, optimize=True)
    return str(dest.relative_to(out))


def csv_safe(value):
    s = str(value if value is not None else "")
    return "'" + s if s.startswith(("=", "+", "-", "@", "\t", "\r")) else s


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", choices=("gbif", "plantnet-gbif", "plantnet", "both", "public"), default="gbif")
    ap.add_argument("--limit", type=int, default=30)
    ap.add_argument("--per-species", type=int, default=3)
    ap.add_argument("--max-local", type=int, choices=(0, 1, 2), default=2)
    ap.add_argument("--species", default="", help="comma-separated canonical species IDs")
    ap.add_argument("--out", default="workflow/open-photo-candidates/manual-latest")
    ap.add_argument("--download", action="store_true")
    ap.add_argument("--skip-library-scanned", action="store_true", help="Avoid species already scanned in permanent photo-library batches")
    ap.add_argument("--allow-requested-any-gallery", action="store_true", help="Diagnostic candidate review: explicit canonical IDs even with 3+ installed photos")
    args = ap.parse_args()
    if not (1 <= args.limit <= 60 and 1 <= args.per_species <= 8):
        ap.error("limit must be 1-60; per-species must be 1-8")
    key = os.environ.get("PLANTNET_API_KEY")
    if args.source == "plantnet" and not key:
        ap.error("PLANTNET_API_KEY required for the Pl@ntNet source")
    desired = {s.strip() for s in args.species.split(",") if s.strip()}
    if args.allow_requested_any_gallery and not desired:
        ap.error("--allow-requested-any-gallery requires explicit --species IDs")
    items, eligible, snapshot = select_taxa(args.limit, args.max_local, desired,
                                           library_scanned_ids() if args.skip_library_scanned else set(),
                                           args.allow_requested_any_gallery)
    out = pathlib.Path(args.out)
    out = out if out.is_absolute() else ROOT / out
    out.mkdir(parents=True, exist_ok=True)
    rows, errors = [], []
    plantnet_access = "not_requested"
    plantnet_available = False
    if args.source in ("both", "plantnet"):
        if not key:
            plantnet_access = "missing_secret"
            errors.append({"source": "Pl@ntNet", "stage": "access_preflight",
                           "error_type": "MissingApiKey"})
        else:
            # A single low-cost request proves whether this key can access
            # Darwin Core observation search; a general API key may not.
            try:
                get_json("https://my-api.plantnet.org/v2/dwc/occurrence/search",
                         {"api-key": key, "scientificName": "Asclepias curassavica",
                          "limit": 1})
                plantnet_available = True
                plantnet_access = "available"
            except urllib.error.HTTPError as exc:
                plantnet_access = "unavailable_http_" + str(exc.code)
                errors.append({"source": "Pl@ntNet", "stage": "access_preflight",
                               "error_type": "HTTPError", "http_status": exc.code})
            except Exception as exc:
                plantnet_access = "unavailable_" + type(exc).__name__
                errors.append({"source": "Pl@ntNet", "stage": "access_preflight",
                               "error_type": type(exc).__name__})
    for n, item in enumerate(items, 1):
        found = []
        for source in (("GBIF", "Pl@ntNet via GBIF", "Pl@ntNet") if args.source == "both" else
                       ("GBIF", "Pl@ntNet via GBIF") if args.source == "public" else
                       ("GBIF",) if args.source == "gbif" else
                       ("Pl@ntNet via GBIF",) if args.source == "plantnet-gbif" else
                       ("Pl@ntNet",)):
            if source == "Pl@ntNet" and not plantnet_available:
                continue
            try:
                if source == "GBIF":
                    found.extend(gbif(item, args.per_species))
                elif source == "Pl@ntNet via GBIF":
                    found.extend(gbif(item, args.per_species, plantnet_dataset=True))
                else:
                    found.extend(plantnet(item, args.per_species, key))
            except Exception as exc:
                errors.append({"species": item["id"], "source": source,
                               "stage": "search", "error_type": type(exc).__name__})
        for r in found:
            if args.download:
                try:
                    r["staged_file"] = stage(r, out)
                except Exception as exc:
                    errors.append({"species": item["id"], "source": r["source"],
                                   "stage": "download", "error_type": type(exc).__name__})
            rows.append(r)
        print(f"{n}/{len(items)} {item['name']}: {len(found)} candidates", flush=True)
    with (out / "candidates.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows({col: csv_safe(r.get(col, "")) for col in COLUMNS} for r in rows)
    (out / "selected-species.json").write_text(json.dumps({
        "coverage_snapshot": snapshot,
        "species": [{"id": x["id"], "scientific_name": x["name"],
                     "local_files_at_scan": x["files"], "gallery_records_at_scan": x["gallery"]}
                    for x in items]
    }, indent=2) + "\n", encoding="utf-8")
    summary = {"generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
               "coverage_snapshot": snapshot, "source": args.source,
               "plantnet_access": plantnet_access,
               "candidate_counts_by_source": {
                   k: sum(r["source"] == k for r in rows)
                   for k in ("GBIF", "Pl@ntNet via GBIF", "Pl@ntNet")
               },
               "eligible_unclaimed_taxa": eligible, "selected_taxa": len(items),
               "candidate_count": len(rows),
               "staged_image_count": sum(bool(r["staged_file"]) for r in rows),
               "canonical_species_modified": 0, "identity_verified": False,
               "notes": "Review exact pictured species, image-level rights, photographer, and visual role before installing.",
               "errors": errors}
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
