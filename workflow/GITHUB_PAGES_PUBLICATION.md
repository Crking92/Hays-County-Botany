# Public GitHub Pages from a private Hays Botany repository

**Status 2026-10-18:** workflow prepared; NOT deployed or proven live.
GitHub source repository `Crking92/Hays-County-Botany` remains **private**.
Only the whitelisted learner's static `dist/` asset package is ever uploaded publicly.
Never change the repository's visibility to public just to make Pages work.

## Owner's one-time activation

1. Confirm the repo owner has a GitHub plan that supports **Pages from private repositories**
   (GitHub Pro, GitHub Team or eligible Enterprise; a Free personal private repo
   cannot use this publication approach without an upgrade).
2. Open `https://github.com/Crking92/Hays-County-Botany/settings/pages`.
3. Under **Build and deployment** → **Source**, choose **GitHub Actions**.
4. Open the **Actions** tab and choose `Publish Hays Botany on GitHub Pages (manual)`
   (`.github/workflows/publish-public-learner-github-pages.yml`).
5. **First run with Publish unchecked**: inspect `pages-image-quality-report`
   artifact; no public site is launched. Preview optimized diagnostic comparisons.
6. When visual/rights audit is acceptable, run the same workflow manually with
   **Publish checked**. Verify both build and deploy jobs succeed.
7. In Settings → Pages open **Visit site**; expect a project path
   `/Hays-County-Botany/` under the account's GitHub Pages domain
   unless a custom domain is configured. Validate homepage, Photo Lab version,
   tile navigation, flower macros, credits and iPhone saved-web-app navigation.
8. The old Cloudflare Worker is a separate URL and will continue to display old
   content until removed or redirected. Publishing Pages does NOT update
   Cloudflare or remove its original worker automatically.

## Build / photo safeguards

- Site source: `scripts/build_cloudflare_site.sh` stages `dist/`. That filename
  is historical and only refers to the build packaging; it DOES NOT deploy to Cloudflare.
- Local web-only copies: `scripts/optimize_public_photo_copies.py`, default
  JPEG over 750 KB, 2800px max long edge, JPEG quality 86, no EXIF.
- Visual QA: `scripts/audit_public_photo_quality.py` generates 1:1 and full
  original/optimized comparison contact sheets and a JSON report. The test
  modifies nothing and does not independently certify the botanic identity of photos.
- Size guard: 850 MB staged site fails before deployment; official Pages site
  limit 1 GB. Avoid heavy automatic deployments when new plants arrive.
- Whitelist: public `index.html`, `photo-review.html`, `assets`,
  `content`, `data`, app web manifest and service worker. **Private**
  `workflow`, research, reports, GitHub reviews, photo-library release archives
  and automation files are never uploaded. Do not put secret tokens in `content`.
- Public site is for educational display. Individual CC licenses and creator
  attribution remain legally relevant; Joey Santore's CC BY-NC images require
  qualifying noncommercial usage. The owner has explicitly authorized public
  site-specific display of his personally owned Glass Root Garden photos,
  including 16 older private-study-only records. Do not rewrite old iNaturalist
  source license metadata. Rights-unclear or taxonomically dubious third-party
  images require separate review before choosing them for public display.
- Static GitHub Pages cannot write to a private approval queue; the Learner's
  local-server approval feature remains a read-only/disabled public-site view.
- No change to the five scheduled botany automations; no deployment after every
  taxonomic/photo commit. Trigger publication manually in deliberate batches.

## Test records

- Initial 2026-10-18 optimizing pilot: `reports/public-site-photo-size-pilot-20261018.json`.
  **703.1 MB → 618.8 MB**; **102** optimized website JPEG copies; original files unchanged.
- Read-only diagnostic quality preview workflow:
  `.github/workflows/photo-macro-quality-preflight.yml`; action run
  `39159475173` completed successfully with a mean compressed-vs-original pixel
  absolute difference 2.35 at published resolution; one photo flagged for closer
  visual review and zero processing errors. This is encouraging but not full
  botanical pixel-level inspection.

**Website status remains NOT DEPLOYED until the owner enables GitHub Pages,
manual publish is run and URL/production batch verified.**
