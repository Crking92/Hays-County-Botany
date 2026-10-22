#!/usr/bin/env python3
"""Create a separately publishable, filtered Hays Botany web snapshot.

This is for the stand-alone NONCOMMERCIAL educational GitHub Pages site.
The canonical repository is publicly accessible as of October 20, 2026.
The rights-filtered output is dist/ only; source JSON/photo files are not edited.
The website filter cannot conceal any originals already committed to public GitHub.
No Photo Lab review page or restricted/unsupported photo bytes are shipped.

Image-level rights checks are conservative, not a substitute for the
original-source or full website rights review.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from collections import Counter
from pathlib import Path

from PIL import Image, ImageOps

IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".tif", ".tiff"}
ALLOWED_DOCS = {"species.json", "family.json", "genus.json"}
ALLOWED_DATA = {
    "manifest.json", "project.json", "learning-layer.json", "lesson-index.json"
}
OWNER = {"calvin king", "glass root garden", "calvin king / glass root garden"}
JOEY_CREDITED_PERMISSION = "JOEY_CREDITED_PUBLIC_LEARNER_20261021"
JOEY_CREATORS = {"joey santore", "joey santore / crime pays but botany doesn't"}


def credited_joey_frame(item: dict, noncommercial: bool) -> bool:
    """User-attested site-specific permission; NOT a change to the source license."""
    creator = str(item.get("creator") or "").strip().lower()
    source = str(item.get("source_page") or "").strip()
    frame_id = str(item.get("source_record_id") or "").strip()
    return (
        noncommercial
        and item.get("site_specific_public_permission") == JOEY_CREDITED_PERMISSION
        and creator in JOEY_CREATORS
        and source.startswith("https://www.youtube.com/watch?v=")
        and (
            bool(re.fullmatch(
                r"(?:jvid-)?" + re.escape(source.split("?v=", 1)[1].split("&", 1)[0]) + r"-[0-9]+",
                frame_id,
            ))
            or (
                not frame_id
                and source == "https://www.youtube.com/watch?v=Y7A530PjEbU"
                and item.get("file") in {
                    "images/chrysactinia-mexicana_habit-source-label_03-40.jpg",
                    "images/chrysactinia-mexicana_flower-head-leaves_04-00.jpg",
                }
            )
        )
    )


def rights(item: dict, noncommercial: bool) -> tuple[bool, str]:
    """An eligible *photograph*, not just an observation or search result."""
    creator = str(item.get("creator") or item.get("photographer") or "").strip()
    license_text = str(item.get("license") or "").strip().lower()
    source = str(item.get("source_page") or item.get("photo_source_url") or "").strip()
    reuse = str(item.get("public_reuse") or "").strip().lower()
    person = creator.lower()
    photo_id = (
        item.get("source_photo_id")
        or item.get("photo_id")
        or item.get("inat_photo_id")
    )
    if not source:
        return False, "missing verified individual photo source"
    if person in OWNER and photo_id:
        # Public display on this learner was expressly granted by the owner,
        # including older 'private' metadata: DO NOT rewrite historic licenses.
        return True, "Glass Root Garden photo: site-specific owner permission"
    if credited_joey_frame(item, noncommercial):
        return True, "Joey frame: credited noncommercial site permission"
    if reuse in {"no", "false", "private", "private_study_only"}:
        return False, "explicit private-use / no-public-reuse restriction"
    if not creator and not re.search(r"cc\s*0|cc0|public domain|\bpd\s*mark\b", license_text):
        return False, "missing creator"
    if any(t in license_text for t in ("all rights reserved", "private", "unknown", "not cleared", "no license")):
        return False, "unknown/private/all-rights-reserved license"
    # Detect ND in *all* CC orderings, including cc-by-nc-nd and cc-by-nd.
    # The old by-nd-only pattern missed licenses with NC before ND.
    if re.search(r"(?:^|[-\s])nd(?:$|[-\s])|no[- ]?deriv", license_text):
        return False, "no-derivatives license not screened for annotated lessons"
    if re.search(r"\bcc\s*0\b|cc0|public domain|\bpd[- ]?mark\b", license_text):
        return True, "CC0 / public domain"
    if not re.search(r"\bcc[- ]?by\b", license_text):
        return False, "no supported image-level public license"
    if re.search(r"\bnc\b|[- ]nc\b|noncommercial", license_text):
        if not noncommercial:
            return False, "noncommercial license, deployment use not confirmed"
        return True, "CC BY-NC (stand-alone noncommercial educational website)"
    return True, "CC BY / CC BY-SA"


def clean_web_copy(filename: Path):
    """Remove embedded EXIF/GPS or other raster metadata in public copies."""
    with Image.open(filename) as raw:
        image = ImageOps.exif_transpose(raw)
        suffix = filename.suffix.lower()
        tmp = filename.with_name(filename.name + ".clean")
        if suffix in {".jpg", ".jpeg"}:
            image.convert("RGB").save(tmp, "JPEG", quality=87, optimize=True)
        elif suffix == ".png":
            image.save(tmp, "PNG", optimize=True)
        elif suffix == ".webp":
            image.save(tmp, "WEBP", quality=88)
        elif suffix == ".gif":
            # Preserve animated content without silently altering its frames;
            # GIFs are held instead of shipping unexamined metadata/frames.
            raise ValueError("GIF requires individual animated-media review")
        else:
            raise ValueError("unsupported publication image type")
    tmp.replace(filename)


def build(root: Path, noncommercial: bool) -> dict:
    root = root.resolve()
    subprocess.run(["bash", "scripts/build_cloudflare_site.sh"], cwd=root, check=True)
    site = root / "dist"

    # Do not publish the PRIVATE candidate review gallery.
    (site / "photo-review.html").unlink(missing_ok=True)
    html = (site / "index.html").read_text(encoding="utf-8")
    html, count = re.subn(
        r'<a\s+class="photo-lab-nav"[^>]*>.*?</a>',
        "",
        html,
        flags=re.I | re.S,
    )
    if count != 1:
        raise RuntimeError("Cannot safely remove Photo Lab link; HTML layout changed")
    (site / "index.html").write_text(html, encoding="utf-8")

    data = site / "data"
    for file in data.iterdir():
        if file.name not in ALLOWED_DATA:
            if file.is_dir():
                shutil.rmtree(file)
            else:
                file.unlink()

    grant = json.loads((root / "workflow" / "JOEY_PHOTO_CREDITED_PUBLIC_PERMISSION_20261021.json").read_text(encoding="utf-8"))
    if grant.get("authorization_id") != JOEY_CREDITED_PERMISSION:
        raise RuntimeError("Joey permission registry ID mismatch; cannot publish its media")
    permitted_frames = set(grant.get("authorized_images", []))
    approved_paths: set[Path] = set()
    holds = []
    tally = Counter()
    content = site / "content"
    for sp in sorted((content / "taxa").rglob("species.json")):
        doc = json.loads(sp.read_text(encoding="utf-8"))
        accepted = []
        for img in doc.get("images", []):
            if not isinstance(img, dict) or not isinstance(img.get("file"), str):
                holds.append({"species": doc.get("id"), "reason": "invalid image record"})
                continue
            filename = img["file"].strip()
            if re.match(r"(?i)https?://", filename):
                holds.append({"species": doc.get("id"), "reason": "external media is not stored/individually reviewed"})
                continue
            path = (sp.parent / filename).resolve()
            if not path.is_relative_to(site) or not path.is_file():
                holds.append({"species": doc.get("id"), "reason": "missing or unsafe photo file"})
                continue
            # Only enumerated historic original Joey frames gain the user-attested
            # site-specific credit exception. A filename match alone is NOT enough:
            # creator + video origin + frame ID must also match.
            key = str(doc.get("id") or "") + "/" + filename
            if key in permitted_frames:
                candidate = dict(img)
                candidate["site_specific_public_permission"] = JOEY_CREDITED_PERMISSION
                if credited_joey_frame(candidate, noncommercial):
                    img = candidate
            ok, reason = rights(img, noncommercial)
            if not ok:
                tally["excluded_rights"] += 1
                holds.append({"species": doc.get("id"), "photo": filename, "reason": reason})
                continue
            if path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
                tally["excluded_format"] += 1
                continue
            try:
                clean_web_copy(path)
            except Exception as exc:
                tally["excluded_unreadable"] += 1
                holds.append({"species": doc.get("id"), "photo": filename, "reason": "unreadable public photo: " + str(exc)[:100]})
                continue
            approved_paths.add(path)
            if credited_joey_frame(img, noncommercial):
                # The source's old private-study statement stays intact on main.
                # The generated public-site copy gives visitors an accurate,
                # visible permission/attribution note instead.
                img = dict(img)
                img["historical_license_label"] = img.get("license")
                img["historical_public_reuse_label"] = img.get("public_reuse")
                img["license"] = "Credited educational website use (permission reported by project owner)"
                img["public_reuse"] = "yes — site-specific user-attested creator permission"
            accepted.append(img)
            tally["approved_photos"] += 1
            tally["rights_" + reason[:24]] += 1
        tally["species_checked"] += 1
        if not accepted:
            tally["cards_without_public_photos"] += 1
        elif len(accepted) == 1:
            tally["cards_with_one_public_photo"] += 1
        # Do not retain stale gallery references to files being excluded.
        doc["images"] = accepted
        # Existing private-source photo counts would be misleading on public pages.
        if isinstance(doc.get("curation_status"), dict):
            doc["curation_status"]["public_site_photo_count"] = len(accepted)
        sp.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Only published canonical species and approved family/genus/terms JSON are
    # needed. Don't expose SOURCES.txt, image-sources CSV, raw research, or
    # private photo candidate records.
    for file in sorted(content.rglob("*"), reverse=True):
        if not file.is_file():
            continue
        if file.suffix.lower() in IMAGE_EXT:
            if file.resolve() not in approved_paths:
                file.unlink()
                tally["unlinked_or_restricted_media_removed"] += 1
        elif file.suffix.lower() == ".json":
            if file.name not in ALLOWED_DOCS and "/terms/" not in file.as_posix():
                file.unlink()
        else:
            # Fail closed: only canonical lesson JSON and cleared photo bytes
            # belong in the publicly cloned content tree. Remove every other
            # file type, not just known private extensions.
            file.unlink()

    # The public repository should not run Jekyll on source JSON or asset paths.
    (site / ".nojekyll").write_text("", encoding="utf-8")
    # Force phone home-screen service workers to refresh when published.
    sw = site / "sw.js"
    if sw.is_file():
        state = str(tally["approved_photos"]) + "-" + str(tally["species_checked"])
        code = sw.read_text(encoding="utf-8")
        code, _ = re.subn(
            r'const CACHE_NAME = "[^"]+";',
            'const CACHE_NAME = "hays-botany-public-' + state + '";',
            code,
            count=1,
        )
        sw.write_text(code, encoding="utf-8")
    # Safety invariant: no candidate gallery or outside-project secrets.
    assert not (site / "photo-review.html").exists()
    for private_dir in ("workflow", "research-drafts", "reports", ".github", "curation-inbox", "curation-archive"):
        assert not (site / private_dir).exists()
    report = {
        "site_type": "stand-alone noncommercial educational GitHub Pages",
        "source_repo_remains_private": False,
        "source_repo_visibility_note": "public as of 2026-10-20; recheck GitHub Settings if changed",
        "photo_lab_excluded": True,
        "noncommercial_assumption": noncommercial,
        "counts": dict(tally),
        "holds_preview": holds[:75],
        "holds_total": len(holds),
        "note": "Public web copy excludes restricted photos and private archives; all approved photos still require ongoing attribution and appropriate use. This filter is not legal certification."
    }
    report_path = root / "reports" / "public-pages-snapshot-latest.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--noncommercial", action="store_true", help="Allow individually licensed CC BY-NC on a standalone, strictly noncommercial site")
    opts = p.parse_args()
    result = build(Path("."), opts.noncommercial)
    print(json.dumps(result["counts"], indent=2))
    print("Held photo records:", result["holds_total"])
    print("Public preview staged in dist; canonical source unchanged (source repository is public).")
