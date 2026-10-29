# Hays Botany — multi-repository operating rules (2026-10-28)

**Status: ACTIVE coordination instructions for staging and manual curation. NOT authorization to enable Pages, publish a family website, change the live hub, transfer canonical ownership, unpause automations, change repository visibility, or copy restricted photos.**

**Current user priority — EXISTING ASSETS FIRST:** First preserve all original source/data/photo bytes, then defer additional photo harvesting, species expansion, anatomy polish and per-family publication QA until the user selects that family for renewed work. See [migration-first existing asset handoff](MIGRATION_FIRST_EXISTING_ASSETS_HANDOFF_20261028.md). Keep all photo-rights, private archival and one-writer protections; unknown-rights photos may be privately archived but MUST NOT be copied into a public repo without clearance.\n\nThis document supplements [PROJECT_RULES.md](../PROJECT_RULES.md), [workflow/COORDINATION.md](COORDINATION.md), [workflow/ACTIVE_CARD_MODE_20261020.md](ACTIVE_CARD_MODE_20261020.md), and the [photo reuse policy](PUBLIC_PHOTO_REUSE_POLICY_20261019.md). It overrides older *single-repository workflow assumptions* only where they conflict with the staged multi-repo layout; all scientific, rights, arrow, review and safety protections remain in force.

## Repository topology and authorities

- **Current canonical botanical records and production site:** `Crking92/Hays-County-Botany`; its established GitHub Pages learner remains the public fallback.
- **Proposed separate public hub:** `Crking92/Hays-Botany-Public`; a browsable static preview and source-index staging files now exist (1,191 source species, 146 families, 10 planned collections). This is NOT the canonical production website and is not an approved family routing/ownership cutover. Family collection buttons must reflect private-transfer / not-live states until explicit release.
- **Family-group staging destinations:** `Hays-Botany-Poaceae`, `Hays-Botany-Asteraceae`, `Hays-Botany-Fabaceae`, `Hays-Botany-Monocots-Aquatics`, `Hays-Botany-Lamiales`, `Hays-Botany-Asterid-Allies`, `Hays-Botany-Cacti-Buttercups`, `Hays-Botany-Spurges-Mallows`, `Hays-Botany-Trees-Shrubs`, and `Hays-Botany-Mixed-Families` (all under `Crking92`).
- See [family-to-destination registry](../planning/MULTI_REPO_FAMILY_ROUTING_DRAFT_20261028.json) for the family grouping. Its `PLANNING_DRAFT_NOT_ACTIVE` status means **no production routing or editor ownership has changed**. Consult current family source and destination states instead of inferring migration completion from repo existence.
- **One authoritative editor per species:** until a documented, separately approved family cutover, write accepted species/taxonomy/lessons to the original hub. Family repositories may hold verified, independently developed **staging** copies and curated previews; prevent unattended reverse/forward overwrites. After cutover, document new editor ownership and update automated workers together.

## Mandatory pre-write coordination for any chat, script, Action or worker

1. Identify species/family and correct destination from the family registry. Read this file, the destination `AGENTS.md`, relevant family README and the narrow target files. Existing-card work follows fast-card rules rather than repeating all legacy source-pool/range research.
2. Refresh live original-hub `main` SHA, `data/manifest.json`, `workflow/work-claims.json`, the target source paths and destination branch SHA. Check any competing manual chat/automation claim, staging manifest, pending batch, and latest already-merged changes.
3. Declare the lane **SOURCE_CANONICAL_EDIT**, **FAMILY_STAGING**, **PHOTO_PROVENANCE**, **READ_ONLY_QA**, **PRIVATE_TEACHING_ARTIFACT**, or **PUBLIC_RELEASE**; never infer permission to make another type of edit.
4. For copied files, retain pinned original path/blob SHA and compare exact source vs destination. If the source changed since the pinned migration SHA, re-audit and merge explicitly; never blindly overwrite the newer source or count stale inventory as current.
5. Write in small, narrowly scoped commits against fresh blob SHAs and verify readback. If a claim/permission/merge gate rejects an edit, record a precise manual handoff rather than bypassing it. No simultaneous writes to the same file by different chats.
6. Report separately **source committed**, **staging copied**, **bytes archived**, **website eligible**, and **actually deployed**; a GitHub commit, passing preview or rights ledger never alone proves public visibility.

## Photo and learning requirements (unchanged, enforced across repositories)

- Morphology-first, beginner-friendly, real-photo-led Field ID and Learner. Prefer Hays/Central Texas diagnostic evidence, true attachment/scale views, clear arrows only on visibly verifiable structures, accurate look-alike comparisons and glossary cues; preserve genus/family lessons.
- For each image preserve exact taxon, original creator, original/source URL, original license or precise permission scope, media bytes and hash when practical, visible credit, adaptation/arrow rights and changes. No license invention, implied Joey/Glass Root redistribution, inaccurate anatomy or CC relabeling. Glass Root Garden owner-created pictures must be credited per the documented permission.
- **Private staging is not publication.** Restrict unclear rights, unusable crops and untraceable credit. Public repository *history* can expose files even if GitHub Pages filters them; review before making an image-containing repo public or copying restricted files to a public repo.
- A strict **CC-only release candidate** may intentionally exclude NC and individual site-permission photos; the existing **noncommercial educational site** has its own conditional, image-specific NC and permission criteria in the governing photo policy. Never treat preview counts as a public-rights clearance.
- Keep photo status distinct: `SOURCE_ACCOUNTED`, `PHYSICALLY_ARCHIVED`, `VISIBLE_PRIVATE_PREVIEW`, `PUBLIC_WEB_ELIGIBLE`, `ACTUALLY_DEPLOYED`, `NEEDS_DIAGNOSTIC_PHOTO`, `NEEDS_PUBLIC_PHOTO`, `ANATOMY_ARROW_VERIFIED`, and `FIELD_READY_WITH_GAPS`. A photo count does not equal finished anatomy.
- Do not delete originals, silently replace creator/permissions, add fabricated arrows or force an all-rights-reserved/private-only image into a public card merely to reach 100%.

## Common website contract

The approved Option B is **separate collection websites with a consistent appearance**, linked through a main hub. Preserve current visual language and functioning Learner, Field ID, Quiz (hub-wide quiz link), search/deep links `?species=<stable-species-id>`, glossary and iNaturalist photo controls, mobile swiping, credits and image loads. Keep back navigation and original-site fallback functional; resolve cross-family look-alikes through hub/collection links. No independent redesign or broken master search.

## Release and cutover (requires separate approval)

A FAMILY_STAGING pass may add copied science, independently verified rights-cleared media and preview QA, but **must not** enable Pages, make a private repository public, re-route the original site or assert a new source of truth. Release requires:
1. Reconcile pinned source against latest hub, full species/genus/family inventory, stable IDs and duplicate-free family catalog.
2. Verify full output/media rights **and public repository history**, actual photo bytes, attribution/source links, adaptation notices, excluded private images and EXIF/GPS policy.
3. Inspect real diagnostic imagery/arrow targets and family/genus/scientific content; record honest unresolved roles and species/photo holds.
4. Pass desktop/mobile screenshots or browser tests, deep links, Learner/Field ID/glossary/quiz/cross-family navigation and local fallback.
5. Record tested build SHA, deployment SHA, owner approval, reversible hub routing, rollback path, and explicit one-writer handoff *before* any canonical cutover.
6. Keep original source files/history and working old URLs intact until separately approved cleanup.

## Automation and chat coordination snapshot

At the 2026-10-28 audit, **all 11 existing ChatGPT automations were paused**, including five grass-specific workers and the older family/genus workers. Their stored prompts may still say `KEEP ENABLED`; those are stale prompt text, **not instructions to activate them**. Never create, start, reconfigure or resume scheduled work without a fresh user instruction. Continue manual staging and disjoint grass lanes with live GitHub claims, not from presumed active schedules.

See [ACTIVE_CHAT_HANDOFFS_20261028.md](ACTIVE_CHAT_HANDOFFS_20261028.md) for cross-chat work and dated counts. That snapshot is not a durable proof of future progress; the latest GitHub README, ledger, SHA and Action win. Chat transcripts are not edited by changes to this file; each continuing chat should read these rules before its next write.

## Scientific scope preserved

Original learner admission remains encounter-first including introduced/invasive comparison species when scientifically justified. Range research is distinct; do not invent nativity, silently change accepted names or reopen paused county-native fast-fill. When user explicitly needs native-range certification use BONAP/NAPA first, with recorded target-zone counties. Keep source taxonomy, aliases/hybrids and hold decisions intact.
