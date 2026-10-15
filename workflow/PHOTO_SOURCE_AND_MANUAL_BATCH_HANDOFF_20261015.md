# Photo-source update and manual diagnostic-batch boundary — 2026-10-15

**User instruction:** Make all five existing botany automations aware of Joey Santore's new Texas-wide photo catalog **and** the user's own iNaturalist / Glass Root Garden photo sources. **Keep all five existing automations enabled, scheduled and working in their current lanes.** Do not create, pause, repurpose, or reschedule automations. The user will conduct **new coordinated multi-species diagnostic-photo enrichment batches manually in this ChatGPT conversation**.

Read this file with `PROJECT_RULES.md`, `workflow/COORDINATION.md`, `workflow/VISUAL_PHOTO_LESSON_STANDARD.md`, `workflow/work-claims.json`, `data/manifest.json`, and latest `reports/photo-coverage-latest.json`.

## 1 — Joey Santore, statewide Texas inventory (available in GitHub)

- Observer: `joeysantore`. Full Texas photo inventory: `workflow/joey-texas-inat-photo-inventory/photo-candidates.csv` (one row **per actual iNaturalist photo**), `species-photo-summary.csv`, and `summary.json`.
- At the 2026-10-15 inventory snapshot: **2,974 plant observations, 1,373 named taxa, 15,041 individual photos**, of which 2,775 photo rows matched already installed canonical species at inventory time. Snapshot statistics are **not live installed-photo counts**.
- Original local/project-county pool remains `workflow/joey-inat-photo-inventory/photo-candidates.csv` plus summary, containing the 24 Central/West Texas target counties. **Prefer genuinely local examples** when comparing equally suitable exact-species views; statewide photographs are allowed when verified. The local inventory is a **subset**; don't double-count it as separate photographs.
- Source rights in statewide snapshot: Joey-credited **CC BY-NC**, **noncommercial** with full photographer credit. The permission to use his photography with attribution must NOT be interpreted as unrestricted/commercial licensing. Recheck live individual-photo creator, license, photo ID, observation ID, taxon/rank and image source before installing. Don't infer photo permissions from an observation's data license.
- Existing catalog/enrichment scripts: `scripts/joey_inat_photo_inventory.py`, `scripts/joey_photo_quick_batch.py`. These are available for **manual ChatGPT-invoked batches**. **Do not independently trigger** `workflow/joey-inat-photo-inventory/next-batch.json` or launch autonomous 10–15 taxon runs unless the user requests a manual batch in chat. Metadata candidates do not count as installed images.

## 2 — User's own iNaturalist / Glass Root Garden photographs

- Observer login `calvinking`; preferred public credit **Glass Root Garden** (photographer Calvin King). Existing inventory and individual photo metadata: `workflow/glass-root-inat/README.md`, `workflow/glass-root-inat/output/`, per-batch approvals and summaries. The GitHub Action **Glass Root Garden iNaturalist Photo Inventory** can query public Research Grade Texas plant observations for this login; individual image attribution and rights must still be verified.
- Original October 2026 personal CSV export is in the user's ChatGPT Library under **Inaturalist Observations Texas October 2026**, file **observations-797290.csv** (previous handoff recorded 2,431 observations / 444 names). **That private CSV has not been imported as a raw GitHub file.** The GitHub workers cannot assume they possess or have synced the Library CSV; use the already persisted observation IDs and/or live approved iNaturalist inventory instead.
- Owner permission is durable in `workflow/glass-root-inat/OWNER_PERMISSION_2026-10-14.md`: the user attested their ownership of their photographs and directly authorized **private learner** use. This is **not** a blanket public Creative Commons license and **does not** extend to photos uploaded by the account but credited to someone else.
- For every photo: verify exact observation and photo IDs, accepted taxon or explicitly checked synonym, creator/attribution, current source license and source page, image bytes, and required ID structure before declaring it installed. If permission is direct-owner private use but API license is missing/all-rights-reserved, preserve that original source status, mark `public_reuse=no`, record the direct permission basis and credit Glass Root Garden. For a genuinely licensed photo, preserve its actual photo-level CC terms.
- Relevant durable records: `reports/glass-root-personal-photo-progress-20261014-003.md`, `workflow/mass-photo-match-20261015-user-source-handoff.json`, `workflow/mass-photo-match-20261015-user-stage1.json`. These latter mass-match files are **candidate-only**, not authorization to install or claims of photo completion. Never expose restricted GPS/EXIF.

## 3 — Division of work: manual batches versus existing automations

**Manual ChatGPT photo-batch lane (user owns selection and start):**
- New multi-species diagnostic enrichment batches (roughly 12–15 species), including the batch discussed in chat around grasses, asters, crotons/euphorbs, milkweed vines, Sida, Ludwigia, and confusing look-alikes.
- Choose candidates from the **live** `reports/photo-coverage-latest.json` and `data/manifest.json`, not historical numbers. One-photo status can change hourly: do not assume previously suggested species are still one-photo cards.
- Prefer +1 genuinely different diagnostic view and optionally +2 complementary views; don't inflate galleries with near-duplicate habit photos. Needed part-specific views: grass ligule/spikelets; aster involucre/phyllaries; Croton pistillate sepals/trichomes; milkweed hoods/corona; Sida calyx/fruit; Ludwigia decurrent wings/fruit, **as anatomically applicable**.
- Before manual edits, check current claimed/inbox species and avoid colliding with active photo/genus/family work. Reserve exact species scoped to an actual manual batch when it begins; don't preclaim all one-photo species.
- Continue to treat `muhlenbergia-piniflora` as a **source/taxonomic concept HOLD**, not an empty photo to fill with `M. dubia` without identity approval.

**Five existing scheduled ChatGPT automations continue unchanged:**
1. **Approved Taxa Installer:** install approved noncanonical taxa; preserve and correctly credit *both* photographer sources and existing galleries. Do not launch multi-species manual diagnostic enrichment.
2. **Taxonomy Name Fast-Pass:** work on scientific names and synonyms, not photo installations. Source-inventory names are photo leads only, not automatic identity/learner-admission proof.
3. **Diagnostic Photo Fast-Fill:** keep its **existing hourly one-unclaimed-species workflow** including genuine diagnostic gaps and safe failed-publish recoveries. It may refer to either catalog to find an exact candidate, but **must not commandeer the manual batch or launch new automatic bulk Joey/user-photo runs**. Respect manual-photo claims once posted. Do not confuse external-only reference with installed physical image.
4. **Family Similarity Polish:** use new legitimate photo references for structure-based family lessons, citations, and photo-role requests; no bulk species/photo installs.
5. **Genus Comparison Builder:** use new legitimate photo references in real look-alike comparisons, diagnostic photo-role requests, and lesson examples; no bulk species/photo installs.

**Operational safeguards across all lanes:** Preserve all already installed images and scientific HOLD/FAIL/range state; exact-species and image-level licensing checks win over catalog metadata; never invent photo-specific diagnostic roles/arrow positions; respect active claims, existing curation-inbox and GitHub Actions. Distinguish source candidate, linked reference, downloaded/staged image and installed/render-tested image. Keep existing schedules/automation scope unchanged.

## 4 — Current photo audit, not a fixed quota

As of the last audited GitHub snapshot on 2026-10-15: **552 canonical species**, `166` with 1 gallery record, `55` with 2, `330` with 3+, and **one unphotographed source-name/taxonomy HOLD**. Counts are **dated and change as installers run**. A locally installed-file count differs from gallery records; use `reports/photo-coverage-latest.json` and recheck photo file existence.

**Don't rewrite or re-run the historical 15-species chat shortlist as if all 15 are still one-photo cards.** Freshly select only eligible taxa when manual batches actually begin.
