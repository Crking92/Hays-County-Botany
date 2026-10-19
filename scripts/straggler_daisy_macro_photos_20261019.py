#!/usr/bin/env python3
"""One-species, two-photo CC BY 3.0 illustrated anatomical upgrade for Calyptocarpus vialis.
Photos and annotation positions were selected against the named original Wikimedia Commons
image previews before installation. Action must verify real downloaded JPEGs and metadata.
This is NOT an all-project photo importer, taxonomy update, or automation worker.
"""
import csv
import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(".")
SID = "calyptocarpus-vialis"
P = ROOT / "content/taxa/Asteraceae/Calyptocarpus/calyptocarpus-vialis"
CARD = P / "species.json"
LICENSE = "https://creativecommons.org/licenses/by/3.0/"
TODAY = "2026-10-19"

SOURCE = [
    {
        "id": "3968",
        "url": "https://upload.wikimedia.org/wikipedia/commons/3/3d/Starr_050210-3968_Calyptocarpus_vialis.jpg",
        "page": "https://commons.wikimedia.org/wiki/File:Starr_050210-3968_Calyptocarpus_vialis.jpg",
        "filename": "starr-3968-flower-phyllary-arrows.jpg",
        "role": "Confirm it · enlarged flower-head side view: green involucral bract (phyllary) and yellow ray floret labeled with arrows; complete underside and bract count not shown.",
        "points": [
            ("Phyllary / green bract", (0.51, 0.485), (0.10, 0.13)),
            ("Yellow ray floret", (0.535, 0.225), (0.67, 0.11)),
        ],
    },
    {
        "id": "3974",
        "url": "https://upload.wikimedia.org/wikipedia/commons/e/ea/Starr_050210-3974_Calyptocarpus_vialis.jpg",
        "page": "https://commons.wikimedia.org/wiki/File:Starr_050210-3974_Calyptocarpus_vialis.jpg",
        "filename": "starr-3974-cypsela-awns-arrows.jpg",
        "role": "Confirm it · isolated mature cypsela with two visible pappus awns, individually indicated; fine backward/forward-pointing barbs not resolved in this photograph.",
        "points": [
            ("Pappus awn 1", (0.37, 0.18), (0.075, 0.085)),
            ("Pappus awn 2", (0.615, 0.145), (0.68, 0.07)),
            ("Cypsela / dry fruit", (0.48, 0.59), (0.065, 0.65)),
        ],
    },
]

def font(size):
    for name in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                 "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()

def annotate(image, points):
    # Source previews are 4:3. Coordinates were manually selected in the 1000x750
    # version of these same original photos; all coordinates below are normalized.
    w, h = image.size
    d = ImageDraw.Draw(image, "RGBA")
    face = font(max(17, int(w * 0.018)))
    for text, target, label in points:
        tx, ty = round(w * target[0]), round(h * target[1])
        lx, ly = round(w * label[0]), round(h * label[1])
        bbox = d.textbbox((lx, ly), text, font=face, stroke_width=0)
        pad = max(6, int(w * 0.006))
        rect = (lx-pad, ly-pad, bbox[2]+pad, bbox[3]+pad)
        d.rounded_rectangle(rect, radius=7, fill=(11, 28, 24, 228), outline=(247, 246, 231, 255), width=2)
        d.text((lx, ly), text, font=face, fill=(255, 255, 250, 255))
        origin = (min(rect[2], max(rect[0], tx)), rect[3] if ty > rect[3] else rect[1])
        d.line([origin, (tx, ty)], fill=(15, 15, 15, 255), width=7)
        d.line([origin, (tx, ty)], fill=(245, 211, 58, 255), width=3)
        # Small arrowhead ending exactly at the photo-checked target.
        from math import atan2, cos, sin, pi
        angle = atan2(ty-origin[1], tx-origin[0])
        length = max(13, int(w * 0.016))
        pts = [(tx,ty),
               (tx-length*cos(angle-0.40), ty-length*sin(angle-0.40)),
               (tx-length*cos(angle+0.40), ty-length*sin(angle+0.40))]
        d.polygon(pts, fill=(245, 211, 58, 255))
    return image

def get_photo(item):
    u = urlparse(item["url"])
    assert u.scheme == "https" and u.hostname == "upload.wikimedia.org"
    assert u.path.endswith("Starr_050210-"+item["id"]+"_Calyptocarpus_vialis.jpg")
    response = requests.get(item["url"], timeout=45, headers={
        "User-Agent": "HaysCountyBotanyEducationalPhotoReview/1.0 (https://github.com/Crking92/Hays-County-Botany; educational reuse)",
        "Referer": item["page"],
        "Accept": "image/jpeg,image/*;q=0.8"})
    response.raise_for_status()
    if len(response.content) < 50000 or len(response.content) > 12000000:
        raise ValueError("Unexpected original image size: " + item["id"])
    with Image.open(io.BytesIO(response.content)) as src:
        if src.format != "JPEG" or src.size[0] < 1800 or src.size[1] < 1250:
            raise ValueError("Unexpected original image dimensions: " + item["id"])
        src.load()
        im = ImageOps.exif_transpose(src).convert("RGB")
    im.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
    if abs(im.width / im.height - 4/3) > 0.02:
        raise ValueError("Incorrect thumbnail orientation/aspect")
    im = annotate(im, item["points"])
    output = io.BytesIO()
    im.save(output, "JPEG", quality=90, optimize=True, progressive=True)
    data = output.getvalue()
    with Image.open(io.BytesIO(data)) as verify:
        verify.verify()
    return data, list(im.size), hashlib.sha256(response.content).hexdigest()

def main():
    assert CARD.exists()
    manifest = json.loads((ROOT/"data/manifest.json").read_text())
    assert {v["id"]: v["path"] for v in manifest["species"]}.get(SID) == str(CARD)
    claims = json.loads((ROOT/"workflow/work-claims.json").read_text()).get("claims", [])
    for claim in claims:
        if SID in (claim.get("taxa") or []) and claim.get("status") in {"active","claimed","in_progress"}:
            raise SystemExit("Do not overlap another active species claim")
    card = json.loads(CARD.read_text())
    assert card["id"] == SID and card["scientific_name"] == "Calyptocarpus vialis"
    images = card.get("images") or []
    assert len(images) >= 3
    if all(any(r.get("file","").endswith(s["filename"]) for r in images) for s in SOURCE):
        print("Both annotated Commons photos already installed; no-op")
        return
    for item in SOURCE:
        if any(r.get("file","").endswith(item["filename"]) for r in images):
            raise ValueError("Partial photo install detected; do not overwrite")
        if (P/"images"/item["filename"]).exists():
            raise ValueError("Untracked file collision")
    ready = [(item, *get_photo(item)) for item in SOURCE]
    for item, content, dims, raw_sha in ready:
        outfile = P/"images"/item["filename"]
        outfile.parent.mkdir(parents=True,exist_ok=True)
        outfile.write_bytes(content)
        images.append({
            "file": "images/"+item["filename"], "role": item["role"],
            "creator": "Forest & Kim Starr", "license": "CC BY 3.0",
            "license_url": LICENSE, "source_platform": "Wikimedia Commons / Plants of Hawaii",
            "source_page": item["page"], "downloaded_from": item["url"],
            "image_dimensions": dims,
            "study_use": "Attributed botanical education",
            "public_reuse": "CC BY 3.0; attribution and notice of modifications required",
            "modifications": "Original cropped/resized to max 1200 px and annotation arrows/labels added; original untouched at Wikimedia",
            "original_image_sha256": raw_sha,
            "anatomy_arrows": "Baked yellow arrows point at structures checked in original Wikimedia 1000x750 previews; after-install enlarged review still recommended.",
            "photo_review": "Source exact taxon and CC BY 3.0 license visually verified on Wikimedia; arrows selected at actual visible anatomy in source preview. Fine pappus barbs and underside complete phyllary count NOT shown.",
        })
    card["images"] = images
    cur = card.setdefault("curation_status",{})
    cur["photo_metadata_count"] = len(images)
    cur["photo_files_present"] = len(images)
    cur["macro_photo_install"] = TODAY
    cur["finished_field_id_pass"] = "PASS_IN_PROGRESS"
    cur["actual_visual_diagnostic_review"] = "Original source visually checked; two derived arrowed JPEGs need final published-page visual review, fine barbs and underside phyllary count remain unresolved"
    cur["required_to_finish"] = [
        "Inspect installed annotated originals on published site and verify rendered arrow positions",
        "Source true underside phyllary view if teaching entire bract arrangement/count",
        "Source finer pappus barb macro if teaching barb orientation",
        "Verify the exact original license versions for archived Dan Johnson and Linda Jo Conn CC BY photos",
    ]
    visual = card.setdefault("learner_visual_status",{})
    visual["image_count"] = len(images)
    visual["mode"] = "species_finished_text_plus_wikimedia_macro_arrows_pending_final_qc"
    visual["note"] = "Five physical images, including two rights-verified CC BY 3.0 macro photos with visible anatomical labels; fine pappus barbs and entire underside phyllary arrangement remain unresolved. No claim of finished visual QC."
    card["photo_note"] = (card.get("photo_note","") + " Two clearly licensed Wikimedia Commons macro reference photos added with anatomically selected arrows (Forest & Kim Starr, CC BY 3.0). Fine pappus barbs and full underside phyllary count still lack demonstration.").strip()
    CARD.write_text(json.dumps(card, indent=2, ensure_ascii=False)+"\n")
    csvfile=P/"image-sources.csv"
    with csvfile.open(newline="") as f:
        rows=list(csv.DictReader(f))
    if rows:
        names=list(rows[0])
        for item in SOURCE:
            row={k:"" for k in names}
            row.update({"file_name":item["filename"],"role":item["role"],"creator":"Forest & Kim Starr",
                        "license":"CC BY 3.0","license_url":LICENSE,"source_page":item["page"],
                        "direct_url":item["url"],"study_use":"Attributed botanical education",
                        "public_reuse":"CC BY 3.0 with attribution",
                        "modifications":"Resized JPG and anatomical arrows drawn; annotated derivative"})
            rows.append(row)
        with csvfile.open("w",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=names,lineterminator="\n")
            writer.writeheader();writer.writerows(rows)
    report = {
        "species": SID,"state":"INSTALLED_TWO_ANNOTATED_MACRO_PHOTOS_PENDING_FINAL_VISUAL_QC",
        "original_gallery_photos_preserved": 3,"new_photo_count": 2,
        "image_files": [s["filename"] for s in SOURCE],
        "licenses": "Forest & Kim Starr CC BY 3.0; original source Commons file pages independently checked",
        "remaining":cur["required_to_finish"],
        "science_and_nativeness_untouched":True,
        "site_published":False
    }
    (ROOT/"reports/straggler-daisy-macro-photo-20261019.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
if __name__=="__main__":
    main()
