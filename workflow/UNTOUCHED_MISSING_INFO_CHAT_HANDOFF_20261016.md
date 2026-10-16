# Untouched / sparse-information Master Pool research — other manual chat handoff
**2026-10-16 | Research lane only | User-directed**

## Goal
Another ChatGPT project chat should work on **uninstalled Master Plant Pool plants with little or no learner-ready science, visual-ID explanation, or verified photo-source evidence**, so the separate first-card installation chat/Approved Taxa Installer can move new species quickly into the learner. The other chat **does not** create new canonical `species.json`, curation-inbox `READY` markers or GitHub installation workflows for taxa the installer owns.

### Critical clarification
- `data/manifest.json` currently contained **635** canonical cards at the dated Oct 16 snapshot. The Master Pool has **1,282 source-name rows**, which are **not** 1,282 distinct future species: aliases, ranks and holds exist. Refresh the live manifest before any count.
- `workflow/UNINSTALLED_MASTER_POOL_FIRST_CARD_CHECKPOINT_20261016.json` identifies 77 uninstalled, unclaimed species in a **100-candidate preflight subset** on that date. Of those, 74 had **zero Joey inventory metadata**—that alone **does not mean zero photo options or zero botanical information**. Determine missing content per species honestly.
- Full future mapping and exception review: `research-drafts/reconciliation/phase3-consolidated-card-workload-2026-10-15.json`. Verify accepted identity and duplicate aliases; do not brute-force a new card for every raw name.

## Assignment and boundaries
1. Read `PROJECT_RULES.md`, `workflow/COORDINATION.md`, `workflow/FIRST_CARD_MULTISOURCE_POLICY_20261016.md`, `workflow/LEARNER_FAST_FILL.md`, `workflow/photo-library/README.md`, manifest, claims, research queue, phase3 routing, preflight checkpoint and previous drafts.
2. Prioritize **5–10 genuinely uninstalled and under-documented** source-pool concepts per manual batch, not merely plants lacking Joey images. Evaluate existing drafts/provenance and avoid plants already claimed for scientific work or currently being installed. Work an unclaimed species only; respect installer and other scientific/photo lanes. A `research_only` claim can be narrow to a species+phase.
3. For each plant, confirm accepted scientific name, family and genus against POWO/WCVP or relevant flora; map synonyms/accepted varieties correctly. A name that already resolves to an installed canonical card becomes an alias-reconciliation handoff, not another plant.
4. Research the plant's most useful **observable** morphological identification features (phyllotaxy, leaf blades, flower parts, inflorescence, fruit/seed, stems, distinctive measurements), simple LOOK HERE FIRST clue, encountered habitat/season when verified, and just the realistic regional confusers for which actual separating characters are supported. Mark uncertain claims and taxon-concept holds; no invented traits.
5. Search the **existing permanent photo library first**, user's own iNaturalist/photo archive second, Joey third, and properly licensed other exact-species iNaturalist/GBIF/Wikimedia/public-domain images afterward. For each promising image, record photographer, precise individual license/rights, observation/photo/source IDs, source page, actual image URL, intended anatomical role and *whether bytes have actually been downloaded and checked*. A candidate URL alone is not an installed photo. If missing, assign `NEEDS_FIRST_PHOTO` with attempts and precise needed role.
6. Save durable `research-drafts/untouched-first-card-research/<batch-id>.json` or Markdown with **one record per source-pool taxon**, source URL/evidence/caveat, ready-for-installer vs identity-HOLD vs needs-image, and the original source row/alias. Preserve existing science/range data. Do not add unlicensed media or merge with someone else's ongoing claims.
7. The installer will later select a **single real, verified, legally usable** exact-species photograph, build a provisional card and verify GitHub manifest/physical gallery. Photo perfection, three-photo minimum and exhaustive county-native review are deferred. No direct changes to formula-owned Master Plant Pool cells.
8. Re-fetch GitHub after committing, report exact commit/paths, resolved records and remaining blockers. Continue with next eligible research batch; skip claimed/duplicate/unresolvable plants without declaring them done.

## Initial research candidates to evaluate, not preapproved claims
These are examples from the dated preflight shortlist with no Joey inventory match, **not confirmed to lack information**; immediately refresh claims and available evidence before taking any:
- `Aphanostephus riddellii`
- `Boltonia diffusa`
- `Buchnera americana`
- `Corallorhiza wisteriana`
- `Desmodium paniculatum`
- `Desmodium psilophyllum`
- `Desmodium sessilifolium`
- `Galium texense`
- `Galium virgatum`
- `Geum canadense`
- `Eleocharis atropurpurea`
- `Eleocharis geniculata`

Any source-name/identity ambiguity goes to taxonomy name lane as `HOLD_IDENTITY`; a photo gap goes to installer/media handoff as `NEEDS_FIRST_PHOTO`. Do not accidentally call the 74 taxa 'empty cards'—they are *uninstalled names in the preflight queue*, and many may have source material not yet assembled into a learner card.

## Copyable starter instruction for other chat
> Continue my Hays County Botany project using `workflow/UNTOUCHED_MISSING_INFO_CHAT_HANDOFF_20261016.md` and `workflow/FIRST_CARD_MULTISOURCE_POLICY_20261016.md`. Your job is to research **uninstalled Master Plant Pool plants with sparse or missing learner content**, 5–10 unclaimed taxa at a time. Check current manifest/claims/drafts, resolve the accepted taxon and synonyms, add trustworthy LOOK HERE FIRST morphology and realistic look-alikes, and find photo candidates from the permanent library, my iNaturalist, Joey, or other rights-cleared sources. Save verified research and NEEDS_FIRST_PHOTO handoffs to GitHub for my other chat/Approved Taxa Installer to turn into first learner cards. Do not make duplicate cards, curation READY markers, native-by-county determinations or overwrite the other five automation lanes. Give exact committed links and counts.
