# Hays Botany photo file-size policy — October 18, 2026

## Measured repository size (GitHub tree snapshot, 2026-10-18)

- Entire tracked working tree: about **900.6 MB** of file blob contents (NOT the Git history size).
- Installed canonical `content/` tree: about **702.3 MB**.
- Canonical photo files in `content/`: **2,309**, totaling about **690.7 MB**.
- **118** canonical images larger than **750 KB** account for about **159.8 MB**.
- Site package previously measured by GitHub preflight at about **703.1 MB** (before optimization).
- Permanent private photo-library Release ZIP archives are distinct from the published website and MUST NOT be bundled into `dist/`.

The audited numbers are snapshots; the canonical species/photo installers continue to add images, so rerun the measurement before each publication. Do NOT equate GitHub repository size with the published-site package size or with iPhone download bytes.

## Non-destructive workflow

1. Keep every licensed original and canonical `content/taxa/.../images` file **unchanged in private GitHub**. Continue to retain author, exact license (including CC BY-SA and CC BY-NC), direct source and botanical annotations.
2. Build **only** the whitelisted public website into `dist/` with `bash scripts/build_cloudflare_site.sh`. This directory is a temporary deployment package; its name is historical and does not require deployment to Cloudflare.
3. Run `python scripts/optimize_public_photo_copies.py --root dist --report site-image-savings.json`. Only staged JPEG images that exceed 750 KB or have removable EXIF are candidates. It preserves image aspect ratio and keeps a maximum 2800-pixel long edge, with JPEG quality 86, no chroma subsampling, and no location-bearing EXIF. It skips negligible savings unless EXIF stripping requires a rewrite. This first pass deliberately does not transform transparent PNGs.
4. Run the one-time, non-deploying `Public Learner Photo Size Pilot` GitHub Action. Read the `hays-botany-site-photo-size-report` artifact and spot-check leaf hairs, grass spikelets/ligules, milkweed hoods/horns, Asteraceae phyllaries, buds/acorn cup scales, and fine fruit/sepal details. **No public deploy unless the image comparison is acceptable**.
5. Later public site deployment may use this optimization step **only after the pilot succeeds and the user approves the size/quality tradeoff**. No background/scheduled deployment or site compression is enabled by this pilot.

## Recommended future size targets (not automatic hard failures)

- Whole plant/habit image: 150–350 KB if detail remains useful.
- Leaves/flowers: 250–550 KB.
- True diagnostic macro: up to 900 KB or larger where hairs, floral anatomy, ligules or acorn cup scales require it.
- Flag every photo over 750 KB for inspection rather than forcing an arbitrary quality reduction.
- Site budget aim: stay well under the selected host's published-size limit and leave room for another several hundred species.
- Public iPhone experience: smaller gallery images first; retain enough display pixels for tap-to-enlarge diagnostic views.

## Photo permission boundaries

- Calvin King / Glass Root Garden owner confirmed site-specific **public display permission** for personally owned photographs on October 18, 2026; see `workflow/glass-root-inat/OWNER_PERMISSION_2026-10-14.md`. This does NOT automatically turn all source photo license records into CC BY, nor authorize arbitrary third-party reuse. Credit Glass Root Garden.
- Older `public_reuse: no` notes for 16 of the owner's photographs remain part of the historical audit but do not block the personally authorized public learner display when individual ownership is established.
- Joey Santore CC BY-NC photographs can be used only in qualifying noncommercial educational contexts under their separate original conditions; CC BY-SA photographs may require ShareAlike compliance for adaptations.
- Source photography identity, plant identity, visible anatomy, rights and EXIF privacy gates still apply. Never compress or publish a held/unreviewed candidate merely because it exists in the photo library.

## Safety

The pilot cannot edit GitHub originals or installed `species.json`, does not alter the five standing botany automations, does not depend on Cloudflare credentials, and does not publish a new site. It is an objective savings test, not proof of preserved micro-anatomy or a substitute for photo review.
