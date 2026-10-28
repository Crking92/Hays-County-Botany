#!/usr/bin/env python3
"""Audit planning-only family routing versus current canonical hub species manifest.

NEVER migrates records, modifies project rules, publishes Pages, or changes owner.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "planning/MULTI_REPO_FAMILY_ROUTING_DRAFT_20261028.json"


def check(condition, message):
    if not condition:
        raise SystemExit("FAMILY_ROUTING_AUDIT_FAILED: " + message)


def main():
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "data/manifest.json").read_text(encoding="utf-8"))
    check(registry["status"] == "PLANNING_DRAFT_NOT_ACTIVE", "draft routing unexpectedly active")
    collections = registry["collections"]
    lookup = registry["family_to_planned_repository"]
    check(len(collections) == 10, "planned collection count is not ten")
    check(len(lookup) == 146, "baseline family route count changed")
    flat = []
    for coll in collections:
        check(coll["repository"].startswith("Hays-Botany-"), "unexpected collection repository")
        check(coll["family_count"] == len(coll["families"]), "family count mismatch in " + coll["repository"])
        for fam in coll["families"]:
            check(lookup.get(fam) == coll["repository"], "reverse routing mismatch: " + fam)
            flat.append(fam)
    check(len(flat) == len(set(flat)) == len(lookup), "duplicate or missing family mapping")
    species = manifest["species"]
    seen_ids = set()
    current = Counter()
    missing = []
    for row in species:
        sid = row["id"]
        path = row["path"]
        parts = path.split("/")
        check(len(parts) == 6 and parts[0:2] == ["content", "taxa"] and parts[-1] == "species.json",
              "malformed canonical path for " + sid)
        check(sid not in seen_ids, "duplicate species ID: " + sid)
        seen_ids.add(sid)
        fam = parts[2]
        current[fam] += 1
        if fam not in lookup:
            missing.append(fam)
    check(not missing, "NEW FAMILIES REQUIRE ROUTING APPROVAL: " + ", ".join(sorted(set(missing))))
    check(registry["total_installed_species_baseline"] == 1191, "baseline record changed unexpectedly")
    print(json.dumps({
        "audit": "PASS_DRAFT_ROUTING",
        "current_installed_species": len(species),
        "current_represented_families": len(current),
        "baseline_installed_species": registry["total_installed_species_baseline"],
        "planned_collections": len(collections),
        "planned_families": len(lookup),
        "new_family_unassigned": 0,
        "production_owner_unchanged": "Crking92/Hays-County-Botany",
        "counts_by_planned_repository": {
            coll["repository"]: sum(current[f] for f in coll["families"]) for coll in collections
        },
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
