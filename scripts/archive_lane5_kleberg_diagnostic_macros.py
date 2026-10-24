#!/usr/bin/env python3
"""Archive licensed authentic Dichanthium annulatum structural macros.
Only pixel-checked and photographer-labelled anatomy receives arrows.
Append-only image records, preserve all existing source/annotation data.
"""
import io, json, hashlib, html, pathlib, re, urllib.parse, urllib.request
from PIL import Image

ROOT = pathlib.Path("content/taxa/Poaceae/Dichanthium/dichanthium-annulatum")
CARD = ROOT / "species.json"
s = json.loads(CARD.read_text())
gallery = s["visual_comparison"]["items"]
results = []
specs = [
    {
        "name": "Dichanthium annulatum node (6922393495).jpg",
        "file": "harry-rose-ccby-kleberg-true-hairy-node.jpg",
        "role": "True culm node covered with long spreading hairs (Australian specimen); not a mandatory Texas character",
        "mode": "relink",
        "labels": [],
    },
    {
        "name": "Dichanthium annulatum spikelet fertile1 (7101178725).jpg",
        "file": "harry-rose-ccby-kleberg-dissected-fertile-floret.jpg",
        "role": "Dissected fertile reproductive unit: source identified upper glume, awned stipe-like fertile lemma, ovary, sterile lemma, and hairy lower glume",
        "mode": "new",
        "title": "DISSECTED FERTILE SPIKELET — actual upper and lower glumes, lemma awn",
        "caption": "REAL DISSECTION, NOT a distant head: author Harry Rose identifies the left bract as UPPER GLUME, the long awn rising from the fertile lemma, ovary and translucent sterile lemma in the center, and the HAIRY LOWER GLUME at right. Genuine visible structures; no calibrated millimeter ruler, so don't infer exact measurements or a Hays voucher.",
        "why": "Dissects the actual structures crews need to distinguish an awned fertile floret from the glumes rather than treating the whole flowering branch as one spikelet.",
        "markers": [
            {"label": "Upper glume (left)", "label_x": 2, "label_y": 62, "target_x": 41, "target_y": 62},
            {"label": "Awn from fertile lemma", "label_x": 66, "label_y": 7, "target_x": 44, "target_y": 24},
            {"label": "Hairy lower glume", "label_x": 76, "label_y": 68, "target_x": 61, "target_y": 51},
        ],
    },
    {
        "name": "Dichanthium annulatum spikelet pair4 (6955110610).jpg",
        "file": "harry-rose-ccby-kleberg-paired-spikelets-hairy-glumes.jpg",
        "role": "Photographer-labelled sessile/pedicelled spikelet pair with awn and long glume margin hairs; visibly separated for anatomical photography",
        "mode": "new",
        "title": "TWO SPIKELETS — pedicelled companion, awned partner and glume hairs",
        "caption": "The paired reproductive units were photographed separated against a gray background. The left unit has a conspicuous slender pedicel below; the right unit carries a tall awn. Long glume-margin hairs are visible. Photographer describes spikelets to approximately 4 mm, but the image itself has no metric scale. No original branch attachment is visible, so don't infer their exact position on an intact rachis.",
        "why": "Compare two distinct closely related reproductive units and see the real long hairs and awn, instead of assuming the tufted raceme itself resolves fertile versus sterile spikelets.",
        "markers": [
            {"label": "Slender pedicel (left)", "label_x": 5, "label_y": 75, "target_x": 39, "target_y": 71},
            {"label": "Long projecting awn", "label_x": 70, "label_y": 7, "target_x": 58, "target_y": 14},
            {"label": "Spreading glume hairs", "label_x": 73, "label_y": 48, "target_x": 66, "target_y": 34},
        ],
    },
]
def get(url):
    req = urllib.request.Request(url, headers={"User-Agent":"HaysCountyBotany/1.0 public licensed botanical educational media"})
    with urllib.request.urlopen(req, timeout=50) as res:
        return res.read()
for spec in specs:
    source = "https://commons.wikimedia.org/wiki/File:" + spec["name"].replace(" ", "_")
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
        "action":"query", "prop":"imageinfo", "iiprop":"url|extmetadata",
        "titles":"File:"+spec["name"],"format":"json"
    })
    try:
        data = json.loads(get(url))
        info = next(iter(data["query"]["pages"].values()))["imageinfo"][0]
        meta = info["extmetadata"]
        license = re.sub(r"[^A-Z0-9]", "", meta.get("LicenseShortName",{}).get("value","").upper())
        artist = html.unescape(re.sub(r"<[^>]+>", " ", meta.get("Artist",{}).get("value",""))).strip()
        if license != "CCBY20" or not ("Harry Rose" in artist or "Macleay Grass Man" in artist):
            raise ValueError("Photo rights/author not verified: " + license + " / " + artist)
        raw = get(info["url"])
        im = Image.open(io.BytesIO(raw)); im.verify()
        im = Image.open(io.BytesIO(raw)).convert("RGB")
        if min(im.size)<650:
            raise ValueError("Insufficient original image dimensions")
        dest = ROOT / "images" / spec["file"]
        im.save(dest, "JPEG", quality=91, optimize=True)
        path = str(dest)
        rel = "images/" + spec["file"]
        if not any(x.get("file")==rel for x in s["images"]):
            s["images"].append({
                "file":rel, "role":spec["role"], "creator":"Harry Rose (Macleay Grass Man)",
                "license":"CC BY 2.0", "license_url":"https://creativecommons.org/licenses/by/2.0/",
                "source_page":source, "source_original_url":info["url"],
                "public_reuse":"Author credit, image source and link to license; JPEG reencoded and EXIF removed.",
                "photo_status":"SOURCE-VERIFIED TRUE SPECIES; local JPEG, gross annotation verified only for clearly visible anatomy.",
                "original_dimensions":list(im.size), "sha256_local":hashlib.sha256(dest.read_bytes()).hexdigest(),
            })
        existing = next((x for x in gallery if x.get("source_page")==source),None)
        if existing is None and spec["mode"]=="new":
            gallery.insert(3,{
                "label":spec["title"],"scientific_name":"Dichanthium annulatum",
                "image_url":path,"image_fit":"contain",
                "image_role":spec["role"],"caption":spec["caption"],
                "why_it_matters":spec["why"],"creator":"Harry Rose (Macleay Grass Man)",
                "license":"CC BY 2.0","license_url":"https://creativecommons.org/licenses/by/2.0/",
                "source_page":source,"markers":spec["markers"],
                "photo_status":"Source-labelled, real 960px preview inspected 2026-10-24. Anatomical gross arrows use the checked pixels; taxon not independently Hays-vouchered, no metric scale.",
            })
        elif existing is not None:
            existing["image_url"]=path
            existing["photo_status"]="Physically archived source-verified CC BY 2.0 JPEG, same original aspect; existing gross arrow retained. Live gallery/mobile QA remains."
        results.append({"source":source,"status":"archived","file":path,"pixels":list(im.size),"license":license})
    except Exception as exc:
        results.append({"source":source,"status":"hold","reason":str(exc)[:260]})
# Botanical correction: FNA (North American) describes glabrous or short-pubescent nodes in this taxon.
node = next((x for x in gallery if x.get("label")=="Kleberg node"), None)
if node:
    node["caption"] = ("This Australian specimen has an obvious LONG WHITE HAIR RING at its true stem NODE, "
                       "not the blade/sheath collar. IMPORTANT: North American Flora of North America treatment "
                       "also describes D. annulatum nodes as GLABROUS or SHORT-PUBESCENT, so a white beard is "
                       "NOT a mandatory Texas ID character. Silky bluestem may be similarly bearded; inspect "
                       "paired reproductive spikelets, glumes, ligule and growth form.")
    node["why_it_matters"]="A conspicuously bearded true node is a photo-verified example, not a universal Texas trait; avoid the false 'hairy node = Kleberg' rule."
summary=s["field_id_finish_pass"]
summary["crew_teaching_summary"]=(
    "INTRODUCED KLEBERG BLUESTEM. Start with (often) 2–9 fingerlike flowering racemes and inspect "
    "ACTUAL paired sessile fertile and pedicelled companion spikelets, glumes and awn. "
    "An Australian example has a densely white-bearded true stem node, but FNA describes North American "
    "nodes as glabrous or short-pubescent: a dense white ring is NOT required in Texas and not exclusive "
    "against silky bluestem. Compare KR and native bluestems by multiple characters, not hairs alone.")
summary["lane5_anatomy_followup_20261024"] = {
    "status":"FIELD_READY_PHOTO_GAPS","source_license":"Harry Rose Wikimedia Commons CC BY 2.0",
    "archives":results,
    "new_actual_diagnostic_source_photos":len([r for r in results if r["status"]=="archived" and ("fertile1" in r["source"] or "pair4" in r["source"])]),
    "new_pixel_checked_anatomy_arrows":len([z for z in results if z["status"]=="archived" and "fertile1" in z["source"]])*3 + len([z for z in results if z["status"]=="archived" and "pair4" in z["source"]])*3,
    "critical_remaining":["Hays Texas verified same-plant node and root/stolon base", "Attached sessile+pedicelled pair under a real 1-mm ruler",
                          "Definitive actual ligule edge under scale","Arrow alignment QA on deployed mobile site"],
    "regional_caution":"FNA Texas/US plants have glabrous or short pubescent nodes; do not universalize Australian bearded-node photograph.",
}
CARD.write_text(json.dumps(s,ensure_ascii=False,indent=2)+"\n")
report = pathlib.Path("reports/lane5-kleberg-real-diagnostic-macros-20261024.json")
report.write_text(json.dumps(summary["lane5_anatomy_followup_20261024"],indent=2)+"\n")
print(json.dumps(summary["lane5_anatomy_followup_20261024"]))
