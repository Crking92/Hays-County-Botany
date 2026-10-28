# Asteraceae Photo Migration — Handoff checkpoint, 2026-10-28

**Status: PRIVATE FAMILY VISUAL LEARNER PHOTO MIGRATION HANDOFF READY. Independent PUBLIC website deployment/complete anatomy quality is NOT approved.**

## Last confirmed audited totals
- **180 Asteraceae species** in private new family staging `Crking92/Hays-Botany-Asteraceae`.
- **179 of 180 species** have at least one source-backed photographed reference in the private learner.
- **362 photographic gallery files**, tested fully loaded on desktop and mobile; **323 source-original Git blobs** byte-identical from the original 459-photo Asteraceae archive + **39 newly sourced CC photos stored separately**.
- **136 of original 459 physical source files remain in the authoritative main hub**, each with original Git blob SHA and a clear rights/identity hold decision; **zero source files unaccounted for**. The 29 separately referenced external links were never incorrectly counted as original physical photo files.
- New images (separate from original 459): 36 Texas research-grade iNaturalist photos (individual CC BY/BY-SA/CC0 rights checked; across 26 formerly photo-empty species), 1 Harry Rose Australian Commons CC BY 2.0 Chondrilla habit image with non-Texas caption, and 2 Texas photos verified under authoritative Kew homotypic synonyms.
- **One more original photo recovered:** Reid Hardin’s exact old-plainsman var. corymbosus photo ID `276095449` matched research-grade **variety** observation `159788922`, live CC BY photo attribution, original Git SHA and 1/64 dHash distance.
- Only **Pectis angustifolia var. fastigiata** has no independently verified variety-level image in private staging. Original held image `inat-246007542.jpg`, historical CC BY-NC claim, source URL https://www.inaturalist.org/photos/246007542; keep tracked rather than falsely attach a generic parent-species image.

## Passed GitHub validations
- [Successful 362-photo desktop/mobile real-image test](https://github.com/Crking92/Hays-Botany-Asteraceae/actions/runs/40781789809), including 2-photo Yarrow, credited Calvin King and Joey Santore source-rights notices, Texas field priority taxa, Commons Chondrilla, accepted synonym cards and old-plainsman original. [Download the test learner ZIP](https://github.com/Crking92/Hays-Botany-Asteraceae/actions/runs/40781789809/artifacts/12856344914).
- [Strict CC-only candidate verification (NOT DEPLOYED)](https://github.com/Crking92/Hays-Botany-Asteraceae/actions/runs/40781698540) includes **154 photos across 112 species**, with zero noncommercial-only media and zero private/owner-authorized photos. Site release and repo-visibility safety checks remain.
- [Success: revalidate all 459 original photo paths/sha/rights](https://github.com/Crking92/Hays-Botany-Asteraceae/actions/runs/40781663334) confirms original count 323 copied, 136 source-held, zero unaccounted.
- [Success: exact 179-species family photo handoff gate](https://github.com/Crking92/Hays-Botany-Asteraceae/actions/runs/40782004868).

## Permanent new-family evidence
- [Final private photo handoff memo](https://github.com/Crking92/Hays-Botany-Asteraceae/blob/staging/asteraceae-metadata/migration/ASTERACEAE_PHOTO_PASS2_HANDOFF_20261028.md).
- [Machine-readable family handoff status](https://github.com/Crking92/Hays-Botany-Asteraceae/blob/staging/asteraceae-metadata/migration/asteraceae-photo-handoff-readiness-20261028.json).
- [All original 459 image paths and dispositions (CSV)](https://github.com/Crking92/Hays-Botany-Asteraceae/blob/staging/asteraceae-metadata/migration/asteraceae-full-image-asset-reconciliation.csv).
- [36 new Texas photo provenance entries](https://github.com/Crking92/Hays-Botany-Asteraceae/blob/staging/asteraceae-metadata/migration/asteraceae-new-texas-inat-cc-photo-ledger.json).
- [Last-three Kew taxonomic synonym decisions](https://github.com/Crking92/Hays-Botany-Asteraceae/blob/staging/asteraceae-metadata/migration/asteraceae-last-four-taxonomic-photo-decisions.json).

## Exit decision and next lane
**Recommended: move active content/photo collection attention to Fabaceae next**, treating Asteraceae as **private learner photo-migration complete enough to maintain**. The owner still needs to review the actual visual sample before a production site release. Asteraceae maintenance backlog includes:
1. Exact valid variety image or permission for `Pectis angustifolia var. fastigiata`.
2. 136 intentionally source-held original media needing rights/identity review only where material diagnostic improvements warrant it; 29 external reference URL archival decisions; 11 archived unlinked originals intentionally held.
3. Complete genus-level teaching module migration, glossary/quiz routing and anatomy arrow accuracy audits before declaring full production quality.
4. Separate public GitHub Pages safety audit: new repository is PRIVATE and stores NC and author-authorized photos, including in Git history; never simply flip it public or deploy all originals.
5. Explicit approval, public release rollback plan and hub routing updates. Main original source and `PROJECT_RULES.md` / `workflow/COORDINATION.md` remain unchanged.

**Caution:** 179/180 means at least one source-backed photo per species, NOT 179 full 6-role diagnostic galleries or verified anatomy annotations. The nonpublished strict CC-only candidate has 112/180 species with images, so public-ready media coverage still requires a separate rights and source strategy.
