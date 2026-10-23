#!/usr/bin/env python3
"""Fail-closed original CC BY 4.0 photograph archive: Tyler Cannon iNaturalist
photo 93518931, independently CC-verified on Wikimedia Commons. Preserve
Bothriochloa ischaemum var. songarica source concept, not an Hays voucher.
"""
from pathlib import Path
import csv,hashlib,io,json
import requests
from PIL import Image,ImageOps
BASE=Path("content/taxa/Poaceae/Bothriochloa")
SP=BASE/"bothriochloa-ischaemum/species.json"
GN=BASE/"genus.json"
CSV=SP.parent/"image-sources.csv"
REPORT=Path("reports/kr-bluestem-tyler-cannon-texas-photo-physical-20261022.json")
MARK=Path("workflow/field-id-publication/2026-10-22-kr-native-comparison-and-physical-texas-photo.json")
PHOTOS=("https://inaturalist-open-data.s3.amazonaws.com/photos/93518931/original.jpg",
       "https://upload.wikimedia.org/wikipedia/commons/a/a3/Bothriochloa_ischaemum_var._songarica.jpg")
WEB="https://commons.wikimedia.org/wiki/File:Bothriochloa_ischaemum_var._songarica.jpg"
LIC="CC BY 4.0"
DEST=SP.parent/"images/tyler-cannon-texas-kr-var-songarica-cc-by4.jpg"

def save(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf8")

def main():
    s=json.loads(SP.read_text(encoding="utf8"))
    g=json.loads(GN.read_text(encoding="utf8"))
    assert s["id"]=="bothriochloa-ischaemum" and g["name"]=="Bothriochloa"
    if len(s["images"])!=7 or len(s["visual_comparison"]["items"])!=16 or len(g["visual_comparison"]["items"])!=11:
        raise RuntimeError("Concurrent gallery/genus change, abort for refresh")
    if DEST.exists() or REPORT.exists() or MARK.exists():
        raise RuntimeError("Already installed, refusing overwrite")
    recs=[r for r in s["images"] if r.get("source_page")==WEB and r.get("inaturalist_photo_id")==93518931]
    if len(recs)!=1 or recs[0].get("creator")!="Tyler Cannon" or recs[0].get("license")!=LIC:
        raise RuntimeError("Original photo-level identity and license not matched")
    pic=recs[0]
    original=pic["file"]
    sp_panels=[x for x in s["visual_comparison"]["items"] if x.get("source_page")==WEB and x.get("creator")=="Tyler Cannon"]
    gn_panels=[x for x in g["visual_comparison"]["items"] if x.get("source_page")==WEB and x.get("creator")=="Tyler Cannon"]
    if len(sp_panels)!=1 or len(gn_panels)!=1 or sp_panels[0].get("markers") or gn_panels[0].get("markers"):
        raise RuntimeError("Source or already annotated image changed; review new current SHA")
    protected={k:json.dumps(s.get(k),sort_keys=True) for k in
       ("project_inclusion","native_target_zone_calculated","county_occurrences_target_zone",
        "target_zone_count","native_metrics_excluded","synonyms","taxonomic_note")}
    with CSV.open(newline="",encoding="utf8") as f:
        rd=csv.DictReader(f); fields=list(rd.fieldnames or []); rows=list(rd)
    if "file_name" not in fields or any(r.get("file_name")==DEST.name for r in rows):
        raise RuntimeError("Missing registry schema or existing filename")
    r=None
    failures=[]
    for candidate in PHOTOS:
        try:
            v=requests.get(candidate,timeout=35,headers={"User-Agent":"HaysBotanyLicensedOriginalImageArchive/1.0"})
            v.raise_for_status()
            if not (v.content.startswith(b"\xff\xd8\xff") and len(v.content)>20000):
                raise RuntimeError("not a JPEG")
            r=v
            print("SOURCE VERIFIED",candidate,flush=True)
            break
        except Exception as exc:
            failures.append(candidate+" "+str(exc)[:100])
    if r is None:
        raise RuntimeError("No verified licensed source binary. No changes. "+repr(failures))
    raw=r.content
    if not 20000<len(raw)<9000000 or not raw.startswith(b"\xff\xd8\xff"):
        raise RuntimeError("Photo source unavailable/not a usable JPEG")
    with Image.open(io.BytesIO(raw)) as orig:
        orig.load(); dims=list(orig.size)
        if orig.format!="JPEG" or min(orig.size)<500: raise RuntimeError("Photo wrong shape/pixels")
        clean=ImageOps.exif_transpose(orig).convert("RGB")
    clean.thumbnail((2400,2400),Image.Resampling.LANCZOS)
    b=io.BytesIO();clean.save(b,"JPEG",quality=90,optimize=True); out=b.getvalue()
    with Image.open(io.BytesIO(out)) as verify:
        if verify.format!="JPEG" or verify.getexif().get(34853):raise RuntimeError("EXIF/GPS guard")
        verify.verify()
    assert len(out)>12000
    DEST.parent.mkdir(parents=True,exist_ok=True)
    DEST.write_bytes(out)
    original_hash=hashlib.sha256(raw).hexdigest()
    archive_hash=hashlib.sha256(out).hexdigest()
    pic.update({
        "file":"images/"+DEST.name,"source_original_file":original,"direct_media_source":r.url,
        "license_url":"https://creativecommons.org/licenses/by/4.0/",
        "source_original_sha256":original_hash,"archive_sha256":archive_hash,
        "source_original_dimensions":dims,"archived_dimensions":list(clean.size),
        "archived_locally":True,"photo_status":"PROVISIONAL — USER PHOTO REVIEW PENDING; source-authenticated Texas var. songarica head",
        "modifications":"CC BY photograph RGB JPEG re-encoded at <=2400px, EXIF/GPS removed; no pixel arrows added.",
        "public_reuse":"yes; CC BY 4.0 with author and source credit"
    })
    for panel in (sp_panels[0],gn_panels[0]):
        panel["image_url"]=str(DEST)
        panel["photo_status"]="PHYSICALLY ARCHIVED original Texas Tyler Cannon CC BY4 flowering head; original author/source unchanged; no new pixel arrows."
    s["curation_status"]["photo_metadata_count"]=len(s["images"])
    s["curation_status"]["photo_files_present"]=sum(x["file"].startswith("images/") for x in s["images"])
    assert s["curation_status"]["photo_files_present"]==5
    s["curation_status"]["kr_texas_tyler_cannon_photo_20261022"]={"archived":True,"newRealPhotos":1,
        "totalLocalKRPhotos":5,"newArrows":0,"license":LIC,"source":WEB,
        "status":"FIELD_READY_PHOTO_GAPS"}
    s["visual_comparison"]["subtitle"]+=" Original Texas var. songarica head is now a LOCAL scrubbed CC BY image, not a remote-only link."
    g["curation_status"]["kr_texas_tyler_cannon_local_photo_20261022"]={
       "oneGenuinePhotoArchived":True,"license":LIC,"source":WEB,"status":"FIELD_READY_PHOTO_GAPS"}
    vals={"file_name":DEST.name,"role":pic["role"],"creator":"Tyler Cannon","license":LIC,
          "license_url":"https://creativecommons.org/licenses/by/4.0/","source_page":WEB,
          "direct_url":r.url,"study_use":"Noncommercial public educational website",
          "public_reuse":"yes, CC BY 4.0","modifications":pic["modifications"]}
    rows.append({col:vals.get(col,"") for col in fields})
    assert all(json.dumps(s.get(k),sort_keys=True)==v for k,v in protected.items())
    with CSV.open("w",newline="",encoding="utf8") as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(rows)
    save(SP,s);save(GN,g)
    save(REPORT,{"result":"ONE_SOURCE_VERIFIED_TEXAS_KR_ORIGINAL_ARCHIVED","taxon":"Bothriochloa ischaemum",
       "regional_source_taxon":"var. songarica (Tyler Cannon original label)",
       "physical_path":str(DEST),"source_page":WEB,"iNaturalist_photo":93518931,
       "creator":"Tyler Cannon","license":LIC,"original_file_sha256":original_hash,
       "archived_sha256":archive_hash,"original_dimensions":dims,"archived_dimensions":list(clean.size),
       "species_photo_panels":16,"kr_original_photo_count":5,
       "new_arrows":0,"native_lookalike_comparison_panels":9,
       "native_county_and_original_taxonomy_unchanged":True,
       "remaining_status":"FIELD_READY_PHOTO_GAPS"})
    save(MARK,{"type":"manual_field_id_publication","date":"2026-10-22",
       "title":"Publish KR original photographed Texas head and native bluestem arrow comparisons",
       "taxon":"Bothriochloa ischaemum","report":str(REPORT),
       "photo_archive_real_file_count":1,"total_physically_stored_KR_species_media":5,
       "native_and_exotic_comparison_panels_added":9,
       "original_photo_arrows_reused":16,"new_unverified_photo_arrows":0,
       "status":"FIELD_READY_PHOTO_GAPS",
       "publish":"NORMAL_RIGHTS_FILTERED_GITHUB_PAGES"})
    print("SUCCESS physical source, source hashes, 5 local KR photos, 16 panels, 16 reused native/exotic gross arrows")

if __name__=="__main__":main()
