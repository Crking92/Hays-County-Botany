# Multi-repository setup report — October 28, 2026

**STAGE 1 SETUP COMPLETE; NO SPECIES HANDOFF OR WEBSITE CUTOVER.**
This report is historical setup evidence, not a replacement for active `PROJECT_RULES.md`.

## Verified state
- Main hub: [Crking92/Hays-County-Botany](https://github.com/Crking92/Hays-County-Botany), public and still authoritative.
- Existing Poaceae [staging collection](https://github.com/Crking92/Hays-Botany-Poaceae): separately populated, public, awaiting independent public-photo and anatomy gates. Not cut over.
- Nine other family collections were created by the owner, private, on `main`, and verified writable by the GitHub connection.
- Each new collection has `README.md`, `config/collection.json`, `data/collection-index.json` (initially empty), `scripts/validate_collection.py`, and a **nondeploying** validation workflow.
- All nine new collection validation Actions completed **success**. Their scripts detect family/ID mismatches, nonexistent/duplicate entries, or premature authority/publication flags; they do NOT check source photographic reuse or visual anatomy.
- The main hub has a [draft 146-family registry](MULTI_REPO_FAMILY_ROUTING_DRAFT_20261028.json) covering 1,191 baseline installed species, and an [implementation plan](MULTI_REPO_IMPLEMENTATION_STAGES_DRAFT_20261028.md).
- Hub family-routing audit completed **success**; it cross-checks the current installed species manifest against assigned collections and fails on newly unassigned families.
- [Option B website/data contract](OPTION_B_WEBSITE_AND_DATA_CONTRACT_DRAFT_20261028.md) records the agreed independent family-site approach, shared Hays Botany visual style and `?species=` deep links.
- Asteraceae has a first read-only, **unpublished**, zero-photo, zero-species website-shell prototype under `site/`. Its [static build](https://github.com/Crking92/Hays-Botany-Asteraceae/actions/runs/40716980388) passed. An additional desktop/mobile browser screenshot workflow is configured.

## Successful validation URLs
- [Hub family registry routing audit](https://github.com/Crking92/Hays-County-Botany/actions/runs/40716405982)
- [Asteraceae](https://github.com/Crking92/Hays-Botany-Asteraceae/actions/runs/40716081930)
- [Fabaceae](https://github.com/Crking92/Hays-Botany-Fabaceae/actions/runs/40716183823)
- [Monocots-Aquatics](https://github.com/Crking92/Hays-Botany-Monocots-Aquatics/actions/runs/40716186803)
- [Lamiales](https://github.com/Crking92/Hays-Botany-Lamiales/actions/runs/40716200802)
- [Asterid-Allies](https://github.com/Crking92/Hays-Botany-Asterid-Allies/actions/runs/40716205413)
- [Cacti-Buttercups](https://github.com/Crking92/Hays-Botany-Cacti-Buttercups/actions/runs/40716209469)
- [Spurges-Mallows](https://github.com/Crking92/Hays-Botany-Spurges-Mallows/actions/runs/40716217573)
- [Trees-Shrubs](https://github.com/Crking92/Hays-Botany-Trees-Shrubs/actions/runs/40716223296)
- [Mixed-Families](https://github.com/Crking92/Hays-Botany-Mixed-Families/actions/runs/40716228925)

## Remains intentionally unchanged
- Public original homepage and all links, quiz/glossary, local Windows server and approvals.
- Canonical source of botanical records and image files; no transfer into newly created private repositories.
- `PROJECT_RULES.md`, `workflow/COORDINATION.md`, operational photography/rights policy, and the five paused ChatGPT grass automations.
- Poaceae publication and original-hub cutover.

## Next stage
1. Review Asteraceae desktop/mobile prototype's visual layout and polish while retaining the current hub's look.
2. Build reusable shared learner shell with index, glossary/photo/Field ID contracts; do not blanket-copy photographs or import restricted media.
3. Inventory Asteraceae source species/family/genus records, image bytes and exact rights *before* migration.
4. Copy verified source into private Asteraceae staging with immutable source SHA and per-file validation, using explicit rights gates before any public repository or Pages deployment.
5. Once a pilot works, reuse it for the other eight collections, then revise active rules/automation ownership after explicit approval.

**No further user configuration is needed for initial repository setup.**
