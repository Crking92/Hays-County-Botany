#!/usr/bin/env python3
"""Only Bob Harms' exact MUUT-L real M. utilis sheath JPEG; fail closed."""
import io,json,hashlib,requests
from datetime import datetime,timezone
from pathlib import Path
from PIL import Image,ImageOps
D=Path("content/taxa/Poaceae/Muhlenbergia")
SP=D/"muhlenbergia-utilis/species.json"
GP=D/"genus.json"
P=SP.parent/"images/bob-harms-muut-l-original.jpg"
RP=Path("reports/muhlenbergia-utilis-bob-harms-muut-l-20261027.json")
MP=Path("workflow/field-id-publication/2026-10-27-muhlenbergia-utilis-sheath-physical.json")
BASE="https://w3.biosci.utexas.edu/prc/Monocots/GrassHTML/data/"
SOURCE=BASE+"images/MUUT-L.jpg"
PAGE=BASE+"pages/MUUT-L.html"
RIGHTS="https://w3.biosci.utexas.edu/prc/Monocots/"
LICENSE="© Bob Harms — scientific/educational use with attribution (NOT Creative Commons)"
PERMISSION="BOB_HARMS_SELECTED_MONOCOTS_EDU_WITH_CREDIT_20261022"
def write(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def main():
    s=json.loads(SP.read_text(encoding="utf-8"))
    g=json.loads(GP.read_text(encoding="utf-8"))
    assert s["id"]=="muhlenbergia-utilis" and g["name"]=="Muhlenbergia"
    if P.exists() or any(im.get("source_photo_id")=="MUUT-L" for im in s["images"]):
        print("ALREADY PRESENT — nothing to install")
        return
    response=requests.get(SOURCE,timeout=35,headers={"User-Agent":"HaysBotanyResearch/1.0 (source-credited science/education)", "Accept":"image/jpeg,image/*"})
    response.raise_for_status()
    assert response.url.startswith("https://w3.biosci.utexas.edu/prc/Monocots/GrassHTML/data/images/") or response.url.startswith("https://www.biosci.utexas.edu/prc/Monocots/GrassHTML/data/images/")
    raw=response.content
    if not 3000<len(raw)<3_000_000 or not raw.startswith(b"\xff\xd8\xff"):raise ValueError("Invalid actual jpeg source")
    with Image.open(io.BytesIO(raw)) as im:
        im.load()
        if im.format!="JPEG" or min(im.size)<170:raise ValueError("Not proper JPEG or dimensions too small")
        original_dims=list(im.size)
        clean=ImageOps.exif_transpose(im).convert("RGB")
    buf=io.BytesIO()
    clean.save(buf,"JPEG",quality=94,optimize=True)
    blob=buf.getvalue()
    with Image.open(io.BytesIO(blob)) as im:
        assert im.format=="JPEG" and not im.getexif().get(34853)
        im.verify()
    P.parent.mkdir(parents=True,exist_ok=True)
    P.write_bytes(blob)
    metadata={"file":"images/"+P.name,
        "role":"Actual photographed M. utilis leaf–sheath junction and narrow blades with millimeter scale; 0.2–0.8 mm ligule FREE edge still unproven",
        "creator":"Bob Harms","license":LICENSE,"license_url":RIGHTS,
        "source_page":PAGE,"source_image":SOURCE,"source_photo_id":"MUUT-L",
        "source_taxon_name":"Muhlenbergia utilis","site_specific_public_permission":PERMISSION,
        "public_reuse":"Copyright Bob Harms: specifically credited educational/scientific use only, NOT CC",
        "photo_status":"PHYSICALLY_ARCHIVED_VERIFIED_SOURCE_EXIF_STRIPPED; microscopic free ligule NOT resolved",
        "original_sha256":hashlib.sha256(raw).hexdigest(),"archived_sha256":hashlib.sha256(blob).hexdigest(),
        "source_dimensions":original_dims,"archived_dimensions":list(clean.size),
        "modifications":"No crop/annotation. Resaved as EXIF/GPS-free RGB JPEG."
    }
    s["images"].append(metadata)
    local=str(P)
    for array in (s["visual_comparison"]["items"],g["visual_comparison"]["items"]):
        matches=[v for v in array if v.get("source_photo_id")=="MUUT-L"]
        if len(matches)!=1 or matches[0].get("source_page")!=PAGE or matches[0].get("creator")!="Bob Harms":
            raise RuntimeError("Expected one exact original source preview; concurrent gallery change")
        panel=matches[0]
        panel["image_url"]=local
        panel["photo_status"]="PHYSICALLY ARCHIVED exact Bob Harms M. utilis MUUT-L licensed original JPEG; credited educational use, NOT CC; short ligule free edge not anatomically proven"
    s["curation_status"]["photo_files_present"]=sum(
        1 for x in s["images"] if str(x.get("file","")).startswith("images/")
        and (SP.parent/x["file"]).is_file()
    )
    s["curation_status"]["photo_metadata_count"]=len(s["images"])
    s["curation_status"]["aparejograss_harms_sheath_physically_archived_20261027"]="MUUT-L original physically archived; true tiny ligule tip and underground rhizomes remain strict photo holds."
    write(SP,s)
    write(GP,g)
    write(RP,{"date_utc":datetime.now(timezone.utc).isoformat(),"result":"EXACT_ORIGINAL_JPEG_ARCHIVED",
        "taxon":"Muhlenbergia utilis","photo_id":"MUUT-L","source_page":PAGE,"photographer":"Bob Harms",
        "copyright":"Educational use with credit only, not CC",
        "source_dimensions":original_dims,"archived_dimensions":list(clean.size),
        "original_sha256":metadata["original_sha256"],"archive_sha256":metadata["archived_sha256"],
        "path":str(P),"remaining":"True entire ligule tip with 1mm calibrated closeup; actual scaly underground rhizome joined to live stems; mature measured spikelet dissection."})
    write(MP,{"date":"2026-10-27","taxon":"muhlenbergia-utilis","report":str(RP),
        "copyright":"Bob Harms exact Selected Monocots MUUT-L scientific/educational with attribution; NOT CC","approval":"Rights-filtered noncommercial Pages publication required"})
    print("VERIFIED AND ARCHIVED",str(P),original_dims,metadata["archived_sha256"])
if __name__=="__main__":
    main()
