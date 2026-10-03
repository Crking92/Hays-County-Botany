# Project reconciliation — Joey/family audit + curation queue

**Date:** 2026-10-02  
**Decision:** pause additional species deep-review batches long enough to reconcile the completed family work and approved curation backlog.

## What changed

- Joey archive now contains **22 deep batches**, **10 video extractions**, **731 source records**, **351 exact-media locks**, and **183 persisted video-frame records**.
- The family coverage audit spans **39 locally relevant families**.
- **17 family backfill packages/groups** are already indexed.
- The canonical learner still has **81 species across 11 represented families**.
- Only **5 of those 11 represented families currently have a canonical `family.json`**.
- The presentation layer exposes only **5 family profiles** and **35 glossary terms**.
- The research queue currently has **38 approved records ready to move forward**: 33 normal native approvals, 3 approved comparisons, and 2 approved range exceptions.

## Merge gap

The research layer is now ahead of the learner layer.

Completed family diagnostics, Joey exact-media/source records, comparison logic, and glossary terms are preserved in `research-drafts/`, but much of that material is not yet visible in canonical family files or `data/learning-layer.json`.

## Highest-priority reconciliation

1. Merge completed/verified family lessons into `content/taxa/<Family>/family.json` and `data/learning-layer.json` without overwriting newer canonical work.
2. Process the approved species backlog through `curation-inbox/` in manageable batches.
3. During species curation, merge relevant exact Joey source/media records into `SOURCES.txt` and `image-sources.csv`.
4. Promote independently verified morphology vocabulary and comparison rules into the glossary/presentation layer.
5. Leave active family audits/backfills (for example Cupressaceae and later gaps) in research until their family package is complete.

## Canonical family-file coverage

Present:
- Apocynaceae
- Asteraceae
- Convolvulaceae
- Fagaceae
- Papaveraceae

Missing despite current canonical species:
- Asparagaceae
- Cupressaceae
- Ebenaceae
- Lamiaceae
- Onagraceae
- Poaceae

Several existing family files are starter files from 2026-09-30 and should be refreshed from the newer family audit/backfills.

## Rights guardrail

Extracted Joey YouTube frames are private-study assets unless separate reuse permission/license is established. Joey exact media/source notes can inform the learner, but public-reuse status must remain explicit per asset.

## Recommendation

Do the merge/reconciliation pass now, then resume new species batches from a cleaner baseline.
