# Curation queue reconciliation — 2026-10-15

## Canonical verification

GitHub `data/manifest.json` was checked on 2026-10-15 and contained 545 species, including all four taxa below. They are **already installed**; do not create new species cards or repeat curation.

| Queue taxon ID | Existing queue status | Existing canonical status | Reconciliation needed |
| --- | --- | --- | --- |
| `croton-monanthogynus` | `curated_installed` | `installed` | Add canonical ID / reconciliation marker only |
| `croton-texensis` | `curated_installed` | `installed` | Add canonical ID / reconciliation marker only |
| `euphorbia-cyathophora` | `curated_installed` | `installed` | Add canonical ID / reconciliation marker only |
| `euphorbia-marginata` | `curated_installed` | `installed` | Add canonical ID / reconciliation marker only |

The queue records already acknowledge installation. Their missing `canonical_id` and `reconciliation_status` fields are metadata drift, not missing learner species.

## Safe follow-up

A direct update of `research-queue.json` was blocked twice by connector safety checks; **no queue edit succeeded**. On the next safe queue edit, add `canonical_id` equal to the existing ID and `reconciliation_status: resolved_against_canonical_manifest` to these four records, preserving every scientific, range, approval, and photo field. Recheck current main and claims before doing so.

The inbox batch `manual-buddleja-diaperia-20261014` remains `validate_only`, with `require_exact_images: false` and no image-sources CSV. Do not mark READY or install until its owner finishes provenance and exact-photo checks.

No changes to native-range classifications, existing canonical species, galleries, UI, or formula-owned Sheet ranges were made in this reconciliation.
