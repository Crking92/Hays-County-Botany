# Asteraceae: yarrow and Joey Santore / Calvin King photo audit (2026-10-28)

**STATUS: FIXED AND BROWSER-TESTED PRIVATE LEARNER. NO PUBLIC PAGES CUTOVER OR PROJECT RULE CHANGE.**

## User report
User tested Asteraceae learner and observed only one yarrow photograph. User also confirmed Joey Santore and Calvin King photos should be represented with credits. The project must honor actual per-photo iNaturalist licensing; user asserts Calvin King can permit project reuse.

## Yarrow correction
- Both canonical yarrow photo records are present in the original hub `Achillea/achillea-millefolium/species.json`.
- New Asteraceae staging license ledger includes **both** physical photos, creators Jane S. Richardson (CC BY 3.0) and Fritzflohrreynolds (CC BY-SA 3.0).
- Early private preview contained only one, resulting from first license-verification pass.
- Corrected browser QA in `scripts/test_asteraceae_photo_preview_browser.py` now **asserts exactly two yarrow images load and both credits appear** on desktop and mobile. Successful [workflow run 40726997133](https://github.com/Crking92/Hays-Botany-Asteraceae/actions/runs/40726997133).

## Full original photo-credit audit
- **Joey Santore:** 76 photo references in 39 species.
  - 41 originally passed exact iNaturalist photo ID/observation ID license and creator checks, physically archived.
  - 24 more original photo files physically staged for noncommercial private review, source metadata attribution and CC BY-NC claims only; 3 of those lack exact upstream photo-page links. Current per-photo license is **not independently verified for these 24**, so not approved for public release.
  - 11 remaining are held because pinned source metadata does not establish iNaturalist provenance. Do not infer Joey's rights or source photo ID simply because he is credited; reconcile with original photo pages or written photographer authorization.
  - **65/76 Joey-credited image originals** in private staging. Retain attribution and NC restrictions; CC BY-NC is not an unconditional attribution-only grant.
- **Calvin King:** all six photo references were previously held due source status `All rights reserved — owner-authorized private study` (no license metadata) and absence of source observation IDs.
  - Based on user’s explicit Oct 28, 2026 permission assertion, six original files copied into private staging, keeping **Calvin King** attribution and `Used with permission for Hays Botany` label.
  - Do not relabel as Creative Commons, or infer general-purpose/third-party redistribution rights. Exact photo source page names and original Git blob SHA preserved.
- Audited original files from pinned hub commit `034f385e44cec18e8c29be96f83e22aaf78fe3f3` and verified each copied file's Git blob SHA.
- New author-permission/provisional-source metadata: [private Asteraceae author ledger](https://github.com/Crking92/Hays-Botany-Asteraceae/blob/staging/asteraceae-metadata/migration/asteraceae-author-permitted-private-photo-ledger.json), staged branch commit `18a53504d0582305784375932960fb77e2237845`.
- Both fully verified (Commons/iNat) and provisionally attributed (Joey) / author permitted (Calvin) records have separate rights flags in the learner.

## Tested learner status
- **210 physical originals in private Asteraceae staging** = 82 Commons independently verified + 98 iNaturalist independently verified + 24 Joey source-claimed CC BY-NC + 6 Calvin author-permitted.
- 180 searchable species; **106 have at least one preview photo**, 74 remain without any photo in private preview.
- Site test includes 210 optimized photos; **116 NC-only flags** (92 originally exact-photo licensed iNat + 24 provisionally attributed Joey).
- The private preview now visibly distinguishes NC-only and owner-authorization/source-pending photos in captions.
- Desktop and mobile Chromium browser tests passed exact two-yarrow-image requirement, source credit lines, Calvin permission label, Joey NC caption and real image loading.
- [Download the updated private learner + screenshots](https://github.com/Crking92/Hays-Botany-Asteraceae/actions/runs/40726997133/artifacts/12834080274). ZIP extract then `dist/RUN_ASTERACEAE_REVIEW.bat` on Windows using Python 3.
- Strict public Pages release candidate is separately validated and **still limited to 88 independently verified non-NC CC images**; zero provisional Joey / Calvin owner-authorized images allowed. [Strict test workflow 40726997156](https://github.com/Crking92/Hays-Botany-Asteraceae/actions/runs/40726997156).
- Live original website is unchanged. New family GitHub Pages not enabled, not deployed, and hub has no Asteraceae routing cutover.

## Next photo research
1. Resolve the 11 remaining Joey-credited images from exact iNaturalist photo records or written permission. Do not label YouTube frames/iNat taxon thumbnails as verified photographs without evidence.
2. Visually confirm the 210 gallery images and anatomy arrows before any public release. No arrow locations are auto-guessed.
3. If public Asteraceae Pages is authorized later, explicitly decide site noncommercial usage and exact scope of Calvin King photo license before changing public-photo allowlist.
4. Keep family source authority and project rules unchanged until all migration stages are approved.
