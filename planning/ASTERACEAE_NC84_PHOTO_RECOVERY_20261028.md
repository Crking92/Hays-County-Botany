# Asteraceae — NC84 independent source-photo review and new learner milestone (2026-10-28)

**STATUS: SUCCEEDED. NO PRODUCTION CUTOVER. NO PROJECT RULE CHANGES.** All original source image files are still fully accounted for.

## Original source and private destination
- Canonical source: `Crking92/Hays-County-Botany`, pinned botanical/photo snapshot `034f385e44cec18e8c29be96f83e22aaf78fe3f3`. Source Asteraceae physical image count remains **459**.
- New staging: `Crking92/Hays-Botany-Asteraceae`, **private** branch `staging/asteraceae-metadata`.
- Previous fully audited state: 297 original photographs archived in staging, 162 held in hub.
- Current audit: **319 of 459** byte-identical original photographs staged, **140 held** in original hub and individually tracked. **0 originals unaccounted for** and **0 staged image files without original SHA and rights ledger**.
- 180 Asteraceae species cards staged, 477 original image references reconciled (448 physical-source references + 29 external URLs); 11 physical original files not linked to any species images array.

## 84-photo noncommercial-license review
- Source manifest pinned in Asteraceae main `planning/asteraceae-priority84-nc-source-baseline.json`, **84 exact source blob paths and hashes**.
- **22 passed** independently checking exact *current individual image* licensing and creator attribution against an original image visual/perceptual hash (18 iNaturalist taxa default photos, 1 matching observation photo, 3 GBIF multimedia photographs). All **22 source originals physically archived in private staging**, with original Git blob SHA validated.
- **62 retained** with explicit reasons:
  - **29:** individual iNaturalist photo pages cannot provide reliable machine-verified current rights; stale species-card metadata is insufficient.
  - **30:** no current accessible photo simultaneously matched the source claim, photographer and original archived pixels.
  - **3:** original licenses claim CC BY-NC-ND (no derivative reuse); held pending manual permissions/edits review rather than re-encoding/cropping automatically.
- Every accepted photo remains marked **CC BY-NC or CC BY-NC-SA, private noncommercial educational preview only**, and none is relabeled CC BY or made public-release approved.
- [Success: NC84 verification/archive Action](https://github.com/Crking92/Hays-Botany-Asteraceae/actions/runs/40753225414).
- [Permanent 84-item photo-by-photo decision ledger](https://github.com/Crking92/Hays-Botany-Asteraceae/blob/staging/asteraceae-metadata/migration/asteraceae-84-nc-photo-audit-decisions.json).
- [Verified 22 original-image permissions/credit ledger](https://github.com/Crking92/Hays-Botany-Asteraceae/blob/staging/asteraceae-metadata/migration/asteraceae-verified-84-nc-photo-ledger.json).
- [NC84 summary](https://github.com/Crking92/Hays-Botany-Asteraceae/blob/staging/asteraceae-metadata/migration/asteraceae-84-nc-photo-audit-summary.json).

## Validated learner
- **319 optimized real-photo copies across 147 of 180 species**; **33 species** still have no accepted/private-preview photo. These are photograph-presence counts only, **not** six-role diagnostic anatomy or arrow completeness.
- Private gallery now has **138 images explicitly labeled noncommercial-only** (previous 116 + 22 new source-verified photos). The 6 Calvin King permission images retain individual author credit; another 24 provisional Joey Santore NC source-claim images stay private, not unrestricted public.
- [Successful desktop/mobile learner regression](https://github.com/Crking92/Hays-Botany-Asteraceae/actions/runs/40753714373): yarrow has exactly two working photos, Calvin owner-credit and Joey NC labels are visible, GBIF originals load, **Erigeron geiseri** new NC photo loads with Andy Newman credit and explicit CC BY-NC warning.
- [Download 319-photo private visual learner ZIP + screenshots](https://github.com/Crking92/Hays-Botany-Asteraceae/actions/runs/40753714373/artifacts/12845257454). On Windows extract all, open `dist`, double-click `RUN_ASTERACEAE_REVIEW.bat` (Python 3 required).
- [Passed updated all-459-source reconciliation](https://github.com/Crking92/Hays-Botany-Asteraceae/actions/runs/40753674437).
- No Pages publication or live hub routing occurred. The strict public candidate must contain **zero NC-only and zero author-permission or provisional-source images**; run the preflight after each source change.

## Remaining 140 held source originals by next task
- **62:** noncommercial source cases above (including 3 NC-ND) awaiting exact license/photo matching or separate rights.
- **33:** previously verified priority source batch residual (12 Commons, 4 GBIF, 14 iNaturalist and 3 other).
- **34:** other/unknown owner, provenance and licensing issues.
- **11:** unreferenced original source files needing identification and gallery-role inspection.
- Separately **29 external image references**, not missing local source images; do not count them in 459 physical files or imply they have been archived.

## Safety/ownership
- The private source branch contains noncommercial and owner-authorized photos. Do not turn the repository public or expose raw archived file history as part of a Pages rollout without a complete rights audit.
- The main hub remains source-of-truth. All original photo bytes stay in its immutable source Git commit.
- All programmatic photo approval is metadata+hash verification, not an anatomy-arrow accuracy judgment. Original image content still needs species diagnostic and annotation review.
- `PROJECT_RULES.md`, `workflow/COORDINATION.md`, GitHub Pages configuration, and the paused grass automations are unchanged.

## Suggested next actions
1. Check the **11 unreferenced original files** for species and gallery mapping, then the 33 held source-license mismatches.
2. Revisit the 29 direct iNaturalist photo links where current photo metadata was unavailable, with manual permission or another source-provenance route.
3. Prepare actual diagnostic arrows for individual visible structures without inferring arrows from uncropped photos.
4. Retest mobile and source links before any separately authorized private-to-public release.
