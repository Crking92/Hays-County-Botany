# Glass Root Garden — iNaturalist first photo shortlist (2026-10-14)

**Scope:** REVIEW ONLY; does not install or replace images in canonical species modules.
**Photographer:** Calvin King / public learner attribution requested: **Glass Root Garden**.
**Photographer's instruction in project conversation:** Use their personally owned images in the learner under **CC BY 4.0**, credited to Glass Root Garden. Do not apply this to anyone else's photos.

## Findings
- 2,431 public Research Grade Texas plant observations in `calvinking` API retrieval.
- 2,471 distinct iNaturalist photo IDs across 444 taxa.
- iNaturalist's **per-photo source attribution currently says "(c) Calvin King, all rights reserved"** and `license_code` was absent for all 2,471 photos as of the inventory run; the user's updated observation default license did not synchronize the photo-record license.
- Per-photo published licensing requires confirmation/reconciliation. These are private review samples, not publicly redistributed images.
- 16 staged previews for each of three high-need installed species.

## Photos manually reviewed in private preview contact sheets

### Twistleaf yucca — `yucca-rupicola` (1 existing canonical photo)
- [Photo 607698000](previews/yucca-rupicola/inat-607698000.jpg): Strong patch/habit photo showing many rosettes and surrounding habitat. **KEEP CANDIDATE** for whole-plant/colony concept.
- [Photo 623378710](previews/yucca-rupicola/inat-623378710.jpg): Good isolated leaf rosette, narrow leaves and twist apparent. **KEEP CANDIDATE** for leaves/rosette close context.
- [Review contact sheet](previews/yucca-rupicola-contact-sheet.jpg).
- Missing: leaf edge/fiber true macro, inflorescence and fruit, direct Yucca comparison.

### Shrubby croton — `croton-fruticulosus` (1 existing canonical photo)
- [Photo 573059048](previews/croton-fruticulosus/inat-573059048.jpg): Hand-held leaf and shoot detail; useful, but needs full-resolution botanical confirmation. **KEEP CANDIDATE** for leaf attachment and foliage.
- [Photo 623379901](previews/croton-fruticulosus/inat-623379901.jpg): Leafy woody branch including small reproductive structures; visually promising, tiny parts need macro. **KEEP CANDIDATE** for foliage/branch context.
- [Review contact sheet](previews/croton-fruticulosus-contact-sheet.jpg).
- Missing: leaf hairs/magnification, separate male/female flower images and mature capsule.

### Agarita — `berberis-trifoliolata` (1 existing canonical photo)
- [Photo 615488527](previews/berberis-trifoliolata/inat-615488527.jpg): Usable overall shrubby habit in habitat, but far from botanical parts. **SUPPORTING CANDIDATE** only.
- [Photo 559565073](previews/berberis-trifoliolata/inat-559565073.jpg): Spiny foliage present, but multiple plants intermixed. **LOWER PRIORITY**; prefer diagnostic macro on a clean branch.
- [Review contact sheet](previews/berberis-trifoliolata-contact-sheet.jpg).
- Missing: one isolated trifoliolate leaf, sharp leaflet tips, flower/berry closeup.

## Next gate before installation
1. Update/verify the iNaturalist **photo** license (not merely observation license), or record the photographer's direct CC BY grant as an authorized source separately; never misdescribe iNaturalist's existing source license.
2. Download selected images at the best available resolution and compare against existing species-card images; do not replace a better diagnostic photo.
3. Verify taxon identity and visible structures on uncropped pixels, choose accurate botanical captions and arrows; add original iNaturalist observation/photo links.
4. Update species `images[]` through the established photo pipeline. Only then verify binaries, rendering, licensing and GitHub commit.
