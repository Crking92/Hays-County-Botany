# Hays Botany Work Coordination

This file defines the shared anti-duplication protocol for all ChatGPT chats, automations, local tools, and manual project work.

## Authoritative state order

Before selecting any new work, refresh from `main` and check these sources in order:

1. `data/manifest.json` — canonical installed truth. If a taxon ID is here, do not research or install it as a new taxon.
2. `workflow/work-claims.json` — reservations for work that another chat/process has claimed but may not have written elsewhere yet.
3. `research-queue.json` — queued, reviewed, approved, held, rejected, and historical species workflow state.
4. `research-drafts/` — existing scout/research work. Reuse or improve the draft instead of creating a second draft.
5. `curation-inbox/` and current GitHub Actions — work already entering the canonical pipeline.
6. The relevant family/genus/website/video workflow files for non-species work.

If any source shows the same taxon or scope is already being worked at the same stage, skip it and choose another target unless the existing claim explicitly names the current process as a collaborator.

## Claim-before-work rule

A chat or automation must create or refresh a claim in `workflow/work-claims.json` before beginning substantial work that is not already represented by a queue record, research draft, curation-inbox batch, or other persistent workflow artifact.

Claims are especially useful during the gap between “I chose this target” and “I wrote the first durable project file.”

Use a claim for:
- species scouting/research
- deep review
- curation/package construction
- family backfill/module construction
- major website structural work
- video/species reconciliation

Do not create a second claim for work already durably reserved by the queue/draft/inbox unless a stage-specific claim is needed to prevent two workers from editing the same item simultaneously.

## Claim fields

Each claim should include:
- a stable `claim_id`
- `scope_kind`
- exact `taxa`, `families`, or `scope_key`
- `lane`
- `owner`
- `status`: `queued`, `active`, `blocked`, or `released`
- `claimed_at`
- `expires_at` for short-lived active claims when practical
- a short `release_when` rule
- notes when needed

## Lease behavior

- Manual-chat active claims should normally expire after about 6 hours unless refreshed.
- Automation active claims should normally expire after about 2 hours unless refreshed.
- A deliberately queued reservation may use `expires_at: null`, but it must be ignored automatically if the taxon becomes canonical, appears in the research queue, gains a research draft, or is otherwise durably represented.
- Expired active claims may be reclaimed, but only after checking the authoritative state order above.

## Stage handoff

Typical species flow during Learner Fast-Fill:

`approved source pool → learner admission approved → taxonomy/ID review as needed → curation claim → curation-inbox → canonical manifest`

Scientific deep review may continue enriching taxonomy, range, morphology, and comparison metadata, but a three-county native-range audit is no longer required before a sheet-backed taxon enters the private learner.

**Source-pool learner-admission rule:** membership in Calvin's approved source pools or derived Master Plant Pool is durable user approval for learner inclusion. Preserve native-range PASS/FAIL/UNRESOLVED/CONFLICT separately. Range status controls labeling and native metrics, not admission. Only a genuine taxonomic identity/duplicate-concept problem should block creation of a separate species card; aliases or represented concepts should map to the existing accepted learner entry.

As soon as a later durable artifact exists, the earlier claim should be released or treated as superseded.

The unattended Scout stops at research drafts. Deep Review stops at review status. Curation/install workers own the curation inbox. Website and family workers do not silently promote species.

## Backpressure

The unattended Scout must not create an unlimited backlog. It should pause when either:
- 3 or more coherent noncanonical scout batches are still awaiting deep review, or
- 18 or more noncanonical species are waiting for deep review.

Deep Review should prefer coherent groups of 3–4 taxa, but may take a smaller 1–2 taxon remainder when that safely closes an otherwise stranded scout batch.

## Google Sheet derived-column ownership

Treat these Google Sheet ranges as formula-owned derived state unless a deliberate formula repair is being performed:
- `Master Plant Pool` body is spill/formula driven; do not hand-write its rows. Use source tabs and `_Master Pool Overrides`.
- `Family Study Index` columns B:K are live derived counts from `Master Plant Pool`. Family-content work may edit column A plus study-content columns L:Q, but must not replace B:K with snapshots.
- `Genus Study Index` columns C:M are live derived counts/anchors/status from `Master Plant Pool`. Genus workflows may add/repair family+genus keys in A:B, but must not overwrite C:M with static values.
- `Taxonomy Progress` live metrics and family detail B:E are derived; do not replace them with manual snapshots. The GitHub family-module count is the one external snapshot and should carry its sync date.
- `Species Tracker` summary canonical-count and accepted-name/synonym-note metrics are formula-driven; GitHub pipeline counts are dated snapshots.
- `Species Tracker` body rows A:Q are a one-row-per-canonical-concept mirror of `data/manifest.json`. Columns O:Q (`Canonical ID`, `Source Pool Name`, `Manifest Path`) are identity keys for reconciliation. Preserve detailed range/photo/license notes in E:N when refreshing the body; fold aliases into the accepted canonical row instead of adding duplicate tracker rows.
- Master Plant Pool formulas that consult `Species Tracker` must use expansion-safe tracker ranges (currently through row 1000), not the old row-300 cap.

## Master Pool write rule

- `Master Plant Pool` is a derived spill/output sheet. Never write review, curation, taxonomy, or species metadata directly into its body rows. Write species-level overrides/status into `_Master Pool Overrides` (or the canonical workflow artifact) and let the Master Pool formulas derive the row. Direct writes into the spill range cause `#REF!` failures and break taxonomy dashboards.

## Conflict rule

When two processes collide:
- canonical manifest beats everything;
- existing durable queue/draft/inbox state beats a new claim;
- an older/stale claim never authorizes overwriting newer work;
- if the same target file changed after a worker read it, refetch and rebuild or abort;
- if ownership is ambiguous, skip the target rather than overwrite another process.

## Current lane boundaries

- Species operations/curation owns canonical species installation.
- Unfinished Plant Scout owns research gathering only.
- Botany Deep Review owns independent scientific review only.
- Family Backfill owns family-level modules and audit material.
- Website/UI work owns presentation/interface files, not scientific source-of-truth data.
- Joey/video extraction and reconciliation may feed species/family research. Taxonomic identity remains authoritative; native-range review is descriptive metadata and is not an admission gate for source-pool learner taxa.

The goal is not perfect locking. The goal is to make duplicate effort and destructive overlap rare, obvious, and recoverable.

## Higher-taxonomy family backfill

As of 2026-10-03, the current Google Sheet Master Plant Pool has complete genus-to-family coverage: 612 distinct genera and 1,262 taxa resolve to 147 families. The workbook's hidden `_Genus Family Map` is the working genus→family lookup, and the visible `Taxonomy Progress` / `Taxonomy Hierarchy` tabs are the progress and filter views.

Do not start a second blanket genus→family reconciliation for the current pool. Family Backfill should now focus on the remaining family-recognition/index backlog, while preserving the 36 family lessons already marked Ready unless specific contrary evidence appears. New taxa/genus additions should receive a family mapping when added so the 147-family baseline can change transparently rather than triggering a full re-audit.

## Family batch strategy — lineage first

Family Backfill should prefer batches that share an order or close evolutionary lineage before simply taking the largest remaining families. The teaching goal is to learn both the shared inherited architecture and the characters that split related families.

Priority sequence:
1. Same order / close lineage, 3–5 families when practical.
2. Use already-built related families as comparison anchors rather than rebuilding them.
3. If an order has only 1–2 unfinished families, keep the batch smaller or pair with an immediately adjacent lineage only when the comparison is botanically useful.
4. Do not force unrelated families together solely to hit a batch size.
5. Every family lesson should state the lineage/order context and include at least one close-family tie-breaker.

Current lineage queue:
- Caryophyllales A: Amaranthaceae, Polygonaceae, Nyctaginaceae, Caryophyllaceae.
- Caryophyllales B: Portulacaceae, Talinaceae, Phytolaccaceae, Petiveriaceae, Plumbaginaceae, Tamaricaceae as present in the live pool.
- Brassicales: Brassicaceae + Cleomaceae, using the two-family contrast as the lesson.
- Gentianales: Gentianaceae + Loganiaceae + Gelsemiaceae, with existing Apocynaceae/Rubiaceae as anchors.
- Rosales: Rhamnaceae + Moraceae + Urticaceae, with Rosaceae/Ulmaceae/Cannabaceae as anchors.
- Malpighiales: Linaceae + Salicaceae + Violaceae + Hypericaceae + Phyllanthaceae, anchored against Euphorbiaceae/Malpighiaceae/Passifloraceae.
- Asparagales: Amaryllidaceae + Iridaceae plus any unfinished small Asparagales families, anchored against Asparagaceae/Orchidaceae.
- Dipsacales: Caprifoliaceae + Viburnaceae.
- Lamiales cleanup: Scrophulariaceae + Lentibulariaceae and any other unfinished Lamiales, anchored against the already-built Lamiaceae/Verbenaceae/Acanthaceae/Plantaginaceae/Orobanchaceae/Bignoniaceae/Oleaceae.


## Family audit completion semantics

Family-level audit completion is independent from species/genus curation counts and from visual/photo polish.

For Family Backfill target selection, use this order:
1. Refresh the family's current `content/taxa/<Family>/family.json` (or other durable family-module artifact) and the live `Family Study Index` row.
2. A family is **family-audit adequate / module live** when durable family material already covers the recognition lesson at a usable level: where to look first, shared characters, important local exceptions, confusable families/tie-breakers, diagnostic reproductive and vegetative structures, useful genus/species anchors, and remaining visual needs.
3. `Remaining`, `Priority 1/2/3 Remaining`, and other species/genus curation counts do **not** reopen a completed family audit. Those belong to species/genus lanes.
4. Photo perfection does **not** reopen a completed family audit. Exact missing macros, annotated comparisons, and better local images belong to visual-lock/photo-polish follow-up.
5. A `Backfill Status` stating that a visual/family recognition module is live, built, or a canonical family upgrade is live outranks legacy `Study Status` wording such as “Ready for family/genus batching.”
6. Joey coverage labels describe source sufficiency, not completion state: `Joey-sufficient`, `Joey + authoritative backfill`, and `authoritative-backfill-required` may all be family-audit complete once the required authoritative backfill is durably incorporated.
7. Reopen a family only for a real content gap, a taxonomy/circumscription change that affects the family lesson, a documented scientific correction, or a missing durable family artifact—not merely because species remain uncurated or photos need polish.
8. When all tracked families meet the adequate/module-live test, Family Backfill should report the audit backlog complete and make no unnecessary family changes. Remaining visual polish should be tracked separately.

Target selection must therefore prefer a genuinely missing/inadequate family module, not the family with the largest species backlog.


## Two-ended genus backlog strategy

After the family-recognition backlog is adequate, genus-level completion should use two complementary ends of the same live Genus Study Index instead of multiple workers independently choosing the same high-value genera.

- **Large-genus/manual lane:** manual project chats may work from the largest/high-complexity genera downward, especially coherent confusing groups that benefit from sustained attention.
- **Small-genus automation lane:** the former Family Backfill automation works from the smallest eligible genera upward, prioritizing genera with 1 remaining taxon, then 2, then 3, etc.
- Before every batch, both lanes must refresh `workflow/work-claims.json`, `data/manifest.json`, `research-queue.json`, relevant drafts/inbox artifacts, and the live Genus Study Index. Durable state or a claim always beats size ordering.
- Skip any genus/taxon actively or durably reserved by Joey/video reconciliation, Scout, Deep Review, curation, another genus worker, or a manual chat.
- Small-end batches should be coherent rather than random: prefer 3–5 related genera in the same family/order/close lineage, or a compact family-completion batch. Target roughly 3–8 unresolved taxa per run; smaller batches are acceptable when they close a family/genus cleanly.
- Within the same remaining-count tier, rank Priority-1 remaining first, then local observation/source strength, then whether the batch closes a genus/family teaching set.
- Do not promote species merely to complete a genus. Preserve PASS/FAIL/HOLD/UNRESOLVED and hand species-level work to the appropriate species lane.
- Scientific/genus audit completion and visual readiness remain separate status fields, but new genus batches must perform both in the same workflow whenever feasible. Do not label a new genus learner batch visual-complete if its species pages lack displayable images[]. Older canonicals may stay scientifically complete while entering the photo-recovery backlog.
- The two lanes meet in the middle. Once no eligible genus remains between them, report the genus backlog exhausted rather than recycling completed work.

Known collision examples at the time this rule was written: `Taxodium` and `Malvaviscus` have Joey reconciliation reservations and must be skipped by the small-genus lane until durable state releases/supersedes those reservations.

## Shared visual-priority rule — 2026-10-04

Every lane contributes to a visual learner. Before handing work downstream, preserve or gather the best available real-photo evidence for the diagnostic characters that lane has identified.

- Scout: capture photo leads, exact source pages/IDs, and diagnostic roles alongside research.
- Deep Review: verify that proposed images actually show the diagnostic structures and flag missing roles.
- Species/genus curation: install/wire displayable images[] and provenance; new text-only pages are visual-incomplete.
- Family Backfill: include real-photo anchors or explicit visual needs for recognition lessons; scientific audit status may remain separate from visual-ready status.
- Joey/video reconciliation: preserve exact timestamp/frame roles and taxon confidence as visual assets.
- Website/UI: render the canonical images[] and surface visual-incomplete status rather than hiding missing media.
- Photo Recovery: repair older canonical pages that predate the visual gate without unnecessarily reopening settled taxonomy/range decisions.

Real photos, local material, diagnostic closeups, arrows/labels, and side-by-side confuser comparisons are preferred in that order when they improve identification learning.

## Audit checkpoint — 2026-10-04

Queue and claims share the 5-batch/30-species unreviewed Scout ceiling. Count only genuinely noncanonical work awaiting independent review; reviewed approval/curation backlog is tracked separately. Completed draft reviews outrank stale pending queue labels. Installed provisional entries retain scientific holds but must not be installed twice. Historical reconciliation counts must not be used as live backlog counts.

Four completed PASS reviews (Acalypha phleoides, Acalypha radians, Tragia betonicifolia, Argythamnia aphoroides) were explicitly user-approved in the audit chat and now await curation. Exact image licensing/diagnostic polish remains explicit and approval does not convert unresolved taxa to PASS.

## Existing material reuse and private-study media — 2026-10-04

Before collecting new images or repeating Joey research, consult `workflow/existing-material-routing-2026-10-04.json` and `workflow/photo-recovery-audit-2026-10-04.json`, then read the referenced original archive records. The routing index preserves all 886 currently indexed Joey records and provides exact-name/string-synonym species targets, family candidates, term candidates, diagnostic roles, filenames, timestamps, and original source metadata.

Calvin has authorized sorting and using existing material for his own private study, with replacement/review before a future public release. This is project direction, not a change to source licenses or public-reuse permissions. Preserve creator credits, source pages, license/rights notes, and study-use/public-reuse flags. Do not ask for another batch approval merely to organize existing private-study source material.

Routing is not installation: verify the actual binary, taxon identity, diagnostic structure and destination before setting images[]. Do not mark a page visually complete from archive pointers alone. Preserve settled taxonomy/range decisions and active claims. A family/term candidate is a routing lead, not proof the current module exists or the teaching claim is verified.

Study-only images may be organized in the private repository's research/workflow area. Before moving them into learner-facing content/, data/, or assets/, confirm local/private delivery or authenticated Cloudflare Access. The existing Cloudflare build publishes these directories; a private GitHub repository and an unshared URL do not establish private hosting. Public-cleared images may continue through the normal learner pipeline.

Reuse exact existing images first; gather new material only for the diagnostic roles that remain missing. This index does not modify automation schedules or install images automatically.

### Saved-frame recovery and privacy confirmation — 2026-10-04

Calvin confirms the learner is private. Proceed with authorized private-study media installation while retaining original credits and public-reuse restrictions. Do not repeatedly block this work on hosting confirmation. All 338 expected frames from 15 indexed videos were located by exact filename in persistent storage, with nonzero file sizes; see `workflow/saved-video-frame-locations-2026-10-04.json` for exact file IDs and paths. Reuse these saved images before any re-extraction. The routing index now handles file_name/filename/asset and taxon/source_taxon/taxon_or_group schema differences: 125 records match 65 installed species. Counts do not establish visual verification or installation; full binary decoding remains part of installation.


## Joey Santore visual-source priority — 2026-10-04

For Calvin's private visual learner, Joey Santore video frames/screenshots are a preferred authoritative field-teaching source whenever the saved frame clearly shows the diagnostic structure, habit, comparison, or reproductive feature being taught.

- Before gathering a new external image for a family/genus/species visual role, check the saved Joey routing/index files for an applicable existing frame.
- Prefer an applicable Joey frame over a generic external photo when it shows the needed character more clearly.
- Preserve exact video/source credit, timestamp/frame provenance, filename/file ID, and private-study/public-reuse status.
- Joey's identification/context is high-value authoritative field evidence, but it does not bypass current taxonomy, accepted-name, provenance, or target-zone range verification.
- A Joey frame from a related already-built family may be used as a comparison anchor for a new family lesson when that improves lineage learning.
- Do not re-extract a frame that already exists in `workflow/saved-video-frame-locations-2026-10-04.json`; reuse the saved binary.
- Public release remains a separate rights/licensing decision; this priority rule applies to Calvin's private-study learner.

## LEARNER FAST-FILL mode — 2026-10-05

Current project priority is broad usable visual-learner coverage while Calvin is actively using the learner. This temporarily outranks final-quality photo polish for records that are already canonical or otherwise legitimately learner-ready.

- Prioritize usable learner content over perfect final curation.
- For learner-ready species, reuse existing project photos, Calvin's photos, and saved Joey Santore/video-frame material first.
- If those are insufficient, use good exact-species iNaturalist photos whose licenses permit the project's noncommercial study use; retain photographer, license, source URL, and observation/photo source information.
- Skip all-rights-reserved external images during fast-fill rather than spending time seeking permission.
- Initial target is about three useful images when practical: whole plant/habit, reproductive structure, and an identification structure such as leaf, stem, bark, fruit, seedhead, or diagnostic macro.
- Exact species is mandatory. Never substitute a related species merely to fill a gallery.
- Photo perfection is not required in fast-fill; stronger diagnostic images can replace provisional learner images later.
- Do not reopen settled taxonomy/range research merely because a canonical page needs photos.
- Do not run a project-wide reconciliation before every small task. Refresh main, check data/manifest.json, workflow/work-claims.json, and the exact records being edited; consult queue/draft/inbox state when the target is not already settled.
- Commit useful work in small durable batches and move on.
- Scientific labels remain strict, but HOLD/FAIL/UNRESOLVED **range** states may still be learner-ready. Never upgrade them to confirmed native merely for inclusion. Genuine taxonomy-identity conflicts remain a separate-card blocker until mapped safely.
- Deep photo polishing, exhaustive citation cleanup, and specialized diagnostic imagery are follow-up phases after broad learner coverage is substantially filled.

## Current manual-chat priority — 2026-10-05

During LEARNER FAST-FILL mode, manual project work follows this priority order unless Calvin explicitly changes it:

1. **Learner photo/gallery fast-fill lane** — missing-photo and photo-gallery continuation work. This is the highest-priority manual lane because visible learner usefulness is the current project goal. Work existing canonical/legitimately learner-ready taxa first, reuse project/Joey media before external collection, and add provisional exact-species imagery without reopening settled science.
2. **Large-genus continuation lane** — the manual continuation/“Continue Workflow Estimate” style work that closes larger or confusing genera and moves legitimate species/genus packages toward usable learner state. Preserve active claims and let the photo lane own broad gallery backfill rather than duplicating image searches.
3. **Taxonomy/recognition lane** — the “Continue Taxonomy Work” style work that improves accepted-name handling, recognition characters, comparisons, and taxonomy structure. It should correct real scientific issues but must not independently rebuild galleries already owned by the photo lane.

These three lanes outrank family polish, botanical-term polish, additional Joey extraction, generalized audits, new scouting, and other optional/manual cleanup while fast-fill mode is active.

### Secondary/manual chat behavior

- A non-priority chat that is resumed should first refresh this file, `workflow/work-claims.json`, `data/manifest.json`, and the exact target records it intends to touch.
- Existing durable state and active claims from the three priority lanes take precedence. Secondary chats must skip overlapping taxa/files rather than duplicate or overwrite work.
- Do **not** require a project-wide reconstruction of old chat history before routine work. GitHub coordination files and durable project artifacts are the shared source of workflow state. Cross-chat review is only needed when Calvin explicitly requests it or when repository state contains a real ambiguity/conflict.
- Do not start a new generalized audit/reconciliation merely because a secondary chat has been reopened. Continue only its clearly defined lane or remain idle.
- If a secondary lane finds a problem belonging to one of the three priority lanes, record/flag the issue durably when practical and hand it off instead of expanding scope.
- Fast-fill visual work may be provisional; scientific truth may not. HOLD/FAIL/UNRESOLVED status must never be silently upgraded to make a page look complete.

### Collision rule within the three priority lanes

When two priority lanes touch the same taxon or file, normal authoritative-state and claim rules still win. If both are otherwise eligible, use the priority order above: photo/gallery fast-fill first for presentation-only edits, large-genus continuation for package/genus closeout, and taxonomy/recognition for scientific corrections. A scientific correction always blocks propagation of known-wrong content even when the visual lane is higher priority for ordinary presentation work.



## Learner FAST-FILL mode — active

The project is currently operating in **LEARNER FAST-FILL** mode. Read and follow `workflow/LEARNER_FAST_FILL.md` before new learner-facing species/genus work. This mode prioritizes broad usable learner coverage and small durable commits while preserving strict scientific PASS/HOLD/FAIL decisions. Do not reopen settled taxonomy/range solely to improve photos, and do not run project-wide reconciliation before each small task.

## Background automation layout — 2026-10-05

During LEARNER FAST-FILL mode, unattended project work is intentionally reduced to three active lanes:

1. **Learner Photo Backfill** — hourly at :05. Presentation/media only. Improve galleries on canonical/learner-ready taxa using existing project/Joey/user media first, then properly licensed exact-species iNaturalist images. Do not change taxonomy/range decisions.
2. **Botany Deep Review** — every two hours at :25. Scientific review only for the small existing reviewed/scouted backlog. Do not create new scout batches and do not edit learner galleries.
3. **Approved Species Installer** — hourly at :50. Drain explicitly approved noncanonical taxa through the existing curation pipeline. Reuse existing science and use provisional exact-species imagery when needed; do not wait for perfect galleries.

The former **Unfinished Plant Scout** and **Small Genus Backfill** automations are paused during fast-fill mode so they do not create additional backlog or compete with the three priority manual lanes. Do not reactivate them unless Calvin explicitly changes the project mode or the current fast-fill/approved backlog is substantially exhausted.

This staggered schedule is deliberate. Preserve the :05 / :25-every-two-hours / :50 separation unless a future coordination change explicitly replaces it.

## Curation inbox READY-marker rule — 2026-10-05

To avoid noisy/redundant GitHub Actions while a batch is still being assembled, curation-inbox packages now use a final READY marker.

- Chats/automations may stage `batch.json`, species files, provenance, images, and other batch contents across multiple commits without triggering curation.
- Create `curation-inbox/<batch-id>/READY` **last**, only after the entire batch is complete and safe to process.
- The GitHub curation workflow triggers only on commits that add/change a `curation-inbox/**/READY` marker.
- `scripts/curation_pipeline.py` processes only batch directories containing both `batch.json` and `READY`.
- Never create READY early. If a batch is incomplete, leave READY absent.
- After successful processing, the existing pipeline archives the whole batch, including READY, as before.
- Manual chats and automations that use the curation inbox must follow this rule; direct canonical edits outside the inbox remain governed by their existing lane rules.

This keeps rapid staging commits from creating/cancelling multiple redundant Actions and prevents one finished batch from accidentally processing another incomplete staged batch.



## Canonical target-zone county rule — 2026-10-05

Before any taxonomy/range PASS, read `workflow/target-zone-counties.json`. It is the canonical county list for the project's >=3-county native-range threshold and supersedes older inferred county sets. Do not classify a county as inside or outside the target zone from memory.
