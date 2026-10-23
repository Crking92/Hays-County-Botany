#!/usr/bin/env python3
"""Physically archive five source-named Bob Harms Selected Central Texas Monocots
Andropogon gerardii originals for a credited educational public learner.
Source-level photographs; DO NOT pretend one matched Hays voucher exists.
"""
import hashlib, io, json, time
from pathlib import Path
import requests
from PIL import Image, ImageOps

ROOT=Path("content/taxa/Poaceae/Andropogon")
SP=ROOT/"andropogon-gerardi/species.json"
GP=ROOT/"genus.json"
IMAGE_DIR=SP.parent/"images"
REPORT=Path("reports/andropogon-big-five-harms-real-jpegs-20261022.json")
RELEASE=Path("workflow/field-id-publication/2026-10-22-andropogon-five-physical-harms-release.json")
BASE="https://w3.biosci.utexas.edu/prc/Monocots/GrassHTML/data/"
RIGHTS="https://w3.biosci.utexas.edu/prc/Monocots/"
LIC="© Bob Harms — scientific/educational use with attribution (NOT Creative Commons)"
PERMIT="BOB_HARMS_SELECTED_MONOCOTS_EDU_WITH_CREDIT_20261022"
FILES=[
  ("ANGE-i","complete single awned flowering branch; NOT whole multi-ray terminal head"),
  ("ANGE-j1","attached units with original author scale; microscopic sessile/pedicelled assignments not independently proven"),
  ("ANGE-L","leaf sheath and true ligule region with source reference scale; no inferred membrane measurement"),
  ("ANGE-9","detached mature awned spikelets; not connected to the living parent individual"),
  ("ANGE-d","separating rachis segments; true fracture and organ names require independent pixel-level audit"),
]
s=json.loads(SP.read_text(encoding="utf-8"));g=json.loads(GP.read_text(encoding="utf-8"))
assert s["id"]=="andropogon-gerardi" and s["scientific_name"].startswith("Andropogon gerard")
assert s["project_inclusion"]["target_zone_status"]=="PASS"
assert len(s["visual_comparison"]["items"])==15
assert len(s["images"])==5
assert "FIELD_READY_PHOTO_GAPS" in s["field_id_finish_pass"]["stage"]
session=requests.Session()
session.headers.update({"User-Agent":"HaysBotanyEducationalPhotoArchive/1.0 (attributed Texas monocots)",
                        "Accept":"image/jpeg,image/*;q=0.9"})
result={"species":"Andropogon gerardii","source_collection":RIGHTS,
        "rights":"Bob Harms copyrighted originals; Selected Monocots grants scientific and educational uses with proper attribution, NOT Creative Commons",
        "source_scope":"Five named exact-species images ANGE-i, ANGE-j1, ANGE-L, ANGE-9, ANGE-d only",
        "verified_new_files":0,"entries":[],"missing_critical_anatomy":"Matched live locally vouchered root-to-head and Florida-paspalum inner sheath pair + one specimen's attached and dissected fertile/stalked pair"}
IMAGE_DIR.mkdir(parents=True,exist_ok=True)
for ident, role in FILES:
    url=BASE+"images/"+ident+".jpg"
    source=BASE+"pages/"+ident+".html"
    fn="bob-harms-big-bluestem-"+ident.lower()+".jpg"
    path=IMAGE_DIR/fn
    matches=[p for p in s["visual_comparison"]["items"] if p.get("image_url")==url or p.get("image_url")==str(path)]
    assert len(matches)==1, (ident,"species panels",len(matches))
    if not path.is_file():
        last_error=None
        for trial in range(3):
            try:
                resp=session.get(url,timeout=35)
                resp.raise_for_status()
                if not resp.content.startswith(bytes.fromhex("ffd8ff")):
                    raise ValueError("source not JPEG")
                with Image.open(io.BytesIO(resp.content)) as orig:
                    orig.load()
                    if orig.format!="JPEG" or min(orig.size)<175: raise ValueError("source dimensions too small")
                    out=ImageOps.exif_transpose(orig).convert("RGB")
                    original_size=orig.size
                out.save(path,"JPEG",quality=93,optimize=True)
                original_hash=hashlib.sha256(resp.content).hexdigest()
                result["verified_new_files"]+=1
                break
            except (requests.RequestException,ValueError,OSError) as error:
                last_error=str(error)
                if trial<2: time.sleep(4*(trial+1))
        else:
            raise RuntimeError(f"Source JPEG unavailable for {ident}: {last_error}")
    else:
        original_hash=None
        with Image.open(path) as im: original_size=im.size
    data=path.read_bytes()
    with Image.open(path) as im:
        assert im.mode=="RGB" and im.format=="JPEG" and min(im.size)>=175
        assert not im.getexif().get(34853)
        dims=im.size
        im.verify()
    record={
      "file":"images/"+fn,"role":role, "creator":"Bob Harms","license":LIC,
      "license_url":RIGHTS,"source_page":source,"source_image":url,
      "source_taxon_name":"Andropogon gerardii",
      "site_specific_public_permission":PERMIT,
      "public_reuse":"YES for attributed scientific/educational use of these exact copyrighted Selected Monocots originals only; NOT CC/general redistribution",
      "image_status":"REAL_ORIGINAL_PHYSICALLY_ARCHIVED_SOURCE_VERIFIED_PROVISIONAL_ARROWS",
      "image_dimensions":list(dims),"archive_sha256":hashlib.sha256(data).hexdigest(),
      "modifications":"Decoded original JPEG and re-encoded clean RGB without metadata or cropping. Original credit/source/rights preserved. Anatomical arrow targets pending pixel-level review.",
      "photo_review":"PROVISIONAL — USER PHOTO REVIEW PENDING; no assertion images all same collected voucher"
    }
    assert not any(y.get("file")==record["file"] for y in s["images"])
    s["images"].append(record)
    for panel in matches:
        panel["image_url"]=str(path)
        panel["license"]=LIC
        panel["license_url"]=RIGHTS
        panel["source_page"]=source
        panel["creator"]="Bob Harms"
        panel["photo_status"]="PHYSICAL COPYRIGHTED EDUCATIONAL ORIGINAL; attributed and source-verified, unmodified anatomical scale in original image. PROVISIONAL USER PHOTO REVIEW, no invented fine arrows or same-voucher proof."
        assert not panel.get("markers"),"Do not overwrite existing microscopic arrow claims without checking"
    result["entries"].append({"id":ident,"source":url,"source_page":source,"role":role,
       "path":str(path),"dimensions":list(dims),"archived_bytes":len(data),
       "source_original_sha256":original_hash,"archived_sha256":record["archive_sha256"]})
assert len(result["entries"])==5 and len(s["images"])==10
assert len(s["visual_comparison"]["items"])==15
assert sum(str(p.get("image_url","")).startswith(BASE+"images/") for p in s["visual_comparison"]["items"])==0
s["curation_status"]["photo_metadata_count"]=10
s["curation_status"]["photo_files_present"]=8
s["curation_status"]["harms_five_physical_anatomy_20261022"]={
 "new_real_jpegs":5,"total_physical_species_jpegs":8,"species_visual_panels":15,
 "source_collection":RIGHTS,"permission":"attributed scientific/educational Bob Harms copyrighted, NOT CC",
 "stage":"FIELD_READY_PHOTO_GAPS","all_fine_anatomy_arrows_verified":False
}
s["diagnostic_photo_second_pass_20261022"]["source_photo_status"]["local_physical_image_files_original"]=8
s["diagnostic_photo_second_pass_20261022"]["source_photo_status"]["new_physical_image_files"]=5
s["diagnostic_photo_second_pass_20261022"]["source_photo_status"]["new_bob_harms_educational_macro_panels"]=5
s["diagnostic_photo_second_pass_20261022"]["source_photo_status"]["original_image_metadata_total"]=10
s["diagnostic_photo_second_pass_20261022"]["source_photo_status"]["physical_harms_release_report"]=str(REPORT)
s["field_id_finish_pass"]["physical_archived_diagnostic_update_20261022"]={
 "five_actual_photos": [ident for ident,_ in FILES],"original_hashes_report":str(REPORT),
 "remaining_hold":["matched vouchered local rooted whole flowering culm",
                    "matched inner fresh Florida-paspalum versus big sheaths with true membrane measured",
                    "same identified mature paired sessile fertile & pedicellate spikelet 1-mm dissection"],
 "note":"Regional source labelled photos and original scale bars do not establish one-voucher connected anatomy. Microscopic arrow positions require source pixel visual confirmation.",
 "status":"FIELD_READY_PHOTO_GAPS"
}
SP.write_text(json.dumps(s,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
REPORT.parent.mkdir(parents=True,exist_ok=True)
REPORT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
RELEASE.parent.mkdir(parents=True,exist_ok=True)
RELEASE.write_text(json.dumps({
 "type":"manual_field_id_publication","species":"Andropogon gerardii",
 "date":"2026-10-22","archive_report":str(REPORT),
 "archived_big_bluestem_source_images":5,"total_species_image_files":8,
 "teaching_panels":15,
 "permission":"Bob Harms Selected Central Texas Monocots copyrighted educational use with creator credit",
 "held":"Exact same-voucher 1-mm intact fertile/pedicelled pair, root-to-head Hays series, matched Florida-paspalum opened sheath",
 "status":"FIELD_READY_PHOTO_GAPS",
 "release":"Rights-filtered GitHub Pages; separate SUCCESS check required"
},indent=2)+"\n",encoding="utf-8")
print("PASS: five original source-vetted Bob Harms exact-species physical JPEGs, no unverified microscopic arrows",flush=True)
