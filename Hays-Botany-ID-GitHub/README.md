# Hays Botany ID — GitHub edition

This is a portable snapshot of **Hays Botany ID Site version 12**. It keeps the family-first identifier, botanical vocabulary, family evidence, visual comparisons, private study photographs, progress saved in the browser, and both research workbooks.

The project is built with **React + Vite**. That is the most practical form for this guide because it is:

- easy to edit in GitHub or GitHub Codespaces;
- static—there is no database, server, API key, or paid host required;
- testable before anything is shared;
- ready for GitHub Pages later, after the photographs are cleared for publication; and
- installable as a small browser app when served over HTTPS.

## Important privacy rule

Keep the repository **private** while photograph permissions are pending. Do not enable the optional GitHub Pages workflow yet. A private repository does **not** automatically make its Pages website private; GitHub gives the same warning in its [Pages publishing documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site). See [PHOTO-USAGE.md](PHOTO-USAGE.md) before publishing.

The publishing workflow is deliberately parked in `.github/optional-workflows/`. GitHub will not run it from there.

## Easiest way to build and play in GitHub

1. Create a new **private** GitHub repository named `hays-botany-id`.
2. Unzip this package on your computer.
3. Use GitHub Desktop to add the unzipped folder as a local repository, then publish it to the private repository. This preserves all nested and hidden configuration folders.
4. On GitHub, choose **Code → Codespaces → Create codespace on main**.
5. Wait for setup to finish, then run this in the Codespaces terminal:

   ```bash
   npm run dev
   ```

6. Open the offered **Hays Botany ID preview**. The Codespaces preview port is configured as private.

Each of your GitHub accounts can be invited to the private repository as a collaborator. Each account can open its own private Codespace and work with the same files.

## Run it on your computer

Install [Node.js 22](https://nodejs.org/), then either double-click `START_HERE_WINDOWS.bat` on Windows or run:

```bash
npm ci
npm run dev
```

Open the local address printed in the terminal. Stop the preview with `Ctrl+C`.

Before saving a change, check the complete build:

```bash
npm test
```

## Where things live

| What you want to change | File or folder |
|---|---|
| Main guide and page sections | `src/App.tsx` |
| Family browser and comparisons | `src/family-guide.tsx` |
| Main family, evidence, vocabulary, and source data | `src/botany-data.mjs` |
| Full family catalog and evidence rows | `src/family-evidence-data.mjs` |
| Colors, spacing, mobile layout, and card styling | `src/globals.css` |
| Included private-study photographs | `public/images/ut-study/` |
| Downloadable research workbooks | `public/downloads/` |
| Photograph source and rights checklist | `IMAGE-SOURCES.csv` and `PHOTO-USAGE.md` |
| UT archive research inventory | `research/` |

Answers and checked photo targets are stored only in that browser using local storage. They are not uploaded anywhere.

## Publish later, after permission review

Only do this after every included or embedded photograph is approved for the intended public use—or if your organization has properly configured private GitHub Pages access.

1. Move `.github/optional-workflows/deploy-pages.yml` to `.github/workflows/deploy-pages.yml`.
2. Commit and push that move.
3. In the repository, open **Settings → Pages**.
4. Set **Source** to **GitHub Actions**.
5. Open the Actions tab and confirm that **Publish GitHub Pages** succeeds.

The relative-path build works whether the repository is named `hays-botany-id` or something else.

## Snapshot provenance

- Original Site slug: `hays-botany-id`
- Source Site version: **12**
- Source commit: `d48badd913b29321f65cdb557676c11ea887f1a7`
- GitHub conversion: static React/Vite; no content was intentionally removed
- Included UT study set: **12 local photographs**
- Other diagnostic set: **18 source-linked photographs**

This package does not change or republish the private ChatGPT Site. It is a separate working copy.
