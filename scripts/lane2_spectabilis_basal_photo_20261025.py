#!/usr/bin/env python3
"""Lane 2: one rights-verified purple lovegrass basal-leaf photograph."""
from __future__ import annotations
import hashlib
import io
import json
from pathlib import Path
from urllib.request import Request, urlopen
from PIL import Image, ImageOps

ROOT=Path("content/taxa/Poaceae/Eragrostis/eragrostis-spectabilis")
CARD=ROOT/"species.json"
OUT=ROOT/"images"/"david-stang-basal-blades-5zz.jpg"
REPORT=Path("reports/lane2-purple-lovegrass-basal-leaves-20261025.json")
SOURCE="https://commons.wikimedia.org/wiki/File:Eragrostis_spectabilis_5zz.jpg"
IMAGE="https://upload.wikimedia.org/wikipedia/commons/0/09/Eragrostis_spectabilis_5zz.jpg"
LICENSE="CC BY-SA 4.0"
CREATOR="David J. Stang"

def main():
    doc=json.loads(CARD.read_text(encoding="utf-8"))
    assert doc["id"]=="eragrostis-spectabilis"
    # Canonical photo provenance, separately inspected from the Commons file page:
    # David J. Stang, source-identified Eragrostis spectabilis, CC BY-SA 4.0.
    req=Request(IMAGE,headers={"User-Agent":"Hays-Botany-Learner/1.0 (CC-BY-SA educational archive)"})
    with urlopen(req,timeout=35) as resp:
        assert resp.url.startswith("https://upload.wikimedia.org/")
        data=resp.read(5_000_001)
    assert len(data) in range(200_000,5_000_001), "Unexpected image byte count"
    with Image.open(io.BytesIO(data)) as raw:
        assert raw.format=="JPEG" and raw.size==(1000,667), "Source image changed: hold"
        im=ImageOps.exif_transpose(raw).convert("RGB")
        bio=io.BytesIO()
        im.save(bio,format="JPEG",quality=88,optimize=True)
    clean=bio.getvalue()
    assert clean.startswith(b"\xff\xd8") and b"Exif" not in clean[:200], "Failed EXIF strip"
    OUT.parent.mkdir(parents=True,exist_ok=True)
    if OUT.exists():
        assert hashlib.sha256(OUT.read_bytes()).hexdigest()==hashlib.sha256(clean).hexdigest(), "Existing photo differs: stop"
    else:
        OUT.write_bytes(clean)
    rel="images/"+OUT.name
    if not any(row.get("file")==rel for row in doc["images"]):
        doc["images"].append({
            "file":rel,
            "role":"Real basal leafy clump, many arching/sheathing blades and reddish stems — NO exposed true ligule or root system",
            "creator":CREATOR,
            "license":LICENSE,
            "license_url":"https://creativecommons.org/licenses/by-sa/4.0/",
            "source_page":SOURCE,
            "public_reuse":"yes — attribution and ShareAlike",
            "modifications":"Resaved at source dimensions with EXIF/GPS removed; no crop",
            "photo_status":"Original 1000x667 Commons source photograph visually inspected 2026-10-25 for basal clump and blades. Fine ligule/collar, roots and glumes NOT visible."
        })
    url="content/taxa/Poaceae/Eragrostis/eragrostis-spectabilis/"+rel
    items=doc["visual_comparison"]["items"]
    if not any(a.get("image_url")==url for a in items):
        item={
            "label":"BASAL LEAF DETAILS · same-species photographed lower tuft",
            "scientific_name":"Eragrostis spectabilis",
            "image_url":url,
            "image_fit":"contain",
            "image_role":"Source-labelled perennial basal clump, arching and upright leaf blades, reddish stems; not a dissected collar/true ligule",
            "caption":"Real photographed low leafy crown of source-labelled purple lovegrass. The dark upright reddish blade and cluster of basal leaf blades are visible. Root attachment, isolated ligule, 0.2–0.4 mm fringe/membrane and spikelets cannot be resolved. Original David J. Stang photograph, CC BY-SA 4.0.",
            "why_it_matters":"A different angle from three panicle-led photographs: train crew to locate blades and the basal tuft separately from the cloudlike flowering head.",
            "creator":CREATOR,
            "license":LICENSE,
            "license_url":"https://creativecommons.org/licenses/by-sa/4.0/",
            "source_page":SOURCE,
            "markers":[
                {"label":"Upright reddish leaf blade (not ligule)","label_x":67,"label_y":18,"target_x":51,"target_y":15},
                {"label":"Basal leafy tuft (roots not visible)","label_x":7,"label_y":87,"target_x":45,"target_y":85}
            ],
            "photo_status":"Original pixels inspected for gross foliage only; arrows do NOT claim unseen micromorphology. Same source taxon identified by creator, not voucher-confirmed Hays plant."
        }
        lookalike=next((i for i,x in enumerate(items) if x.get("scientific_name")!="Eragrostis spectabilis"),len(items))
        items.insert(lookalike,item)
    gallery_same=sum(x.get("scientific_name")=="Eragrostis spectabilis" for x in items)
    doc["curation_status"]["photo_metadata_count"]=len(doc["images"])
    doc["curation_status"]["photo_files_present"]=len(doc["images"])
    doc["curation_status"]["lane2_20261025_basal_photo"]="PUBLIC-LICENSED FIELD FOLIAGE UPGRADE; detailed anatomical gaps persist"
    doc["field_photo_quickcheck"]["featured_photo_indices"]=list(range(gallery_same))
    doc["field_photo_quickcheck"]["warning"]+=" Added one CC BY-SA 4.0 lower-tuft image showing REAL basal blades (not exposed ligule); true collar/spikelet/glume/lemma photos remain essential."
    doc["photo_note"]+="\n2026-10-25: Exact-source CC BY-SA 4.0 David J. Stang 1000x667 basal-plant photo archived and added to comparison gallery with 2 visible gross-organ arrows. No microstructure labelled; no county/taxonomy fields altered."
    doc["field_id_finish_pass"]["photo_evidence_limits"]+=" The added 5zz basal photograph shows leaf arrangement and partly leaf-wrapped stems, but NOT a true unfolded ligule, root structure, or reproductive details."
    doc["learner_visual_status"]["image_count"]=len(doc["images"])
    CARD.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps({
        "species":"Eragrostis spectabilis",
        "source":SOURCE,"original_media_url":IMAGE,"creator":CREATOR,"license":LICENSE,
        "photo_path":str(OUT),"sha256":hashlib.sha256(clean).hexdigest(),
        "clean_jpeg_size":len(clean),"dimensions":[1000,667],
        "new_archived_photo_count":1,"same_species_gallery_panels":gallery_same,
        "new_annotations":2,"annotation_level":"gross leaves / basal tuft only",
        "unresolved_diagnostic_photos":["true 0.2-0.4 mm ligule/collar with mm scale","isolated mature many-flowered spikelet with mm scale","dissected lower/upper glumes and lemmas","attached same-vouchered roots to full panicle"],
        "stage":"FIELD_READY_PHOTO_GAPS","source_id_level":"source-labelled; no local voucher",
    },indent=2)+"\n",encoding="utf-8")
    print(f"Installed basal foliage JPEG: {len(clean)} bytes, {gallery_same} exact-taxon teaching panels")
if __name__=="__main__": main()
