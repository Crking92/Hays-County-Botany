# Open-photo bulk candidate harvest — manual workflow (2026-10-15)

This is a **manual, review-first** way to source additional photographs for the Hays County Botany learner. It does not modify canonical `species.json`, images, manifests, scientific conclusions, five existing scheduled automations, or any work claims.

## Run the first batch

Open GitHub → Actions → **Bulk Open Photo Candidate Harvest** → **Run workflow**. Suggested first run:

- `source: gbif` (no API key)
- `limit: 30`
- `per_species: 3`
- `max_local: 2`
- `species: [blank]`
- `download: true`

The run generates the **hays-open-photo-review-candidates** artifact (available from the completed Actions run for 14 days): `candidates.csv`, `summary.json`, and a `staged_images/` folder for photographs with suitable **media-level or Pl@ntNet observation-level** license metadata. It does **not** install or publish any of these images.

For local command-line use from the repository root:

```bash
python -m pip install Pillow
python scripts/bulk_open_photo_harvest.py --source gbif --limit 30 --per-species 3 --download
```

The default output directory is `workflow/open-photo-candidates/manual-latest`.

## Public Pl@ntNet photos through GBIF (recommended)

**This route worked in an actual GitHub Actions run on 2026-10-15**, without a Pl@ntNet API key. Choose `source: plantnet-gbif` in the manual workflow (or `--source plantnet-gbif` in Python). It searches the Pl@ntNet community-validated **observations with photographs** dataset on GBIF: https://www.gbif.org/dataset/7a3679ef-5582-4aaa-81f0-8c2545cafc81, DOI 10.15468/gtebaa. It does **not** use the separate automated-identification-only dataset, which lacks photos.

Initial 30-species test: 26 licensed, downloaded Pl@ntNet photographs spanning 10 sparse-gallery species; individual media records were CC BY-SA, creator names retained. Photographs must be credited **Creator / Pl@ntNet, CC BY-SA** and remain subject to independent taxonomic and diagnostic-image review before installation.

Choose `source: both` for GBIF general + public Pl@ntNet GBIF + direct Pl@ntNet DWC *when accessible*. The public sources work even when a direct Pl@ntNet key lacks DWC access.

## Optional Pl@ntNet enrichment

The Pl@ntNet `/v2/dwc/occurrence/search` API can search exact scientific names and research-validated observations, with image organ metadata. It needs a developer API key **with DWC route access**; a working key for other API endpoints does not guarantee permission to use DWC. In the October 15 live test, the saved key accessed `/v2/projects` (HTTP 200) but the basic DWC request returned HTTP 403. Store it as a GitHub Actions repository secret named `PLANTNET_API_KEY` or as a **local** environment variable, never in the code or public workflow input. Then select `source: plantnet` or `source: both`.

The Pl@ntNet taxonomy `/species?images=true` image option requires Pro; this tool uses the observation endpoint and does not bypass account or quota restrictions. Verify plan access before relying on it at scale.

## Candidate-to-install gate

1. Refresh live `data/manifest.json`, `reports/photo-coverage-latest.json`, `workflow/work-claims.json`, and curation-inbox; skip active claims and unresolved taxon concepts.
2. Search for correctly labeled observations (GBIF Texas first, with global fallback). Names must match including any infraspecific rank. This is **metadata only**, not independent verification of a pictured specimen.
3. Preserve observation ID, original media URL, source page, creator, rights label, organ when known, and provenance in `candidates.csv`.
4. GBIF occurrence/dataset Creative Commons rights do **not necessarily grant image rights**. If individual media licensing is not clear, retain candidate URL for investigation but do not automatically download/publish it. Pl@ntNet requires creator, Pl@ntNet credit, and the individual license (often CC BY-SA); adaptations may carry ShareAlike obligations.
5. Review the photograph for actual taxon identity, photo ownership/licensing, whether it shows a diagnostic organ, duplicates, and actual image quality before marking ready for installation.
6. Use the existing canonical installer/photo-curation pipeline for accepted photos; verify local media exists, image credits are linked, the gallery renders, and the species remains in `data/manifest.json` before counting installed success.
7. Keep Joey Santore CC BY-NC images and Calvin King's directly authorized private learner images under their original, distinct licenses. Never silently relabel them.

## Why not add every proposed source immediately?

- **GBIF** is the broadest initial discovery route, including some Pl@ntNet-origin observations.
- **Pl@ntNet** is optional because the relevant API needs a key and usage limits apply.
- **PlantCLEF** combines datasets with different source licenses; it needs a separate license reconciliation pass.
- **UCI Leaf** is a tiny leaf-focused dataset, unlikely to help with Hays County floral details, phyllaries, ligules or milkweed hoods.
- **Perenual** may be useful for later gap fill, but per-image rights, authorship, exact taxa, and service terms need tighter checking.

### Reporting vocabulary

`candidate` ≠ `staged photo` ≠ `verified source media` ≠ `installed/render-tested learner photo`.

A newly harvested candidate never counts as an installed photograph. `summary.json` explicitly reports canonical cards modified = 0.

The new action is **manual-only**; do not schedule it or trigger bulk runs from any existing automation. The two temporary one-time test workflows were removed after successful retrieval. See `reports/bulk-open-photo-gbif-plantnet-test-20261015.md` for exact test results, and use the original **Bulk Open Photo Candidate Harvest** workflow for future batches.