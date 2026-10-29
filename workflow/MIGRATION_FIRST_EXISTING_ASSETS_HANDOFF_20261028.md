# MIGRATION FIRST — preserve the existing Hays Botany collection (2026-10-28 evening)

> **LATEST OWNER DECISION — Oct 28:** The 56 Poaceae originals have already been byte-verified in the EXISTING PRIVATE archive at `Crking92/Hays-Botany-Monocots-Aquatics/staging/original-source-transfer/migration/poaceae-rights-held-originals`; all **1,402/1,402 Poaceae original files are preserved**, and the total project original-family inventory is **7,521/7,521 preserved across collection repos and existing private source holds**. The owner directs: **LEAVE THE 56 AS-IS; DEFER PHOTO REUSE CREDENTIALS; NO NEW REPOSITORY, NO COPYING INTO PUBLIC POACEAE, NO FURTHER LICENSE HUNT UNTIL THAT FAMILY IS REVISITED.** The older paragraph below proposing a separate new private archive is superseded and must NOT be followed. Individual records are marked in [Poaceae deferred ledger](https://github.com/Crking92/Hays-Botany-Poaceae/blob/main/migration/poaceae-originals-56-deferred-no-public-import-20261028.json). This resolves *preservation*, not public photo clearance or site readiness.


**ACTIVE PRIORITY:** Physically preserve existing botanical source content and original photographs in their assigned family repositories, or in *private and non-displayed* rights-hold archives when necessary. **Do not** begin new-photo sourcing, species expansion, genus/family lesson polishing, forced anatomical-photo completion, public Pages activation or source-ownership cutovers as part of this migration-only phase. The owner will request a family-specific QA and any new data collection when they resume work on that family.

**Scope of this directive:** This narrows migration work; it does not cancel scientific identity, provenance, copyright, current photo-publication or GitHub write-safety checks. Existing photo provenance and rights-hold ledgers must be retained unchanged. Preserve raw source bytes even when a photo cannot be shown on a website.

## Verified source-preservation checkpoint

Full original assigned-family inventory: **1,191 species / 146 families / ten collection repositories / 7,521 family-source files**.

| Collection | Original species | Original source files | Physically copied in family repository | Not copied there | Preservation location |
| --- | ---: | ---: | ---: | ---: | --- |
| Poaceae | 112 | 1,402 | 1,346 | 56 | Public `Hays-Botany-Poaceae` has the 1,346 copied files; the exact 56 held image paths/blobs are recorded in its `migration/source-file-ledger.json` and remain intact in the original hub. **This is a moving checkpoint; refresh latest ledger before any copy.** |
| Asteraceae | 180 | 1,137 | 1,137 | 0 | PRIVATE `staging/asteraceae-metadata`; 136 original images stored in non-displayed private quarantine, no public release |
| Fabaceae | 91 | 491 | 491 | 0 | PRIVATE `staging/fabaceae-metadata`; 118 original images in non-displayed private quarantine |
| Monocots-Aquatics | 113 | 587 | 587 | 0 | PRIVATE `staging/original-source-transfer`; 205 photographs quarantined |
| Lamiales | 102 | 582 | 582 | 0 | PRIVATE `staging/original-source-transfer`; 240 photographs quarantined |
| Asterid-Allies | 118 | 693 | 693 | 0 | PRIVATE `staging/original-source-transfer`; 306 photographs quarantined |
| Cacti-Buttercups | 107 | 543 | 543 | 0 | PRIVATE `staging/original-source-transfer`; 194 photographs quarantined |
| Spurges-Mallows | 130 | 764 | 764 | 0 | PRIVATE `staging/original-source-transfer`; 347 photographs quarantined |
| Trees-Shrubs | 133 | 790 | 790 | 0 | PRIVATE `staging/original-source-transfer`; 320 photographs quarantined |
| Mixed-Families | 105 | 532 | 532 | 0 | PRIVATE `staging/original-source-transfer`; 170 photographs quarantined |
| **TOTAL** | **1,191** | **7,521** | **7,465** | **56** | All 56 remaining source photos preserved in original repository |

The nine private family-group collections total **6,119 / 6,119 files physically copied and hash checked**. The public Poaceae repository's latest live ledger recorded **1,346 copied / 56 original-only images** after further rights-supported migrations by another chat; its README and original October 28 verification report can show older totals. Do not use older 224- or 58-held counts without a new read. Source-file preservation is not a declaration of field/photo completeness.

## Exact remaining obstacle: public Poaceae and unknown/limited photo reuse

`Hays-Botany-Poaceae` is a **PUBLIC repository**. Even a new branch, folder, or commit in that repository is publicly accessible, and deleting a mistakenly published photo from the default branch does not reliably remove it from repository history. Do **not** transfer the remaining 56 originally held files into that public repository without item-specific clearance merely to reach 100%.

**For an immediate bytes-only, no-licensing-decision transfer, use a separately created PRIVATE repository such as `Crking92/Hays-Botany-Poaceae-Source-Archive`** (proposed target only; creation not yet verified). Treat it as a non-displayed preservation vault: exact existing bytes and original paths or lossless reversible path map, original blob hashes, ledger, no Pages, no publication. Never combine these with gallery assets by default. The connected GitHub operations available for this pass cannot create a new private repository, so this step requires the repository owner to create one first; do not send them to a different public repository as a workaround.

Before copying, refresh `Hays-Botany-Poaceae/migration/source-file-ledger.json` and recalculate the remaining `IMAGE_HELD_IN_ORIGINAL_SOURCE_ONLY` rows. Several manual grass chats are updating this ledger; never duplicate or overwrite their work. Copy only still-untransferred source paths and verify each original Git blob hash and media byte count on destination. If a source cannot be fetched, record it as not transferred, not as complete.

## What 'transfer complete' does and does not mean

Transfer complete = original scientific and source-photo files physically replicated with verified bytes into the assigned family/private preservation destination. Site-ready means **separate**, including photo rights, public repository history, usable gallery selections, correct arrows and anatomy lessons, private/public site testing, working deep links and finally user-approved source-ownership handoff. Do not conflate them.

Shared hub-wide source files (learner code, glossary, quiz, coordination, UI, research logs, photo-policy documents and other project data outside `content/taxa`) continue to live authoritatively in `Hays-County-Botany`; the public hub has a read-only 1,191-species index but is **not** a complete clone of the original project. Do not bulk-publish restricted archives or replace the original site to chase a 'complete' number.

## Handoff for the next active family

Only when the user selects a family to work on again: refresh latest source and destination SHA and manifest, compare all new/changed original files since the pinned migration SHA, check provenance/licensing and correct learner/public site QA for that selected family. Move only deltas after review, preserve ownership and prevent concurrent overwrites. Other families remain archived without repeated photo-hunting or unnecessary rechecking.

**This document is a dated checkpoint, not an unattended automation schedule. No automation has been resumed; all existing original copies remain untouched.** Consult [multi-repo operating rules](MULTI_REPO_OPERATING_RULES_20261028.md) and [cross-chat handoffs](ACTIVE_CHAT_HANDOFFS_20261028.md).
