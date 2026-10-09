# Approved Installer handoff — 2026-10-09

## Durable staged curation
- Batch: `curation-inbox/approved-installer-asteraceae-symphyotrichum-pair-20261009-001/`
- Staging commit: `19535329cde8bfdd76f88b709494bbce31fd2f52`.
- Species: `symphyotrichum-oblongifolium` (reviewed PASS, Hays/Travis/Bexar) and `symphyotrichum-praealtum` (UNRESOLVED, Travis only).
- Both species have complete `species.json`, `SOURCES.txt`, and `image-sources.csv` with three licensed CC0 exact-species Wikimedia Commons photo leads total.
- Canonical manifest at staging had 445 taxa, neither species installed. No active species claim or curation Action was present.
- **Do not assume installed**: final `READY` trigger was blocked twice by connector safety checks; a READY commit object was created but branch ref was NOT advanced. Verify live inbox and manifest before attempting trigger.
- Only create `curation-inbox/approved-installer-asteraceae-symphyotrichum-pair-20261009-001/READY` after checking current main, active claims, and Actions. Confirm images downloaded and provenance retained, then reconcile only affected records. If a new worker installs either species first, shrink/rebuild the batch rather than duplicate.
- No Master Plant Pool formula-owned cells were edited.

## Claim reconciliation opportunities (not applied)
- `automation-genus-physaria-20261008-2335` expired after the five-species genus comparison was committed in `4cca94f7c0d54c1a9aafb74653c5080d0d4d089b`; all five taxa already canonical.
- `automation-family-similarity-malvaceae-20261008-2010` expired after the family comparison was committed in `62c7d694a268b7ac3039f6937ee2cc7e0d2a6b18`.
- Releasing these two claims in `workflow/work-claims.json` was attempted but blocked by connector write-safety checks. Do not infer they are released; recheck live claims before changing them. The Fagaceae claim was intentionally left untouched because no later matching family commit was verified.

## Existing taxonomy mapping holds
`clematis-reticulata`, `grindelia-squarrosa`, `silphium-integrifolium` remain mapping-needed, not installable as separate cards until concepts resolve.
