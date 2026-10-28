# Hays Botany — Asteraceae Stage 3 photo learner checkpoint (2026-10-28)

**STATE: REAL-PHOTO PRIVATE TEST SITE PASSED; PUBLIC GITHUB PAGES AND HUB CUTOVER NOT APPROVED OR DEPLOYED.** This is a migration checkpoint, not a `PROJECT_RULES.md` rewrite.

## Source and canonical ownership
- Original authoritative repository: `Crking92/Hays-County-Botany`, source Git commit `034f385e44cec18e8c29be96f83e22aaf78fe3f3` (pinned for byte-exact transfer).
- Private Asteraceae staging repository: `Crking92/Hays-Botany-Asteraceae`, branch `staging/asteraceae-metadata`, validated latest photo archive commit `8c6551b30a2d3f08d991a7067e7dafb508be491f`.
- 678/678 original text, source metadata, family and genus lesson files staged byte-exact; includes 180/180 `species.json` records, one family lesson, and 45 existing standalone genus lessons.
- Original source remains canonical. No hub code, search routing, public website, old photo archive, or `PROJECT_RULES.md` modified for the migration.

## Image licensing and physical storage
- Original Asteraceae source has 459 physical image files and 477 species image references.
- **82 Commons photos** verified by exact Commons File page, imageinfo license metadata, attribution matching and original Git blob SHA.
- **98 iNaturalist photos** verified by exact observation ID/photo ID, current photo license code/attribution and original Git blob SHA.
- Across both, **180 source-exact photographs are physically archived** in private Asteraceae staging. Source tree verified 180 original image files plus 180 species JSON records; no guessed source-photo rights.
- **92 of the 98 iNaturalist photos have CC BY-NC terms**: these are deliberately labeled noncommercial-only in the private site; not cleared for an unrestricted public/commercial release.
- The 180-photo review website uses optimized JPEG derivatives with metadata removed and per-photo creator, source, license and alteration notices. No unreviewed images, held original source photos or arbitrary photos are included in the site snapshot.
- **90 of 180 species** have at least one independently verified photograph; 90 remain photo-incomplete. The old source has unverified/restricted references and 29 nonlocal/unmatched image references. This is not full public-photo completeness.
- The first archive audit separately found **49 genus folders without standalone genus lessons**; keep backlog instead of inventing lessons.

## Test website
- The Asteraceae website shell preserves the main Hays Botany learner's dark-green/cream theme, familiar responsive controls, species-name search, Learner/Field ID, and working ordinary links back to the main hub plus Glossary and Quiz.
- Direct `?species=achillea-millefolium` deep links and live photograph loading verified in headless Chromium.
- Verified-photo scroller includes full role, creator, current original license and source/license links; NC-only captions explicitly warn about noncommercial restrictions. **No anatomy arrow overlays have been fabricated.**
- Latest successful **180-photo private test build**: [GitHub Actions run](https://github.com/Crking92/Hays-Botany-Asteraceae/actions/runs/40723638146). [Download test website and desktop/mobile screenshots](https://github.com/Crking92/Hays-Botany-Asteraceae/actions/runs/40723638146/artifacts/12831212655). Build contains 180 species, 180 optimized photos, 90 species with photos, and 92 NC-only photo captions.
- Windows review: download ZIP, extract, open `dist/RUN_ASTERACEAE_REVIEW.bat`; use local Python 3 server at `http://127.0.0.1:8767/?species=achillea-millefolium`. Opening `index.html` directly via `file://` is not supported because learner fetches JSON.
- No Pages deployment occurred. Separate family URL is not yet a live public website; hub search still links to the original learner.

## Remaining blockers before a real website migration
1. User review of private test site’s appearance and gallery behavior; verify common and scientific name matches and links.
2. Visually inspect existing/photo-added anatomy arrow coordinates on actual pixels and complete high-value missing diagnostics; do not count generic photo-gallery roles as anatomy-certification.
3. Source-rights and privacy release gate: decide noncommercial-only restrictions for the future public site; only verified lawful materials in both public source repository and Pages output.
4. Prepare a controlled Pages publishing workflow under the new collection, with mandatory rights-filtering, provenance checks, QA and **manual** release approval. Repository is presently PRIVATE; Pages availability depends on GitHub plan, otherwise a public repository is required.
5. Verify the actually deployed URL and deep links, add reversible all-species routing to main hub, then test hub→family→hub navigation on mobile and desktop.
6. Only after source handoff and rollback checks, revise project rules and coordination/automation ownership as the user directed.

**Do not automatically start the five paused grass automations or cut over Poaceae or Asteraceae.**
