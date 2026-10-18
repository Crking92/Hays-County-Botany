#!/usr/bin/env python3
"""Read-only learner-wide diagnostic photo triage. Never changes species/cards."""
from __future__ import annotations
from collections import Counter, defaultdict
from datetime import datetime, timezone
from hashlib import sha256
from io import BytesIO
from pathlib import Path
import json
import re
from xml.etree import ElementTree

from PIL import Image, ImageOps
from photo_quality_audit import audit, load

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports"
PREFIX = "diagnostic-photo-audit-057-20261017"
GROUPS = {
    "Poaceae": ("grass_spikelet_and_ligule", r"ligule|spikelet|sheath|awn|floret|collar"),
    "Asteraceae": ("aster_phyllaries_and_reproductive_parts", r"phyllar|involucr|pappus|capitulum|floret|trichome"),
}
GENUS_GROUPS = {
    "Quercus": ("oak_acorn_cup_bud_and_leaf", r"acorn|cupule|bud|leaf underside|leaf base"),
    "Asclepias": ("milkweed_corona_hoods", r"corona|hood|gynostegium|pollinaria|pollinium"),
    "Funastrum": ("milkweed_vine_flower_structure", r"corona|hood|gynostegium|pollinaria"),
    "Matelea": ("milkweed_vine_flower_structure", r"corona|hood|gynostegium|pollinaria"),
    "Gonolobus": ("milkweed_vine_flower_structure", r"corona|hood|gynostegium|pollinaria"),
    "Croton": ("croton_female_flower_and_trichomes", r"pistillate|female flower|sepal|trichome|stellate|style"),
    "Euphorbia": ("euphorbia_cyathium_and_capsule", r"cyathium|gland|involucre|capsule|seed"),
    "Galium": ("galium_whorl_and_fruit", r"whorl|hook|bristle|fruit|flower"),
    "Silene": ("silene_sticky_node_and_calyx", r"sticky|gland|node|calyx|capsule"),
    "Ludwigia": ("ludwigia_flower_and_fruit", r"hypanthium|ovary|sepal|capsule|fruit"),
    "Ipomoea": ("morning_glory_sepals_and_leaf", r"sepal|calyx|leaf lobe|leaf base|capsule"),
}
GENERAL_PARTS = {
    "recognize": re.compile(r"recognize|whole plant|plant habit|growth habit|tree canopy|rosette|bunchgrass|clump|groundcover|landscape", re.I),
    "look_closer": re.compile(r"look closer|leaf|leaves|flower|floret|fruit|pod|seed|petiole|bark|bud|twig|petal|stamen|pistil|foliage|stem", re.I),
    "confirm_clue": re.compile(r"confirm clue|ligule|phyllar|involucr|corona|gynostegium|pollinaria|cyathium|pistillate|trichome|awn insertion|cupule|acorn|sticky band|bristle", re.I),
}
PROVISIONAL = re.compile(r"provisional|unverified|pending|metadata.only|not visually certified|not expert verified|review required", re.I)

def diagnostic_group(sp):
    genus = str(sp.get("genus") or "")
    family = str(sp.get("family") or "")
    if genus in GENUS_GROUPS: return GENUS_GROUPS[genus]
    return GROUPS.get(family, ("general_field_ID_parts", r"leaf|flower|fruit|seed|stem|bud"))

def checksum_and_pixels(path):
    raw = path.read_bytes()
    digest = sha256(raw).hexdigest()
    if path.suffix.lower() == ".svg":
        # Browser-displayable vector art is not a JPEG; Pillow alone cannot decode it.
        # Validate XML without fetching external resources. No fabricated pixel-hash.
        root = ElementTree.fromstring(raw)
        if root.tag != "{http://www.w3.org/2000/svg}svg":
            raise ValueError("Not an SVG document")
        viewbox = root.attrib.get("viewBox", "").replace(",", " ").split()
        if len(viewbox) != 4:
            raise ValueError("SVG has no numeric viewBox")
        width, height = int(float(viewbox[2])), int(float(viewbox[3]))
        if width <= 0 or height <= 0:
            raise ValueError("SVG viewBox invalid")
        return digest, width, height, None
    with Image.open(BytesIO(raw)) as pic:
        pic.verify()
    with Image.open(BytesIO(raw)) as pic:
        im = ImageOps.exif_transpose(pic)
        width, height = im.size
        gray = im.convert("L").resize((9, 8), Image.Resampling.LANCZOS)
        a = list(gray.getdata())
        value = 0
        for y in range(8):
            for x in range(8):
                value = (value << 1) | (a[y*9+x] > a[y*9+x+1])
        return digest, width, height, value

def active_claim_ids(claims, sid, now):
    out = []
    for c in claims.get("claims", []):
        if c.get("status") not in ("active", "queued", "blocked"): continue
        expire = c.get("expires_at")
        if expire:
            try:
                if datetime.fromisoformat(expire.replace("Z", "+00:00")).astimezone(timezone.utc) <= now:
                    continue
            except (ValueError, TypeError): pass
        if sid in (c.get("taxa") or []): out.append(str(c.get("claim_id") or "unnamed"))
    return out

def run():
    manifest = load(ROOT / "data/manifest.json")
    indexfile = ROOT / "workflow/photo-library/species-index.json"
    index = load(indexfile) if indexfile.exists() else {}
    library = index.get("species") or {}
    claims = load(ROOT / "workflow/work-claims.json")
    now = datetime.now(timezone.utc)
    results, hashes_by_taxon, cross_sha = [], {}, defaultdict(set)
    totals = Counter()
    bad_manifest = []
    for entry in manifest.get("species") or []:
        sid = str(entry.get("id") or "")
        rel = str(entry.get("path") or "")
        path = (ROOT / rel).resolve()
        if not sid or not rel or not path.is_relative_to(ROOT) or not path.is_file():
            bad_manifest.append((sid, rel))
            continue
        sp = load(path)
        baseline = audit(entry, sp, ROOT, claims, now)
        requested_label, target_regex = diagnostic_group(sp)
        requested = re.compile(target_regex, re.I)
        row = {
            "id": sid, "scientific_name": str(sp.get("scientific_name") or sid),
            "path": rel, "family": str(sp.get("family") or ""), "genus": str(sp.get("genus") or ""),
            "gallery_entries": len(sp.get("images") or []),
            "physical_photos": 0, "vector_illustrations": 0, "external_only": 0, "broken": [], "unreadable": [],
            "small_photo_candidates": [], "same_source_photos": [], "exact_duplicates": [],
            "possible_visual_duplicates": [], "missing_attribution_or_license": [],
            "provisional_status_photos": 0, "explicitly_anatomy_verified_photos": 0,
            "explicitly_identity_verified_photos": 0,
            "three_role_cues_in_metadata": [], "role_metadata_gaps": baseline["missing_role_metadata"],
            "priority_structure": requested_label, "priority_structure_role_cue": False,
            "archive_candidates_indexed": (library.get(sid) or {}).get("stored_images", 0),
            "claimed": active_claim_ids(claims, sid, now),
            "parts_to_recheck": str(sp.get("look_here_first") or "")[:340],
        }
        role_cues = set()
        seen_url, seen_hash = {}, {}
        hashes = []
        for pos, im in enumerate(sp.get("images") or []):
            if not isinstance(im, dict): continue
            f = str(im.get("file") or "")
            role = " ".join(str(im.get(k) or "") for k in ("role", "view", "image_role"))
            source = str(im.get("media_source_url") or im.get("source_page") or "").strip()
            if source and source in seen_url: row["same_source_photos"].append([seen_url[source], pos])
            if source: seen_url[source] = pos
            for name, pattern in GENERAL_PARTS.items():
                if pattern.search(role): role_cues.add(name)
            if requested.search(role): row["priority_structure_role_cue"] = True
            if PROVISIONAL.search(role + " " + str(im.get("photo_review") or "")):
                row["provisional_status_photos"] += 1
            if im.get("diagnostic_role_verified") or im.get("annotation_verified"):
                row["explicitly_anatomy_verified_photos"] += 1
            if im.get("expert_botanical_identity_verified") is True:
                row["explicitly_identity_verified_photos"] += 1
            if not (im.get("creator") or im.get("credit")) or not im.get("license") or not im.get("source_page"):
                row["missing_attribution_or_license"].append(pos)
            if not f or f.startswith(("http://", "https://")) or im.get("external_reference"):
                row["external_only"] += 1
                continue
            image_path = (path.parent / f).resolve()
            if not image_path.is_relative_to(ROOT) or not image_path.is_file():
                row["broken"].append({"index": pos, "file": f})
                continue
            try:
                digest, w, h, dh = checksum_and_pixels(image_path)
            except (OSError, ValueError, SyntaxError, TypeError) as e:
                row["unreadable"].append({"index": pos, "file": f, "error": type(e).__name__})
                continue
            row["physical_photos"] += 1
            if dh is None: row["vector_illustrations"] += 1
            cross_sha[digest].add(sid)
            if digest in seen_hash:
                row["exact_duplicates"].append([seen_hash[digest], pos])
            seen_hash[digest] = pos
            if min(w, h) < 350: row["small_photo_candidates"].append({"index": pos, "dimensions": [w, h]})
            for idx, prev, previous_w, previous_h in hashes:
                if dh is not None and prev is not None and (dh ^ prev).bit_count() <= 4 and abs(w/h - previous_w/previous_h) < 0.10:
                    row["possible_visual_duplicates"].append([idx, pos])
            hashes.append((pos, dh, w, h))
        row["three_role_cues_in_metadata"] = sorted(role_cues)
        row["missing_teaching_steps_in_metadata"] = sorted(set(GENERAL_PARTS) - role_cues)
        row["review_flags"] = []
        for key, label in (("broken", "missing_image_file"), ("unreadable", "unreadable_photo"),
                           ("exact_duplicates", "exact_duplicate_files"),
                           ("possible_visual_duplicates", "possible_near_duplicate_views"),
                           ("same_source_photos", "same_source_requires_dedup_review"),
                           ("small_photo_candidates", "low_resolution_candidate"),
                           ("missing_attribution_or_license", "provenance_incomplete")):
            if row[key]: row["review_flags"].append(label)
        if row["physical_photos"] == 0: row["review_flags"].append("no_physically_installed_photo")
        if not row["priority_structure_role_cue"]:
            row["review_flags"].append("specialized_diagnostic_role_not_documented")
        if row["gallery_entries"] >= 3 and not row["priority_structure_role_cue"]:
            row["review_flags"].append("three_plus_without_documented_diagnostic_macro")
        row["priority_score"] = (
            (160 if row["physical_photos"] == 0 else 0)
            + (25 if row["physical_photos"] == 1 else 10 if row["physical_photos"] == 2 else 0)
            + 115*len(row["broken"]) + 100*len(row["unreadable"])
            + 65*len(row["exact_duplicates"]) + 24*len(row["possible_visual_duplicates"])
            + 65*(not row["priority_structure_role_cue"])
            + 18*len(row["missing_teaching_steps_in_metadata"])
            + 20*len(row["missing_attribution_or_license"])
            + 10*len(row["small_photo_candidates"])
            + (12 if row["archive_candidates_indexed"] else 0)
        )
        hashes_by_taxon[sid] = hashes
        results.append(row)
        totals["gallery_entries"] += row["gallery_entries"]
        totals["physical_photo_files"] += row["physical_photos"]
        totals["vector_illustrations"] += row["vector_illustrations"]
        totals["broken"] += len(row["broken"])
        totals["unreadable"] += len(row["unreadable"])
        totals["exact_duplicate_pairs"] += len(row["exact_duplicates"])
        totals["possible_visual_duplicate_pairs"] += len(row["possible_visual_duplicates"])
        totals["no_role_macro_metadata"] += int(not row["priority_structure_role_cue"])
        totals["three_plus_lacking_macro_cue"] += int(row["gallery_entries"] >= 3 and not row["priority_structure_role_cue"])
        totals["cards_with_local_zero"] += int(row["physical_photos"] == 0)
        totals["cards_with_local_one"] += int(row["physical_photos"] == 1)
        totals["cards_with_local_two"] += int(row["physical_photos"] == 2)
        totals["cards_with_local_three_plus"] += int(row["physical_photos"] >= 3)
    if bad_manifest or len(results) != len(manifest.get("species") or []):
        raise RuntimeError("Manifest not fully audited: " + repr(bad_manifest[:20]))
    source_collision = [sorted(ids) for ids in cross_sha.values() if len(ids) > 1]
    available = sorted((x for x in results if not x["claimed"]), key=lambda x: (-x["priority_score"], x["id"]))
    family_focus = defaultdict(list)
    for x in available:
        if x["priority_structure"] != "general_field_ID_parts":
            family_focus[x["priority_structure"]].append(x)
    priority = []
    for x in available:
        if x["physical_photos"] == 0 or x["broken"] or x["unreadable"] or x["exact_duplicates"]:
            priority.append(x)
    for group in ("grass_spikelet_and_ligule", "aster_phyllaries_and_reproductive_parts",
                  "milkweed_corona_hoods", "milkweed_vine_flower_structure",
                  "croton_female_flower_and_trichomes", "euphorbia_cyathium_and_capsule",
                  "oak_acorn_cup_bud_and_leaf", "galium_whorl_and_fruit", "silene_sticky_node_and_calyx"):
        priority.extend(family_focus[group][:10])
    priority.extend(available[:90])
    dedup, seen = [], set()
    for x in priority:
        if x["id"] not in seen:
            dedup.append(x); seen.add(x["id"])
    summary = dict(totals)
    summary.update({
        "audit_time_utc": now.isoformat(), "manifest_species": len(results),
        "known_library_species": len(library), "library_index_date": index.get("last_rebuilt_utc"),
        "cross_species_identical_file_sets": source_collision[:100],
        "cross_species_identical_file_group_count": len(source_collision),
        "claimed_species": sum(bool(x["claimed"]) for x in results),
        "unclaimed_priority_queue_length": len(dedup),
        "scope": "All manifest species photo metadata, local file presence, image decode, exact and possible visual duplicate detection; NO expert botanical pixel-ID certification.",
        "inference_caveat": "An absent role label is not proof an organ is absent. A matching role label is NOT pixel verification. Perceptual hashes only suggest lookalikes for human review. Image decoding does not verify exact species identification.",
    })
    out_json = {
        "summary": summary, "priority_queue": [x["id"] for x in dedup],
        "rows": sorted(results, key=lambda x: x["id"]),
    }
    lines = [
        "# Diagnostic photo audit 057 — entire Hays learner",
        "", "Generated: " + now.isoformat(), "",
        "## What this pass actually checks",
        "",
        "**Complete automated technical/metadata inventory** over every canonical species. JPEG/PNG files are decoded and inspected for pixel dimensions; identical files and potential perceptual near-duplicates are flagged. Anatomy roles are **metadata cues only** and NOT visual or expert species certification. No files or science changed.",
        "",
        "## Live results", "",
        "| Metric | Count |", "|---|---:|",
    ]
    for key, label in [
        ("manifest_species", "Canonical species"), ("gallery_entries", "Gallery image records"),
        ("physical_photo_files", "Locally installed readable images (raster and validated SVG)"),
        ("vector_illustrations", "Validated SVG illustrations"), ("cards_with_local_zero", "Cards with 0 readable local images"),
        ("cards_with_local_one", "Cards with 1"), ("cards_with_local_two", "Cards with 2"),
        ("cards_with_local_three_plus", "Cards with 3+"), ("broken", "Broken local references"),
        ("unreadable", "Unreadable image files"), ("exact_duplicate_pairs", "Exact duplicates within cards"),
        ("possible_visual_duplicate_pairs", "Potential perceptual duplicates (review required)"),
        ("no_role_macro_metadata", "Cards without documented key structural role"),
        ("three_plus_lacking_macro_cue", "3+ photo cards without documented key structural cue"),
        ("cross_species_identical_file_group_count", "Identical image hashes across species (review required)"),
        ("claimed_species", "Currently claim-owned cards held from new manual assignment")
    ]:
        lines.append("| " + label + " | **" + str(summary[key]) + "** |")
    lines += [
        "", "## Ranked manual *pixel-inspection* work queue",
        "",
        "Priority emphasizes broken/absent media and distinctive botanical structures. Matching labels do not prove anatomy is shown. Frozen claims skipped. Archived candidate counts are stale and remain provisional.",
        "",
        "| Plant | Family | Saved | Missing anatomical cue (metadata) | Archive leads | Priority |",
        "|---|---|---:|---|---:|---:|",
    ]
    for row in dedup[:75]:
        lines.append("| *" + row["scientific_name"].replace("|", " ") + "* | " + row["family"] +
                     " | " + str(row["physical_photos"]) + " | " +
                     ("check " + row["priority_structure"] if not row["priority_structure_role_cue"] else "role appears; verify pixels") +
                     " | " + str(row["archive_candidates_indexed"]) + " | " + str(row["priority_score"]) + " |")
    lines += [
        "", "## Review contract",
        "",
        "- For each shortlisted card, inspect the actual installed image AND several archive candidates at enough resolution to identify the claimed part.",
        "- Assign Recognize → Look closer → Confirm clue only when the picture really shows that level of structure. Use exact part names, not one generic caption across multiple views.",
        "- Flag source-taxonomy uncertainty, cultivar mismatches, licensing issues, and incorrect arrow coordinates; do not mark any as verified by filename, taxon string, or a hash.",
        "- Preserve existing noncommercial/private source rights, photos, scientific HOLDs and five scheduled automations.",
        "- The full JSON lists every audited card, exact missing references, duplicate pairs, potential near-duplicates, claimed species and role cues; never treat automated heuristic flags as proven mistakes.",
        "",
    ]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / (PREFIX + ".json")).write_text(json.dumps(out_json, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (OUT / (PREFIX + ".md")).write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"report": PREFIX, "summary": summary, "top_12": dedup[:12] and [x["id"] for x in dedup[:12]]}, indent=2))
if __name__ == "__main__": run()
