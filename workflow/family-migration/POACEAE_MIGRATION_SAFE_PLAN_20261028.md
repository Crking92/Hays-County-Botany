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
- Select source `content/taxa/Poaceae/**`, including *every* real file, raw photo (including unpublished restricted-source material), `species.json`, family/genus records and provenance. Preserve folder-relative path until new site links are audited.
- Include required shared website code, glossary links, taxon indices, and build scripts by explicit dependency inventory, not wholesale blind copy.
- Preserve all per-image creator/license/restriction fields and source links. Source image rights do NOT automatically authorize publishing on a new website. New site must run its own photo-rights preflight with site-specific grants reviewed.
- Initial staging can be a content-only destination: do not switch public homepage or search until links, annotations and dependencies pass.
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
The currently available connected GitHub actions can read/write to existing repositories but do not expose an operation to create a new repository. The owner must create blank `Crking92/Hays-Botany-Poaceae` from GitHub's New repository page (public if using Free Pages), without initializing README/license/gitignore, then authorize the connected GitHub app for the new repo if access is scoped. Never send a token/password in chat.
No upload/copy has been run yet. No original records have been deleted.
