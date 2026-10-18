#!/usr/bin/env python3
"""Read-only botanical photo QA for staged public-site JPEG copies.

Original images are in the private source tree. Dist images are compressed
website copies. This never writes to content/, species.json, or dist/.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageOps, ImageStat

DIAGNOSTIC_WORDS = (
    "asclepias", "euphorbia", "croton", "ipomoea", "quercus",
    "bouteloua", "aristida", "solidago", "coreopsis", "cirsium",
    "ludwigia", "sorghum", "cyperus", "matelea", "helianthus"
)


def make_thumb(image, width=500, height=320):
    return ImageOps.contain(image.convert("RGB"), (width, height), Image.Resampling.LANCZOS)


def center_crop(image, zoom=2, target=(480, 300)):
    im = image.convert("RGB")
    w, h = im.size
    crop_w, crop_h = max(1, int(w / zoom)), max(1, int(h / zoom))
    x, y = (w - crop_w) // 2, (h - crop_h) // 2
    im = im.crop((x, y, x + crop_w, y + crop_h))
    return ImageOps.contain(im, target, Image.Resampling.LANCZOS)


def qa(source: Path, staged: Path):
    with Image.open(source) as raw, Image.open(staged) as final:
        raw.verify()
        final.verify()
    with Image.open(source) as raw, Image.open(staged) as final:
        src = ImageOps.exif_transpose(raw).convert("RGB")
        out = final.convert("RGB")
        # Compare images at the published resolution, avoiding false distortion
        # flags caused solely by reducing display pixel dimensions.
        scaled = src.resize(out.size, Image.Resampling.LANCZOS)
        delta = ImageChops.difference(scaled, out)
        avg = ImageStat.Stat(delta).mean
        mae = round(sum(avg) / 3, 2)
        return {
            "source_dims": list(src.size),
            "published_dims": list(out.size),
            "source_bytes": source.stat().st_size,
            "published_bytes": staged.stat().st_size,
            "pixel_mean_absolute_error": mae,
            "downscaled": src.size != out.size,
            "gps_exif_in_published": bool(final.getexif().get_ifd(0x8825)),
        }


def build_sheet(entries, source_root, dist_root, output_path):
    if not entries:
        return
    # Four columns: full original, full deployed, detail original, detail
    # deployed. Images are embedded only in the private GitHub Action artifact.
    width = 2040
    cell_w = 500
    height_per = 350
    canvas = Image.new("RGB", (width, height_per * len(entries)), "white")
    draw = ImageDraw.Draw(canvas)
    for ix, entry in enumerate(entries):
        path = entry["path"]
        with Image.open(source_root / path) as base, Image.open(dist_root / path) as deployed:
            base = ImageOps.exif_transpose(base).convert("RGB")
            deployed = deployed.convert("RGB")
            imgs = [
                make_thumb(base), make_thumb(deployed),
                center_crop(base), center_crop(deployed)
            ]
        y = ix * height_per
        label = (path[-96:] + " | original · published · original zoom · published zoom")
        draw.text((10, y + 2), label, fill="black")
        for j, image in enumerate(imgs):
            canvas.paste(image, (10 + j * 507, y + 24))
    canvas.save(output_path, "JPEG", quality=88, optimize=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default=".")
    ap.add_argument("--site", default="dist")
    ap.add_argument("--out", default="photo-visual-quality")
    ap.add_argument("--max-preview", type=int, default=16)
    args = ap.parse_args()
    src = Path(args.source).resolve()
    dist = Path(args.site).resolve()
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    if not (src / "data/manifest.json").is_file() or not (dist / "index.html").is_file():
        raise SystemExit("Requires private source checkout and built staged public site")
    files = sorted(
        p.relative_to(src) for p in (src / "content").rglob("*")
        if p.is_file() and p.suffix.lower() in (".jpg", ".jpeg")
    )
    errors = []
    changed = []
    photo_total = 0
    for rel in files:
        staged = dist / rel
        if not staged.exists():
            errors.append({"path":str(rel),"reason":"missing public JPEG"})
            continue
        photo_total += 1
        a, b = src / rel, staged
        if a.stat().st_size == b.stat().st_size:
            # Identical sizes can still mean different pixels; optimizer only
            # alters files to change byte size, so this is the safe fast path.
            continue
        try:
            result = qa(a, b)
            result["path"] = str(rel)
            result["source_bytes_saved"] = result["source_bytes"] - result["published_bytes"]
            result["diagnostic_candidate"] = any(word in str(rel).lower() for word in DIAGNOSTIC_WORDS)
            if result["published_dims"][0] < 500 or result["published_dims"][1] < 350:
                result["warning"] = "Review small anatomical resolution"
            elif result["pixel_mean_absolute_error"] > 12:
                result["warning"] = "Inspect for texture/color loss"
            if result["gps_exif_in_published"]:
                errors.append({"path":str(rel),"reason":"GPS EXIF present in published JPEG"})
            changed.append(result)
        except Exception as e:
            errors.append({"path":str(rel),"reason":type(e).__name__+":"+str(e)[:160]})
    priority = sorted(changed, key=lambda x:(
        not x["diagnostic_candidate"], -x["source_bytes_saved"]
    ))[:args.max_preview]
    if priority:
        for i in range(0,len(priority),4):
            build_sheet(priority[i:i+4], src, dist, out / f"diagnostic-comparison-{i//4+1:02d}.jpg")
    result = {
        "mode":"read_only_before_and_after_anatomical_quality_review",
        "site_published":False,
        "jpeg_source_count":len(files),
        "jpeg_found_in_site":photo_total,
        "changed_photo_count":len(changed),
        "total_bytes_saved_by_changed_photos":sum(x["source_bytes_saved"] for x in changed),
        "mean_pixel_error_of_changed_photos":round(sum(x["pixel_mean_absolute_error"] for x in changed)/max(len(changed),1),2),
        "warnings":[x for x in changed if "warning" in x],
        "hard_errors":errors,
        "preview_paths":[str(x["path"]) for x in priority],
        "all_changed":changed
    }
    (out / "quality-report.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k not in ("all_changed","warnings")},indent=2))
    print("QA flagged images requiring visual review:", len(result["warnings"]))
    if errors:
        raise SystemExit(f"QA found {len(errors)} problems; report created, do not deploy")


if __name__ == "__main__":
    main()
