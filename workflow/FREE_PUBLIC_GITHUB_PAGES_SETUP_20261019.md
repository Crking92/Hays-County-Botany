# Free GitHub Pages setup — Hays Botany phone learner
Recorded October 19, 2026

## What this setup does

Publish the **website only** from a PRIVATE working repository to a separate PUBLIC website repository. Do NOT flip `Crking92/Hays-County-Botany` to public. GitHub Free supports GitHub Pages from public repositories. You do not need Codespaces or Cloudflare. Publishing is MANUAL: new plant/photo commits keep arriving in private GitHub, and you choose when to publish a new snapshot.

The new exporter `scripts/build_public_pages_snapshot.py` creates a rights-filtered static site and excludes the Photo Lab preview and private source files. Photos not cleared for public display are intentionally omitted from the website copy; the original private learner is left intact. This is an initial technical rights filter, not final legal verification of every image, attribution or external link. Site use is assumed to be **strictly noncommercial educational** as requested; review NC licenses if that use ever changes.

## One-time setup — your GitHub account

1. Visit **https://github.com/new**. Create an **empty PUBLIC repository** named `Hays-Botany-Public` owned by `Crking92`. Check **Add a README** so it has a `main` branch. Do **NOT** use GitHub's importer or fork the private Hays-County-Botany repo: those methods can copy confidential/source/photo history.
2. In the new PUBLIC repository visit **Settings → Pages**. Under **Build and deployment**, choose **Deploy from a branch**, branch **main**, folder **/(root)**, and Save.
3. At **https://github.com/settings/personal-access-tokens/new**, create a **fine-grained personal access token** (not a classic account-wide token) with:
   - Resource owner: **Crking92**
   - Repository access: **Only select repositories** → `Hays-Botany-Public`
   - Repository permission: **Contents: Read and write** (Metadata read is automatic)
   - Choose a limited expiration and renew when needed. Never paste this token into ChatGPT, issues, files or the public repo.
4. In the PRIVATE `Crking92/Hays-County-Botany` repository open **Settings → Secrets and variables → Actions → New repository secret**. Name it **`PUBLIC_PAGES_REPO_TOKEN`**, and enter the token there. It must be stored only in private Actions secrets.
5. In the PRIVATE repo's **Actions** tab select **Prepare and publish public-only Hays Botany Pages site**. Run it the FIRST time with **publish = false** and **public_repo = Crking92/Hays-Botany-Public**. Review the **public-website-rights-audit** artifact: this run does not publish publicly.
6. When the preview and excluded-photo counts are acceptable, run the SAME workflow with **publish = true**. It clones only the dedicated public repository, copies the filtered `dist/` website and pushes `main`. The public repository's branch-based Pages publishing then deploys it. Watch both workflow histories for success.
7. Open **https://crking92.github.io/Hays-Botany-Public/** in Safari on your iPhone. Select **Share → Add to Home Screen**. Expect GitHub Pages to take a little time to publish after a commit.

## Each time you want the latest plants

In PRIVATE `Hays-County-Botany`, open **Actions → Prepare and publish public-only Hays Botany Pages site → Run workflow** with **publish = true**. Visit the phone web app when the private export + public Pages build have both succeeded. You do NOT need Codespaces, Cloudflare, or to run a computer locally.

## Important caveats

- Even an unshared GitHub Pages URL and its PUBLIC repository are visible to anyone. Public is not password-protected.
- The private learner contains previously installed photos with conditional rights; site output omits those instead of removing them from private source. If a plant photo is missing publicly, check the audit report before trying to restore it.
- CC BY-NC is accepted by the exporter ONLY for the declared stand-alone noncommercial educational site. Correct individual photograph licenses, credit, ShareAlike/change notices and any applicable permission still matter. A commercial or promotional future website may require a stricter export.
- The README and repo creation do not publish the original private history. **Never change the original repository's visibility**.
- No future automatic publication; you choose when to publish. The five established botany automations continue working on private GitHub.
- Don't commit token values. If compromised, revoke at GitHub token settings and replace the secret.

## Current status

The private exporter and manual publishing workflow were COMMITTED and read-back confirmed on October 19, 2026. The **public destination repo has not been created or Pages activated by these steps**, and **the exporter has not yet passed its first full GitHub Actions preview**. Do not assume a website exists or that the snapshot is publication-ready until both explicit runs succeed.
