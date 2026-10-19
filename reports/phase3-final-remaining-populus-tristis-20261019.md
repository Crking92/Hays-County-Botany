# Phase 3 — remaining alternative-taxonomy concept: Populus tristis
Date: 2026-10-19
Status: HOLD — explicit accepted-name backbone decision required, **not a photograph problem**.

## Current verified result
After successful GitHub first-card runs manual-five-synonym-20261019-b008, b009 and b010, **1,184** canonical learner cards are in data/manifest.json; **1** of the original Phase 3 concepts remains unrepresented by exact slug.

The source pool uses **Populus trichocarpa Torr. & A.Gray ex Hook.** (black cottonwood), while the reconciled phase3 accepted destination is **Populus tristis Fisch.** (slug `populus-tristis`). The preflight decision is `CONFIRMED_KEW_TARGET_WITH_ALTERNATIVE_TAXONOMY_CAUTION`. The installer deliberately does not treat this as an unconditional pass and has not created a learner species card.

## Authoritative name evidence
- Kew POWO treats **Populus tristis** as accepted and **Populus trichocarpa** as its synonym: https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:776895-1
- Kew lists the alternate **Flora of North America** treatment under **Populus trichocarpa** on its synonym-name page: https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:208350-2
- USDA's National Agricultural Library agricultural thesaurus uses **Populus trichocarpa** as the preferred taxon: https://lod.nal.usda.gov/nalt/en/page/17743
- USDA plant guide also uses the familiar black-cottonwood name **Populus trichocarpa**: https://plants.usda.gov/DocumentLibrary/plantguide/pdf/cs_pobat.pdf

### Geographic caution, not a county nativity audit
Kew's taxon-page native distribution lists western North America and Baja California Norte, not Texas. Do not infer a Texas native occurrence or use a photo of a tree growing in Texas as proof. County-specific native-range certification remains paused per user direction. No invasive/exotic categorization has been made here.

## Suggested final resolution
Review the project's **scientific-name backbone priority**, whether this widespread western black cottonwood source-pool row is intended in the Central Texas **learner** at all, and whether the alternative-taxon caution may be released. If the project explicitly chooses POWO accepted names here, map `Populus trichocarpa` as an alias to one provisional `Populus tristis` card; if an FNA/USDA backbone is preferred for this genus, retain or approve `Populus trichocarpa` as the working display name. In either case require a properly credited exact-species photo and avoid duplicate taxa. **Do not force an installation until that decision is recorded.**

## Integrity checkpoints
- GitHub Action successful: https://github.com/Crking92/Hays-County-Botany/actions/runs/39273849350 (4 installed, one taxon hold)
- GitHub Action successful: https://github.com/Crking92/Hays-County-Botany/actions/runs/39274800446 (3 installed; cactus photo candidates unresolved)
- GitHub Action successful: https://github.com/Crking92/Hays-County-Botany/actions/runs/39276030515 (2 exact-source Commons cactus photos installed; original GPS/EXIF stripped)

All nine Phase 3 additions across these three latest batches are credited one-photo provisional cards. Image-level diagnostic character certification and detailed galleries remain future work, distinct from the first-photo install count. Existing automations and disconnected Cloudflare stay untouched.
