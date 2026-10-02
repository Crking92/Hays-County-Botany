# Hays Botany ID — Project Rules

## Canonical project home
GitHub repository `Crking92/Hays-County-Botany` is the canonical home for botany data, learner files, workflow rules, and finalized curation packages.

Google Sheets is a coordination/status view. ZIP files and local BAT downloaders are not the primary finished product.

## Target zone
Hays, Bell, Blanco, Burnet, Comal, Concho, Crockett, Edwards, Frio, Gillespie, Bandera, Kimble, Kinney, Maverick, McCulloch, Medina, Menard, Real, San Saba, Tom Green, Travis, Uvalde, Val Verde, Williamson, Kerr.

## Native threshold and range status
A plant counts as native to the project target zone only when it is documented as native in **at least 3 target-zone counties**.

Every curated species must be assigned one of:
- **PASS** — native in at least 3 target-zone counties
- **FAIL** — evidence supports fewer than 3 target-zone counties
- **UNRESOLVED** — evidence is insufficient or conflicting

Never infer county occurrence. Do not promote an incomplete or uncertain species package to final status.

## Range authority priority
1. BONAP / NAPA
2. USDA PLANTS
3. Lady Bird Johnson Wildflower Center / NPSOT
4. Herbarium records and other authoritative regional floras
5. iNaturalist / GBIF / Leafminers as supporting occurrence evidence

Record the actual counties used for the target-zone decision.

## Required curation order
For every new species or batch:

1. Confirm accepted taxonomy, authority, synonyms, and current genus placement.
2. Apply target-zone range rules and record PASS, FAIL, or UNRESOLVED.
3. Build the morphology-first identification package.
4. Identify the most important local look-alikes and the structures that separate them.
5. Define the diagnostic image roles required for that species.
6. Select exact source photographs whenever possible and record provenance/licensing.
7. Create `species.json`, `SOURCES.txt`, and `image-sources.csv`.
8. Use a stable species ID such as `ipomoea-hederacea`.
9. Sync completed batches to this GitHub repository.
10. Let GitHub automation handle final photo downloading, resizing, folder installation, manifest generation, and validation.

## Identification method
Strict morphology first: floral and reproductive structures, phyllotaxy, leaf morphology, sap, stem features, fruit/seed structures, measurements, and diagnostic look-alikes.

Do not identify primarily by flower color.

Every learner entry should answer: **“Where should I look first?”**

## Look-alikes
Each species package should identify the most important local look-alikes and specify the exact structures that separate them.

Prefer measurable or structural differences over vague gestalt descriptions.

## Species folder standard
`species.json + SOURCES.txt + image-sources.csv + images/`

Genus-level and family-level files must be preserved and merged rather than rebuilt blindly.

## Diagnostic image roles
Choose image roles from the actual diagnostic needs of the species, for example:

- habit / whole plant
- leaves and phyllotaxy
- stem attachment / nodes
- flower front
- flower side
- calyx / sepals / phyllaries
- reproductive structures
- fruit / seed
- bark / twig / bud
- diagnostic look-alike comparison

Do not assume every species needs the same generic five-photo set.

## Image provenance
Whenever possible, select exact source photographs rather than relying on a generic search-based downloader.

For each selected photograph record:
- source platform
- observation or file ID
- photo ID when available
- creator
- license
- source page
- intended diagnostic role
- private study-use status
- public-reuse status

Private study suitability and public reuse permission are separate statuses.

## GitHub automation role
GitHub automation is responsible for the final mechanical steps:
- downloading the approved source photographs
- resizing/normalizing images
- installing images into species folders
- generating manifests
- validating file structure and required metadata

The curation layer must choose and document the photographs before automation runs.

## Google tracker role
Google Sheets is a coordination/status view only. It may summarize taxonomy, range status, curation progress, image status, and GitHub sync status, but it is not the canonical data store.

### Standing sync permission
As of 2026-10-02, Calvin has explicitly authorized ChatGPT/OpenAI curation chats to keep the Google tracker synchronized as normal project maintenance after deep review, approval, installation, taxonomy corrections, photo/provenance updates, and batch-status changes.

GitHub remains authoritative. Sheet synchronization may update the Species Tracker, Study Batches, Master Plant Pool status/notes, Family Study Index, Genus Study Index, Project Rules, and supporting lookup data as needed to mirror canonical/review state. Do not let a Sheet value override a conflicting canonical GitHub record.

Never store API keys, tokens, passwords, or other credentials in the tracker.

## Incomplete work
If taxonomy, county range, morphology, look-alikes, or image provenance is incomplete or uncertain, keep the package clearly flagged as incomplete/UNRESOLVED and do not install it as final.
