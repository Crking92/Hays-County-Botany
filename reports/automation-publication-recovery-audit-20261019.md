# Automation publication and cancellation audit — 2026-10-19

**Scope:** live GitHub `main`, five enabled botany automations, current curation inbox and archive, published family/genus/index files, explicit taxonomy recovery handoffs, photo backlog, and GitHub Actions history through October 19. Historical workflow cancellations are **not** equivalent to unpublished species/photos. Continue to refresh live claims and main before changing anything.

## Verified successful recovery this audit

- `Malus ioensis`: the Approved Taxa Installer's complete, staged `approved-installer-malus-ioensis-20261019-001` batch lacked READY. New source/license check verified Krzysztof Ziarnek (Kenraiz), Wikimedia Commons `Malus_ioensis_kz03.jpg`, CC BY-SA 4.0; identity and diagnostic details remain provisional. Collision-free manifest/claims preflight. READY commit `dfb16db83113bdcfd4c0fc92a2a146c5c109e4a0`; [curation Action 39261484459](https://github.com/Crking92/Hays-County-Botany/actions/runs/39261484459) **success**. Canonical species path `content/taxa/Rosaceae/Malus/malus-ioensis/species.json`, a 116,318-byte physical JPEG, image record, license/source metadata and `data/manifest.json` were re-fetched and confirmed. Count at that successful completion: **1,149**; later runs may increase it. The image is a flowering-branch first look, **not** mature fruit confirmation.
- Previously blocked `Geraniaceae` family anatomy/identification lesson was merged in commit `3155daf8b1fabfe6648ae682cbfb8be987c6e978` and verified; four photo-role requests remain `needs_photo/annotation_pending`. Its recovery handoff now says `canonical_published_verified`.
- A GitHub photo-validation script crash from missing report directory was fixed on `main` in commit `1b5010212e0b20dbab65261db6b38618f4b26565`; source photos are untouched. The fix was read-back verified; **a subsequent full read-only diagnostic-photo preflight run succeeded**: [GitHub Action 39262684396](https://github.com/Crking92/Hays-County-Botany/actions/runs/39262684396)..

## Cancelled GitHub Actions ≠ unpublished work

- Latest 300 GitHub Action records inspected: **61 cancelled** runs, all named `Visual Learner Photo Quality Queue`. Workflow `.github/workflows/photo-quality-audit.yml` uses `concurrency.cancel-in-progress: true`, and its body is a read-only report/QA artifact job. A newer audit cancels an older one; it does not undo or drop a prior species/image commit. Newer runs have succeeded. Do **not** rerun 61 identical audits.
- Older historical cancellations also exist for `Sync learner lesson index` and `Botany curation pipeline`. These require current index/manifest/inbox reconciliation, not blind retry, because their targets may already have been committed in later successful runs.
- Failed `master-pool-multisource first-card batch 047` (Git merge conflict) was followed by a successful same-batch Action `39195608297` and canonical readback. Do not republish.
- Failed `Install Supplementary Diagnostic Photos 033` had a missing preview manifest; a later `reports/manual-library-install-033-20261016.json` reports **4 installed** photo records. Reinspect exact photo-level expertise before promoting them as diagnostic confirmation, but do not install duplicate originals.
- Failed `Install Historic Muhlenbergia Plate 024` (unexpected non-JPEG input) has a later `reports/manual-external-mirror-install-024-20261016.json` showing the multi-taxon plate physically installed for `muhlenbergia-x-involuta` with Public Domain Mark provenance. It is **not** a living-plant field photo.
- Failed `Restore Missing Leersia Panicle 059` was HTTP 429 from Wikimedia Commons. `Leersia oryzoides` still has **3 real gallery images**; its original missing Matt Lavin CC BY-SA 2.0 panicle JPEG stays in `unresolved_photo_references[]`. No successful retry of that precise image was verified. Leave this as an optional licensed-photo recovery, not a zero-photo species.

## Canonical publication status of explicit stale handoffs

- `data/lesson-index.json` contains **Chloris, Alternanthera, Ammannia, Helenium, Tridens, Lactuca**. Their genus lessons were independently present on main when checked. In particular, Tridens has 4 `visual_lesson.steps` and 4 `photo_role_assignments`; Lactuca has 4 visual steps and 3 comparison cards; Helenium has 4 `anatomy_lessons`. Prior genus recovery notes calling these *unpublished* are historical and must be compared to the current documents before any retry.
- `workflow/family-recovery/oxalidaceae-2026-10-18-2011.json`, `rhamnaceae-2026-10-18-1814.json`, and `geraniaceae-2026-10-19-0419.json` have verified publication outcomes (with diagnostic photographs still to source/verify).
- Taxonomy explicit recovery handoffs for `Setaria italica`, `Myriophyllum heterophyllum` and `Boltonia diffusa` say canonical name evidence and Sheet mirrors have already been verified. The historical `sheet-mirror-2026-10-15-040-050.json` ledger still has a **documentation reconciliation** pending for Boltonia; **do not republish its scientific decision or Sheet cell**.

## Current curation inbox

Following Malus' successful run, remaining staged folders are `approved-installer-elephantopus-echinochloa-20261017-001`, `approved-installer-lupinus-melia-20261016-001`, `approved-installer-recovery-geum-sabal-20261016-001` and `manual-buddleja-diaperia-20261014`. **None has READY**. The corresponding first-card species (including Elephantopus, Echinochloa, Lupinus, Melia, Geum, Sabal, Buddleja and Diaperia) were independently checked as already canonical. Leave these older staged batches `validate_only` or held; adding READY would risk duplicate installation.

Other older handoffs such as limestone ferns and the first-35 `Amorphophallus titanum` concept have since become canonical, so their dated instructions must not be blindly replayed.

## Genuine unresolved work (do not force publish)

1. Latest physically zero-photo canonical queue `reports/photo-fast-fill-zero-queue.json`: **Cuscuta indecora, Cuscuta obtusiflora, Euphorbia roemeriana, Muhlenbergia piniflora**. These four need exact-taxon, rights-cleared, physically stored media before claiming photo completion. Diagnostic Photo owns installed-canonical photo work.
2. `Leersia oryzoides`: one optional exact-source panicle photo still blocked by Commons HTTP 429; existing gallery remains usable. Reuse verified private archive or retry conservatively later, without fabricating a recovered file.
3. `Asclepias viridis`: five existing private photos are not yet independently cleared for public reuse because image-level photographer/rights provenance is missing. `Pluchea camphorata` also has a metadata/source-rights follow-up. Keep honest restrictions.
4. Remaining library media candidates and macro/anatomy arrows are selection/diagnostic-review tasks. Archive metadata alone does not authorize installation or botanical arrow labels.
5. **RESOLVED:** A fresh diagnostic-photo site-copy QA run at current code ([Action 39262684396](https://github.com/Crking92/Hays-County-Botany/actions/runs/39262684396)) completed successfully after the report-directory fix. No need to repeat the failed old SHA.

## Routing / safe next steps

Keep the existing five hourly automations enabled and their ownership unchanged. Approved Taxa Installer: new uninstalled accepted concepts with one verified real image. Diagnostic Photo: four zero-photo first, then one-photo/macro/rights issues. Taxonomy: name/identity holds and any mirror **documentation**, not repeated accepted-name publication. Genus/Family: visual lesson polishing and actual diagnostic photo selection only where missing. Check `main`, manifest, live claims, and precise provenance before each write. A failed or cancelled **run** is not automatically an unpublished **deliverable**.

This is a status reconciliation, not permission to erase scientific holds, delete historical provenance or bypass connector safety checks.
