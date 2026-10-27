#!/usr/bin/env python3
"""Archive Bob Harms' four real M. involuta originals for the hybrid card.
The archived historic plate remains a distinct illustration. This archival pass
does not certify a herbarium voucher, hybrid parentage, or microscopic ID.
Only author's Selected Central Texas Monocots originals, scientifically and
educationally reusable WITH author credit; copyright retained, NOT CC.
"""
from __future__ import annotations
import hashlib,io,json,time
from pathlib import Path
from datetime import datetime,timezone
from urllib.parse import urlparse
import requests
from PIL import Image,ImageOps

BASE="https://w3.biosci.utexas.edu/prc/Monocots/GrassHTML/data/"
MIRROR="https://www.biosci.utexas.edu/prc/Monocots/GrassHTML/data/"
PERMISSION="BOB_HARMS_SELECTED_MONOCOTS_EDU_WITH_CREDIT_20261022"
LICENSE="© Bob Harms — scientific/educational use with attribution (NOT Creative Commons)"
LICENSE_URL="https://w3.biosci.utexas.edu/prc/Monocots/"
D=Path("content/taxa/Poaceae/Muhlenbergia")
SPEC=D/"muhlenbergia-x-involuta/species.json"
GEN=D/"genus.json"
REPORT=Path("reports/muhlenbergia-involuta-harms-four-actual-photos-20261027.json")
HOLD=Path("reports/muhlenbergia-involuta-harms-source-hold-20261027.json")
RELEASE=Path("workflow/field-id-publication/2026-10-27-muhlenbergia-involuta-actual-photo-archive.json")
PHOTOS=[
 ("MUIN-a","HABIT: source-labelled living canyon muhly clump","Actual source-identified living plant in natural habitat, NOT a dug or herbarium vouchered verified hybrid crown."),
 ("MUIN-I","PANICLE: source-labelled flowering head with scale","Real flowering panicle with a physical size scale, not sufficient to count every spikelet nerve."),
 ("MUIN-J","SPIKELET POSITION: flowering branch macro","Actual flowering branches and attached spikelets; details of glumes and lemma microscopic anatomy are not separately resolved."),
 ("MUIN-L","COLLAR: actual blade/sheath junction and ligule reference","Original source-identified leaf–sheath junction with printed scale. The photographed region is genuine, but fully lifted membrane and precise free ligule tip remain unproven.")
]
def put(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def fetch(s,id):
    errors=[]
    for base in (BASE,MIRROR):
        for attempt in range(2):
            try:
                r=s.get(base+"images/"+id+".jpg",timeout=35,headers={"Accept":"image/jpeg,image/*"})
                r.raise_for_status()
                if urlparse(r.url).hostname not in ("w3.biosci.utexas.edu","www.biosci.utexas.edu"):
                    raise ValueError("Untrusted redirect")
                raw=r.content
                if raw[:3]!=b"\xff\xd8\xff" or not 3000<len(raw)<5_000_000:
                    raise ValueError("Not a substantive JPEG original")
                with Image.open(io.BytesIO(raw)) as im:
                    im.load()
                    if im.format!="JPEG" or min(im.size)<130 or max(im.size)>7000:
                        raise ValueError("Unexpected JPEG image dimensions")
                    original=list(im.size)
                    clean=ImageOps.exif_transpose(im).convert("RGB")
                stream=io.BytesIO()
                clean.save(stream,"JPEG",quality=94,optimize=True)
                saved=stream.getvalue()
                with Image.open(io.BytesIO(saved)) as ck:
                    assert ck.format=="JPEG" and not ck.getexif().get(34853)
                    ck.verify()
                return {"data":saved,"original_sha256":hashlib.sha256(raw).hexdigest(),
                    "saved_sha256":hashlib.sha256(saved).hexdigest(),
                    "original_dimensions":original,"saved_dimensions":list(clean.size),
                    "downloaded_from":r.url}
            except Exception as ex:
                errors.append(type(ex).__name__+": "+str(ex)[:135])
                time.sleep(1+attempt)
    return {"error":"; ".join(errors[-4:])}
def main():
    sp=json.loads(SPEC.read_text(encoding="utf8"));gn=json.loads(GEN.read_text(encoding="utf8"))
    if sp.get("id")!="muhlenbergia-x-involuta" or gn.get("name")!="Muhlenbergia":
        raise RuntimeError("Changed taxon path")
    if not any("HITCHCOCK" in x.get("creator","").upper() or "Hitchcock" in x.get("creator","") for x in sp["images"]):
        raise RuntimeError("Previous historic illustration unexpectedly absent; reconcile")
    added=[];blocked=[]
    existing_ids={x.get("source_photo_id") for x in sp["images"]}
    sess=requests.Session()
    sess.headers["User-Agent"]="HaysBotanyEducationalRealGrassPhoto/1.0 (Crking92/Hays-County-Botany)"
    for id,role,caption in PHOTOS:
        if id in existing_ids:
            print("ALREADY_PRESENT",id);continue
        page=BASE+"pages/"+id+".html"
        sourceimage=BASE+"images/"+id+".jpg"
        filename="bob-harms-"+id.lower()+".jpg"
        dest=SPEC.parent/"images"/filename
        if dest.exists():raise RuntimeError("Image file exists but no matching source ID: "+str(dest))
        candidates=[]
        for group in (sp,gn):
            matches=[x for x in group.get("visual_comparison",{}).get("items",[]) if x.get("source_page")==page or x.get("source_photo_id")==id]
            if len(matches)>1:raise RuntimeError("Duplicate source-linked teaching panel "+id)
            if matches and matches[0].get("creator")!="Bob Harms":
                raise RuntimeError("Source author mismatch "+id)
            candidates.append(matches)
        found=fetch(sess,id)
        if "error" in found:
            blocked.append({"id":id,"issue":found["error"]});print("HOLD",id,flush=True);continue
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(found["data"])
        sp["images"].append({
          "file":"images/"+filename,"role":role,"creator":"Bob Harms",
          "license":LICENSE,"license_url":LICENSE_URL,"source_page":page,
          "source_image":sourceimage,"source_taxon_name":"Muhlenbergia involuta",
          "accepted_taxon_name":"Muhlenbergia ×involuta",
          "source_photo_id":id,"site_specific_public_permission":PERMISSION,
          "public_reuse":"Yes; original copyright Bob Harms, specific noncommercial scientific/educational use with proper photographer attribution only, NOT CC",
          "image_status":"PHYSICALLY_ARCHIVED_EXACT_ORIGINAL_AUTHOR_CREDITED; specimen voucher/hybrid parentage independent proof still pending",
          "modifications":"Original JPEG converted to RGB no crop, GPS/EXIF removed, no added anatomy pixels or arrows",
          "source_image_dimensions":found["original_dimensions"],"stored_dimensions":found["saved_dimensions"],
          "original_sha256":found["original_sha256"],"saved_sha256":found["saved_sha256"],
          "downloaded_from":found["downloaded_from"]
        })
        for group,match in zip((sp,gn),candidates):
            item={"label":role,"scientific_name":"Muhlenbergia ×involuta",
              "image_url":str(dest),"image_fit":"contain","image_role":role,
              "caption":caption+" Actual Bob Harms identification is published as Muhlenbergia involuta. Archival photos alone cannot independently certify hybrid origin.",
              "why_it_matters":"Genuine living exact-source photographs to complement the former historic illustration-only card.",
              "creator":"Bob Harms","license":LICENSE,"license_url":LICENSE_URL,
              "source_page":page,"source_image":sourceimage,"source_photo_id":id,
              "source_taxon_name":"Muhlenbergia involuta","accepted_taxon_name":"Muhlenbergia ×involuta",
              "site_specific_public_permission":PERMISSION,"markers":[],
              "photo_status":"Source-identified real Bob Harms original locally archived, scientific/educational credited use; NOT CC, no tiny structure arrows."}
            if match:
                old=match[0]
                for key in ("label","caption","image_role","why_it_matters"):
                    if old.get(key):item[key]=old[key]
                old.update(item)
            else:
                group["visual_comparison"]["items"].append(item)
        added.append({"id":id,"file":str(dest),"source":page,
                      "original_sha256":found["original_sha256"],"archived_sha256":found["saved_sha256"],
                      "original_dimensions":found["original_dimensions"],"archived_dimensions":found["saved_dimensions"]})
        print("VERIFIED",id,found["original_dimensions"],flush=True)
    if not added:
        put(HOLD,{"checked_utc":datetime.now(timezone.utc).isoformat(),"result":"NO_NEW_VERIFIED_PHOTOS","blocked":blocked})
        return
    sp["curation_status"]["photo_files_present"]=sum(1 for img in sp["images"]
        if str(img.get("file","")).startswith("images/") and (SPEC.parent/img["file"]).is_file())
    sp["curation_status"]["photo_metadata_count"]=len(sp["images"])
    sp["curation_status"]["involuta_four_exact_real_photos_20261027"]=(
        f"{len(added)} authentic real Bob Harms photographed canyon-muhly organs saved locally. Historic illustration remains separately. "
        "Source-identified hybrid photos are a FIELD ID reference, not independent genetic/voucher proof; true measured floret holds retained.")
    sp["curation_status"]["visual_finish"]="FIELD_READY_PHOTO_GAPS — living source-labelled canyon-muhly habit, head, branch and collar real photos; verified local hybrid voucher and mature microscopic diagnostic glumes still missing"
    put(SPEC,sp);put(GEN,gn)
    put(REPORT,{"date_utc":datetime.now(timezone.utc).isoformat(),
        "result":"MUHLENBERGIA_INVOLUTA_REAL_ORIGINAL_JPEGS_ARCHIVED",
        "added":len(added),"photos":added,"source_holds":blocked,
        "archive_count":sp["curation_status"]["photo_files_present"],
        "panels":len(sp["visual_comparison"]["items"]),
        "rights":"© Bob Harms Selected Monocots scientific and educational with attribution only, copyright retained, NOT CC",
        "limitations":"No independently verified wild hybrid voucher or measured mature glume/lemma; original Hitchcock drawing retained as illustration; no invented fine ligule arrows."})
    put(RELEASE,{"date":"2026-10-27","species":"muhlenbergia-x-involuta",
        "report":str(REPORT),"photo_rights":"Bob Harms source-specific credited educational only NOT CC",
        "publication":"Noncommercial rights-filtered Pages QA; confirm successful deployment independently"})
    print("ARCHIVAL_PASS",len(added))
if __name__=="__main__":main()
