# Hays Botany — active future-write routing (user direction, October 28, 2026)

**STATUS: ACTIVE FOR FUTURE BOTANICAL EDITS. NOT A PAGES / VISIBILITY / PRODUCTION SITE CUTOVER.**

The user explicitly directed that all **future plant data** be written directly into its assigned `Crking92/Hays-Botany-*` family collection, **not** into `Crking92/Hays-County-Botany`. Original-file source preservation is complete; do not spend time collecting replacement photos as part of routing. This newer, narrower prospective editorial-write rule supersedes the previous **original-hub canonical editor** wording for future botanical changes only. It does not grant public publication or change old website URLs.

## Exact destination (one writer per taxon)

Read the **active machine-readable route**: [ACTIVE_NEW_PLANT_WRITE_ROUTING_20261028.json](ACTIVE_NEW_PLANT_WRITE_ROUTING_20261028.json).

Use the accepted **botanical family**, not the species common name, to select the repository. Examples:
- `Poaceae` (all grasses) → [Hays-Botany-Poaceae](https://github.com/Crking92/Hays-Botany-Poaceae), branch `main` (**public repository: only files licensed/authorized for public source access**).
- `Asteraceae` → [Hays-Botany-Asteraceae](https://github.com/Crking92/Hays-Botany-Asteraceae), branch `staging/asteraceae-metadata` (private).
- `Fabaceae` → [Hays-Botany-Fabaceae](https://github.com/Crking92/Hays-Botany-Fabaceae), branch `staging/fabaceae-metadata` (private).
- `Lamiaceae` → [Hays-Botany-Lamiales](https://github.com/Crking92/Hays-Botany-Lamiales), branch `staging/original-source-transfer` (private).
- `Euphorbiaceae` → [Hays-Botany-Spurges-Mallows](https://github.com/Crking92/Hays-Botany-Spurges-Mallows), branch `staging/original-source-transfer` (private).
- Other families → exact `family_to_repository` mapping, branch `repository_write_branches`. The seven grouped-family repositories keep their current verified original files on `staging/original-source-transfer`; **main remains a scaffold**, not the botany editing branch.

For a newly recognized family **not already in the 146-family routing table**, stop and open a routing decision; **never fallback to writing plants to the old hub**.

## What to write, and what not to write

**Write to the assigned family repository only:** `content/taxa/<Family>/<Genus>/<species-id>/species.json`, `SOURCES.txt`, `image-sources.csv`, exact source-verified media, genus/family lessons, matching local collection index and photo/rights/QA reports. Follow that family's established schema, keep stable slug and accepted-name/synonym checks and verified source hashes.

**Do not write new botanical information to the original hub:** no new species card, genus/family lesson, diagnostic arrows, new species photo, refreshed original `data/manifest.json` taxon entries, or source/taxa backfill from family repos. Old `content/taxa/**` and old manifest are a **read-only legacy snapshot** for the operating public website and historic research. Workflows which still assume old-hub write paths must stay **paused or dispatch-blocked** until rewritten; do not re-enable old installer/fast-fill/card tasks. Do not delete or rewrite old site data.

**Stay safe across chats:** inspect the latest destination branch/README/AGENTS and current Git blob, claims and GitHub Actions for the same species before writing; one writer per species/workstream. Preserve existing canonical/source records and rights provenance. New source photos need individual image rights: CC / explicit owner website grant / correctly applied NC only under documented noncommercial terms, with original creator/source. Public Poaceae raw repository must never receive ARR/private-only/unverified photos. Private quarantine is storage, not an automatic gallery release.

**Do not trigger or claim publication:** the public original learner remains active as a fallback while separate family previews are tested. Changes made to family staging will **not automatically appear** on `https://crking92.github.io/Hays-County-Botany/`, and the existing site should not receive an automatic reverse-sync. Public Pages, private repo visibility changes, hub deep-link routing, new live cards and rollbacks require their own release verification and owner approval.

## Action items for existing workflows / another ChatGPT chat

1. Stop pointing all card installers, grass/photo fast-fill jobs, local `IMPORT_TAXA_ZIP.bat`, manual species fixes and scheduled worker prompts at the original `Hays-County-Botany` plant directories; route into family destinations using the active JSON registry.
2. For the seven private collection branches, perform writes against **`staging/original-source-transfer`**, not empty `main`. Update `data/collection-index.json` on that branch whenever adding or changing a card; run `scripts/validate_collection.py`.
3. Ensure the original hub's species-writing workflows are not dispatched in the meantime. A GitHub documentation change cannot by itself prevent a manually run legacy workflow or collaborator from committing. Apply a suitable main-branch protection / push ruleset after evaluating existing website exceptions; no release/automation schedules are changed by this document.
4. Continue to read the old hub as a historical source for aliases, citations, old cards, site fallback and coordination; **never use it as the destination for new plant science/media writes**. Record chosen destination and commit in the shared cross-chat handoff.

## Human verification checklist (after a manual plant write)

Record family, target repository and branch, species slug, stable ID, accepted name and source evidence, photo creator/license/source if used, old-vs-new duplicate check, destination commit, family index validation, and **whether deployed (usually NO)**.

This is a prospective editorial routing rule adopted at the user's direction, not a retrospective claim that every old plant in the original hub is already served from its new family repo.
