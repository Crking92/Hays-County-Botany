# PUBLIC PHOTO REUSE GATE — effective 2026-10-19

**User request:** The Hays Botany learner and crew's Everyday Plants curriculum are intended to become **public knowledge on a publicly viewable website**. From this date forward, *select and install only photos with individually documented permission for public web display under the site's intended use*, even while the canonical GitHub source repository remains private. This rule takes priority over older private-study-only first-card/photo-enrichment allowances.

## Acceptable photos for NEW canonical installation and lessons

1. **Owner-authored media:** Photos personally owned by Calvin King / Glass Root Garden with the already recorded *public display on this learner* permission at `workflow/glass-root-inat/OWNER_PERMISSION_2026-10-14.md` and `workflow/glass-root-inat/public-display-authorizations-20261018.json`; confirm actual photographer ownership and photo ID, use visible credit **Glass Root Garden**, remove GPS/EXIF from published copies, retain source license and historical restriction fields. This site-specific display permission is NOT a blanket CC license for redistribution by others.
2. **Public domain / CC0**, with reliable photo-level evidence and requested attribution where relevant.
3. **CC BY, CC BY-SA** with verified *individual photograph* creator, specific applicable license/version, link to original photo/source, and accessible site attribution/license link. Honor ShareAlike on adapted works and document any crop/labels/annotation changes.
4. **CC BY-NC / NC-SA** only if the *specific actual deployment* is unambiguously noncommercial under the license, all credit and ShareAlike obligations are honored, or the photographer explicitly authorized public website use at the intended level. A public URL by itself does not violate NC, but a business, monetized or promotional site may make NC unsuitable. Until the intended site's commercial status is verified, mark NC **conditional / NOT PUBLICATION-READY** and prefer equally useful CC BY/SA/CC0 alternatives. Joey's currently inventoried iNaturalist photographs are often CC BY-NC; credit alone does not waive NC. Privately archived Joey video frames are not automatically authorized for public display.
5. **Other permission** only if there is a clear image-specific documented authorization covering actual public web use, with its conditions and permitted alterations recorded.

**Not eligible for new canonical photo installation:** only private-study or private-use authorization from someone else; an all-rights-reserved third-party image lacking explicit web permission; unknown image-level license/creator; search thumbnail or API link without original media rights; a website whose copyright/license belongs only to the page; unclear botanical identity; reused generic family photo presented as the exact species; an archived candidate not image-reviewed or physically verified. A legal URL does **not** prove a legal copy.

## Per-photo durable metadata (new and recovered)

- Exact taxon, photograph/observation ID where available, creator, original source page, source photo URL, physical file path, recorded original photo license/version, permission scope (PUBLIC-WEB-CLEARED or CONDITIONAL/RESTRICTED), photographer credit, and direct license/permission evidence.
- Whether commercial usage and alteration are permitted; attribution/license link and change notices (e.g. crop, arrow or annotated version). Apply correct CC BY-SA/NC-SA adaptation rules. Never silently convert a private-use record into a CC BY record.
- Match the photographed botanical organ to the label, preserve existing photos and source metadata, and verify file/commit readback before counting installed.

## Existing galleries vs eventual public release

**Do not erase prior private-gallery history.** Existing canonical cards may include valid *private-study* photos that are not automatically cleared for public display. Build a photo-by-photo rights audit for the existing collection; replace restricted third-party images with verified publicly usable equivalents when feasible. The 2026-10-18 *site-specific* owner authorization can resolve older Glass Root Garden entries when exact ownership is independently established. Until the audit is complete, never claim that every current canonical photo is safe to publish on the open web.

`scripts/build_cloudflare_site.sh` presently copies the whole `content/` directory to `dist/` without photo-rights filtering; this copying alone does **not** verify licensing. **No manual public GitHub Pages or Cloudflare deployment should ship this staged `dist/` before a complete rights check/exclusion of uncleared media and private review materials.** Prefer a fail-closed public-deployment gate and/or a verified rights-filtered public site build. Keep private GitHub study access intact; Cloudflare automatic builds remain disconnected and GitHub Pages remains off until deliberately configured.

## Division of work

- Approved Taxa Installer: first cards should use one public-web-cleared image, or leave a clear media hold and move to the next taxon; do not install a newly restricted-only photograph simply for the first-card count.
- Diagnostic Photo Fast-Fill: prioritize the large one-photo backlog using public-web-cleared additional diagnostic views; don't add a nonpublic second photo just to increase gallery count.
- Family and Genus workers and the Everyday Plants crew lesson chat: distinguish allowed image examples from missing/conditional references. Structure labels/arrows require both visual verification and permission for adaptation.
- Taxonomy Name Fast-Pass does not select or install photos. The manual private candidate archive can retain research leads of varying rights, but only public-cleared images may be promoted to new canonical galleries.
- Never change or restart other automations or reconnect Cloudflare in the course of rights review.

## Deployment interpretation

GitHub `main` is the **private source**, not necessarily a deployed website. GitHub repository Settings > Pages currently reports `has_pages=false`; the manual Pages Actions workflow is prepared but not yet an enabled public site. Disconnecting Cloudflare automatic builds **does not prevent new GitHub commits**, but any older Cloudflare URL may remain frozen until a separate, user-authorized publication.
