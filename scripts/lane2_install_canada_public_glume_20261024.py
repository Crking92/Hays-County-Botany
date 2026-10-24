#!/usr/bin/env python3
"""Physically archive CC BY-SA 2.0 original Canada wildrye glume macro and wire public gallery."""
import io, json, pathlib, hashlib, time, urllib.request, urllib.error
from PIL import Image

base=pathlib.Path("content/taxa/Poaceae/Elymus/elymus-canadensis")
path=base/"species.json"
source="https://commons.wikimedia.org/wiki/File:Elymus_canadensis_(3738626381).jpg"
original="https://upload.wikimedia.org/wikipedia/commons/c/c8/Elymus_canadensis_%283738626381%29.jpg"
dest=base/"images/matt-lavin-canada-rachis-narrow-glumes-3738626381.jpg"
report={"source":source,"license":"CC BY-SA 2.0","creator":"Matt Lavin","status":"HOLD"}
try:
    raw=None
    for attempt in range(5):
        try:
            req=urllib.request.Request(original,headers={"User-Agent":"HaysCountyBotanyVisualLearner/1.1 (publicly credited botany media reuse)","Accept":"image/jpeg"})
            with urllib.request.urlopen(req,timeout=85) as f:
                raw=f.read()
            break
        except urllib.error.HTTPError as e:
            if e.code not in (429,502,503,504) or attempt==4:
                raise
            time.sleep([2,5,11,20,30][attempt])
    assert raw is not None and 20000 < len(raw) < 10000000
    check=Image.open(io.BytesIO(raw));check.verify()
    im=Image.open(io.BytesIO(raw)).convert("RGB")
    assert im.size==(1704,2272),f"unanticipated dimensions: {im.size}"
    dest.parent.mkdir(parents=True,exist_ok=True)
    im.save(dest,format="JPEG",quality=93,optimize=True)
    j=json.loads(path.read_text())
    assert j.get("id")=="elymus-canadensis"
    if not any(x.get("source_page")==source for x in j.get("images",[])):
        j["images"].append({
            "file":"images/"+dest.name,
            "role":"MATURE NODE MACRO — two narrow glumes enclosing multiflowered paired spikelets on a source-identified Canada wildrye rachis; NOT a metric or locality voucher",
            "creator":"Matt Lavin",
            "license":"CC BY-SA 2.0",
            "license_url":"https://creativecommons.org/licenses/by-sa/2.0/",
            "source_page":source,
            "original_source":"https://www.flickr.com/photos/plant_diversity/3738626381",
            "photo_taxon":"Photographer-named Elymus canadensis",
            "source_locality":"Bozeman, Montana; not Hays County",
            "public_reuse":"YES: CC BY-SA 2.0 with creator/source/license credit and ShareAlike notices",
            "modifications":"Original RGB JPEG re-encoded without EXIF/GPS; original pixels not cropped",
            "archive_status":"LOCALLY_STORED",
            "photo_review":"Exact photo original viewed 2026-10-24; mature paired slender glumes visible, no exact 1-mm base proof or fine organ arrows"
        })
    if not any(x.get("source_page")==source for x in j["visual_comparison"]["items"]):
        panel={
           "label":"CANADA — TRUE NARROW GLUMES ON ATTACHED NODE · close original",
           "scientific_name":"Elymus canadensis",
           "image_url":str(dest),
           "image_fit":"contain",
           "image_role":"Real unscaled close-up of Canada wildrye paired spikelets and narrow glumes along the rachis; not an instrument-measured Hays voucher",
           "caption":"Matt Lavin's CC BY-SA 2.0 photograph of a Canada wildrye flowering node; the narrow green glumes and subtended multiple-flowered spikelets are photographed directly. Compare with the separate licensed Virginia wildrye photograph showing hardened outwardly bowed glume bases. Do NOT infer millimeter dimensions or same-voucher taxonomy from these different Montana originals.",
           "why_it_matters":"Direct close detail of real Canada glume architecture permits side-by-side comparison with Virginia wildrye without relying on external image availability.",
           "creator":"Matt Lavin",
           "license":"CC BY-SA 2.0",
           "license_url":"https://creativecommons.org/licenses/by-sa/2.0/",
           "source_page":source,
           "markers":[],
           "photo_status":"Exact CC BY-SA 2.0 original converted into stored RGB JPEG; photo checked gross glumes but NOT anatomic pixel-placed arrows or 1mm ruler."
        }
        j["visual_comparison"]["items"].insert(5,panel)
    existing=j["field_photo_quickcheck"].get("featured_photo_indices",[])
    newindex=next((i for i,x in enumerate(j["images"]) if x.get("source_page")==source),None)
    if newindex is not None:
        j["field_photo_quickcheck"]["featured_photo_indices"]=[newindex]+[i for i in existing if 0<=i<len(j["images"]) and i!=newindex]
    j["field_photo_quickcheck"]["warning"] = (
       "Twelve exact-species JPEGs now stored, including three Commons CC BY-SA 2.0 photos and nine Bob Harms copyrighted site-permitted educational-only originals. "
       "The new original Canada macro shows visibly narrow glume architecture, not a calibrated 1mm base or photo of a same plant as Virginia. "
       "Previously stored CC BY-SA comparison images all served from local repository paths. "
       "Separate ligule tip and matched native vouchers still missing; live site QA pending."
    )
    f=j["field_id_finish_pass"].setdefault("lane2_photo_finish_20261023",{})
    f["close_detail_20261024"]={
       "status":"FIELD_READY_PHOTO_GAPS",
       "new_photo":"images/"+dest.name,
       "license":"CC BY-SA 2.0, Matt Lavin (original source credited)",
       "local_exact_species_JPEGs":len([x for x in j["images"] if x.get("file","").startswith("images/")]),
       "new_macro_arrow_count":0,
       "comparison_local":"Canada glumes plus already archived Virginia outward-bowed glumes",
       "critical_remaining":["Matched vouchered Canada/Virginia mature rachis nodes with mm ruler", "Opened true ligule margin and auricles, scale", "Same rooted Hays-area mature plant source and live Pages/mobile QA"]
    }
    path.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n")
    report.update(status="ARCHIVED",path=str(dest),dimensions=list(im.size),
                  source_sha256=hashlib.sha256(raw).hexdigest(),
                  installed_sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),
                  gallery_panel_added=True)
except Exception as exc:
    report["error"]=str(exc)
out=pathlib.Path("reports/lane2-canada-wildrye-public-glume-20261024.json")
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
