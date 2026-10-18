# Cloudflare deployment

This repository deploys the visual learner as a Cloudflare Worker with Static Assets.

Cloudflare build settings:

- **Build command:** `bash scripts/build_cloudflare_site.sh`
- **Deploy command:** `npx wrangler deploy`
- **Root directory:** `/`
- **Production branch:** `main`

The build script copies only the learner-facing files into `dist/`:

- `index.html`
- `manifest.webmanifest`
- `sw.js`
- `assets/`
- `content/`
- `data/`

Repository workflow files, scripts, research queues, and other project-only files are not published as static web assets.

After the first successful deployment, protect the Worker with Cloudflare Access before treating the URL as private.


## October 18 — direct GitHub Actions deploy (Cloudflare monthly build minutes exhausted)

`/.github/workflows/deploy-public-learner.yml` is the approved **manual** deployment
path. It stages the same static `dist/` package from the **private** canonical
GitHub repo, then uses `cloudflare/wrangler-action@v4` to deploy directly to the
existing **public** `hays-county-botany` Worker. This does **not** invoke Cloudflare's
integrated Workers Builds service and does not require GitHub Pages, a public
source repository, or a new hosting URL.

One-time owner setup:
1. In Cloudflare, create an API token with **Edit Cloudflare Workers** permissions
   limited to the Worker account. Do not put the token into a repo file, issue,
   chat, deployment report, or screenshot.
2. In the private GitHub repo, go to Settings → Secrets and variables → Actions →
   New repository secret, and add exactly:
   - `CLOUDFLARE_API_TOKEN`: value of the token above;
   - `CLOUDFLARE_ACCOUNT_ID`: your Cloudflare account ID from the dashboard.
3. In GitHub Actions, select **Deploy public Hays Botany learner (manual)**,
   choose **Run workflow** on `main`, and check that the Wrangler deploy step
   succeeds. Open the production `/photo-review.html` in a fresh browser tab
   and verify the displayed batch.
4. After a successful direct deployment, adjust/disable the Cloudflare
   integrated GitHub automatic build trigger if desired, so research commits
   do not consume future Cloudflare build minutes. The private photo archive,
   5 standing botany automations, review exclusions and canonical learner data
   must remain unchanged.

Only the whitelist from `scripts/build_cloudflare_site.sh` is exposed by the
public Worker. Private research files, candidate-photo archives and GitHub
review annotations are **not** copied to `dist/`.

Manual-only deploy is intentional: the project has many daily research/curation
commits. Batch site updates to avoid GitHub Actions minute usage and unwanted
upload churn. The workflow requires both GitHub secrets and fails clearly if
either is missing; it cannot deploy without the one-time credential setup.
