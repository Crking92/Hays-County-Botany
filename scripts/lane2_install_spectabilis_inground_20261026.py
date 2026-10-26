#!/usr/bin/env python3
"""Lane 2: archive source-verified in-ground purple lovegrass tuft photo."""
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request,urlopen
import json, io, hashlib
from PIL import Image, ImageOps
ROOT=Path("content/taxa/Poaceae/Eragrostis/eragrostis-spectabilis")
CARD=ROOT/"species.json"
PIC=ROOT/"images"/"david-stang-grounded-basal-tuft-6zz.jpg"
REPORT=Path("reports/lane2-spectabilis-inground-crown-20261026.json")
TITLE="Eragrostis spectabilis 6zz.jpg"
SOURCE="https://commons.wikimedia.org/wiki/File:Eragrostis_spectabilis_6zz.jpg"
LICENSE_URL="https://creativecommons.org/licenses/by-sa/4.0/"
UA={"User-Agent":"HaysBotanyVisualLearner/1.0 (educational photograph source license check)"}
def fetch(url):
    with urlopen(Request(url,headers=UA),timeout=45) as resp:
        return resp.url,resp.read(8_000_001)
def main():
    j=json.loads(CARD.read_text(encoding="utf-8"))
    assert j["id"]=="eragrostis-spectabilis"
    assert not any(x.get("source_page")==SOURCE for x in j["images"]),"Same source already installed: stop"
    url="https://commons.wikimedia.org/w/api.php?action=query&titles="+quote("File:"+TITLE)+"&prop=imageinfo&iiprop=url%7Cextmetadata&format=json"
    _,payload=fetch(url)
    data=json.loads(payload)
    row=next(iter(data["query"]["pages"].values()))["imageinfo"][0]
    meta=row["extmetadata"]
    assert meta["LicenseShortName"]["value"].replace(" ","").lower()=="ccby-sa4.0",meta.get("LicenseShortName")
    assert "David J. Stang" in meta["Artist"]["value"],"Unexpected original creator"
    orig=row["url"]
    assert orig.startswith("https://upload.wikimedia.org/wikipedia/commons/"),orig
    final,raw=fetch(orig)
    assert final.startswith("https://upload.wikimedia.org/") and len(raw)>200_000
    with Image.open(io.BytesIO(raw)) as source:
        assert source.format=="JPEG" and source.size==(1000,667),"Original Commons file changed: hold"
        im=ImageOps.exif_transpose(source).convert("RGB")
    out=io.BytesIO()
    im.save(out,format="JPEG",quality=89,optimize=True)
    clean=out.getvalue()
    with Image.open(io.BytesIO(clean)) as checked:
        assert checked.format=="JPEG" and not checked.getexif(),"EXIF/GPS detected after cleaning"
    PIC.parent.mkdir(parents=True,exist_ok=True)
    if PIC.exists():
        assert PIC.read_bytes()==clean,"Do not overwrite another media version"
    else:
        PIC.write_bytes(clean)
    rel="images/"+PIC.name
    url="content/taxa/Poaceae/Eragrostis/eragrostis-spectabilis/"+rel
    j["images"].append({
        "file":rel,
        "role":"IN-GROUND LOW CROWN: source-identified live leafy tuft rooted in soil, radiating basal blades, loose scattered upright leaves; NO exposed rootstock/rhizome, no collar macro and no attached inflorescence in this frame",
        "creator":"David J. Stang",
        "license":"CC BY-SA 4.0",
        "license_url":LICENSE_URL,
        "source_page":SOURCE,
        "source_location":"United States Botanic Garden, Washington DC (garden; NOT Hays County)",
        "public_reuse":"yes, credited Creative Commons Attribution-ShareAlike 4.0",
        "photo_status":"Public source individually checked and 1000x667 original pixels reviewed 2026-10-26. Visible ground-anchored tuft; roots, true ligule and actual rhizomes NOT seen.",
        "modifications":"JPEG RGB re-encoded to remove EXIF/GPS without crop or color edits; two separate SVG visual-learning arrow overlays."
    })
    items=j["visual_comparison"]["items"]
    assert not any(x.get("image_url")==url for x in items)
    new={
        "label":"GROWING IN SOIL · ground-anchored leafy crown (roots not exposed)",
        "scientific_name":"Eragrostis spectabilis",
        "image_url":url,
        "image_fit":"contain",
        "image_role":"Actual planted growing tuft at ground level with radiating narrow blades and bundled shoots; roots/rhizomes and true ligule unexposed",
        "caption":"David J. Stang's photographed living Eragrostis spectabilis at the United States Botanic Garden. The green crown and many narrow leaves visibly emerge from soil. This helps crew recognize a low tuft in the ground, but does NOT demonstrate an excavated knotty rhizome, emerging subterranean node, 0.1–0.4 mm true ligule or attached full seedhead. The botanical-garden plant is not a local Hays County voucher.",
        "why_it_matters":"Teaches the actual soil-surface crown and narrow leaves, a different practical photo role from the several existing cloudlike flowering heads.",
        "creator":"David J. Stang",
        "license":"CC BY-SA 4.0",
        "license_url":LICENSE_URL,
        "source_page":SOURCE,
        "modifications":"EXIF/GPS removed by RGB JPEG re-encode; two separate arrow overlays only",
        "markers":[
            {"label":"Basal leafy tuft at soil surface (not visible roots)","label_x":2,"label_y":81,"target_x":49,"target_y":67},
            {"label":"Narrow leaf blades radiating from crown","label_x":71,"label_y":16,"target_x":47,"target_y":39}
        ],
        "photo_status":"1000×667 actual CC BY-SA source pixels manually reviewed 2026-10-26. Only gross structures labelled; no true ligule/root or microanatomy inferred."
    }
    last=next((i for i,x in enumerate(items) if x.get("scientific_name")!="Eragrostis spectabilis"),len(items))
    items.insert(last,new)
    j["field_photo_quickcheck"]["featured_photo_indices"]=list(range(last+1))
    j["field_photo_quickcheck"]["steps"][0]="START with the five locally archived actual Eragrostis spectabilis photographs: four show panicle or leafy-aboveground views and the new David Stang 6zz source shows an actual GREEN CROWN growing out of soil. None alone exposes the underground rooted rhizome, measured collar or isolated reproductive parts."
    j["field_photo_quickcheck"]["warning"]+=" 2026-10-26: added real source-authenticated 1000x667 in-ground basal tuft (David J. Stang, CC BY-SA 4.0) with two crown/blade arrows; crown is soil-anchored, actual rhizomes and roots remain hidden. Complete attached flowering-head images are preserved separately."
    j["curation_status"]["photo_metadata_count"]=len(j["images"])
    j["curation_status"]["photo_files_present"]=len([p for p in j["images"] if str(p.get("file","")).startswith("images/")])
    j["curation_status"]["lane2_inground_20261026"]="EXACT-SOURCE IN-GROUND BUNCH CROWN ADDED; PHOTO-GAPS REMAIN"
    j["field_id_finish_pass"]["photo_evidence_limits"]+=" October 26 in-ground crown addition shows green leaves anchored at ground level; no underground nodes, root system, exposed 0.1-0.4 mm ligule, or same-specimen crown to panicle series."
    if isinstance(j.get("learner_visual_status"),dict):
        j["learner_visual_status"]["image_count"]=len(j["images"])
    j["photo_note"]=j.get("photo_note","")+"\n2026-10-26: real in-ground David J. Stang CC BY-SA 4.0 (6zz) tuft photographed at US Botanic Garden; physically archived scrubbed JPEG, gallery taught with 2 visible-organ arrows. Existing gross/flowerhead photos untouched. Roots/rhizomes and actual ligule remain precise roles to capture."
    CARD.write_text(json.dumps(j,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps({
        "species":"Eragrostis spectabilis",
        "date":"2026-10-26",
        "source":SOURCE,
        "license":"CC BY-SA 4.0",
        "license_url":LICENSE_URL,
        "creator":"David J. Stang",
        "photo_path":str(PIC),
        "sha256":hashlib.sha256(clean).hexdigest(),
        "bytes":len(clean),
        "dimensions":[1000,667],
        "new_photo_count":1,
        "local_photo_count":j["curation_status"]["photo_files_present"],
        "same_species_gallery_panels":last+1,
        "new_annotations":2,
        "actual_visible":["soil-surface leafy crown","narrow radiating blades"],
        "still_unproven":["connected root+short knotty rhizome","true opened ligule/collar with scale","root/crown and entire attached flowering head on the same documented specimen"],
        "scientific_status":"FIELD_READY_PHOTO_GAPS"
    },indent=2)+"\n",encoding="utf-8")
    print("ARCHIVE_SUCCESS",len(clean),str(PIC),"gallery",last+1)
if __name__=="__main__":
    main()
