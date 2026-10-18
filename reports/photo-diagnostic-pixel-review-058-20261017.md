# Diagnostic photo audit — pixel-checked follow-up 058

Date: 2026-10-17 (local). Complements [full manifest audit 057](diagnostic-photo-audit-057-20261017.md).

## Correction to automated image counts

The original raster-only run counted a valid SVG illustration of *Oenothera triloba* as unreadable. The follow-up run now **parses and validates SVG separately**, giving **2,122 readable local media objects (including 1 SVG), 5 truly missing JPEG references, 0 unreadable existing assets**. Valid SVG != raster JPEG: no perceptual photo hash was inferred for the drawing.

## Broken local references — preserve provenance, do not silently delete

| Taxon | Missing gallery file | Existing valid photo count | Recovery guidance |
|---|---|---:|---|
| *Bouteloua rigidiseta* | `images/01-texas-grama-diagnostic-source.jpg` | 2 | Source USGS WARC plant-ID page; existing private Glass Root and Joey photos remain; confirm the original source file and rights before recovering |
| *Leersia oryzoides* | `images/leersia-oryzoides-panicle-matt-lavin.jpg` | 3 | Source Wikimedia Commons Matt Lavin, CC BY-SA 2.0. Reacquire the exact image with attribution if reliably available; existing habit and two newer gallery images remain |
| *Oenothera curtiflora* | `images/01-diagnostic-source.jpg` | 2 | UT Austin K12 image/source link, no stored image or image-level rights. Treat as an external research lead until download and licensing are resolved |
| *Oenothera suffulta* | `images/01-diagnostic-source.jpg` | 3 | Same UT K12 external research-only source issue; other three photos still exist |
| *Yucca constricta* | `images/01-diagnostic-source.jpg` | 2 | Wikimedia category page is not an individual image license/source. Replace only with a separately checked exact-taxon photo |

These are **five broken local gallery references**, not five completely photo-less species. Do not promote a web page or category URL into a physically installed photo. Source pages/credits and research history should be retained in a repair handoff until a licensed image actually exists.

## Actual image pixels inspected — NOT metadata guesses

### 1. *Asclepias viridis* — needs credit correction, not necessarily new flower photos

- Examined `images/04-flower-macro.png` and `images/05-diagnostic.png` at displayed image level. Both show green reflexed corolla/lobe areas and obvious central reddish-purple/pale corona structures in a tight floral cluster. The second frame includes more of the subtending broad foliage.
- This directly shows that **a photo-metadata search which fails to find the words 'corona/hood' can wrongly suggest the macro is missing**. Both images are candidates for 'Look closer / Confirm clue' captions **after source identity and botanical detail are independently reviewed**.
- In canonical `species.json`, these image entries currently contain **no creator, license or source_page**. DO NOT mark them publicly reusable or anatomy-verified until the provenance is recovered. The current flower close-ups are useful enough to investigate rather than discard.
- Additional needs: verified hood close-up with explicit corolla-versus-corona explanation, full plant habit and maturity, and a safe-source audit for all five gallery images.

### 2. *Croton monanthogynus* — foliage visible; hairs are NOT resolved

- Examined `images/glass-root-garden-665835725-leaves-and-tiny-flowers.jpg`. This is a meaningful view of branching foliage and small reproductive structures.
- But the **dark-centered stellate hairs, pistillate sepals and deeply divided styles cannot confidently be resolved** in this frame. It is a good 'Look closer' plant view, not an approved 'Confirm ID' hair macro.
- Next acquisition priority: extreme close-up of underside leaf trichomes and separately a pistillate flower/style. Preserve Glass Root Garden credit/license as already recorded.

### 3. *Quercus laceyi* — branch view is not acorn documentation

- Examined `images/05-same-tree-field-view-3.jpg`. Broad field view includes mature leaves, branch/twig and a visible catkin-like flowering structure.
- This particular photo **does not establish the acorn/cupule features**, and its original generic label gives the crew no idea what to check.
- Next: mature acorn and cup macro, bud/twig detail, blue-green leaf upper and underside alongside same-tree reference. One image's leaf appearance is not enough for exact oak ID; maintain taxonomy/source caution.

### 4. *Plectocephalus americanus* — probable redundant low-value pair confirmed

- Compared `images/03-same-plant-field-view-1.jpg` and `images/04-same-plant-field-view-2.jpg` at actual pixel level. Both show the same flower from nearly the same scene; **the second is noticeably out of focus on the flower**.
- These are distinct physical photos, not identical hash files. Keep them provisionally for archive/history but **do not count the blurry duplicate as a diagnostic second view**. Prioritize replacement with involucral bracts/phyllaries or other fine species-separating characters.
- Both source records are labeled 'all rights reserved / license not supplied by API'. Do NOT present them as public-reuse-safe. No images removed or added here.

## Follow-on manual photo work (claim-safe)

1. First resolve the five missing JPEG entries as correct image files or honest external research leads, preserving all source notes/rights. Valid SVG is *not* part of that backlog.
2. Repair missing photo provenance for the existing green-milkweed image group before changing usage/reuse claims.
3. Target real diagnostic macrophotography: *Croton monanthogynus* leaf trichomes/female styles; *Quercus laceyi* acorn cups/buds; *Plectocephalus* phyllaries; grass ligules and mature spikelets.
4. Flag older slides that overpromise identity confirmation from metadata. Use Recognize → Look closer → Confirm clue captions only when the exact feature can be found in the actual photo.
5. Keep first-card installers, five scheduled automations, source-concept HOLDs and noncommercial/private-photo rules unchanged.

Status of this report: **actual pixels inspected for six named image files** (two Asclepias, one Croton, one Quercus, two Plectocephalus); all other species-level anatomy remains queued for future visual review. No botanical or license certifications and no canonical gallery edits performed.
