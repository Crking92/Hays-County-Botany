#!/usr/bin/env python3
"""Safely reduce JPEG storage in a BUILT public website, never in canonical source.

All work stays inside the supplied dist/ directory. This preserves full-quality
plant references and independently licensed originals in the private GitHub repo.
The saved image has no source EXIF/GPS; original photo credit in JSON is unchanged.
"""
from __future__ import annotations

import argparse
import io
import json
from pathlib import Path

from PIL import Image, ImageOps

MIB = 1024 * 1024


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-dir", type=Path, default=Path("dist"))
    parser.add_argument("--report", type=Path, default=Path("reports/site-photo-budget-local.json"))
    parser.add_argument("--minimum-kb", type=int, default=750)
    parser.add_argument("--max-long-edge", type=int, default=2400)
    parser.add_argument("--quality", type=int, default=85)
    parser.add_argument("--warn-mib", type=int, default=750)
    parser.add_argument("--stop-mib", type=int, default=920)
    args = parser.parse_args()

    site = args.site_dir.resolve()
    if not (site / "index.html").is_file() or not (site / "photo-review.html").is_file():
        parser.error("Expected a staged site with index.html and photo-review.html")
    if not (site / "content").is_dir():
        parser.error("Expected a staged site with a content directory")
    if not 65 <= args.quality <= 92 or args.max_long_edge < 1200:
        parser.error("Refusing extreme compression unsuitable for botanical details")
    if args.stop_mib <= args.warn_mib:
        parser.error("Hard stop must exceed warning threshold")

    candidates = sorted(
        p for p in (site / "content").rglob("*")
        if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg"}
    )
    before_site = sum(p.stat().st_size for p in site.rglob("*") if p.is_file())
    original_image_bytes = sum(p.stat().st_size for p in candidates)
    examined = 0
    optimized = 0
    with_exif = 0
    skipped_not_smaller = 0
    rejected = []
    larger_samples = []
    total_saved = 0
    minimum_bytes = args.minimum_kb * 1024

    for photo in candidates:
        start = photo.stat().st_size
        try:
            with Image.open(photo) as im:
                contains_exif = bool(im.getexif()) or bool(im.info.get("exif"))
                if start < minimum_bytes and not contains_exif:
                    continue
                examined += 1
                if contains_exif:
                    with_exif += 1
                # JPEG output is RGB. Exif transpose corrects source orientation
                # before stripping location/device metadata.
                image = ImageOps.exif_transpose(im)
                if image.mode != "RGB":
                    image = image.convert("RGB")
                longest = max(image.size)
                if longest > args.max_long_edge:
                    scale = args.max_long_edge / longest
                    target = (max(1, round(image.width * scale)), max(1, round(image.height * scale)))
                    image = image.resize(target, Image.Resampling.LANCZOS)
                output = io.BytesIO()
                # Preserve color management when present, but never GPS/EXIF.
                save_kwargs = {"format": "JPEG", "quality": args.quality,
                               "optimize": True, "progressive": True, "subsampling": 0}
                icc = im.info.get("icc_profile")
                if icc:
                    save_kwargs["icc_profile"] = icc
                image.save(output, **save_kwargs)
                candidate_bytes = output.getvalue()
                with Image.open(io.BytesIO(candidate_bytes)) as check:
                    check.verify()
            # Keep an original that is already more compact, unless it had
            # EXIF/device/location metadata that must be discarded publicly.
            if len(candidate_bytes) >= start and not contains_exif:
                skipped_not_smaller += 1
                continue
            photo.write_bytes(candidate_bytes)
            optimized += 1
            total_saved += start - len(candidate_bytes)
            if start >= 2 * MIB:
                larger_samples.append({
                    "file": str(photo.relative_to(site)),
                    "source_mib": round(start / MIB, 2),
                    "public_mib": round(len(candidate_bytes) / MIB, 2)
                })
        except Exception as exc:
            rejected.append({"file": str(photo.relative_to(site)), "error_type": type(exc).__name__})
            # An unreadable published JPEG is a problem; do not silently
            # publish it just because every other image passed.
            continue

    after_site = sum(p.stat().st_size for p in site.rglob("*") if p.is_file())
    report = {
        "scope": "STAGED PUBLIC SITE ONLY; canonical photos unchanged",
        "site_files": sum(1 for p in site.rglob("*") if p.is_file()),
        "jpeg_files": len(candidates),
        "jpeg_files_examined": examined,
        "jpeg_files_reencoded": optimized,
        "jpeg_files_with_exif_stripped": with_exif,
        "jpeg_files_kept_as_smaller_original": skipped_not_smaller,
        "input_image_mib": round(original_image_bytes / MIB, 2),
        "site_before_mib": round(before_site / MIB, 2),
        "site_after_mib": round(after_site / MIB, 2),
        "savings_mib": round(total_saved / MIB, 2),
        "website_warning_limit_mib": args.warn_mib,
        "website_stop_limit_mib": args.stop_mib,
        "warning": after_site >= args.warn_mib * MIB,
        "rejected_files": rejected[:40],
        "large_image_examples": larger_samples[:20]
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if rejected:
        raise SystemExit("Some JPEG files could not be processed; review before publishing")
    if after_site >= args.stop_mib * MIB:
        raise SystemExit("Published site reached safety stop; reduce image sizes or choose another host")


if __name__ == "__main__":
    main()
