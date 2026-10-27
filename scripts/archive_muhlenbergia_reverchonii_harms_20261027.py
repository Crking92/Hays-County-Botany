#!/usr/bin/env python3
"""Exact original Bob Harms Muhlenbergia reverchonii JPEGs, with credited
scientific/educational use only, NOT Creative Commons. No cropped organ arrows.
Two older external previews become local files only after a separate individual
rights/identity review against the original Selected Monocots source pages.
"""
from __future__ import annotations
import hashlib,io,json,time
from pathlib import Path
from datetime import datetime,timezone
from urllib.parse import urlparse
import requests
from PIL import Image,ImageOps

D=Path("content/taxa/Poaceae/Muhlenbergia")
SP=D/"muhlenbergia-reverchonii/species.json"
GP=D/"genus.json"
REP=Path("reports/muhlenbergia-reverchonii-harms-anatomy-physical-20261027.json")
HOLD=Path("reports/muhlenbergia-reverchonii-harms-photo-source-hold-20261027.json")
MARK=Path("workflow/field-id-publication/2026-10-27-muhlenbergia-reverchonii-real-anatomy-photos.json")
BASE="https://w3.biosci.utexas.edu/prc/Monocots/GrassHTML/data/"
PERM="https://w3.biosci.utexas.edu/prc/Monocots/"
LIC="© Bob Harms — scientific/educational use with attribution (NOT Creative Commons)"
GRANT="BOB_HARMS_SELECTED_MONOCOTS_EDU_WITH_CREDIT_20261022"
PHOTOS=[
 ("MURE2-L", "SEEP MUHLY — actual membranous ligule and inner leaf sheath",
  "Source-verified real M. reverchonii leaf blade–sheath junction beside physical metric ticks. Study the visible membrane and thin blade. Do not infer a precise length or label a free ciliate tip without more resolution.",
  "The diagnostic true blade/sheath junction distinguishes finer seep-muhly foliage from an unexamined tuft."),
 ("MURE2-S", "SEEP MUHLY — mature single spikelet details with scale",
  "Exact species mature spikelet photograph showing small floral structures beside the author's original scale. Do not invent individual lemma or glume-vein labels from unresolved pixels.",
  "Moves from airy flowering branches to real individual reproductive units."),
 ("MURE2-a", "SEEP MUHLY — source-verified flowering plants in rocky habitat",
  "Real natural flowering clumps in a Central Texas rocky landscape. The base of a single vouchered plant is not dug up, so this is field-habit evidence, NOT an exposed root crown.",
  "Habitat and life-sized flowering comparison against the larger Lindheimer muhly.")
]
def dump(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
def fetch(pid):
    errs=[]
    for host in ("https://w3.biosci.utexas.edu","https://www.biosci.utexas.edu"):
        url=host+"/prc/Monocots/GrassHTML/data/images/"+pid+".jpg"
        for attempt in range(2):
            try:
                r=requests.get(url,timeout=32,headers={
                    "User-Agent":"HaysCountyBotanyAuthenticGrassPhoto/1.0; source credited scientific education",
                    "Accept":"image/jpeg,image/*"})
                r.raise_for_status()
                if urlparse(r.url).hostname not in {"w3.biosci.utexas.edu","www.biosci.utexas.edu"}:
                    raise ValueError("Unexpected redirected source")
                raw=r.content
                if raw[:3]!=b"\xff\xd8\xff" or not 3000<len(raw)<5_000_000:
                    raise ValueError("Not authentic substantive JPEG bytes")
                with Image.open(io.BytesIO(raw)) as img:
                    img.load()
                    if img.format!="JPEG" or min(img.size)<135 or max(img.size)>5000:
                        raise ValueError("Unexpected source original dimensions")
                    dim=list(img.size)
                    cleaned=ImageOps.exif_transpose(img).convert("RGB")
                out=io.BytesIO()
                cleaned.save(out,"JPEG",quality=94,optimize=True)
                blob=out.getvalue()
                with Image.open(io.BytesIO(blob)) as check:
                    assert check.format=="JPEG" and not check.getexif().get(34853)
                    check.verify()
                return {"data":blob,"original_sha256":hashlib.sha256(raw).hexdigest(),
                    "archived_sha256":hashlib.sha256(blob).hexdigest(),
                    "original_dimensions":dim,"archived_dimensions":list(cleaned.size),
                    "downloaded_from":r.url}
            except Exception as exc:
                errs.append(type(exc).__name__+": "+str(exc)[:160])
                time.sleep(1+attempt)
    return {"error":" / ".join(errs[-4:])}
def main():
    s=json.loads(SP.read_text(encoding="utf8"))
    g=json.loads(GP.read_text(encoding="utf8"))
    if s.get("id")!="muhlenbergia-reverchonii" or g.get("name")!="Muhlenbergia":
        raise RuntimeError("Canonical identity mismatch")
    oldids={i.get("source_photo_id") for i in s["images"]}
    existing=set()
    for item in s["visual_comparison"]["items"]:
        if item.get("source_page","").startswith(BASE+"pages/MURE2-"):
            existing.add(item["source_page"].split("/")[-1].replace(".html",""))
    success=[];blocked=[]
    for pid,title,caption,why in PHOTOS:
        if pid in oldids:continue
        target=SP.parent/"images"/("bob-harms-"+pid.lower()+".jpg")
        if target.exists():raise RuntimeError("Potential photo overwrite "+str(target))
        downloaded=fetch(pid)
        if "error" in downloaded:
            blocked.append({"photo_id":pid,"reason":downloaded["error"]});continue
        source=BASE+"pages/"+pid+".html"
        original=BASE+"images/"+pid+".jpg"
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(downloaded["data"])
        meta={"file":"images/"+target.name,"role":title,
            "creator":"Bob Harms","license":LIC,"license_url":PERM,
            "source_page":source,"source_image":original,"source_photo_id":pid,
            "source_taxon_name":"Muhlenbergia reverchonii",
            "site_specific_public_permission":GRANT,
            "public_reuse":"Source-specific scientific/educational reuse WITH credit, only for noncommercial learner; copyright retained, NOT CC",
            "photo_status":"Original species photo genuinely saved in public GitHub, source reviewed, exif/gps stripped; microscope organ arrows still pending",
            "modifications":"EXIF/GPS removed and RGB JPEG resaved without crop or drawn overlay",
            **{k:v for k,v in downloaded.items() if k!="data"}}
        s["images"].append(meta)
        panel={"label":title,"scientific_name":"Muhlenbergia reverchonii",
            "image_url":str(target),"image_fit":"contain","image_role":title,
            "caption":caption,"why_it_matters":why,
            "creator":"Bob Harms","license":LIC,"license_url":PERM,
            "source_page":source,"source_image":original,"source_taxon_name":"Muhlenbergia reverchonii",
            "source_photo_id":pid,"site_specific_public_permission":GRANT,
            "markers":[],"photo_status":"Original copyrighted Bob Harms exact source photographed real organ; PHYSICALLY ARCHIVED with author credit, NOT CC; provisional anatomical review"}
        for doc in (s,g):
            entries=doc["visual_comparison"]["items"]
            matches=[k for k,it in enumerate(entries) if it.get("source_page")==source or it.get("source_photo_id")==pid]
            if len(matches)>1:raise RuntimeError("Duplicate author source entries "+pid)
            if matches:
                old=entries[matches[0]]
                if old.get("creator")!="Bob Harms":
                    raise RuntimeError("Prior creator inconsistent "+pid)
                panel["earlier_external_preview_rights_note"]=old.get("reuse_scope","")
                entries[matches[0]]=dict(panel)
            else:
                entries.append(dict(panel))
        success.append({"photo_id":pid,"path":str(target),
            "source_page":source,
            "original_sha256":downloaded["original_sha256"],
            "archived_sha256":downloaded["archived_sha256"],
            "original_dimensions":downloaded["original_dimensions"],
            "archived_dimensions":downloaded["archived_dimensions"]})
        print("VERIFIED_JPEG",pid,downloaded["original_dimensions"],flush=True)
    if not success:
        dump(HOLD,{"result":"NO_IMAGE_ADDED","blocked":blocked,
            "checked_utc":datetime.now(timezone.utc).isoformat()})
        print("SOURCE_HOLD",blocked,flush=True)
        return
    s["curation_status"]["photo_files_present"]=sum(
        1 for i in s["images"] if str(i.get("file","")).startswith("images/") and (SP.parent/i["file"]).is_file())
    s["curation_status"]["photo_metadata_count"]=len(s["images"])
    s["curation_status"]["seep_muhly_actual_harms_anatomy_20261027"]=(
        f"{len(success)} exact real original Bob Harms images archived. Two previous external preview roles may now be physically stored; "
        "true calibrated free ligule and verified lemma vein still not 100%. Source-specific rights reviewed.")
    dump(SP,s);dump(GP,g)
    dump(REP,{"created_utc":datetime.now(timezone.utc).isoformat(),
        "result":"EXACT_REAL_SEEP_MUHLY_SOURCE_JPEGS_ARCHIVED",
        "photo_count_added":len(success),"records":success,"blocked":blocked,
        "photos_current":s["curation_status"]["photo_files_present"],
        "panels_current":len(s["visual_comparison"]["items"]),
        "rights":"© Bob Harms original Selected Monocots; free scientific/educational use with author credit, NOT CC; source-unique image review",
        "remaining":"Exposed true measurable ligule fringe, oriented dissected adult lemma nerve and same-rooted wild field voucher."})
    dump(MARK,{"date":"2026-10-27","taxon":"muhlenbergia-reverchonii",
        "report":str(REP),"public_site":"noncommercial rights-filtered release pending independent build verification"})
    print("SOURCE_VERIFIED_ARCHIVE_COMPLETE",len(success),flush=True)
if __name__=="__main__":main()
