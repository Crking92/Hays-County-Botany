# Helianthus photo-first field ID — image/arrow verification handoff
_Date: 2026-10-14 · UI/visual media audit, not a new taxonomy or native-range verdict._

## Scope and guardrails

Compare **Helianthus annuus** with **H. maximiliani** using the existing canonical exact-species references in `content/taxa/Asteraceae/Helianthus/`. The site now prioritizes diagnostic photo roles **in the displayed species gallery only**. Do **not** reorder `species.json` `images[]`: family lessons depend on `anchor_image_index`. All original media, licenses, credits, source pages, `public_reuse` gates, and photographs remain unchanged.

**No arrow coordinates are approved in this pass.** The scientific notes and original source descriptions corroborate the intended characters, but an annotation is only verified after someone checks the **exact rendered image** at full resolution and records the arrow's actual target coordinates on that image. No unspecified or guessed target percentages should enter `markers[]`.

## Diagnostic priority order (same instructional sequence on both species)

| Priority | Annual sunflower — existing photo | Maximilian sunflower — existing photo | Specific feature proposed for an arrow (pending visual/pixel verification) |
|---|---|---|---|
| 1 · Mid-stem leaf and vein pattern | [Harry Rose broad leaf + basal veins](https://commons.wikimedia.org/wiki/File:Helianthus_annuus_leaf2_-_Flickr_-_Macleay_Grass_Man.jpg) (CC BY 2.0; externally hosted) and [Thayne Tuason leaf](https://commons.wikimedia.org/wiki/File:Helianthus_annuus_leaf-9-16-04.jpg) (CC BY-SA 4.0; genus comparison) | Existing **02-curated-reference.jpg** (Mike Fenoglio, CC BY-NC, `public_reuse=review`) and [Matt Lavin NC State leaf insertion](https://plants.ces.ncsu.edu/plants/helianthus-maximiliani/) (CC BY-SA as recorded; externally hosted) | Annual: three strong veins diverging near blade base, broad serrated blade. Maximilian: single prominent midvein and long narrow/conduplicate leaf. Each line/label must land on a clearly visible *part*, not an assumed vein under glare. |
| 2 · Attachment at stem node | Annual Harry Rose broad leaf reference; show the actual petiole only if its base and junction are visible in the selected crop | Matt Lavin NC State **Helianthus-maximiliani-leaf-arrangement** reference: narrow leaves close to node | Annual: actual blade-to-petiole and petiole-to-stem junction; Maximilian: direct/short-stalked insertion. **Do not assert** an image shows a node junction if it is outside its crop; obtain a new matching view instead. |
| 3 · Involucre/phyllaries | [Matt Lavin underside / broad hairy phyllaries](https://commons.wikimedia.org/wiki/File:Helianthus_annuus_(5021132604).jpg) (CC BY-SA 2.0, externally hosted) | Matt Lavin NC State **Helianthus-maximiliani-calyx** reference (CC BY-SA as recorded, externally hosted) | Under a *mature head*, label one broad, rather abruptly pointed hairy annual phyllary versus one long narrow, gradually tapered Maximilian phyllary. Do not mistakenly target a yellow ray floret or overall green involucre as though it were a single phyllary. |
| 4 · Whole-plant context | Existing five original photo views (roles generic or whole-plant) | Existing five original photo views | No structural arrows needed until individual roles are verified. Use for overall habit / context; do not infer annual versus perennial from one image. |

## What is verified versus still pending

- **Existing science:** Written morphology supports broad, toothed, petiolate, usually three-basal-veined `H. annuus` and narrow, V-folded, short-stalked `H. maximiliani`; phyllaries differ in breadth and attenuation. Leaf arrangement, dark disk color, total height, number of heads, and cypsela characters **alone** do not separate this pair. This is already recorded in canonical species/genus modules.
- **Existing media and rights:** Four externally linked CC BY/CC BY-SA diagnostic references already appear in the canonical species galleries, while several installed iNaturalist images remain **CC BY-NC / public_reuse=review**. Displaying or prioritizing these pre-existing gallery references does **not** confer further redistribution rights. The genus comparison also contains a Thayne Tuason external leaf view and previously curated comparison text.
- **Source corroboration:** Matt Lavin's Commons file for the annual underside describes broad coarse-haired involucral bracts; the genus's existing comparison documents leaf/node and phyllary views. The Oklahoma State University Maximilian photo page also contains a close-up of direct leaf attachment, useful as an original-site-only check.
- **Image-level arrow verification: PENDING.** The exact four priority reference files could not be downloaded into this review runtime for full-resolution point confirmation. Existing photo-role review notes do **not** certify arrow geometry. No new overlay or verified-marker claim was made.
- **Image coverage still needed:** matched scale/angle mid-stem node photos, matched mature side/underside head close-ups, a whole-plant annual vs. returning rhizomatous patch comparison, and mature cypsela/pappus views for shared-character teaching.

## Next photo-annotation reviewer checklist

1. Open **the exact `image_url` or `file` in the current canonical module**, not a merely similar photo.
2. Confirm correct species concept, visible structure, and rights/attribution metadata.
3. Label a named structure only when it is unmistakably visible; distinguish a botanical term from a species-diagnostic comparison.
4. Record point location on actual **original image pixels** and validate normalized percentages against `object-fit` crop/contain. Test at desktop and narrow iPhone width. Do not infer coordinates from a different crop.
5. Add a one-line **where to look / why it matters** tied to the photographed target and retain the full source, creator, license, and public reuse restrictions.
6. Promote review status to verified only after the arrow visually lands on the correct part; otherwise preserve `annotation_pending` and specify the missing view.

## Changes completed in this UI pass

- Species gallery now selects **reviewed diagnostic leaf/attachment views first**, keeps the original thumbnail/face image for browse cards, sorts its swipe/thumb order in presentation only, and retains all gallery entries.
- Current chosen photo displays its role, photographer/license/source, and where available a corresponding **source-backed written morphology clue**. This is **not** a visual arrow or a promise that the character is annotated on the image.
- Image rights and all canonical records are untouched.
