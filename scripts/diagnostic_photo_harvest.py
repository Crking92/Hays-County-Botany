#!/usr/bin/env python3
"""Collect NEW botanical diagnostic-view candidates for explicit canonical taxa.

This is a provisional photo-source harvester, not an anatomy classifier.
Wanted parts are prompts for later PIXEL-LEVEL visual curation, not claims
that any downloaded image actually depicts those parts.
"""
import argparse
import collections
import csv
import datetime as dt
import json
import pathlib
import time

import bulk_open_photo_harvest as base

ROOT = pathlib.Path(__file__).resolve().parent.parent
LIBRARY = ROOT / "workflow/photo-library"


def known_urls():
    paths = LIBRARY / "catalog.csv"
    found = collections.defaultdict(set)
    if paths.is_file():
        with paths.open(newline="", encoding="utf-8-sig") as handle:
            for x in csv.DictReader(handle):
                sid, url = x.get("canonical_id", ""), x.get("image_url", "")
                if sid and url:
                    found[sid].add(url)
    return found


def check_target(entry, lookup, claimed, holds):
    sid = entry.get("id")
    if not sid or sid not in lookup or sid in holds or sid in claimed:
        return None
    path = ROOT / lookup[sid]["path"]
    species = json.loads(path.read_text(encoding="utf-8"))
    name = species.get("scientific_name") or (
        str(species.get("genus") or "") + " " + str(species.get("species") or "")
    ).strip()
    if not name or len(name.split()) < 2 or species.get("id") != sid:
        return None
    return {"id": sid, "name": name,
            "files": len(species.get("images") or []),
            "gallery": len(species.get("images") or []),
            "wanted_parts": entry.get("wanted_parts", []),
            "source_record": lookup[sid]["path"]}


def search_new(item, source, per_source, old):
    """Use multiple GBIF pages; prioritize different source observations and URLs."""
    chosen, used, obs_counts = [], set(old), collections.Counter()
    scanned_pages = 0
    datasets = source == "Pl@ntNet via GBIF"
    for location in ("texas", "global"):
        if len(chosen) >= per_source:
            break
        for offset in (0, 80, 160):
            if len(chosen) >= per_source:
                break
            params = {"scientificName": item["name"], "mediaType": "StillImage",
                      "limit": 80, "offset": offset}
            if datasets:
                params["datasetKey"] = base.PLANTNET_GBIF_DATASET
            if location == "texas":
                params.update({"country": "US", "stateProvince": "Texas"})
            occurrences = base.get_json(
                "https://api.gbif.org/v1/occurrence/search", params
            ).get("results", [])
            scanned_pages += 1
            if not occurrences:
                break
            for occ in occurrences:
                if len(chosen) >= per_source:
                    break
                if not base.same_name(item["name"], occ.get("scientificName") or ""):
                    continue
                oid = str(occ.get("key") or "")
                if not oid or obs_counts[oid] >= 2:
                    continue
                for media in occ.get("media") or []:
                    if len(chosen) >= per_source or obs_counts[oid] >= 2:
                        break
                    if media.get("type") and str(media["type"]).lower() not in ("stillimage", "image"):
                        continue
                    url = base.valid_url(media.get("identifier"))
                    if not url or url in used:
                        continue
                    creator = (media.get("creator") or media.get("rightsHolder") or
                               occ.get("rightsHolder") or occ.get("recordedBy"))
                    if isinstance(creator, list):
                        creator = "; ".join(str(x) for x in creator)
                    rights = media.get("license") or media.get("rights")
                    if not creator or not rights:
                        continue   # Occurrence or dataset CC license is NOT photo permission.
                    r = base.row(item, source, oid,
                                 "https://www.gbif.org/occurrence/" + oid,
                                 url, media.get("identifier"), "", creator, rights, "media",
                                 str(occ.get("stateProvince") or "") + ", " +
                                 str(occ.get("country") or ""))
                    if r["photo_license_status"] != "supported":
                        continue
                    # Exact-name metadata is not a human verification of what is pictured.
                    r["identity_status"] = "exact_name_metadata_only_review_image"
                    used.add(url)
                    obs_counts[oid] += 1
                    chosen.append(r)
            time.sleep(0.2)
    return chosen, scanned_pages


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    request = json.loads((ROOT / args.request).read_text(encoding="utf-8"))
    per = max(1, min(6, int(request.get("per_source", 4))))
    manifest = {x["id"]: x for x in base.load("data/manifest.json")["species"]}
    hold = {"muhlenbergia-piniflora"}
    hold.update(x["id"] for x in base.load("reports/photo-coverage-latest.json").get("zero_gallery_items", [])
                if "HOLD" in str(x.get("status", "")).upper())
    busy = base.busy_ids()
    old = known_urls()
    selected, skipped = [], []
    for entry in request.get("targets", []):
        item = check_target(entry, manifest, busy, hold)
        if item:
            selected.append(item)
        else:
            skipped.append({"id": entry.get("id"), "reason": "not canonical, held or claimed"})
    out = pathlib.Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    out.mkdir(parents=True, exist_ok=True)
    rows, errors = [], []
    for n, item in enumerate(selected, 1):
        found, pages = [], 0
        for source in ("GBIF", "Pl@ntNet via GBIF"):
            try:
                candidates, page_count = search_new(
                    item, source, per, old[item["id"]] |
                    {x["image_url"] for x in found}
                )
                found.extend(candidates)
                pages += page_count
            except Exception as exc:
                errors.append({"species": item["id"], "source": source,
                               "stage": "search", "type": type(exc).__name__})
        for candidate in found:
            try:
                candidate["staged_file"] = base.stage(candidate, out)
            except Exception as exc:
                errors.append({"species": item["id"], "source": candidate["source"],
                               "stage": "download", "type": type(exc).__name__})
            rows.append(candidate)
        print(f"{n}/{len(selected)} {item['name']}: {len(found)} new candidates; "
              f"{pages} search pages", flush=True)
    with (out / "candidates.csv").open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=base.COLUMNS)
        writer.writeheader()
        writer.writerows({col: base.csv_safe(x.get(col, "")) for col in base.COLUMNS} for x in rows)
    (out / "selected-species.json").write_text(json.dumps({
        "mode": "diagnostic_candidate_research_not_verified_anatomy",
        "source_request": args.request, "selected_species_count": len(selected),
        "species": [{"id": x["id"], "scientific_name": x["name"],
                     "wanted_parts": x["wanted_parts"],
                     "source_record": x["source_record"]} for x in selected],
        "skipped": skipped
    }, indent=2) + "\n", encoding="utf-8")
    summary = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source": "targeted GBIF + Pl@ntNet public GBIF observation images",
        "candidate_count": len(rows),
        "staged_image_count": sum(bool(x.get("staged_file")) for x in rows),
        "selected_taxa": len(selected),
        "new_source_observations": len(set((x["source"], x["observation_id"]) for x in rows)),
        "skipped_taxa": skipped,
        "canonical_species_modified": 0,
        "identity_verified": False,
        "organ_verified": False,
        "notes": "Wanted anatomical roles are REVIEW TARGETS ONLY; pixel-level ID and structure review required before install.",
        "errors": errors
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
