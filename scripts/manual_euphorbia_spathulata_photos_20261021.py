#!/usr/bin/env python3
"""One-time exact-species, per-photo licensed Euphorbia spathulata field photo intake."""
import csv
import hashlib
import io
import json
from pathlib import Path

import requests
from PIL import Image, ImageOps

BASE = Path("content/taxa/Euphorbiaceae/Euphorbia/euphorbia-spathulata")
SPECIES = BASE / "species.json"
SOURCES = BASE / "image-sources.csv"
REPORT = Path("reports/euphorbia-spathulata-diagnostic-photo-intake-20261021.json")
SITE = "https://yavapaiplants.extension.arizona.edu/euphorbia-spathulata"
UA_URLS = [
    "https://yavapaiplants.extension.arizona.edu/sites/default/files/Forbs/Images/Euphorbia_spatulatha_SL_w.jpg",
    "https://yavapaiplants.extension.arizona.edu/sites/default/files/styles/yp_card_image/public/Forbs/Images/Euphorbia_spatulatha_SL_w.jpg.webp?itok=5taXTaN-",
]
ALLOWED = {
    "cc0": ("CC0 1.0", "https://creativecommons.org/publicdomain/zero/1.0/", "yes"),
    "cc-by": ("CC BY 4.0", "https://creativecommons.org/licenses/by/4.0/", "yes"),
    "cc-by-sa": ("CC BY-SA 4.0", "https://creativecommons.org/licenses/by-sa/4.0/", "yes"),
    "cc-by-nc": ("CC BY-NC 4.0", "https://creativecommons.org/licenses/by-nc/4.0/", "yes, noncommercial education only"),
}
s = requests.Session()
s.headers.update({"User-Agent":"HaysCountyBotanyEducationalMediaQA/1.0 (public morphology learner)"})
data = json.loads(SPECIES.read_text())
assert data["scientific_name"] == "Euphorbia spathulata", "Wrong canonical card"
images = data["images"]
existing = {i["file"] for i in images}
results = []

def download_photo(url):
    r = s.get(url, timeout=30)
    r.raise_for_status()
    raw = r.content
    assert len(raw) > 10_000, "Too few bytes"
    with Image.open(io.BytesIO(raw)) as im:
        im.load()
        width,height = im.size
        assert width >= 600 and height >= 350, f"Image too small: {width}x{height}"
        result = ImageOps.exif_transpose(im).convert("RGB")
        result.thumbnail((2400,2400))
        out=io.BytesIO()
        result.save(out, format="JPEG", quality=91, optimize=True)
        jpg=out.getvalue()
    with Image.open(io.BytesIO(jpg)) as verified:
        verified.verify()
    return jpg, [width,height], hashlib.sha256(jpg).hexdigest()

def install(filename, urls, meta):
    rel = "images/"+filename
    if rel in existing:
        results.append({"file":rel,"status":"already installed"})
        return
    errors=[]
    for url in urls:
        try:
            raw,dims,sha=download_photo(url)
            (BASE/"images").mkdir(parents=True,exist_ok=True)
            (BASE/rel).write_bytes(raw)
            record=dict(meta)
            record.update({"file":rel,"downloaded_from":url,"image_dimensions_source":dims,
                           "saved_jpeg_sha256":sha,"anatomy_arrows":[],
                           "photo_review":"Physically downloaded, resized, source and license checked. Diagnostic arrow coordinates require actual saved-image visual inspection.",
                           "public_reuse":"yes, attribution plus source Creative Commons terms apply"})
            images.append(record)
            existing.add(rel)
            results.append({"file":rel,"status":"installed","from":url,"license":record["license"],"dimensions":dims,"sha256":sha})
            return
        except Exception as e:
            errors.append(f"{url}: {type(e).__name__}: {e}")
    results.append({"file":rel,"status":"held","errors":errors})

# Nathan Taylor's Texas observation was cited with fruit microphotograph in their DFW spurge guide.
obsid=11085572
pid=15653221
try:
    obj=s.get(f"https://api.inaturalist.org/v1/observations/{obsid}",timeout=30).json()
    obs=obj["results"][0]
    obsname=obs.get("taxon",{}).get("name","")
    assert obsname=="Euphorbia spathulata", f"Observation taxon mismatch: {obsname}"
    photo=next(p for p in obs["photos"] if p["id"]==pid)
    license_code=(photo.get("license_code") or "").lower()
    assert license_code in ALLOWED, f"Individual photo license not eligible: {license_code}"
    license_name,license_url,scope=ALLOWED[license_code]
    creator=photo.get("attribution") or "(c) Nathan Taylor; individual iNaturalist photo"
    # Only the exact already visually screened diagnostic image is used.
    install("nathan-15653221-warty-capsule.jpg",
            [f"https://inaturalist-open-data.s3.amazonaws.com/photos/{pid}/original.jpeg",
             f"https://inaturalist-open-data.s3.amazonaws.com/photos/{pid}/large.jpeg"],
            {"role":"Texas source close-up showing rounded capsule verrucae, styles, cyathial glands and separate leaflike bracts",
             "creator":creator,"license":license_name,"license_url":license_url,
             "source_platform":"iNaturalist","source_page":f"https://www.inaturalist.org/photos/{pid}",
             "observation_url":f"https://www.inaturalist.org/observations/{obsid}",
             "observation_id":obsid,"photo_id":pid,
             "public_site_use_scope":scope,
             "caption":"Photographed Texas fruit exhibits low rounded warts (verrucae). Broad separate bracts frame the cyathium; tiny gland details should only be marked if visible in saved source pixels."})
except Exception as e:
    results.append({"file":"nathan-15653221-warty-capsule.jpg","status":"held","reason":f"{type(e).__name__}: {e}"})

# University of Arizona Extension's exactly named E. spathulata page assigns CC BY-SA to Max Licher image.
try:
    html=s.get(SITE,timeout=30).text
    assert "Euphorbia spathulata" in html and "Max Licher" in html and "CC BY-SA" in html, "University Arizona source page or copyright evidence changed"
    install("max-licher-uaz-flowering-bracts.jpg", UA_URLS,
            {"role":"Multiple flowering tip bract pairs and warty fruits in foliage, photo originally credited by U Arizona Extension",
             "creator":"Max Licher, via Southwest Environmental Information Network / University of Arizona Extension",
             "license":"CC BY-SA 4.0",
             "license_url":"https://creativecommons.org/licenses/by-sa/4.0/",
             "source_platform":"Yavapai County Native and Naturalized Plants, University of Arizona Extension",
             "source_page":SITE,
             "public_site_use_scope":"CC BY-SA attribution and ShareAlike terms",
             "caption":"Several distinct broad flowering bracts enclose yellow cyathia while warted rounded capsules protrude. Do not confuse separate bracts with the fused cyathial involucre."})
except Exception as e:
    results.append({"file":"max-licher-uaz-flowering-bracts.jpg","status":"held","reason":f"{type(e).__name__}: {e}"})

accepted=[x for x in results if x["status"]=="installed"]
if accepted:
    data["images"]=images
    data.setdefault("learner_visual_status",{})["image_count"]=len(images)
    data["learner_visual_status"]["mode"]="provisional_diagnostic_photo_intake_pending_arrow_review"
    data["learner_visual_status"]["note"]=f"Now {len(images)} physically saved licensed original photographs; newly downloaded sources awaiting saved-pixel arrow coordinates and QA before finishing species."
    data.setdefault("curation_status",{})["photo_metadata_count"]=len(images)
    data["curation_status"]["photo_files_present"]=len(images)
    data["curation_status"]["field_status"]="DIAGNOSTIC_IMAGES_INSTALLED_PENDING_ARROW_QA"
    SPECIES.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
    with SOURCES.open(newline="",encoding="utf-8") as f:
        rows=list(csv.DictReader(f))
        fields=list(rows[0]) if rows else ["file_name","role","creator","license","source_page","direct_url","study_use","public_reuse","observation_id","photo_id"]
    old={r["file_name"] for r in rows}
    for x in images:
        filename=x["file"].split("/")[-1]
        if filename not in old:
            row={col:"" for col in fields}
            row.update({"file_name":filename,"role":x["role"],"creator":x["creator"],"license":x["license"],
                        "source_page":x["source_page"],"direct_url":x.get("downloaded_from",""),
                        "study_use":"Educational public learner under source license",
                        "public_reuse":x["public_reuse"],
                        "observation_id":str(x.get("observation_id","")),
                        "photo_id":str(x.get("photo_id",""))})
            rows.append(row)
    with SOURCES.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=fields)
        writer.writeheader();writer.writerows(rows)
REPORT.parent.mkdir(parents=True,exist_ok=True)
REPORT.write_text(json.dumps({"species":"Euphorbia spathulata","date":"2026-10-21",
                              "photo_checks":results,"installed_new":len(accepted),
                              "canonical_photo_count":len(images),
                              "conservative_rule":"No arrows to unexamined source pixels; no false claims of glands, warts, or bract fusion"},indent=2)+"\n")
print(json.dumps(results,indent=2))
assert accepted or all(x["status"]=="already installed" for x in results), "No photos installed; check candidates and license records"
