# Hays Botany ID — Project Rules

## Canonical project home
GitHub repository `Crking92/Hays-County-Botany` is the canonical home for botany data, learner files, workflow rules, and finalized curation packages.

Google Sheets is a coordination/status view. ZIP files and local BAT downloaders are not the primary finished product.

## Work coordination and duplicate prevention

Every chat, automation, and local workflow must check `workflow/COORDINATION.md` and the current `workflow/work-claims.json` before selecting new work.

The required duplicate-prevention gate is:
1. refresh `data/manifest.json`;
2. check `workflow/work-claims.json`;
3. check `research-queue.json` and existing `research-drafts/`;
4. check `curation-inbox/` and current curation Actions when relevant;
5. skip any taxon/scope already canonical, durably queued/drafted, or actively claimed by another lane.

Create or refresh a short-lived claim before beginning substantial work that is not yet represented by a durable project artifact. Release or supersede the claim as soon as the queue, draft, review artifact, curation batch, or canonical install records the work.

Never overwrite another process merely because its tracker status looks stale. Canonical GitHub state wins; if ownership is ambiguous, skip the target.

## Target zone
Tom Green, Concho, McCulloch, San Saba, Burnet, Llano, Mason, Menard, Schleicher, Sutton, Kimble, Gillespie, Blanco, Travis, Hays, Comal, Bexar, Kendall, Kerr, Edwards, Real, Bandera, Uvalde, Medina.

## Learner admission vs. native-range status — standing rule as of 2026-10-05

**Learner admission and native-range certification are separate decisions.**

During Learner Fast-Fill mode, a taxon is eligible for the private learner when it appears in one of Calvin's approved source pools or the derived `Master Plant Pool`, including the personal iNaturalist flora, LBJ/Hays County native source material, and NPSOT ecoregion backlog. **Three-county native proof is not required before a sheet-backed taxon may be curated or installed.**

Native-range status remains scientifically strict metadata:
- **PASS** — confirmed native in at least 3 project target-zone counties.
- **FAIL / FAIL_TARGET_ZONE / COMPARISON_NON_NATIVE** — not confirmed as project-target native under the current evidence or explicitly non-native/comparison.
- **UNRESOLVED / CONFLICT** — native-range evidence is incomplete or conflicting.

These range states do **not** block learner admission. They control labeling and native-only metrics.

Every learner page should keep the two concepts separate:
- learner admission: approved / represented / taxonomy-mapping-needed;
- range label: confirmed target-zone native / range unresolved / nonlocal or target-zone fail / introduced or non-native comparison / other clearly sourced status.

Never relabel an unresolved or non-native taxon as native merely to include it. Never count comparison, FAIL, CONFLICT, or UNRESOLVED taxa in confirmed-native totals.

The remaining hard gate for a separate canonical species card is **taxonomic identity**, not county nativity. Obsolete synonyms, parent concepts, duplicate names, or genuinely ambiguous taxon concepts should be mapped to the correct accepted learner concept or retained as aliases/comparison references rather than installed as misleading duplicate cards.

### Encounter-value comparison species

The learner should retain non-native, invasive, naturalized, weedy, escaped, nonlocal, unresolved-range, and other useful encounter taxa when they occur in the approved source pools or have clear identification value. Invasive status must still be sourced and must not be inferred merely from non-native status.

Use learner roles such as `TARGET_NATIVE_CONFIRMED`, `RANGE_UNRESOLVED`, `NONLOCAL_COMPARISON`, `NON_NATIVE_COMPARISON`, `INVASIVE_COMPARISON`, `COMMON_WEED_COMPARISON`, `LOOKALIKE_COMPARISON`, or `TAXONOMY_REFERENCE` as appropriate.

## Range authority priority
1. BONAP / NAPA
2. USDA PLANTS
3. Lady Bird Johnson Wildflower Center / NPSOT
4. Herbarium records and other authoritative regional floras
5. iNaturalist / GBIF / Leafminers as supporting occurrence evidence

Record the actual counties used for the target-zone decision.

## Required curation order
For every new species or batch:

1. Confirm accepted taxonomy, authority, synonyms, and current genus placement well enough to avoid duplicate or misleading learner concepts.
2. Record the best current native-range status when already known or cheaply available, but do not require a three-county audit before a source-pool taxon enters the learner.
3. Build the morphology-first identification package.
4. Identify the most important local look-alikes and the structures that separate them.
5. Define the diagnostic image roles required for that species.
6. Select exact source photographs whenever possible and record provenance/licensing.
7. Create `species.json`, `SOURCES.txt`, and `image-sources.csv`.
8. Use a stable species ID such as `ipomoea-hederacea`.
9. Sync completed batches to this GitHub repository.
10. Let GitHub automation handle final photo downloading, resizing, folder installation, manifest generation, and validation.

## Identification method
Strict morphology first: floral and reproductive structures, phyllotaxy, leaf morphology, sap, stem features, fruit/seed structures, measurements, and diagnostic look-alikes.

Do not identify primarily by flower color.

Every learner entry should answer: **“Where should I look first?”**

## Look-alikes
Each species package should identify the most important local look-alikes and specify the exact structures that separate them.

Prefer measurable or structural differences over vague gestalt descriptions.

## Species folder standard
`species.json + SOURCES.txt + image-sources.csv + images/`

Genus-level and family-level files must be preserved and merged rather than rebuilt blindly.

## Diagnostic image roles
Choose image roles from the actual diagnostic needs of the species, for example:

- habit / whole plant
- leaves and phyllotaxy
- stem attachment / nodes
- flower front
- flower side
- calyx / sepals / phyllaries
- reproductive structures
- fruit / seed
- bark / twig / bud
- diagnostic look-alike comparison

Do not assume every species needs the same generic five-photo set.

## Visual learner standard
The project is intentionally optimized for a visual learner. When choosing or building teaching visuals, use this priority order:

1. **Real photographs first** whenever the structure can be shown clearly.
2. Add **learner-generated arrows and labels** that point to the exact diagnostic structure.
3. Pair the real photograph with a **simple drawing or diagram** when the real structure is hard to understand in isolation.
4. Prefer **specific part labels** over generic captions: name the exact sepal, calyx, ligule, node, cupule, phyllary, awn, etc.
5. When two concepts are commonly confused, prefer using the **same underlying image with different overlays** to teach the relationship (for example: one sepal vs. the whole calyx; node vs. culm; ligule vs. collar).
6. Use close-ups or macro views for small structures. A beautiful whole-plant image does not substitute for a diagnostic close-up.
7. Preserve source provenance and licensing. Learner overlays must be described as overlays and must not imply that the original source image contained the added arrows or labels.
8. For visual teaching, prioritize clarity over aesthetics. If the diagnostic structure is not obvious at a glance, the image is not finished.

Whenever practical, a botanical term lesson should include:
- one real photo,
- one clearly labeled target structure,
- a “where do I look?” cue,
- a “why does it matter for ID?” cue,
- and a diagram only when it improves understanding.

This visual standard applies to glossary terms, family lessons, genus comparisons, species pages, and future teaching modules.

## Visual-learner completion gate — standing rule as of 2026-10-04

The primary product is a visual learner, not a text database. For all new species/genus curation work, information and photos are one deliverable.

A new species page is not visual-learner complete until it has:
- usable morphology-first text and a clear “Where should I look first?” cue;
- realistic local look-alikes and exact separating structures;
- at least one displayable real photograph wired through species.json -> images[];
- a diagnostic photo plan that covers the structures actually needed for ID;
- photo provenance/reuse metadata for every selected image.

Target photo coverage is normally 3–5 diagnostic views per species when feasible, adapted to the taxon. Prefer:
1. real photographs over generic illustrations;
2. Hays/Central Texas/Texas material when diagnostically reliable;
3. whole-plant/habit plus diagnostic close-ups;
4. reproductive structures, fruit/seed, bark/twig/bud, ligule/calyx/phyllary/awn/etc. as required;
5. side-by-side or annotated comparisons for commonly confused taxa.

A whole-plant glamour shot alone does not satisfy the visual gate when the ID depends on a small structure.

If exact/licensed final images cannot yet be secured, the page may be installed only as provisional / visual-incomplete with that status explicit. Do not call it learner-complete.

Existing canonical pages that predate this rule may remain scientifically valid while visually incomplete. They belong in the photo-recovery backlog and should be repaired opportunistically without reopening settled taxonomy/range work.

This rule applies across species curation, genus batching, Scout, Deep Review, family/genus teaching modules, video reconciliation, and UI work. Each lane should gather or preserve visual evidence appropriate to its role rather than assuming a later chat will add the pictures.

## Image provenance
Whenever possible, select exact source photographs rather than relying on a generic search-based downloader.

For each selected photograph record:
- source platform
- observation or file ID
- photo ID when available
- creator
- license
- source page
- intended diagnostic role
- private study-use status
- public-reuse status

Private study suitability and public reuse permission are separate statuses.

## GitHub automation role
GitHub automation is responsible for the final mechanical steps:
- downloading the approved source photographs
- resizing/normalizing images
- installing images into species folders
- generating manifests
- validating file structure and required metadata

The curation layer must choose and document the photographs before automation runs.

## Google tracker role
Google Sheets is a coordination/status view only. It may summarize taxonomy, range status, curation progress, image status, and GitHub sync status, but it is not the canonical data store.

### Standing sync permission
As of 2026-10-02, Calvin has explicitly authorized ChatGPT/OpenAI curation chats to keep the Google tracker synchronized as normal project maintenance after deep review, approval, installation, taxonomy corrections, photo/provenance updates, and batch-status changes.

GitHub remains authoritative. Sheet synchronization may update the Species Tracker, Study Batches, Master Plant Pool status/notes, Family Study Index, Genus Study Index, Project Rules, and supporting lookup data as needed to mirror canonical/review state. Do not let a Sheet value override a conflicting canonical GitHub record.

Never store API keys, tokens, passwords, or other credentials in the tracker.

## Incomplete work
Incomplete **county-range evidence alone does not block learner installation** for an approved source-pool taxon. Preserve the range state as UNRESOLVED/FAIL/COMPARISON and label it honestly.

A separate species card may still be blocked when the taxonomic identity itself is unresolved enough that installation would create a duplicate, obsolete, or misleading concept. Morphology and image provenance may be provisional during Learner Fast-Fill as long as the page is clearly marked and remains useful for identification.
