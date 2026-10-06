# Hays Botany ID Visual Learner — User Commands

These are plain-language commands Calvin can use in any ChatGPT conversation working on this project.
GitHub is the canonical project home. Scheduled Scout runs and the Deep Review automation may run automatically, but any of these can also be requested manually.

## Global coordination gate

Before any command below selects new work, refresh the current GitHub state and follow `workflow/COORDINATION.md`.

At minimum, check:
- `data/manifest.json`
- `workflow/work-claims.json`
- `research-queue.json`
- existing `research-drafts/`
- `curation-inbox/` / active curation state when relevant

If another chat or automation is already working the same taxon/scope, skip it. Create a short-lived work claim before starting work that has not yet been durably represented. Canonical state always wins over stale queue/chat assumptions.

## Research / Scout commands

### "Run another scout batch"
Process the next queued taxa in `research-queue.json` using the Botany Scout workflow. Gather taxonomy candidates, supporting occurrence leads, exact diagnostic-photo candidates, provenance, and a contact sheet. Do not curate or install automatically.

### "Scout [taxon]"
Research the named taxon immediately. If needed, add it to the queue first. Produce a research draft only.

### "Queue [taxon]"
Add the named taxon to the research queue without curating it yet.

### "Queue the next batch"
Choose the next useful taxa from approved source pools/backlogs, prioritizing personally observed and locally relevant taxa, and add them to the research queue.

### "Show me the queue"
Summarize queued, scouted, reviewing, ready, and blocked taxa.

## Review commands

### "Deep review the latest batch"
Independently audit newly scouted taxa using project source priority:
1. BONAP/NAPA
2. USDA PLANTS
3. Lady Bird Johnson Wildflower Center / NPSOT
4. authoritative regional floras / herbaria
5. iNaturalist / GBIF as supporting evidence only

Check taxonomy, native target-zone range, morphology, realistic local look-alikes, and whether photo candidates actually show diagnostic structures.

Return one status per taxon:
- READY FOR CURATION
- NEEDS MANUAL REVIEW
- REJECT / RE-SCOUT

### "Deep review [taxon]"
Run the same audit for one named taxon.

### "Re-scout photos for [taxon]"
Keep the research package but search again specifically for weak or missing diagnostic image roles.

### "Show me what needs approval"
Summarize only taxa that have completed deep review and are waiting for Calvin's decision.

## Curation commands

### "Approve [taxon]"
Treat Calvin's approval as permission to build the curated species package from the reviewed evidence. Do not skip required project validation.

### Source-pool default approval
During Learner Fast-Fill, Calvin has given standing learner-admission approval to taxa present in the approved source pools / derived Master Plant Pool. Individual approval is not required merely because native-range status is FAIL, HOLD, UNRESOLVED, or not yet fully audited. Preserve that range label separately and do not call the taxon confirmed native unless the evidence supports it. Taxonomic identity conflicts still require mapping to the correct accepted/represented concept before a separate card is installed.

### "Approve this batch"
Curate all taxa currently marked READY FOR CURATION in the referenced review batch.

### "Hold [taxon]"
Do not curate the taxon yet. Leave it available for later review.

### "Reject [taxon]"
Mark the current research attempt as unsuitable and preserve the reason. Do not install it.

### "Curate [taxon]"
Build the full morphology-first learner package, including diagnostic image roles, exact provenance, sources, local look-alikes, and LOOK HERE FIRST guidance. Send it through the normal curation pipeline.

## Source-pool / backlog commands

### "Build the next batch from my source pools"
Choose a balanced research batch from the master source pool using these priorities:
1. taxa Calvin has personally observed in iNaturalist
2. Hays County native taxa from authoritative local sources
3. NPSOT Edwards Plateau / Blackland Prairie backlog
4. taxa useful for completing a genus or family comparison set
5. common local confusers missing from the learner

Avoid duplicate taxa already curated, queued, or under review.

### "Give me the next [family/genus/order] batch"
Choose a sensible batch within that taxonomic group, emphasizing locally useful comparisons.

### "Find gaps in [family/genus]"
Compare the master source pool against the curated learner and queue/review state, then list missing useful taxa.

## Learner / interface commands

### "Update the review queue"
Refresh the learner-facing review data from current Scout and Deep Review results.

### "Show my iNaturalist plants not in the learner"
Use the deduplicated personal-observation list and compare it against curated taxa.

### "Show uncurated [family/genus]"
Filter the master source pool to taxa not yet in the learner.

### "Test me on [family/genus/taxon]"
Use the learner's morphology-first approach: LOOK HERE FIRST → diagnostic structure → confuser → reveal why.

## Normal status model

Approved source pool
→ learner admission approved
→ taxonomy/ID review as needed
→ morphology + visual package
→ curated package
→ installed learner

Native-range status runs in parallel as metadata:

`PASS / FAIL / UNRESOLVED / CONFLICT / COMPARISON`

A range HOLD no longer means "do not use in the learner." It means "do not label as confirmed target-zone native yet."

No automated Scout or Reviewer may create a misleading duplicate taxon concept; canonical installation still belongs to the curation/installer lane.
