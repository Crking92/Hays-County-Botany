# Learner diagnostic-photo roles — manual review 050

Date: 2026-10-17

## Source and boundary

Reviewed the actual contact-sheet images for [manual review 048](manual-library-review-048-20261016/preview-manifest.json) ([contact 01](manual-library-review-048-20261016/contact-01.jpg), [contact 02](manual-library-review-048-20261016/contact-02.jpg)), checked the [manual install 049 record](manual-library-install-049-20261016.json), and updated photo-specific caption text in the eight canonical `species.json` galleries below.

**Scope:** 8 canonical cards, 22 existing photos, 22 presentation-only role captions corrected. **New photos installed: 0. Removed/replaced photos: 0.** All original image files, source links, original photographer credits, individual CC licenses, taxonomy, nativity fields, and other scientific content are preserved.

The label **Recognize** means general field appearance; **Look closer** means organ detail visible in that specific image; **Confirm clue** means a promising structure appears visible and warrants further examination. **None of these labels certifies an exact taxon determination**. Existing GBIF/Pl@ntNet source IDs and independently expert-unverified source identifications remain provisional. No anatomical arrows approved.

## Species assessed and the next missing *diagnostic* views

| Species | Photos now | What this gallery helps with | Still worth photographing |
|---|---:|---|---|
| *Gelsemium sempervirens* | 2 | Yellow trumpet flowers among slender vine stems | Opposite leaves clearly attached at a node, twining/climbing habit, and a sharp flower-throat view |
| *Gleditsia triacanthos* | 4 | Tree habit, flattened pods, thorn on twig, compound foliage | Sharper thorn branching/attachment and fruit detail, plus independent taxon identity confirmation |
| *Heteropogon contortus* | 3 | Tussock habit and conspicuous long awns | **Ligule and sheath** macro, spikelet pairs with awn insertion |
| *Gamochaeta purpurea* | 3 | Small rosette and tall flowering stalk | Underside leaf wool/hairs, individual heads and involucral bracts |
| *Ranunculus macranthus* | 2 | Bright yellow flower together with lower foliage | Close basal leaves and attachments, sepals, mature achenes/receptacle |
| *Galium virgatum* | 3 | Delicate branching stems and upper leafy nodes | **Whorl arrangement and leaf count**, fruit hair texture, sufficiently sharp flowers/fruits |
| *Guaiacum angustifolium* | 2 | Purple flowers, narrow leaflets and woody fruiting branch | Fruit/capsule near-macro, leaflet undersides, stem nodes |
| *Silene antirrhina* | 3 | Seed capsule, narrow buds and fine stems | **Sticky band below upper nodes**, open petals/calyx at close range |

### Why this matters

Previously the new pictures on several cards repeated a single generic "requested diagnostic view" across different photos (for example, the seed-pod image, twig/thorn image and foliage image on *Gleditsia* all had the same caption). This has now been corrected. Captions describe the particular visible view rather than promising that each candidate depicts every requested feature. The visible gallery caption/thumbnail label field is `images[].role`; no incompatible UI fields were introduced.

### Next manual photo work

Continue 3–4 **separate, image-inspected** library-first enrichment batches, using the current manifest and unexpired species claims rather than the older 746-species queue snapshot. For each candidate, look at the pixels at sufficient magnification, check exact species/organ, image-level rights and photographer, choose distinct views, then install only after duplicate checks and GitHub verification. Prioritize specimens showing structures that separate look-alikes, not extra general overviews. After those batches, do a full cross-learner diagnostic-photo audit for missing organs, duplicate perspectives, wrong plant parts, provisional ID/credit issues, and misleading photo arrows.

No changes to any of the five scheduled automations.
