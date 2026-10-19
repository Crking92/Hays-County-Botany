#!/usr/bin/env python3
"""Optimize website-only JPEG copies, never canonical GitHub originals.

This tool changes files only under an already-built dist/ directory.
The learner's species.json, image sources, author credits and original media
in content/ are not modified. Run in CI before public site deployment.
"""
from __future__ import annotations

import argparse
import io
import json
import os
from pathlib import Path

from PIL import Image, ImageOps


def totals(root: Path) -> tuple[int, int]:
    files = [p for p in root.rglob("*") if p.is_file()]
    return len(files), sum(p.stat().st_size for p in files)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="dist", help="Already staged public site, not source")
    parser.add_argument("--threshold-kb", type=int, default=750)
    parser.add_argument("--max-edge", type=int, default=2800)
    parser.add_argument("--quality", type=int, default=86)
    parser.add_argument("--report", default="site-image-savings.json")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    if root.name != "dist" or not (root / "index.html").is_file():
        raise SystemExit("Refusing to modify anything other than a built dist/ website")
    if args.threshold_kb < 100 or not (70 <= args.quality <= 95):
        raise SystemExit("Threshold or quality outside safe pilot limits")
    if args.max_edge < 1800:
        raise SystemExit("Keep enough edge pixels for plant diagnostic detail")

    all_count, all_bytes_before = totals(root)
    photos = sorted(
        p for dirname in ("content", "assets")
        for p in (root / dirname).rglob("*")
        if p.is_file() and p.suffix.lower() in (".jpg", ".jpeg")
    )
    before = sum(p.stat().st_size for p in photos)
    changed, selected, errors = [], 0, []
    # JPEG only in this conservative first pass; skip PNG/transparency and WebP.
    for path in photos:
        original_size = path.stat().st_size
        try:
            with Image.open(path) as original:
                if original.format != "JPEG":
                    continue
                had_exif = bool(original.info.get("exif") or original.getexif())
                if original_size < args.threshold_kb * 1024 and not had_exif:
                    continue
                selected += 1
                image = ImageOps.exif_transpose(original)
                size_before = image.size
                if max(image.size) > args.max_edge:
                    image.thumbnail((args.max_edge, args.max_edge), Image.Resampling.LANCZOS)
                if image.mode != "RGB":
                    image = image.convert("RGB")
                result = io.BytesIO()
                # Explicitly omit EXIF/GPS and comments from the published copy.
                image.save(
                    result, format="JPEG", quality=args.quality,
                    subsampling=0, progressive=True, optimize=True
                )
                blob = result.getvalue()
                # Avoid lowering quality for trivial savings, except when metadata
                # needs to be removed for privacy.
                if not had_exif and len(blob) >= original_size * 0.98:
                    continue
                tmp = path.with_name(path.name + ".optimize-tmp")
                try:
                    tmp.write_bytes(blob)
                    os.replace(tmp, path)
                finally:
                    tmp.unlink(missing_ok=True)
                changed.append({
                    "path": str(path.relative_to(root)),
                    "before_bytes": original_size,
                    "after_bytes": len(blob),
                    "saved_bytes": original_size - len(blob),
                    "dimensions_before": list(size_before),
                    "dimensions_after": list(image.size),
                    "had_exif": had_exif,
                    "quality": args.quality,
                })
        except Exception as exc:
            errors.append({"path": str(path.relative_to(root)), "error": type(exc).__name__})
    after = sum(p.stat().st_size for p in photos)
    all_count_after, all_bytes_after = totals(root)
    if all_count != all_count_after:
        raise SystemExit("Unexpected website file-count change")
    report = {
        "mode": "WEBSITE_DIST_COPIES_ONLY_NONDESTRUCTIVE",
        "originals_changed": False,
        "input_file_count": all_count,
        "jpeg_count": len(photos),
        "jpeg_total_bytes_before": before,
        "jpeg_total_bytes_after": after,
        "site_bytes_before": all_bytes_before,
        "site_bytes_after": all_bytes_after,
        "saved_bytes": all_bytes_before - all_bytes_after,
        "saved_percent": round(100 * (all_bytes_before - all_bytes_after) / max(all_bytes_before, 1), 2),
        "large_or_exif_photos_examined": selected,
        "photos_optimized": len(changed),
        "settings": {
            "threshold_kb": args.threshold_kb,
            "max_edge": args.max_edge,
            "jpeg_quality": args.quality,
            "preserve_original_github_media": True,
            "publishing_automatic": False
        },
        "biggest_savings": sorted(changed, key=lambda x: x["saved_bytes"], reverse=True)[:25],
        "errors": errors
    }
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k not in ("biggest_savings",)}, indent=2))
    if errors:
        raise SystemExit(f"Encountered {len(errors)} JPEG processing errors; see report")


if __name__ == "__main__":
    main()
