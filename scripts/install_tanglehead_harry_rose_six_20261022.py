#!/usr/bin/env python3
"""Archive six Harry Rose CC BY 2.0 tanglehead anatomy originals.
Fail closed: if one original can't be downloaded/decoded, commit nothing.
Existing photos, source rights, science holds, and pixel overlays are preserved.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import time
from pathlib import Path
from urllib.parse import quote

import requests
from PIL import Image, ImageOps

ROOT=Path(".")
SPEC=ROOT/"content/taxa/Poaceae/Heteropogon/heteropogon-contortus/species.json"
GENUS=ROOT/"content/taxa/Poaceae/Heteropogon/genus.json"
CSV=SPEC.parent/"image-sources.csv"
REPORT=ROOT/"reports/heteropogon-harry-rose-physical-six-20261022.json"
MARK=ROOT/"workflow/field-id-publication/2026-10-22-tanglehead-six-physical-cc-by-photos.json"
LICENSE="https://creativecommons.org/licenses/by/2.0/"
BASE="https://commons.wikimedia.org/wiki/File:"
PHOTOS=[
 ("ligule1","8232577557","harry-rose-8232577557-ligule1.jpg", (1600,1200)),
 ("ligule2","8233611392","harry-rose-8233611392-ligule2.jpg", (928,1182)),
 ("spikelets1","8233648182","harry-rose-8233648182-spikelets1.jpg", (808,1115)),
 ("spikelets3","8233651018","harry-rose-8233651018-spikelets3.jpg", (3008,2000)),
 ("spikelets4","8233653534","harry-rose-8233653534-spikelets4.jpg", (2517,1600)),
 ("spikelets6","8232551199","harry-rose-8232551199-spikelets6.jpg", (1218,1423)),
]

def save_json(path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

def canonical_page(part,pid):
    return BASE+"Heteropogon_contortus_"+part+"_("+pid+").jpg"

def fetch_original(session,part,pid,original_link):
    name=f"Heteropogon contortus {part} ({pid}).jpg"
    candidates=[original_link,"https://commons.wikimedia.org/wiki/Special:Redirect/file/"+quote(name)]
    errors=[]
    for u in candidates:
        for trial in range(2):
            try:
                r=session.get(u,timeout=40,allow_redirects=True)
                r.raise_for_status()
                if not 18000 < len(r.content) < 9_000_000:
                    raise RuntimeError("invalid content length")
                if not r.content[:3]==b"\xff\xd8\xff":
                    raise RuntimeError("not JPEG source bytes")
                return r.content,r.url
            except Exception as ex:
                errors.append(f"{type(ex).__name__}: {str(ex)[:90]}")
                time.sleep(2+trial*3)
    # No fallback to a different specimen or guessed URL.
    raise RuntimeError(f"Cannot retrieve exact Harry Rose {pid}; no publication. {errors}")

def jpeg_no_exif(raw, expected):
    with Image.open(io.BytesIO(raw)) as im:
        im.load()
        if im.format!="JPEG":
            raise ValueError("source not a JPEG")
        dims=im.size
        if dims!=expected:
            raise RuntimeError(f"source dimensions mismatch {dims} expected {expected}")
        clean=ImageOps.exif_transpose(im).convert("RGB")
    clean.thumbnail((2400,2400),Image.Resampling.LANCZOS)
    out=io.BytesIO()
    clean.save(out,format="JPEG",quality=92,optimize=True,progressive=True)
    payload=out.getvalue()
    if len(payload)<15000 or len(payload)>3_000_000:
        raise RuntimeError("processed JPEG outside size safeguards")
    with Image.open(io.BytesIO(payload)) as chk:
        if chk.format!="JPEG" or chk.getexif().get(34853):
            raise RuntimeError("JPEG/EXIF GPS QA failed")
        chk.verify()
    return payload,dims,clean.size

def main():
    s=json.loads(SPEC.read_text(encoding="utf8"))
    g=json.loads(GENUS.read_text(encoding="utf8"))
    assert s["id"]=="heteropogon-contortus" and s["scientific_name"]=="Heteropogon contortus"
    assert g["name"]=="Heteropogon" and g["project_scope"]["species_ids"]==["heteropogon-contortus"]
    original_science={k:json.dumps(s.get(k),sort_keys=True) for k in
       ("project_inclusion","county_occurrences_target_zone","native_target_zone_calculated",
        "target_zone_count","synonyms","taxonomic_note")}
    genus_scope=json.dumps(g["project_scope"],sort_keys=True)
    target=[]
    for part,pid,name,expected in PHOTOS:
        page=canonical_page(part,pid)
        matches=[x for x in s["images"] if x.get("source_page")==page]
        spanel=[x for x in s["visual_comparison"]["items"] if x.get("source_page")==page]
        gpanel=[x for x in g["visual_comparison"]["items"] if x.get("source_page")==page]
        if len(matches)!=1 or len(spanel)!=1 or len(gpanel)>1:
            raise RuntimeError("Photo-source count changed or duplicated for "+page)
        entry=matches[0]
        if entry["creator"]!="Harry Rose (Macleay Grass Man)" or entry["license"]!="CC BY 2.0" or entry["license_url"]!=LICENSE:
            raise RuntimeError("Photo individual author/license changed: "+page)
        if not entry["file"].startswith("https://upload.wikimedia.org/"):
            raise RuntimeError("Photo no longer the expected externally linked source: "+page)
        if spanel[0]["image_url"]!=entry["file"]:
            raise RuntimeError("Source entry/gallery out of sync for "+page)
        if any(x["image_url"]!=entry["file"] for x in gpanel):
            raise RuntimeError("Genus/gallery out of sync for "+page)
        dest=SPEC.parent/"images"/name
        if dest.exists() or any(x.get("file")=="images/"+name for x in s["images"]):
            raise RuntimeError("Destination photo already installed or partially installed: "+name)
        target.append((part,pid,name,expected,page,entry,spanel[0],gpanel,dest))
    if len(s["images"])!=9 or len(s["visual_comparison"]["items"])!=12 or len(g["visual_comparison"]["items"])!=7:
        raise RuntimeError("Concurrent edit changed card counts; refetch canonical first")
    with CSV.open("r",encoding="utf-8",newline="") as fh:
        reader=csv.DictReader(fh)
        cols=list(reader.fieldnames or [])
        rows=list(reader)
    if not cols or "file_name" not in cols:
        raise RuntimeError("Unexpected photo provenance CSV")
    staged=[]
    session=requests.Session()
    session.headers.update({"User-Agent":"HaysCountyBotanyResearchPhotoArchive/1.0 (public educational image attribution; github.com/Crking92/Hays-County-Botany)", "Accept":"image/jpeg,image/*"})
    for part,pid,name,expected,page,entry,spanel,gpanel,dest in target:
        raw,actual_source=fetch_original(session,part,pid,entry["file"])
        data,raw_dims,new_dims=jpeg_no_exif(raw,expected)
        staged.append((name,page,entry,spanel,gpanel,dest,raw,actual_source,data,raw_dims,new_dims))
        print("VALIDATED",pid,len(raw),len(data),raw_dims,new_dims,flush=True)

    report=[]
    for name,page,entry,spanel,gpanel,dest,raw,actual_source,data,raw_dims,new_dims in staged:
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(data)
        relative="images/"+name
        display_path=str(dest)
        entry.update({
          "file":relative,
          "source_image_original_url":entry["file"],
          "original_sha256":hashlib.sha256(raw).hexdigest(),
          "archived_sha256":hashlib.sha256(data).hexdigest(),
          "source_dimensions":list(raw_dims),
          "archived_dimensions":list(new_dims),
          "downloaded_from":actual_source,
          "image_status":"LOCALLY_ARCHIVED_PUBLIC_CC_BY_2_PROVISIONAL_USER_REVIEW",
          "public_reuse":"yes — CC BY 2.0 attribution, source and license link, modifications identified",
          "modifications":"Re-encoded to JPEG (max 2400px), stripped EXIF/GPS; photo content not retouched, browser arrows remain overlays.",
          "photo_review":entry.get("photo_review","")+" Physically archived exactly identified source bytes with image dimension QA, 2026-10-22."
        })
        for panel in [spanel,*gpanel]:
            panel["image_url"]=display_path
            panel["photo_status"]="PHYSICALLY ARCHIVED Harry Rose original CC BY 2.0 JPEG, resized where necessary and EXIF/GPS stripped; original source credited. PROVISIONAL — USER PHOTO REVIEW PENDING; no local Hays voucher or calibrated spikelet dissection."
        info={"file_name":name,"role":entry["role"],"creator":entry["creator"],"license":entry["license"],
          "source_page":page,"direct_url":actual_source,"study_use":"Public noncommercial field-ID learner",
          "public_reuse":"CC BY 2.0 source + attribution + modifications","observation_id":"",
          "photo_id":name.split("-")[2],"license_url":LICENSE,"modifications":entry["modifications"]}
        rows.append({k:info.get(k,"") for k in cols})
        report.append({"path":display_path,"source_page":page,"original_sha256":entry["original_sha256"],
          "archived_sha256":entry["archived_sha256"],"source_dimensions":list(raw_dims),
          "archive_dimensions":list(new_dims),"creator":entry["creator"],"license":entry["license"]})
    with CSV.open("w",newline="",encoding="utf8") as fh:
        writer=csv.DictWriter(fh,fieldnames=cols,lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    s["curation_status"]["photo_files_present"]=9
    s["curation_status"]["photo_metadata_count"]=9
    s["curation_status"]["harry_rose_original_jpegs_archived_20261022"]="Six real CC BY 2.0 Harry Rose photos physically stored with source hashes, attribution, metadata stripping and stable local gallery paths; anatomy holds remain."
    s["field_id_finish_pass"]["new_physical_photos"]=6
    s["field_id_finish_pass"]["existing_physical_photos_verified"]=9
    s["field_id_finish_pass"]["source_rights"]=(s["field_id_finish_pass"].get("source_rights","")+" Six Harry Rose CC BY 2.0 JPGs physically archived, original credit and rights retained.").strip()
    s["field_id_finish_pass"]["diagnostic_second_pass_20261022"]["new_physical_archive_files_followup"]=6
    s["field_id_finish_pass"]["diagnostic_second_pass_20261022"]["source_physical_archive_status"]="SIX_PHYSICALLY_ARCHIVED_FROM_VERIFIED_CC_BY_2_SOURCES"
    s["visual_comparison"]["subtitle"]+=" Harry Rose six anatomy photos now physically stored on GitHub (not external-only)."
    s["visual_comparison"]["overlay_note"]+=" Six Harry Rose originals saved as RGB JPEG in canonical images/ with EXIF/GPS removed. Existing overlay percentages preserved, not independently pixel audited after downscaling."
    s["field_photo_quickcheck"]["warning"]+=" Update: six Harry Rose source photos have now been archived as physical local JPEG copies and serve without Commons hotlink dependence."
    g["visual_comparison"]["subtitle"]+=" The three Harry Rose photo panels shown in this genus card now reference the same physical JPEG files archived in the species folder."
    g["visual_comparison"]["overlay_note"]=(g["visual_comparison"].get("overlay_note","")+" Six total source photos installed on species; three shared genus references now local and credited.").strip()
    g["curation_status"]["harry_rose_physical_sources_20261022"]="Three shown in genus, six unique licensed source files stored within Heteropogon contortus species images folder; no duplicate image bytes in genus."
    for key,orig in original_science.items():
        if json.dumps(s.get(key),sort_keys=True)!=orig:
            raise RuntimeError("Protected native/taxonomic/scientific state changed")
    if json.dumps(g["project_scope"],sort_keys=True)!=genus_scope:
        raise RuntimeError("Genus scope changed")
    assert len(s["visual_comparison"]["items"])==12 and len(g["visual_comparison"]["items"])==7
    assert sum(len(p.get("markers",[])) for p in s["visual_comparison"]["items"])==18
    assert all(i<12 for i in s["field_photo_quickcheck"]["featured_photo_indices"])
    save_json(SPEC,s)
    save_json(GENUS,g)
    save_json(REPORT,{"result":"SIX_HARRY_ROSE_CC_BY_2_JPEGS_ARCHIVED",
      "taxon":"Heteropogon contortus","files":report,"physical_files_added":6,
      "new_license_claims":0,"species_panels":12,"genus_panels":7,
      "same_source_rights_retained":True,"scientific_holds_unchanged":True,
      "diagnostic_status":"FIELD_READY_PHOTO_GAPS","new_anatomy_arrows":0,
      "last_mile":"Need attached scaled sessile/pedicellate spikelet pair, 2–3 mm bearded sharp callus, true 1mm local ligule and full awn."})
    save_json(MARK,{"type":"manual_field_id_publication","date":"2026-10-22",
      "title":"Real licensed tanglehead anatomy JPEGs physically archived and credited",
      "taxon":"Heteropogon contortus","report":str(REPORT),
      "image_files_added":6,"license":"CC BY 2.0 / Harry Rose","photos_local":True,
      "native_range_unchanged":True,"completion":"FIELD_READY_PHOTO_GAPS",
      "publish":"Rights-filtered public learner; provisional user photo review on species page."})
    print("SIX PHYSICAL SOURCES INSTALLED, 12 SPECIES PANELS, 7 GENUS PANELS",flush=True)

if __name__=="__main__":
    main()
