#!/usr/bin/env python3
"""Fail-closed first-pass media-rights gate for PUBLIC static-site deployment.

This script does not modify canonical source JSON, metadata, or images. The source repository may be PUBLIC; the rights-filtered Pages build cannot make source-committed restricted originals private.
A PASS is a necessary screening result, not a legal opinion or full content audit.
Run only on a public deployment candidate AFTER the normal build.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

MEDIA_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".tif", ".tiff"}
OWNER_NAMES = {"calvin king", "glass root garden", "calvin king / glass root garden"}
JOEY_CREDITED_PERMISSION = "JOEY_CREDITED_PUBLIC_LEARNER_20261021"
JOEY_CREATORS = {"joey santore", "joey santore / crime pays but botany doesn't"}
PUBLIC_CC = re.compile(r"\bcc\s*[- ]?by(?:[- ]?sa)?\b", re.I)
CC_ZERO = re.compile(r"\bcc\s*[- ]?0\b", re.I)
PUBLIC_DOMAIN = re.compile(r"public domain|\bpd[- ]?mark\b", re.I)
UNPUBLISHABLE = re.compile(r"private.?study|private.?use|all rights reserved|no public|not cleared", re.I)
NONCOMMERCIAL = re.compile(r"\bnc\b|noncommercial", re.I)
NO_DERIVATIVES = re.compile(r"\bnd\b|no[- ]?derivatives", re.I)


def clean(text):
    return str(text or "").strip().lower()


def photo_rights(record, noncommercial=False):
    creator = clean(record.get("creator") or record.get("photographer"))
    lic = clean(record.get("license"))
    source = record.get("source_page") or record.get("photo_source_url") or record.get("source_url")
    public_reuse = clean(record.get("public_reuse"))
    photo_id = record.get("source_photo_id") or record.get("photo_id") or record.get("inat_photo_id")
    explicitly_private = public_reuse in {"no", "false", "private", "private_study_only"}
    is_owner = creator in OWNER_NAMES and bool(source) and bool(photo_id)
    if is_owner:  # Separately recorded site-specific owner authorization, not a Creative Commons license.
        return None
    # The publisher inserts this marker only for explicitly enumerated frames.
    # Validate it again here, including creator, video source and record ID.
    if clean(record.get("site_specific_public_permission")) == JOEY_CREDITED_PERMISSION.lower():
        # YouTube IDs are case-sensitive; do not lowercase archived frame IDs.
        frame_id = str(record.get("source_record_id") or "").strip()
        if (
            noncommercial
            and creator in JOEY_CREATORS
            and str(source or "").startswith("https://www.youtube.com/watch?v=")
            and (
                bool(re.fullmatch(
                    r"(?:jvid-)?" + re.escape(str(source).split("?v=", 1)[1].split("&", 1)[0]) + r"-[0-9]+",
                    frame_id,
                ))
                or (
                    not frame_id
                    and str(source) == "https://www.youtube.com/watch?v=Y7A530PjEbU"
                    and record.get("file") in {
                        "images/chrysactinia-mexicana_habit-source-label_03-40.jpg",
                        "images/chrysactinia-mexicana_flower-head-leaves_04-00.jpg",
                    }
                )
            )
        ):
            return None
        return "invalid or out-of-scope Joey creator-permission marker"
    if explicitly_private:
        return "public_reuse is explicitly denied/limited and no verified owner exception"
    if UNPUBLISHABLE.search(lic):
        return "private-use/all-rights-reserved image license; public display not permitted"
    if NO_DERIVATIVES.search(lic):
        return "no-derivatives image requires separate adaptation review"
    if not source:
        return "missing individual image source page / rights evidence"
    if CC_ZERO.search(lic) or PUBLIC_DOMAIN.search(lic):
        return None
    if PUBLIC_CC.search(lic) and creator:
        # The exporter and the rights preflight must agree: a documented
        # CC BY-NC photo is eligible ONLY for the user-confirmed, standalone,
        # strictly noncommercial educational GitHub Pages display.
        if NONCOMMERCIAL.search(lic) and not noncommercial:
            return "CC BY-NC needs confirmed noncommercial website use or permission"
        return None
    return "missing or unsupported public-web license / attribution"


def inspect(site: Path, noncommercial=False):
    reasons = []
    referenced = set()
    content = site / "content" / "taxa"
    species_files = sorted(content.rglob("species.json"))
    for sp in species_files:
        try:
            doc = json.loads(sp.read_text(encoding="utf-8"))
        except (ValueError, OSError) as exc:
            reasons.append((str(sp.relative_to(site)), f"invalid species JSON: {exc}"))
            continue
        for ix, img in enumerate(doc.get("images", [])):
            if not isinstance(img, dict):
                reasons.append((str(sp.relative_to(site)), f"images[{ix}] lacks source record"))
                continue
            filename = img.get("file")
            if not isinstance(filename, str) or not filename.strip():
                reasons.append((str(sp.relative_to(site)), f"images[{ix}] missing file path"))
                continue
            target = sp.parent / filename
            referenced.add(target.resolve())
            if not target.is_file():
                reasons.append((str(sp.relative_to(site)), f"gallery image missing: {filename}"))
            problem = photo_rights(img, noncommercial=noncommercial)
            if problem:
                reasons.append((str(sp.relative_to(site)), f"{filename}: {problem}"))
    for file in content.rglob("*"):
        if file.is_file() and file.suffix.lower() in MEDIA_EXTS and file.resolve() not in referenced:
            # A public static build exposes these bytes even if no card currently displays them.
            reasons.append((str(file.relative_to(site)), "unreferenced public media file; rights not matched to a species gallery entry"))
    # Current Photo Lab includes archived, unapproved candidate photographs. Never release it as-is.
    if (site / "photo-review.html").exists():
        reasons.append(("photo-review.html", "private Photo Lab candidate-review page is present in public package"))
    return len(species_files), len(referenced), reasons


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--site", default="dist")
    p.add_argument("--noncommercial", action="store_true", help="Confirm publication is a stand-alone strictly noncommercial educational site")
    p.add_argument("--limit", type=int, default=15)
    args = p.parse_args()
    site = Path(args.site)
    if not (site / "index.html").is_file():
        raise SystemExit("Public-rights audit FAILED: missing staged site index.html")
    cards, images, issues = inspect(site, noncommercial=args.noncommercial)
    print(f"Checked {cards} species records, {images} referenced gallery paths.")
    print(f"Public image/candidate-page rights holds: {len(issues)}.")
    for path, reason in issues[:args.limit]:
        print(f"HOLD {path}: {reason}")
    if len(issues) > args.limit:
        print(f"... and {len(issues)-args.limit} more. Audit the full private source before public release.")
    if issues:
        raise SystemExit("Public website release BLOCKED pending exact photo rights audit/exclusion.")
    print("Rights preflight passed. Still verify external assets, full attribution and website use manually.")


if __name__ == "__main__":
    main()
