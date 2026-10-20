#!/usr/bin/env python3
"""Read-only canonical source scan: exact species without website-eligible photos.

Uses the same rights() function as the existing noncommercial GitHub Pages builder.
Does NOT relicense, copy, edit or install source photographs or publish the website.
This is an eligibility PRE-SCREEN based on recorded rights, not external license proof.
Refresh after verified 2026-10-20 CC BY recovery of Ludwigia and Symphyotrichum.
Refresh after verified 2026-10-20 Tinantia noncommercial CC BY-NC and new Arbutus/Dalea exact-source CC BY first photos.
Refresh after individually licensed CC BY first public images installed for Asclepias texana, Asclepias viridis, and Senna roemeriana; retain existing science and private-research images untouched.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import re

from PIL import Image

from build_public_pages_snapshot import rights

ROOT = Path(__file__).resolve().parent.parent
TAXA = ROOT / "content" / "taxa"
OUT = ROOT / "reports"
ACCEPTABLE = {".jpg", ".jpeg", ".png", ".webp"}


def photo_review(folder: Path, image: object) -> dict:
    result = {
        "file": None, "creator": None, "license": None,
        "source_page": None, "status": "HELD",
        "reason": None,
    }
    if not isinstance(image, dict):
        result["reason"] = "invalid image record"
        return result
    result["file"] = image.get("file")
    result["creator"] = image.get("creator") or image.get("photographer")
    result["license"] = image.get("license")
    result["source_page"] = image.get("source_page") or image.get("photo_source_url")
    path_field = image.get("file")
    if not isinstance(path_field, str) or not path_field.strip():
        result["reason"] = "image has no local file path"
        return result
    if re.match(r"(?i)^https?://", path_field):
        result["reason"] = "external URL is not a verified local photograph"
        return result
    target = (folder / path_field).resolve()
    if not target.is_relative_to(ROOT) or not target.is_file():
        result["reason"] = "missing or unsafe local image file"
        return result
    result["physical_bytes"] = target.stat().st_size
    if target.suffix.lower() not in ACCEPTABLE:
        result["reason"] = "unsupported public photo format"
        return result
    try:
        with Image.open(target) as im:
            result["dimensions"] = list(im.size)
            im.verify()
    except Exception as exc:
        result["reason"] = "unreadable local image: " + str(exc)[:120]
        return result
    result["local_file_verified"] = True
    okay, reason = rights(image, noncommercial=True)
    if not okay:
        result["reason"] = reason
        return result
    result["status"] = "ELIGIBLE_FOR_NONCOMMERCIAL_PAGES_BUILD"
    result["reason"] = reason
    return result


def main() -> None:
    manifest = json.loads((ROOT / "data" / "manifest.json").read_text())
    canonical_paths = {
        str(entry["path"]) for entry in manifest["species"]
        if isinstance(entry, dict) and isinstance(entry.get("path"), str)
    }
    paths = sorted(TAXA.rglob("species.json"))
    cards = []
    records = Counter()
    reasons = Counter()
    local_dist = Counter()
    public_dist = Counter()
    photo_eligible_count = 0
    for sp in paths:
        rel = str(sp.relative_to(ROOT))
        doc = json.loads(sp.read_text(encoding="utf-8"))
        images = doc.get("images") or []
        reviews = [photo_review(sp.parent, image) for image in images]
        good = sum(x["status"] == "ELIGIBLE_FOR_NONCOMMERCIAL_PAGES_BUILD" for x in reviews)
        physical = sum(bool(x.get("local_file_verified")) for x in reviews)
        photo_eligible_count += good
        records["canonical_image_records"] += len(images)
        records["physical_local_records"] += physical
        records["public_eligible_records"] += good
        local_dist["0" if physical == 0 else "1" if physical == 1 else "2" if physical == 2 else "3+"] += 1
        public_dist["0" if good == 0 else "1" if good == 1 else "2" if good == 2 else "3+"] += 1
        for x in reviews:
            if x["status"] != "ELIGIBLE_FOR_NONCOMMERCIAL_PAGES_BUILD":
                reasons[x["reason"]] += 1
        if good:
            continue
        if not images:
            bucket = "NO_IMAGE_RECORD"
        elif physical == 0:
            bucket = "MISSING_VALID_PHYSICAL_IMAGE"
        elif all(x.get("local_file_verified") and x["reason"] for x in reviews):
            bucket = "PUBLIC_LICENSE_OR_METADATA_HOLD"
        else:
            bucket = "MIXED_FILE_AND_RIGHTS_HOLD"
        cards.append({
            "id": doc.get("id") or sp.stem,
            "scientific_name": doc.get("scientific_name") or doc.get("name") or doc.get("id"),
            "family": doc.get("family"),
            "genus": doc.get("genus"),
            "path": rel,
            "in_manifest": rel in canonical_paths,
            "bucket": bucket,
            "canonical_image_records": len(images),
            "physically_verified_local_images": physical,
            "public_eligible_images": good,
            "photo_review": reviews,
        })
    cards.sort(key=lambda c: ({"PUBLIC_LICENSE_OR_METADATA_HOLD":0, "MIXED_FILE_AND_RIGHTS_HOLD":1, "MISSING_VALID_PHYSICAL_IMAGE":2,"NO_IMAGE_RECORD":3}[c["bucket"]], c["scientific_name"] or ""))
    result = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": "canonical main checked out by GitHub Actions",
        "rights_rule": "same build_public_pages_snapshot.rights() for noncommercial site, plus Pillow local-byte verification",
        "photo_metadata_not_independent_external_legal_verification": True,
        "canonical_species": len(paths),
        "manifest_species": len(canonical_paths),
        "manifest_paths_missing_canonical_species_json": sorted(canonical_paths - {str(p.relative_to(ROOT)) for p in paths}),
        "counts": {
            **dict(records),
            "cards_without_public_photos": len(cards),
            "zero_local_image_cards": local_dist["0"],
        },
        "physical_image_card_distribution": dict(local_dist),
        "public_eligible_image_card_distribution": dict(public_dist),
        "rejected_photo_reasons": dict(reasons.most_common()),
        "cards_without_public_photos": cards,
    }
    OUT.mkdir(exist_ok=True)
    (OUT / "public-photo-gaps-latest.json").write_text(json.dumps(result, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    lines = [
        "# Public learner photo gaps — source eligibility scan",
        "",
        f"Generated (UTC): {result['generated_at_utc']}",
        "",
        f"- Canonical species: **{len(paths)}**",
        f"- Public-photo-free species: **{len(cards)}**",
        f"- Physically photo-free species: **{local_dist['0']}**",
        f"- Recorded site-eligible photographs: **{photo_eligible_count}**",
        "",
        "This is a source-record/physical-byte audit using the current noncommercial Pages policy, NOT proof that a photo's upstream license or botanical ID is correct. No source content was changed.",
        "",
        "| Species | Triage | Local images | Exact recorded blockers |",
        "|---|---|---:|---|",
    ]
    for card in cards:
        why = "; ".join(sorted({str(x["reason"]) for x in card["photo_review"] if x["reason"]})) or "No image records"
        why = why.replace("|", "/").replace("\n", " ")
        lines.append(f"| *{card['scientific_name']}* | `{card['bucket']}` | {card['physically_verified_local_images']} | {why} |")
    lines += [
        "",
        "## Next safe action",
        "Recover existing physical, exact-taxon photos with independently documented web-reuse rights and complete attribution before adding replacement images. Keep unknown/private-only/all-rights-reserved images excluded and preserve original source metadata. Diagnostic Photo Fast-Fill owns gallery changes; this report makes no changes to images or website publication.",
    ]
    (OUT / "public-photo-gaps-latest.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    print(json.dumps({"canonical_species":len(paths),"no_public_photo":len(cards),"physical_zero":local_dist["0"],"buckets":dict(Counter(c["bucket"] for c in cards))},indent=2))


if __name__ == "__main__":
    main()
