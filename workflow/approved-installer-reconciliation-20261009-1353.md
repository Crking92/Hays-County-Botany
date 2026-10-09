# Approved Taxa Installer — verified reconciliation (2026-10-09 13:53 CDT)

## Canonical installation
- `data/manifest.json` contains 452 taxa, including `boerhavia-coccinea`, `boerhavia-erecta`, and `boerhavia-linearifolia`.
- The three species files are installed under `content/taxa/Nyctaginaceae/Boerhavia/` and each references one licensed exact-species photo; `images/` directories exist.
- Each preserves `project_inclusion.target_zone_status: UNRESOLVED` and `learner_role: RANGE_UNRESOLVED`; none should enter confirmed-native counts.
- GitHub Action 37970816247 completed successfully on merge commit `1bea1723b492b6fd26043115f6594d2ed719de24`.
- `research-queue.json` contains 278 items with no ordinary approved/ready-for-curation backlog.

## Reconciliation requiring file update
- `research-drafts/bothriochloa-laguroides/draft.json` still says `SCOUTED_RESEARCH_ONLY`, while canonical `content/taxa/Poaceae/Bothriochloa/genus.json` maps historical Texas source usage to `bothriochloa-torreyana`. Close the *historical source usage* as `represented_existing_no_new_card`, without asserting `B. laguroides` sensu stricto is synonymous with `B. torreyana`.
- `workflow/work-claims.json` has an expired `automation-family-similarity-verbenaceae-20261009-1011` active claim. Canonical `content/taxa/Verbenaceae/family.json` contains version `1.1-recognition-confusion-polish`; release the completed claim after confirming no later ownership.
- Attempts to update these existing files were blocked by GitHub connector write safety checks; do not mark either correction complete without verifying a later commit.

No Google Sheet spill or formula ranges were modified.
