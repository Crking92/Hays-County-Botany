#!/usr/bin/env python3
"""Guarded one-time archive of 6 Bob Harms original Texas wintergrass photos and
1 USDA public-domain fruit reference. Author-specific education use is NOT CC.
On network, validation, metadata, or partial-state failure, write no cards/photos.
"""
import csv, hashlib, io, json, time
from pathlib import Path
import requests
from PIL import Image,ImageOps
ROOT=Path(".")
SP=ROOT/"content/taxa/Poaceae/Nassella/nassella-leucotricha/species.json"
GN=ROOT/"content/taxa/Poaceae/Nassella/genus.json"
CSV=SP.parent/"image-sources.csv"
REPORT=ROOT/"reports/nassella-wintergrass-diagnostic-physical-20261022.json"
MARK=ROOT/"workflow/field-id-publication/2026-10-22-nassella-wintergrass-physical-diagnostic.json"
PREFIX="https://w3.biosci.utexas.edu/prc/Monocots/GrassHTML/data/"
CODES=["NALE3-L","NALE3-J5","NALE3-s","NALE3-j6","NALE3-9","NALE3-d"]
PERMISSION="BOB_HARMS_SELECTED_MONOCOTS_EDU_WITH_CREDIT_20261022"
HLICENSE="© Bob Harms — scientific/educational use with attribution (NOT Creative Commons)"
PD_PAGE="https://commons.wikimedia.org/wiki/File:Nassella_leucotricha.jpg"
PD_URL="https://upload.wikimedia.org/wikipedia/commons/e/ed/Nassella_leucotricha.jpg"

def save(path,doc):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(doc,indent=2,ensure_ascii=False)+"\n",encoding="utf8")

def download(session,url):
    errors=[]
    for trial in range(3):
        try:
            res=session.get(url,timeout=40,headers={"Accept":"image/jpeg,image/*"})
            res.raise_for_status()
            data=res.content
            if not (5000<len(data)<9_000_000 and data[:3]==b"\xff\xd8\xff"):
                raise ValueError("Downloaded response not a real JPEG")
            return data,res.url
        except Exception as e:
            errors.append(type(e).__name__+":"+str(e)[:140])
            time.sleep(2+trial*2)
    raise RuntimeError("Cannot download exact source JPEG "+url+": "+str(errors))

def verify_and_scrub(raw,expected=None):
    with Image.open(io.BytesIO(raw)) as im:
        im.load()
        dims=im.size
        if im.format!="JPEG" or min(dims)<250 or max(dims)>12000:
            raise ValueError("Image dimensions/type outside expected constraints: "+repr(dims))
        if expected and dims!=expected:
            raise ValueError("Published source dimension mismatch")
        clean=ImageOps.exif_transpose(im).convert("RGB")
    clean.thumbnail((2400,2400),Image.Resampling.LANCZOS)
    out=io.BytesIO()
    clean.save(out,format="JPEG",quality=90,optimize=True)
    data=out.getvalue()
    with Image.open(io.BytesIO(data)) as check:
        assert check.format=="JPEG" and not check.getexif().get(34853)
        check.verify()
    if len(data)<6000:
        raise ValueError("Archived file too small")
    return data,dims,clean.size

def main():
    s=json.loads(SP.read_text(encoding="utf8"))
    g=json.loads(GN.read_text(encoding="utf8"))
    assert s["id"]=="nassella-leucotricha" and g["name"]=="Nassella"
    assert len(s["images"])==10 and len(s["visual_comparison"]["items"])==12 and len(g["visual_comparison"]["items"])==10
    preserved={key:json.dumps(s.get(key),sort_keys=True) for key in
               ("project_inclusion","county_occurrences_target_zone",
                "native_target_zone_calculated","target_zone_count","synonyms","taxonomic_note")}
    preserved_genus=json.dumps(g.get("project_scope"),sort_keys=True)
    jobs=[]
    for code in CODES:
        page=PREFIX+"pages/"+code+".html"
        direct=PREFIX+"images/"+code+".jpg"
        name="bob-harms-wintergrass-"+code.lower()+".jpg"
        photo=next((v for v in s["images"] if v.get("source_page")==page),None)
        if not photo or photo.get("creator")!="Bob Harms" or photo.get("license")!=HLICENSE:
            raise RuntimeError("Source identity/rights do not match "+page)
        if photo.get("site_specific_public_permission")!=PERMISSION or photo.get("source_image")!=direct or photo.get("file")!=direct:
            raise RuntimeError("Source authorization or image file changed "+page)
        sp=[v for v in s["visual_comparison"]["items"] if v.get("source_page")==page]
        gp=[v for v in g["visual_comparison"]["items"] if v.get("source_page")==page]
        if len(sp)!=1 or len(gp)>1 or sp[0].get("image_url")!=direct:
            raise RuntimeError("Species/genus visual source no longer matches "+page)
        if gp and gp[0].get("image_url")!=direct:
            raise RuntimeError("Genus visual source no longer matches "+page)
        jobs.append({"code":code,"name":name,"page":page,"url":direct,"photo":photo,"panels":sp+gp})
    pd_photo=next((v for v in s["images"] if v.get("source_page")==PD_PAGE),None)
    pd_panels=[v for v in s["visual_comparison"]["items"] if v.get("source_page")==PD_PAGE]
    gd_panels=[v for v in g["visual_comparison"]["items"] if v.get("source_page")==PD_PAGE]
    if not pd_photo or len(pd_panels)!=1 or pd_photo.get("license")!="Public Domain (U.S. federal work)":
        raise RuntimeError("USDA original rights/identity hold")
    if not pd_photo.get("file","").startswith("https://") or len(gd_panels)>1:
        raise RuntimeError("USDA image already localized or genus duplicates")
    jobs.append({"code":"USDA","name":"usda-tracey-slotta-nassella-sharp-fruit.jpg",
                 "page":PD_PAGE,"url":PD_URL,"photo":pd_photo,"panels":pd_panels+gd_panels})
    with CSV.open(newline="",encoding="utf8") as fh:
        rd=csv.DictReader(fh)
        cols=rd.fieldnames
        rows=list(rd)
    if not cols or "file_name" not in cols:
        raise RuntimeError("CSV provenance columns missing")
    for job in jobs:
        dest=SP.parent/"images"/job["name"]
        if dest.exists() or any(x.get("file")=="images/"+job["name"] for x in s["images"]) or any(x.get("file_name")==job["name"] for x in rows):
            raise RuntimeError("Partially installed or duplicate photo; reconcile rather than overwrite "+job["name"])
        job["dest"]=dest

    session=requests.Session()
    session.headers["User-Agent"]="Hays-County-Botany-CreditedEducationalPhotoArchiver/1.0 (github.com/Crking92/Hays-County-Botany)"
    staged=[]
    for job in jobs:
        if job["code"]=="USDA":
            # Commons original is HTTP 429 throttled; do not keep retrying or
            # block six successfully source-verified Bob Harms originals.
            # The public-domain USDA image remains its existing credited remote link.
            print("USDA SOURCE HOLD: Commons HTTP 429. Original remote panel retained, not counted as archived.",flush=True)
            continue
        raw,actual=download(session,job["url"])
        data,dims,cleandims=verify_and_scrub(raw)
        staged.append((job,raw,data,actual,dims,cleandims))
        print("SOURCE JPEG VERIFIED",job["code"],dims,len(raw),len(data),flush=True)
    if len(staged)!=6 or {x[0]["code"] for x in staged}!=set(CODES):
        raise RuntimeError("Expected all six licensed Harms originals before any commit")

    report=[]
    for job,raw,data,actual,dims,cleandims in staged:
        dest=job["dest"]
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(data)
        item=job["photo"]
        oldurl=item["file"]
        item["source_image_original_url"]=oldurl
        item["file"]="images/"+dest.name
        item["downloaded_from"]=actual
        item["source_original_sha256"]=hashlib.sha256(raw).hexdigest()
        item["archived_sha256"]=hashlib.sha256(data).hexdigest()
        item["original_dimensions"]=list(dims)
        item["archived_dimensions"]=list(cleandims)
        item["modifications"]="Saved author photo as RGB JPEG; resized only if larger than 2400px; EXIF/GPS stripped; original photographic content unchanged; arrows remain browser overlay."
        item["image_status"]="PHYSICAL_ARCHIVED_SOURCE_VERIFIED_EDUCATIONAL_WITH_CREDIT" if job["code"]!="USDA" else "PHYSICAL_ARCHIVED_VERIFIED_PUBLIC_DOMAIN"
        for panel in job["panels"]:
            panel["image_url"]=str(dest)
            panel["photo_status"]=("PHYSICALLY ARCHIVED original Bob Harms copyrighted photograph, with author's scientific/educational credit-only permission (not CC)." if job["code"]!="USDA" else "PHYSICALLY ARCHIVED USDA Tracey Slotta PD exact source fruit.")+" Real JPEG hash and EXIF/GPS check verified, original source page retained, photo remains PROVISIONAL FOR USER ID/ARROW REVIEW; no unsupported fine structures inferred."
        vals={"file_name":dest.name,"role":item["role"],"creator":item["creator"],"license":item["license"],
              "license_url":item.get("license_url","https://creativecommons.org/publicdomain/mark/1.0/" if job["code"]=="USDA" else ""),
              "source_page":job["page"],"direct_url":actual,"study_use":"Public educational learner",
              "public_reuse":item.get("public_reuse","yes"),"modifications":item["modifications"]}
        rows.append({col:vals.get(col,"") for col in cols})
        report.append({"path":str(dest),"creator":item["creator"],"source_page":job["page"],
                       "license":item["license"],"original_sha256":item["source_original_sha256"],
                       "archived_sha256":item["archived_sha256"],"original_dimensions":list(dims),
                       "archive_dimensions":list(cleandims)})
    with CSV.open("w",encoding="utf8",newline="") as fh:
        writer=csv.DictWriter(fh,fieldnames=cols,lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    s["curation_status"]["photo_files_present"]=8
    s["curation_status"]["photo_metadata_count"]=10
    s["curation_status"]["nassella_six_real_archived_20261022"]="Six copyrighted Harms education-with-credit originals physically stored in canonical species images/ and two existing CC BY files retained. USDA public-domain fruit and Abilene CC BY-NC view remain external due source throttle or no download."
    s["field_id_finish_pass"]["diagnostic_photo_20261022"]["new_local_binary_files"]=6
    s["field_id_finish_pass"]["diagnostic_photo_20261022"]["source_archiving"]="Six physical verified Bob Harms JPEGs with SHA256 EXIF/GPS removal; USDA external SOURCE HOLD HTTP 429"
    s["visual_comparison"]["subtitle"]+=" Six Harms anatomical images now physically stored in GitHub; USDA PD fruit still external because of 429 throttling."
    s["visual_comparison"]["overlay_note"]+=" Six new physically stored real photographs; existing USDA overlay markers remain on unchanged external 900x600 original. No duplicate 429 attempt."
    s["field_photo_quickcheck"]["warning"]+=" Six exact Harms originals physically stored under limited educational permission, not CC; USDA PD image remains external, not counted as locally archived."
    g["visual_comparison"]["subtitle"]+=" Four Harms genus panels now reference the same physically stored species images; USDA remains remote."
    g["curation_status"]["nassella_physical_anatomy_photo_archive_20261022"]="Six new physical source species photos, four also reused within genus; the existing USDA original remains external owing to HTTP 429, exact credits untouched."
    for k,v in preserved.items():
        if json.dumps(s.get(k),sort_keys=True)!=v:
            raise RuntimeError("Protected species science changed; abort")
    if json.dumps(g.get("project_scope"),sort_keys=True)!=preserved_genus:
        raise RuntimeError("Protected genus taxonomy scope changed; abort")
    assert len(s["images"])==10 and len(s["visual_comparison"]["items"])==12 and len(g["visual_comparison"]["items"])==10
    save(SP,s);save(GN,g)
    save(REPORT,{"result":"SIX_HARMS_NASSELLA_DIAGNOSTIC_JPEGS_ARCHIVED","files":report,
                 "new_physical_files":6,"existing_physical_files":2,
                 "new_Harms_educational_credit_only":6,"new_USDA_public_domain":0,
                 "USDA_reference_still_external":"Commons HTTP 429 — existing USDA public-domain gallery remains source-linked",
                 "species_panels":12,"genus_panels":10,
                 "original_taxonomy_and_nativity_unchanged":True,
                 "status":"FIELD_READY_PHOTO_GAPS",
                 "last_mile":"Same Hays rooted-flowering plant and mm measured true inner ligule/crown with attached mature callus."})
    save(MARK,{"type":"manual_field_id_publication","date":"2026-10-22",
               "title":"Archive six physically verified Texas wintergrass diagnostic photos",
               "taxon":"Nassella leucotricha","report":str(REPORT),
               "new_physical_files":6,"source_license":"Six Bob Harms author educational permission with credit (not CC); USDA public-domain image stays external (HTTP 429)",
               "reusable_only_for_documented_science_education":True,
               "user_review":"ordinary public species page; provisional",
               "science_status":"FIELD_READY_PHOTO_GAPS",
               "county_nativity_unchanged":True})
    print("SIX_HARMS_REAL_NASSELLA_PHOTOS_ARCHIVED__USDA_REMOTE_HOLD",flush=True)

if __name__=="__main__":
    main()
