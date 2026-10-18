# Hays Botany: photo quality, published-site budget, and public-display rights

**2026-10-18 operating policy; manual size audit, no automated destructive editing**

## One source of truth, two different storage budgets

1. **Canonical private GitHub repository** contains species cards, licensed image files,
   scientific materials, private candidate review exports and photographic attribution.
   Its size keeps growing as the field learner gains species and views.
2. **Published public website** is a *whitelisted build of that repository* (only the
   files copied into `dist/` by `scripts/build_cloudflare_site.sh`). A static
   photo optimizer can reduce large JPEGs **only inside the staged site**.
   The originals stay in GitHub. The site could later be hosted using GitHub Pages
   if the repository owner has a Pages-eligible GitHub plan and enables it.

As measured from the current Git tree on 2026-10-18: **2,309 JPEG/PNG/WebP image
files under `content/` totaling about 690.7 decimal MB**; **118 files exceed
750 KB** and together account for approximately **159.8 MB**. Most smaller
images already need no work. Original staged site before optimization was
about **703.1 MB**, based on an earlier GitHub Actions preflight (it may grow).
GitHub's published Pages site limit is **1 GB** and the source repository has
a recommended limit of **1 GB**. Do not equate a successful GitHub commit with
a successful website deployment, and do not use Cloudflare build logs as a
proxy for GitHub Pages readiness.

## Photo priorities before more collecting

- Recognize it: whole-plant habit.
- Look closer: leaves, flowering parts, fruiting structures.
- Confirm the ID: true diagnostic anatomy such as phyllaries, ligules,
  Euphorbia cyathia, milkweed corona, or acorn cups.
- Verify actual pictured taxon, correct role, photographer, source page, and
  individual image license before installing. Do not treat reviewer labels or
  archived observation metadata as taxonomic confirmation.
- Preserve the original image for reference and reuse when possible.
  Where large original archives are needed, keep them in private Releases rather
  than embedding every multi-megabyte original in live learner cards.

## Suggested size targets for NEW canonical learner images

| Type | Working target for the web-ready canonical image |
| --- | --- |
| Whole-plant/habit | 1600-2000 px long edge, usually 150-500 KB JPEG |
| Leaves, flowers, or fruit | up to 2400 px long edge, usually 250-750 KB |
| Macro diagnostic detail | up to 2400-2600 px long edge when justified, normally <=1.2 MB |

These are guideposts, not reasons to discard fine identifying structures.
Use a larger file when botanical diagnostic quality really needs it. Keep
source credit, correct crop, and image orientation; never upscale or introduce
fake details.

## Safe public-copy photo optimization

`scripts/optimize_public_site_photos.py` (Pillow required) can run **after**
`bash scripts/build_cloudflare_site.sh` has staged a copy in `dist/`.
By default, it tests JPEGs over 750 KB, caps the long edge at 2400 pixels,
encodes at JPEG quality 85 with 4:4:4 color detail, writes only when the result
is smaller (or must remove original EXIF), and strips EXIF/GPS from reencoded
public JPEGs. It preserves a color profile when supplied. It will not modify
canonical source, the private library, copyright metadata, attribution, or
other image formats. Some smaller files and non-JPEGs may retain metadata;
full public EXIF validation is a **separate required QA gate**, not a promise
of this selective optimizer.

The size script writes a JSON report and raises an error on unreadable JPEG
or a staged website >= 920 MiB. It warns at 750 MiB, leaving extra headroom
under the GitHub Pages 1 GB maximum. A one-time/manual
`.github/workflows/public-site-budget-audit.yml` workflow builds the
public staging directory, runs the optimizer, and uploads the size report
without deploying anything. No recurring run is added.

## Preserve public-display permission and photo rights

- The author directly authorized displaying **his own** photographs on the
  public Hays Botany educational learner with **Glass Root Garden** credit on
  2026-10-18. See
  `workflow/glass-root-inat/OWNER_PERMISSION_2026-10-14.md` and
  `workflow/glass-root-inat/public-display-authorizations-20261018.json`.
- Those documents cover the 16 existing direct-owner private-study-only
  photo records when exact ownership is established. Keep historical
  `public_reuse:no` records as provenance; effective current permission for
  this particular website is public **display**, not necessarily open reuse.
  **Do not invent CC BY for photos previously marked all-rights-reserved.**
- Where the owner has separately granted CC BY 4.0 to a particular photo,
  preserve that existing grant.
- Joey Santore photos keep CC BY-NC and original license terms; other
  photographers keep their own individual rights and attribution.
- Never publish privately sourced raw EXIF coordinates or project-only files,
  work claims, archived candidate review exports, research backups or
  private release archives through the public static site.
- Size audit/optimization does not override image identity or rights holds.

## Future publication

The public GitHub Pages workflow (if enabled) should stage only `dist/`,
run the selective JPEG optimizer and its size/report checks, and publish
that generated artifact. Never point Pages directly at the private
repository's `main` root: that would risk exposing internal working files.
Manual or infrequent deployment is preferable to automatic rebuilds on
hundreds of daily research commits.
