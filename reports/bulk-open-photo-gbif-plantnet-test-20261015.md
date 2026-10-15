# Open photo sourcing — GBIF + Pl@ntNet test report (2026-10-15)

## Working results — download/review stage only

| Lane | Run | Candidate media | Locally staged JPEGs | Taxa represented | Source-level image permission |
|---|---|---:|---:|---:|---|
| GBIF general | [run #2](https://github.com/Crking92/Hays-County-Botany/actions/runs/38753278755) | 84 | 80 | 28 | 80 media-level CC BY/CC0; 4 occurrence-license-only links withheld |
| Pl@ntNet via public GBIF observations | [public dataset test](https://github.com/Crking92/Hays-County-Botany/actions/runs/38756305154) | 26 | 26 | 10 (all overlap the GBIF 28 species) | 26 photo-level CC BY-SA |

**Unique combined result** (do **not** double-count the redundant GBIF rows from combined run): **110 source candidates, 106 successfully staged and SHA256-distinct images, 28 species with at least one candidate.** This is *not* an installed learner-card count. Identity/source/photo-role review still pending.

- Combined two-source API attempt: https://github.com/Crking92/Hays-County-Botany/actions/runs/38754721380 (GBIF succeeded but direct Pl@ntNet DWC requests failed). The 84 GBIF results in that attempt duplicate the first GBIF harvest and are excluded from combined unique statistics.
- Pl@ntNet secret test: https://github.com/Crking92/Hays-County-Botany/actions/runs/38755587848. Pl@ntNet `/v2/projects` returned HTTP **200** (key recognized for general API); `/v2/dwc/occurrence/search` returned HTTP **403** for a basic search and **400** with extra filters. The exact account entitlement/rejection reason is not established; **do not request payment or re-expose the secret**. The harvester now performs one safe DWC preflight and skips 30 repetitive denied calls.
- Public Pl@ntNet dataset: https://www.gbif.org/dataset/7a3679ef-5582-4aaa-81f0-8c2545cafc81, DOI 10.15468/gtebaa. This dataset contains community-validated observations with sharable images. Photograph permission is **not** inherited from the dataset's CC BY metadata; check each `media` CC BY-SA or other image rights and credit the photographer + Pl@ntNet.
- The working manual GitHub action now exposes `plantnet-gbif` (no key), plus `gbif`, `plantnet` (direct API), and `both`. With `both`, it can retrieve GBIF and Pl@ntNet-via-GBIF candidates even when direct DWC access is denied.

## Curation / installation remaining

1. Visual diagnosis against exact accepted species, reject misidentifications and suspect taxon concepts, and choose complementary diagnostic parts rather than near-identical plant shots.
2. Recheck photographer and media rights, source/photo IDs, existing gallery duplication and work claims.
3. Put selected images through the normal image installer, write `images[]` and per-photo provenance, verify image bytes and learner rendering.
4. Preserve all scientific HOLD/FAIL statuses, existing galleries, active task boundaries, and manual-only batch ownership.

No canonical card, public webpage, or photo-credit record was edited by the harvesting workflows. This report intentionally distinguishes discovered, downloaded/staged, verified and installed images.
