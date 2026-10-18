# Permanent photo candidate library — shared operating contract

## October 17: second Photo Lab review preserved

The user's **Batch 002 photo labeling** is durable in `workflow/photo-library/reviews/diagnostic-002-user-labels-20261017.json`. It covers **73 image records across 15 species**, preserving media credit, explicit roles, and original GBIF/Pl@ntNet source links. **62 are potential diagnostic candidates** and **11 were marked "Unclear / not useful" and MUST be excluded**. User export misleadingly printed SHORTLISTED on all 73, including the 11 unwanted photographs; the specific "Unclear / not useful" classification overrides the shortlist text. Do not install or mark any of these image candidates as verified until image pixels, taxonomy, copyright, structure and existing gallery uniqueness have been checked. Batch 001 review remains preserved separately. No standing automation has been changed to install these unreviewed candidates.


## October 17: user's first Photo Lab review is preserved in GitHub

Photo Lab 001 review from the user is now saved as `workflow/photo-library/reviews/diagnostic-001-user-labels-20261017.json`. It contains **73 individually attributed, source-linked labels from 16 canonical species**, including **67 provisional potentially useful photo choices** and **six images the user marked "Unclear / not useful"**. The latter are explicitly excluded from any install shortlist. Other labeled images require true image-level identity/structure verification and ordinary gallery/claim duplicate checks; **these labels alone are NOT botanical approval for installing or captioning a photograph**.

The user-facing `photo-review.html` now automatically shortlists photos when a useful part is chosen, and offers Copy review, Save review file, and Resume from file. Local controls don't write to GitHub; the review JSON above is the durable submitted result. Read it before gathering more photographs for those same species or reviewing this batch. Do not change the five standing automations or their workflows to consume provisional labels directly.

## October 16: new manual diagnostic-view candidate collection lane

The original sparse-species first-pass harvest covered 401 species, with 2,283 stored provisional photographs at the prior verified checkpoint. The user has approved an additional **candidate-gathering pass for already-photographed species** to increase useful visual perspectives, without performing bulk unreviewed installations.

- Read `workflow/photo-library/requests/20261016-diagnostic-batch-001.json` for the exact initial 21 morphology-priority taxa and desired plant structures.
- The new manually triggered `.github/workflows/photo-library-diagnostic-collect.yml` uses the existing GBIF + public Pl@ntNet source pipeline, may search taxa with 3+ installed images, takes no more than two photos per single occurrence, and persists files/metadata in the same private Release / indexed library format.
- **Do not interpret the requested organ as proof of what a newly harvested photograph depicts.** GBIF photographs generally lack reliable organ labels. All results retain `exact_name_metadata_only_review_image` until a person checks the actual image; then select only genuinely useful distinct parts.
- The new collection is manual-only and does not add or alter any of the five automations. Other photo/installer/genus/family chats may use these candidates **after** archive success and standard scientific/copyright/duplication review; protect taxonomic HOLDs.


## 2026-10-16 — Diagnostic-view candidate expansion (manual phase)

**First-pass sparse-card collection complete:** 401 canonical species scanned, 2,283 provisional image files archived across sources at the checked snapshot. These are candidate images, not botanical/photo-part certifications or installations.

**New manually triggered workflow:** `.github/workflows/photo-library-diagnostic-candidates.yml` with source script `scripts/diagnostic_photo_harvest.py`. The first saved target list and requested anatomical structures are `workflow/photo-library/requests/diagnostic-001.json`. It searches for **previously unseen media URLs** across additional GBIF occurrence pages, prioritizing Texas and diversifying source observations. The resulting `selected-species.json` inside each permanent private Release archive records the sought structures (grass ligules/spikelets, aster phyllaries, milkweed corona/hoods, etc.).

**CRITICAL:** A target part listed in `wanted_parts` is **not** proof that the photograph shows it. Image search results, taxon names, and source media descriptions remain metadata-only until a human/model inspects actual pixels and verifies the exact species, anatomy, photo license, photographer credit and any copied or adapted conditions. Archive files are independent photo *candidates*; existing automations may choose/use them within their normal lanes but MUST NOT bulk-install unreviewed images or claim part-specific success just because a new archive exists.

This collector is **manual-only**, not a new sixth automation, and intentionally does not alter installed species, canonical cards, scientific HOLD decisions, or schedules. It can search species already rich in local gallery photos when more diagnostic views are desired. Check current work claims at collection and again at installation; hold `muhlenbergia-piniflora` until its source concept is resolved.

## 2026-10-16 multisource first-card clarification

The user approved replacing any **Joey-only** photo prerequisite for new canonical first cards: read `workflow/FIRST_CARD_MULTISOURCE_POLICY_20261016.md`. This archive is the **first source to check**, not a mandatory supplier of a first-card image. If a taxon has no suitable archived option, use Calvin's own authorized photos, Joey's, or properly licensed exact-species images from other sources. One physically downloaded, image-level rights-verified photo can support a **provisional** first card; photo archiving, metadata-only source matching or unreviewed GBIF labels do not count as installations. Keep individual attribution/private-use/CC BY-NC/SA restrictions intact. Diagnostic Photo Fast-Fill continues to work existing canonical galleries separately; bulk collector remains manual.


## October 16 — library-first manual selection as collection continues

The user is continuing broad photo collection and wants **plenty of options before choosing the best visual-ID images**. Keep the collector running only on its existing manually initiated schedule; do not create or reschedule a standing automation.

**New manual workflow:** Before any new manual second-photo install, check the latest actual canonical gallery/local-file counts, existing work claims, and the permanent candidate library. Use the library's *published private Release JPEGs* before searching/downloading anew. The collection index and old counts can be stale, so use fresh species files and the per-batch archive records. The initial reusable review queue is generated by `scripts/photo_library_selection_queue.py` and published at `reports/photo-library-selection-queue-latest.md` and `reports/photo-library-selection-queue-latest.json`.

**Visual selection gate:** Choose the best complementary habit/leaf/flower/fruit/detail image(s) *after viewing the actual pixels*. A metadata exact-name match, CC status, or library archive alone does not verify the plant identity or diagnostic structure. Prefer several distinct candidate observations and views over repeated shots. Keep the original media-specific photographer/license (including NC/SA), source, taxon cautions and old gallery intact. An unresolved taxon-source concept remains on HOLD. Report selected/installed separately from merely archived/staged. The five existing hourly automations retain their established scopes and schedules.

Updated: 2026-10-15

## New project decision: mass collection first, curation on demand

**This file is required reading for all ChatGPT project chats and all five existing botany automations** whenever they need images, research a taxon, build a species card, or work on family/genus visual lessons. The canonical rules in `PROJECT_RULES.md`, `workflow/COORDINATION.md`, and `workflow/PHOTO_SOURCE_AND_MANUAL_BATCH_HANDOFF_20261015.md` still apply.

**User direction (2026-10-15):** Gather as many responsibly licensed, exact-name candidate photographs as possible in large manual collection runs **now**; maintain a permanent reusable library; allow existing scheduled and manual scientific/photo-correction lanes to curate/select/install from it later. No new ten-species installation batch requirement. New species, more photos, and stronger diagnostic views can always be collected later. Do not wait to make perfect image choices during bulk gathering.

## Start here

- **Durable metadata:** `workflow/photo-library/batches/<batch-id>/candidates.csv`, `summary.json`, `selected-species.json`, `archive.json`. New catalog index: `workflow/photo-library/catalog.csv` and `species-index.json` (if generated). The per-batch files are authoritative when a consolidated index is stale.
- **Durable actual JPEGs:** compressed `photos.zip` release asset attached to a private GitHub Release tagged `hays-photo-library-<batch-id>`. See the batch `archive.json` for the asset name/tag, file integrity, and mapping; use `gh release download <tag> -p photos.zip` on an authorized repository checkout. GitHub Actions *artifacts* expire: never treat an artifact URL as the permanent photo library.
- **Manual collection workflow:** `Bulk Open Photo Candidate Harvest` and, after enabled, `Photo Library Mass Collect`. The collector gathers GBIF general and Pl@ntNet via GBIF (dataset `7a3679ef-5582-4aaa-81f0-8c2545cafc81`), which worked in a real batch without a Pl@ntNet API key. Direct Pl@ntNet DWC endpoint returned HTTP 403 with the current key; don't repeatedly retry it for ordinary collection. Record external source URL, creator, *image-level* license and provenance.
- **Additional existing source pools:** Joey's Texas iNaturalist photo CSV; Calvin's Glass Root Garden/iNaturalist photo inventory and direct private-use permission. These are **candidate inventories**, not all installed photos. Preserve Joey's CC BY-NC restrictions, Calvin's private-only direct permissions, and separate licenses. Do not silently consolidate rights into CC BY.
- **Do not re-run the same first 30 every time:** Choose eligible species that have not been batch-scanned first; prioritize live 0 local photos, then 1–2; allow explicit manual rescans / new sources / better anatomy later. Species with genuine taxonomy/source-concept holds (e.g., `muhlenbergia-piniflora`) must not be assigned a substituted species photo.
- **Live canonical installed truth:** `data/manifest.json` and real local image files. A record in this library *never* counts as an installed or verified learner photo.

## Status contract

`candidate_metadata` -> `downloaded_provisional` -> `visual_identity_and_license_verified` -> `curation_selected` -> `installed_render_tested`.

Harvest workers may set **only** the first two states. Photo/installer/lesson chats select actual views, check identity/license/claims/duplicates, preserve any copyright requirements (attribution and ShareAlike for adaptations), and run the established installer before reporting completion. A source label, AI guess, or GBIF observation name is not independent proof of botanical identity.

Every worker should **search the permanent library before requesting/download-searching new media** and may look at fresh external sources only for remaining diagnostic gaps, failed URLs, wrong labels, or unavailable images. No need to modify existing completed cards simply because new candidates exist.

## Lane-specific reading instructions

1. **Approved Taxa Installer:** query library for new accepted species aliases/exact accepted names; install only identity-checked, credited, safe images. Preserve old gallery and science.
2. **Diagnostic Photo Fast-Fill:** check photo library first, continue one independently unclaimed species per existing run. Select the missing diagnostic role; don't bulk-install the dump or claim the manual collector's scope.
3. **Family Similarity Polish:** use candidate links to locate real anatomy references; do not treat metadata labels as visual evidence or publish an unexamined photo.
4. **Genus Comparison Builder:** consult candidate images for real separating structures/look-alikes; no unverified species swap; preserve source photo rights.
5. **Taxonomy Name Fast-Pass:** use candidate names as leads only; taxonomy decisions come from authority, not image labels. Do not run photo harvest.

Keep all five schedules and existing automation scopes unchanged. There is no need for an additional scheduled automation. The collector is **manually initiated** in ChatGPT/GitHub, and does not preclaim all sparse species or interfere with other work.

## Persistence, privacy and failure gates

- The repository is currently private. If making any photo release or repository public later, reassess rights/attribution of every asset; never expose private GPS/EXIF.
- Keep large photo bytes out of the main git history; use private GitHub Release assets for durable storage. Check total archive size and ZIP integrity; preservation lasts only while repository/releases are retained.
- Only store JPEGs after valid image-byte checks and usable individual-photo permissions. Original photographer and photo license appear in the matching CSV and source page; release assets must include their metadata.
- When release upload fails, **do not** mark any row as permanently stored; fail and keep temporary Actions artifact as recovery only.
- Never overwrite or delete already installed `content/taxa/**/species.json`, existing galleries, or disputed source-concept research during mass collecting.
- Avoid exposing tokens/API keys in scripts, commit messages, job logs, or exported candidate metadata. Use GitHub Actions secret handling for any private API keys.

## Historic batches

GBIF harvest #2: 84 metadata rows, 80 staged images, 28 taxa. Public Pl@ntNet via GBIF: 26 image candidates and 26 staged images across 10 of the same taxa. **110 total candidate rows / 106 staged files**, not 106 verified or installed learner photos. Report: `reports/bulk-open-photo-gbif-plantnet-test-20261015.md`. Source GitHub artifacts expire 2026-10-29; archive them into private Release assets before that date.

If the persistent library is missing an initial batch, treat it as *not yet migrated* rather than assuming it is permanently saved.
