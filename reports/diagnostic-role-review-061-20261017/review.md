# Manual existing-photo diagnostic-role review 061

Reviewed: 2026-10-17 local. Follows the [full technical audit 057](../diagnostic-photo-audit-057-20261017.md) and the [missing-reference cleanup 059](../photo-missing-reference-cleanup-059-20261017.md).

**Actual image pixels were screened:** all 34 existing installed images across eight species on four [contact sheets](contact-01.jpg) ([sheet 2](contact-02.jpg), [sheet 3](contact-03.jpg), [sheet 4](contact-04.jpg)). Several key original-resolution files were also individually inspected. Seven canonical `species.json` cards received **31 distinct image-specific `images[].role` captions**. The eighth, *Matelea reticulata*, already had meaningful part-specific captions and was not rewritten.

## Precise outcome

| Taxon | Existing image labels clarified | What the actual gallery can teach | Priority remaining structure |
|---|---:|---|---|
| *Bouteloua curtipendula* | 4 | One-sided drooping flowering racemes; red anthers; leaf blade held for scale | **Ligule / blade-sheath collar and close spikelets** — no clear confirmation macro in these four photos |
| *Asclepias asperula* | 5 | Narrow leaves and growth habit, flower clusters/buds and tapered follicle | **Individual corona hoods and central flower structures** at useful resolution; field comparisons with *A. viridis* |
| *Coreopsis basalis* | 5 | Yellow head, darker disk, divided narrow leaf segments, whole plant among grasses | **Involucral bracts/phyllaries and fruit**, with photographic tie-breaker versus *C. tinctoria* |
| *Croton texensis* | 3 | Narrow-leaved sandy-soil habit, **staminate/male flowers with obvious exserted stamens** | **Pistillate/female flowers, warty mature capsules** and separate female plant; do not pretend the male flower frames prove the fruit |
| *Solidago altissima* | 5 | Tall arching plume, leaf underside/venation, flowering branches and general stem | **Lower stem hair density, mature mid-stem leaf underside and head/phyllary macro** for comparisons to giant/Canada goldenrod |
| *Euphorbia cyathophora* | 3 | Red upper bracts, growing plant, round green capsules and reproductive upper branches | **Individual cyathium gland, its margin/shape, and capsule hairlessness at macro scale** |
| *Quercus laceyi* | 6 | **Acorn in textured cup already exists** (gallery index 0); leaf, tree crown, bark and flowering twig all represented | Better copyright-cleared acorn/cup view, measured mature acorn and bud twig; documented image 0 rights need checking |
| *Matelea reticulata* | **0 (already well described)** | Front and underside of green reticulated corolla, netting and central pale structure visible in Joey video frames | Whole vine/leaves, mature fruit and detailed independent floral structure verification; frames remain private study only |

## Specific discovery that changes the work queue

The existing Lacey oak **index 0 image contains an acorn with a visibly textured cup** and green lobed leaves. The earlier automatic audit missed it because the metadata merely said `curated taxon reference`. **The problem was a label, not a missing photograph.** That image is source-marked **all rights reserved/license not supplied**, and this review does not grant new rights or certify public display. A comparable explicitly licensed acorn image is still desirable before unrestricted publication.

The two close Joey Santore photos of *Croton texensis* are valuable **male/staminate flower** lessons, not a pistillate or fruit example. New captions identify that fact, preserving Joey's CC BY-NC terms.

The *Euphorbia cyathophora* green spherical structures in index 1 are prominent **developing fruit capsules**. Their visibility does not prove the fine cyathial gland details needed for species confirmation.

In *Solidago altissima*, the existing close leaf photo does show venation and fine marginal hairs, but there is **no lower-stem hair photo** adequate to separate the difficult goldenrod complex.

## Verification levels and remaining boundaries

- Actual contact-sheet pixels inspected for **all eight galleries**; higher resolution separately inspected for sideoats flowering, Croton staminate flowers, Lacey oak acorn, goldenrod leaf detail and *Euphorbia* capsules.
- The labels **Recognize**, **Look closer** and **Confirm clue** describe image usefulness, **not** an independently expert-certified species determination. In particular the source-observation taxon assignments still have their original status.
- No new photos harvested, no extra `images[]` entries, **no image removed, no credits/licenses changed, no cultivar/range or taxonomy fields edited, and no anatomical arrows added**.
- Some sources are **CC BY-NC, private study or all rights reserved**. Do not reuse them publicly on the strength of these captions. Source-level licensing and intended publication remain separate review steps.
- Avoid misreading multiple photos from the same observation as independent identity confirmations.

## Next high-value targets

1. Move to a second image-level gallery pass among 3+ photo species with generic labels; rank by visible organ gaps instead of raw photo count.
2. First-useful macro list: Poaceae ligules/spikelets; *Asclepias* hoods/corona; *Croton* pistillate flowers and mature capsules; *Coreopsis* phyllaries; *Solidago* stem-hairs; *Euphorbia* cyathial glands; oak buds/acorns with clear rights.
3. In the separate photo-collecting chat, archived media can be sourced for these **requested** organs, but an archive's `wanted_parts` label does not prove a photo shows the organ. Every candidate still requires actual-image inspection.
4. Next edits here will remain existing-photo labeling and QA only. Honor active claims and leave the five scheduled automations unchanged.

**Full list of inspected galleries and original image provenance:** [view-manifest.json](view-manifest.json). 
