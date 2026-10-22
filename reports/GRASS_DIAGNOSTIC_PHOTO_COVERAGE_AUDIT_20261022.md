# Poaceae diagnostic-photo completion inventory — 2026-10-22

## Scope and exact interpretation

Audited **all 112 canonical installed Poaceae species.json files** enumerated by the current `data/manifest.json` (53 genera) on 2026-10-22. Each file was fetched from GitHub and parsed individually. No records were skipped or inaccessible in this pass.

This is a **canonical metadata and species-gallery ROLE screen**, not a pixel-by-pixel forensic image audit and not a fresh botanical re-determination. Photo-role evidence was screened from `visual_comparison.items` whose `scientific_name` matches the target species. Source photo IDs, life-stage/structure labels, official finish statuses, and explicit last-mile gaps are kept separate from actual diagnostic verification.

### Quantitative results

| Audit measure | Species | Interpretation |
|---|---:|---|
| Canonical species installed | **112** | Count independently confirmed from manifest |
| Genera | **53** | Manifest genus directory count |
| **Marked VERIFIED `FINISHED` by the strict diagnostic-photo standard** | **0 / 112** | No card has exact `FINISHED` in the inspected `field_id_finish_pass.stage` / fallback `curation_status.visual_finish` |
| At least one same-species gallery panel mentioning *whole habit / roots / tuft / crown / runner* | **60 / 112** | Optimistic keyword/role screen, **not** proof of full rooted source-vouched habit |
| At least one same-species gallery panel mentioning *ligule / leaf collar / blade–sheath junction* | **25 / 112** | Does not prove actual membrane, scale, or valid arrow |
| At least one same-species panel mentioning fine reproductive morphology (*lemma / glume / palea / callus / pedicel / detailed spikelet*) | **44 / 112** | Includes descriptive or reference macro panels; **not** independently verified decisive fertile anatomy |
| **At least one panel in all three broad photo-role groups** | **17 / 112** | Shortlist for further independent QA only; NOT 17 FINISHED species |
| Missing at least one broad role by this screen | **95 / 112** | Highest priority for filling a substantive missing photo role |

The earlier grass field-identification status report recorded **107 of 112 field-ready** (95.5%). This is a **different, less strict denominator of success** and should **not** be relabeled as full diagnostic-photo completion. Four canonical scientific-identification holds remain (`anatherum-tenuispatheum`, `chloris-x-subdolichostachya`, `muhlenbergia-x-involuta`, `sorghastrum-elliottii`). By user direction `muhlenbergia-piniflora` is deliberately reserved until last.

The strict factual conclusion is **zero VERIFIED `FINISHED` records**, NOT a claim that every species actually lacks every required photographed organ. Several cards contain strong source-licensed diagnostic imagery and should be prioritized for photo-accuracy QA rather than reacquiring generic photographs.

## The 17 candidates with at least one same-species gallery panel in each broad photo-role group

These **are not complete**. They have candidate material for whole habit, collar/ligule, and detailed reproduction, and must pass exact-source identity, license, anatomy, image-resolution, measured scale, local look-alike, marker accuracy and taxon-science checks before someone may consider `FINISHED`.

1. `andropogon-gerardi` — Bob Harms Central Texas scaled floral macros; same-voucher local attached fertile/pedicelled pair and full culm still missing.
2. `arundo-donax` — metadata role coverage; live card has no strict `FINISHED` certification.
3. `bothriochloa-ischaemum` — KR bluestem; papilla-based blade hairs, true membrane measurement and full attached Texas spikelet pair remain.
4. `bouteloua-dactyloides` — buffalograss; rooted stolon, natural female bur and true ligule remains.
5. `echinochloa-crus-galli` — *E. muricata* versus introduced species fertile upper-lemma membranous tip/hairline under 25–40× still missing.
6. `eleusine-indica` — real external goosegrass ligule and already annotated spikelet; original restricted-license photo remains held and rooted Texas specimen / same plant still missing.
7. `eragrostis-hirsuta` — still requires independent exact diagnostic marker/structure QA.
8. `eragrostis-trichodes` — still requires independent exact diagnostic marker/structure QA.
9. `hopia-obtusa` — still requires independent exact diagnostic marker/structure QA.
10. `leersia-oryzoides` — sheath/nodes/ligule and lemma/palea photographed; actual retrorse BLADE-margin teeth with a 1 mm scale and verified lowermost panicle branch count still missing.
11. `muhlenbergia-x-involuta` — exact-species photographic coverage exists, but independent voucher-anatomy/hybrid scientific hold persists; **do not clear or prioritize as easy finish**.
12. `panicum-virgatum` — true collar, scaled spikelets already pictured; additional same-source local specimen and comparative proof must be evaluated, not automatically FINISHED.
13. `polypogon-monspeliensis` — role coverage is screening-only; exact diagnostic measurements and comparisons need QA.
14. `schizachyrium-scoparium` — detailed first upgrade done elsewhere; 1 mm actual local ligule and attached paired spikelet/rachis still missing.
15. `setaria-parviflora` — photographic Croatia series demonstrates true rhizome, hair ligule, basal bristles and original labeled glumes/lemmas, but same-plant Hays voucher and bristle counts still need verification.
16. `sorghastrum-nutans` — documented true ligule and bare pedicel macro; same-plant Texas 1 mm collar and intact fertile/bare-pedicel attachment remain.
17. `sorghum-halepense` — actual source rhizome and hairy collar photographed, but paired sessile/pedicellate spikelet bases and measured membrane remain.

**Eleven of these 17** also have explicit different-species look-alike photo panels in the target species lesson. The remaining six do not yet expose such panels in the same species card, even if a genus or comparison table describes look-alikes. This is a *presentation metadata* count, not a quality endorsement.

## Immediate prioritized next phase

- **A. Finish-photo opportunity review:** examine the best 17 source-verified role-rich cards first for actual pixels and a clearly bounded last missing feature. Preserve any science/license holds; do not relabel the 17 as done.
- **B. Missing collar/ligule lane:** this is the largest measurable broad organ gap (only 25 of 112 species cards mention a same-species collar photo). Scout real, licensed actual blade/sheath junctions with 1 mm scales, rather than repeating flowerhead photos.
- **C. True reproductive macro lane:** prioritize photographed **attached** spikelets, glumes and lemmas, pedicel pairs, awn insertions, hairs, and *measured* traits in 10–40× photos. Preserve a precise last-mile hold when a source is unavailable.
- **D. Public QA:** put only permissibly credited species-verified pictures into ordinary species gallery with `PROVISIONAL — USER PHOTO REVIEW PENDING`. Validate correct anatomy arrow pixel locations before adding markers. Do not infer local native/county status from overseas photos.
- **E. Science exceptions:** preserve four botanical holds, postpone `muhlenbergia-piniflora`, and maintain historical rejected/unlicensed materials outside public image galleries.

### Classification rules for all grass chats

For each target, require (1) exact-source, publicly usable whole-plant growth form, (2) photographed correct actual leaf sheath and diagnostic collar with suitable scale, (3) entire flowering architecture from an attached plant, (4) **actual diagnostic reproductive structures** photographed at relevant scale, (5) supported visible arrows and source-identified relevant local look-alikes, (6) explicit science/range and photo rights reviewed. `FIELD_READY_PHOTO_GAPS` is the honest result if it is usable for crew ID but anything critical is missing. `FINISHED` is reserved for independent verified closeout of all critical differentiating evidence; no card can pass merely by gallery count or substring matches.

*Audit provenance:* live GitHub `data/manifest.json` SHA `db14364428bd3119ed63c8c335ea8f4f2669be60`, and 112 individual canonical species.json fetches on 2026-10-22. The counts above are derived from present gallery text and finish flags, not a claim that 112 original photographs were independently enlarged and anatomically vetted in this pass.
