# Oxalis bulbous pair — installed and reconciled

**Current state verified 2026-10-14 (America/Chicago): both species are canonical. Do not resubmit READY or create duplicate cards.**

- `oxalis-drummondii` — installed at `content/taxa/Oxalidaceae/Oxalis/oxalis-drummondii/species.json`; two licensed Jim Conrad public-domain photograph records: flower/leaf habit and flower side. **Neither proves the bulb or sepal-tip tubercles.**
- `oxalis-violacea` — installed at `content/taxa/Oxalidaceae/Oxalis/oxalis-violacea/species.json`; two licensed Wikimedia Commons photograph records: flowering habit (CC BY-SA 3.0) and flower/leaves (CC BY 3.0).
- Both retain **UNRESOLVED** target-native range labels; neither is counted as a confirmed target-zone native.
- Installation commit `957b049ad7e41af5ed14eafc94956f8df42008ad` created READY; GitHub Actions runs `38497505497` and `38500163970` each report a completed successful curate job. Current canonical manifest has **531** species.
- The most recent `reports/last-curation-run.json` at inspection was a separate diagnostic-photo batch for `justicia-americana`, with no Oxalis reinstallation.

## Diagnostic Photo Polish handoff (not installed/verified views)

Seek exact-species, rights-cleared macro photographs showing: bulb and basal attachment (both); matched leaflet notch and oxalate-line views (both); sepal-tip detail where diagnostic (*O. drummondii*); and mature capsule/fruit views (both). Compare side-by-side at matched scale. Existing images are installed gallery records; these requested views are **needs_photo**, not completed photos or verified arrow targets. Annotation state remains **annotation_pending** until the actual anatomy and coordinates are checked. Preserve all installed gallery records, creators, source pages, licenses and reuse restrictions during enrichment.

## Curation/coordination cleanup

The historical claim `approved-installer-oxalis-bulbous-pair-20261013-001` expired 2026-10-13 20:49:22 -0500. Its two taxa are installed. On 2026-10-14 the installer tried a normal claim release and a minimal status-only retry; both `workflow/work-claims.json` updates were rejected by connector safety checks on the large file. The claim must be treated as **expired/superseded by canonical installation**, not an active lock. Do not repeatedly rewrite the entire claims file solely for this claim.

Separate installed comparison records `euphorbia-heterophylla` and `abutilon-theophrasti` still have legacy queue notes saying “READY FOR COMPARISON CURATION” despite their installed statuses; when a safe targeted queue write is available, reconcile those notes and `canonical_id` identity fields only. Do not reinstall, relabel native-range status, or overwrite formula-owned Sheet ranges.

## Historical handoff

The original staging pass reported 520 species, a queued Action, and a missing *O. drummondii* photo. Those statements were **superseded** by successful installation and the two actual gallery photographs documented above.
