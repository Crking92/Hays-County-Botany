# Approved installer reconciliation — 2026-10-08

Canonical manifest: 430 species at inspection. Already installed but queue remains `approved_pending_curation`: `quercus-alba`, `grindelia-adenodonta`, `silphium-laciniatum`. Their native-range classifications must be preserved.

Complete but untriggered staging batch: `curation-inbox/approved-installer-asteraceae-grindelia-solidago-20261008-001` for `grindelia-ciliata` (range unresolved) and `solidago-mexicana` (target-zone fail). Batch has `batch.json`, `species.json`, `SOURCES.txt`, and `image-sources.csv` for each; `READY` is absent. Two attempts to create `READY` were blocked by connector safety checks; do not rebuild or duplicate. Recheck current Action/manifest before triggering. No curation Action was active at last inspection. Photos still need exact-species backfill.

## Reconciliation update — 2026-10-08 10:49 CDT

The previously listed Grindelia ciliata + Solidago mexicana batch is **now installed**, archived, and confirmed by successful curation Action 37796565995. Canonical `data/manifest.json` has **432 species**. The old 'untriggered' status above is historical only.

Five installed taxa still have outdated `learner_curation_status=approved_pending_curation` in `research-queue.json`: `quercus-alba`, `grindelia-adenodonta`, `grindelia-ciliata`, `silphium-laciniatum`, `solidago-mexicana`. Preserve their independent native-range statuses when reconciling. Updating the 502 KB queue file was blocked by connector safety checks.

New partial staging batch `curation-inbox/approved-installer-asteraceae-rudbeckia-tetraneuris-20261008-001` has `batch.json` and a complete **Tetraneuris acaulis** package (`species.json`, `SOURCES.txt`, `image-sources.csv`). It is intentionally **not READY** because both attempts to write the final trigger were blocked. `Rudbeckia maxima` was skipped after blocked staging writes; it has no staged species card. The batch metadata still mentions both originally planned taxa, but only Tetraneuris is present. Before retrying READY, check claims, manifest, and Actions; optionally correct batch notes. `Tetraneuris acaulis` remains **FAIL_TARGET_ZONE** and provisional visual-incomplete pending exact licensed photos.
