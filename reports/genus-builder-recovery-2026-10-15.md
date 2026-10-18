# Genus Comparison Builder — recovery handoff (2026-10-15)

This report records incomplete **genus-lane** publication only. It is not a completed lesson or authorization to bypass active claims. Read latest `PROJECT_RULES.md`, `workflow/COORDINATION.md`, `workflow/work-claims.json`, canonical manifest and index before any retry.

## Priority 1 — Alternanthera lesson published; index not yet registered

- Published canonical genus lesson: `content/taxa/Amaranthaceae/Alternanthera/genus.json`
- Verified commit: `d2bc1a3630b71c7af879d5ce122423c05e285a2e`
- Lesson was re-fetched and verified: 3 canonical species, 5 comparison characters, 4 anatomy roles.
- Source species: `alternanthera-caracasana`, `alternanthera-philoxeroides`, `alternanthera-pungens`. No species/range/photo binaries changed.
- Google Sheet `Hays_Botany_ID_Master_Curation_Tracker`, `Genus Study Index!A220:B220` = `Amaranthaceae | Alternanthera`; readback verified. Derived C:M were not edited.
- **Still blocked:** `data/lesson-index.json` lacks `{ "family": "Amaranthaceae", "genus": "Alternanthera" }`. Two fresh-SHA GitHub `update_file` attempts were rejected with exact tool response: `This tool call was blocked by OpenAI's safety checks. Please double check what you are sending.` This was **not** a confirmed GitHub 409/422 error.
- **Next safe action:** first check whether a concurrent worker has registered it. If absent, fetch latest index SHA, add exactly one genus entry without deleting or reordering other work, commit once and re-fetch. If connector safety rejects again, do not use an alternative tool to bypass the rejection; leave this handoff unresolved.

## Other outstanding genus-lane work

- `content/taxa/Lythraceae/Ammannia/genus.json` absent on this check. Both `ammannia-auriculata` and `ammannia-coccinea` are canonical and Sheet `Genus Study Index` row 201 already exists. Old claim `automation-genus-ammannia-20261014-1637` was still marked active despite expiry at 2026-10-14 18:37 CDT. Verify claim ownership and latest durable state before reclaiming; do not bypass the coordination safeguard.
- `content/taxa/Asteraceae/Helenium/genus.json` exists but its proposed anatomy/comparison upgrade failed twice with the same connector-level safety-check rejection. No new Helenium content was committed this run. Existing file and four canonical species remain authoritative. Recover as a small merged update after a fresh read, if permitted.
- `content/taxa/Poaceae/Tridens/genus.json` exists; a small anatomy/comparison upgrade also hit the same connector-level safety-check rejection. No Tridens changes were committed this run. Keep existing taxonomy cautions and photo rights unchanged.

## Visual follow-ups

Alternanthera still needs visually verified, same-scale flower-head peduncle comparisons; `A. caracasana` versus `A. pungens` bract-tip macros; rooting-node photos of `A. philoxeroides`; and mature fruit/seed close-ups. The genus lesson references species-record paths and provenance but does **not** claim new photos installed or arrows verified.

All other workers' claims, schedules, canonical species and range classifications remain untouched.

## 2026-10-16 Lactuca unpublished lesson handoff

- **Blocked path:** `content/taxa/Asteraceae/Lactuca/genus.json` (existing blob `fcfe6da69bcc7db2a4ef37af3f3876f751744c1a` at attempt).
- **Prepared, not published:** four photo-role anatomy lessons (all-ligulate head/phyllaries; abaxial midrib prickles and clasping auricles; ripe cypsela face nerves; measured cypsela body versus beak), three comparison cards, current canonical status (only `lactuca-serriola` installed; `lactuca-ludoviciana` remains source-pool noncanonical), two physical existing image references with Harry Rose CC BY 2.0 and Matt Lavin CC BY-SA 2.0 rights, and an eight-candidate archived photo-library handoff (`mass-38925103720`). Original FNA references and seven-row comparison matrix would be preserved. No images or arrows were installed.
- **Source artifacts:** existing genus JSON and `content/taxa/Asteraceae/Lactuca/lactuca-serriola/species.json`, `data/manifest.json`, `workflow/photo-library/species-index.json`, live `Master Plant Pool` and `Genus Study Index`.
- **Exact failure:** GitHub connector returned `This tool call was blocked by OpenAI's safety checks. Please double check what you are sending.` This was not a confirmed 409/422 SHA conflict. No Lactuca content was committed.
- **Next action:** check current genus lesson and active claims before selecting this recovery; only if safe, refresh blob SHA, rebuild and merge the prepared anatomy/photo-role lesson from the authoritative records, make one permitted write and verify on `main`. Do not bypass connector safety or mark this handoff complete.
- **Separate successful genus this run:** `content/taxa/Poaceae/Bouteloua/genus.json` committed as `527656ed63b32f2ecf0876114b4c76a0453a8248` and re-fetched on `main`; four anatomy lessons, three comparison cards, 29 gallery-record inventory reconciliation, index and Sheet registrations already present. No photos or species installed.

## 2026-10-18 Tridens retry — connector blocked

- Path: `content/taxa/Poaceae/Tridens/genus.json`; latest blob at attempted write `d2d1e8ca80bde94b90b1bd737f18a39a0cc0fc1c`.
- Intended change: correct the non-exclusive bare proximal branch distinction between *T. texanus* and *T. flavus*; retain the existing seven-row comparison, four anatomy steps, three cards; add four measured photo roles and six existing photo records with creator, license and source.
- Source artifacts: current genus and Poaceae family lessons, three canonical `species.json` records, manifest, live Master Plant Pool rows 1199–1204, Genus Study Index row 121; all six existing JPEGs re-fetched on main.
- Exact error: `This tool call was blocked by OpenAI's safety checks. Please double check what you are sending.` Not a confirmed GitHub SHA conflict. **No genus change committed.**
- Next safe action: after coordination/claims check, re-fetch current genus SHA, prepare a small merge preserving intervening edits and try once; do not treat this retry as complete or overwrite other lanes.
