# GBIF photo harvest — manual Batch #2 review (2026-10-15)

**Run:** https://github.com/Crking92/Hays-County-Botany/actions/runs/38753278755
**Source artifact:** `hays-open-photo-review-candidates` (artifact ID `11981369634`, expires 2026-10-29)
**Coverage snapshot:** 2026-10-15T14:37:18.731902Z
**Harvest completed:** 2026-10-15T14:40:41.253209Z

## Retrieved and locally inspected

- 30 sparse-card species queried from the canonical coverage report; 28 returned image candidates.
- 84 candidate media rows across 48 distinct GBIF occurrences.
- 80 image files successfully staged; 4 candidates were *not* downloaded due to uncertain media-level licensing (occurrence-level CC0 alone is not conclusive).
- License labels in harvested metadata: 62 CC BY, 22 CC0; **only 80 have media-level license evidence** and staged image bytes.
- Primary image host: iNaturalist Open Data (80 candidates); 3 Texas Advanced Computing Center; 1 Symbiota.
- 76 candidates geolocated to Texas in metadata; remaining came from broader fallback matches.
- All 84 image URLs are distinct, but multiple images can come from the same plant/observation and be near-duplicates.
- The quick visual contact sheet reveals useful diagnostic views and some need closer morphology/identity review. **No photo is yet botanically or publicly approved just by being staged.**
- 0 canonical `species.json` files, cards, native statuses, or gallery installations modified.

## Next steps

1. Review image bytes and visible diagnostic part against exact accepted species. The 4 undownloaded candidate URLs require individual image-license verification first.
2. De-duplicate within existing galleries by actual photo ID/URL and image content.
3. Select useful diagnostic views (grass inflorescences/spikelets, woody leaves/buds, flowers, reproductive structures) rather than indiscriminate three-photo bulk installs.
4. Preserve source creator, photo URL/observation ID, **media-level** license, precise role and credit in `image-sources.csv` and `species.json`.
5. Use existing installer with active claim/manifest check, validate actual image bytes and render before counting an installation.

## Next batch

Combined GBIF + Pl@ntNet photo harvest has been triggered separately via one-time workflow, using the user's saved `PLANTNET_API_KEY` Actions secret. Its output remains candidate-only. Existing automations remain unchanged.
