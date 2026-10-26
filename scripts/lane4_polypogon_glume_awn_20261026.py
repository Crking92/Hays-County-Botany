#!/usr/bin/env python3
"""Add one actual detached-spikelet CC BY-SA field macro. Never invent glume/lemma boundaries."""
import hashlib, io, json, pathlib, time, urllib.request
from PIL import Image, ImageOps

root=pathlib.Path("content/taxa/Poaceae/Polypogon/polypogon-monspeliensis")
p=root/"species.json"
d=json.loads(p.read_text(encoding="utf-8"))
assert d["id"]=="polypogon-monspeliensis"
assert d["field_id_finish_pass"]["stage"]=="FIELD_READY_PHOTO_GAPS"

source="https://commons.wikimedia.org/wiki/File:Polypogon_monspeliensis_fruit_(01).jpg"
original="https://upload.wikimedia.org/wikipedia/commons/f/fc/Polypogon_monspeliensis_fruit_%2801%29.jpg"
sha1="f29a04705abcc7ac43275360e2ef72640e44642e"
fname="images/commons-matt-lavin-andrey-zharkikh-fruit-01.jpg"
dest=root/fname
report={"species":"Polypogon monspeliensis","added":[],"held":[],"new_gross_markers":0,
        "source":source,"copyright":"CC BY-SA 2.0 Generic (Flickr source separately reviewed by FlickrReviewR on Commons)",
        "review_date":"2026-10-26"}
if any(x.get("file")==fname for x in d["images"]):
    report["held"].append("Already indexed in canonical species metadata, no duplicate made")
else:
  try:
    req=urllib.request.Request(original,headers={"User-Agent":"HaysBotanyEducationalVisualLearner/1.0 (species-specific rights verified)"})
    blob=None
    for trial in range(3):
        try:
            with urllib.request.urlopen(req,timeout=45) as resp: blob=resp.read(1000000)
            break
        except Exception:
            if trial==2:raise
            time.sleep(4*(trial+1))
    if not(12000<len(blob)<1000000):raise ValueError("Unexpected file size")
    if hashlib.sha1(blob).hexdigest()!=sha1:raise ValueError("Original file checksum differs from source. HOLD")
    Image.open(io.BytesIO(blob)).verify()
    im=ImageOps.exif_transpose(Image.open(io.BytesIO(blob))).convert("RGB")
    if tuple(im.size)!=(792,516):raise ValueError("Unexpected original dimensions")
    if dest.exists():raise ValueError("Refuse to overwrite existing file")
    dest.parent.mkdir(parents=True,exist_ok=True)
    im.save(dest,format="JPEG",quality=94,optimize=True)
    digest=hashlib.sha256(dest.read_bytes()).hexdigest()
    attribution="Andrey Zharkikh (Commons file author); original Flickr upload associated with Matt Lavin — credit both because source attribution is inconsistent"
    d["images"].append({
      "file":fname,
      "role":"Genuine original species-captioned photograph of loosened separate reproductive units and conspicuously long thin awns; NOT an isolated microscope-verified lemma",
      "creator":attribution,
      "license":"CC BY-SA 2.0",
      "license_url":"https://creativecommons.org/licenses/by-sa/2.0/",
      "source_page":source,
      "source_image":original,
      "original_sha1":sha1,
      "archived_sha256":digest,
      "public_reuse":"Attribution, license link, re-encoding change notice; any distributed adaptations must respect ShareAlike",
      "modifications":"RGB JPEG recompressed with EXIF/GPS metadata excluded; labels are a separate webpage overlay",
      "photo_status":"SOURCE LICENSE AND REAL PIXELS VERIFIED. Detached awned units visible; glume notch, true awn insertion and lemma organ identity NOT micromorphologically established."
    })
    photo={
      "label":"Annual beardgrass — detached spikelets with unusually long awns",
      "scientific_name":"Polypogon monspeliensis",
      "image_url":str(dest).replace("\\","/"),
      "image_fit":"contain",
      "image_role":"TRUE photographed separated reproductive structures on dark green background: multiple tan-green narrow spikelet-scale bodies and exceptionally long fine awns; glumes, lemma and notches not separately resolved at this resolution",
      "caption":"Real sourced photograph shows widely separated small pointed green-brown reproductive units and very long thin pale awns, including two long awned structures near the left of the frame. It makes the awns' enormous length relative to tiny spikelet bodies easy to learn. Pixel resolution is insufficient to identify the notch of each individual glume or distinguish the inner lemma from a glume. Don't confuse this with Setaria's sterile-branch bristles.",
      "why_it_matters":"Unlike a whole fuzzy bottlebrush, this gets close to the actual reproductive units and makes the long-awns-versus-small-spikelets clue visible. The definitive proof of TWO notched awned glumes plus smaller fertile lemma still needs a better dissected macro.",
      "creator":attribution,
      "license":"CC BY-SA 2.0",
      "license_url":"https://creativecommons.org/licenses/by-sa/2.0/",
      "source_page":source,
      "modifications":"Original CC BY-SA image re-encoded EXIF-free; only visible whole-unit and long-awn overlay arrows",
      "markers":[
        {"label":"Very long fine awn","label_x":69,"label_y":6,"target_x":45,"target_y":6},
        {"label":"Tiny reproductive unit","label_x":73,"label_y":81,"target_x":82,"target_y":47},
        {"label":"Separated awned unit","label_x":4,"label_y":69,"target_x":24,"target_y":42}
      ],
      "photo_status":"Original JPEG visually inspected 2026-10-26, exact Commons SHA-1 confirmed before archive, 3 visible-only arrows. No lower versus upper glume, notch, lemma or length falsely annotated. Author credit ambiguity documented."
    }
    # Put the diagnostically closer reproductive photograph ahead of general seedhead views.
    d["visual_comparison"]["items"].insert(0,photo)
    d["curation_status"]["photo_metadata_count"]=len(d["images"])
    d["curation_status"]["photo_files_present"]=sum((root/x["file"]).is_file() for x in d["images"])
    d["curation_status"]["photo_panels"]=len(d["visual_comparison"]["items"])
    d["curation_status"]["gross_visible_arrows"]=sum(len(x.get("markers",[])) for x in d["visual_comparison"]["items"])
    d["learner_visual_status"]["image_count"]=len(d["images"])
    d["field_id_finish_pass"]["visible_structure_arrows"]=d["curation_status"]["gross_visible_arrows"]
    d["field_id_finish_pass"]["lane4_reproductive_macro_20261026"]={
      "stage":"FIELD_READY_PHOTO_GAPS",
      "new_public_macro_photos":1,
      "new_visible_only_arrows":3,
      "archive_source_sha1":sha1,
      "actual_local_photos":d["curation_status"]["photo_files_present"],
      "visible_public_gallery_panels":len(d["visual_comparison"]["items"]),
      "confirmed_reproductive_details":["separate minute green-tan reproductive units","long pale threadlike awns visibly exceeding their small spikelet-scale bodies"],
      "NOT_confirmed":["two individually separated notched glumes on SAME SPIKELET","which long awn is inserted in which glume notch","fertile lemma body and any shorter lemma awn","calibrated glume and lemma length"],
      "photo_reuse":"CC BY-SA 2.0; dual credit records publisher discrepancy on Wikimedia Commons",
      "future_highest_priority":"Sharp microscope photo with both glumes opened and notch-to-awn insertion traced; measured lemma shown alongside",
      "site_QA":"not independently verified"
    }
    d["visual_comparison"]["subtitle"]="NEW real detached spikelet/long-awn source photograph first, two public CC BY collar photos and existing field head/habit images after; definitive double notched-glume and fertile-lemma dissections still missing. License holds preserved."
    d["photo_note"]+=" 2026-10-26 Lane 4 second reproductive pass added physically archived CC BY-SA 2.0 detached awned spikelet photo, 3 gross visible arrows, no unsupported glume notch/lemma identifications."
    p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    report["added"].append({"source":source,"local":str(dest),"sha256":digest,"pixel_dimensions":list(im.size),"gallery_panels_added":1,"markers_added":3})
    report["new_gross_markers"]=3
  except Exception as e:
    if dest.exists() and not any(x.get("file")==fname for x in d["images"]):dest.unlink()
    report["held"].append(str(e))
path=pathlib.Path("reports/lane4-polypogon-spikelet-20261026.json")
path.parent.mkdir(exist_ok=True)
path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps(report))
