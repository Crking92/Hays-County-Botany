#!/usr/bin/env python3
"""Read-only photo metadata quality and diagnostic coverage audit. Python 3.10+."""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
RULES = {
    "habit": r"\b(habit|whole[\s_-]?plant|entire[\s_-]?plant|growth[\s_-]?form)\b",
    "leaf": r"\b(leaf|leaves|foliage|blade|petiole|venation|conduplicate|leaflet|needle)\b",
    "flower": r"\b(flower|floret|corolla|ray florets|disk florets|capitulum|inflorescen|umbel|spikelet|panicle)\b",
    "fruit": r"\b(fruit|seed|pod|follicle|berry|capsule|acorn|cypsela|achene|samara)\b",
    "stem": r"\b(stem|bud|twig|node|bark|insertion|attachment)\b",
    "phyllary": r"\b(phyllar|involucre|involucral|underside[\s_-]?head)\b",
    "ligule": r"\b(ligule|collar|sheath|auricle)\b",
    "corona": r"\b(corona|hood|horn|gynostegium|pollinaria|pollinium|pollinia)\b",
}
LABELS = {
    "habit": "whole-plant habit", "leaf": "mature leaf, venation or attachment",
    "flower": "flower or inflorescence", "fruit": "fruit or seed",
    "stem": "stem, node or buds", "phyllary": "involucre / phyllary macro",
    "ligule": "grass collar and ligule", "corona": "milkweed corona / hood macro",
}
GENERIC = re.compile(r"^(curated taxon reference|same.observation field view|photo \d+|field view \d+|reference image)", re.I)
HIGH_VALUE = re.compile(r"diagnostic|verified (?:vegetative|floral|macro|leaf|fruit)|phyllar|venation|leaf insertion|attachment|ligule|corona", re.I)

def load(path):
    obj = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("JSON object required: " + str(path))
    return obj

def required_roles(sp):
    family = str(sp.get("family", "")).casefold()
    genus = str(sp.get("genus", "")).casefold()
    if family == "poaceae": return ["habit", "leaf", "flower", "ligule"]
    if genus in ("asclepias", "funastrum", "gonolobus", "matelea"): return ["habit", "leaf", "flower", "corona"]
    if family == "asteraceae": return ["habit", "leaf", "flower", "phyllary"]
    if genus == "quercus": return ["habit", "leaf", "fruit", "stem"]
    return ["habit", "leaf", "flower", "fruit"]

def image_roles(img):
    role = str(img.get("role") or img.get("view") or img.get("image_role") or "").strip()
    if not role or GENERIC.match(role): return []
    return [key for key, pattern in RULES.items() if re.search(pattern, role, re.I)]

def score_image(img):
    role = " ".join(str(img.get(key) or "") for key in ("role", "view", "image_role"))
    reviewed = bool(img.get("visual_role_reviewed") or img.get("diagnostic_role_verified") or img.get("annotation_verified"))
    if reviewed and re.search(r"diagnostic|leaf|venation|petiole|phyllar|involucre|bud|acorn|ligule|fruit|flower|corona|pollinia|macro|structure", role, re.I): return 120
    if re.search("diagnostic", role, re.I): return 95
    if re.search(r"verified .*(leaf|flower|macro|fruit|vegetative|phyllar)", role, re.I): return 78
    if not GENERIC.match(role) and re.search(r"leaf|petiole|venation|phyllar|involucre|corona|gynostegium|ligule|acorn|bud|bark|pappus|fruit|seed|macro|detail", role, re.I): return 53
    if re.search(r"whole plant|habit|field view", role, re.I): return 16
    return 0

def reuse_state(img):
    rule = str(img.get("public_reuse") or "").strip().lower()
    license = str(img.get("license") or "").lower()
    if re.search(r"\b(no|private|restricted|review|pending)\b", rule): return "review_or_private"
    if "by-nc" in license or "noncommercial" in license: return "noncommercial"
    if rule.startswith(("yes", "allowed", "verified")) and license: return "conditional_licensed"
    return "unspecified"

def existing_claims(claims, taxon_id, now):
    out = []
    for c in claims.get("claims", []):
        if not isinstance(c, dict) or c.get("status") != "active": continue
        try:
            if c.get("expires_at") and datetime.fromisoformat(str(c["expires_at"]).replace("Z", "+00:00")).astimezone(timezone.utc) < now: continue
        except (ValueError, TypeError): pass
        if not re.search("photo|image|media", str(c.get("lane") or ""), re.I): continue
        if taxon_id in (c.get("taxa") or []) or taxon_id in str(c.get("scope_key") or ""):
            out.append(str(c.get("claim_id") or "active-claim"))
    return out

def audit(entry, sp, root, claims, now):
    base = root / Path(entry["path"]).parent
    images = [im for im in (sp.get("images") or []) if isinstance(im, dict) and im.get("file")]
    covered, counts, views = set(), Counter(), []
    for i, img in enumerate(images):
        file = str(img["file"])
        external = file.startswith(("https://", "http://")) or bool(img.get("external_reference"))
        counts["external" if external else "local_reference"] += 1
        if not external:
            resolved = (base / file).resolve()
            if not resolved.is_relative_to(root) or not resolved.is_file():
                counts["broken_local_reference"] += 1
        if not (img.get("creator") or img.get("credit")): counts["no_credit"] += 1
        if not img.get("license"): counts["no_license"] += 1
        if not img.get("source_page"): counts["no_source"] += 1
        reuse = reuse_state(img)
        counts["reuse_" + reuse] += 1
        role_list = image_roles(img)
        covered.update(role_list)
        views.append({
            "canonical_index": i, "role": str(img.get("role") or ""),
            "source_type": "external_reference" if external else "local_reference",
            "role_categories": role_list, "role_metadata_reviewed": bool(img.get("visual_role_reviewed")),
            "license": str(img.get("license") or ""), "reuse_state": reuse,
            "credit_present": bool(img.get("creator") or img.get("credit")),
            "photo_priority": score_image(img),
            "arrow_status": "pending_image_coordinate_review" if not img.get("annotation_verified") else "annotation_verified_field_present",
        })
    missing = [role for role in required_roles(sp) if role not in covered]
    active = existing_claims(claims, str(entry["id"]), now)
    best = max((v["photo_priority"] for v in views), default=0)
    score = ((120 if not images else 0) + (85 if images and best < 53 else 0)
             + 16 * len(missing) + 50 * counts["broken_local_reference"]
             + 10 * (counts["no_credit"] + counts["no_license"] + counts["no_source"])
             + (12 if images and not any(v["role_metadata_reviewed"] for v in views) else 0))
    if not images: action = "Locate one exact-species, appropriately attributed displayable photo."
    elif counts["broken_local_reference"]: action = "Repair broken local image reference without deleting its source history."
    elif missing: action = "Verify or photograph: " + ", ".join(LABELS[k] for k in missing[:3])
    elif best < 53: action = "Review an anatomical view and assign a source-backed photo role."
    else: action = "Inspect exact source image before assigning any annotation coordinates."
    return {
        "id": str(entry["id"]), "path": str(entry["path"]),
        "scientific_name": str(sp.get("scientific_name") or sp.get("accepted_name") or entry["id"]),
        "family": str(sp.get("family") or ""), "genus": str(sp.get("genus") or ""),
        "photo_total": len(images), "local_references": counts["local_reference"],
        "external_references": counts["external"], "broken_local_references": counts["broken_local_reference"],
        "missing_credit": counts["no_credit"], "missing_license": counts["no_license"],
        "missing_source_page": counts["no_source"],
        "photos_with_noncommercial_or_review_reuse": counts["reuse_review_or_private"] + counts["reuse_noncommercial"],
        "role_metadata_coverage": sorted(covered), "missing_role_metadata": missing,
        "best_canonical_image_index": max(range(len(views)), key=lambda j: views[j]["photo_priority"]) if views else None,
        "best_image_score": best, "photo_views": views, "priority_score": score,
        "active_photo_claims": active, "suggested_action": action,
        "audit_limit": "Metadata screening only: does not verify photo anatomy, reachability of external URLs, rights clearance or arrows.",
    }

def write_reports(root, out, size, offset):
    manifest = load(root / "data/manifest.json")
    claims_file = root / "workflow/work-claims.json"
    claims = load(claims_file) if claims_file.is_file() else {"claims": []}
    rows, errors, seen = [], [], set()
    now = datetime.now(timezone.utc)
    for entry in manifest.get("species", []):
        if not isinstance(entry, dict) or not entry.get("id") or not entry.get("path"):
            errors.append("manifest row with no path/id"); continue
        if entry["id"] in seen: errors.append("duplicate taxon " + str(entry["id"])); continue
        seen.add(entry["id"])
        path = (root / str(entry["path"])).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            errors.append("missing species JSON " + str(entry["path"])); continue
        try: rows.append(audit(entry, load(path), root, claims, now))
        except (ValueError, OSError) as exc: errors.append(str(entry["path"]) + ": " + str(exc))
    if errors: raise RuntimeError("Refusing incomplete inventory: " + "; ".join(errors[:20]))
    available = sorted((row for row in rows if not row["active_photo_claims"]),
                       key=lambda row: (-row["priority_score"], row["id"]))
    chosen = available[offset:offset+size]
    stamp = now.isoformat(timespec="seconds")
    inventory = {
        "generated_at": stamp, "species_audited": len(rows),
        "with_any_gallery_photo": sum(bool(row["photo_total"]) for row in rows),
        "with_no_gallery_photos": sum(not row["photo_total"] for row in rows),
        "missing_one_or_more_role_labels": sum(bool(row["missing_role_metadata"]) for row in rows),
        "blocked_by_current_photo_claim": len(rows)-len(available), "rows": rows,
    }
    batch = {"generated_at": stamp, "offset": offset, "batch_size": size,
             "eligible_total": len(available), "selected": chosen}
    md = [
        "# Photo-quality queue — visual learner",
        "", "Generated: " + stamp, "",
        f"**{len(rows)} taxa audited** · {inventory['with_no_gallery_photos']} without gallery entries · {inventory['missing_one_or_more_role_labels']} lacking at least one diagnostic role in metadata.",
        "",
        "This is a metadata-only screen. No source image was visually verified, downloaded, relicensed or annotated. Missing labels are NOT proof that the structure is absent. Current photo-installation claims are excluded from actionable batches.",
        "", f"## Batch: {len(chosen)} targets (offset {offset})", "",
        "| Plant | Local / external photos | Unverified roles | Priority | Next action |",
        "|---|---:|---|---:|---|",
    ]
    for row in chosen:
        missing = ", ".join(LABELS[key] for key in row["missing_role_metadata"]) or "none flagged"
        md.append(f"| *{row['scientific_name']}* | {row['local_references']} / {row['external_references']} | {missing} | {row['priority_score']} | {row['suggested_action']} |")
    md += ["", "## Rules", "",
           "- Existing species and image data are never modified by this utility.",
           "- CC BY-NC, restricted and review-only images retain their existing reuse conditions.",
           "- Proposed anatomical arrows stay pending until the exact image and pixel target are confirmed.",
           "- Queue rows become candidates for existing photo research and installer lanes; claimed taxa are held out.",
           "- Full inventory.json includes all installed species and canonical image indices.",
           ""]
    out.mkdir(parents=True, exist_ok=True)
    for name, obj in (("inventory.json", inventory), ("queue.json", batch)):
        (out / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    (out / "queue.md").write_text("\n".join(md), encoding="utf-8")
    print(f"Photo audit OK: {len(rows)} taxa; {inventory['with_no_gallery_photos']} zero-gallery taxa; {len(chosen)} unclaimed batch targets; output {out}")
    return inventory

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--out-dir", type=Path, default=Path("photo-quality-output"))
    p.add_argument("--batch-size", type=int, default=25)
    p.add_argument("--offset", type=int, default=0)
    a = p.parse_args()
    if not 1 <= a.batch_size <= 500 or a.offset < 0: p.error("batch-size 1..500, offset >= 0")
    write_reports(a.root.resolve(), a.out_dir, a.batch_size, a.offset)
if __name__ == "__main__": main()
