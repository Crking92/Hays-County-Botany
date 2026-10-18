# Photo reference cleanup 059 — no image loss

Date: 2026-10-17 (local). Work lane: diagnostic-photo QA; **not** permanent photo candidate collection.

## Canonical gallery repair results

The five entries below pointed to nonexistent JPEGs. Each was safely moved **without changing or deleting any physical photo** from the species `images[]` gallery into a new `unresolved_photo_references[]` list on the **same** species record. Every saved recovery item contains the entire original JSON record, original index, image filename, source page, any original attribution and licensing, explicit recovery requirements, and display policy.

| Species | Nonexistent JPEG moved to non-gallery reference | Real gallery photos retained | Recovery pathway |
|---|---|---:|---|
| *Bouteloua rigidiseta* | `images/01-texas-grama-diagnostic-source.jpg` | 2 | USGS WARC PlantID page; source/license and exact image unverified |
| *Leersia oryzoides* | `images/leersia-oryzoides-panicle-matt-lavin.jpg` | 3 | Exact Matt Lavin Commons image, CC BY-SA 2.0; tried restoration but Wikimedia HTTP 429 |
| *Oenothera curtiflora* | `images/01-diagnostic-source.jpg` | 2 | UT Austin plant description page is a research lead, not an individually verified/licensed JPEG |
| *Oenothera suffulta* | `images/01-diagnostic-source.jpg` | 3 | Same UT Austin source type; exact independently cleared file required |
| *Yucca constricta* | `images/01-diagnostic-source.jpg` | 2 | Wikimedia Commons taxon category is not a specific image/rights statement |

**Source history preserved:** The complete original `images[]` record is available at `unresolved_photo_references[].original_gallery_record`. It can be reintroduced to the `images[]` gallery when an actual licensed file is installed and visually screened. Keeping missing media in a live gallery caused broken images and made "number of photos" wrong. The site uses `imagesFor(sp)` to display `images[]` entries.

## Matt Lavin panicle restoration attempt

On 2026-10-17, original file and license were independently verified on the [Wikimedia Commons file page](https://commons.wikimedia.org/wiki/File:Leersia_oryzoides_(3880376141).jpg). The image shows an open *Leersia* panicle amid other marsh vegetation. Commons lists original dimensions of 2272 × 1704, credits Matt Lavin, and confirms Creative Commons BY-SA 2.0 with FlickrReview. One-time GitHub [workflow run 39084766973](https://github.com/Crking92/Hays-County-Botany/actions/runs/39084766973) was **unsuccessful**, because Commons HTTP returned 429 on each attempt. This is a download rate limit, **not** evidence of a wrong identification or copyright hold. No binary was committed; do not count as installed. The original source record is preserved in the canonical recovery queue.

## Provisional provenance of other real images

Asclepias viridis has five physically installed PNGs, but its `image-sources.csv` classifies each as `search-result-staged` and its `species.json` lacks photographer, license, source URL and source photo ID for all five. Previous visual review confirmed some useful flower/hood features, but **photo creator and public rights are not known**. Do not reuse/publish these photos outside the existing restricted/private status based solely on a visually good ID. Need original-source matching/review before reassigning rights. Another manual photo-candidate collector may work independently.

## Next steps

1. Refresh entire photo inventory to verify **zero broken currently displayed references**, without rewriting/scientifically promoting images or old source leads.
2. Recover Matt Lavin original when Commons rate limit eases, preserving required CC BY-SA 2.0 credit/license link and any processing notes. Prefer exact matching file; do not insert an arbitrary URL or substitute a different image.
3. For other four source-only leads, seek separately licensed diagnostic photos in the other chat's permanent candidate pool; verify original species, actual photographed organ and individual copyright.
4. Focus photo QA on the remaining high-value anatomical gaps: grass ligules, aster phyllaries, milkweed hoods/corona, Croton trichomes and female floral parts, oak acorn/cup details.

All five ChatGPT scheduled automations and the manual Photo Lab harvesting lane remain unchanged.
