# Joey Santore Deep-Extraction Library

This folder is the research-stage source library for material by Joey Santore / Crime Pays But Botany Doesn't that may feed the Hays Botany learner.

## Status

Everything in this folder is **research-stage material**, not canonical species data yet.

Normal promotion path:

`research-drafts/joey-santore/ -> ChatGPT/human curation -> curation-inbox/ -> GitHub curation pipeline -> content/taxa/`

Google Sheets remains a coordination/status view. GitHub is the canonical project home.

For user-supplied Joey videos, selected teaching frames are extracted at exact timestamps. Because the GitHub connector cannot directly persist binary frame files, the selected JPEGs are staged persistently in the ChatGPT Library under `/Hays Botany ID/Joey Santore/video-frames/<youtube-id>/`, while the source manifest and promotion metadata live here in GitHub. The intended eventual repo asset path is `research-drafts/joey-santore/video-frames/<youtube-id>/`.

## Source authority

For this project, Joey Santore is treated as a **high-weight expert field/botany source** for:

- diagnostic morphology
- plant-family and genus characters
- field identification logic
- habitat and plant-community observations
- geology/soil relationships
- pollination and dispersal observations
- ecology and evolutionary context
- his own direct field observations

Current accepted taxonomy, nomenclatural changes, and strict project range decisions are still reconciled against the project's taxonomic/range authorities. If Joey presents an interpretation, hypothesis, or tentative observation, preserve that uncertainty rather than flattening it into a hard fact.

## Media statuses

- `exact_observation_identified` — exact Joey observation/page located; useful media visibly confirmed.
- `source_page_with_labeled_media` — Joey page contains useful images with plant/part labels, but exact image URL/photo ID is not yet locked.
- `source_identified_access_limited` — useful Patreon/other source identified, but media still needs access/extraction.
- `text_or_lesson_only` — useful teaching/explanation source without an exact image selected yet.
- `exact_media_locked` — direct image URL/file ID + source page + creator + rights metadata are captured and ready for species image-sources.csv.
- `video_frames_extracted_and_persisted` — exact user-supplied video moments have been visually reviewed, keeper frames extracted, timestamped, and persistently staged with a GitHub manifest.

## Video extraction standard

For a supplied Joey video:

1. Search subtitles/transcript for plant names and botanical terms.
2. Visually scan the video for useful morphology the transcript may miss.
3. Pull neighboring frames around each candidate moment and choose the sharpest/clearest view.
4. Reject frames that do not clearly teach the plant or structure.
5. Save the exact timestamp in the filename and manifest.
6. Record taxon wording exactly when Joey is tentative.
7. Describe the anatomical/teaching role rather than merely calling an image attractive.
8. Preserve uncertain claims as uncertain until independently verified.
9. Stage selected frames persistently and index the extraction in `index.json -> video_extractions`.
10. Promote approved frames later into term/family teaching modules or species packages.

## Photo selection standard

A source is not counted as a completed diagnostic media record merely because it contains a pretty plant photo. Preferred records name the taxon and identify what the image teaches, such as:

- habit / whole plant
- phyllotaxy / leaves
- leaf base / margin / surface
- stem / nodes / attachment
- flower front / flower side
- calyx / sepals / phyllaries
- stamens / anthers / style / stigma
- inflorescence
- fruit / seed
- root / rhizome
- bark / twig / bud
- look-alike separator
- habitat / substrate

## Rights

Joey's iNaturalist profile states that his photos are free to use for non-commercial and educational purposes with credit. Record that as strong private-study/educational permission, but still retain the exact per-photo iNaturalist license whenever possible before public publication.

Extracted frames from YouTube videos are treated more conservatively: private-study use is allowed in this learner workflow, but public reuse is **not** assumed cleared unless separate permission or licensing supports it.

## Promotion rule

Before Joey media is promoted into a canonical species package:

1. Resolve the taxon to the canonical project name.
2. Identify the anatomical/diagnostic role.
3. Preserve Joey as creator/source.
4. Preserve source page and exact observation/photo IDs or video timestamp when available.
5. Capture direct image URL where possible; for extracted video frames preserve the exact source-video ID and timestamp.
6. Distinguish direct observation from Joey's inference/hypothesis.
7. Record study-use and public-reuse status separately.
8. Add approved exact media to that species' `image-sources.csv` or the relevant term/family teaching module.
