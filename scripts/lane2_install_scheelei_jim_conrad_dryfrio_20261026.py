#!/usr/bin/env python3
"""Add two Jim Conrad PUBLIC DOMAIN exact-species field photographs from Uvalde County.
Creator policy https://www.backyardnature.net/j/copyrite.htm expressly releases his
own photos; the original 2013 Dry Frio naturalist article is his, with no other photo credit.
"""
import hashlib
import io
import json
from pathlib import Path
from urllib.request import urlopen, Request

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "content/taxa/Poaceae/Setaria/setaria-scheelei/species.json"
IMAGES = CARD.parent / "images"
REPORT = ROOT / "reports/lane2-scheelei-jim-conrad-dryfrio-public-domain-photos-20261026.json"
SOURCE_PAGE = "https://www.backyardnature.net/n/h/scheelei.htm"
RIGHTS_PAGE = "https://www.backyardnature.net/j/copyrite.htm"
PREFIX = "content/taxa/Poaceae/Setaria/setaria-scheelei/images/"
ASSETS = [
    {
        "src": "https://www.backyardnature.net/n/13/130908st.jpg",
        "name": "jim-conrad-dry-frio-whole-plant-habitat-2013.jpg",
        "label": "UVALDE COUNTY · living plant in Dry Frio rocky gulley habitat",
        "role": "Field plant with attached flowering heads and living foliage above ground; roots and rhizomes NOT exposed",
        "caption": "Jim Conrad photographed actual Southwestern/Scheele's bristlegrass beside the Dry Frio River in northern Uvalde County in September 2013. Look for slender tapered flowering heads attached to leafy culms in rocky, partly shaded habitat. Multiple grasses share the scene: do not infer that every green blade belongs to this one specimen. The root system and true ligule are hidden.",
        "why": "A genuine southwest-central-Texas habitat photograph rather than a plant in a nursery; demonstrates attached head and leaf-bearing field growth.",
        "markers": []
    },
    {
        "src": "https://www.backyardnature.net/n/13/130908su.jpg",
        "name": "jim-conrad-dry-frio-green-spikelets-long-bristles-2013.jpg",
        "label": "UVALDE COUNTY · actual attached green spikelets and projecting bristles",
        "role": "Close view of several pale elliptic spikelets and distinct long projecting sterile bristles, attached to tapered panicle; without mm scale",
        "caption": "Original Jim Conrad close photograph of the same north-Uvalde Setaria scheelei population: elongated pale-green spikelets sit on a branched axis with many long threadlike projecting bristles. The bristles are reduced sterile branchlets, not lemma awns. These clear structures help crew compare foxtails. No 1-mm scale or peeled ligule is present; do NOT derive numerical length or exact per-spikelet bristle counts from this image.",
        "why": "Real attached spikelets and long distinct sterile bristles provide more useful diagnostic detail than only a distant bottlebrush silhouette.",
        "markers": [
            {"label":"Pale elongated spikelet","label_x":70,"label_y":67,"target_x":43,"target_y":42},
            {"label":"Long projecting bristles (not lemma awns)","label_x":39,"label_y":5,"target_x":60,"target_y":30}
        ]
    }
]
UA = {"User-Agent": "HaysCountyBotanyVisualLearner/1.0 (Jim Conrad own photo public domain Uvalde botanical education)"}

def fetch(url):
    with urlopen(Request(url,headers=UA),timeout=50) as handle:
        out=handle.read(5_000_001)
    if len(out)>5_000_000:
        raise RuntimeError("Oversized unsafe image")
    return out

def verify_rights():
    rights=fetch(RIGHTS_PAGE).decode("utf-8",errors="replace").lower()
    page=fetch(SOURCE_PAGE).decode("utf-8",errors="replace").lower()
    # HTML line wraps and inline <strong> formatting break an otherwise exact visible sentence.
    import re, html
    rights_visible = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", rights))).strip()
    found={"public domain": "public domain" in rights_visible, "jim conrad": "jim conrad" in rights_visible, "all images produced by myself": "all images produced by myself" in rights_visible}
    print("RIGHTS_PAGE_CHECK", json.dumps(found), "chars", len(rights), "snippet", repr(rights[:1000]))
    if not all(found.values()):
        raise RuntimeError("Rights evidence not found; stop without downloading images")
    assert "jim conrad" in page and "setaria scheelei" in page and "uvalde" in page
    assert "130908st.jpg" in page and "130908su.jpg" in page
    # Fail rather than infer rights for a specifically credited alternate photographer
    for phrase in ["photo by someone else", "photo by another", "courtesy of", "photographed by"]:
        if phrase in page:
            raise RuntimeError("Page includes third-party photo attribution; manual inspection needed")
    return True

def main():
    verify_rights()
    card=json.loads(CARD.read_text())
    assert card["scientific_name"]=="Setaria scheelei"
    existing_urls={p["image_url"] for p in card["visual_comparison"]["items"]}
    if all(PREFIX+a["name"] in existing_urls for a in ASSETS):
        print("Already installed: no changes")
        return
    new_meta=[]
    panels=[]
    for a in ASSETS:
        rel=PREFIX+a["name"]
        if rel in existing_urls:
            raise RuntimeError("Partial prior install; manual review required")
        raw=fetch(a["src"])
        with Image.open(io.BytesIO(raw)) as im:
            if im.format not in {"JPEG","PNG"}:
                raise RuntimeError("unexpected file format")
            im=ImageOps.exif_transpose(im).convert("RGB")
            dims=list(im.size)
            if min(dims)<400:
                raise RuntimeError(f"source resolution too small: {dims}")
            # Strip all EXIF/GPS and metadata; separate overlay arrows are not embedded.
            output=io.BytesIO()
            im.save(output,format="JPEG",quality=91,optimize=True)
        b=output.getvalue()
        if not b.startswith(b"\xff\xd8") or not b.endswith(b"\xff\xd9"):
            raise RuntimeError("JPEG encoding/EOI verification failed")
        path=IMAGES/a["name"]
        if path.exists():
            raise RuntimeError(f"Unreviewed conflicting path {path}")
        path.write_bytes(b)
        entry={
          "file":"images/"+a["name"],"role":a["role"],
          "creator":"Jim Conrad",
          "license":"Public domain — photographer Jim Conrad's explicit own-image dedication",
          "license_url":RIGHTS_PAGE,"source_page":SOURCE_PAGE,"source_image_url":a["src"],
          "public_reuse":"yes — author-produced image expressly dedicated to public domain",
          "modifications":"Rotated per EXIF if needed and saved clean RGB JPEG without EXIF/GPS; separate browser annotations; original not inlined",
          "photo_status":"Author-owned exact-species Dry Frio Uvalde original field photo; pixels visually assessed for gross flowering/field structures; no root/ligule/mm-scale claim"
        }
        card["images"].append(entry)
        panel={
          "label":a["label"],"scientific_name":"Setaria scheelei",
          "image_url":rel,"image_fit":"contain","image_role":a["role"],
          "caption":a["caption"],"why_it_matters":a["why"],"creator":"Jim Conrad",
          "license":"Public domain — Jim Conrad own-image dedication","license_url":RIGHTS_PAGE,
          "source_page":SOURCE_PAGE,"source_image_url":a["src"],
          "public_reuse":"yes — public domain own-image dedication",
          "markers":a["markers"],
          "photo_status":"Real photo of original author's Uvalde County 2013 grass; pointers on plainly visible large organs only. No millimeter calibration. Original source diagnosis retained as author's determination, not DNA voucher.",
          "modifications":"Clean EXIF/GPS-free re-encoded JPEG; browser overlay arrows only",
          "verification":{"source_dimensions_px":dims,"reencoded_bytes":len(b),
                          "sha256":hashlib.sha256(b).hexdigest(),"origin":a["src"]}
        }
        panels.append(panel)
        new_meta.append({"path":rel,"dimensions":dims,"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest(),
                         "source_photo":a["src"],"markers":len(a["markers"])})
    # Put same-species habitat + close photo before the separate-species lookalike panels.
    index=next((i for i,p in enumerate(card["visual_comparison"]["items"]) if p.get("scientific_name")!="Setaria scheelei"),len(card["visual_comparison"]["items"]))
    card["visual_comparison"]["items"][index:index]=panels
    card["visual_comparison"]["subtitle"] = (
      "Five physically archived source-labelled Scheele's bristlegrass photos, including Jim Conrad's "
      "explicitly public-domain Uvalde County habit and green spikelet/bristle close-ups, credited Kyla "
      "Miller NC photograph and existing Commons views; three separately labeled look-alikes. "
      "Real connected rhizomes, opened true ligule and calibrated basal bristle attachment still missing.")
    card["photo_note"] += (
       "\n2026-10-26: Lane 2 archived TWO Jim Conrad individually author/public-domain "
       "Uvalde County field photographs from original 2013 Dry Frio article, preserving "
       "two justifiable gross bristle/spikelet arrows on closeup, zero arrows on ambiguous "
       "multi-species habitat. Roots/rhizomes and real inner ligule remain missing.")
    c=card["curation_status"]
    c["lane2_scheelei_jim_conrad_dryfrio_20261026"]={
       "state":"FIELD_READY_PHOTO_GAPS",
       "public_domain_original_photo_count_added":2,
       "archived_exact_species_photos":5,
       "same_species_teaching_panels":5,
       "lookalike_panels":3,
       "new_markers":2,
       "source_locality":"Dry Frio River northern Uvalde County, Texas",
       "rights_page":RIGHTS_PAGE,
       "provenance":"2013 Jim Conrad original naturalist newsletter",
       "not_yet_shown":["excavated connected rhizome","peeled true ligule with mm scale","bristle/spikelet insertion with mm scale"],
       "publish":"Pending rights-filtered Pages validation"
    }
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps({
      "status":"FIELD_READY_PHOTO_GAPS",
      "source_page":SOURCE_PAGE,"copyright_dedication":RIGHTS_PAGE,
      "photographer":"Jim Conrad","date":"2013 September",
      "species":"Setaria scheelei","locality":"Uvalde County, Texas",
      "photos":new_meta,"photos_added":2,"new_arrows":2,
      "new_true_ligules":0,"new_exposed_root_systems":0,
      "source_credit_rule":"Explicit Jim Conrad-produced images are public domain; third party excluded",
      "public_website_deployment":"unverified"
    },indent=2)+"\n")
    CARD.write_text(json.dumps(card,indent=2,ensure_ascii=False)+"\n")
    print("SAVED",json.dumps(new_meta), "status FIELD_READY_PHOTO_GAPS")

if __name__ == "__main__":
    main()
