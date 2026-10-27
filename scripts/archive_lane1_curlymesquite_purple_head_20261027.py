#!/usr/bin/env python3
"""Add licensed close-up of attached purplish Hilaria belangeri reproductive groups.

Never use this picture as the true ligule, a separated sexed triad or measured glumes.
"""
import io
import json
from pathlib import Path
import time
import urllib.request
from PIL import Image

base = Path("content/taxa/Poaceae/Hilaria/hilaria-belangeri")
card = base / "species.json"
dst = base / "images" / "patrick-alexander-curlymesquite-purple-attached-head-cc0.jpg"
source_page = "https://commons.wikimedia.org/wiki/File:Hilaria_belangeri_-_Flickr_-_aspidoscelis_(4).jpg"
source_original = "https://upload.wikimedia.org/wikipedia/commons/2/2f/Hilaria_belangeri_-_Flickr_-_aspidoscelis_%284%29.jpg"
sp = json.loads(card.read_text(encoding="utf-8"))
assert sp["id"] == "hilaria-belangeri"
if any(p.get("file") == "images/" + dst.name for p in sp.get("images", [])) and dst.is_file():
    print("Already archived. Nothing to change.")
    raise SystemExit(0)
assert not dst.exists(), "Existing unmatched bytes at target image path"
source = None
for attempt in range(4):
    try:
        req = urllib.request.Request(source_original, headers={"User-Agent": "HaysBotanyCrewLearner/1.0 (licensed public teaching photo)"})
        with urllib.request.urlopen(req, timeout=60) as response:
            source = response.read()
        break
    except Exception as exc:
        print("Source fetch attempt", attempt+1, str(exc), flush=True)
        if attempt == 3:
            raise
        time.sleep(8*(attempt+1))
assert source and 20000 < len(source) < 12000000, "unexpected file size"
im = Image.open(io.BytesIO(source))
im.load()
assert im.format == "JPEG" and im.width >= 1500 and im.height >= 1000, "Unusable image resolution"
size = [im.width, im.height]
if im.width > 2500:
    im.thumbnail((2500, 2500), Image.Resampling.LANCZOS)
dst.parent.mkdir(parents=True, exist_ok=True)
im.convert("RGB").save(dst, "JPEG", quality=90, optimize=True)  # strips EXIF, GPS and camera location
img = {
    "file": "images/" + dst.name,
    "role": "Real close-up of purple-red attached curlymesquite flowering groups; reproductive stage before pale papery shattering; no measurable split glumes or individual sexed spikelets",
    "creator": "Patrick Alexander",
    "license": "CC0 1.0",
    "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
    "source_page": source_page,
    "source_original": source_original,
    "source_taxon_name": "Hilaria belangeri",
    "source_region": "Owl Canyon, Hidalgo County, New Mexico (2014-11-23). Not a Texas voucher.",
    "source_license_note": "Wikimedia Commons individual file page confirms Flickr review of CC0",
    "photo_review": "Source original independently pixel-inspected: narrow continuous inflorescence axis with successive tight reddish flowering groups; no visible inner blade-sheath junction, rooted stolon node, sexed central vs lateral member or mm ruler.",
    "image_dimensions_original": size,
    "public_reuse": "CC0; creator and Commons original still voluntarily credited",
    "modifications": "resized and recompressed GPS/EXIF-free JPEG",
}
sp.setdefault("images", []).append(img)
panel = {
    "label": "ATTACHED PURPLE FLOWERING UNITS — real curlymesquite reddish head (Patrick Alexander)",
    "scientific_name": "Hilaria belangeri",
    "image_url": str(dst).replace("\\", "/"),
    "image_fit": "contain",
    "creator": "Patrick Alexander",
    "license": "CC0 1.0",
    "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
    "source_page": source_page,
    "image_role": "Tightly attached purple-red reproductive units arranged successively on a narrow spike-like flowering axis, earlier stage than papery open pale groups.",
    "caption": "Actual curlymesquite flowering head in Hidalgo County, New Mexico. Look at the successive reddish intact flowering groups on a slender axis; compare with the already archived mature pale clusters and detached papery units. No exact individual three-spikelet boundary or underlying true ligule can be concluded here.",
    "why_it_matters": "Adds a distinct attached reddish flowering stage so crew members do not expect all curlymesquite heads to be pale, opened or disarticulated.",
    "markers": [
        {"label": "Attached purple-red flowering group", "label_x": 1, "label_y": 17, "target_x": 36, "target_y": 26},
        {"label": "Successive flowering groups on axis", "label_x": 66, "label_y": 81, "target_x": 33, "target_y": 59}
    ],
    "photo_status": "Actual original image pixel-reviewed: arrows on plainly visible complete flower groups only, not claims about internal spikelet sexes or diagnostic ligule. Live Pages arrow QA pending."
}
vc=sp.setdefault("visual_comparison",{})
panels=vc.setdefault("items",[])
assert not any(x.get("image_url") == panel["image_url"] for x in panels), "Duplicate visual panel"
where=next((i for i, p in enumerate(panels) if p.get("scientific_name") != "Hilaria belangeri"),len(panels))
panels.insert(where, panel)
sp.setdefault("curation_status", {})["lane1_curlymesquite_early_purple_reproductive_20261027"] = "TRUE_CC0_ATTACHED_PURPLE_FLOWERING_HEAD_ADDED_NO_LIGULE_CLAIM"
sp["curation_status"]["photo_files_present"] = len(sp["images"])
sp.setdefault("learner_visual_status",{})["image_count"] = len(sp["images"])
sp["photo_note"] = sp.get("photo_note","") + " 2026-10-27: Patrick Alexander CC0 New Mexico 2014 attached purple-red reproductive macro added; actual gross flowering groups visible, no true ligule or triad split established."
card.write_text(json.dumps(sp,ensure_ascii=False,indent=2)+"\n", encoding="utf-8")
print(json.dumps({"source":source_page,"photo":str(dst),"original_size":size,"stored_images":len(sp["images"]),"teaching_panels":len(panels),"arrow_count":len(panel["markers"])}))
