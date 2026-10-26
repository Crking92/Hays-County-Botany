#!/usr/bin/env python3
"""Lane 2: physically archive licensed living Setaria parviflora attached-head habit photo."""
from pathlib import Path
from urllib.request import Request,urlopen
import io,json,hashlib
from PIL import Image, ImageOps
P=Path("content/taxa/Poaceae/Setaria/setaria-parviflora/species.json")
F=P.parent/"images"/"stefan-lefnaer-whole-attached-flowering-sl1.jpg"
REPORT=Path("reports/lane2-setaria-parviflora-attached-whole-20261026.json")
SOURCE="https://commons.wikimedia.org/wiki/File:Setaria_parviflora_sl1.jpg"
URL="https://upload.wikimedia.org/wikipedia/commons/4/4e/Setaria_parviflora_sl1.jpg"
L="https://creativecommons.org/licenses/by-sa/4.0/"
def main():
    doc=json.loads(P.read_text())
    assert doc["id"]=="setaria-parviflora"
    original=next(v for v in doc["images"] if v.get("source_page")==SOURCE)
    if str(original.get("file","")).startswith("images/"):
        raise RuntimeError("Already installed, stop without duplicate")
    with urlopen(Request(URL,headers={"User-Agent":"Hays-Botany-CC-BY-SA-Attribution/1.0"}),timeout=45) as h:
        assert h.url.startswith("https://upload.wikimedia.org/"),"Unexpected origin"
        binary=h.read(12_000_000)
    assert 1_000_000<len(binary)<12_000_000
    with Image.open(io.BytesIO(binary)) as raw:
        assert raw.format=="JPEG" and set(raw.size)=={3000,4000}, "Source image dimensions changed"
        im=ImageOps.exif_transpose(raw).convert("RGB")
    im.thumbnail((2400,2400))
    out=io.BytesIO();im.save(out,format="JPEG",quality=88,optimize=True)
    compressed=out.getvalue()
    with Image.open(io.BytesIO(compressed)) as chk:
        assert chk.format=="JPEG" and not chk.getexif(),"Image not stripped of EXIF/GPS"
    F.parent.mkdir(parents=True,exist_ok=True)
    if F.exists(): 
        assert F.read_bytes()==compressed,"Different content already at location; do not overwrite"
    else:
        F.write_bytes(compressed)
    original["historical_remote_photo_url"]=original["file"]
    original["file"]="images/"+F.name
    original["role"]="Source-identified FULL LIVE FLOWERING CLUMP in natural habitat: many attached tapering foxtail heads and long linear leaf blades converging toward basal leafy tuft. Underground rhizome NOT exposed in this photo."
    original["photo_review_status"]="SOURCE-IMAGE_PIXEL_VERIFIED_AND_PHYSICALLY_ARCHIVED_20261026: CC BY-SA 4.0 from photographer Stefan.lefnaer"
    original["public_reuse"]="Yes, individually verified CC BY-SA 4.0 public reproduction with visible credit, source, license, adaptation notice and ShareAlike obligations"
    original["modifications"]="Scaled 3000x4000 authored image to 2400px longest side; oriented RGB and stripped EXIF/GPS; original photo not cropped, separate non-destructive browser-arrow overlays"
    gallery=doc["visual_comparison"]["items"]
    panel=next(x for x in gallery if x.get("image_url","").startswith("https://commons.wikimedia.org/wiki/Special:Redirect/file/Setaria%20parviflora%20sl1.jpg"))
    panel["image_url"]="content/taxa/Poaceae/Setaria/setaria-parviflora/images/"+F.name
    panel["label"]="FULL LIVE PLANT · intact tapered foxtail heads above leafy basal clump"
    panel["image_role"]=original["role"]
    panel["caption"]="Stefan.lefnaer's actual flowering stand on the Croatian island of Unije, photo-authenticated as Setaria parviflora. Multiple intact inflorescences remain attached to shoots arising among long, narrow upright blades. The leafy shoot base is visible at ground level; ROOTS and connected knotty rhizomes are NOT visible here. Study the separate real rhizome panel to learn underground connections. CC BY-SA 4.0, image scaled and GPS metadata stripped."
    panel["why_it_matters"]="Completes a genuine broad growth-form view rather than treating detached spikelets as sufficient for field ID; teaches where to look next for rootstock and collar."
    panel["markers"]=[
      {"label":"Attached entire foxtail seedhead","label_x":69,"label_y":13,"target_x":66,"target_y":24},
      {"label":"Long narrow leaf blades","label_x":7,"label_y":48,"target_x":38,"target_y":56},
      {"label":"Basal leafy tuft — roots not visible","label_x":5,"label_y":84,"target_x":43,"target_y":75}
    ]
    panel["photo_status"]="Real 3000x4000 photographer original visually reviewed 2026-10-26; CC BY-SA 4.0 from independent photo source, archived as clean 2400px JPEG; three gross-organ arrows. No fake rhizome/root or true ligule arrow."
    doc["field_photo_quickcheck"]["steps"][0]="Start with the locally archived living plant and follow one entire slender foxtail head down to its leafy basal tuft. Then open the separate actual excavated knotty rhizome photo; it shows the connected hard underground stem and attached roots that the live field shot does NOT expose."
    doc["field_photo_quickcheck"]["warning"]+=" 2026-10-26: source CC BY-SA 4.0 whole-plant image sl1 is now a locally archived EXIF-free JPEG, with three gross-only arrow markers; original NC-licensed S. scheelei comparison remains preserved with attribution, subject to noncommercial use and individual license recheck. Site must pass rights-filtered deployment before live claim."
    doc["curation_status"]["photo_metadata_count"]=len(doc["images"])
    doc["curation_status"]["photo_files_present"]=sum(str(x.get("file","")).startswith("images/") for x in doc["images"])
    doc["curation_status"]["lane2_whole_head_role_20261026"]="SOURCE_LICENSED CC BY-SA 4.0 FULL FLOWERING LIVE CLUMP PHYSICALLY LOCAL; underground roots still separate photograph"
    if isinstance(doc.get("learner_visual_status"),dict):
        doc["learner_visual_status"]["image_count"]=len(doc["images"])
    doc["photo_note"]=doc.get("photo_note","")+"\n2026-10-26 Lane 2: Stefan.lefnaer sl1 actual attached flowering stand publicly CC BY-SA 4.0 now stored as scrubbed local JPEG; 3 accurate whole-head/blade/basal tuft arrows. Sl13 belowground rhizome, sl16 true hair ligule, sl24 attached bristles and sl29 reproductive dissection retained. No noncommercial license content deleted."
    P.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+"\n")
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps({
       "species":"Setaria parviflora","original_source":SOURCE,"creator":"Stefan.lefnaer","license":"CC BY-SA 4.0","license_url":L,
       "photo_path":str(F),"sha256":hashlib.sha256(compressed).hexdigest(),"bytes":len(compressed),"dimensions":list(im.size),"original_dimensions":"3000x4000 with source camera orientation metadata",
       "local_photo_count":doc["curation_status"]["photo_files_present"],"gross_arrows":3,
       "roles_demonstrated":["complete aboveground leafy tuft","multiple still attached mature seedheads","narrow leaf blades"],
       "existing_roles_preserved":["real rhizome and roots","short hair-fringed ligule photo","bristle base","glume/lemma dissection"],
       "explicit_gaps":["entire rooted local specimen with underground nodes connected to photographed heads", "same-voucher Hays-area collar and seedhead photos"],
       "NC_rights":"No NC photo removed or relicensed; conditional suitability requires individual photo-specific verification for each hosted NC asset.",
       "scientific_status":"FIELD_READY_PHOTO_GAPS"
    },indent=2)+"\n")
    print("ARCHIVED",F,len(compressed), im.size)
if __name__=="__main__":main()
