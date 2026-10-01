# Curation Inbox

This folder is the handoff point between a completed curation batch and the canonical Hays Botany project.

Each batch lives in its own folder:

```text
curation-inbox/<batch-id>/
  batch.json
  taxa/
    Family/
      family.json            optional
      Genus/
        genus.json           optional
        species-id/
          species.json       required
          SOURCES.txt        required
          image-sources.csv  optional until exact photos are selected
          images/            optional
```

## batch.json

Example:

```json
{
  "batch_id": "asteraceae-batch-5",
  "mode": "install",
  "require_exact_images": true
}
```

- `mode: install` validates and installs the batch.
- `mode: validate_only` validates without installing.
- `require_exact_images: true` fails the batch unless exact-image metadata is present with direct image URLs.

Successful install runs move the original batch into `curation-archive/`, rebuild `data/manifest.json`, update the canonical species count, and write `reports/last-curation-run.json`.

Do not place guessed county records or unidentified image files in the inbox.
