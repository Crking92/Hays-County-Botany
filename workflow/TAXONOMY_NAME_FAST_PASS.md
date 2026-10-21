# Taxonomy Name Fast-Pass — 2026-10-14

**Mode: ACTIVE.** The exhaustive native-range/county-verification lane remains **PAUSED**.
Canonical GitHub is authoritative; Google Master Plant Pool is a derived coordination view.

## Objective

Make all approved-source-pool plants identifiable in the visual learner without creating duplicate cards from historic names, infraspecific concepts, misspellings or disputed accepted names. This is a **name/taxon-concept audit**, not three-county nativity certification, photo installation, or final specimen identification.

Baseline snapshot on 2026-10-14: 1,282 Master Plant Pool rows, 545 canonical species in `data/manifest.json`, 406 Master rows still showing legacy combined 'Pending taxonomy/range audit'. These figures are temporary snapshots, not a count of taxonomic errors or a count of names independently verified. Already-reviewed rows also need a lightweight audit of their existing name authority before declaring the full 1,282 done.

## Phases and ordering

1. **Phase 1 — Name fast-pass:** Process the unreviewed Master Pool names first in small batches (8–12 per run; fewer when names are difficult). Check spelling, rank, name author, accepted genus, accepted family using Kew POWO/WCVP; use ITIS, World Flora Online, IPNI and relevant flora when ambiguous. Record exact source URL and date. No full distribution research. Use `ACCEPTED`, `SYNONYM_TO_ACCEPTED`, `ACCEPTED_WITH_CONCEPT_CAUTION`, or `HOLD_IDENTITY`; never manufacture an accepted mapping. Mark the native-range audit explicitly **DEFERRED**.
2. **Phase 2 — Previously reviewed and installed concepts:** Audit existing canonical `species.json` names/family/genus plus the remaining source-pool entries against their recorded authorities. Reuse credible recent verified sources rather than duplicate exhaustive research. Identify outdated binomials, inaccurate rank formatting, family placement, contradictory synonym notes and exact/near-duplicates. Do not rebuild installed galleries.
3. **Phase 3 — Synonym and duplicate reconciliation:** Group all variants of the same accepted taxon concept and check source-pool and canonical existing entries. Preserve original names as searchable aliases, merge evidence and observation/photo provenance, and hand mapping decisions to Approved Taxa Installer. Do not create a second card for a synonym; do not auto-collapse taxonomically distinct accepted taxa merely because older floras grouped them.
4. **Phase 4 — Exception review and audit closure:** Resolve true taxonomic conflicts, varieties/subspecies, hybrids, homonyms, and name-versus-photo concept disagreement with focused source/diagnostic work. Mark honest holds until evidence exists. Publish a ledger of which of the 1,282 source rows have verified-name records and which still need review; do not conflate with native range.

## Work-unit contract

- Refresh `PROJECT_RULES.md`, `workflow/COORDINATION.md`, `workflow/work-claims.json`, `data/manifest.json`, `research-queue.json`, the current Master Pool and prior `research-drafts/taxonomy-name-fast-pass/` batches. Skip active claims and previously verified names. Each batch must be independently durable and verified on GitHub main before reporting success.
- A record must include source pool spelling, accepted name with author, family/genus, accepted/synonym status, original source and authoritative URL, duplicate/homonym caution, and decision: new card possible / alias to concept / human concept review. Preserve original name for search.
- **Safe write boundary:** Name audit owns `research-drafts/taxonomy-name-fast-pass/` records and precise `_Master Pool Overrides` rows where safe. It does not install species or alter canonical species.json, media assets, genus/family modules, native-range evidence, native metrics, work owned by another claim, or the formula-driven Master Plant Pool body. Use fresh SHAs and verify writes.
- **Taxonomy alone does not verify specimen ID.** Especially for closely related species, leave photo/source-observation identity concerns as a distinct `concept_photo_review` handoff rather than implying all photographs are correct.
- Installation after name mapping is controlled exclusively by Approved Taxa Installer; photo/part installation by media lane; structural comparisons by genus/family lanes. Taxonomic identity conflicts genuinely block *separate duplicate concepts* but should not stop unrelated safe approved taxa.
- A pure native-range FAIL, HOLD, or UNRESOLVED never blocks approved encounter-value taxa.
- Prefer actual completed rows per automation run over expansive speculative batches. Skip/retry safely and choose another unclaimed group when blocked. Maintain the running ledger and cumulative counts, avoid re-review churn.

## First durable batch

`research-drafts/taxonomy-name-fast-pass/batch-2026-10-14-001.json`: 12 source rows checked, 9 accepted as entered, 1 accepted with a taxon-concept caution, and 2 historic synonym mappings. No species installed and no county nativity claimed. Notable:
- *Acaciella angustissima* var. *hirta* -> *A. angustissima* var. *texensis*; map alias rather than installing two varieties.
- *Arabis petiolaris* -> *Streptanthus petiolaris*; accepted name already appears in Master Pool.
- *Baptisia bracteata* is accepted as a distinct species from *B. leucophaea*; do not relabel Texas observations automatically.
- *Arenaria benthamii* requires author-identity awareness: *A. benthamii* Fenzl ex Torr. & A.Gray is accepted; *A. benthamii* Edgew. is a different illegitimate homonym.

## Automation instructions

**Taxonomy + Diagnostic Review** is the **single owner of new name-pass batches** unless a manual chat chooses a disjoint reserved set. For now it should prioritize Phase 1 and hand off 8–12 high-confidence names per run, with a small separately tracked `HOLD_IDENTITY` list. It should not spend a run on the county-range backlog or perform photo installs. When Phase 1 unreviewed backlog is exhausted, switch automatically to Phase 2 canonical name checks, then Phases 3/4. Other enabled automations continue their current independent roles.


## Taxonomy-only lightweight claim recovery (2026-10-21)

This section governs the Taxonomy Name Fast-Pass worker only; do not change other lanes' claim protocol.

- Before reserving, read canonical batch evidence, target-specific active claims, and the lease expiration. A canonical verified batch wins over an expired or stale claim; never republish it.
- Prefer a compact **per-batch** record at `workflow/taxonomy-claims/<batch-id>.json` rather than rewriting the large historical `workflow/work-claims.json`. Record batch ID, owner, exact taxa, claimed_at, expires_at (two hours), intended evidence path, status, and verified commit SHA if published. Create only after checking the target path and both legacy and new claims. Existing live legacy claims still take precedence.
- Use create-once for new claim files. Do not overwrite another worker's claim. If the per-batch claim write is rejected, do not publish without a safe reservation; preserve the research handoff and choose another eligible target.
- After publishing, verify the canonical batch file on main. Try to update **only that small claim file** to released with its fresh blob SHA. If release fails for a non-conflict safety/permission denial, do not retry via another route; the canonical batch remains completed and the claim expires naturally. On a genuine stale-SHA conflict, refetch/merge and retry once.
- Legacy `workflow/work-claims.json` remains readable as historical coordination; do not rewrite it solely to release a taxonomy claim. Never interpret expired historical `active` records as a current lock without checking their expiration and canonical publication.
- Preserve existing scientific and Sheet restrictions, exact evidence, source URLs, decisions, and original range/identity states. No automation schedule or other lane changes.
