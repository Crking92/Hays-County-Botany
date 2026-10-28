# Family repository migration — non-destructive handoff plan
Checkpoint date: 2026-10-28.
Original project: https://github.com/Crking92/Hays-County-Botany
Snapshot source commit: `d5812999ea32d03b873110db1a526e20ac6ea730`
Frozen recovery branch: `migration-snapshot-20261028`
Preparation branch: `migration-prep-20261028`
First target repository name: `Hays-Botany-Poaceae` (destination not created by this plan).

## DO NOT MODIFY ORIGINAL PRODUCTION
- Original `main` and existing Pages site must continue to work during migration.
- Source currently canonical for all families. No original images/records/history deleted or moved.
- Five ChatGPT grass automations paused on 2026-10-28 at user request; avoid concurrent editorial edits.
- GitHub Actions independent scheduled/push workflows may continue; audit those separately before any final synchronization.
- Desktop/OneDrive backup must be completed and independently verified, and preferably a second archive outside OneDrive retained.
- Never use force pushes or destructive history rewrites as part of phase one.
- Do not claim verified when an upload or website deployment remains pending.

## First pilot: Poaceae
- Inventory source `content/taxa/Poaceae/**` completely, including published/restricted photo sources, species records and provenance. Copy every **publishable** byte into the future public family repo; keep all restricted/uncertain media in the unchanged original and separate full backup (or later private archive). Track every excluded file and reason; full source byte-check is for an archival copy only, not a rights-filtered public export.
- Include required shared website code, glossary links, taxon indices, and build scripts by explicit dependency inventory, not wholesale blind copy.
- Preserve every carried-forward creator/license/restriction field and source link. Source rights do NOT automatically authorize public use on another website. New site must run rights preflight with site-specific grants reviewed; **never commit held/unlicensed photos into a future public repo, even temporarily, because deleting them later does not remove Git history**.
- Initial staging can be a content-only public destination comprised solely of verified publicly reusable content: do not switch homepage or search until links, annotations, exclusion ledger and dependencies pass.
- New repository must avoid importing original `.git` history, unrelated families, private review data, or unneeded artifacts. Build clean new history after verifying source snapshot and destination contents.
- Keep an independent archive of all original sources including restricted photos and unpublished records rather than dropping held research.

## Required transfer audit, before cutover
1. Record original `main` source SHA and each destination import commit SHA.
2. Enumerate every file path, length, SHA-256. Compare source Poaceae files byte-for-byte against destination (allow a separate explicit list for intentional path changes).
3. Check 112 installed species at prior checkpoint, 53 genera, every image record, each cited photo file, every anatomy marker coordinate, learning steps, citations, names and comparison links against live manifest (counts may be higher on migration date).
4. Confirm every photo referenced by a lesson loads, licenses remain correct, rights-checks for a new site pass, and no human-only photo research file is leaked to public site.
5. Run mobile Learner, Field ID and Quiz checks, including cross-family look-alikes and universal glossary navigation.
6. Sync new edits since snapshot, then run a second byte-level audit against a *new pinned* source SHA.
7. Publish dedicated Poaceae Pages site only after the new pages artifact is below 1 GB and passes photo QA. Test using an unpublished preview where possible.
8. Main hub integration: link Search/Field ID/Quiz to the new site's Poaceae lessons. Hold original publicly accessible as rollback while verifying user experience.
9. Record final sign-off; only afterward consider removing *redundant current source* (not history rewriting), first with separate backup and explicit approval.

## Manual setup barrier
The currently connected GitHub actions can read/write to existing repositories but cannot create a new repository. The owner must create blank `Crking92/Hays-Botany-Poaceae` using GitHub's New repository page, **PUBLIC only for a clean, rights-filtered destination** (never first copy copyright-held originals into its Git history). Leave README/license/gitignore unchecked, and authorize the connected GitHub app for the new repo if access is scoped. Never send a token/password in chat. The frozen original and independent ZIP remain the complete source archive while restricted evidence is separately retained.
No upload/copy has been run yet. No original records have been deleted.
