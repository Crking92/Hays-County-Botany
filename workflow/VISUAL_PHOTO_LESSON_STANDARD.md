# Visual learner — photo-led anatomy lesson standard
_Last approved by Calvin: 2026-10-13. Applies to canonical family, genus, species, look-alike, and glossary lessons._

## The user-approved teaching experience

Build a real **visual field guide**, not simply a text database. The learner should follow:
**See it → Spot it → Name it → Compare it → Remember it.**

On each species page, preserve the existing science and prominently link to the **full Family and Genus lessons**. Present a large, obvious **“Look at the actual plant parts”** section with separately labeled, accessible Family → Genus → Species groups. Within each group show **multiple relevant structure examples**, not only a generic whole-plant photo. The current website implementation (October 13) is in `assets/js/app.js` (`botanyPartExamples`, `botanyPartPhotoCard`, `botanyGenusPartPreview`, `taxonomyTeachingTrail`, `familyVisualLessonHTML`) with responsive styling in `assets/css/styles.css`. The app supports expandable groups, thumb-to-enlarge photos, plain-language descriptions, source credits, and explicit missing-photo placeholders. Keep these pieces working and improve their content as science/photos arrive; do not reinvent or remove them.

This applies across plant groups, not just milkweeds. For milkweeds a useful sequence includes family fused corolla/leaf clues, milkweed-specialized **corona, hoods, horn, gynostegium, pollinaria**, then foliage, flower clusters, follicle fruit and species differences. For asters, oaks, grasses, euphorbs, sages and others, select the *actual structures relevant to that taxon*, not a forced milkweed checklist.

## Every meaningful lesson should teach

1. **Family — why this family?** Show several representative real photographs illustrating reliable structural family clues, with exceptions and 1–3 important locally confusable families. Explain terms plainly alongside formal vocabulary. Do not incorrectly extend specialized subgroup traits to an entire family.
2. **Genus — why this genus?** Show several real examples of the anatomical traits shared by related species, an ordered “LOOK HERE FIRST”, differences from confusable genera, and a species comparison matrix/key where applicable. When a multi-species genus has weak media, list its exact missing photographic roles.
3. **Species — why this species?** Show distinct diagnostic perspectives when feasible: habit, leaf shape and attachment, reproductive macro, fruit/seed, stems/buds, and the precise tie-breakers against realistic look-alikes. Make photograph, caption and identification reasoning appear together.
4. **Photos before decorative diagrams.** Prefer a representative real plant image + a useful diagnostic macro, with *different* views where feasible, matched scale/angle for look-alikes. A pretty whole-plant image is not sufficient to teach hidden anatomy. Tap-to-enlarge and mobile legibility matter.
5. **Evidence accuracy first.** Differentiate (a) physically installed exact-species media, (b) credible externally linked/reference photographs, (c) a specific photo still needed. A card can use a representative family/genus species **if visibly labeled as such**. An external reference does not count as installed. Do not mislabel the subject species or assert a photo demonstrates an anatomical feature that was not visually verified.
6. **Future arrows, not invented ones.** Preserve annotations/arrow targets as **pending** until the photographed structure is personally verified on the actual image and target coordinates are checked. Do not claim that an existing source image contains arrows added by the learner. A named structure on an unannotated photo is a suggested *place to look*, not proof the feature is visible.
7. **Preserve provenance and rights.** Record exact species ID, file path or source_page, creator, license, reuse permissions, intended role, short teaching caption, and when possible observation/photo ID. User/Joey material is not automatically cleared for public use. Respect CC BY-NC / `public_reuse: review`, and do not silently upgrade reuse status.
8. **Respect scientific HOLD/FAIL.** Taxonomic identity, admission, source-pool scope, range status, scientifically uncertain characters, and original lessons remain authoritative. Do not remove existing information to simplify the UI. Provisional/visual-incomplete is an honest status, not a blocker to displaying the best available valid content.

## Small durable handoff per completed item

For a family, genus, or species being meaningfully curated, use established JSON/module fields and existing project conventions. Record:
- Family/genus/species and **the exact structures to inspect**, with simple phrasing plus botanical terminology;
- a **photo-role plan**, ideally several *different* specific features, including precise "where to look / why this separates it" cues;
- exact image candidates or installed paths, IDs, creator/license/source, what the verified photo actually shows;
- distinction between `installed_verified`, `external_reference`, `needs_photo`, and `annotation_pending` **in existing notes/fields** (do not impose an unsupported new JSON schema);
- accepted/overlapping diagnostic traits and realistic local look-alikes;
- what is complete versus still provisional, with a durable GitHub handoff to another lane when needed.

Do **not** rewrite completed modules merely to fill a quota, force five images of the same view, fake an annotation, or pause ongoing coverage while polishing one impossible macro. Existing source concepts, field keys, and status gates win.

## Ownership across five active automations

- **Family Similarity Polish:** refine structural **family** explanations, several exact diagnostic photo roles, representative image mappings, confusion separators and exceptions. Put lesson-ready content in established family diagnostic/visual-lesson fields. No bulk image installations or UI edits.
- **Genus Comparison Builder:** refine shared **genus** morphology, multiple photo roles, specific side-by-side species separating characters, and photo/arrow target handoffs. Continue filling genuinely unfinished multi-species genera. No bulk image installations or UI edits.
- **Taxonomy + Diagnostic Review:** verify scientific identity, accepted names, exact structural claims and **whether specific pictures can actually prove the distinguishing characters**. Record uncertainty and handoffs; do not alter canonical galleries or visual UI.
- **Diagnostic Photo Polish:** obtain, install and validate **several genuinely useful exact-taxon views** when possible. Target requests from the family/genus lessons. Keep licenses/attribution and installer preservation safeguards; verify files actually exist and metadata remains intact. Do not alter scientific fields or UI.
- **Approved Taxa Installer:** install approved taxa safely, preserving original science and prior media. Supply at least one proper exact-species view where practical and a specific list of missing photo roles. Do not delay admission on a final-quality five-photo gallery; hand off photo enrichment.

All five read `PROJECT_RULES.md` and `workflow/COORDINATION.md` every run; these files refer to this standard. Claim/release own scopes per normal coordination. Don't overwrite another worker. **Website/UI work owns rendering, mobile layout, previews and future verified arrows—not the research lanes.**

## Visual quality acceptance checks

- The useful structure title and plain-language explanation are visible alongside the image on mobile.
- Family/Genus/Species labels and navigation are obvious; actual full family and genus lessons are reachable.
- Images render from confirmed files (not merely an `images[]` counter), enlarge when tapped, and don't hide credits.
- Scientific captions match the real subject and visible structure; no wrong-species stand-ins or invented morphological confidence.
- Photo omissions are identified honestly; the next useful close-up is a concrete work item.
- Future arrows are approved only after visual check and spatial verification, with a note of their exact targeted structure.
- Preserve all original botanical terms, native-range decisions, look-alike comparisons, science evidence and media licenses.
- Finish with a small durable commit/handoff and re-fetch; don't equate "candidate found" with "installed photo verified."
