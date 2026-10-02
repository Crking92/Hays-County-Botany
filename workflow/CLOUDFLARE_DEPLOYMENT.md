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
