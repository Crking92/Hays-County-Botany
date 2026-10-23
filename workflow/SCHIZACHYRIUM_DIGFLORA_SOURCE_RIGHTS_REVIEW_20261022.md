# Little bluestem: four anatomically verified North Hays source photos — rights/finish audit (2026-10-22)

**Outcome:** All **four real Bob Harms original DigFlora/KR photographs** were fetched and decoded as genuine JPEGs by the Hays GitHub Actions verifier. The source hashes and dimensions are preserved in `reports/schizachyrium-digflora-four-source-verification-20261022.json`, audit commit `e279eacbeee952d177d4b8f36a7fb6e773eac8c0`. All four original direct URLs, botanical roles, primary references, source rights holds and research notes have been saved in `content/taxa/Poaceae/Schizachyrium/schizachyrium-scoparium/species.json` and `genus.json`. **None of these four copyright-unresolved originals was downloaded into / rehosted from the public git repository.** We already have 15 separately sourced local photos and 16 species teaching panels.

## Photo-specific scientific verification

| Source original | Actual original pixels | Bob Harms' documented morphology | Honest limit |
| --- | ---: | --- | --- |
| [SCSC-L-Shth-Nod.JPG](https://w3.biosci.utexas.edu/prc/DigFlora/KR/0-BOISS4Web/SCSC-L-Shth-Nod.JPG) | 573 × 360 | L-labelled real **ligule**, with blade/sheath/keel/nodes and photographed original metric scale | Not a demonstrably fully unfolded free membrane with tip/fringe proved at 1mm |
| [SCSC-disart-w-red.JPG](https://w3.biosci.utexas.edu/prc/DigFlora/KR/0-BOISS4Web/SCSC-disart-w-red.JPG) | 298 × 504 | Author labels **A** axis segment, **F** fertile sessile spikelet, **P** pedicellate companion; red arrows at rachis disarticulation, physical scale | Not clearly the same numbered plant as the separate root/dissection photo |
| [SCSC-spkcut.JPG](https://w3.biosci.utexas.edu/prc/DigFlora/KR/0-BOISS4Web/SCSC-spkcut.JPG) | 429 × 333 | Separated **g1** first glume, **g2** second glume, **lf** fertile lemma, **ls** sterile lemma, **ps** sterile palea, with physical scale | Detached parts; not demonstrated to be from the exact attached A/F/P photographed raceme |
| [SCSC-04-P-bX.JPG](https://w3.biosci.utexas.edu/prc/DigFlora/KR/0-BOISS4Web/SCSC-04-P-bX.JPG) | 432 × 498 | Actual little-bluestem rooted tuft, dense culm bases and fine fibrous roots, N. Hays study | No full mature flowering shoot in this individual picture; same-voucher chain not established |

Source page: https://w3.biosci.utexas.edu/prc/DigFlora/KR/SCSC.html

## Cross-source morphology audit

- **Accepted name:** Schizachyrium scoparium (Michx.) Nash, accepted by Kew POWO: https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:420956-1/general-information
- **Ligule:** FNA 0.5–2 mm; Kew GrassBase 1–3 mm and uses the term *eciliate membrane*, while SDSU educational description calls it *fringed* and less than 2.5 mm. This discrepancy must **not** become a false single absolute character; examine the actual inner membrane and its free edge rather than nearby longer sheath hairs. https://openherbarium.org/portal/taxa/index.php?clid=26&taxauthid=1&tid=239979 and https://openprairie.sdstate.edu/nativeplant/114/
- **Fertile/pedicellate pair:** the sessile spikelet contains upper fertile bisexual and lower sterile florets; companion pedicellate member can be reduced/sterile OR more developed/staminate. The genus must not be identified merely from a tiny pedicellate stub.
- **Local contrast with King Ranch bluestem:** numerous short racemes at upper leafy branch tips vs KR's clustered longer terminal fingers. Leaf color, single node hair or unmeasured detached fluffy spikelet is insufficient, especially before recommending invasive removals.
- **Locality:** Harms discusses North Hays populations. Nothing in the original page identifies an accession number connecting ALL four actual photographs to ONE live collected individual. Save this limitation, do not invent same-voucher provenance.

## Copyright / source-use decision

Bob Harms's *Selected Central Texas Monocots* homepage (https://w3.biosci.utexas.edu/prc/Monocots/) permits credited scientific/educational reuse of **that selected collection**. The four above are different original files in **DigFlora/KR**, whose exact publication/rehosting terms were not shown on its photo page. The PRC Travis herbarium-image gallery has its own distinct five-image/noncommercial terms; those also cannot automatically cover these four author photographs.

**Current safe publication decision:** preserve exact public source links + creator attribution + original JPEG SHA-256 fingerprints, and retain site-only research links. Do not add four DigFlora/KR original JPEGs to the public learner or publish altered/cropped copies until the rightsholder confirms permission to reproduce those exact sources publicly.

### Ready permission question for the creator / PRC

> I'm producing a free, noncommercial educational visual identification guide for Central Texas field crews. May I reproduce the four **Bob Harms DigFlora/KR original photographs** listed above, credited to Bob Harms and linked to the DigFlora/KR source page, on the public Hays County Botany GitHub Pages learner and in its public GitHub photo folder? The site will not sell or sublicense photographs. Please confirm whether the **Selected Central Texas Monocots** scientific/educational reuse statement also covers these four separate DigFlora originals, or provide any specific credit, noncommercial, or redistribution restrictions.

**Do not report that a permission request was sent**: this file merely prepares the exact question for the user/rightsholder.

## Final 100-percent photo gate

Status stays `FIELD_READY_PHOTO_GAPS` even though field teaching is strong. For strict photographic FINISHED, either a clear source/collection accession ties a genuinely mature rooted flowering source to both the ligule and real same-voucher A/F/P dissection **with demonstrably accurate scale**, or obtain a verified fresh Hays County source-vouchered specimen photo series. Distinct licensed anatomy across separate specimens still supports a **field-ready** teaching card, but not the current project criterion of one connected detailed specimen.

Re-run only the metadata audit script `scripts/verify_schizachyrium_digflora_four_sources_20261022.py` if source URLs change; it neither archives copyrighted images nor promotes the taxon to FINISHED. In parallel, study already locally archived Bob Harms Selected Monocots / USGS photos, which are independently rights-cleared on their exact sources.
