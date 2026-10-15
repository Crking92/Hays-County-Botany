# First-photo source research — remaining hard targets (2026-10-14 Central Time)

Source: live `reports/photo-fast-fill-zero-queue.json` after external CC and Wikimedia Commons fast passes.

## Status
- 15 canonical zero-gallery entries remain after 11 previously successful external-source first-photo installations.
- 5 entries have active claims in other processes and must not be edited by this lane.
- 10 are unclaimed but the exact-name iNaturalist Research Grade CC0/CC BY/CC BY-SA search and the direct exact-scientific-name Commons-category fallback returned no immediately installable media.
- This is **not** proof suitable licensed photos do not exist. Try synonym searches, carefully verified specimen photos, appropriate educational sources, and direct rights checks. Don't install generic genus-level or parent-taxon stand-ins as exact species.

## Unclaimed exact-species photo targets
1. `erigeron-geiseri` — research trusted Flora of North America and regional herbarium specimens; avoid generic Erigeron images.
2. `symphyotrichum-lanceolatum-subsp-lanceolatum` — verify *subsp. lanceolatum* independently; species-level Aster photos are not necessarily infraspecific proof.
3. `thelesperma-megapotamicum-var-ambiguum` — Kew accepts this variety; synonyms `Thelesperma ambiguum` and `Thelesperma fraternum` may unlock images, but confirm actual variety concept. https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:250998-2
4. `physaria-sessilis` — POWO lists a relevant herbarium catalogue image. Confirm image-specific Kew permission and exact specimen before using. https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:1150625-2/images
5. `croton-capitatus` — North Carolina State Extension provides multiple photo views, including two labeled CC0 (male/female flowers and leaves), but direct S3 download URLs are signed and may expire. Verify stable source retrieval and species diagnostic concept; retain credit, source-specific license. https://plants.ces.ncsu.edu/plants/croton-capitatus/ (This species is a difficult strict identity concept; do not rely on a filename alone.)
6. `astragalus-crassicarpus-var-berlandieri` — need exact variety confirmation; species-level material alone insufficient.
7. `astragalus-nuttallianus-var-pleianthus` — need exact variety confirmation; species-level material alone insufficient.
8. `oenothera-patriciae` — prioritize authoritative flower, leaf, fruit and locality specimens.
9. `muhlenbergia-piniflora` — grass spikelet/ligule macro preferred; require current species identification.
10. `tridentopsis-buckleyana` — accepted name confirmed in POWO. Search earlier Chloris/Tridens combinations with synonym identity checks, not arbitrary Tridentopsis photos. https://powo.science.kew.org/taxon/77160904-1

## Active-claim exclusions
- `sorghastrum-elliottii` — genus comparison claim.
- `senna-pilosior`, `bouteloua-pectinata`, `eragrostis-hirsuta` — photo-fast-fill claim.
- `ammannia-auriculata` — genus lesson claim.

## Source-pass record
- `scripts/zero_photo_external_quick_fill.py`: exact Research Grade iNaturalist images with individually recorded public CC licenses; broad Texas + global; skips uncertain and occupied cards.
- `scripts/commons_first_photo_quick_batch.py`: exact scientific-name category, imageinfo and license checks; latest batch found 0 installable files for 6 unclaimed target species.
- Both preserve scientific records and avoid forcing potentially wrong photo identifications.
- Maintain first-photo provisional status and independently verify distinguishing structures in final diagnostic polish.

## Physaria sessilis media recovery (2026-10-15)
- Status: no physical image installed; gallery still empty. Canonical taxon and photo queue checked; no active taxon claim.
- Candidate: Kew POWO herbarium catalogue shows one image and a CC BY 3.0 source credit. Specimen identifier, image bytes, and photo-specific attribution not yet verified. No READY stage or external gallery link added.
- LOOK HERE FIRST: whole flowering plant with upper leaves. Missing views: upper leaf attachment, inflated fruits, stellate hairs.
- Annotation pending: true; no anatomical arrows verified.
- Blocker: no verified retrievable exact-species image file. Preserve science and all existing gallery entries; recover only after photo ID, rights, and bytes are checked.
