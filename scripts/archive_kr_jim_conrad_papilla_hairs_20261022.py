#!/usr/bin/env python3
"""Archive exactly one actual Uvalde KR bluestem papilla-hair close-up.
Source: Jim Conrad, Backyard Nature, Jan 27 2013; author's express
public domain photo dedication: https://www.backyardnature.net/j/copyrite.htm
Species concept: original photographer B. ischaemum var. songarica.
No invented 1mm ligule or explicitly single resolved papilla-base arrow.
"""
from pathlib import Path
import csv, io, json, hashlib, requests
from PIL import Image, ImageOps

ROOT = Path(".")
BASE = ROOT / "content/taxa/Poaceae/Bothriochloa"
SP = BASE / "bothriochloa-ischaemum/species.json"
GN = BASE / "genus.json"
CSV = SP.parent / "image-sources.csv"
DEST = SP.parent / "images/jim-conrad-uvalde-kr-bulbous-based-collar-hairs.jpg"
REPORT = ROOT / "reports/kr-jim-conrad-uvalde-papilla-hair-photo-20261022.json"
MARK = ROOT / "workflow/field-id-publication/2026-10-22-kr-uvalde-papilla-hairs-one-photo.json"
SOURCE = "https://www.backyardnature.net/n/13/130127gt.jpg"
PAGE = "https://www.backyardnature.net/n/h/kingblue.htm"
RIGHTS = "https://www.backyardnature.net/j/copyrite.htm"
LICENSE = "Public domain — express photographer dedication by Jim Conrad"
LABEL = "KR leaf-base long hairs with swollen bases — actual Uvalde photo (two arrows)"
REGION = "Dry Frio River valley, northern Uvalde County, Texas; 2013-01-27"
MARKERS = [
 {"label":"Long hairs at right leaf base","label_x":59,"label_y":10,"target_x":70,"target_y":45},
 {"label":"Long hairs at left leaf base","label_x":4,"label_y":84,"target_x":22,"target_y":51},
]

def save(path,obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def main():
    s=json.loads(SP.read_text(encoding="utf-8"))
    g=json.loads(GN.read_text(encoding="utf-8"))
    if s["id"]!="bothriochloa-ischaemum" or g["name"]!="Bothriochloa":
        raise RuntimeError("Canonical taxon no longer matches")
    if (len(s["images"]),len(s["visual_comparison"]["items"]),len(g["visual_comparison"]["items"])) != (7,16,11):
        raise RuntimeError("Concurrent card change, no write; refresh first")
    if DEST.exists() or REPORT.exists() or MARK.exists():
        raise RuntimeError("Candidate already present; no duplicate/overwrite")
    if any(x.get("source_page")==PAGE or x.get("file")=="images/"+DEST.name for x in s["images"]):
        raise RuntimeError("Jim Conrad photo already in image records")
    protected={k:json.dumps(s.get(k),sort_keys=True) for k in (
       "id","scientific_name","authority","synonyms","project_inclusion",
       "county_occurrences_target_zone","native_target_zone_calculated",
       "target_zone_count","native_metrics_excluded","taxonomic_note")}
    old_scope=json.dumps(g.get("project_scope"),sort_keys=True)
    with CSV.open(newline="",encoding="utf-8") as f:
        reader=csv.DictReader(f)
        fields=list(reader.fieldnames or [])
        rows=list(reader)
    if "file_name" not in fields or any(row.get("file_name")==DEST.name for row in rows):
        raise RuntimeError("Source CSV is missing expected columns or existing record")
    # Exact permission is in the cited public-domain declaration. The original
    # KR page credits its text and images to Jim Conrad without other photographer.
    response=requests.get(SOURCE,timeout=35,headers={"User-Agent":"HaysBotanyConservationEducationalPublicPhoto/1.0"})
    response.raise_for_status()
    raw=response.content
    if not (raw.startswith(b"\xff\xd8\xff") and 12000<len(raw)<6000000):
        raise RuntimeError("Source is unavailable or not a real JPEG; no canonical modifications")
    with Image.open(io.BytesIO(raw)) as orig:
        orig.load()
        w,h=orig.size
        if orig.format!="JPEG" or w<475 or h<330 or w>5000 or h>5000:
            raise RuntimeError("Source image isn't the vetted landscape hair photo")
        clean=ImageOps.exif_transpose(orig).convert("RGB")
    dst=io.BytesIO()
    clean.save(dst,format="JPEG",quality=94,optimize=True)
    encoded=dst.getvalue()
    if len(encoded)<11000: raise RuntimeError("Would archive poor-quality image")
    with Image.open(io.BytesIO(encoded)) as img:
        assert img.format=="JPEG" and img.size==clean.size
        assert not img.getexif().get(34853)
        img.verify()
    if not all(0<=m[k]<=100 for m in MARKERS for k in ("label_x","label_y","target_x","target_y")):
        raise RuntimeError("Invalid marker coordinate")
    before_photos=s["curation_status"]["photo_files_present"]
    if before_photos!=5: raise RuntimeError("Photo count changed concurrently")
    role="TRUE Texas upper-leaf-base long hairs with raised/swollen bases — unsized original photo; membranous ligule edge NOT visible"
    record={
      "file":"images/"+DEST.name,"role":role,"creator":"Jim Conrad",
      "license":LICENSE,"license_url":RIGHTS,"source_page":PAGE,
      "source_image":SOURCE,"original_source_label":"Bothriochloa ischaemum var. songarica",
      "source_taxon_name":"Bothriochloa ischaemum",
      "source_region":REGION,"source_type":"Original photographed field identification, author newsletter",
      "original_sha256":hashlib.sha256(raw).hexdigest(),
      "archived_sha256":hashlib.sha256(encoded).hexdigest(),
      "image_dimensions":[w,h],"photo_review":"Actual original page labels papilla/bulbous-based hairs at leaf bases; gross tufts visually reviewed. Individual papilla bases and true free ligule not reliably measured.",
      "modifications":"Re-encoded actual source photograph to RGB JPEG, removed EXIF/GPS; JSON overlay adds two broad real-hair-zone arrows, no false microscopic detail.",
      "public_reuse":"YES, original author expressly dedicated his photographs to the public domain; creator/source credited",
      "anatomy_arrows":"Two broad visible hair-group arrows; NO exact papilla-base or free ligule tip arrow",
      "archived_locally":True
    }
    panel={
      "label":LABEL,
      "scientific_name":"Bothriochloa ischaemum",
      "image_url":str(DEST),
      "image_fit":"contain","image_role":role,
      "caption":"Original documented KR bluestem var. songarica from the Dry Frio River valley, Uvalde County, January 2013. Long pale hairs protrude beside the leaf bases; the photographer calls out their swollen/bulbous attachment bases. The arrows indicate only HAIR-BEARING REGIONS visible in this modest-resolution original. It does NOT reveal a lifted true membranous ligule free margin, exact papilla insertion on one hair at high magnification, a mm scale, or a same-vouchered flowering spikelet.",
      "why_it_matters":"Real local invasive bluestem vegetative diagnostic: inspect the UPPER leaf blade near the collar for stiff hairs arising from raised bases, unlike native little-bluestem hairs along the SHEATH edge. Multiple characters still required before removing native plants.",
      "creator":"Jim Conrad","license":LICENSE,"license_url":RIGHTS,"source_page":PAGE,
      "source_image":SOURCE,"source_taxon_name":"Bothriochloa ischaemum",
      "source_original_label":"Bothriochloa ischaemum var. songarica",
      "source_region":REGION,"markers":MARKERS,
      "photo_status":"PROVISIONAL gross arrows to real hairs on source-determined Texas KR; no 1mm scale; not microscopic ligule or per-hair papilla resolved. Public domain by author's express dedication."
    }
    s["images"].append(record)
    s["visual_comparison"]["items"].append(panel)
    g["visual_comparison"]["items"].append(dict(panel))
    s["visual_comparison"]["subtitle"] += " One NEW physically archived genuine Uvalde County Jim Conrad public-domain image has two arrows to visible hair tufts; individual papillae/ligule remain unmeasured."
    s["curation_status"]["photo_metadata_count"]=len(s["images"])
    s["curation_status"]["photo_files_present"]=before_photos+1
    s["curation_status"]["kr_uvalde_true_hairs_one_photo_20261022"]={
       "new_real_photos":1,"species_panels":len(s["visual_comparison"]["items"]),
       "new_broad_hair_zone_arrows":2,"source":"Jim Conrad Uvalde (Jan 2013)",
       "status":"FIELD_READY_PHOTO_GAPS","scientific_treatment_unchanged":True,
       "true_ligule_tip_photo_still_needed":True,"microscopic_papilla_insertions_still_needed":True
    }
    s["field_photo_quickcheck"]["featured_photo_indices"].insert(4,16)
    steps=s["field_photo_quickcheck"]["steps"]
    if len(steps)<3 or not steps[2].startswith("3."):
        raise RuntimeError("Crew-step structure changed concurrently")
    steps[2]=(
      "3. KR LEAF-BASE HAIRS — NEW photo 17, genuine Jim Conrad Dry Frio/Uvalde specimen: two arrows mark real long hair TUFTS at upper leaf bases. Author describes SWOLLEN papilla-based attachments. Differentiate these from ordinary native little-bluestem SHEATH-edge hairs. STILL NEED isolated individual hair base, opened free true ligule under 10–20x and physical 1-mm ruler; do not invent membrane length from this view."
    )
    g["curation_status"]["KR_jim_conrad_uvalde_hairs_20261022"]={
       "new_verified_binary":1,"genus_panels":len(g["visual_comparison"]["items"]),
       "broad_true_hair_arrows":2,"author":"Jim Conrad",
       "express_public_domain_source":RIGHTS,"status":"FIELD_READY_PHOTO_GAPS"
    }
    s["field_id_finish_pass"]["stage"]="FIELD_READY_PHOTO_GAPS — now includes genuine Jim Conrad Uvalde County KR upper leaf-base hair clusters, with two broad arrows, but still needs exact per-hair papilla bases + physically pulled-open 1-mm true membranous ligule and actual same-voucher Texas attached fertile/pedicelled spikelet pair."
    assert all(json.dumps(s.get(k),sort_keys=True)==v for k,v in protected.items())
    assert json.dumps(g.get("project_scope"),sort_keys=True)==old_scope
    values={
     "file_name":DEST.name,"role":role,"creator":"Jim Conrad",
     "license":LICENSE,"license_url":RIGHTS,"source_page":PAGE,
     "direct_url":SOURCE,"study_use":"Public crew educational learner",
     "public_reuse":"YES original Jim Conrad public-domain dedication, credited",
     "modifications":record["modifications"]
    }
    rows.append({field:values.get(field,"") for field in fields})
    DEST.parent.mkdir(parents=True,exist_ok=True)
    DEST.write_bytes(encoded)
    with CSV.open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=fields,lineterminator="\n")
        writer.writeheader();writer.writerows(rows)
    save(SP,s);save(GN,g)
    save(REPORT,{
      "result":"ONE_TRUE_UVALDE_KR_LEAF_BASE_HAIR_PHOTO_ARCHIVED",
      "taxon":"Bothriochloa ischaemum",
      "original_variety_determination":"var. songarica (Jim Conrad)",
      "source_region":REGION,"photo":str(DEST),
      "source_page":PAGE,"original_image_url":SOURCE,
      "permission":RIGHTS,"license":LICENSE,"creator":"Jim Conrad",
      "original_sha256":record["original_sha256"],
      "archived_sha256":record["archived_sha256"],"original_dimensions":[w,h],
      "new_real_photo_count":1,"arrow_count":2,"species_panels":17,"genus_panels":12,
      "new_species_local_photos_total":6,
      "photo_answers":"long hairs at leaf base, source-identified bulging attachment",
      "photo_does_not_answer":"specific isolated papilla base / lifted ligule edge to true mm / same-voucher Texas attached paired spikelets",
      "stage":"FIELD_READY_PHOTO_GAPS"
    })
    save(MARK,{
      "type":"manual_field_id_publication","date":"2026-10-22",
      "title":"Publish Jim Conrad Uvalde KR collar-hair close-up with two real visible arrow targets",
      "species":"Bothriochloa ischaemum","report":str(REPORT),
      "new_verified_real_photos":1,"new_visible_gross_arrows":2,
      "species_panels":17,"genus_panels":12,
      "status":"FIELD_READY_PHOTO_GAPS",
      "publish":"NORMAL_RIGHTS_FILTERED_GITHUB_PAGES"
    })
    print("SUCCESS: one actual source photograph, rights checked, source hashes, 2 genuine broad hair arrow targets; photo gaps preserved",flush=True)

if __name__=="__main__":main()
