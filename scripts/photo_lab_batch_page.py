#!/usr/bin/env python3
"""Build one standalone, provisional, credited Photo Lab review gallery from an archived batch.

No image is installed into any canonical species card. The gallery is a viewing
and user-labeling surface, not botanical identity verification.
"""
import argparse
import csv
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
ALLOWED = {"CC0", "CC BY", "CC BY-SA", "CC BY-NC", "CC BY-NC-SA"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-id", required=True, help="e.g. diagnostic-123456789")
    ap.add_argument("--batch-number", required=True, help="e.g. 002")
    ap.add_argument("--max-per-species", type=int, default=5)
    args = ap.parse_args()

    batch_id = args.batch_id
    if not re.fullmatch(r"diagnostic-\d+", batch_id):
        ap.error("batch ID should match diagnostic-<numeric GitHub run ID>")
    number = args.batch_number
    if not re.fullmatch(r"\d{3}", number):
        ap.error("batch number should be three digits")

    batch = ROOT / "workflow/photo-library/batches" / batch_id
    archive = json.loads((batch / "archive.json").read_text(encoding="utf-8"))
    if archive.get("persistent_release") is not True:
        raise RuntimeError("Photo archive was not permanently published")
    photos = []
    groups = {}
    with (batch / "candidates.csv").open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            if (
                not row.get("staged_file")
                or row.get("license_basis") != "media"
                or row.get("photo_license_status") != "supported"
                or row.get("license") not in ALLOWED
                or row.get("identity_status") != "exact_name_metadata_only_review_image"
            ):
                continue
            species_id = row.get("canonical_id", "")
            image_url = row.get("image_url", "")
            record_id = row.get("observation_id", "")
            if not species_id or not image_url.startswith("https://") or not record_id:
                continue
            state = groups.setdefault(species_id, {"seen": set(), "count": 0})
            if state["count"] >= args.max_per_species or record_id in state["seen"]:
                continue
            state["seen"].add(record_id)
            state["count"] += 1
            photos.append({
                "id": species_id,
                "name": row["scientific_name"],
                "url": image_url,
                "page": row["source_page"],
                "credit": row["creator"],
                "license": row["license"],
                "observation": record_id,
                "source": row["source"],
                "archiveFile": row["staged_file"],
            })

    if not photos:
        raise RuntimeError("No individually licensed photo candidates to review")
    template_path = ROOT / "workflow/photo-library/templates/photo-lab-gallery-template.html"
    template = template_path.read_text(encoding="utf-8")
    payload = json.dumps(photos, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    page, replaced = re.subn(
        r"const PHOTOS=\[.*?\];\s*const KEY=",
        lambda m: "const PHOTOS=" + payload + ";\nconst KEY=",
        template,
        count=1,
        flags=re.DOTALL,
    )
    if replaced != 1:
        raise RuntimeError("Photo Lab template no longer contains the expected image list")
    page = page.replace(
        'const KEY="hays-botany-photo-review-diagnostic-001"',
        'const KEY="hays-botany-photo-review-diagnostic-' + number + '"',
    )
    page = page.replace(
        'batch:"diagnostic-38996245346"',
        'batch:"' + batch_id + '"',
    )
    page = page.replace(
        'Batch: <a href="https://github.com/Crking92/Hays-County-Botany/actions/runs/38996245346">Diagnostic 001</a>',
        'Batch: <a href="https://github.com/Crking92/Hays-County-Botany/actions/runs/'
        + batch_id.split("-")[1] + '">Diagnostic ' + number + "</a>",
    )
    page = page.replace(
        "Initial 21 targets; this page shows the 16 species with downloaded image-level licensed candidates, up to five distinct observations per species.",
        "This page shows " + str(len(groups)) + " species and "
        + str(len(photos)) + " attributed provisional images from separate source observations.",
    )
    page = page.replace(
        "<title>Photo Lab | Hays Botany</title>",
        "<title>Photo Lab Batch " + number + " | Hays Botany</title>",
    )
    page = page.replace(
        "<div class=\"brand\">✣ Hays Botany · Photo Lab</div>",
        "<div class=\"brand\">✣ Hays Botany · Photo Lab " + number + "</div>",
    )
    page = page.replace(
        "Look closer. Then decide.",
        "Batch " + number + ": Look closer. Then decide.",
    )
    # The live Photo Lab should display the newest unreviewed collection only.
    # Older pages and user reviews stay in GitHub history / photo-library records,
    # but no completed batch is linked from the learner or deployed by Cloudflare.
    page = re.sub(
        r'<a class="back" href="\./photo-review-batch-\d{3}\.html">.*?</a>',
        "",
        page,
    )
    page = page.replace(
        '<a class="back" href="./index.html">← Back to Visual Learner</a>',
        '<a class="back" href="./index.html">← Visual Learner</a>',
    )
    target_name = "photo-review-batch-" + number + ".html"
    (ROOT / target_name).write_text(page, encoding="utf-8")
    (ROOT / "photo-review.html").write_text(page, encoding="utf-8")
    print(json.dumps({
        "batch": batch_id, "number": number,
        "species": len(groups), "visible_review_photos": len(photos),
        "page": target_name, "installed_into_learner": 0
    }))


if __name__ == "__main__":
    main()
