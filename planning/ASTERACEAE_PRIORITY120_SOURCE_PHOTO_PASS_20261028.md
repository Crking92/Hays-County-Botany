# Hays Botany Asteraceae — source-license priority 120 completion, Oct 28 2026

**Result: 120/120 photo source files individually addressed; 87 exact-source photographs physically archived during this pass. Asteraceae is not fully photo-complete or publicly cut over.**

## Latest audited totals
- Source Asteraceae original folder: **459 physically archived photos**, **180 installed species**, source Git tree `394bb64d90c025a51a8d6e10dc4a19bce1aaf623`.
- New Asteraceae private staging: **297 original source photo files** (previous 210 + new 87). Each newly transferred file has original Git blob SHA and rights ledger; private source-licensing checks were performed, **not automatic public publication approvals**.
- **162 original photos retained, hashed and traced in the hub**, not physically copied to staging. Nothing deleted. All 459 accounted for with per-file status.
- **477 species image references**: 448 original physical files + **29 separate external URLs**; **11 source photos not attached to species card**.
- Private learner: 180 species, **297 optimized gallery photographs covering 141 species**, **39 species still lack a migrated photo**. 116 gallery photos are explicitly marked NC-only (92 independent-photo checks + 24 provisional original-source Joey Santore claims); six Calvin King photos retain owner-permission attribution and are not relicensed as CC.
- Nonpublishing strict source-verified CC snapshot: **112 photos across 81 species**, **zero NC-only**, **zero author-permission/private-only**; this is still not a live public Pages site.
- The actual original source repo and main Hays Botany learner remain authoritative. No rules/coordination rewrite, GitHub Pages activation, repository visibility change, hub redirect or grass automation restart occurred.

## Newly completed 120-file source-license batch

| Upstream source | Original priority candidates | Verified and physically copied | Held with file-level reasons |
|---|---:|---:|---:|
| Wikimedia Commons | 40 | 28 | 12 |
| GBIF multimedia (mostly Texas iNaturalist records) | 58 | 54 | 4 |
| iNaturalist taxon/photo/guide pages | 19 | 5 | 14 |
| USGS | 1 | 0 | 1 |
| Backyard Nature | 2 | 0 | 2 |
| **Total** | **120** | **87** | **33** |

- Commons images required exact upstream File metadata, a compatible current CC/PD claim, credited creator agreement, plus perceptual image match with the pinned Git original. Twelve held for creator mismatch (5), license mismatch (5), or nonstandard source license interpretation (2).
- GBIF's normal occurrence endpoint was failing, but `/v1/occurrence/{id}/fragment` provides the **multimedia-specific** license, media identifier and image creator; record-level and photo-level licenses can differ. 54 originals matched actual multimedia license, creator, pixels and Git SHA. Four are held.
- iNaturalist taxon pages were not treated as exact-photo records without proof. Nine taxon-page photos were compared against current default_photo ID/license/creator/image; five passed. Ten more direct-photo or guide links lack independently established current photo license/identity, and four taxon-cover comparisons did not pass.
- The original author permissions for Calvin King and noncommercial terms for Joey Santore remain intact and independently labeled.
- The 33 still held in the priority batch are part of the **162 overall remaining original photos**. Other remaining groups: 84 source NC claims pending exact checks, 34 other permissions/rights, and 11 unreferenced originals.

## Files to resume accurately
- [Full original 459-row asset ledger](https://github.com/Crking92/Hays-Botany-Asteraceae/blob/staging/asteraceae-metadata/migration/asteraceae-full-image-asset-reconciliation.csv).
- [All 120 photo-source rights outcomes, one row per photo](https://github.com/Crking92/Hays-Botany-Asteraceae/blob/staging/asteraceae-metadata/migration/asteraceae-priority120-upstream-review-decisions.csv).
- [120-photo JSON records with original Git URLs and detailed mismatch reasons](https://github.com/Crking92/Hays-Botany-Asteraceae/blob/staging/asteraceae-metadata/migration/asteraceae-priority120-upstream-review-decisions.json).
- [Complete 120-photo review summary](https://github.com/Crking92/Hays-Botany-Asteraceae/blob/staging/asteraceae-metadata/migration/asteraceae-priority120-review-summary.json).
- [Source-permissions stage audit workflow](https://github.com/Crking92/Hays-Botany-Asteraceae/actions/runs/40748610800).
- [Passed 297-photo desktop/mobile QA workflow](https://github.com/Crking92/Hays-Botany-Asteraceae/actions/runs/40748676688).
- [Download updated **private** 297-photo learner with screenshots](https://github.com/Crking92/Hays-Botany-Asteraceae/actions/runs/40748676688/artifacts/12843256522); unzip, open `dist`, double-click `RUN_ASTERACEAE_REVIEW.bat` (Python 3).
- [Passed strict 112-photo release candidate](https://github.com/Crking92/Hays-Botany-Asteraceae/actions/runs/40748533766). It was built and checked, **not published**.

## Next work priorities
1. **84 NC source claims**, verifying actual current individual-photo licenses and credit, for private noncommercial preview without confusing them with public-rights approved photos.
2. The remaining **33** priority source/creator mismatches (especially 12 Commons, 4 GBIF, 14 iNat, 3 other), where possible seek exact original source records or photographer permission.
3. The 34 unknown/rights-conflicted photos and 11 unreferenced originals; check licensing before attaching.
4. Independently track the 29 external photo URLs, deciding whether to physically archive each (do not pretend they are physical original images already stored in the main hub).
5. Visual verification of diagnostic arrows, full family site QA and release rights before any public Pages or hub cutover.

**Terminology:** “100% accounted for” means all original source files have an immutable hash and a clear disposition; it does **not** mean all source photos have legally transferable or public-use rights.
