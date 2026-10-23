#!/usr/bin/env python3
"""Recover genuine USGS Schizachyrium scoparium sheath photograph locally.
Keep existing external source, original license and no false 1-mm ligule tip.
Fail closed on HTTP error or suspect photo dimensions.
"""
import csv,hashlib,io,json,time
from pathlib import Path
import requests
from PIL import Image,ImageOps

BASE=Path("content/taxa/Poaceae/Schizachyrium")
SP=BASE/"schizachyrium-scoparium/species.json"
GEN=BASE/"genus.json"
CSV=SP.parent/"image-sources.csv"
REPORT=Path("reports/schizachyrium-usgs-original-sheath-physical-20261022.json")
MARK=Path("workflow/field-id-publication/2026-10-22-little-bluestem-usgs-sheath-physical.json")
URL="https://warcapps.usgs.gov/PlantID/Image/GivenFile?file=Schizachrium_scoparium_sheath+and+leaf_2.JPG&id=2568&size=w"
PAGE="https://warcapps.usgs.gov/PlantID/Species/Details/2568"
LICENSE="Public domain — USGS employee federal plant photograph"
RIGHTS="https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits"
DEST=SP.parent/"images/usgs-larry-allain-schizachyrium-sheath-leaf.jpg"
def save(path,val):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(val,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
def retrieve():
    s=requests.Session()
    s.headers.update({"User-Agent":"HaysBotanyAttributionPreservingEducationBot/1.0 github.com/Crking92/Hays-County-Botany",
     "Accept":"image/jpeg,image/*"})
    r=s.get(URL,timeout=40)
    r.raise_for_status()
    raw=r.content
    if not raw.startswith(b"\xff\xd8\xff") or not 10000<len(raw)<4500000:
        raise RuntimeError("USGS source did not return real normal JPEG")
    with Image.open(io.BytesIO(raw)) as im:
        im.load()
        if im.format!="JPEG" or min(im.size)<240 or max(im.size)>8500:
            raise RuntimeError("USGS original type or size unsuitable "+str(im.size))
        original=list(im.size)
        converted=ImageOps.exif_transpose(im).convert("RGB")
    temp=io.BytesIO()
    converted.save(temp,"JPEG",quality=92,optimize=True)
    data=temp.getvalue()
    with Image.open(io.BytesIO(data)) as img:
        assert img.format=="JPEG" and not img.getexif().get(34853)
        img.verify()
    return raw,data,original,list(converted.size),r.url
def main():
    s=json.loads(SP.read_text(encoding="utf8"))
    g=json.loads(GEN.read_text(encoding="utf8"))
    assert s["id"]=="schizachyrium-scoparium" and g["name"]=="Schizachyrium"
    assert len(s["images"])==14 and len(s["visual_comparison"]["items"])==16 and len(g["visual_comparison"]["items"])==15
    if DEST.exists():raise RuntimeError("Existing physical file must be reconciled; no overwrite")
    sp=[p for p in s["visual_comparison"]["items"] if p.get("source_page")==PAGE and p.get("image_url")==URL]
    gp=[p for p in g["visual_comparison"]["items"] if p.get("source_page")==PAGE and p.get("image_url")==URL]
    assert len(sp)==1 and len(gp)==1
    assert sp[0]["creator"]=="Larry Allain / U.S. Geological Survey" and sp[0]["license"]==LICENSE
    assert len(sp[0]["markers"])==0 and len(gp[0]["markers"])==0
    with CSV.open(newline="",encoding="utf8") as f:
        rd=csv.DictReader(f);cols=rd.fieldnames;rows=list(rd)
    assert "file_name" in cols and "direct_image_url" in cols
    assert not any(x.get("file_name")==DEST.name for x in rows)
    protected={k:json.dumps(s.get(k),sort_keys=True) for k in
       ("county_occurrences_target_zone","native_target_zone_calculated","project_inclusion","target_zone_count","synonyms","authority","project_tracker_diagnostic")}
    scope=json.dumps(g["project_scope"],sort_keys=True)
    raw,data,orig,stored,actual=retrieve()
    print("VERIFIED USGS true Schizachyrium leaf-sheath photo",orig,len(data),flush=True)
    DEST.parent.mkdir(parents=True,exist_ok=True)
    DEST.write_bytes(data)
    meta={"file":"images/"+DEST.name,"role":"Authentic little-bluestem blade/sheath overlap and long whitish sheath-edge hairs, NOT definitively measured free true ligule",
       "creator":"Larry Allain / U.S. Geological Survey",
       "license":LICENSE,"license_url":RIGHTS,"source_page":PAGE,"source_image":URL,"source_taxon_name":"Schizachyrium scoparium",
       "source_locality":"Louisiana, not a Hays plant voucher",
       "source_original_sha256":hashlib.sha256(raw).hexdigest(),"archived_sha256":hashlib.sha256(data).hexdigest(),
       "source_dimensions":orig,"archived_dimensions":stored,"downloaded_from":actual,
       "public_reuse":"Original USGS federal employee photograph public domain, original government photo and photographer cited.",
       "modifications":"RGB JPEG re-encode to strip EXIF/GPS; no crop or burned-in false anatomy arrows",
       "image_status":"PHYSICAL_VERIFIED_USGS_FEDERAL_PD_SOURCE_ANATOMY_PROVISIONAL",
       "photo_review":"Original federal species source inspected, exact blade/sheath edge and long hairs; TRUE MEMBRANOUS LIGULE TIP not independently isolated to 1-mm certainty. Provisional user check."}
    s["images"].append(meta)
    for p in sp+gp:
        p["image_url"]=str(DEST)
        p["source_image"]=URL
        p["photo_status"]="Real original source-verified USGS Larry Allain Little bluestem photo physically archived and SHA-recorded with accurate USGS public-domain credit. Photographs sheath and hairs; NO unmeasured real free membranous ligule tip marked. User review provisional."
    row={"file_name":DEST.name,"role":meta["role"],"platform":"USGS Plants of Louisiana",
       "creator":meta["creator"],"license":LICENSE,"source_page":PAGE,"direct_image_url":URL,"public_reuse":meta["public_reuse"],"study_use":"yes"}
    rows.append({field:row.get(field,"") for field in cols})
    assert all(json.dumps(s.get(k),sort_keys=True)==v for k,v in protected.items())
    assert json.dumps(g["project_scope"],sort_keys=True)==scope
    s["curation_status"]["photo_metadata_count"]=15
    s["curation_status"]["photo_files_present"]=15
    s["curation_status"]["usgs_sheath_real_photo_archive_20261022"]="Exact USGS Larry Allain federally photographed sheath image now local, independently provenance-hashed and credited; true ligule free fringe not visually calibrated."
    s["field_id_finish_pass"]["nine_real_texas_harms_photos_20261022"]["extra_USGS_physically_archived"]=True
    s["visual_comparison"]["subtitle"]+=" The separate original USGS sheath/leaf view is also physically archived; real fine membranous ligule tip remains a scale-photo gap."
    g["curation_status"]["usgs_little_bluestem_real_sheath_20261022"]={"new_local_photos":1,"source":PAGE,"right":"Federal PD Larry Allain","existing_genus_panel_reused":True,"native_taxonomy_unchanged":True}
    with CSV.open("w",newline="",encoding="utf8") as f:
        wr=csv.DictWriter(f,fieldnames=cols,lineterminator="\n");wr.writeheader();wr.writerows(rows)
    save(SP,s);save(GEN,g)
    save(REPORT,{"result":"USGS_LITTLE_BLUESTEM_SHEATH_TRUE_JPEG_LOCAL","source":PAGE,"direct":URL,
     "path":str(DEST),"source_sha256":meta["source_original_sha256"],"archive_sha256":meta["archived_sha256"],
     "original_dimensions":orig,"archived_dimensions":stored,"new_local_photos":1,
     "total_stored_species_images":15,"species_panels":16,"genus_panels":15,
     "reused_source_gallery_not_duplicated":True,"true_ligule_not_measure_proven":True,"native_science_unchanged":True})
    save(MARK,{"type":"manual_field_id_publication","date":"2026-10-22","taxon":"Schizachyrium scoparium",
    "title":"Store exact real USGS leaf sheath photo locally and retain full credits",
    "report":str(REPORT),"license":LICENSE,"new_real_JPEGs":1,
    "status":"FIELD_READY_PHOTO_GAPS","public_user_review":"Provisional visible on normal species page no approval required"})
    print("SUCCESS source USGS Schizachyrium original archived",flush=True)
if __name__=="__main__":
    main()
