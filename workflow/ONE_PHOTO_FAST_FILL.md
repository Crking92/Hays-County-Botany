# One-Photo Fast-Fill SOP

## Purpose

This is the **breadth-first first pass** for the private Hays County Botany visual learner.

The goal is simple: give as many eligible zero-photo species as possible **one recognizable exact-species photo**, then move on. This lane is not responsible for building a diagnostic gallery, polishing every caption, deep-reviewing range/taxonomy, or finding the best possible image. Other chats and automations own those later improvements.

## Target selection

Work only on taxa that are already canonical or explicitly learner-ready.

A target is eligible only when:

- its current canonical/learner-ready page has **zero displayable images**;
- a fresh `images[]` / physical-media check confirms it is a true zero immediately before claiming/staging;
- no active claim or durable inbox/backfill work already owns the same media task;
- its identity is clear enough that an exact-species/current accepted taxon concept photo can be selected without reopening scientific review.

Do not use this lane to resolve taxonomy, native-range disputes, difficult synonym problems, or ambiguous IDs. Skip those and leave them to Deep Review or a dedicated curation lane.

## Batch size

- **Default target: 10 species.**
- Normal operating range: **8–12 species**.
- Use 11–12 only when the sources are already clean/easy.
- A smaller batch is fine only when the remaining true-zero backlog is genuinely sparse.
- Never keep a batch small merely because one or two candidates became difficult; replace those candidates with easier true zeros.

This size gives useful visible coverage while keeping source checks, installer time, and failure recovery bounded.

## Easy-source ladder

Use the first clean exact-species source that satisfies the learner need.

1. Existing project-vetted image/provenance already in research, review, Joey/user media routing, or prior curation material.
2. Wikimedia Commons exact-species/current-concept image with clear reusable licensing.
3. USDA, NPS, or another clearly public-domain/authoritative exact-species image.
4. iNaturalist only when the exact photo, creator, license, and stable direct image source are immediately clear.

For Wikimedia Commons, use a **width-limited download URL** (normally 960 px). Do not stage a bare full-size `/wiki/Special:Redirect/file/...` URL.

If the first easy source is ambiguous, licensing is unclear, the image is not obviously the taxon, the direct URL is unreliable, or the search starts branching across multiple sites, **skip the species and replace it**.

## Search/timebox rule

This lane must not become a research marathon.

For each species:

- prefer one obvious recognizable habit/flower/fruit image;
- inspect at most a small number of obvious candidates;
- do not chase the perfect diagnostic macro;
- do not perform broad web research across many sites;
- do not rewrite settled scientific fields;
- do not spend substantial effort proving county range or morphology.

A recognizable exact-species “face” is enough for this pass.

## Media status

Every installed first-pass image should remain clearly marked as provisional, using the existing learner-fast-fill conventions, including:

- `learner_visual_status.status = provisional_learner_ready`
- `learner_visual_status.mode = learner_fast_fill`
- a note that stronger diagnostic gallery coverage may replace or supplement it later.

Preserve creator, license, source page, direct image source, study-use/public-reuse fields, and existing scientific content.

## Commit / installer pattern

Keep GitHub writes coarse-grained.

1. Refresh `main`, manifest, current claims, inbox, and relevant current species files.
2. Claim the whole 8–12 species batch once.
3. Assemble the complete batch locally/in-memory.
4. Prefer **one atomic curation-inbox commit containing the whole batch and READY**. If the available writer cannot do that, use exactly one complete staging commit and one final READY commit.
5. Never stage species packages one file/species at a time across many commits.
6. Verify the curation workflow result and canonical image files.
7. Release the claim after successful installation.

If one species breaks the batch before READY, remove/replace that species instead of expanding the research effort.

If a READY batch fails during installation, repair or disable that failed batch promptly. Do not leave a failed READY batch sitting in `curation-inbox/`, because every later curation run will try it again before newer batches.

## Downloader guardrail

The curation pipeline normalizes Wikimedia Commons Special:Redirect image downloads to a width-limited request. New fast-fill batches should still record width-limited URLs directly when practical.

A source that repeatedly returns 404/429/timeout is not worth blocking this lane. Replace the source or skip that taxon and keep moving.

## Definition of success

Success is **coverage breadth**, not polish:

- true zero -> one usable exact-species learner image;
- correct provenance retained;
- scientific status unchanged;
- provisional status obvious;
- installer succeeds;
- move immediately to the next zero.

Gallery quality, diagnostic closeups, stronger local imagery, arrows/labels, comparisons, and scientific enrichment belong to Learner Photo Backfill, Deep Review, Joey/user-media work, and later visual-polish lanes.

## Performance budget

This lane is intentionally optimized for wall-clock speed. Do not turn a production batch into a workflow-design or research session.

### Candidate discovery

- Prefer `reports/photo-fast-fill-zero-queue.json` as the first source of current zero-photo candidates. The curation pipeline rebuilds this report after successful curation runs.
- Do not start each batch by reopening dozens of species files or re-reading the historical photo-recovery audit.
- Pick roughly 10–14 promising unclaimed candidates from the live queue, then do one fresh parallel verification of those specific pages plus `workflow/work-claims.json`.
- The historical recovery audit is a source-hint archive, not live zero-photo truth.

### Source-search cap

- Run **one batched source search** for the whole candidate pool whenever possible.
- One small follow-up search is allowed only to replace obvious failures.
- Do not repeatedly search the same difficult species in the same batch.
- After two source passes, ship the clean subset. A **6–10 species successful batch is better than a 12-species batch delayed by hard taxa**.
- Record or remember skipped hard taxa for later backfill rather than immediately retrying them in the next fast-fill batch.

### Production-batch discipline

During a requested fast-fill batch:

- do not refactor unrelated workflow code;
- do not improve scientific content;
- do not rebuild old audits;
- do not investigate unrelated automation state;
- do not expand the batch because another lane changed nearby files;
- make only the minimum changes needed to claim, stage, install, verify, and release the selected media batch.

Workflow/tooling improvements should be made between batches, not in the middle of one.

### Write and verification budget

Preferred write sequence:

1. one claim commit;
2. one complete staging commit;
3. one READY commit;
4. one release commit after success.

If the atomic Git-tree write fails once because of a connector/API error, refetch the current head and use the reliable staging fallback immediately. Do not spend multiple attempts trying to preserve a single-commit ideal.

For Actions verification, check the triggered run, then verify the final report/canonical files. Avoid excessive polling. The installer itself is expected to be fast; source discovery should not dominate the run.
