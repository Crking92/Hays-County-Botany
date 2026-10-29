# Cross-chat handoffs — 2026-10-28 coordination snapshot

**Dated observation, not an auto-refreshing live status board.** Refresh relevant README, staged branch, source SHA, latest migration ledgers, work claims and Actions before any new write. Original `Crking92/Hays-County-Botany` is canonical until a separately approved cutover. No public family deployment approved.

## Multi-repo migration lanes

| Lane | Latest documented condition | Next work / rule |
| --- | --- | --- |
| Asteraceae | Private staging; 180 species, 459/459 original photos accounted; current README reports 323 original photos physically staged, 39 separately sourced; 179/180 species have at least one archived photo; curated private view 334 photos across 169 species; strict CC-only candidate 153 photos across 112 species. | Continue final per-species photo/credit/arrow QA; do not imply that archived = displayed = public. Eleven species have no photo in curated preview. `Pectis angustifolia var. fastigiata` exact-variety/rights hold remains. Missing 49 standalone genus lessons are a separate backlog. Keep Pages and production routing unchanged. |
| Fabaceae | Private staging; 91 species and 200/200 original images accounted. 70 source-verified originals staged, covering 48 species; 130 source images held. | Continue rights/source recovery and accurate field-first preview; no Pages or ownership cutover. Do not overwrite concurrently updated originals. |
| Poaceae | Staged 112 species, 53 genera; 1,178 initial checked files incl. 788 photo candidates; 224 images held. Existing hub unchanged. | Separate grass diagnostic/manual work from migration. Rights-filtered galleries, arrow checks, incomplete detailed panels and site/hub integration remain. Do not declare production switched. |
| Seven grouped-family repositories | Created as empty/planning collection staging with family assignments and READMEs. | No bulk image import or family ownership claims until verified source and per-photo rights manifests. |
| Hays-Botany-Public | Separate repository exists but is not the live central website. | Build and test consistent hub catalog/search/quiz/navigation before any approved cutover. |

The older Asteraceae `ASTERACEAE_ALL_459_PHOTOS_ACCOUNTED_20261028.md` documents an **earlier** 210-staged/249-held snapshot. Its 459-row provenance ledger is still useful, but do not promote those old totals over the later family README/QA handoff without reconciling branch/SHA. Different metrics count different things.

## Other manual chats / independent artifacts

- **Grass lanes 1–5 and species-specific work:** current focus is actual usable diagnostic photographs, verified arrows, difficult grass look-alikes, permanent GitHub copies, and species-by-species status bars. Keep work assigned per target taxon, compare live changes before writing and respect `Muhlenbergia piniflora` being deferred until last. Different grass chats must not race on the same species card, photos or genus lesson.
- **King Ranch bluestem / silver bluestem and other priority grass anatomy:** preserve the actual rights or permission evidence (including Bob Harms permission scope where applicable), no blanket inferred crop/annotation rights, and anatomy-detail review. Distinguish field-ready from 100% photo complete.
- **Printable grass anatomy visual workbook:** separate page-by-page review artifact (diagram + real photo, minimal text, verified credit); not automatically a public-website asset or approval to rehost nonpublic images. Reuse only verified permitted media on GitHub.
- **Arundo / Phragmites reed ID booklet:** a separate page-by-page, printable, user-reviewed teaching product; user's private educational photo allowance here must NOT be imported wholesale into any public repo.
- **Other site improvements:** keep existing Learner / Field ID / Quiz user experience and photo scroller, glossary links and visual arrow precision; avoid design drift among family collections.
- **Paused bots:** 11/11 tasks disabled at Oct 28 audit, including five grass-specific; do not obey stale `KEEP ENABLED` text as a request to resume. Older hub files may describe five other hourly botany workers; update the active-state wording, not task schedules.

## Cross-chat completion and claims contract

For a change, record **target species/family, repo/branch, lane, source SHA, destination SHA, media-rights gate, commit SHA, pages deployed? (yes/no), remaining exact blockers**. Each chat reads `workflow/MULTI_REPO_OPERATING_RULES_20261028.md` and its destination `AGENTS.md` before writes. A private preview pass is not proof of public deployment or anatomy completion.

When a source and destination snapshot disagree, preserve both states, classify the source revision and update the ledger before making a claim. Do not delete source photos merely because the archived image is weak or license-untraceable; hide unsafe gallery instances and leave precise holds. Public release is a separate, approved gate.

## Live hub coordination check performed October 28

The hub `data/manifest.json` currently reports **1,191 species across 146 distinct family folders**, matching the *baseline* routing table; these are installed source records, not completed or migrated public family sites. The shared `workflow/work-claims.json` has **505 historical claims: 490 released, 12 marked active, 2 queued, and 1 blocked**. Most non-released entries are old and many have expired dates; their status alone does **not** prove a chat is currently running or authorize deletion/overwrite. Before touching a listed scope, inspect its durable state/latest commits, resolve the handoff explicitly, and update or close only with verified ownership. The claim registry was **not** mutated by this coordination pass.
