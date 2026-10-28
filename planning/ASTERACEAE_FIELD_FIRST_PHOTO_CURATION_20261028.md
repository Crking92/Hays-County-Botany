# Asteraceae Visual Learner — photo curation rule (2026-10-28)

**Owner direction:** Use only photographs that have a worthwhile role in field identification and have traceable original photographer credit, source and reuse rights. Photographs without verifiable credit or individual reuse terms should not appear in the learner for now.

## Changes applied to the private Asteraceae review builder

1. **Preserve original source data.** The canonical `Hays-County-Botany` originals, immutable SHA snapshots, all 459-file inventory, existing private copied files and rights ledgers are **not deleted or rewritten**. A photo omitted from the learner is excluded at site-build time, not purged from storage.
2. **Temporarily exclude 24 provisional Joey Santore images** where the pinned original records claim CC BY-NC but the current individual photo rights have **not** been independently verified. This does not impugn the authorship: it keeps uncertain *reuse terms* out of the gallery. The **41 Joey photos independently checked against exact iNaturalist photo IDs remain eligible**, with their CC BY-NC attribution.
3. **Keep Calvin King photos** that have explicit author permission for this Hays Botany use with the `Calvin King` attribution. Do not describe them as CC-licensed.
4. **Hold any further photographs** with a missing source URL, missing/ambiguous creator, or missing traceable rights evidence. A CC0-licensed record may say `no rights reserved`; that is acceptable with an exact source page and CC0 dedication.
5. **Trim repetitive recognition/distance photos.** Keep at most two clearly generic habit/recognition views per species. Do **not** apply that limit to specific documented diagnostic photographs (leaf, stem, bud, flowering head, phyllaries, fruits, pappus, seeds, basal rosette, etc.). This is a first-pass role filter and does not replace visual QA.
6. **No invented anatomy arrows.** Preserve helpful images and current visible instructional content, but label anatomy only after reviewing actual structures.
7. **Public candidate stays stricter:** no CC BY-NC, no permission-limited author photos, no provisional licenses; no public Pages deployment or visibility change without owner approval.
8. **Audit every exclusion.** The static preview includes `data/photo-curation-summary.json`; the QA workflow artifact contains a file-by-file list in `qa-report/photo-curation/private/curation-decisions.json`. Original per-file source/permission ledgers remain the permanent archive.

## Intent

The learner should not become a wall of random photos. Photos should show a recognizable field view or an actual diagnostic structure, with attribution clearly visible. A few good photographs teaching a useful identification feature are better than multiple redundant landscape images.

## Scope

This is a **presentation rule**, not an erasure request. Original hub, Asteraceae staging, taxonomic lessons, original rights metadata, protected photo files and project rules all remain in place. Also no modification to Poaceae or other family repositories was made.

The canonical original Asteraceae migration state before this curation was 323 of 459 old original photo files staged plus 39 newly acquired, independently credited CC files, with 179 of 180 species carrying at least one photo. After applying the new curation, the count *shown* in the learner may be lower, by design. Report displayed-photo count separately from archived-photo count.

Resume: [Asteraceae private learner site build](https://github.com/Crking92/Hays-Botany-Asteraceae/blob/main/scripts/build_asteraceae_photo_preview.py), and [desktop/mobile browser QA](https://github.com/Crking92/Hays-Botany-Asteraceae/blob/main/scripts/test_asteraceae_photo_preview_browser.py).
