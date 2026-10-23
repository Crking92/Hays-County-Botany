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


# Narrow site-specific reuse grant: Bob Harms personally states these own Selected
# Central Texas Monocots images are free for scientific/educational use WITH credit.
# This is NOT a general photo license or a Creative Commons substitution.
HARMS_ALLOWED_IDS = frozenset({"NALE3-L", "NALE3-J5", "NALE3-s", "NALE3-j6", "NALE3-9", "NALE3-d"})
HARMS_BASE = "https://w3.biosci.utexas.edu/prc/Monocots/GrassHTML/data/"
HARMS_SITE_PERMISSION = "BOB_HARMS_SELECTED_MONOCOTS_EDU_WITH_CREDIT_20261022"
HARMS_EXACT_LICENSE = "© Bob Harms — scientific/educational use with attribution (NOT Creative Commons)"


# Independent site-specific, photo-by-photo Carolina canarygrass permission.
# Bob Harms Selected Central Texas Monocots: scientific/educational WITH CREDIT.
# No blanket waiver for any other copyrighted UT PRC images.
HARMS_PHCA_IMAGE_IDS = frozenset({"PHCA6-b","PHCA6-i","PHCA6-j","PHCA6-S","PHCA6-L"})


def permitted_harms_phalaris(item: dict, noncommercial: bool) -> bool:
    if not noncommercial or item.get("creator") != "Bob Harms":
        return False
    if item.get("license") != HARMS_EXACT_LICENSE:
        return False
    if item.get("site_specific_public_permission") != HARMS_SITE_PERMISSION:
        return False
    if item.get("license_url") != "https://w3.biosci.utexas.edu/prc/Monocots/":
        return False
    if item.get("source_taxon_name") != "Phalaris caroliniana":
        return False
    return any(item.get("source_page") == HARMS_BASE + "pages/" + photo_id + ".html"
               and item.get("source_image") == HARMS_BASE + "images/" + photo_id + ".jpg"
               for photo_id in HARMS_PHCA_IMAGE_IDS)



# Exact credited educational use for eight already source-vetted S. vaginiflorus
# photographs by Bob Harms. NOT a Creative Commons grant for other reuse.
SPVA_IDS = frozenset({"SPVA-a3","SPVA-b1","SPVA-c","SPVA-i","SPVA-J1","SPVA-j2","SPVA-d","SPVA-L"})
SPVA_LICENSE = "© Bob Harms — scientific/educational use permitted with photographer credit ONLY (NOT Creative Commons)"

def permitted_harms_spva(item: dict, noncommercial: bool) -> bool:
    if not noncommercial or item.get("creator") != "Bob Harms":
        return False
    if item.get("license") != SPVA_LICENSE:
        return False
    if item.get("site_specific_public_permission") != HARMS_SITE_PERMISSION:
        return False
    if item.get("license_url") != "https://w3.biosci.utexas.edu/prc/Monocots/":
        return False
    if item.get("source_taxon_name") != "Sporobolus vaginiflorus":
        return False
    return any(item.get("source_page") == HARMS_BASE + "pages/" + ident + ".html"
               and item.get("source_image") == HARMS_BASE + "images/" + ident + ".jpg"
               for ident in SPVA_IDS)


# Exact original copyrighted hairyseed paspalum photographs: Bob Harms grants
# scientific/educational use with individual creator credit, NOT a CC grant.
HARMS_PAPU_IDS = frozenset({"PAPU5-I","PAPU5-J","PAPU5-J1","PAPU5-L"})

def permitted_harms_papu(item: dict, noncommercial: bool) -> bool:
    if not noncommercial or item.get("creator") != "Bob Harms":
        return False
    if item.get("license") != HARMS_EXACT_LICENSE:
        return False
    if item.get("site_specific_public_permission") != HARMS_SITE_PERMISSION:
        return False
    if item.get("license_url") != "https://w3.biosci.utexas.edu/prc/Monocots/":
        return False
    if item.get("source_taxon_name") != "Paspalum pubiflorum":
        return False
    return any(item.get("source_page") == HARMS_BASE + "pages/" + i + ".html" and
               item.get("source_image") == HARMS_BASE + "images/" + i + ".jpg"
               for i in HARMS_PAPU_IDS)

# Strict image-level permission for original Selected Central Texas Monocots
# rough dropseed photographs. Copyright remains with Bob Harms; NOT CC.
SPCL_IDS = frozenset(["SPCL-a","SPCL-a1","SPCL-b","SPCL-I","SPCL-i1","SPCL-I2","SPCL-J","SPCL-J1","SPCL-J2","SPCL-S","SPCL-L"])
SPCL_LICENSE = "© Bob Harms — free for scientific/educational use with proper credit only (NOT CC)"

def permitted_harms_spcl(item: dict, noncommercial: bool) -> bool:
    if not noncommercial or item.get("creator") != "Bob Harms":
        return False
    if item.get("license") != SPCL_LICENSE:
        return False
    if item.get("site_specific_public_permission") != HARMS_SITE_PERMISSION:
        return False
    if item.get("license_url") != "https://w3.biosci.utexas.edu/prc/Monocots/":
        return False
    if item.get("source_taxon_name") != "Sporobolus clandestinus":
        return False
    return any(item.get("source_page") == HARMS_BASE + "pages/" + pid + ".html"
               and item.get("source_image") == HARMS_BASE + "images/" + pid + ".jpg"
               for pid in SPCL_IDS)

# Source- and variety-specific scientific/educational credit exception for these
# original Bob Harms composite-dropseed photographs. Copyrighted, NOT CC.
SPCO_IDS = frozenset(["SPCOD3-b","SPCOD3-i","SPCOD3-J0","SPCOD3-J1","SPCOD3-v","SPCOM-b","SPCOM-j1","SPCOM-8"])
SPCO_LICENSE = "© Bob Harms — scientific/educational use with credit only (NOT Creative Commons)"

def permitted_harms_spco(item: dict, noncommercial: bool) -> bool:
    if not noncommercial or item.get("creator") != "Bob Harms":
        return False
    if item.get("license") != SPCO_LICENSE or item.get("site_specific_public_permission") != HARMS_SITE_PERMISSION:
        return False
    if item.get("license_url") != "https://w3.biosci.utexas.edu/prc/Monocots/":
        return False
    if item.get("source_taxon_name") != "Sporobolus compositus":
        return False
    for pid in SPCO_IDS:
        variety = "Sporobolus compositus var. drummondii" if pid.startswith("SPCOD3-") else "Sporobolus compositus var. macer"
        if (item.get("source_page") == HARMS_BASE + "pages/" + pid + ".html"
            and item.get("source_image") == HARMS_BASE + "images/" + pid + ".jpg"
            and item.get("source_taxon") == variety):
            return True
    return False


# Bob Harms Selected Central Texas Monocots: only these 9 SCSC original
# photographs are permitted under exact copyrighted scientific/educational
# use WITH creator credit. Not CC / generic redistribution permission.
HARMS_SCSC_IMAGE_IDS = frozenset({"SCSC-a","SCSC-a1","SCSC-i","SCSC-J","SCSC-J1","SCSC-s","SCSC-9","SCSC-C","SCSC-L"})

def permitted_harms_little_bluestem(item: dict, noncommercial: bool) -> bool:
    if not noncommercial:
        return False
    if item.get("creator") != "Bob Harms":
        return False
    if item.get("license") != HARMS_EXACT_LICENSE:
        return False
    if item.get("site_specific_public_permission") != HARMS_SITE_PERMISSION:
        return False
    if item.get("license_url") != "https://w3.biosci.utexas.edu/prc/Monocots/":
        return False
    if item.get("source_taxon_name") != "Schizachyrium scoparium":
        return False
    return any(item.get("source_page") == HARMS_BASE+"pages/"+id+".html"
               and item.get("source_image") == HARMS_BASE+"images/"+id+".jpg"
               for id in HARMS_SCSC_IMAGE_IDS)


def permitted_harms_wintergrass(item: dict, noncommercial: bool) -> bool:
    if not noncommercial:
        return False
    if item.get("creator") != "Bob Harms" or item.get("license") != HARMS_EXACT_LICENSE:
        return False
    if item.get("site_specific_public_permission") != HARMS_SITE_PERMISSION:
        return False
    if item.get("license_url") != "https://w3.biosci.utexas.edu/prc/Monocots/":
        return False
    if item.get("source_taxon_name") != "Nassella leucotricha":
        return False
    page = item.get("source_page")
    img = item.get("source_image")
    return any(page == HARMS_BASE + "pages/" + photo_id + ".html" and
               img == HARMS_BASE + "images/" + photo_id + ".jpg"
               for photo_id in HARMS_ALLOWED_IDS)


# Five Bob Harms original Andropogon gerardii images, NOT all DigFlora.
# Selected Monocots credited scientific/educational publication only.
HARMS_ANGE_IDS = frozenset({"ANGE-i", "ANGE-j1", "ANGE-L", "ANGE-9", "ANGE-d"})

def permitted_harms_big_bluestem(item, noncommercial=False):
    if not noncommercial or item.get("creator") != "Bob Harms":
        return False
    if item.get("license") != HARMS_EXACT_LICENSE or item.get("site_specific_public_permission") != HARMS_SITE_PERMISSION:
        return False
    if item.get("license_url") != "https://w3.biosci.utexas.edu/prc/Monocots/":
        return False
    if item.get("source_taxon_name") != "Andropogon gerardii":
        return False
    return any(item.get("source_page") == HARMS_BASE+"pages/"+pid+".html"
               and item.get("source_image") == HARMS_BASE+"images/"+pid+".jpg"
               for pid in HARMS_ANGE_IDS)

# Bob Harms Selected Monocots BOISS-9 only; copyrighted author-licensed for
# credited science/education, NOT a grant for any separate DigFlora ligule.
def permitted_harms_kr_spikelets(record, noncommercial=False):
    return (
        bool(noncommercial)
        and record.get("creator") == "Bob Harms"
        and record.get("license") == HARMS_EXACT_LICENSE
        and record.get("site_specific_public_permission") == HARMS_SITE_PERMISSION
        and record.get("license_url") == "https://w3.biosci.utexas.edu/prc/Monocots/"
        and record.get("source_taxon_name") == "Bothriochloa ischaemum var. songarica"
        and record.get("source_page") == HARMS_BASE+"pages/BOISS-9.html"
        and record.get("source_image") == HARMS_BASE+"images/BOISS-9.jpg"
    )

# Bob Harms's four exact Panicum obtusum (= Hopia obtusa) Selected Monocots photographs.
# Scientific/educational reuse WITH credited original author, not Creative Commons.
HARMS_HOPIA_IDS = frozenset({"PAOB-I","PAOB-J","PAOB-C","PAOB-L"})

def permitted_harms_hopia(item, noncommercial=False):
    if not noncommercial or item.get("creator") != "Bob Harms":
        return False
    if item.get("license") != HARMS_EXACT_LICENSE:
        return False
    if item.get("site_specific_public_permission") != HARMS_SITE_PERMISSION:
        return False
    if item.get("license_url") != "https://w3.biosci.utexas.edu/prc/Monocots/":
        return False
    if item.get("source_taxon_name") != "Panicum obtusum":
        return False
    if item.get("accepted_taxon_name") != "Hopia obtusa":
        return False
    return any(item.get("source_page") == HARMS_BASE+"pages/"+ident+".html" and
               item.get("source_image") == HARMS_BASE+"images/"+ident+".jpg"
               for ident in HARMS_HOPIA_IDS)

# Only the originally identified Selected Monocots ERSE5-9 cupgrass
# macro, author-released for credited scientific/educational use (NOT CC).
def permitted_harms_eriochloa_sericea(record, noncommercial=False):
    return (
        bool(noncommercial)
        and record.get("creator") == "Bob Harms"
        and record.get("license") == HARMS_EXACT_LICENSE
        and record.get("site_specific_public_permission") == HARMS_SITE_PERMISSION
        and record.get("license_url") == "https://w3.biosci.utexas.edu/prc/Monocots/"
        and record.get("source_taxon_name") == "Eriochloa sericea"
        and record.get("source_page") == HARMS_BASE+"pages/ERSE5-9.html"
        and record.get("source_image") == HARMS_BASE+"images/ERSE5-9.jpg"
    )

# Five source-specific Bob Harms green sprangletop images, identified originally
# as Leptochloa dubia (= accepted Disakisperma dubium). Licensed by their creator
# ONLY for properly credited scientific / educational use, not Creative Commons.
HARMS_LEDU_IDS = frozenset({"LEDU-i","LEDU-j","LEDU-j2","LEDU-S","LEDU-d"})

def permitted_harms_disakisperma(item, noncommercial=False):
    if not noncommercial or item.get("creator") != "Bob Harms":
        return False
    if item.get("license") != HARMS_EXACT_LICENSE:
        return False
    if item.get("site_specific_public_permission") != HARMS_SITE_PERMISSION:
        return False
    if item.get("license_url") != "https://w3.biosci.utexas.edu/prc/Monocots/":
        return False
    if item.get("source_taxon_name") != "Leptochloa dubia" or item.get("accepted_taxon_name") != "Disakisperma dubium":
        return False
    return any(item.get("source_page") == HARMS_BASE+"pages/"+ident+".html" and
               item.get("source_image") == HARMS_BASE+"images/"+ident+".jpg"
               for ident in HARMS_LEDU_IDS)

# Exactly six selected Bob Harms ORIGINAL Limnodea arkansana images.
# The copyright holder permits properly credited scientific/educational use,
# NOT generic Creative Commons or unrelated DigFlora images.
HARMS_LIAR_IDS = frozenset({"LIAR-b","LIAR-i","LIAR-J","LIAR-s","LIAR-d","LIAR-L"})

def permitted_harms_limnodea(item, noncommercial=False):
    if not noncommercial or item.get("creator") != "Bob Harms":
        return False
    if item.get("license") != HARMS_EXACT_LICENSE:
        return False
    if item.get("site_specific_public_permission") != HARMS_SITE_PERMISSION:
        return False
    if item.get("license_url") != "https://w3.biosci.utexas.edu/prc/Monocots/":
        return False
    if item.get("source_taxon_name") != "Limnodea arkansana":
        return False
    return any(item.get("source_page") == HARMS_BASE+"pages/"+ident+".html" and
               item.get("source_image") == HARMS_BASE+"images/"+ident+".jpg"
               for ident in HARMS_LIAR_IDS)

# Exactly four explicitly credited Bob Harms Selected Monocots originals
# of *other subspecies* D. panicea subsp. brachiata; NEVER count as
# subsp. mucronata photographed voucher.
HARMS_LEPAB_IDS = frozenset({"LEPAB-I","LEPAB-J","LEPAB-J1","LEPAB-L"})
def permitted_harms_dinebra_brachiata_comparison(record, noncommercial=False):
    return (
        bool(noncommercial)
        and record.get("creator") == "Bob Harms"
        and record.get("license") == HARMS_EXACT_LICENSE
        and record.get("license_url") == "https://w3.biosci.utexas.edu/prc/Monocots/"
        and record.get("site_specific_public_permission") == HARMS_SITE_PERMISSION
        and record.get("source_taxon_name") == "Dinebra panicea subsp. brachiata"
        and record.get("taxon_comparison_only") is True
        and any(record.get("source_page") == HARMS_BASE+"pages/"+id+".html"
                and record.get("source_image") == HARMS_BASE+"images/"+id+".jpg"
                for id in HARMS_LEPAB_IDS)
    )

# Five original source-authenticated Bob Harms Elymus virginicus frames,
# Selected Central Texas Monocots. Copyrighted, NOT Creative Commons;
# educational/scientific site publication only with original author credit.
HARMS_ELVI3_IDS = frozenset({"ELVI3-b","ELVI3-b1","ELVI3-I","ELVI3-i1","ELVI3-J2"})

def permitted_harms_elymus_virginicus(item, noncommercial=False):
    if not noncommercial or item.get("creator") != "Bob Harms":
        return False
    if item.get("license") != HARMS_EXACT_LICENSE:
        return False
    if item.get("site_specific_public_permission") != HARMS_SITE_PERMISSION:
        return False
    if item.get("license_url") != "https://w3.biosci.utexas.edu/prc/Monocots/":
        return False
    if item.get("source_taxon_name") != "Elymus virginicus":
        return False
    return any(item.get("source_page") == HARMS_BASE+"pages/"+ident+".html" and
               item.get("source_image") == HARMS_BASE+"images/"+ident+".jpg"
               for ident in HARMS_ELVI3_IDS)

# Nine exact original photographed Elymus canadensis Selected Central Texas Monocots images.
# Credit Bob Harms, copyrighted author's educational/scientific use grant, NOT CC.
HARMS_ELCA4_IDS = frozenset({"ELCA4-b", "ELCA4-I", "ELCA4-i1", "ELCA4-J1", "ELCA4-J", "ELCA4-J3", "ELCA4-S", "ELCA4-d", "ELCA4-L"})

def permitted_harms_elymus_canadensis(item, noncommercial=False):
    if not noncommercial or item.get("creator") != "Bob Harms":
        return False
    if item.get("license") != HARMS_EXACT_LICENSE or item.get("site_specific_public_permission") != HARMS_SITE_PERMISSION:
        return False
    if item.get("license_url") != "https://w3.biosci.utexas.edu/prc/Monocots/" or item.get("source_taxon_name") != "Elymus canadensis":
        return False
    return any(item.get("source_page") == HARMS_BASE+"pages/"+pid+".html" and
               item.get("source_image") == HARMS_BASE+"images/"+pid+".jpg"
               for pid in HARMS_ELCA4_IDS)

def photo_rights(record, noncommercial=False):
    if permitted_harms_elymus_canadensis(record, noncommercial):
        return None
    if permitted_harms_elymus_virginicus(record, noncommercial):
        return None
    if permitted_harms_dinebra_brachiata_comparison(record, noncommercial):
        return None
    if permitted_harms_limnodea(record, noncommercial):
        return None
    if permitted_harms_disakisperma(record, noncommercial):
        return None
    if permitted_harms_eriochloa_sericea(record, noncommercial):
        return None
    if permitted_harms_hopia(record, noncommercial):
        return None
    if permitted_harms_kr_spikelets(record, noncommercial):
        return None
    if permitted_harms_big_bluestem(record, noncommercial):
        return None

    creator = clean(record.get("creator") or record.get("photographer"))
    lic = clean(record.get("license"))
    source = record.get("source_page") or record.get("photo_source_url") or record.get("source_url")
    public_reuse = clean(record.get("public_reuse"))
    photo_id = record.get("source_photo_id") or record.get("photo_id") or record.get("inat_photo_id")
    explicitly_private = public_reuse in {"no", "false", "private", "private_study_only"}
    is_owner = creator in OWNER_NAMES and bool(source) and bool(photo_id)
    if is_owner:  # Separately recorded site-specific owner authorization, not a Creative Commons license.
        return None
    if permitted_harms_wintergrass(record, noncommercial) or permitted_harms_phalaris(record, noncommercial) or permitted_harms_spva(record, noncommercial) or permitted_harms_little_bluestem(record, noncommercial) or permitted_harms_papu(record, noncommercial) or permitted_harms_spcl(record, noncommercial) or permitted_harms_spco(record, noncommercial):
        return None  # Explicit photographed author educational-use permission, still copyrighted.
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
