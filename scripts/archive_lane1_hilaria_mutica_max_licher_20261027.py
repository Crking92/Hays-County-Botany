#!/usr/bin/env python3
"""Archive one genuine CC BY-SA Hilaria mutica flowering-head photo, never an invented ligule."""
import io, json, pathlib, time, urllib.request
from PIL import Image

ROOT = pathlib.Path("content/taxa/Poaceae/Hilaria/hilaria-mutica")
CARD = ROOT / "species.json"
NAME = "max-licher-tobosa-attached-flowering-fans-cc-by-sa.jpg"
IMAGE = ROOT / "images" / NAME
SOURCE_PAGE = "https://yavapaiplants.extension.arizona.edu/pleuraphis-mutica"
SOURCE_IMAGE = "https://yavapaiplants.extension.arizona.edu/sites/default/files/styles/yp_card_image/public/Grasses/Images/Hilaria_mutica_F_web_N0057.jpg.webp?itok=B-4TMjnW"
LICENSE = "CC BY-SA"
CREATOR = "Max Licher"
data = json.loads(CARD.read_text(encoding="utf-8"))
assert data["id"] == "hilaria-mutica"
if IMAGE.exists() and any(x.get("file") == "images/" + NAME for x in data.get("images", [])):
    print("Already installed; no duplicate")
    raise SystemExit(0)

raw = None
for attempt in range(3):
    try:
        request = urllib.request.Request(SOURCE_IMAGE, headers={"User-Agent": "Mozilla/5.0 (HaysBotany licensed botanical field learner)"})
        with urllib.request.urlopen(request, timeout=45) as response:
            raw = response.read()
        break
    except Exception as exc:
        print("Source retry", attempt+1, str(exc), flush=True)
        if attempt == 2:
            raise
        time.sleep(8*(attempt+1))
assert raw and len(raw) > 15000 and len(raw) < 13000000, "Unexpected photo payload"
im = Image.open(io.BytesIO(raw))
im.load()
assert im.width >= 480 and im.height >= 350, "Photo does not meet macro-view minimum resolution"
assert im.format in ("WEBP", "JPEG", "PNG"), "Unsupported image type"
im = im.convert("RGB")
IMAGE.parent.mkdir(parents=True, exist_ok=True)
im.save(IMAGE, "JPEG", quality=94, optimize=True)  # no EXIF or GPS saved
item = {
    "file": "images/" + NAME,
    "role": "Genuine source-labelled Tobosa attached flowering-head macro: pale fan-shaped projecting papery glume lobes on true reproductive axis. Does not expose three sexed members or a ligule.",
    "creator": CREATOR,
    "license": LICENSE,
    "license_version_note": "University of Arizona image-level caption explicitly says CC BY-SA without a version; preserve source wording.",
    "source_page": SOURCE_PAGE,
    "source_original": SOURCE_IMAGE,
    "source_taxon_name": "Pleuraphis mutica (syn. Hilaria mutica)",
    "photo_review": "Original 640x480 source visually inspected 2026-10-27. Pale splaying papery fans and attached flowering axis actually visible. No central/lateral sexing, membranous ligule, sheath junction, subterranean rhizome or scale asserted.",
    "public_reuse": "Credit Max Licher, CC BY-SA; preserve same license attribution for adapted copies.",
    "modifications": "WEBP source converted to GPS/EXIF-free JPEG",
    "image_dimensions": [im.width, im.height]
}
data.setdefault("images", []).append(item)
panel = {
    "label": "TOBOSA MATURING HEAD — real fan-shaped papery lobes attached to flowering axis (Max Licher)",
    "scientific_name": "Hilaria mutica",
    "image_url": str(IMAGE).replace("\\","/"),
    "image_fit": "contain",
    "image_role": "Exact-species growing reproductive head with attached pale, broad fanlike floral bracts; no sexed triad assignment or scale.",
    "creator": CREATOR,
    "license": LICENSE,
    "source_page": SOURCE_PAGE,
    "caption": "Max Licher's actual tobosa head shows pale flaring fan-shaped papery glumelike structures on a continuous flowering axis. Contrast the projecting fan contours against the softer, denser head. The exact separate three spikelets within any single cluster are NOT labelled, and no inner collar or ligule appears.",
    "why_it_matters": "A real close flowering view makes tobosa's broad papery flowering structures accessible in the field, complementing the separate detached fascicle and overall plant photos without fabricating an anatomical dissection.",
    "markers": [
        {"label": "Real fan-shaped pale floral lobes", "label_x": 3, "label_y": 10, "target_x": 49, "target_y": 34},
        {"label": "Attached flowering axis", "label_x": 70, "label_y": 82, "target_x": 49, "target_y": 68}
    ],
    "photo_status": "Same-species true photograph pixel reviewed at source display; arrows identify only gross plainly visible lobes/axis. Actual website alignment, sexed triad/glume dissection and true ligule remain open."
}
gallery=data.setdefault("visual_comparison",{}).setdefault("items",[])
if not any(x.get("image_url") == panel["image_url"] for x in gallery):
    first_compare=next((i for i,x in enumerate(gallery) if x.get("scientific_name") != "Hilaria mutica"),len(gallery))
    gallery.insert(first_compare,panel)
data.setdefault("curation_status",{})["photo_files_present"] = len(data["images"])
data["curation_status"]["lane1_tobosa_attached_fans_20261027"] = "ONE_ACTUAL_CC_BY_SA_FLOWERING_MACRO_ADDED_TRUE_LIGULE_STILL_OPEN"
data.setdefault("learner_visual_status",{})["image_count"] = len(data["images"])
data["photo_note"] = data.get("photo_note","") + " 2026-10-27: Max Licher actual attached papery fan-shaped flowering head photo archived with original University of Arizona CC BY-SA caption and two visible gross arrows; ligule and sexed three-member fascicle still unresolved."
CARD.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"archived":str(IMAGE),"size":[im.width,im.height],"source":SOURCE_PAGE,"rights":LICENSE,"gallery":len(gallery),"species_photos":len(data["images"])}))
