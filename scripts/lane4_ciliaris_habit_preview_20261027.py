#!/usr/bin/env python3
"""Reduce archived 1.37MB Southern crabgrass field-habit to review size only.

The canonical archived licensed original remains untouched. The reduced preview
is kept in non-public reports directory for visual QA, not counted as a photo.
"""
from pathlib import Path
from PIL import Image,ImageOps
p=Path("content/taxa/Poaceae/Digitaria/digitaria-ciliaris/images/starr-140909-1746-live-habit-maui.jpg")
assert p.is_file()
with Image.open(p) as pic:
    pic=ImageOps.exif_transpose(pic).convert("RGB")
    assert pic.size==(1920,1440)
    pic.thumbnail((780,780),Image.Resampling.LANCZOS)
    dst=Path("reports/lane4-ciliaris-20261027-habit-qa-preview.jpg")
    dst.parent.mkdir(exist_ok=True)
    pic.save(dst,"JPEG",quality=78,optimize=True)
assert dst.stat().st_size<450000
print("VISUAL REVIEW ONLY",dst, pic.size,dst.stat().st_size)
