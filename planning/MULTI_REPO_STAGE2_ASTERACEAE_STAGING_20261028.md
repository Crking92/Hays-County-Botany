# Multi-repository Stage 2 checkpoint — October 28, 2026

**STATUS:** first real family-migration staging in progress; no original-site cutover and no rules rewrite.

## Shared presentation
- Approved Asteraceae shell uses the existing Hays Botany visual design (dark green, cream, Georgia headings, responsive Learner/Field ID controls, all-plants and universal quiz navigation).
- The same shared shell has been installed in all eight additional new private family-group collections. All eight nonpublishing preview-build workflows **passed**.
- Poaceae remains an independent public repository in staging and was not modified during this Stage 2 Asteraceae pass.

## Asteraceae source migration: scientific metadata
- Original source: `Crking92/Hays-County-Botany` main commit `034f385e44cec18e8c29be96f83e22aaf78fe3f3`.
- Staging destination: `Crking92/Hays-Botany-Asteraceae`, **private** branch `staging/asteraceae-metadata`, commit `a7b767d7d831b2e2495f8809a5ab262e21df7893`.
- Source directory: 1,137 tracked files, 159,032,356 bytes: 678 metadata files (2,227,611 bytes), 459 original photographs (156,804,745 bytes).
- **678 of 678 metadata files were transferred and hash-verified** against original Git blobs.
- **180 of 180 species JSON records** are present in staged index; **45 existing genus lessons** and one family lesson copied.
- **49 of the 94 genera with installed species** have no standalone genus lesson yet. Preserve backlog; do not fabricate completed genus modules.
- **Zero photographic files** transferred, confirmed through full destination Git tree. Publication/photo rights must be checked before transfer.
- 477 photo references in species records; 448 point to physical source originals, 29 do not; 11 physical image files are not directly referenced from `species.json`. External URL references must not be misclassified as missing local files without review.
- Recorded image license claims: 38 CC0, 175 CC BY/SA, 203 CC BY-NC, 18 public-domain, 43 other. Source metadata **does not independently prove rights** and none of these is automatically publishable by this migration.
- The Asteraceae source census, full source Git-file ledger and photo-rights triage CSV reside in the staging branch under `migration/`.
- [Successful scientific metadata staging workflow](https://github.com/Crking92/Hays-Botany-Asteraceae/actions/runs/40719637225).
- [Asteraceae metadata staging branch](https://github.com/Crking92/Hays-Botany-Asteraceae/tree/staging/asteraceae-metadata).

## Next gates
1. Review the Asteraceae real-data, zero-photo learner preview before treating it as the shared content rendering standard. Still no Pages deployment.
2. Review photo rights and verify exact source for each candidate; privately archive only image bytes with documented permission, exact preserved authorship, source, license and alteration/SA conditions.
3. Reconcile missing local images vs external URLs, then add real diagnostic photo panels and visually checked anatomy arrows.
4. Verify family web site on desktop/mobile and both hub/deep-link navigation; publish only after public repository/PAGES raw asset and permissions audit.
5. Cut over only with reversible hub fallback, and then revise `PROJECT_RULES.md` and collaboration/automation instructions once architecture is approved.

No data was deleted or moved from the original hub. No Pages deployment, main-hub routing change, canonical ownership switch, project rules change or ChatGPT automation restart was made.
