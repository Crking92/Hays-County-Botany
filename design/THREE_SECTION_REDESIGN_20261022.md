# Three-section website redesign — development branch (2026-10-22)

Status: **IN PROGRESS — DO NOT MERGE/PUBLISH UNTIL QA IS COMPLETE.**

Goal: one Hays Botany site with three top-level experiences:
1. **Learner**: illustrated scrolling beginner course and species lessons; species first, then look-alikes, genus, family, additional gallery and expandable full reference.
2. **Field ID**: existing visual field-identification application; original app.js and CSS remain the engine.
3. **Quiz**: the existing mystery-plant quiz in its own page, using the existing app.js engine and an automatic first mystery plant.

Implementation in this branch:
- `index.html` is the new unified learner landing page, adapted from the user-approved prototype. It reads canonical `data/manifest.json` and per-species/genus/family JSON; it does NOT copy or mutate botanical records.
- `field-id.html` is the existing public site's original `index.html` with a small cross-section navigation bar and quiz toggle off at entry.
- `quiz.html` is that same original interface, with its quiz mode activated and a mystery plant started after the existing app finishes loading.
- The current `assets/js/app.js`, `assets/css/styles.css`, species JSON, genus/family records, images and existing photo publishing workflows are **untouched**.
- Learner reuses authorized existing photo references, image-level credits, source links and existing coordinate annotations. For cards with limited photos it shows an explicit in-progress message and never invents absent annotations.
- The standalone-file preview reads public main; on the real GitHub Pages origin (and when locally hosted for development), the new learner reads same-origin project files so incoming canonical species updates appear naturally.

Validation performed so far:
- Node JavaScript syntax check on the standalone learner script.
- Chromium automation with mocked plant data at desktop (1280px) and mobile (390px): botanical basics, species browse/search, annotated species, genus/family sections, sparse-photo fallback and navigation passed, with no JS page errors.
- The original Field ID and Quiz source pages were copied without modifications to their application engines; cross-page integrations were checked structurally but have not yet passed a complete real-data browser test.
- All changes isolated to this branch, not published by GitHub Pages.

**Required before final release**:
- Reconcile branch with the latest `main` immediately before merge. Ongoing species/grass automations must be allowed to continue; do not overwrite current records.
- Validate Field ID and Quiz against the current full production manifest and ensure the new quiz entry works on mobile.
- Validate the updated shell in a real hosted browser, with correct image URLs, mobile photo/arrow positions, original attribution and no prohibited photos.
- Run the existing rights-filtered release/preflight and confirm all public page assets; do not bypass licensing or EXIF/privacy safeguards.
- Update and test the existing service worker/cache version for the new landing page and both additional pages, otherwise returning offline users may receive an old home screen.
- Improve beginner browse with a common-name search index when available; the current manifest only supports scientific-name and genus matching.
- Verify accessible keyboard navigation and thumb-friendly touch behavior.
- Do not automatically call any species finished merely because it appears in the scrolling layout.

No automation schedules were changed by this branch.