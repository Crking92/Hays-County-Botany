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

See `PROJECT_RULES.md` and `workflow/`.

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
