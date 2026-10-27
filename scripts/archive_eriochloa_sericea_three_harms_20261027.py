#!/usr/bin/env python3
"""Three original Bob Harms E. sericea photos: real attached spikelets,
flowering anthers/stigmas, and culm/sheath hairs (NOT an inner ligule).
Source-specific credited educational use with copyright retained, NOT CC.
"""
import hashlib,io,json,time
from pathlib import Path
from datetime import datetime,timezone
from urllib.parse import urlparse
import requests
from PIL import Image,ImageOps

BASE="https://w3.biosci.utexas.edu/prc/Monocots/GrassHTML/data/"
ALTERNATE="https://www.biosci.utexas.edu/prc/Monocots/GrassHTML/data/"
LICENSE="© Bob Harms — scientific/educational use with attribution (NOT Creative Commons)"
LICURL="https://w3.biosci.utexas.edu/prc/Monocots/"
PERM="BOB_HARMS_SELECTED_MONOCOTS_EDU_WITH_CREDIT_20261022"
D=Path("content/taxa/Poaceae/Eriochloa")
SP=D/"eriochloa-sericea/species.json"
GEN=D/"genus.json"
REPORT=Path("reports/lane3-eriochloa-sericea-harms-attached-photos-20261027.json")
HOLD=Path("reports/lane3-eriochloa-sericea-harms-source-hold-20261027.json")
RELEASE=Path("workflow/field-id-publication/2026-10-27-eriochloa-sericea-harms-anatomy.json")
PHOTOS=[
 ("ERSE5-j","ATTACHED MATURING SPIKELETS — hairy short branch",
 "A true source-identified Texas cupgrass flowering branch with attached spikelets, long bristly hairs and a photographed scale strip. Attachment visible, but the cup-shaped basal callus is not unambiguously exposed/outlined at this angle.",
 "What an attached flowering unit looks like before dissecting the cup; do not claim the basal cup from this angle."),
 ("ERSE5-J1","OPEN FLOWERS — real exserted anthers and feathery stigmas",
 "Real green attached E. sericea flowering spikelets with dark projecting anthers and feathery purple/brown stigma branches. The external flowers are unmistakable; tiny glume/lemma and basal cup identity not arrow-labeled.",
 "Teaches that dark protruding parts are reproductive organs rather than ripe caryopses."),
 ("ERSE5-C","SHEATH AND CULM SURFACES — visible hairs, NOT true ligule",
 "Bob Harms multi-view photograph of actual hairy E. sericea lower culm/sheath and leaf/culm junctions with scale. The INNER blade-sheath junction and free ligule fringe are NOT opened or independently visible. No 'ligule' arrow belongs on these sheath hairs.",
 "Shows real surface pubescence while preventing a common beginner mistake: treating any sheath hair as the true ligule.")
]
def write(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def fetch(pid):
    errors=[]
    for base in (BASE,ALTERNATE):
        for attempt in range(2):
            try:
                r=requests.get(base+"images/"+pid+".jpg",timeout=35,headers={
                  "User-Agent":"HaysCountyBotany-CreditedOriginalGrass/1.0 (science/education)", "Accept":"image/jpeg,image/*"})
                r.raise_for_status()
                if urlparse(r.url).hostname not in ("w3.biosci.utexas.edu","www.biosci.utexas.edu"):
                    raise ValueError("Unknown photo source")
                data=r.content
                if data[:3]!=b"\xff\xd8\xff" or not 3000<len(data)<5_000_000:
                    raise ValueError("Incorrect source JPEG bytes")
                with Image.open(io.BytesIO(data)) as img:
                    img.load()
                    if img.format!="JPEG" or min(img.size)<125 or max(img.size)>6000:
                        raise ValueError("Unexpected original image dimensions")
                    dims=list(img.size)
                    clean=ImageOps.exif_transpose(img).convert("RGB")
                out=io.BytesIO()
                clean.save(out,"JPEG",quality=94,optimize=True)
                cleaned=out.getvalue()
                with Image.open(io.BytesIO(cleaned)) as test:
                    assert test.format=="JPEG" and not test.getexif().get(34853)
                    test.verify()
                return {"blob":cleaned,"source_sha256":hashlib.sha256(data).hexdigest(),
                  "archive_sha256":hashlib.sha256(cleaned).hexdigest(),
                  "source_dimensions":dims,"archive_dimensions":list(clean.size),
                  "downloaded_from":r.url}
            except Exception as e:
                errors.append(f"{type(e).__name__}: {str(e)[:150]}")
                time.sleep(1+attempt)
    return {"error":" | ".join(errors[-4:])}
def main():
    s=json.loads(SP.read_text(encoding="utf-8"))
    genus=json.loads(GEN.read_text(encoding="utf-8"))
    if s.get("id")!="eriochloa-sericea" or genus.get("name")!="Eriochloa":
        raise RuntimeError("Species/genus mismatch")
    if not any(str(im.get("source_page","")).endswith("/ERSE5-9.html") for im in s["images"]):
        raise RuntimeError("Existing real Bob Harms basal cup anatomical photo missing; reconcile first")
    old={str(x.get("source_photo_id")) for x in s["images"]}
    installed=[];blocked=[]
    for pid,label,caption,why in PHOTOS:
        if pid in old:continue
        sourcepage=BASE+"pages/"+pid+".html"
        sourceimage=BASE+"images/"+pid+".jpg"
        if any(x.get("source_page")==sourcepage for x in s["images"]):
            raise RuntimeError("Duplicated source record without source ID: "+pid)
        filename="bob-harms-"+pid.lower()+".jpg"
        local=SP.parent/"images"/filename
        if local.exists():raise RuntimeError("Existing image destination not listed in canonical source record")
        image=fetch(pid)
        if "error" in image:
            blocked.append({"photo_id":pid,"reason":image["error"]})
            print("SOURCE_HOLD",pid,image["error"],flush=True)
            continue
        local.parent.mkdir(parents=True,exist_ok=True)
        local.write_bytes(image["blob"])
        meta={"file":"images/"+filename,"role":label,"creator":"Bob Harms",
          "license":LICENSE,"license_url":LICURL,
          "source_page":sourcepage,"source_image":sourceimage,
          "source_photo_id":pid,"source_taxon_name":"Eriochloa sericea",
          "site_specific_public_permission":PERM,
          "public_reuse":"Bob Harms original Selected Central Texas Monocots copyright retained; properly credited scientific/educational use only, NOT CC",
          "photo_status":"ORIGINAL_JPEG_PHYSICALLY_ARCHIVED; fine anatomical role held until actual exposed membrane or basal cup is visible",
          "modifications":"Original RGB composition preserved, EXIF/GPS removed; no cropping or pixel arrows",
          **{k:v for k,v in image.items() if k!="blob"}}
        s["images"].append(meta)
        panel={
          "label":label,"scientific_name":"Eriochloa sericea",
          "image_url":str(local),"image_fit":"contain",
          "image_role":label,"caption":caption,"why_it_matters":why,
          "creator":"Bob Harms","license":LICENSE,"license_url":LICURL,
          "source_page":sourcepage,"source_image":sourceimage,
          "source_photo_id":pid,"source_taxon_name":"Eriochloa sericea",
          "site_specific_public_permission":PERM,
          "markers":[],"photo_status":"Genuine copyrighted Bob Harms original photographic specimen archived, educational use with credit, NOT CC; conservative structure ID only"}
        for doc in (s,genus):
            items=doc["visual_comparison"]["items"]
            if any(x.get("source_page")==sourcepage or x.get("source_photo_id")==pid for x in items):
                raise RuntimeError("Duplicated exact source teaching panel "+pid)
            items.append(dict(panel))
        installed.append({"id":pid,"local":str(local),"source":sourcepage,
          "source_dimensions":image["source_dimensions"],"archived_dimensions":image["archive_dimensions"],
          "original_sha256":image["source_sha256"],"archived_sha256":image["archive_sha256"]})
        print("REAL_SOURCE_ARCHIVED",pid,image["source_dimensions"],flush=True)
    if not installed:
        write(HOLD,{"checked_at":datetime.now(timezone.utc).isoformat(),
          "result":"NO_NEW_VERIFIED_ARCHIVE","blocked":blocked})
        return
    s["curation_status"]["photo_files_present"]=sum(
        1 for x in s["images"] if str(x.get("file","")).startswith("images/") and (SP.parent/x["file"]).is_file())
    s["curation_status"]["photo_metadata_count"]=len(s["images"])
    s["curation_status"]["lane3_cupgrass_real_harms_20261027"]=(
       f"{len(installed)} original-source Bob Harms photos added for hairy attached heads, opened flower organs and culm/sheath hairs. "
       "A REAL EXPOSED INNER LIGULE, rooted crown and visible attached globular cup/callus remain unresolved.")
    s["learner_visual_status"]["status"]="FIELD_READY_PHOTO_GAPS"
    s["learner_visual_status"]["image_count"]=len(s["images"])
    write(SP,s);write(GEN,genus)
    write(REPORT,{"date_utc":datetime.now(timezone.utc).isoformat(),
      "result":"ERIOCHLOA_SERICEA_REAL_SOURCE_ANATOMY_JPEGS_ARCHIVED",
      "number":len(installed),"records":installed,"source_failures":blocked,
      "photos_current":s["curation_status"]["photo_files_present"],
      "teaching_panels":len(s["visual_comparison"]["items"]),
      "copyright":"Original Bob Harms scientific/educational credited use only, copyright retained, NOT CC",
      "science_holds":["True inner hair-fringed ligule not shown by ERSE5-C","Root-to-head attached live rooted Texas specimen","Globular basal cup while spikelet remains attached at 1 mm scale","Higher magnification fertile lemma/palea hair micro"]})
    write(RELEASE,{"date":"2026-10-27","species":"eriochloa-sericea",
      "report":str(REPORT),"publication":"Rights-filtered noncommercial Pages must succeed; no unconditional live assumption"})
    print("COMPLETE",len(installed),flush=True)
if __name__=="__main__":main()
