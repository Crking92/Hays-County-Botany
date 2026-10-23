# Grass three-card completion audit — 2026-10-23

## Publication rule
100% = taxon identity resolved, species-specific photographs archived in repository with independently checked public-use licenses (CC0 / CC BY / CC BY-SA / explicit grant), habit + flowering unit + diagnostic ligule/spikelet coverage, arrows verified against actual pixels, build/deploy verified. A text lesson or external image URL alone is not completion.

## Muhlenbergia piniflora → Muhlenbergia dubia
**Name correction is warranted.** `Muhlenbergia piniflora` is an erroneous source label, not a botanical synonym; common name "pine muhly" refers to accepted `Muhlenbergia dubia E.Fourn.`. Existing `scripts/resolve_muhlenbergia_piniflora_20261019.py` prepares an atomic migration of species entry, manifest, genus, and provenance; DO NOT just rename the display field or make a duplicate species.

Source: https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:408994-1
CC0 wild photo by Patrick Alexander, verified Commons licensing: https://commons.wikimedia.org/wiki/File:Muhlenbergia_dubia_-_Flickr_-_aspidoscelis.jpg
Public-domain cultivated photo source as recorded in existing migration script: https://commons.wikimedia.org/wiki/File:Muhlenbergia_dubia_001.jpg

**Pending:** run migration in a network-enabled working tree after validating current file SHAs / no conflicting claims; actually download photographs, strip EXIF, archive them, update image-sources.csv and read back public deployment. Verify local native-zone range separately; do not silently mark county native. Existing migration script must be refreshed against current concurrent edits before use.

## Anatherum tenuispatheum
Current species gallery has 1 archived CC BY-NC source candidate: `images/inat-171915634.jpg`. Existing lesson has general gross-feature arrows, but species-voucher ID and measured reproductive anatomy unresolved. Accepted name verified: https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:77347166-1/general-information
Synonym searches: `Andropogon tenuispatheus`, `Andropogon glomeratus var. pumilus`; DO NOT mix with `Anatherum eremicum` (scabriglumis concept). Needs independently licensed, source-identified flowering habit, spathe/raceme, true membranous ligule, measured sessile spikelet / glumes and awn. Verify determinations and exact photo licenses before archiving. North Carolina flora contains labeled `A. tenuispatheum` photos but their individual reuse terms need verification: https://auth1.dpr.ncparks.gov/flora/species_account.php?id=3665

**Status:** FIELD_READY_PHOTO_GAPS; not 100%.

## Chloris andropogonoides
Current species gallery has 1 archived CC BY-NC source candidate: `images/inat-649943218.jpg`. Existing head/hub arrows do not show diagnostic sterile lemmas or mature spikelets.
**New source identified:** Smithsonian NMNH exact-species specimen, collector Victor L. Cory, Texas, 1946; Smithsonian identifies specimen media as **public domain / CC0**, with usage conditions and specimen identification.
https://www.si.edu/object/chloris-andropogonoides-e-fourn:nmnhbotany_10607789
This is a verified candidate for an authoritative herbarium panel, not yet a hosted JPG. Download precise media through its IIIF source, verify exact object ID and license, locally archive JPG and inspect visible characters before annotation. Also acquire live habit, ligule, unilateral raceme and dissected fertile/sterile lemmas with ruler; compare `C. virgata`, `C. verticillata` and `C. cucullata`.

**Status:** FIELD_READY_PHOTO_GAPS; not 100%.

## Execution result
Research audit sources and existing canonical records checked. This report is the only repository artifact submitted by this pass. **No photos installed, no canonical species edits, no name migration, and no Pages publication asserted.** All three remain blocked from 100%-complete designation by actual photo/anatomy/publication verification.
