# Asteraceae — practical family handoff checkpoint (2026-10-28)

**Recommendation:** Budget **three targeted passes total** from the user's 2026-10-28 request, counting the photo-gap rescue already completed. Therefore **two focused passes remain** for a maintenance-ready *private family learner* if held/rights-restricted gaps are explicitly documented. This is not a guarantee of 100% anatomical-photo coverage or of a public Pages launch.

## Latest verified milestone (pass 1)
- **322 of 459** existing Asteraceae source photos physically staged byte-exact in private `Crking92/Hays-Botany-Asteraceae`.
- **137 originals held** in the canonical source repo, all linked in the 459-row rights ledger; none silently missing/deleted.
- **149 of 180 species** have at least one vetted private-preview gallery image; **31 species remain photo-empty**.
- Two previously photo-empty taxa rescued this pass: `Heterotheca subaxillaris` (2 exact Commons MathKnight CC BY-SA originals) and `Carthamus tinctorius` (1 exact Commons Pseudoanas public-domain-by-author-dedication original). Licenses/creators and image perceptual hashes compared to pinned Git originals.
- These new photo imports are independently staged, not automatic public releases. The safflower PD dedication was verified distinctly; it was **not falsely reported as CC0**.
- [Successful exact-file import workflow](https://github.com/Crking92/Hays-Botany-Asteraceae/actions/runs/40778419639).
- [Successful 322-photo desktop/mobile browser QA](https://github.com/Crking92/Hays-Botany-Asteraceae/actions/runs/40778598888), verifying both Camphorweed images and Safflower plus Yarrow/Calvin/Joey/GBIF credits.
- [Download tested 322-photo local learner](https://github.com/Crking92/Hays-Botany-Asteraceae/actions/runs/40778598888/artifacts/12854814253). Extract ZIP, open `dist`, run `RUN_ASTERACEAE_REVIEW.bat` on a Windows machine with Python 3.
- [Successful full photo-source asset reconciliation](https://github.com/Crking92/Hays-Botany-Asteraceae/actions/runs/40778638329).

## Handoff plan
1. **Pass 1 (COMPLETED):** Resolve clearly licensed source photos for empty species and build a verified 31-species gap/backlog. All source photo files still accounted for.
2. **Pass 2 (NEXT):** Prioritize field-useful photo-empty species, obtain verifiable alternate public-safe sources where possible, and close high-impact license mismatches. Never copy all-rights-reserved video frames or treat NC as unrestricted.
3. **Pass 3 (FINISH):** Final desktop/mobile QA, public-safe release-candidate check, credited originals and anatomy annotation review, migration/URL/ownership readiness. Freeze a durable backlog for remaining nonessential or permission-blocked images. User signs off on private learner before moving focus.

After pass 3, `Fabaceae` or another collection can be the primary content/photo migration lane while Asteraceae remains in tracked maintenance, **provided** all source assets are accounted for, QA is green, and any missing field-priority images are listed with specific reasons. Public Pages and hub routing remain separate release gates; a source repo with NC or permission-limited images must not be made public solely to deploy Pages.

## Remaining photo-empty taxa
- Exactly **31** entries, with the source-photo link, rights bucket, correct photographer claim and recommended next work for each: [Asteraceae 31-photo-empty species worklist](https://github.com/Crking92/Hays-Botany-Asteraceae/blob/staging/asteraceae-metadata/migration/asteraceae-31-photo-empty-species-backlog.json).
- 5 have original photo references bearing permissive CC claims needing independent recheck, 24 have source NC claims/replacement needs, and 2 depend on a new licensed source or explicit permission.
- 10 are **editorial review priorities for the Kyle field crew** (not proof they are all common): `Amphiachyris amoena`, `Ratibida columnifera`, `Verbesina encelioides`, `Plectocephalus americanus`, `Pyrrhopappus grandiflorus`, `Tetraneuris linearifolia`, `Centaurea melitensis`, `Hymenopappus artemisiifolius`, `Carphochaete bigelovii`, `Heterotheca canescens`.
- [Detailed family handoff gate](https://github.com/Crking92/Hays-Botany-Asteraceae/blob/staging/asteraceae-metadata/migration/ASTERACEAE_REMAINING_PASSES_AND_EXIT_GATE_20261028.md).
- [Machine-readable handoff status](https://github.com/Crking92/Hays-Botany-Asteraceae/blob/staging/asteraceae-metadata/migration/asteraceae-family-transition-readiness.json).
- [Successful 31-species handoff audit](https://github.com/Crking92/Hays-Botany-Asteraceae/actions/runs/40778804310).

## Explicit limits
- All historical source photos/metadata retain the original hub as authoritative. 29 additional external URLs are not counted as physical source files.
- Having one species photograph does **not** prove complete anatomy, ligule-like diagnostic photo roles, or arrows. Dedicated diagnostic gap filling can continue in future rounds.
- The new family repo is private, includes CC BY-NC and author-permission files. No GitHub Pages activation, public repository visibility change, or hub redirects were performed.
- Main hub project rules and the existing paused grass automations have not been changed.

**Result:** Recommended **two more passes** to close *Asteraceae migration readiness*, then start the next family while keeping its 31-species gap queue and the 137 rights-held originals documented. A perfectly complete public illustrated Asteraceae field reference cannot be promised within a fixed number of passes.
