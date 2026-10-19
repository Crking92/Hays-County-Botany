# Phase 3 first-card continuation — verified checkpoint, October 18–19, 2026

## Latest verified state
- Canonical learner manifest: **1,119** species, read from `data/manifest.json` after completed workflow run 39201037290.
- Working Phase 3 distinct accepted-name source concepts left uninstalled: **66**; **41** have simple binomial names and **25** are more complicated infraspecific/hybrid concepts. These are candidate identities, **not 66 guaranteed new cards**; final synonym and identity checks may lower total.
- The previously noted **12 separate taxonomy/identity holds** remain outside this working candidate backlog; do not force them through.
- County nativity review remains paused; keep recorded range metadata and comparisons accurate.

## This continuation's verified installations
1. `reports/phase3-accepted-firstcard-002-installed.json`: 16 verified species, 16 physically stored attributed provisional photographs, 7 blocked by no exact accepted rank taxon in iNaturalist.
2. `reports/phase3-accepted-firstcard-003-installed.json`: 3 verified species, 3 physical photos, 13 held (12 exact name/rank lookup misses and one `HOLD_NOT_PREFLIGHT_CLEARED`).
3. `reports/phase3-synonym-photo-001-installed.json`: 10 verified species, 10 physical photos; **Thelypteris ovata** remained `NEEDS_FIRST_PHOTO_OR_SOURCE_CHECK`.
Total this continuation: **29 new verified cards and 29 photos**, from 1,090 to 1,119. Live counts may change when other workers install new species; refresh before selecting.

## Kew synonym-photo method that succeeded
`workflow/phase3-synonym-photo-001-20261018.json` contains the accepted-name-to-source-name crosswalk and a Kew name reference for each of 11 candidates. `scripts/phase3_synonym_photo_001.py` enforces an exact iNaturalist species-rank match on the **documented source synonym**, usable image bytes and individual photo-level licensing, preserves accepted scientific name in the canonical learner, saves searched synonym in `species.json` and original photo name/evidence in `SOURCES.txt`. Independently verified examples:
- `Muenchhusia moscheutos` ← `Hibiscus moscheutos`
- `Hemionitis alabamensis` ← `Myriopteris alabamensis`
- `Aquarius cordifolius` ← `Echinodorus cordifolius`
Other installed matches are in the report. These are **provisional first photos, not verified diagnostic organ assignments**.

## Remaining work / handoff
- **Media/taxonomy bridge**: prioritize `Thelypteris ovata` / `Christella ovata` (Kew equivalent, but not an exact iNaturalist species result), `Cleome dodecandra`, `Hedeoma serpyllifolia`, `Lappula texana`, `Sclerocactus warnockii`, `Munroa pulchella`, `Cleome trachysperma`, and `Valeriana amarella` using accepted name and known synonyms. Do not treat a Kew synonym as proof that any arbitrary photo depicts the right taxon.
- Review valid image-level licensed GBIF / project library / original iNaturalist imagery, source concepts and duplicate parent/subspecies mapping. If unverifiable, keep precise `NEEDS_FIRST_PHOTO` or identity HOLD instead of forcing a card.
- Keep the five scheduled botany automation scopes and Cloudflare disconnection unchanged. Do not re-run completed batches or overwrite their canonical cards.
- For remaining simple names, check current `data/manifest.json`, `workflow/work-claims.json`, `research-queue.json` and existing drafts/inbox before any install.
