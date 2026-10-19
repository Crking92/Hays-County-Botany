# Phase 3 — Populus tristis final accepted-name resolution

## RESOLVED — final black cottonwood installation (2026-10-19)

**Outcome: completed** after the historical HOLD review below. Main-branch `data/manifest.json` contains **1,185** canonical learner cards and **zero remaining unrepresented slugs** in the 633-concept Phase 3 reconciliation. This closes the **Phase 3 accepted-first-card pass**, not all visual anatomy curation, county nativity review, or the full 1,282-source-row universe.

- Installed canonical ID: `populus-tristis`; displayed name **Populus tristis Fisch.** under the project’s Kew POWO/WCVP working-name backbone.
- Searchable synonym and familiar Flora of North America name: **Populus trichocarpa Torr. & A.Gray ex Hook.** The documented alternative-taxonomic treatment is retained in `taxonomic_note`; no duplicate `populus-trichocarpa` card was created.
- Kew accepted name and synonym: https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:776895-1 ; FNA alternative: https://beta.floranorthamerica.org/Populus_trichocarpa .
- Exact botanical-name photo source: Wikimedia Commons `Populus trichocarpa new leaves in spring 2.jpg` by **Thayne Tuason** (https://commons.wikimedia.org/wiki/File:Populus_trichocarpa_new_leaves_in_spring_2.jpg), under **CC BY-SA 4.0** (https://creativecommons.org/licenses/by-sa/4.0/). File decoded, JPEG resized to 1,800 × 1,202, EXIF/GPS removed, source license, author, original source page, modifications and `PUBLIC-WEB-CLEARED` permission scope persisted in canonical species and archived image-sources CSV. Reuse and adapted versions require CC BY-SA attribution, source/license links and ShareAlike treatment.
- **Native-range caution:** POWO lists western North America/Baja California Norte, **not Texas**. No Hays County native status is claimed and detailed county audits remain paused. No introduced/invasive badge is inferred without its own evidence.
- **Provisional learner only:** original photo represents spring leaves, not a verified set of mature leaf, catkin, bud and bark diagnostic views. Future photo-rich morphology polish should add separate credited reference shots and especially distinguish `Populus deltoides`.
- GitHub installation: [successful v2 first-card run](https://github.com/Crking92/Hays-County-Botany/actions/runs/39277911007); report `reports/manual-last-phase3-populus-20261019-v2-installed.json`. First source-format attempt was correctly blocked: `reports/manual-last-phase3-populus-20261019-installed.json`; no false first-attempt addition.
- Existing five scheduled workers unchanged; Cloudflare disconnected, Pages not enabled. This is verified **private GitHub data**, not confirmation of an updated public website.

---

### Historical hold analysis (retained for provenance)

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
