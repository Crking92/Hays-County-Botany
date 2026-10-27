#!/usr/bin/env python3
"""Guarded real source-JPEG archive: Tridens flavus anatomy, Bob Harms originals.
Only 3 vetted Selected Central Texas Monocots photo IDs. Photographer retains
copyright; free for properly credited scientific/educational site display, NOT CC.
Never add invented anatomical arrows or transfer photo license between sources.
"""
from __future__ import annotations
import hashlib,io,json,time
from pathlib import Path
from datetime import datetime,timezone
from urllib.parse import urlparse
import requests
from PIL import Image,ImageOps

ROOT=Path(".")
D=ROOT/"content/taxa/Poaceae/Tridens"
SPEC=D/"tridens-flavus/species.json"
GEN=D/"genus.json"
REPORT=ROOT/"reports/tridens-flavus-harms-three-originals-20261027.json"
MARK=ROOT/"workflow/field-id-publication/2026-10-27-tridens-flavus-real-harms-anatomy.json"
HOLD=ROOT/"reports/tridens-flavus-harms-originals-source-hold-20261027.json"
BASE="https://w3.biosci.utexas.edu/prc/Monocots/GrassHTML/data/"
ALTERNATE="https://www.biosci.utexas.edu/prc/Monocots/GrassHTML/data/"
PERM="https://w3.biosci.utexas.edu/prc/Monocots/"
LICENSE="© Bob Harms — scientific/educational use with attribution (NOT Creative Commons)"
PERMID="BOB_HARMS_SELECTED_MONOCOTS_EDU_WITH_CREDIT_20261022"
# Original exact taxon/source pages checked against author Tridens genus index.
PHOTOS=[
 ("TRFL2-L", "PURPLETOP — real blade–sheath collar and ligule region",
  "Actual source-identified blade–sheath junction; examine inner ligule and collar hair region. The tiny free ligule tip must not be assigned a length or pixel arrow without an independently measurable microscope image.",
  "Photograph of the ACTUAL leaf collar of Tridens flavus, not a generic grass diagram."),
 ("TRFL2-9", "PURPLETOP — actual detached mature spikelet parts",
  "Source-identified mature detached spikelet and floral parts with metric reference; useful genuine reproduction photo. Specific glume/lemma veins and hairs must be confirmed on visible pixels before detailed pointers.",
  "Genuine source-taxon reproductive anatomy to compare with crowded attached spikelets."),
 ("TRFL2-j1", "PURPLETOP — attached flowering branches and units",
  "Actual narrow branchlets with attached spikelets during flowering. The overall reproductive branch architecture is visible; no tiny floret nerve claims from these pixels.",
  "Relates complete open purpletop panicle to the attached units and branches.")
]
def dump(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def fetch(session,pid):
    errors=[]
    for base in (BASE,ALTERNATE):
        for attempt in range(2):
            try:
                r=session.get(base+"images/"+pid+".jpg",timeout=32,headers={"Accept":"image/jpeg,image/*"})
                r.raise_for_status()
                if urlparse(r.url).hostname not in ("w3.biosci.utexas.edu","www.biosci.utexas.edu"):
                    raise ValueError("Unexpected source redirect host")
                raw=r.content
                if not raw.startswith(b"\xff\xd8\xff") or not (3000<len(raw)<5_000_000):
                    raise ValueError("Not a substantive source JPEG")
                with Image.open(io.BytesIO(raw)) as img:
                    img.load()
                    if img.format!="JPEG" or min(img.size)<125 or max(img.size)>6500:
                        raise ValueError("Unexpected original JPEG pixel dimensions")
                    source_dims=list(img.size)
                    clean=ImageOps.exif_transpose(img).convert("RGB")
                target=io.BytesIO()
                clean.save(target,"JPEG",quality=94,optimize=True)
                encoded=target.getvalue()
                with Image.open(io.BytesIO(encoded)) as ck:
                    assert ck.format=="JPEG" and not ck.getexif().get(34853)
                    ck.verify()
                return {"bytes":encoded,"original_sha256":hashlib.sha256(raw).hexdigest(),
                        "archived_sha256":hashlib.sha256(encoded).hexdigest(),
                        "original_dimensions":source_dims,"archived_dimensions":list(clean.size),
                        "downloaded_from":r.url}
            except Exception as exc:
                errors.append(f"{type(exc).__name__}: {str(exc)[:145]}")
                time.sleep(1+attempt)
    return {"error":"; ".join(errors[-4:])}

def main():
    sp=json.loads(SPEC.read_text(encoding="utf-8"))
    gn=json.loads(GEN.read_text(encoding="utf-8"))
    if sp.get("id")!="tridens-flavus" or gn.get("name")!="Tridens":
        raise RuntimeError("Canonical target species/genus changed")
    images=sp["images"]
    actual_ids={p.get("source_photo_id") for p in images}
    s=requests.Session()
    s.headers["User-Agent"]="HaysBotanyFieldPhotoSourceVerifier/1.0 (noncommercial botanical education; GitHub Crking92/Hays-County-Botany)"
    added=[];holds=[]
    for pid,label,caption,why in PHOTOS:
        if pid in actual_ids:
            continue
        source=BASE+"pages/"+pid+".html"
        image=BASE+"images/"+pid+".jpg"
        existing_files=(SPEC.parent/"images"/("bob-harms-"+pid.lower()+".jpg"))
        if existing_files.exists():
            raise RuntimeError("Unregistered photo path already exists: "+str(existing_files))
        payload=fetch(s,pid)
        if "error" in payload:
            holds.append({"source_photo_id":pid,"reason":payload["error"]})
            continue
        existing_files.parent.mkdir(parents=True,exist_ok=True)
        existing_files.write_bytes(payload["bytes"])
        meta={
            "file":"images/"+existing_files.name,
            "role":label,"creator":"Bob Harms","license":LICENSE,
            "license_url":PERM,"source_page":source,"source_image":image,
            "source_photo_id":pid,"source_taxon_name":"Tridens flavus",
            "site_specific_public_permission":PERMID,
            "public_reuse":"YES for this noncommercial scientific/educational site with proper Bob Harms credit; copyright retained, NOT CC",
            "photo_status":"PHYSICALLY_ARCHIVED_FROM_EXACT_ORIGINAL_BOB_HARMS; anatomy annotations unverified; review as provisional",
            "modifications":"RGB JPEG re-encode and original EXIF/GPS stripped; no pixel crops, overlays or altered composition",
            **{k:v for k,v in payload.items() if k!="bytes"}
        }
        images.append(meta)
        panel={
            "label":label,"scientific_name":"Tridens flavus",
            "image_url":str(existing_files),"image_fit":"contain",
            "image_role":label,"caption":caption,"why_it_matters":why,
            "creator":"Bob Harms","license":LICENSE,"license_url":PERM,
            "source_page":source,"source_image":image,
            "source_photo_id":pid,"source_taxon_name":"Tridens flavus",
            "site_specific_public_permission":PERMID,
            "modifications":meta["modifications"],
            "markers":[],
            "photo_status":"Source-verified exact species Bob Harms original physically saved in GitHub; educational credit only, NOT CC; no inferred microscope arrows"
        }
        for doc in (sp,gn):
            items=doc["visual_comparison"]["items"]
            old=[k for k,it in enumerate(items) if it.get("source_photo_id")==pid]
            if len(old)>1:raise RuntimeError("Duplicate exact source-ID gallery entry "+pid)
            if old:
                if items[old[0]].get("creator")!="Bob Harms" or items[old[0]].get("source_page")!=source:
                    raise RuntimeError("Existing photo provenance not matching author original "+pid)
                items[old[0]]=dict(panel)
            else:
                items.append(dict(panel))
        added.append({"source_photo_id":pid,"path":str(existing_files),
            "original_dimensions":payload["original_dimensions"],
            "archive_dimensions":payload["archived_dimensions"],
            "original_sha256":payload["original_sha256"],
            "archived_sha256":payload["archived_sha256"],"source_page":source})
        print("ARCHIVED",pid,payload["original_dimensions"],flush=True)
    if not added:
        dump(HOLD,{"date_utc":datetime.now(timezone.utc).isoformat(),
            "state":"NO_NEW_VERIFIED_JPEG_INSTALLED","blocked":holds,
            "already_present_ids":sorted(str(pid) for pid in actual_ids if pid in {r[0] for r in PHOTOS})})
        print("NOTHING_ARCHIVED",holds)
        return
    sp["curation_status"]["photo_files_present"]=sum(
        1 for x in images if str(x.get("file","")).startswith("images/")
        and (SPEC.parent/x["file"]).is_file())
    sp["curation_status"]["photo_metadata_count"]=len(images)
    sp["curation_status"]["purpletop_original_anatomy_20261027"]=(
       f"{len(added)} real exact-author Tridens flavus photographed organs physically stored with creator, source and permission. "
       "Unknown microscopic lemma vein and true tiny ligule-tip positions not arrowed; FIELD_READY_PHOTO_GAPS retained.")
    sp["learner_visual_status"]["status"]="FIELD_READY_PHOTO_GAPS"
    dump(SPEC,sp);dump(GEN,gn)
    dump(REPORT,{"date_utc":datetime.now(timezone.utc).isoformat(),
        "result":"EXACT_REAL_ORIGINAL_PURPLETOP_PHOTOS_ARCHIVED",
        "source":"Bob Harms Selected Central Texas Monocots",
        "copyright":"Bob Harms, credited scientific/educational use ONLY; NOT CC",
        "species":"Tridens flavus","number":len(added),"records":added,"blocked":holds,
        "photo_files_present":sp["curation_status"]["photo_files_present"],
        "teaching_panels":len(sp["visual_comparison"]["items"]),
        "remaining":"Actual calibrated free ligule edge and its cilia, connected rooted crown, attached mature spikelets and detached glumes/lemma nerves at 10–20× for exact Hays plant."})
    dump(MARK,{"date":"2026-10-27","species":"tridens-flavus","report":str(REPORT),
        "publisher":"noncommercial rights-filtered Pages; QA must pass before declaring photos live"})
    print("REAL_PHOTOS_INSTALLED",len(added))
if __name__=="__main__":
    main()
