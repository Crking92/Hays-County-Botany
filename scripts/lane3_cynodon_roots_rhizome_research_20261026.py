#!/usr/bin/env python3
"""Add a *supporting* CC-BY-reuse research figure showing Cynodon roots and rhizome.
Its labels are authored in the source: do not claim close-up nodes, buds or scale.
"""
from pathlib import Path
from PIL import Image
import io,urllib.request,json,hashlib

ROOT=Path("content/taxa/Poaceae/Cynodon/cynodon-dactylon")
P=ROOT/"species.json"
OUT=ROOT/"images/cynodon-dactylon-alam-2018-roots-rhizome-ccby4.jpg"
REPORT=Path("reports/lane3-cynodon-research-root-rhizome-20261026.json")
SOURCE="https://html.scirp.org/file/2-1660545x2.png"
PAPER="https://www.scirp.org/journal/paperinformation?paperid=89403"
LIC="https://creativecommons.org/licenses/by/4.0/"
def run():
    data=json.loads(P.read_text())
    assert data["id"]=="cynodon-dactylon"
    assert not OUT.exists(), "Already downloaded; don't repeat."
    request=urllib.request.Request(SOURCE,headers={"User-Agent":"HaysCountyBotanyEduResearch/1.0","Accept":"image/png,image/*"})
    with urllib.request.urlopen(request,timeout=40) as r:
        assert r.status==200 and "image" in r.headers.get("Content-Type","")
        raw=r.read(2_000_001)
    assert 10000<len(raw)<2000000
    with Image.open(io.BytesIO(raw)) as im:
        assert im.format=="PNG" and im.width>=300 and im.height>=300,(im.format,im.size)
        rgb=im.convert("RGB")
        output=io.BytesIO()
        rgb.save(output,format="JPEG",quality=94,optimize=True,exif=b"")
        img=output.getvalue()
    with Image.open(io.BytesIO(img)) as im:
        assert im.format=="JPEG" and im.size[0]>=300
        assert not im.getexif().get(34853)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_bytes(img)
    item={
        "label":"ROOT + RHIZOME — documented research figure (limited resolution)",
        "scientific_name":"Cynodon dactylon",
        "image_url":OUT.as_posix(),"image_fit":"contain",
        "image_role":"Original research photograph of a field-collected Cynodon dactylon root mass and horizontally spreading rhizome with source-printed labels; not an isolated rhizome node/bud macro, and no mm scale",
        "caption":"Alam et al. (2018), Figure 1, photographed bermudagrass belowground system with the rhizome and descending fibrous roots already labeled by the paper's authors. This is a LOW-RESOLUTION supporting image, NOT a certified individual rhizome bud or sheath-scale demonstration. This Louisiana-sourced paper does not prove that a wild Central Texas plant has been vouchered.",
        "why_it_matters":"Field crews can see that the lateral underground stem (rhizome) is not the same organ as the fine downward soil roots. The true rhizome bud/scale/node identification photo is still missing.",
        "creator":"Shaurav Alam, Ashlesh Banjara, Jay Wang, William B. Patterson and Sujan Baral",
        "license":"CC BY 4.0","license_url":LIC,"source_page":PAPER,
        "source_image":SOURCE,"source_figure":"Figure 1",
        "source_citation":"Alam et al. (2018), Novel Approach in Sampling and Tensile Strength Evaluation of Roots to Enhance Soil for Preventing Erosion, Open Journal of Soil Science 8:330–349, DOI 10.4236/ojss.2018.812024",
        "source_taxonomy":"Species ID from peer-reviewed scientific paper, without independent specimen voucher inspection",
        "modification_note":"Source figure originally printed with author arrows/text. Image converted losslessly in geometry from PNG to JPG, no crop or new annotations; original 315-pixel-resolution artwork retained. Credit + CC BY 4.0.",
        "photo_status":"ARCHIVED_RESEARCH_FIGURE_ONLY; anatomical overview helpful; too small to certify node/bud/scale, roots from particular node or independently scaled organ",
        "markers":[]
    }
    assert not any(x.get("image_url")==item["image_url"] for x in data["visual_comparison"]["items"])
    data["visual_comparison"]["items"].append(item)
    data["images"].append({
      "file":"images/"+OUT.name,
      "role":"Published scientific photograph of belowground Cynodon root mass and lateral rhizome, source annotations already present; low resolution, not species-field four-role completion",
      "creator":item["creator"],"license":"CC BY 4.0","license_url":LIC,"source_page":PAPER,"source_image":SOURCE,
      "sha256":hashlib.sha256(img).hexdigest(),"modifications":item["modification_note"],
      "photo_status":"ARCHIVED_RESEARCH_FIGURE_SUPPORT_ONLY"
    })
    data["field_id_finish_pass"]["lane3_research_roots_rhizome_20261026"]={
       "status":"SUPPORTING_ROOT_RHIZOME_ARCHITECTURE_FIGURE_ADDED",
       "field_role_finished":False,"scientific_photo_size_px":list(rgb.size),
       "visible":"Source-labeled dense root system and horizontal subterranean rhizome segment",
       "remaining":["live rooted node of photographed wild Cynodon dactylon",
                    "individual exposed rhizome with identifiable nodes, scale leaves and bud + mm scale",
                    "true inner short hairy ligule dimension separately measured"],
       "source":PAPER,"license":"CC BY 4.0"}
    P.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n")
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps({
      "status":"SUPPORTING_ROOT_RHIZOME_FIGURE_ARCHIVED_NOT_FOUR_ROLE_CERTIFIED",
      "path":OUT.as_posix(),"sha256":hashlib.sha256(img).hexdigest(),"dimensions":list(rgb.size),
      "author":item["creator"],"license":"CC BY 4.0","source":PAPER,
      "source_figure":SOURCE,"new_gallery_panels":1,"new_arrows":0,
      "holds":["subterranean rhizome bud, node, scale leaf with mm reference",
      "wild same-taxon surface runner with photographed actual nodal roots",
      "short true inner ligule measured; current collar photo only shows hair clusters"]},indent=2)+"\n")
    print("Verified archived research figure. Role not complete.")
if __name__=="__main__":
    run()
