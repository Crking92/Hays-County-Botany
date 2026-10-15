# Approved Taxa Installer — limestone fern batch recovery (2026-10-15)

Batch: `curation-inbox/approved-installer-limestone-ferns-20261015-001/`.

Approved source-pool taxa: `anemia-mexicana` (Schizaeaceae) and `asplenium-resiliens` (Aspleniaceae). Both were absent from canonical manifest at 550 species; no active conflicting taxon claims or curation Action at staging.

**Do not add READY yet.** The main-branch package has both species.json, both SOURCES.txt, Anemia's complete image-sources.csv and a header-only Asplenium image-sources.csv. The full intended seven-file package was committed as `b30f15523086b8f978165baeaf6cb0d561a62d49` on `curation/approved-ferns-20261015-001`; attempts to publish the full Asplenium CSV and merge branch were blocked by connector safety checks. No installation Action was triggered.

Recovery: re-fetch main manifest, claims, inbox and Actions; compare branch CSV against main; replace only `taxa/Aspleniaceae/Asplenium/asplenium-resiliens/image-sources.csv` with the complete branch version (CC BY 4.0 Sam Kieschnick, exact-species habit image, Commons photo page and direct URL). Re-fetch all seven files and verify both photo licenses and direct URLs. Only then add `READY` in the final commit and check the Action once. Verify both canonical species and downloaded images before reporting installation. Preserve UNRESOLVED target-county status and native-metric exclusions; do not edit family/genus modules or UI. The separate Buddleja/Diaperia validation-only package remains untouched.
