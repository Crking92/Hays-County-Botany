# Cloudflare production deployment failure — October 18, 2026

## User-visible symptom
Photo Lab at the Cloudflare Worker production URL still shows Batch 003 even though `photo-review.html` on GitHub `main` is Batch 004. This is not proof of a Safari cache problem.

## Confirmed evidence
- `photo-review.html` on GitHub `main` contains **Photo Lab Batch 004** (82 review candidates/18 taxa); all Photo Lab Batch 003 reviews are saved at `workflow/photo-library/reviews/diagnostic-003-user-labels-20261018.json` (86 annotated candidates, 68 shortlisted, 18 explicitly excluded).
- Cloudflare Workers Builds GitHub check for commit `ac880c2aff062c9f76da7702de0c210e0f84df39` is **failure**: https://dash.cloudflare.com/8fc22923103802955f95202cc5a08164/workers/services/view/hays-county-botany/production/builds/5ff62b85-022e-4149-9b47-2ae1ced013ec.
- GitHub Actions one-shot static site preflight on **the same commit** succeeded: https://github.com/Crking92/Hays-County-Botany/actions/runs/39156123837.
- That GitHub preflight reproduced the Cloudflare build command (`bash scripts/build_cloudflare_site.sh`), verified Batch 004 and `_headers`, counted **5,696 static files**, **703,110,432 bytes**, maximum single file **7,197,940 bytes**, and successfully ran `npx --yes wrangler@4 deploy --dry-run` (Wrangler 4.151.1). No production deployment was attempted by GitHub.
- Cloudflare build checks were succeeding on some commits as late as about `2026-10-18T06:06:37Z` (e.g. `d6a6ac90c6`); a subsequent check `397d5fb24b` failed at `2026-10-18T06:06:42Z`, with many more failures since. GitHub checks expose only the outcome and Cloudflare build link, not underlying log text.

## Interpretation and required next diagnosis
GitHub's static site build and Wrangler dry-run are passing. **Production Cloudflare Builds itself is failing**, so merely editing HTML, bumping service worker versions, or adding query-string cache busting cannot publish Batch 004. Avoid declaring the current live site updated solely from GitHub commits.

The exact Cloudflare error is not available from this connected GitHub tool. Open the linked Cloudflare failed build in an authenticated dashboard, expand the **build/deploy logs**, and look at the first fatal error and the preceding context. Check the Workers Builds build-minute usage/limits, account authentication/deploy token, API rate or concurrent-build limits, and asset upload stage **based on the actual logs**, without guessing which is at fault.

**Once underlying Cloudflare error is repaired**, retry the latest main-branch build in Cloudflare or trigger a new build. Confirm `/photo-review.html` actually returns Batch 004 on production and test the iPhone saved-web-app route.

## Safety
- Keep all permanent photo releases, user reviews, and all live canonical photos unchanged.
- Do not alter the five scheduled botany automations or enable an unverified alternate deployment method.
- `.github/workflows/cloudflare-one-shot-preflight-20261018.yml` is manually dispatchable and only auto-triggered by its own creation path; it does not deploy or schedule extra jobs.
