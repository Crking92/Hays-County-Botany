# Species Queue Reconciliation — 2026-10-03

## Scope
Species research queue only. This pass intentionally does **not** edit family-backfill files, website/page files, canonical taxa, manifests, curation archive, or formula-owned Master Plant Pool rows.

## Result
- Canonical species/entries in manifest: **132**
- Historical queue records resolved because they are already canonical: **70**
- Noncanonical FAIL/HOLD/manual-review records preserved and made inactive: **10**
- New genuine scout candidates queued: **8**

## New active scout queue
- priority 1: `monarda-citriodora` — Lamiaceae — Monarda pair
- priority 1: `monarda-punctata` — Lamiaceae — Monarda pair
- priority 2: `scutellaria-drummondii` — Lamiaceae — Scutellaria pair
- priority 2: `scutellaria-wrightii` — Lamiaceae — Scutellaria pair
- priority 3: `lantana-urticoides` — Verbenaceae local pair
- priority 3: `phyla-nodiflora` — Verbenaceae local pair
- priority 4: `commelina-erecta` — Commelinaceae local pair
- priority 4: `tinantia-anomala` — Commelinaceae local pair

## Standing authority
- `data/manifest.json` = installed canonical truth.
- Master Plant Pool = candidate universe.
- `research-queue.json` = scout/review workflow state only.
- Never select a species for curation merely because an old queue status says pending; first confirm the ID is absent from the canonical manifest.
