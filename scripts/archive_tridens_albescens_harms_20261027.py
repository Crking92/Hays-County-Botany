#!/usr/bin/env python3
"""Archive exact Bob Harms white tridens anatomy images, copyright retained.
Fail closed for any unverified file; partial successful exact photos permitted.
"""
import hashlib,io,json,time
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlparse
import requests
from PIL import Image,ImageOps
BASE="https://w3.biosci.utexas.edu/prc/Monocots/GrassHTML/data/"
LICENSE="© Bob Harms — scientific/educational use with attribution (NOT Creative Commons)"
RIGHTS="https://w3.biosci.utexas.edu/prc/Monocots/"
PERMIT="BOB_HARMS_SELECTED_MONOCOTS_EDU_WITH_CREDIT_20261022"
D=Path("content/taxa/Poaceae/Tridens")
SP=D/"tridens-albescens/species.json"
GP=D/"genus.json"
REPORT=Path("reports/tridens-albescens-real-harms-three-20261027.json")
MARK=Path("workflow/field-id-publication/2026-10-27-tridens-albescens-harms-real-anatomy.json")
SOURCE_IDS=("TRAL2-i1","TRAL2-J","TRAL2-9")
def dump(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
def download(pid):
    urls=[BASE+"images/"+pid+".jpg","https://www.biosci.utexas.edu/prc/Monocots/GrassHTML/data/images/"+pid+".jpg"]
    errors=[]
    for url in urls:
        for attempt in range(2):
            try:
                r=requests.get(url,timeout=30,headers={"Accept":"image/jpeg,image/*","User-Agent":"HaysBotanyEducationalPhotoArchive/1.0"})
                r.raise_for_status()
                if urlparse(r.url).hostname not in {"w3.biosci.utexas.edu","www.biosci.utexas.edu"}:
                    raise ValueError("Unexpected redirect host")
                raw=r.content
                if not raw.startswith(b"\xff\xd8\xff") or not (3000<len(raw)<4_000_000):
                    raise ValueError("Not actual source JPEG / bad length")
                with Image.open(io.BytesIO(raw)) as im:
                    im.load()
                    if im.format!="JPEG" or min(im.size)<145 or max(im.size)>4500:
                        raise ValueError("Implausible original JPEG dimensions")
                    before=list(im.size)
                    img=ImageOps.exif_transpose(im).convert("RGB")
                bio=io.BytesIO()
                img.save(bio,"JPEG",quality=94,optimize=True)
                cleaned=bio.getvalue()
                with Image.open(io.BytesIO(cleaned)) as check:
                    if check.getexif().get(34853):
                        raise ValueError("GPS metadata still present")
                    check.verify()
                return {"data":cleaned,"original_sha256":hashlib.sha256(raw).hexdigest(),
                        "archive_sha256":hashlib.sha256(cleaned).hexdigest(),
                        "dims":before,"archive_dims":list(img.size),"downloaded":r.url}
            except Exception as exc:
                errors.append(type(exc).__name__+": "+str(exc)[:140])
                time.sleep(1+attempt)
    return {"error":"; ".join(errors[-4:])}
def main():
    sp=json.loads(SP.read_text(encoding="utf8"));gn=json.loads(GP.read_text(encoding="utf8"))
    if sp.get("id")!="tridens-albescens" or gn.get("name")!="Tridens":
        raise RuntimeError("Canonical species/genus guard failure")
    byid={x.get("source_photo_id"):x for x in sp.get("images",[])}
    successful=[];blocked=[]
    for pid in SOURCE_IDS:
        if pid in byid:
            print("already archived",pid)
            continue
        d=download(pid)
        if "error" in d:
            blocked.append({"photo":pid,"error":d["error"]})
            continue
        path=SP.parent/"images"/("bob-harms-"+pid.lower()+".jpg")
        if path.exists():
            raise RuntimeError("Filename collision not present in canonical photo metadata: "+str(path))
        source=BASE+"pages/"+pid+".html"
        panels=[]
        for group in (sp,gn):
            matched=[x for x in group["visual_comparison"]["items"] if x.get("source_photo_id")==pid]
            if len(matched)!=1 or matched[0].get("source_page")!=source or matched[0].get("creator")!="Bob Harms":
                raise RuntimeError("Original source-preview mapping changed for "+pid)
            panels.append(matched[0])
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(d["data"])
        meta={"file":"images/"+path.name,
          "role":panels[0]["image_role"],"creator":"Bob Harms",
          "license":LICENSE,"license_url":RIGHTS,"source_page":source,
          "source_image":BASE+"images/"+pid+".jpg","source_taxon_name":"Tridens albescens",
          "source_photo_id":pid,"site_specific_public_permission":PERMIT,
          "public_reuse":"Yes, source-specific copyrighted Bob Harms educational/scientific use WITH photographer credit; NOT CC",
          "photo_status":"PHYSICALLY_STORED_AUTHOR_CREDITED_EXACT_ORIGINAL; no inferred microscopic arrows",
          "modifications":"Original photo re-encoded unaltered composition, EXIF and GPS removed",
          "original_sha256":d["original_sha256"],"archived_sha256":d["archive_sha256"],
          "source_dimensions":d["dims"],"archived_dimensions":d["archive_dims"],
          "downloaded_from":d["downloaded"]}
        sp["images"].append(meta)
        for panel in panels:
            panel["image_url"]=str(path)
            panel["photo_status"]="PHYSICALLY STORED in GitHub; exact Bob Harms scientific/educational copyrighted original with attribution; no anatomical arrows inferred"
        successful.append({"source_photo_id":pid,"path":str(path),"source_page":source,
          "original_dimensions":d["dims"],"archived_dimensions":d["archive_dims"],
          "original_sha256":d["original_sha256"],"archived_sha256":d["archive_sha256"]})
        print("VERIFIED",pid,d["dims"],len(d["data"]))
    if not successful:
        print("NO_NEW_PHOTOS",blocked)
        # Do not publish no-op; a failed source never becomes a canonical JPEG.
        return
    sp["curation_status"]["photo_files_present"]=sum(1 for im in sp["images"]
          if str(im.get("file","")).startswith("images/") and (SP.parent/im["file"]).is_file())
    sp["curation_status"]["photo_metadata_count"]=len(sp["images"])
    sp["curation_status"]["tridens_albescens_harms_archive_20261027"]=(
       f"{len(successful)} exact source photos physically archived from copyrighted credited Bob Harms Selected Monocots. "
       "Do not mark the true leaf ligule or detached lemma-vein hair macro complete; FIELD_READY_PHOTO_GAPS remains.")
    dump(SP,sp);dump(GP,gn)
    dump(REPORT,{"created_utc":datetime.now(timezone.utc).isoformat(),"result":"LICENSED_REAL_SOURCE_PHOTOS_ARCHIVED",
       "species":"Tridens albescens","number":len(successful),"records":successful,"blocks":blocked,
       "copyright":"Bob Harms scientific/educational WITH CREDIT; NOT Creative Commons",
       "photo_count":sp["curation_status"]["photo_files_present"],"panels":len(sp["visual_comparison"]["items"]),
       "last_mile":"True ciliate ligule with metric scale, connected living root-knot, separately oriented glume and lemma hair/vein macro."})
    dump(MARK,{"date":"2026-10-27","scope":"tridens-albescens","report":str(REPORT),
       "noncommercial_educational":True,"publication":"Strict rights-filtered Pages; verify success separately"})
    print("READY_FOR_PAGES",len(successful))
if __name__=="__main__":main()
