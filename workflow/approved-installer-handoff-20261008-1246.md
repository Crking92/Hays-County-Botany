# Approved installer handoff — 2026-10-08 13:46 CDT

Canonical manifest verified: **433 species**. **Adiantum pedatum** installed by successful curation Action [37822608861](https://github.com/Crking92/Hays-County-Botany/actions/runs/37822608861); confirmed in `data/manifest.json` and `reports/last-curation-run.json`. Keep its `FAIL_TARGET_ZONE` scientific status and provisional visual-incomplete label.

**One fully staged, untriggered batch remains:** `curation-inbox/approved-installer-asteraceae-rudbeckia-tetraneuris-20261008-001`, containing **Tetraneuris acaulis only** (species.json, SOURCES.txt, image-sources.csv, batch.json all verified). No READY marker. Two READY attempts were blocked by GitHub connector write-safety checks on 2026-10-08 at 13:46 CDT. No active curation Action at inspection. Do not duplicate/rebuild the package. Preserve `FAIL_TARGET_ZONE` and provisional visual-incomplete; `Rudbeckia maxima` is not in this package.

**Six canonical species have stale research-queue learner statuses** (`approved_pending_curation` despite installed manifest): `quercus-alba`, `adiantum-pedatum`, `grindelia-adenodonta`, `grindelia-ciliata`, `silphium-laciniatum`, `solidago-mexicana`. Two queue update attempts failed GitHub write-safety checks. When writes work, update only their learner/canonical/reconciliation status and clear execution priority; retain original scientific `status`, native-range, and approval fields.

Latest curation Action status at inspection: 37822608861 completed/success, 37796565995 completed/success. No Google Sheet formula-owned cells changed.

Next safe action: re-fetch manifest, claims, queue, inbox and Actions; if no collision, trigger existing Tetraneuris package with READY as the final commit. If blocked again, move to another eligible curation target or queue reconciliation, without disabling the installer.

## Reconciliation update — 2026-10-08 19:55 CDT

Canonical manifest checked at **440 taxa**. The previous Tetraneuris, Rudbeckia and Sorghastrum entries are installed; historical pending notes above are superseded by the manifest.

**Matelea parvifolia**: source-pool learner-approved, taxonomy accepted, range **FAIL_TARGET_ZONE** (Big Bend/SW Texas; no confirmed target-zone counties). The existing inbox batch `curation-inbox/approved-installer-apocynaceae-matelea-parvifolia-20261008-001` now has its complete species.json, SOURCES.txt, image-sources.csv and batch.json staged. Morphology-first comparisons include M. sagittifolia, Chthamalia biflora, M. reticulata and M. edwardsensis. No exact licensed photo yet; explicitly provisional visual-incomplete. **READY not present**: two clean trigger-write attempts were blocked by connector safety checks. Do not rebuild or create duplicate packages; retry only after checking latest manifest/claims/inbox/Actions.

**9 stale queue statuses**: `quercus-alba`, `sorghastrum-elliottii`, `tetraneuris-acaulis`, `adiantum-pedatum`, `rudbeckia-maxima`, `grindelia-adenodonta`, `grindelia-ciliata`, `silphium-laciniatum`, `solidago-mexicana` are installed according to the canonical manifest but still have `learner_curation_status=approved_pending_curation` in research-queue.json. Reconcile their learner/canonical state when a safe 502 KB queue update is possible, preserving original range/science/approval fields. Do not reinstall.

No Matelea-specific active claim at this check; other family-polish claims must remain untouched. No Google Sheet derived ranges modified. GitHub Actions run-list access was unavailable through the current connector, so no claim is made about a newly active Action.
