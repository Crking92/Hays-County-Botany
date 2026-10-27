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


# Five original Bob Harms Selected Monocots BIG bluestem micro photographs.
# Source-specific, credited, educational/noncommercial website use only; NOT CC.
HARMS_ANGE_IDS = frozenset({"ANGE-i", "ANGE-j1", "ANGE-L", "ANGE-9", "ANGE-d"})

def permitted_harms_big_bluestem(item: dict, noncommercial: bool) -> bool:
    if not noncommercial or item.get("creator") != "Bob Harms":
        return False
    if item.get("license") != HARMS_EXACT_LICENSE:
        return False
    if item.get("site_specific_public_permission") != HARMS_SITE_PERMISSION:
        return False
    if item.get("license_url") != "https://w3.biosci.utexas.edu/prc/Monocots/":
        return False
    if item.get("source_taxon_name") != "Andropogon gerardii":
        return False
    return any(item.get("source_page") == HARMS_BASE+"pages/"+pid+".html"
               and item.get("source_image") == HARMS_BASE+"images/"+pid+".jpg"
               for pid in HARMS_ANGE_IDS)

# Exact one KR bluestem source photo from Bob Harms' Selected Monocots, not DigFlora.
# The Selected Monocots author permits scientific/educational use with credit.
# Do not grant the separate DigFlora BOISS-LX-21Jul-A.JPG this permission.
def permitted_harms_kr_spikelets(item: dict, noncommercial: bool) -> bool:
    return (
        bool(noncommercial)
        and item.get("creator") == "Bob Harms"
        and item.get("license") == HARMS_EXACT_LICENSE
        and item.get("site_specific_public_permission") == HARMS_SITE_PERMISSION
        and item.get("license_url") == "https://w3.biosci.utexas.edu/prc/Monocots/"
        and item.get("source_taxon_name") == "Bothriochloa ischaemum var. songarica"
        and item.get("source_page") == HARMS_BASE+"pages/BOISS-9.html"
        and item.get("source_image") == HARMS_BASE+"images/BOISS-9.jpg"
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

# Exact documented Bob Harms Selected Monocots Eriochloa sericea spikelet
# image ERSE5-9 ONLY; author licenses credited science/education, NOT CC.
# No blanket rights to his other collections, commercial use or generic taxa.
def permitted_harms_eriochloa_sericea(item: dict, noncommercial: bool) -> bool:
    return (
        bool(noncommercial)
        and item.get("creator") == "Bob Harms"
        and item.get("license") == HARMS_EXACT_LICENSE
        and item.get("site_specific_public_permission") == HARMS_SITE_PERMISSION
        and item.get("license_url") == "https://w3.biosci.utexas.edu/prc/Monocots/"
        and item.get("source_taxon_name") == "Eriochloa sericea"
        and item.get("source_page") == HARMS_BASE+"pages/ERSE5-9.html"
        and item.get("source_image") == HARMS_BASE+"images/ERSE5-9.jpg"
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

# Exact Selected Monocots Leptochloa panicea ssp. brachiata (= Dinebra
# panicea subsp. brachiata), OTHER subspecies, never treated as mucronata.
# Copyright Bob Harms, reuse permitted for credited science/education ONLY.
HARMS_LEPAB_IDS = frozenset({"LEPAB-I","LEPAB-J","LEPAB-J1","LEPAB-L"})
def permitted_harms_dinebra_brachiata_comparison(item: dict, noncommercial: bool) -> bool:
    return (
        bool(noncommercial)
        and item.get("creator") == "Bob Harms"
        and item.get("license") == HARMS_EXACT_LICENSE
        and item.get("license_url") == "https://w3.biosci.utexas.edu/prc/Monocots/"
        and item.get("site_specific_public_permission") == HARMS_SITE_PERMISSION
        and item.get("source_taxon_name") == "Dinebra panicea subsp. brachiata"
        and item.get("taxon_comparison_only") is True
        and any(item.get("source_page") == HARMS_BASE+"pages/"+id+".html"
                and item.get("source_image") == HARMS_BASE+"images/"+id+".jpg"
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

# Seven exact source-identified Bob Harms Eleusine indica photo originals.
# Copyrighted educational/scientific reuse with credit, NOT Creative Commons.
HARMS_ELIN3_IDS = frozenset({"ELIN3-b","ELIN3-I","ELIN3-i1","ELIN3-j1","ELIN3-J2","ELIN3-9","ELIN3-L"})

def permitted_harms_eleusine_indica(item, noncommercial=False):
    if not noncommercial or item.get("creator") != "Bob Harms":
        return False
    if item.get("license") != HARMS_EXACT_LICENSE or item.get("site_specific_public_permission") != HARMS_SITE_PERMISSION:
        return False
    if item.get("license_url") != "https://w3.biosci.utexas.edu/prc/Monocots/" or item.get("source_taxon_name") != "Eleusine indica":
        return False
    return any(item.get("source_page") == HARMS_BASE+"pages/"+pid+".html" and
               item.get("source_image") == HARMS_BASE+"images/"+pid+".jpg"
               for pid in HARMS_ELIN3_IDS)

# Exact Tom Chester South Kaibab Trail Erioneuron originals.
# Author explicitly permits credited reproduction of his page. This is NOT CC.
# These exact filenames and original linked URLs are the only exception.
TOM_CHESTER_PAGE = "https://tchester.org/gc/plants/species/erioneuron_pilosum.html"
TOM_CHESTER_BASE = "https://tchester.org/gc/plants/species/pix/erioneuron_pilosum/"
TOM_CHESTER_PERMISSION = "TOM_CHESTER_PAGE_CREDITED_REPRODUCTION_20261026"
TOM_CHESTER_LICENSE = "Author's explicit source-page credited-reproduction permission (not CC)"
TOM_CHESTER_FILES = {
    "images/tom-chester-hairy-tridens-in-situ-heads-and-crown.jpg": "erioneuron_pilosum_5_crop_35.jpg",
    "images/tom-chester-hairy-tridens-narrow-white-edged-basal-leaves.jpg": "erioneuron_pilosum_4_crop_50.jpg",
    "images/tom-chester-hairy-tridens-woolly-spikelet-head-close.jpg": "erioneuron_pilosum_3_crop_2.jpg",
}

def permitted_tom_chester_erioneuron(item: dict, noncommercial: bool) -> bool:
    if not noncommercial:
        return False
    if item.get("creator") != "Tom Chester" or item.get("license") != TOM_CHESTER_LICENSE:
        return False
    if item.get("site_specific_public_permission") != TOM_CHESTER_PERMISSION:
        return False
    if item.get("source_taxon_name") != "Erioneuron pilosum":
        return False
    if item.get("license_url") != TOM_CHESTER_PAGE or item.get("source_permission_page") != TOM_CHESTER_PAGE:
        return False
    name = item.get("file")
    return name in TOM_CHESTER_FILES and item.get("source_page") == TOM_CHESTER_BASE + TOM_CHESTER_FILES[name]


# Source-specific educational reuse ONLY: John Kava's exact Yavapai
# curlymesquite hairy-node photo. This is NOT a Creative Commons license,
# and NOT a general release for unrelated University of Arizona photographs.
KAVA_SOURCE_PAGE = "https://yavapaiplants.extension.arizona.edu/hilaria-belangeri"
KAVA_PERMISSION_PAGE = "https://yavapaiplants.extension.arizona.edu/about-website"
KAVA_PERMISSION_ID = "YAVAPAI_JOHN_KAVA_HIBE_NODE_EDUCATIONAL_20261026"
KAVA_LICENSE = "© John Kava — educational-use permission with credit (NOT Creative Commons)"
KAVA_REL = "images/john-kava-curlymesquite-hairy-node-educational.jpg"
KAVA_FULL = "content/taxa/Poaceae/Hilaria/hilaria-belangeri/" + KAVA_REL

def permitted_kava_curly_node(item: dict, noncommercial: bool) -> bool:
    image = item.get("file") or item.get("image_url")
    return (
        noncommercial
        and item.get("creator") == "John Kava"
        and item.get("license") == KAVA_LICENSE
        and item.get("site_specific_public_permission") == KAVA_PERMISSION_ID
        and item.get("source_page") == KAVA_SOURCE_PAGE
        and item.get("source_permission_page") == KAVA_PERMISSION_PAGE
        and item.get("license_url") == KAVA_PERMISSION_PAGE
        and item.get("source_taxon_name") == "Hilaria belangeri"
        and item.get("source_photo_id") == "Hilaria_belangeri_FNodewithtuft_20"
        and image in {KAVA_REL, KAVA_FULL}
    )



# Dave Thayer explicitly grants unrestricted reuse of his own photographs on
# https://www.azgrasses.org/ ; the two species-labelled images below are his
# own documented site images. This is NOT a Creative Commons relicensing and
# must never be extended to the site's few third-party credited images.
THAYER_KR_PERMISSION = "DAVE_THAYER_AZGRASSES_OWN_PHOTOS_FREE_USE_20261027"
THAYER_KR_LICENSE = "© Dave Thayer — own photographs free to use per site statement (NOT Creative Commons)"
THAYER_KR_SOURCE = "https://www.azgrasses.org/pages-grasses/BB/Bothriochloa%20ischaemum.html"
THAYER_KR_PERMISSION_PAGE = "https://www.azgrasses.org/"
THAYER_KR_IMAGES = {
    "Bothriochloa_ischaemum8": "https://www.azgrasses.org/images-grasses/B/Bothriochloa_ischaemum/Bothriochloa_ischaemum8.JPG",
    "Bothriochloa_ischaemum9": "https://www.azgrasses.org/images-grasses/B/Bothriochloa_ischaemum/Bothriochloa_ischaemum9.JPG",
}

def permitted_thayer_kr_anatomy(item: dict, noncommercial: bool) -> bool:
    # Constrain website exception to two authenticated photos, exact taxon,
    # exact original source/permission pages, and the documented creator.
    photo_id = item.get("source_photo_id")
    image = item.get("image_url") or item.get("file")
    return (
        noncommercial
        and item.get("creator") == "Dave Thayer"
        and item.get("license") == THAYER_KR_LICENSE
        and item.get("site_specific_public_permission") == THAYER_KR_PERMISSION
        and item.get("source_page") == THAYER_KR_SOURCE
        and item.get("source_permission_page") == THAYER_KR_PERMISSION_PAGE
        and item.get("license_url") == THAYER_KR_PERMISSION_PAGE
        and item.get("source_taxon_name") == "Bothriochloa ischaemum"
        and photo_id in THAYER_KR_IMAGES
        and image == THAYER_KR_IMAGES.get(photo_id)
    )

def rights(item: dict, noncommercial: bool) -> tuple[bool, str]:
    if permitted_thayer_kr_anatomy(item, noncommercial):
        return True, "Exact Dave Thayer AZ Grasses KR photos: author grants free use; NOT CC"

    if permitted_kava_curly_node(item, noncommercial):
        return True, "Exact John Kava Yavapai educational-use permission with credit; NOT CC"
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
    if permitted_tom_chester_erioneuron(item, noncommercial):
        return True, "Exact Tom Chester hairy tridens credited-reproduction page permission; NOT CC"
    if permitted_harms_dinebra_brachiata_comparison(item, noncommercial):
        return True, "Bob Harms other subspecies brachiata source comparison, exact Selected Monocots educational credit only, NOT CC"
    if permitted_harms_eriochloa_sericea(item, noncommercial):
        return True, "Bob Harms ERSE5-9 exact E. sericea Selected Monocots spikelet original, educational with credit, NOT CC"
    if permitted_harms_kr_spikelets(item, noncommercial):
        return True, "Bob Harms Selected Monocots exact KR spikelets original, scientific/educational with credit, NOT CC"
    if permitted_harms_big_bluestem(item, noncommercial):
        return True, "Bob Harms exact Andropogon gerardii Selected Monocots photo, educational with credit, NOT CC"
    if permitted_harms_hopia(item, noncommercial):
        return True, "Bob Harms exact source Panicum obtusum / accepted Hopia obtusa Selected Monocots, educational credited permission; NOT CC"
    if permitted_harms_disakisperma(item, noncommercial):
        return True, "Bob Harms exact Leptochloa dubia / accepted Disakisperma dubium educational credited originals"
    if permitted_harms_limnodea(item, noncommercial):
        return True, "Copyright Bob Harms exact selected Ozarkgrass originals educational-with-credit, NOT CC"
    if permitted_harms_eleusine_indica(item, noncommercial):
        return True, "Bob Harms exact Eleusine indica original Selected Monocots educational permission with credit (NOT CC)"
    if permitted_harms_elymus_canadensis(item, noncommercial):
        return True, "Bob Harms nine exact Elymus canadensis original Central Texas educational credited photographs; copyrighted NOT CC"
    if permitted_harms_elymus_virginicus(item, noncommercial):
        return True, "Bob Harms exact Elymus virginicus Selected Monocots originals, credited educational reuse NOT CC"
    if permitted_harms_wintergrass(item, noncommercial) or permitted_harms_phalaris(item, noncommercial) or permitted_harms_spva(item, noncommercial) or permitted_harms_little_bluestem(item, noncommercial) or permitted_harms_papu(item, noncommercial) or permitted_harms_spcl(item, noncommercial) or permitted_harms_spco(item, noncommercial):
        return True, "Bob Harms original: source-specific credited scientific/educational permission; NOT CC"
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
    # The Learner no longer has a Photo Lab nav item. The unchanged Field ID
    # and Quiz interfaces do. Remove that private-review link from all three
    # public pages, and never add the Photo Lab route to the public snapshot.
    for name in ("index.html", "field-id.html", "field-id-classic.html", "quiz.html", "quiz-classic.html"):
        page = site / name
        if not page.is_file():
            raise RuntimeError(f"Required public section missing from staged site: {name}")
        html = page.read_text(encoding="utf-8")
        html, _ = re.subn(
            r'<a\s+class="photo-lab-nav"[^>]*>.*?</a>',
            "",
            html,
            flags=re.I | re.S,
        )
        if "photo-lab-nav" in html:
            raise RuntimeError(f"Unremoved Photo Lab navigation on public {name}")
        page.write_text(html, encoding="utf-8")

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

    # Lightweight name index for every public species. Regenerate on each
    # publish so the beginner search automatically includes newly installed
    # species without manually editing the website or canonical records.
    public_names = []
    field_tiles = []
    for species_path in sorted((site / "content" / "taxa").rglob("species.json")):
        sp = json.loads(species_path.read_text(encoding="utf-8"))
        sid = sp.get("id")
        if not isinstance(sid, str) or not sid:
            continue
        public_names.append({
            "id": sid,
            "scientific_name": sp.get("scientific_name") or
                " ".join(str(sp.get(k) or "").strip() for k in ("genus", "species")).strip(),
            "common_name": sp.get("common_name") or "",
            "genus": sp.get("genus") or "",
            "family": sp.get("family") or "",
        })
        # Only use the filtered PUBLIC species JSON and its retained photos.
        # Never pull a thumbnail from pre-filter canonical records, unapproved
        # external references or the private Photo Lab.
        filtered = sp.get("images") if isinstance(sp.get("images"), list) else []
        first = next(
            (img for img in filtered if isinstance(img, dict)
             and isinstance(img.get("file"), str)
             and (species_path.parent / img["file"]).is_file()),
            None,
        )
        thumb = ""
        if first is not None:
            thumb = (species_path.parent / first["file"]).relative_to(site).as_posix()
        field_tiles.append({
            "id": sid,
            "path": species_path.relative_to(site).as_posix(),
            "family": sp.get("family") or "",
            "genus": sp.get("genus") or "",
            "scientific_name": sp.get("scientific_name") or "",
            "common_name": sp.get("common_name") or "",
            "thumbnail": thumb,
            "thumbnail_creator": (first or {}).get("creator") or "",
            "thumbnail_license": (first or {}).get("license") or "",
            "thumbnail_source": (first or {}).get("source_page") or "",
            "photo_count": len(filtered),
            "cue": str(sp.get("look_here_first") or "").strip()[:190],
        })
    (data / "learner-search-index.json").write_text(
        json.dumps({"version": 1, "species": public_names}, ensure_ascii=False,
                   separators=(",", ":")) + "\n", encoding="utf-8"
    )
    tally["learner_search_entries"] = len(public_names)
    # A compact, rights-filtered, photo-enabled tile directory. The Field ID
    # app retrieves full canonical detail only when an individual tile opens.
    (data / "field-id-index.json").write_text(
        json.dumps({"version": 1, "species": field_tiles}, ensure_ascii=False,
                   separators=(",", ":")) + "\n", encoding="utf-8"
    )
    tally["field_id_tile_entries"] = len(field_tiles)

    # The public repository should not run Jekyll on source JSON or asset paths.
    (site / ".nojekyll").write_text("", encoding="utf-8")
    # Force phone home-screen service workers to refresh when published.
    sw = site / "sw.js"
    if sw.is_file():
        # Bust offline cache when layout/code changes even if plant counts do not.
        import hashlib
        digest = hashlib.sha256()
        for page_name in ("index.html", "field-id.html", "field-id-classic.html", "quiz.html", "quiz-classic.html"):
            digest.update((site / page_name).read_bytes())
        digest.update((site / "assets" / "js" / "app.js").read_bytes())
        digest.update((site / "assets" / "js" / "field-id-tiles.js").read_bytes())
        digest.update((site / "assets" / "css" / "field-id-tiles.css").read_bytes())
        digest.update((site / "assets" / "js" / "quiz-tiles.js").read_bytes())
        digest.update((site / "assets" / "css" / "quiz-tiles.css").read_bytes())
        state = (str(tally["approved_photos"]) + "-" +
                 str(tally["species_checked"]) + "-" +
                 digest.hexdigest()[:12])
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
