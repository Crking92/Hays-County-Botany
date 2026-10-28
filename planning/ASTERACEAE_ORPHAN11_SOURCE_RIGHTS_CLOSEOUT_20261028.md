# Asteraceae orphan-photo cleanup — 11 originals checked (2026-10-28)

**Outcome: 11/11 evaluated and permanently accounted for; 0 passed the strict import gate.** No original photo deleted, and no false license promotions. The existing private test site remains at **319 actual images / 147 of 180 species with photographs**. This is intentionally not described as 11 new photographs.

## Photo-by-photo disposition

| Original species | Original filename(s) | Source provenance / reason to hold |
|---|---|---|
| *Ambrosia trifida* | `02-curated-reference.jpg` | The original `image-sources.csv` lists Eadie Schillinger, *all rights reserved*; source did not supply reuse license |
| *Cirsium texanum* | `02-curated-reference.jpg` | Original `PHOTO-SET-NOTES.txt` expressly says the Suzette Rogers photo (iNat photo 7378430) was removed October 12 because it was all rights reserved; do not re-enable |
| *Rudbeckia hirta* | `01-curated-reference.jpg`, `02-curated-reference.jpg`, `03/04/05-same-plant-field-view...` | Five leftover source photo bytes are absent from active species gallery and current image-sources CSV; earlier media notes say all-rights-reserved images from observation 398164325 were intentionally omitted. These five are **not** assumed to have current verified CC rights; held pending exact photo-by-photo evidence |
| *Simsia calva* | `02-curated-reference.jpg` | Original source CSV lists Julia Soper, all rights reserved |
| *Solidago canadensis* | `03-texas-reference.jpg` | Original CSV names iNaturalist photo 657694951 in observation 360436188, credited “lan” CC BY-NC. Current image metadata was retrieved, but its displayed image did **not** match the old archived pixels closely enough; do not substitute different photograph or miscredit |
| *Symphyotrichum subulatum* | `symphyotrichum-subulatum-provisional-face.jpg` | Commons File `SYMPHYOTRICHUM SUBULATUM.jpg` identifies Gaiacoyote and **CC0 1.0**, independently confirmed from current page and pinned [revision 1229646195](https://commons.wikimedia.org/w/index.php?title=File:SYMPHYOTRICHUM_SUBULATUM.jpg&oldid=1229646195). Both automatic metadata and alternate Wikimedia original image fetch were unavailable (HTTP errors) so original Git blob vs actual Commons image comparison **did not complete**. Keep held; this is the highest priority for a manual pixel/image-source match |
| *Tetraneuris scaposa* | `01-habit-big-bend.jpg` | Exact original creator and source not recorded in linked source metadata. Requires tracing the original photograph before reuse |

## Preservation and checks
- All 11 have immutable source file paths and original Git blob SHA in `asteraceae-full-image-asset-reconciliation.json`; source repository `Crking92/Hays-County-Botany` still owns the originals.
- Every file's explicit decision is now written in [the private Asteraceae staging ledger](https://github.com/Crking92/Hays-Botany-Asteraceae/blob/staging/asteraceae-metadata/migration/asteraceae-orphan11-all-decisions.json).
- Exact audit summary: [orphan11 summary](https://github.com/Crking92/Hays-Botany-Asteraceae/blob/staging/asteraceae-metadata/migration/asteraceae-orphan11-summary.json).
- [Successful per-file audit Action](https://github.com/Crking92/Hays-Botany-Asteraceae/actions/runs/40777355163).
- Separate gallery overrides exist as an **empty** map (no unapproved photos promoted). The real-data preview remains photo rights-filtered; no unreviewed anatomy arrows added.
- Main Hays Botany live learner, family Pages deployment, project rules, and GitHub repository visibility remain unchanged.

## Next action
Work on the remaining **33 failed source-claim candidates**, particularly the Commons creator/license mismatches and GBIF media discrepancies; alternatively supply proof/owner permission for a held file. For the single CC0 *Symphyotrichum* original, a visual comparison of the archived 44,813-byte image against the actual [Commons original](https://commons.wikimedia.org/wiki/File:SYMPHYOTRICHUM_SUBULATUM.jpg) would be the fastest manual rescue. Do not treat a CC0 license on the online file as proof that the local archived photo is the same photograph.

This closes out the orphan list's *audit*, not its *license-permitted migration*. In the 459-file physical source inventory, 319 have been transferred and 140 remain held.
