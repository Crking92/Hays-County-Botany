# Phase 3 first-card continuation — verified checkpoint, October 18–19, 2026

## Fresh verified handoff — October 19, 2026 (batch 004 + synonym batch 002)
- Canonical `data/manifest.json`: **1,137 species**, confirmed after commit `981eb03a9c`. Earlier 1,119 / 66-backlog values below are historical snapshots, not the current count.
- Another lane's `reports/phase3-accepted-firstcard-004-installed.json` independently installed **13** provisional first-photo cards (1,120 → 1,133); that work must not be repeated.
- This recovery lane created `workflow/phase3-synonym-photo-002-20261019.json`, `scripts/phase3_synonym_photo_002.py`, and `.github/workflows/phase3-synonym-photo-002.yml`. GitHub run [39258653397](https://github.com/Crking92/Hays-County-Botany/actions/runs/39258653397) **succeeded**, committing **4/4 newly installed** provisional cards and **4/4 physically present photo files** (1,133 → 1,137) in `reports/phase3-synonym-photo-002-installed.json`. No blocked records.
- `Valeriana amarella` ← `Valerianella amarella` — iNaturalist photo 7237652, Chuck Sexton, CC BY-NC.
- `Munroa pulchella` ← `Dasyochloa pulchella` — iNaturalist photo 227453246, Don Rideout, CC BY-NC.
- `Sclerocactus warnockii` ← `Echinomastus warnockii` — iNaturalist photo 637939830, Michelle W., CC BY.
- `Thelypteris ovata` ← `Pelazoneuron ovatum` — iNaturalist photo 336557398, Turner Brockman, CC BY-SA. Do **not** substitute `Thelypteris ovata var. lindheimeri`; Kew maps it to distinct `Thelypteris lindheimeri`.
- Remaining media/name questions: `Cleome dodecandra` and `Cleome trachysperma` are distinct under Kew; iNaturalist's broader `Polanisia dodecandra` species concept could mix them, so require verified infraspecific resolution rather than selecting a random species photo. `Hedeoma serpyllifolia` has a Kew-documented infraspecific synonym but no verified species-rank photo bridge; `Lappula texana` similarly remains unresolved.
- Preserve 12 separately held source concepts unless specifically cleared, and keep paused county nativity audits, existing five automations, other worker claims, and Cloudflare-disconnected setup unchanged. Recalculate remaining candidate count against the live manifest and merged claims rather than subtracting unverified counts.


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
