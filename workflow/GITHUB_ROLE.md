# GitHub role

Repository: `Crking92/Hays-County-Botany`

GitHub is the canonical persistent home for Hays Botany ID.

## Canonical content
GitHub stores:
- species curation data
- learner files
- taxonomy/range decisions
- morphology and look-alike packages
- image-source selections and licensing/provenance
- workflow rules
- manifests and validation outputs

## Automation responsibilities
After curation has selected exact approved image sources, GitHub automation handles:
- photo downloading
- resizing/normalization
- species-folder image installation
- manifest generation
- validation of required files and metadata

Automation should not silently choose substitute photographs or change unresolved taxonomy/range decisions.

## Finalization rule
Only complete, validated packages should be treated as final.

Any species with unresolved taxonomy, range status, morphology, look-alikes, or image provenance remains explicitly incomplete.
