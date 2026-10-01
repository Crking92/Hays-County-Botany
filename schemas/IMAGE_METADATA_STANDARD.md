# Exact Image Metadata Standard

The automated photo stage reads `image-sources.csv` inside each species folder.

Recommended columns:

```csv
file_name,role,platform,observation_id,photo_id,creator,license,source_page,direct_image_url,study_use,public_reuse
```

## Required for fully automatic photo download

- `file_name`
- `role` or `view`
- `creator`
- `license`
- `source_page`
- `direct_image_url`

The exact observation/file/photo identifiers should also be retained when the platform provides them.

## Diagnostic roles

Use the views that actually help identify the taxon. Common roles include:

- habit
- leaves / phyllotaxy
- stem / attachment
- flower front
- flower side
- reproductive detail
- fruit / seed
- look-alike comparison

Oak packages may instead emphasize leaf upper/lower surfaces, twig/bud, bark, acorn and cupule.

## Rights fields

`study_use` and `public_reuse` are separate. A useful private-study image is not automatically cleared for public publication.

## Download behavior

The GitHub pipeline:

- skips completed image files
- waits at least 15 seconds between downloaded files
- waits about 75 seconds and retries after a failed request
- preserves the CSV source/license record
- resizes large photos to a maximum 1600 px dimension when Pillow is available
