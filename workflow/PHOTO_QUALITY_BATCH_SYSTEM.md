# Automated photo-quality batches — Central Texas Visual Learner

**Status:** Read-only photo quality pipeline. The scientific record, species gallery files, license terms and reviewed image status always remain canonical. This tool cannot install a photo, verify an anatomical arrow, change a species name, or publish previously restricted material.

## What changes automatically

When an installed species JSON, the manifest, or this audit utility changes on GitHub main, the **Visual Learner Photo Quality Queue** GitHub Action runs. It also runs weekly and can be started manually. Unlike a ChatGPT scheduled task, it **does not use one of the five ChatGPT automations**.

Every run:
1. Reads all currently installed species from data/manifest.json — including newly installed taxa.
2. Reads each species gallery and checks whether local image references resolve on disk. External URLs are counted as references but **not downloaded, visually checked or confirmed reachable**.
3. Checks roles documented on photos: habit, leaf, flower/inflorescence, fruit, stem, and when applicable Asteraceae phyllaries, Poaceae ligules, or milkweed corona structures.
4. Reports metadata gaps: missing credit/license/source, restricted or CC BY-NC use, vague roles, and missing role coverage. A missing role label is **not proof a visible feature is missing from a photo**.
5. Scores a priority queue, avoiding species currently claimed by the photo installation lanes. The full inventory still shows those claimed taxa.
6. Uploads three downloadable artifacts to the GitHub Actions run: inventory.json for every installed species, queue.json for the selected batch, and queue.md for a readable crew handoff.

**No source code, botanical records, license permissions, or photo files are written during the Action.** It has contents:read permissions and no Git push steps. This deliberately prevents races with five existing ChatGPT automations and species installers.

## How to use

On GitHub, open **Actions → Visual Learner Photo Quality Queue → Run workflow**. Use batch_size 25 (or 12–15 for faster passes), offset 0 for highest-priority unclaimed plants. After working through that list, use offset 25, 50, and so on to inspect subsequent priorities. Species with confirmed new photos/roles will naturally move lower in the next inventory.

When the run completes, open it and download the **visual-photo-quality-queue** artifact. The queue.md file is the short worklist to give an existing photo installer or curation chat. The queue.json records exact taxon IDs and paths. The full inventory.json preserves evidence about which image roles were (and were not) supported **by existing metadata**.

You can also run locally, using Python 3.12:

    python scripts/photo_quality_audit.py --batch-size 25 --offset 0 --out-dir photo-quality-output
    python -m unittest discover -s tests -p test_photo_quality_audit.py -v

Batch order is deterministic for a fixed manifest and claim state: highest priority first, then alphabetical taxon ID. Active photo claims are withheld from new worklists; the claim record is not changed. Any missing/corrupt species JSON causes a **failed** run, not a misleading partial success.

## Photo-role priorities and their limits

| Taxa | Routine review checklist |
|---|---|
| Asteraceae | Whole plant, leaf/attachment, capitulum/florets, mature phyllaries |
| Poaceae | Habit, blades, inflorescence/spikelets, ligule and collar |
| Asclepias, Funastrum, Matelea, Gonolobus | Habit, leaves, flower cluster, corona/hood/horn structure |
| Quercus | Whole tree, mature leaves, acorn/cup, twig/bark/buds |
| Other taxa | Habit, foliage, flowering, fruit/seed; use documented taxon-specific diagnostics before claiming these are the correct features |

The generator only infers what **review requests** are worth checking based on metadata; it does not assert that every species has those characters, that all species flower visibly, that a licensed diagnostic macro proves a field identity, or that missing role labels mean missing anatomical content. Existing genus/family lessons and scientific cautions control the final photographic teaching plan.

## Arrows and anatomy review

Anatomy labels can be proposed during photo polish, but **a new arrow must remain pending** until someone or a trusted image-review process checks the exact image at full size, confirms the species and structure, and verifies the target coordinates on the actual rendered photo. There is deliberately no automatic overlay-writing function in this pipeline.

Recommended follow-on: a separate **reviewed-only annotation queue** keyed by existing image paths/photo IDs and target anatomical structures. Never auto-mark arrows as verified based only on filenames, image roles or AI guesses.

## Safety and future integration

- Read-only pipeline; no conflict with photograph import scripts or other automations.
- Image creator, license, public_reuse, and source_page are preserved from species JSON; no automatic CC BY-NC promotion.
- Exact accepted taxon ID from data/manifest.json is the sole installation universe. New taxa join automatically when added to the manifest.
- No county-native PASS/FAIL classification is used to suppress encounter-first study cards.
- Use the existing approved photo installer to act on suggestions; this report **does not** create duplicate curation drafts or reserve species.
- Human/image-level confirmation remains necessary before asserting an anatomical part is actually visible or a photo is fully licensed for the intended public use.

Implementation: scripts/photo_quality_audit.py and .github/workflows/photo-quality-audit.yml. Unit tests: tests/test_photo_quality_audit.py.
