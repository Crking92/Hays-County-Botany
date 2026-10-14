# Glass Root Garden — iNaturalist photo inventory

**Status:** Metadata inventory plus explicitly approved canonical photo installations; see per-batch manifests and reports.

## Purpose
Inventory all photos (not just the single image URL in the original CSV) attached to public Research Grade plant observations by `calvinking` in Texas. Cross-reference the *current* canonical `data/manifest.json`. Preserve individual photo ID, source link, license and iNaturalist attribution without exposing GPS coordinates.

## Run
On GitHub, open **Actions → Glass Root Garden iNaturalist Photo Inventory → Run workflow**. The workflow also runs automatically when first added. Download the `glass-root-inat-photo-metadata` artifact when complete. It contains:

- `photo-candidates.csv` — one row per actual photo, individual attribution and copyright gate, diagnostic role still pending
- `species-photo-summary.csv` — species/photo counts and GitHub canonical matching
- `summary.json` — totals and licensing warnings

To recreate an inventory for **exactly the IDs in the user's October 2026 CSV** on a local computer, run:

```bash
python scripts/glass_root_inat_photo_metadata.py --csv observations-797290.csv --out workflow/glass-root-inat/output
```

The GitHub workflow uses the public iNaturalist query for observer `calvinking`, Texas (place 18), Plantae (taxon 47126), Research Grade, because that private CSV is not checked into GitHub. Numbers can differ from the original export if observations change.

## Rights and validation rules
- The photographer's requested credit is **Glass Root Garden**, and the preferred license for personally owned photographs is **Creative Commons Attribution 4.0 (CC BY 4.0)**.
- **Do not assume** that a photo uploaded by `calvinking` is personally owned. Only label `candidate_for_visual_review` when the *individual photo* is already recorded CC BY on iNaturalist and the attribution text matches the expected photographer.
- If photo license is different, missing, or attribution does not match, retain it in the inventory with a rights-review hold. Do not silently convert another photographer's work or assume the observation data license applies to photos.
- Do not copy, download or publish photos from the candidate list until exact taxon, photographer/permissions, visual ID role, quality and source are confirmed.
- No BONAP/NAPA range status is inferred from iNaturalist observations. The nonmatching species require accepted-name reconciliation before creating cards.
- No hidden/private geolocation fields are stored in output. Observation page links remain, however, and may expose voluntarily public locations.

## Follow-up
Review a small high-value set first (Lindheimer's senna, Maximilian sunflower, flame acanthus, Simsia calva and other no-photo/one-photo installed taxa), download original photo files in approved batches, install true diagnostic views through the existing species photo pipeline, and verify both rendered cards and arrow targets. Other ongoing genus/family automation is unaffected.

## Owner-authorized private-use exception — 2026-10-14

Calvin explicitly confirmed his ownership and authorized use of his iNaturalist photographs in the private learner in this project chat. Follow [OWNER_PERMISSION_2026-10-14.md](OWNER_PERMISSION_2026-10-14.md). For new photos whose individual API record still says all rights reserved, retain that source state and record the separate owner-authorized private-study permission; set public_reuse=no. Do not invent a public CC license, change previous photo licenses, or apply this permission to another creator's photographs. Match exact observer, photo ID, scientific identity and owner attribution, inspect image content, and preserve all previous galleries/science.
