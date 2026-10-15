# Phase 2/3 – Source pool → canonical learner reconciliation
**Snapshot:** 2026-10-15 | **County-native range fast-fill:** PAUSED

## Counts reconciled against live GitHub + Google Sheet
- **1,282** distinct Master Plant Pool source-name rows; **552** installed species in `data/manifest.json` (each has one matching Species Tracker canonical ID).
- **576 source rows already represented by installed canonical concepts:** 519 exact accepted scientific names, 26 Species Tracker original source-name links, 24 previously verified external source-name aliases, 7 newly reconfirmed existing accepted-species mappings.
- **706 source rows still needing a decision:** **400 accepted-binomial evidence preflights**, and **306 exception/rank/synonym/identity records**.
- The 400 were selected from **404** qualifying source rows; **4 were reserved under active work claims** and excluded from these manual preflight batches. All 400 are **NOT READY FOR AUTOMATIC INSTALLATION** until a canonical name/synonym check, source concept, actual image rights, and current installer state are checked.
- **Counts are source-name rows, not a guaranteed number of distinct new species cards.** Do not interpret 706 as the final card count or subtract installed cards from this source-row inventory.
- Reconciliation unit check: **569 + 7 + 400 + 306 = 1,282**, with no duplicated or missing source rows in the six durable reports.

## Durable inputs
1. Full 1,282-row crosswalk: `research-drafts/reconciliation/phase2-master-pool-canonical-routing-2026-10-15.json`
2. Accepted-name preflight tranche 1, 120 rows: `research-drafts/reconciliation/phase2-reviewed-uninstalled-candidates-2026-10-15-b001.json`
3. Accepted-name preflight tranche 2, 120 rows: `research-drafts/reconciliation/phase2-reviewed-uninstalled-candidates-2026-10-15-b002.json`
4. Accepted-name preflight tranche 3, 160 rows: `research-drafts/reconciliation/phase2-reviewed-uninstalled-candidates-2026-10-15-b003.json`
5. 313 original exception records (before 7 were confirmed installed): `research-drafts/reconciliation/phase2-remaining-source-concept-routing-2026-10-15.json`
6. Seven newly confirmed aliases to installed cards, including canonical file checks: `research-drafts/reconciliation/phase2-verified-installed-aliases-2026-10-15-b001.json`

## Next work, in priority order
1. **Approved Taxa Installer:** Recheck a coherent **8–12-source-row** set from the three accepted-name preflight reports against fresh manifest, claims, existing drafts and inbox, rank/parent concepts and image licensing. Only genuine distinct accepted taxa become new canonical species; source synonyms map to a single card. Source-pool approval suffices for admission even if local native county status is deferred.
2. **Phase 3 synonym reviewer:** Of the 306 residual records, prioritize the **17 proposed aliases to another uninstalled pool source name**. Confirm accepted concept, parent and rank before merging. Also prioritize the **60 source records whose proposed accepted target name is not itself a source-pool row**: the accepted name may become the card destination, while the historical source remains a searchable alias. These are *candidate mappings*, not confirmed equivalents.
3. For the remaining exceptions, prioritize 10 infraspecific/parent questions and missing backbone evidence. Preserve identity/concept holds. Never flatten an accepted variety/subspecies to a parent automatically.
4. **Canonical card owner**: `Dracopis amplexicaulis` is a verified homotypic synonym of existing `Rudbeckia amplexicaulis` (Kew POWO `https://powo.science.kew.org/taxon/202167-1`). Its existing canonical species.json lacks the Dracopis name under synonyms. Add the search alias in the canonical edit lane; **do not install a second card**. The other six newly confirmed aliases were already in their target canonical cards.
5. Photo lane: prioritize zero-physical-image canonicals and one-face image installs, then diagnostic macro and look-alike polish; separate photo-science from source-row name reconciliation.

## Scope and safety
- This snapshot compares the live **Master Plant Pool**, **Species Tracker**, and **data/manifest.json**; it is not a second independent Kew review of all 1,282 plant names.
- No native-by-county data, existing family/genus lessons, species.json, manifest, source observations or image metadata changed during the six-report reconciliation.
- Source names and rejected/provisional taxon concepts remain archived. Do not change derived **Master Plant Pool** cells directly; write only via permitted source/override or proper canonical-owner workflows.
- The two legacy combined pending taxonomy/range labels at the time of earlier audit were **Malvaviscus arboreus** and **Zizania texana**, already reserved for Joey reconciliation; do not force them through the general installer.
- Recompute counts after the installer adds new species; the 2026-10-15 inventory is a dated baseline, not a live ticker.
