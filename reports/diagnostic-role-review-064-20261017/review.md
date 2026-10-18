# Existing-gallery diagnostic review 064 — grass hairs and composite flower IDs

Reviewed 2026-10-17 local, against current 855-species manifest at selection time. Continuation of the existing-photo diagnostic lesson lane; separate photo-harvesting work was not touched.

## Commit/readback-verified result

- **4 canonical species reviewed, 14 existing photographs individually represented on two saved contact sheets.**
- **13 original gallery `images[].role` captions improved**, each based on actual reviewed image content.
- **1 misleading mixed-scene image moved out of active *Solidago canadensis* gallery into a reversible `unresolved_photo_references[]` identity hold**. The original JPEG remains physically in the repository and its entire creator/license/source/photo-ID JSON record is preserved on the species card.
- Active galleries contain **13 photos after the hold**; no image binaries were created, deleted, renamed, or replaced, and no species science/nativity/taxonomic status was edited.
- The original source media may have provisional IDs; identifying a useful photographed structure does **not** independently verify the species determination.

| Species | Initial photos | Current active gallery | Revised captions | What the images genuinely show | Still needed |
|---|---:|---:|---:|---|---|
| *Bouteloua hirsuta* — hairy grama | 3 | 3 | 3 | Very long **spreading hairs on comb-like flowering branches**, narrow projecting branch tip, hanging anthers | Clear ligule/blade–sheath junction, whole tussock, careful macro distinguishing hairs on glumes vs branch parts |
| *Eragrostis hirsuta* — hairy lovegrass | 3 | 3 | 3 | **Dense long hairs on leaf sheaths near the base** (image 0, visually inspected at full resolution), delicate airy panicle, narrow spikelets | Branch axil beard and collar/ligule close-up, scale-matched spikelet details |
| *Solidago canadensis* — Canada goldenrod | 3 | 2 | 2 | Arching yellow flowering sprays and narrow green leaves in two usable frames | Matched lower-stem indumentum, mature leaf margins/undersides and head/phyllaries to separate *S. altissima* and *S. gigantea* |
| *Symphyotrichum divaricatum* | 5 | 5 | 5 | Small lavender-rayed flowerheads and yellow disks, slender stems, narrow foliage, branching/ground habit | Clear underside of involucre and phyllary arrangement, leaf attachment and fine stem hairs for species-level comparison |

## One important image-ID quarantine

The [third *Solidago canadensis* gallery image](../../content/taxa/Asteraceae/Solidago/solidago-canadensis/species.json), saved originally as `images/03-texas-reference.jpg` with iNaturalist observation **360436188** / photo **657694951**, was inspected at original image size. The composition is **dominated by pink-white evening-primrose-like flowers** and mixed vegetation. Although there may be other green plants present, a diagnostic Canada goldenrod subject **cannot be established from those pixels**.

That photograph was **not deleted or assigned to another taxon**. The exact original creator, CC BY-NC designation, iNaturalist observation/photo IDs, file reference, and reuse status are preserved in `unresolved_photo_references[]` with status `PHOTO_IDENTITY_HOLD_MIXED_SCENE`. The original JPEG also remains in `images/` in GitHub, but is no longer in active `images[]`. Restore **only** after checking what the original source observation identified and whether the pictured goldenrod subject is unambiguous. Pink primrose-like flowers must not be presented as goldenrod flowers.

## Contact sheet and exact provenance

- [Sheet 01 — hairy grama and hairy lovegrass](contact-01.jpg)
- [Sheet 02 — Canada goldenrod and *Symphyotrichum*](contact-02.jpg)
- [Original gallery manifest](view-manifest.json)

Full-size photo checks included hairy grama's flowering-branch hairs, hairy lovegrass's leaf-sheath hairs and two panicle views, the Canada goldenrod mixed scene, and a small *Symphyotrichum* flower head and branching stems. Remaining frames were examined on saved contact sheets; no artificial arrows or specialist microscopic character confirmation added.

All gallery entries retained their original photographer, source, license, and image ordering (apart from the single separately preserved hold). The separate Photo Lab harvest pipeline and five existing scheduled automations were not changed.

**Next diagnostic work:** close/inspect **grass ligules and panicle branch axil hairs**, **Solidago lower-stem hairs and leaf undersides**, and **aster phyllaries** before giving those structures Confirm-ID labels. Do not treat existing generic role metadata as proof a microscopic feature appears in a photograph.
