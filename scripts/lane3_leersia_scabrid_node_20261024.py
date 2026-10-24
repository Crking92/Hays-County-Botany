#!/usr/bin/env python3
"""Lane 3: install exact-source CC BY-SA Leersia sheath/node/spikelet photos.

Record only anatomy visible in source captions, not pixel-certified marker positions.
Do not republish the study-only Joey Santore frame.
"""
import hashlib
import io
import json
import pathlib
import time
import urllib.error
import urllib.parse
import urllib.request
from PIL import Image, ImageOps

root = pathlib.Path("content/taxa/Poaceae/Leersia/leersia-oryzoides")
card = root / "species.json"
d = json.loads(card.read_text())
assert d["id"] == "leersia-oryzoides"

selected = {
  21: ("hairy stem node (source-labelled); not leaf-margin retrorse teeth", "Hairy-node ring; do not place a true ligule label"),
  22: ("recurved barbs on actual leaf SHEATH surface, not the blade margin", "Sheath surface macro; leaf-margin spinules remain a separate photo gap"),
  31: ("opened real spikelet with internal floret views, not calibrated lemma/glume lengths", "Opened spikelet; no tiny anatomy arrow without pixel review"),
}
report = {"species": "leersia-oryzoides", "added": [], "holds": [], "reused": [], "source_author": "Stefan.lefnaer", "restricted_study_only_frame_not_copied": True}

def request(url):
    req = urllib.request.Request(url, headers={"User-Agent":"HaysBotanyVisualLearner/1.0 (licensed educational archive; github.com/Crking92/Hays-County-Botany)"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=38) as response:
                return response.read(16_000_001)
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == 2:
                raise
            time.sleep(8 * (attempt + 1))

for n, (role, caution) in selected.items():
    name = f"Leersia oryzoides sl{n}.jpg"
    source = f"https://commons.wikimedia.org/wiki/File:Leersia_oryzoides_sl{n}.jpg"
    try:
        matches = [x for x in d["images"] if x.get("source_page") == source]
        if len(matches) != 1:
            raise ValueError("canonical source mismatch")
        row = matches[0]
        if row["file"].startswith("images/"):
            report["reused"].append({"source":source,"local":row["file"]})
            continue
        api = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
            "action":"query","format":"json","prop":"imageinfo",
            "iiprop":"url|extmetadata","titles":"File:"+name,
        })
        dat = json.loads(request(api))
        info = next(iter(dat["query"]["pages"].values()))["imageinfo"][0]
        lic = info["extmetadata"].get("LicenseShortName",{}).get("value","")
        artist = info["extmetadata"].get("Artist",{}).get("value","")
        if "CC BY-SA 4.0" not in lic or "Stefan" not in artist:
            raise ValueError(f"photo author/license hold: {lic}; {artist[:90]}")
        blob0 = request(info["url"])
        with Image.open(io.BytesIO(blob0)) as im:
            im.verify()
        with Image.open(io.BytesIO(blob0)) as im:
            im = ImageOps.exif_transpose(im).convert("RGB")
            if min(im.size) < 400:
                raise ValueError("under-resolution for macro archive")
            size_original=list(im.size)
            im.thumbnail((2100,2100))
            out=io.BytesIO()
            im.save(out,"JPEG",quality=90,optimize=True)
            blob=out.getvalue()
        rel=f"images/stefan-lefnaer-sl{n}-cc-by-sa4.jpg"
        target=root/rel
        if target.exists():
            raise ValueError("existing local photo protected, no overwrite")
        target.write_bytes(blob)
        original=row["file"]
        row["file"]=rel
        row["original_media_url"]=info["url"]
        row["sha256"]=hashlib.sha256(blob).hexdigest()
        row["image_dimensions_original"]=size_original
        row["role"]=role
        row["source_detail_caution"]=caution
        row["photo_review"]="Exact species/rights archive verified; markers held until original-pixel anatomical QA; no metric ruler certified"
        row["modifications"]="JPEG re-encode resized and EXIF removed; CC BY-SA 4.0 and photographer retained"
        for panel in d["visual_comparison"]["items"]:
            if panel.get("image_url")==original:
                panel["image_url"]=str(root/rel)
                panel["photo_status"]="ARCHIVED_EXACT_SOURCE_CC_BY_SA_4; anatomical arrows need pixel inspection"
                panel["markers"]=panel.get("markers",[])
                panel["source_detail_caution"]=caution
        report["added"].append({"source":source,"file":str(target),"size":len(blob),"license":lic,"sha256":row["sha256"]})
    except Exception as e:
        report["holds"].append({"source":source,"reason":str(e)[:270]})

if report["added"]:
    d["curation_status"]["photo_files_present"]=sum(x.get("file","").startswith("images/") for x in d["images"])
    d["curation_status"]["photo_metadata_count"]=len(d["images"])
    d.setdefault("learner_visual_status",{})["status"]="FIELD_READY_PHOTO_GAPS"
    d["learner_visual_status"]["image_count"]=len(d["images"])
    d["learner_visual_status"]["note"]="Eight or fewer local images now reflect verified downloads; noncommercial study frame excluded from public rights count. True blade-edge retrorse spinules with metric ruler and rooted rhizome still missing."
    d["lane3_fine_detail_pass_20261024"]={
      "stage":"FIELD_READY_PHOTO_GAPS",
      "archived_roles":[x["source"] for x in report["added"]],
      "photo_evidence_hold":"Actual rough SHEATH microphoto is NOT the backward-pointing BLADE MARGIN macro; do not interchange",
      "what_still_needs_photography":[
        "True leaf BLADE-margin retrorse microscopic teeth with 1-mm scale",
        "Actual mature 4–7 mm spikelet photographed with calibrated scale and glume reduction",
        "Connected belowground rhizome and rooted lower node (permitted excavation only)",
        "Lowest primary panicle branching node with all branches in focus"],
      "licensed_source_rule":"Stefan.lefnaer CC BY-SA 4.0 attribution retained; Joey Santore study-only frame must not be promoted as unrestricted public.",
      "annotation_rule":"No new precise arrows; photos require pixel inspection before anatomical markers."
    }
    card.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
pathlib.Path("reports/lane3-leersia-fine-anatomy-20261024.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
