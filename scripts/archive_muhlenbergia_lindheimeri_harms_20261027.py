#!/usr/bin/env python3
"""Fail-closed exact-source Bob Harms Lindheimer muhly photographic archive.
Only original Selected Central Texas Monocots MULI-L, -9, -J4, -J5.
Bob Harms retains copyright; educational use with proper photographer credit.
No crop, arrows, substituted species photos, or commercial reuse.
"""
from __future__ import annotations
import hashlib, io, json, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
import requests
from PIL import Image, ImageOps

ROOT=Path(".")
BASE="https://w3.biosci.utexas.edu/prc/Monocots/GrassHTML/data/"
ALT="https://www.biosci.utexas.edu/prc/Monocots/GrassHTML/data/"
PERMISSION="https://w3.biosci.utexas.edu/prc/Monocots/"
LIC="© Bob Harms — scientific/educational use with attribution (NOT Creative Commons)"
PERMIT_ID="BOB_HARMS_SELECTED_MONOCOTS_EDU_WITH_CREDIT_20261022"
DIR=ROOT/"content/taxa/Poaceae/Muhlenbergia"
SPEC=DIR/"muhlenbergia-lindheimeri/species.json"
GEN=DIR/"genus.json"
REPORT=ROOT/"reports/muhlenbergia-lindheimeri-harms-four-photos-20261027.json"
RELEASE=ROOT/"workflow/field-id-publication/2026-10-27-muhlenbergia-lindheimeri-harms-anatomy.json"

PHOTOS=[
 ("MULI-L", "Ligule / sheath", "Exact-species leaf blade–sheath junction with long membranous ligule and millimeter ticks",
  "The pale papery ligule and folded leaf/sheath region are photographed alongside a printed millimeter scale. Examine the membrane and tightly folded blades. Do not infer its length solely from the web thumbnail or mistake outer sheath tissue for the free margin."),
 ("MULI-9", "Mature spikelet dissection", "Detached flowering structures of actual Lindheimer muhly beside printed metric scale",
  "Several isolated ripe spikelets and their separate parts appear beside a graduated scale. One-flowered units and small awn states are visible; orientation and exact glume versus lemma assignment require a matched dissection and should not be arrow-labeled from this compact frame."),
 ("MULI-J4", "Attached flowering panicle", "Panicle branch junction and mature crowded spikelets beside millimeter ticks",
  "Three connected close views show the attached lateral flowering branches and tightly packed pale spikelets; printed ticks provide an approximate scale for close observation, not a substitute for dissection."),
 ("MULI-J5", "Anthers / florets", "Actual purple protruding anthers on living Lindheimer muhly flowering spikelets",
  "Actual dark purple exserted anthers and pale spikelet bodies are visible on branching flower stems beside a metric strip. These are the stamens of open florets; individual lemma/glume veins are not fully separable."),
]
def write_json(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def fetch_photo(session,pid):
    failures=[]
    for base in (BASE,ALT):
        url=base+"images/"+pid+".jpg"
        for attempt in range(2):
            try:
                r=session.get(url,timeout=35,headers={"Accept":"image/jpeg,image/*"},allow_redirects=True)
                r.raise_for_status()
                if urlparse(r.url).hostname not in ("w3.biosci.utexas.edu","www.biosci.utexas.edu"):
                    raise ValueError("Unexpected redirect origin")
                raw=r.content
                if not raw.startswith(b"\xff\xd8\xff") or not (3000<len(raw)<5_000_000):
                    raise ValueError("Not an actual appropriate JPEG")
                with Image.open(io.BytesIO(raw)) as im:
                    im.load()
                    if im.format!="JPEG" or min(im.size)<140 or max(im.size)>5000:
                        raise ValueError("Unexpected source dimensions (Bob Harms original may be a narrow 163px-wide ligule macro): "+repr(im.size))
                    dims=list(im.size)
                    clean=ImageOps.exif_transpose(im).convert("RGB")
                out=io.BytesIO()
                clean.save(out,"JPEG",quality=94,optimize=True)
                blob=out.getvalue()
                with Image.open(io.BytesIO(blob)) as ck:
                    ck.verify()
                return dict(data=blob,raw_sha=hashlib.sha256(raw).hexdigest(),
                    sha=hashlib.sha256(blob).hexdigest(),dims=dims,
                    saved_dims=list(clean.size),downloaded_from=r.url)
            except Exception as exc:
                failures.append(type(exc).__name__+": "+str(exc)[:180])
                time.sleep(1+attempt)
    raise RuntimeError(pid+": "+" | ".join(failures[-4:]))

def main():
    sp=json.loads(SPEC.read_text(encoding="utf-8"))
    gen=json.loads(GEN.read_text(encoding="utf-8"))
    if sp["id"]!="muhlenbergia-lindheimeri" or gen["name"]!="Muhlenbergia":
        raise RuntimeError("Canonical target mismatch")
    existing=sp.get("images",[])
    oldfiles={p.name for p in (SPEC.parent/"images").glob("*.jpg")}
    oldids={x.get("source_photo_id") for x in existing}
    if all(pid in oldids for pid,*_ in PHOTOS):
        print("ALREADY_ARCHIVED: exact source files previously installed")
        return
    s=requests.Session()
    s.headers["User-Agent"]="HaysCountyBotany-LindheimerPhotoArchive/1.0 (educational attribution, github.com/Crking92/Hays-County-Botany)"
    incoming=[]
    blockers=[]
    for pid,title,role,caption in PHOTOS:
        if pid in oldids:
            continue
        try:
            downloaded=fetch_photo(s,pid)
        except Exception as exc:
            blockers.append(str(exc))
            continue
        filename="bob-harms-"+pid.lower()+".jpg"
        if filename in oldfiles or (SPEC.parent/"images"/filename).exists():
            raise RuntimeError("Existing file without matching photo provenance: "+filename)
        incoming.append((pid,title,role,caption,filename,downloaded))
        print("SOURCE VERIFIED",pid,downloaded["dims"],downloaded["sha"])
    good=oldids | {a[0] for a in incoming}
    if not {"MULI-L","MULI-9"}.issubset(good):
        raise RuntimeError("Fail closed: true ligule reference and spikelet dissection BOTH required. "+repr(blockers))
    if not incoming:
        raise RuntimeError("No new photos acquired; no report or release marker")
    records=[]
    for pid,title,role,caption,filename,dl in incoming:
        target=SPEC.parent/"images"/filename
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(dl["data"])
        source_page=BASE+"pages/"+pid+".html"
        source_image=BASE+"images/"+pid+".jpg"
        metadata={
            "file":"images/"+filename,"role":role,"creator":"Bob Harms","license":LIC,
            "license_url":PERMISSION,"source_page":source_page,"source_image":source_image,
            "source_taxon_name":"Muhlenbergia lindheimeri","source_photo_id":pid,
            "site_specific_public_permission":PERMIT_ID,
            "source_collection":"Selected Central Texas Monocots — Bob Harms originals (NOT UT specimen archive)",
            "public_reuse":"yes; copyrighted Bob Harms scientific/educational site-use with visible attribution only; NOT CC",
            "photo_status":"PHYSICALLY_ARCHIVED_ORIGINAL_AUTHOR_EDUCATIONAL_PERMISSION; PROVISIONAL_FIELD_DIAGNOSTIC",
            "modifications":"Photo resaved without EXIF/GPS metadata, without crop, labels or compositing",
            "original_sha256":dl["raw_sha"],"archived_sha256":dl["sha"],
            "original_dimensions":dl["dims"],"archived_dimensions":dl["saved_dims"],
            "downloaded_from":dl["downloaded_from"]
        }
        sp["images"].append(metadata)
        image_url=str(target)
        panel={
            "label":title+" — Bob Harms actual anatomy",
            "scientific_name":"Muhlenbergia lindheimeri","image_url":image_url,
            "image_fit":"contain","image_role":role,"caption":caption,
            "why_it_matters":role,"creator":"Bob Harms","license":LIC,
            "license_url":PERMISSION,"source_page":source_page,"source_image":source_image,
            "source_photo_id":pid,"source_taxon_name":"Muhlenbergia lindheimeri",
            "site_specific_public_permission":PERMIT_ID,
            "modifications":metadata["modifications"],
            "markers":[],
            "photo_status":"Physical JPEG in GitHub, exact Bob Harms Selected Monocots copyrighted original; permission for this credited noncommercial educational learner, NOT CC; anatomical arrows intentionally not guessed."
        }
        # If a credited external source preview was already placed in the learner,
        # replace that exact photo-ID panel with the LOCAL archived file, do not duplicate.
        for collection in (sp["visual_comparison"]["items"], gen["visual_comparison"]["items"]):
            found=[i for i,x in enumerate(collection) if x.get("source_photo_id")==pid]
            if len(found)>1:
                raise RuntimeError("Duplicate external photo panels; manual reconciliation required: "+pid)
            if found:
                old=collection[found[0]]
                if old.get("source_page")!=source_page or old.get("creator")!="Bob Harms":
                    raise RuntimeError("Changed external photo provenance: "+pid)
                collection[found[0]]=dict(panel)
            else:
                collection.append(dict(panel))
        records.append({k:metadata[k] for k in ("file","source_photo_id","creator","license","source_page","source_image","original_sha256","archived_sha256","original_dimensions","archived_dimensions")})
    sp["curation_status"]["photo_files_present"]=sum(1 for x in sp["images"] if x.get("file","").startswith("images/") and (SPEC.parent/x["file"]).is_file())
    sp["curation_status"]["photo_metadata_count"]=len(sp["images"])
    sp["curation_status"]["lindheimer_muhly_real_anatomy_20261027"]=(
        str(len(incoming))+" exact species original Bob Harms macro photographs physically archived; "
        "true ligule zone, detached mature spikelets and attached flowering structures. "
        "No new microscopic arrows guessed. FIELD_READY_PHOTO_GAPS preserved."
    )
    sp["visual_comparison"]["subtitle"]=(
        "Lindheimer's muhly: real species-specific photographed inner ligule zone, "
        "isolated spikelet dissection, attached flowering branches and dark exserted anthers; "
        "the original whole-plant and distinct seep-muhly comparison are preserved."
    )
    sp["learner_visual_status"]["status"]="FIELD_READY_PHOTO_GAPS"
    sp["learner_visual_status"]["image_count"]=len(sp["images"])
    sp["learner_visual_status"]["note"]="True species-specific macro source images added. An entirely rooted voucher and high-resolution orientated glume/lemma dissection remain the final strict holds."
    write_json(SPEC,sp)
    write_json(GEN,gen)
    report={"created_utc":datetime.now(timezone.utc).isoformat(),
        "status":"REAL_EXACT_SPECIES_JPEG_ARCHIVE_SUCCESS",
        "target":"muhlenbergia-lindheimeri",
        "permission":PERMISSION,"permission_id":PERMIT_ID,
        "rights":"© Bob Harms, educational/scientific use WITH photographer credit only; NOT Creative Commons",
        "archived_added":len(incoming),"gallery_items_added":len(incoming),
        "source_ids_added":[p[0] for p in incoming],"records":records,"source_failures":blockers,
        "photo_files_present":sp["curation_status"]["photo_files_present"],
        "science_holds":"No exposed connected root crown or same-voucher root→head series; orientation of individual glume/lemma still unverified; no arrows on newly copyrighted originals",
        "publication":"Release marker created; live Pages result needs separate success/readback verification"}
    write_json(REPORT,report)
    write_json(RELEASE,{"requested_by":"Grass Photo Finish Lane 3","date":"2026-10-27",
        "scope":["muhlenbergia-lindheimeri"],"noncommercial":True,
        "rights_preflight_required":True,"photo_identity":"Bob Harms MULI-L, -9, -J4, -J5 source originals; only physically verified files published",
        "report":str(REPORT)})
    print(json.dumps({k:report[k] for k in ("status","archived_added","photo_files_present","source_ids_added","source_failures")},indent=2))
if __name__=="__main__":
    main()
