> **October 28 multi-repo coordination:** Original site and source remain canonical; new family repositories are staging. See [operating rules](workflow/MULTI_REPO_OPERATING_RULES_20261028.md) and [cross-chat handoffs](workflow/ACTIVE_CHAT_HANDOFFS_20261028.md). All 11 ChatGPT automations were paused at the Oct 28 audit. No website-routing, publication, visibility or source-ownership cutover has been approved.

# Hays Botany ID

Public working repository for a Central Texas **visual botany learner + curation system**.

This working tree was rebuilt on 2026-09-30 from the current curation packages. The old GitHub React/Vite snapshot was intentionally discarded because it was no longer the active build.

## Public educational learner — current operating mode

[Open the GitHub Pages visual learner](https://crking92.github.io/Hays-County-Botany/).

As of October 20, 2026, the repository and site are publicly accessible. The owner currently uses the learner as a **noncommercial educational work-in-progress**, not a promoted commercial project. One good licensed view is enough for a provisional species card; further diagnostic photos, arrows and look-alikes can be refined later. Some photos are reused under CC BY, CC BY-SA or CC BY-NC and retain their **individual creator, license and attribution conditions**. Glass Root Garden original photos may instead have site-specific permission; site display does not grant blanket redistribution rights.

The GitHub Pages build is **rights-filtered** and published separately after verification via `.github/workflows/publish-public-learner-github-pages.yml`. Prefer this current workflow over the older `deploy-github-pages-learner.yml` and `prepare-public-pages-site.yml` experiments, which retain obsolete private-source/raw-site assumptions. A file committed to GitHub is not proof it appears on the website. The site filters unsupported image records, but the source repository itself is public: files committed here can be accessed directly, independently of the website. Do not add unsourced, all-rights-reserved, private-only or unverified media under the assumption that educational purpose makes it reusable. Replacement-photo handoffs preserve the distinction between NEEDS_PUBLIC_PHOTO and NEEDS_DIAGNOSTIC_PHOTO.

Read `PROJECT_RULES.md`, `workflow/PUBLIC_PHOTO_REUSE_POLICY_20261019.md` (October 20 update) and `workflow/COORDINATION.md` for current licensing, publication and five-worker responsibilities.

## Purpose

Teach field identification by showing **where to look first**, which structures matter, and how to separate close look-alikes. The project is morphology-first rather than flower-color-first.

## Current roles

- **GitHub** — persistent project home
- **ChatGPT/OpenAI** — morphology, look-alikes, image curation, species packages, code/QC (county-native-range fast-fill paused Oct 14, 2026)
- **Google AI** — terminology, definitions and text-heavy comparison wording
- **Master tracker** — coordination source

See `PROJECT_RULES.md`, `workflow/COORDINATION.md`, and `workflow/work-claims.json`. The coordination files are the shared cross-chat reservation layer used to minimize duplicate work.

## Run locally

Double-click `RUN_LOCAL_SERVER.bat`, or run:

```bash
python -m http.server 8000
```

Then open `http://localhost:8000`.

## Current taxon modules

- Apocynaceae / Asclepias
- Convolvulaceae / Ipomoea
- Convolvulaceae / Distimake
- Convolvulaceae / Convolvulus
- Papaveraceae / Argemone
- Fagaceae / Quercus

Some Convolvulaceae modules were intentionally curated in local-occurrence-first mode and still have strict native-range auditing deferred. Read each species JSON rather than assuming every included taxon passes the project's native threshold.


## Approval dashboard

The learner now includes an **Approvals** tab.

- On the static/Cloudflare site, the approval queue is visible in **read-only** mode.
- When the project is opened with `RUN_LOCAL_SERVER.bat`, the same page can write decisions safely through the local Python server.
- Decisions update `research-queue.json` only after an optimistic revision check, so a stale page cannot silently overwrite newer curation work.
- Every local decision is appended to `workflow/approval-audit.jsonl`.
- Normal learner admission is independent of native-range PASS/FAIL/UNRESOLVED; accepted-name/duplicate-concept mapping remains the species-card safeguard. Confirmed invasive/introduced labels are encounter aids, while county-range research remains archived for later.
- Git commits are optional with `HAYS_BOTANY_APPROVAL_AUTO_COMMIT=1`.
- A local tracker-sync command can optionally be supplied through `HAYS_BOTANY_APPROVAL_SYNC_COMMAND`; otherwise the established ChatGPT/Google-Sheet synchronization workflow remains unchanged.

See `workflow/APPROVAL_DASHBOARD.md` for the decision mapping and safety behavior.
