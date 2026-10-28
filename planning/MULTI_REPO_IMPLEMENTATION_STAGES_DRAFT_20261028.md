# Hays Botany multi-repository setup — planning draft (2026-10-28)

**STATUS: PLANNING ONLY.** Do not treat this note as an active project rule, site routing change, automation restart, migration approval, or ownership transfer.

## Agreed direction
- Original `Crking92/Hays-County-Botany` remains the main hub, universal species search, shared glossary, universal quiz, approval dashboard and local launcher.
- Option B: separate GitHub Pages websites for each collection, linked with near-identical current Hays Botany visual presentation. The normal act of clicking into another website is acceptable.
- Ten planned collection repositories; `Hays-Botany-Poaceae` already exists as uncutover staging, nine additional empty repositories to create.
- 146 existing families assigned to one future destination each, covering 1,191 installed species. Exact map: [MULTI_REPO_FAMILY_ROUTING_DRAFT_20261028.json](MULTI_REPO_FAMILY_ROUTING_DRAFT_20261028.json).
- Approximately 150 species per repository is a **soft** target, not a guarantee of storage capacity or completeness. Asteraceae starts with 180; assess bytes and photo count before any split.
- No new taxonomic range policy is implied. Existing BONAP-first source policy and native/introduced/invasive evidence labels stay intact.

## Stage 1: establish destination repositories
Create the nine not-yet-existing repositories under the current `Crking92` account, preferably **private initially**, with README and no blanket license or copied template. Do not import photographs, enable Pages or run scheduled automations yet. Check GitHub app access for new repositories. Keep Poaceae and hub unchanged.

## Stage 2: common skeleton and stable IDs
Prepare standard folders and validation workflows in each new repository, starting with an empty taxonomy index. Do not move canonical files yet. Shared design source comes from the existing hub's presentational conventions; each collection builds a pinned tested version to avoid unrelated UI changes. Keep existing local Windows launcher and approvals working.

## Stage 3: catalog contract and Option B navigation
Each collection must export lightweight species metadata to the hub. A combined index must reject missing/duplicate IDs, mismatched family assignments, stale catalogs and broken links. Stable family deep links use `?species=<species-id>` (already supported by Poaceae beta). Main hub must route all-family search results to the correct live site or retain original-local fallback until publication. Shared nav should retain Learner, Field ID, glossary, iNaturalist gallery controls and a universal hub Quiz link. Browser Back and direct bookmarks must work.

## Stage 4: pilot family migration
Choose one pilot collection (Asteraceae is preferred). Transfer data against a pinned hub SHA, verify full species/genus/family records, photo hashes/rights metadata and source counts, and preserve exact originals in hub until cutover. No dual-authoritative writes; the main hub keeps authority during staging.

## Stage 5: independently release family website
Create strictly filtered published asset set; confirm actual source-specific photo rights, attribution, adaptation permissions, no restricted images in public repository history, correct anatomical arrows, mobile behavior, working links, content and quiz navigation. Only then publish **new** family Pages site. Do not modify original homepage/search until explicitly approved.

## Stage 6: reversible hub integration and source handoff
Verify new Pages live URL and source SHA, then add a narrow family-level routing entry to the hub. Keep old original fallback and rollback procedure. Change authoritative species editor and work-claims routing only after final synchronization and approval. Do not delete original history.

## Stage 7: repeat, then formalize rules
Repeat migration in manageable family collections. After pilot and workflow behavior are confirmed, revise `PROJECT_RULES.md`, `workflow/COORDINATION.md`, current card/rights policies and relevant automations together, retaining existing botanical, provenance and no-overwrite protections. Keep all previously paused ChatGPT grass automations paused unless explicitly requested.

## Explicitly unapproved
No switch of Poaceae into production; no migration of other families; no Pages activation or publishing; no rules rewrite; no automatic resumption, deletion or duplication of scheduled tasks.
