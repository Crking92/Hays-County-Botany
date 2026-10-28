# Hays Botany Option B — cross-repository website and data contract (DRAFT)

**Status:** implementation proposal, not an active project rule, publication approval or ownership handoff.

## One public entry point, independent collection websites
- The existing Hays-County-Botany URL remains the primary homepage, all-plant directory, universal quiz, shared glossary, and single approval dashboard.
- Each of the ten collection sites (one currently Poaceae staging, nine newly initialized private) eventually gets its own separately published learner website.
- Browser navigation between sites is acceptable. The current Hays Botany colors, typography, visual photo-first lessons, anatomy arrows, search behavior, Learner, Field ID and glossary links should be visually consistent.
- Use accessible ordinary anchor links (not JavaScript-only faux buttons) between sites. Preserve browser Back, direct bookmarks and navigation with JavaScript disabled as far as practical.
- Family sites should provide a prominent "Search all Hays Botany plants" and "Return to main hub" link.
- For links into species lessons, standardize the query parameter `?species=<stable-species-id>`, already supported in Poaceae beta. Example shape (NOT YET DEPLOYED): `https://crking92.github.io/Hays-Botany-Asteraceae/?species=solidago-altissima`.
- A non-live collection must never be linked as a working website: keep an original-hub fallback URL until its Pages deployment and deep links are tested.

## Collection record and lightweight directory
- The canonical species JSON and physical images belong to a *single assigned collection after its explicit handoff*. Until then the original hub is authoritative; migration destination copies are staging.
- Every collection has `config/collection.json` with exact assigned families and a no-publish flag.
- Every collection has `data/collection-index.json` as an initially empty, read-only staging catalog. Proposed future export fields: `id`, `scientific_name`, `common_name`, `family`, `genus`, `path` and, after release, `public_lesson_url` plus the validated publication/source SHA. The index MUST be generated from approved canonical records, not independently edited.
- The hub will combine collection exports into a single, checked global search index. Reject missing/duplicate species IDs, mismatched family assignments, an announced published URL that does not resolve, or a changed source revision without validation.
- New families absent from the routing draft are held for explicit assignment first. Taxonomic family transfers require a documented ID/alias migration and redirects to avoid broken bookmarks.

## Shared presentation without distributing photographic archives
- The shared design layer should be pinned by version and tested on both desktop and mobile; keep layout consistent across family sites even when the content differs.
- Photo gallery, source/creator/license credit, navigation, arrow/numbered anatomy legend and glossary links remain consistent.
- Route external cross-family comparisons to the right site without duplicating photographers' image bytes merely for comparison.
- Crop/resize/overlay derivative rights and individual public media license must be validated per image. Private repos are not evidence of legal rights.
- Make every site a stand-alone deployable filtered snapshot; no family site should be built by copying the whole main repository or another family's photographs.
- Universal quiz stays in the hub at first; later family-specific quizzes can link back without breaking existing scores/experience.
- The present Windows local server and approvals workflow remain at the hub until a tested multi-repo coordination mechanism exists.

## Release gates
1. Repository exists and family config validates.
2. Transferred species/family/genus records and all linked data are checked against pinned authoritative SHA.
3. Public image set is independently source-rights reviewed; public repository raw history contains no unauthorized media.
4. Fine anatomy arrows are visually reviewed on the actual source photographs (coordinate bounds alone are insufficient).
5. Build static Pages snapshot with known version and correct attribution, no restricted source records or private metadata.
6. Test mobile/desktop, navigation, deep links, external citations, quiz and glossary.
7. Verify real public Pages URL and publication SHA; only then add hub routing.
8. Keep original fallback and ability to roll back; resynchronize immediately before changing canonical authoring ownership.

## Setup completion checkpoint (October 28, 2026)
- Nine new private repos initialized with README, exact family configs and empty catalogs.
- Each has a nonpublishing GitHub Actions collection validator and the initial check passed.
- Main hub has [family map](MULTI_REPO_FAMILY_ROUTING_DRAFT_20261028.json), [implementation stages](MULTI_REPO_IMPLEMENTATION_STAGES_DRAFT_20261028.md) and a passing nonpublishing routing audit.
- Existing main website, data owner, Poaceae migration and scheduled ChatGPT automations unchanged.
- Next engineering milestone is a **shared learner shell prototype** in Asteraceae, validated before copying the same shell to other collections. Then perform a source/rights audit and controlled first-family transfer.
