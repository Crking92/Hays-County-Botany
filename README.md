# Hays Botany ID

Private working repository for a Central Texas **visual botany learner + curation system**.

This working tree was rebuilt on 2026-09-30 from the current curation packages. The old GitHub React/Vite snapshot was intentionally discarded because it was no longer the active build.

## Purpose

Teach field identification by showing **where to look first**, which structures matter, and how to separate close look-alikes. The project is morphology-first rather than flower-color-first.

## Current roles

- **GitHub** — persistent project home
- **ChatGPT/OpenAI** — range verification, morphology, look-alikes, image curation, species packages, code/QC
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
- Normal approval is blocked for `FAIL` and `UNRESOLVED` range records. Those require a comparison decision, additional review, rejection, or an explicit unresolved exception.
- Git commits are optional with `HAYS_BOTANY_APPROVAL_AUTO_COMMIT=1`.
- A local tracker-sync command can optionally be supplied through `HAYS_BOTANY_APPROVAL_SYNC_COMMAND`; otherwise the established ChatGPT/Google-Sheet synchronization workflow remains unchanged.

See `workflow/APPROVAL_DASHBOARD.md` for the decision mapping and safety behavior.
