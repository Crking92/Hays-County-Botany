#!/usr/bin/env python3
"""Lane 2: add one *external sheath-hair* macro, NOT a true ligule, to purple lovegrass.
Individually verify the original photo's CC license and Research Grade taxon metadata.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageOps
import json,io,hashlib

ROOT=Path("content/taxa/Poaceae/Eragrostis/eragrostis-spectabilis")
CARD=ROOT/"species.json"
OUT=ROOT/"images"/"anne-parker-purple-lovegrass-exterior-collar-hairs-711218981.jpg"
REPORT=Path("reports/lane2-spectabilis-external-collar-hairs-20261026.json")
PID=711218981
OID=388336600
UA={"User-Agent":"HaysBotanyPublicLearner/1.0 photo-level CC rights and visual ID annotation"}
SOURCE=f"https://www.inaturalist.org/photos/{PID}"

def main():
    with urlopen(Request(f"https://api.inaturalist.org/v1/observations/{OID}",headers=UA),timeout=35) as p:
        raw=json.load(p)
    assert len(raw["results"])==1
    obs=raw["results"][0]
    assert obs["id"]==OID and obs["taxon"]["name"]=="Eragrostis spectabilis"
    assert obs["quality_grade"]=="research"
    photo=next(x for x in obs["photos"] if x["id"]==PID)
    assert photo.get("license_code")=="cc-by",(PID,photo.get("license_code"))
    assert "Anne Parker" in photo.get("attribution",""),photo.get("attribution")
    remote=f"https://inaturalist-open-data.s3.amazonaws.com/photos/{PID}/original.jpg"
    with urlopen(Request(remote,headers=UA),timeout=45) as p:
        assert p.url.startswith("https://inaturalist-open-data.s3.amazonaws.com/")
        orig=p.read(10_000_001)
    assert 300_000<len(orig)<10_000_001
    with Image.open(io.BytesIO(orig)) as image:
        assert image.format=="JPEG" and image.size==(1536,2048),image.size
        clean=ImageOps.exif_transpose(image).convert("RGB")
    bio=io.BytesIO()
    clean.save(bio,format="JPEG",quality=89,optimize=True)
    payload=bio.getvalue()
    with Image.open(io.BytesIO(payload)) as chk:
        assert chk.format=="JPEG" and not chk.getexif(),"EXIF/GPS not removed"
    OUT.parent.mkdir(parents=True,exist_ok=True)
    if OUT.exists():
        assert OUT.read_bytes()==payload,"Different existing file; no overwrite"
    else:
        OUT.write_bytes(payload)
    doc=json.loads(CARD.read_text(encoding="utf-8"))
    assert doc["id"]=="eragrostis-spectabilis"
    assert not any(a.get("source_page")==SOURCE for a in doc["images"]),"Already installed by another worker"
    rel="images/"+OUT.name
    doc["images"].append({
      "file":rel,
      "role":"ACTUAL same-species live macro — prominent long WHITE HAIRS at OUTSIDE blade base and sheath mouth, adjacent green blades; tiny internal true ligule NOT exposed",
      "creator":"Anne Parker",
      "license":"CC BY (iNaturalist individual photo metadata: cc-by)",
      "license_url":"https://creativecommons.org/licenses/by/4.0/",
      "source_page":SOURCE,
      "source_observation_page":f"https://www.inaturalist.org/observations/{OID}",
      "public_reuse":"Yes, original photo-level CC BY; credit photographer, original URL, adaptations noted.",
      "photo_source_verification":"Research Grade Eragrostis spectabilis observation 388336600 in Virginia, individual photo 711218981 code cc-by; source species determined in original record, NOT a Hays voucher.",
      "photo_status":"SOURCE-ORIGINAL-PIXEL-INSPECTED 2026-10-26. Long external leaf-base hairs visible. Internal true ligule and its 0.2–0.4 mm margin are NOT visible; no millimeter scale.",
      "modifications":"Re-encoded source 1536×2048 RGB JPEG without crop, stripped GPS/EXIF; separate browser-only SVG arrow."
    })
    url="content/taxa/Poaceae/Eragrostis/eragrostis-spectabilis/"+rel
    index=next((i for i,x in enumerate(doc["visual_comparison"]["items"]) if x.get("scientific_name")!="Eragrostis spectabilis"),len(doc["visual_comparison"]["items"]))
    doc["visual_comparison"]["items"].insert(index,{
        "label":"LONG EXTERIOR HAIRS · actual purple lovegrass blade base; NOT true ligule",
        "scientific_name":"Eragrostis spectabilis",
        "image_url":url,
        "image_fit":"contain",
        "image_role":"Close photographed outer blade base with many long white hairs emerging from sheath-mouth/collar region. Does not reveal the inner tiny ciliate ligule.",
        "caption":"Anne Parker's source-identified purple lovegrass shows the conspicuous long outer hairs near the blade–sheath junction, alongside narrow radiating blades and immature flowering parts. The arrow marks the actual OUTER hair tuft, which is longer than the 0.2–0.4 mm true inner ligule. The blade has not been peeled open, and no millimeter ruler is shown; do not claim this is a ligule macro. Virginia, not a Hays County voucher.",
        "why_it_matters":"A strong close teaching photograph for exactly the common confusion: exterior sheath-mouth hairs are NOT the tiny true ligule hidden inside the blade base.",
        "creator":"Anne Parker",
        "license":"CC BY (iNaturalist photo-level code cc-by)",
        "license_url":"https://creativecommons.org/licenses/by/4.0/",
        "source_page":SOURCE,
        "modifications":"No crop or source-image markup, source EXIF stripped; browser arrow separate",
        "markers":[{"label":"Long OUTSIDE hairs at blade base — not ligule","label_x":4,"label_y":32,"target_x":44,"target_y":48}],
        "photo_status":"Original 1536×2048 photographed same-species Research Grade photo pixel reviewed 2026-10-26, one evidence-limited annotation. No true membranous ligule visible."
    })
    doc["field_photo_quickcheck"]["featured_photo_indices"]=list(range(index+1))
    doc["field_photo_quickcheck"]["steps"].insert(2,"COMPARE 3 actual outside sheath/collar views: the newly archived Anne Parker CC BY frame clearly separates the long external white hairs from the slender blade, but none shows the tiny INNER true ligule. Peel a separate blade away from its sheath; use a 1-mm bar to show the 0.2–0.4-mm white membrane/short cilia.")
    doc["field_photo_quickcheck"]["warning"]+=" 2026-10-26 Anne Parker CC BY Research Grade external hairy blade-base macro physically stored, one gross hair-arrow, YES outer hairs, NO peeled true ligule or calibrated micromorphology. Strict completion remains blocked."
    doc["curation_status"]["photo_metadata_count"]=len(doc["images"])
    doc["curation_status"]["photo_files_present"]=sum(str(a.get("file","")).startswith("images/") for a in doc["images"])
    doc["curation_status"]["lane2_anne_parker_external_hairs_20261026"]="PUBLIC-SAFE DETAILED OUTER COLLAR HAIRS; NOT TRUE LIGULE, STRICT HOLD RETAINED"
    doc["photo_note"]=doc.get("photo_note","")+"\n2026-10-26 Lane 2 source/photo-specific CC BY Anne Parker outer blade-base hair macro archived; one visible-only arrow. Not a replacement for actual true 0.2–0.4-mm ligule; other collar photos preserved."
    if isinstance(doc.get("learner_visual_status"),dict):
        doc["learner_visual_status"]["image_count"]=len(doc["images"])
    CARD.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps({
      "species":"Eragrostis spectabilis","date":"2026-10-26","photo":PID,
      "observation":OID,"photographer":"Anne Parker","license_code":"cc-by",
      "source_page":SOURCE,"original_dimensions":[1536,2048],
      "local_path":str(OUT),"bytes":len(payload),"sha256":hashlib.sha256(payload).hexdigest(),
      "new_same_species_images":1,"local_same_species_images":doc["curation_status"]["photo_files_present"],
      "new_markers":1,"photo_role":"exterior collar hairs only, not ligule",
      "still_missing":"TRUE inner peeled-open short-ciliate ligule with metric scale and rooted rhizome same-voucher",
      "status":"FIELD_READY_PHOTO_GAPS","publication":"not yet verified live"
    },indent=2)+"\n",encoding="utf-8")
    print("ARCHIVED_CC_BY_OUTER_HAIRS",str(OUT),len(payload))
if __name__=="__main__":main()
