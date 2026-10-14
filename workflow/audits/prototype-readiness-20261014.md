# Prototype readiness checkpoint — 2026-10-14 (morning CT)

Read-only audit plus photo-worker automation adjustment. This is NOT a complete repository census.

## Canonical scope
- data/manifest.json: 532 installed species, spanning 183 genus paths and 59 represented families (manifest-derived; 147 family modules in the larger source-pool project).
- Master Plant Pool (Google Sheet): 1,282 source-pool taxa, 612 genera, 147 families. Do not treat the difference as automatically installable; synonyms, FAIL/HOLD and source-pool status must be preserved.
- Genus Study Index has 164 populated genus rows (checked), of which 92 are labeled Complete, 10 Ready, 59 blank and 3 special status notes. Sheet status is not proof of missing GitHub module.
- Stratified 15-genus module existence sample: 15/15 genus.json files exist; 8/15 have the richer `visual_lesson` or `visual_comparison` field. Other 7 may have useful comparison text; treat as VISUAL REVIEW NEEDED, not missing content.
- Stratified 18-species photo-metadata sample: zero = 1, one = 9, multiple = 8. Count LOCAL image path = at least a repository-local reference, NOT verified physically present; REMOTE image = HTTPS reference, NOT physical install. Representative gaps: `muhlenbergia-piniflora` images=0; `quercus-alba` one external reference; `anatherum-glomeratum` three external references. These are sample counts, NOT totals for 532.
- Research queue: no records currently explicitly `approved_pending_curation` or `ready_for_curation` in its primary status fields. Do not indiscriminately promote range HOLDs.
- Recent main commits show a staged `curation-inbox/ulmus-three-elms-local-photo-20261014-001/READY` and subsequent canonical image/source commit. Action may be in progress; DO NOT resubmit or duplicate without checking reports and canonical result.
- Coordination claims: five `active` statuses in latest fetched work-claims; four earlier expiration times and one later. Verify current time, action state and durable outputs before release; do not delete based solely on age.
- Photo worker renamed 'Diagnostic Photo Fast-Fill', scheduled hourly, kept enabled. Smaller per-run target, maximum one or two safe source attempts, do not self-disable, strict provenance and post-install gallery preservation. See automation itself for canonical prompt.

## Suggested action order
1. Verify existing READY batches and installer reports before submitting anything again.
2. Reconcile all 164 indexed genera with GitHub modules, and expand across unindexed master-pool multi-species genera; classify missing, text-only, and visual-ready separately.
3. Complete full 532 canonical species image metadata census AND validate local file presence separately.
4. Physically install zero-photo images before chasing unusual microanatomy; then matched view pairs and part-specific macros, with verified arrows later.
5. Reconcile expired claims and stale queue labels against current commit and action evidence.
6. Continue source-pool accepted-name reconciliation and safe learner admission; retain native-range FAIL/HOLD/PROVISIONAL honestly.

## Evidence caveats
This is a durable checkpoint from connector reads, not an assertion that all images load on the published Pages website, and not a completed comprehensive photo audit. Never show sampled figures as global totals.
