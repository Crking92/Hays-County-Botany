# Approved installer recovery — 2026-10-15

Batch: `approved-installer-cornus-cotinus-20261015-001` (mode install, require exact images). DO NOT ADD READY YET.

Source-pool approved, POWO accepted, absent from canonical manifest (578 at check): Cornus drummondii (Master Plant Pool row 299, Cornaceae) and Cotinus obovatus (row 306, Anacardiaceae). Both from installer preflight mass-02, no active conflicting claims found.

Successfully committed on main: `batch.json`, both `SOURCES.txt`, both `image-sources.csv`. Exact Wikimedia Commons photographs inspected and licenses recorded: Cornus white fruit and red pedicels, Douglas Goldman CC BY-SA 4.0; Cotinus obovate foliage, David J. Stang CC BY-SA 4.0. Both need additional diagnostic close-ups; do not claim they show unphotographed anatomy.

BLOCKER: creation of each `species.json` was rejected by connector safety checks. Cornus was retried once with a shorter valid species card and rejected again. Attempt to update `batch.json` with this note also rejected. Missing exact files:
- `taxa/Cornaceae/Cornus/cornus-drummondii/species.json`
- `taxa/Anacardiaceae/Cotinus/cotinus-obovatus/species.json`

Required card content: Cornus LOOK HERE FIRST opposite rough hairy leaves, arcuate veins, white drupes on reddish pedicels; Cotinus LOOK HERE FIRST alternate obovate entire leaves and hairy-pedicelled panicles. Include morphology, measured leaf/fruit traits, look-alikes, explicit needs_photo, attribution, `images: []`, learner admission from approved pool. Preserve both internal target-zone `UNRESOLVED`, exclude from confirmed-native metrics; Texas state-level nativity alone is not a three-county PASS.

Recovery next: refresh manifest/claims/inbox/Actions; if still absent and unclaimed, publish both `species.json`, re-fetch all seven package files, add `READY` LAST, check Action once and verify canonical manifest, physical images and images[] before counting installed. Do not alter other lanes, galleries, formula-owned Sheets or automation schedules.
