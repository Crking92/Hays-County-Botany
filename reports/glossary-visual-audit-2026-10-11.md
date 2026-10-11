# Glossary visual-audit checkpoint — 2026-10-11

Scope: website glossary only (`data/learning-layer.json > terms`, `assets/js/app.js`, `assets/css/styles.css`). Does not modify canonical taxa, range decisions, curation, research queue, or images.

## Baseline from live main
- 147 glossary entries.
- 126 entries use real-photo source records; 21 use diagrams as primary visual.
- 147 entries contain at least one annotation in `real_photo.annotations`; zero numeric coordinates fall outside 0–100.
- Most photo records reference Wikimedia Commons file pages, resolved by `familyExternalImageUrl()` to the associated image.
- **The coordinate check does not prove that an arrow lands on the correct organ**; image content and annotations need manual visual review.
- Some real-photo records also have a supplementary diagram (`visual`).
- The glossary uses the same overlay method in term modals and the reveal phase of the visual term drill.

## High-severity presentation defect
Existing CSS fits photos with `object-fit:contain` and sometimes caps image height, while the annotation SVG and labels are absolutely positioned across the **entire image element/container**. On nonmatching aspect ratios, displayed image pixels occupy only part of the element. Annotations can point into letterboxed space or to the wrong plant structure, especially on mobile and in term drills.

Repair goal: calculate the actual rendered image *content box* from the intrinsic source width/height, element bounds, and `object-fit`; position the annotation coordinate overlay exactly on that content rectangle, and recalculate on load / viewport resizing / modal rerender. Leave source photos and attribution intact.

## Manual photo/arrow review queue (priority order)
1. **Attachment/structure:** opposite, alternate, whorled, decussate, petiole, sessile, node, leaf-sheath, collar, ligule, stipule, bract.
2. **Flowers:** calyx versus sepal, petal/corolla, receptacle, superior/inferior ovary, staminal-column, style/stigma, hypanthium.
3. **Asteraceae:** phyllary/involucre, capitulum, ray-floret/disc-floret, pappus, cypsela.
4. **Grasses:** spikelet, glume, lemma, palea, awn, culm.
5. **Milkweeds:** corona, hood, horn, gynostegium, pollinium, corpusculum, pollinarium.
6. **Hair surfaces / fruits:** pubescent, glabrous, stellate-hair, and fruit types.

Review each arrow against the **exact full-resolution photograph**, not only the Commons caption; inspect tip and label position at phone and desktop widths. Do not mark a photo/annotation as individually verified until viewed. Replace an ambiguous image before moving the arrow.

## Missing / underrepresented essential vocabulary (first-pass candidates; not yet installed)
- Stem/leaf basics: **internode, axil, axillary bud, terminal bud, lamina/leaf blade, midrib, leaf margin, leaf apex, leaf base, abaxial, adaxial, basal, cauline, compound leaf, simple leaf, palmate, pinnate venation**.
- Leaf shapes/margins: **linear, oblanceolate, elliptic, obovate, oblong, cordate, sagittate, entire, dentate, crenate, undulate, lobed, acute, acuminate**.
- Surface hairs: **hirsute, villous, tomentose, strigose, hispid, scabrous, glandular hair**.
- Flower anatomy: **peduncle, pedicel, stamen, filament, anther, pollen, pistil, carpel, ovary, style, stigma, actinomorphic, anther dehiscence**.
- Inflorescences: **panicle, spike, cyme, corymb, head** (head may be served by capitulum depending on lesson).
- Roots/reproduction/other: **taproot, fibrous root, stolon, bulb, tuber, corm, silique, silicle, perigynium, fruit, seed, annual, perennial, biennial, tree, shrub, forb, vine**.

Some listed concepts overlap existing advanced vocabulary; prioritize field-useful, clearly photographable basics. Never add a text-only term and call it visual-complete.

## Editorial flags
- Current `node` entry defines a node only as a *grass* stem joint; botanical node is broader (leaf/bud/branch attachment on stems in general). Keep grass image as a valid example, but generalize the definition.
- `disc-floret` should include `disk floret` as a search alias; both spellings occur in botany resources.
- For non-local example plants, retain explicit labels as *structure demonstration only*, not evidence of Hays County nativity.

## Completion statuses
- Structural geometry: engineering fix must be committed and read back before marking shipped.
- Term/arrow specific corrections: pending manual visual source verification.
- Glossary completeness: first-pass gap checklist only, not exhaustively complete.
