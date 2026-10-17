# Diagnostic photo handoff — Centaurea melitensis — 2026-10-16

Lane: Diagnostic Photo Fast-Fill; canonical enrichment only. Status: NEEDS_VISUAL_AND_LICENSE_REVIEW; **zero new physical images installed by this handoff**.

## Fresh canonical check
- Canonical manifest: `data/manifest.json` contains `centaurea-melitensis`.
- Existing species: `content/taxa/Asteraceae/Centaurea/centaurea-melitensis/species.json`.
- Existing physical JPEG: `content/taxa/Asteraceae/Centaurea/centaurea-melitensis/images/inat-352790294.jpg`; Git blob `fc05caa0b9723c6b7d56ed2baf910c40baf769b1`; JPEG bytes verified on `main`. Original iNaturalist photo 352790294, photographer credited `abounabatphone`, **CC BY-NC**; preserve attribution and noncommercial restriction. Existing gallery `images[]` contains this one entry; **do not replace it**.
- No current unexpired claim for this canonical species in `workflow/work-claims.json`. Historic unrelated/expired claims must not be overwritten.

## High-value missing views (NOT visually verified yet)
1. **Lateral flower-head macro:** show overlapping involucral bracts/phyllaries and terminal sharp spines clearly; useful against other yellow Centaurea species.
2. **Stem/leaf attachment:** narrow leaves, winged/spiny stem portions; confirm actual structures in pixels before teaching or arrow annotation.
3. **Mature head/fruit:** fruit and pappus if visible and diagnostic; no anatomy arrows until verified on exact photograph.

## Existing private photo-library leads (metadata ONLY; NOT installed)
Archive: private GitHub Release `hays-photo-library-mass-38984897722`, asset `mass-38984897722-photos.zip`; all are `ARCHIVED_PROVISIONAL_VISUAL_REVIEW_REQUIRED`.
- Photo ID `617773932`; Chet Burrier; archived **CC BY**; GBIF occurrence `6163010965`; file `staged_images/centaurea-melitensis/gbif-389481a865d61f.jpg`.
- Photo ID `624196392`; Salem De La Luna; archived **CC BY**; GBIF occurrence `6178705178`; file `staged_images/centaurea-melitensis/gbif-55efaae758409f.jpg`.
- Photo ID `623305860`; Salem De La Luna; archived **CC BY**; GBIF occurrence `6178721947`; file `staged_images/centaurea-melitensis/gbif-bd7ed56e49ff22.jpg`.
- Pl@ntNet via GBIF occurrence `5110512437`; Nieves Ortín; archived **CC BY-SA**; archive file `staged_images/centaurea-melitensis/plantnet-via-gbif-abd9de5be570a4.jpg`; original source image hash `811906dc606873b81bef338cc0008bd3a7e924f6` (NOT an iNaturalist photo ID).

## Next safe step
Download the actual archived JPEGs from the private Release; inspect pixels, exact-species identity, and complementary diagnostic anatomy; confirm **individual image** license and photographer at original source (do not infer from occurrence license). Select one genuinely complementary view, add physical JPEG to the canonical images directory, **append** `images[]` metadata and provenance without replacing the existing CC BY-NC image, and read back JPEG + gallery from GitHub `main`. If none passes, leave this handoff unresolved and choose another unclaimed one-photo canonical taxon. No new species installation, native-range/taxonomy/website changes, or public-use upgrade.
