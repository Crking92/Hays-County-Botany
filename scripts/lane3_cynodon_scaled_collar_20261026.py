#!/usr/bin/env python3
"""Lane 3: archive one exact-taxon, CC BY-SA Cynodon collar photo with true scale.
Only change species.json if photo bytes download and validate successfully.
"""
from __future__ import annotations
import hashlib
import io
import json
import pathlib
import urllib.request
from PIL import Image, ImageOps

ROOT=pathlib.Path("content/taxa/Poaceae/Cynodon/cynodon-dactylon")
SPECIES=ROOT/"species.json"
DEST=ROOT/"images/cynodon-dactylon-stefan-lefnaer-scaled-collar-ccby-sa4.jpg"
REPORT=pathlib.Path("reports/lane3-cynodon-scaled-collar-20261026.json")
ORIGINAL_SOURCE="https://commons.wikimedia.org/wiki/File:Cynodon_dactylon_sl1.jpg"
DERIVATIVE="https://fieldguide.mt.gov/ca/fgImages/362487_1024.jpg"
LICENSE="https://creativecommons.org/licenses/by-sa/4.0/"
def main():
    s=json.loads(SPECIES.read_text(encoding="utf-8"))
    assert s["id"]=="cynodon-dactylon"
    items=s["visual_comparison"]["items"]
    if any(x.get("image_url")==DEST.as_posix() for x in items):
        print("Already installed: no duplicate."); return
    request=urllib.request.Request(DERIVATIVE,headers={"User-Agent":"HaysCountyBotanyEducationalFieldGuide/1.0","Accept":"image/jpeg,image/*"})
    with urllib.request.urlopen(request,timeout=40) as response:
        assert response.status==200
        payload=response.read(6_000_001)
    if len(payload)>6_000_000 or len(payload)<30_000:
        raise ValueError("Unexpected photo download size")
    with Image.open(io.BytesIO(payload)) as im:
        assert im.format=="JPEG" and im.width>=950 and im.height>=550, (im.format,im.size)
        assert im.width/im.height>1.3 and im.width/im.height<2.3
        rgb=ImageOps.exif_transpose(im).convert("RGB")
        rgb.thumbnail((1600,1600))
        out=io.BytesIO()
        rgb.save(out,format="JPEG",quality=89,optimize=True,exif=b"")
        clean=out.getvalue()
    with Image.open(io.BytesIO(clean)) as im:
        assert im.format=="JPEG" and im.width>=950
        assert not im.getexif().get(34853), "GPS found in saved source"
        im.verify()
    DEST.parent.mkdir(parents=True,exist_ok=True)
    DEST.write_bytes(clean)
    photo={
        "label":"BERMUDAGRASS — real collar with hairs and photographed 2 mm scale",
        "scientific_name":"Cynodon dactylon",
        "image_url":DEST.as_posix(),
        "image_fit":"contain",
        "image_role":"Actual source-identifed leaf-blade/sheath junction and pale hairs shown beside original 2 mm scale bar; individual 0.2–0.5 mm inner ligule is not dissected or separately measured",
        "caption":"Stefan Lefnaer's photographed bermudagrass leaf–sheath junction with white hair cluster, longer marginal hairs, and a 2 mm image scale. The original licensed photograph is reproduced via Montana Field Guide's credited copy. Browser arrows point to visible hairs only, not to an inferred 0.5 mm ligule membrane or root/rhizome.",
        "why_it_matters":"An actual collar photo with scale replaces having to infer bermudagrass hairs from distant leafy images; separate the very short inner ligule zone from longer collar hairs while teaching.",
        "creator":"Stefan.lefnaer (Stefan Lefnaer)",
        "license":"CC BY-SA 4.0",
        "license_url":LICENSE,
        "source_page":ORIGINAL_SOURCE,
        "display_copy_source":DERIVATIVE,
        "source_taxon":"Cynodon dactylon",
        "source_locality":"Vienna-Floridsdorf, Austria (not Texas)",
        "modification_note":"Reproduced from a Montana Field Guide credited display copy; JPEG recompressed and EXIF/GPS removed for this educational website; original scale and credit text retained; website arrows separate overlays. BY-SA terms apply to photo reproduction/adaptation.",
        "photo_status":"SOURCE-LICENSE VERIFIED + PHYSICALLY ARCHIVED; pixels screened at published 1000x600 display; collar hairs visible with 2 mm photo scale, no dissected short membranous base, rhizome or rooted stolon claimed.",
        "markers":[
            {"label":"Visible pale hairs at blade–sheath collar","label_x":2,"label_y":12,"target_x":49,"target_y":38},
            {"label":"Longer shoulder hairs (not measured ligule)","label_x":65,"label_y":61,"target_x":54,"target_y":53}
        ]
    }
    items.insert(3,photo)
    s["images"].append({
        "file":"images/"+DEST.name,
        "role":"Exact-species collar hair photo with a 2 mm photographed scale; individual free inner ligule not exposed separately",
        "creator":"Stefan.lefnaer (Stefan Lefnaer)",
        "license":"CC BY-SA 4.0",
        "license_url":LICENSE,
        "source_page":ORIGINAL_SOURCE,
        "display_copy_source":DERIVATIVE,
        "copyright_notice":"CC BY-SA 4.0 original by Stefan.lefnaer; web copy credits photographer",
        "modifications":"Resized/reencoded, EXIF/GPS stripped; web arrows separate overlays",
        "sha256":hashlib.sha256(clean).hexdigest(),
        "photo_status":"PHYSICALLY_ARCHIVED_20261026; short hair fringe and 2 mm scale visible; not calibrated individual ligule length"
    })
    s["field_id_finish_pass"]["lane3_scaled_collar_update_20261026"]={
        "status":"ADDED_SCALED_COLLAR_PHOTOGRAPH_NOT_COMPLETE_FOUR_ROLE",
        "local_file":DEST.as_posix(),
        "visible":"Actual blade–sheath junction, white hair cluster and longer marginal hairs, original 2 mm photo scale",
        "not_visible_or_proven":["separate opened 0.2–0.5 mm free ligule","connected stolon node bearing actual roots","underground scaly rhizome with bud"],
        "attribution":"Stefan.lefnaer, CC BY-SA 4.0, photographed in Vienna, credit retained"
    }
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps({
        "species":"Cynodon dactylon","status":"ONE_SCALED_COLLAR_PHOTO_ARCHIVED",
        "path":DEST.as_posix(),"sha256":hashlib.sha256(clean).hexdigest(),
        "source":ORIGINAL_SOURCE,"display_copy":DERIVATIVE,"creator":"Stefan.lefnaer",
        "license":"CC BY-SA 4.0","license_url":LICENSE,
        "verified_dimensions":list(rgb.size),"added_markers":2,
        "claim_limit":"Collar hairs and 2-mm scale only; no separately measured true ligule, no rooted stolon or rhizome"
    },indent=2)+"\n",encoding="utf-8")
    SPECIES.write_text(json.dumps(s,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Success: new local CC BY-SA image, one gallery panel, two conservative arrows; root/rhizome/inner ligule holds remain.")
if __name__=="__main__":
    main()
