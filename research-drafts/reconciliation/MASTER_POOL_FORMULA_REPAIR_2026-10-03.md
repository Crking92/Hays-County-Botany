# Master Plant Pool formula repair — 2026-10-03

## Status

**Complete and verified.**

## Problem

The Master Plant Pool used spill/ARRAYFORMULA columns but later accumulated row-positioned manual values. Those literals blocked formula expansion and produced `#REF!` in the formula anchors.

The blocking state included:

- one explicit manual species row for **Canna glauca** in A-D
- 198 manual Family cells in column F
- additional manual statuses, review notes, source summaries and curation values inside formula-managed columns

## Repair

The Master Plant Pool is now **formula-owned across A:Z below the header**.

Manual information was not discarded. It was migrated to stable key-based lookup structures:

- **_Master Pool Overrides** — 100 species with manual corrections/statuses/notes, keyed by Scientific Name
- **_Genus Family Map** — genus → family
- **_Family Order Map** — family → order

**Canna glauca** remains explicitly included via the overrides table; Canna → Cannaceae was added to the genus-family map and Cannaceae → Zingiberales to the order map.

## Verification

- Master species: **1,261**
- Keyed override species: **100**
- Override mismatches: **0**
- Formula errors: **0**
- Genus-family mismatches: **0**
- Family-order mismatches: **0**

## Standing rule

Do **not** type manual values directly into Master Plant Pool spill rows. Put species-specific corrections/statuses/notes in **_Master Pool Overrides**, genus-family changes in **_Genus Family Map**, and family-order changes in **_Family Order Map**.
