#!/usr/bin/env python3
"""One-shot KR photo installation from user-submitted exact source references.

An uploaded photograph is proof of the intended pixels, but its binary bytes are
not accessible to GitHub Actions. Fetch the identical photographer's public
original, check 8x8 dHash against the upload, strip all EXIF/GPS, and install
only when taxon, author, license and dimensions are correct.
"""
import hashlib, io, json, re
from datetime import datetime, timezone
from pathlib import Path

import requests
from PIL import Image, ImageOps

ROOT=Path(__file__).resolve().parents[1]
REL="content/taxa/Poaceae/Bothriochloa/bothriochloa-ischaemum"
TARGET=ROOT/REL
SPECIES=TARGET/"species.json"
REPORT=ROOT/"reports/kr-five-user-photo-recovery-20261027.json"
PUB=ROOT/"workflow/field-id-publication/2026-10-27-kr-five-user-photo-physical-archive.json"
COMMONS_API="https://commons.wikimedia.org/w/api.php"
AZ="https://www.azgrasses.org/pages-grasses/BB/Bothriochloa%20ischaemum.html"
LICENSE_SITE="https://www.azgrasses.org/"
AZ_LICENSE="© Dave Thayer — own photographs free to use per site statement (NOT Creative Commons)"
AZ_PERMISSION="DAVE_THAYER_AZGRASSES_OWN_PHOTOS_FREE_USE_20261027"
TIMEOUT=28
UA={"User-Agent":"Hays-Botany-educational-image-curation/1.0 (source-credit retained)"}
SPECS=[
 {"id":"sl2","commons":"Bothriochloa ischaemum sl2.jpg","creator":"Stefan.lefnaer","dhash":"1f1f3dc7391e0f31","file":"kr-stefan-lefnaer-sl2-real-scaled-raceme-20261027.jpg","role":"Actual source species spikelet-bearing raceme with original 5 mm scale"},
 {"id":"sl3","commons":"Bothriochloa ischaemum sl3.jpg","creator":"Stefan.lefnaer","dhash":"0f0f078c350f0fb2","file":"kr-stefan-lefnaer-sl3-spikelet-bases-20261027.jpg","role":"Attached flowering raceme and awned spikelets with original 5 mm scale"},
 {"id":"moro","commons":"Bothriochloa ischaemum spikelets.jpg","creator":"Andrea Moro / Dipartimento di Scienze della Vita, Università degli Studi di Trieste","dhash":"0409234499b64db2","file":"kr-andrea-moro-black-background-spikelets-20261027.jpg","role":"Mature hairy awned spikelet-bearing branches against black backdrop"},
 {"id":"pair","source":"https://www.azgrasses.org/images-grasses/B/Bothriochloa_ischaemum/Bothriochloa_ischaemum8.JPG","creator":"Dave Thayer","photo_id":"Bothriochloa_ischaemum8","dhash":"4af6a923262c352e","file":"kr-az-thayer-spikelet-pair-20261027.jpg","role":"Photographed true sessile and pedicelled companion spikelet pair, 280x280, no mm ruler"},
 {"id":"roots","source":"https://www.azgrasses.org/images-grasses/B/Bothriochloa_ischaemum/Bothriochloa_ischaemum9.JPG","creator":"Dave Thayer","photo_id":"Bothriochloa_ischaemum9","dhash":"c5c0c7c3e2d6e0f0","file":"kr-az-thayer-root-crown-20261027.jpg","role":"Photographed lifted basal crown with roots, 280x280, 1/4 inch graph paper"}
]
def hash_image(image):
    p=list(image.convert("L").resize((9,8),Image.Resampling.LANCZOS).getdata())
    bits=0
    for row in range(8):
        for col in range(8):
            bits=(bits<<1) | (p[row*9+col]>p[row*9+col+1])
    return bits

def fetch(url):
    r=requests.get(url,headers=UA,timeout=TIMEOUT)
    r.raise_for_status()
    if len(r.content)>14_000_000 or len(r.content)<3000:
        raise RuntimeError("unexpected source byte length")
    if not r.headers.get("content-type","").lower().startswith("image/"):
        raise RuntimeError("source did not return image")
    return r.content

def commons(spec):
    q=requests.get(COMMONS_API,params={"action":"query","format":"json",
          "titles":"File:"+spec["commons"],"prop":"imageinfo",
          "iiprop":"url|extmetadata","iiurlwidth":2200},
          headers=UA,timeout=TIMEOUT)
    q.raise_for_status()
    info=list(q.json()["query"]["pages"].values())[0]["imageinfo"][0]
    meta=info.get("extmetadata") or {}
    lic=meta.get("LicenseShortName",{}).get("value","").strip()
    url=meta.get("LicenseUrl",{}).get("value","").strip()
    author=meta.get("Artist",{}).get("value","")
    if not re.match(r"^CC BY(?:-SA)? [234]\.0(?: AT)?$",lic,re.I):
        raise RuntimeError("missing accepted photo-specific Commons license: "+repr(lic))
    if not url.startswith("https://creativecommons.org/licenses/"):
        raise RuntimeError("no Commons CC license link")
    if spec["id"] in {"sl2","sl3"} and "Stefan.lefnaer" not in author:
        raise RuntimeError("photographer mismatch")
    if spec["id"]=="moro" and "Moro" not in author:
        raise RuntimeError("photographer mismatch")
    path=info.get("thumburl") or info["url"]
    return {"license":lic,"license_url":url,"source_page":
        "https://commons.wikimedia.org/wiki/File:"+spec["commons"].replace(" ","_"),
        "download_url":path}

def make_record(spec,source,path,sha,size):
    img={"file":"images/"+spec["file"],"role":spec["role"],"creator":spec["creator"],
        "license":source["license"],"license_url":source["license_url"],
        "source_page":source["source_page"],"study_use":"yes",
        "public_reuse":"yes - exact photographer-authorized original; photographer, source and terms credited",
        "archive_sha256":sha,"image_dimensions":list(size),
        "archived_locally":True,"archive_status":"PHYSICALLY_STORED_EXIF_STRIPPED",
        "photo_review":"Source exact-photo verified to the user-submitted pixel pattern; visible macro roles only. NO invented 1mm measurements or Texas provenance.",
        "geographic_scope":"Arizona, non-Texas" if "photo_id" in spec else "European species-level or other non-Texas reference",
        "modifications":"JPEG RGB re-encoded; EXIF/GPS removed; kept original scale graphic where present"}
    if "photo_id" in spec:
        img.update({"source_photo_id":spec["photo_id"],
            "site_specific_public_permission":AZ_PERMISSION,
            "source_permission_page":LICENSE_SITE,
            "source_taxon_name":"Bothriochloa ischaemum",
            "source_media_url":spec["source"]})
    return img

def main():
    species=json.loads(SPECIES.read_text(encoding="utf-8"))
    if species["id"]!="bothriochloa-ischaemum":
        raise RuntimeError("wrong canonical taxon")
    panels=species["visual_comparison"]["items"]
    gallery=species["images"]
    report={"date":"2026-10-27","taxon":"Bothriochloa ischaemum","source":"same photographer source photo as 5 user-uploaded originals","items":[]}
    installed=[]
    for x in SPECS:
        try:
            source=commons(x) if "commons" in x else {"license":AZ_LICENSE,"license_url":LICENSE_SITE,"source_page":AZ,"download_url":x["source"]}
            full=TARGET/"images"/x["file"]
            if full.is_file():
                actual=full.read_bytes()
                with Image.open(io.BytesIO(actual)) as im: im.verify()
            else:
                data=fetch(source["download_url"])
                with Image.open(io.BytesIO(data)) as raw:
                    im=ImageOps.exif_transpose(raw).convert("RGB")
                    im.load()
                if (im.width<270 or im.height<270 or
                    ("commons" in x and min(im.size)<850)):
                    raise RuntimeError("source resolution too small")
                distance=(hash_image(im)^int(x["dhash"],16)).bit_count()
                if distance>11:
                    raise RuntimeError("source download is not the same photo as supplied upload; dHash distance "+str(distance))
                if max(im.size)>2600:im.thumbnail((2600,2600),Image.Resampling.LANCZOS)
                full.parent.mkdir(parents=True,exist_ok=True)
                im.save(full,"JPEG",quality=90,optimize=True,subsampling=0)
                with Image.open(full) as again:
                    if again.getexif(): raise RuntimeError("sanitized image retained EXIF")
                    again.verify()
                actual=full.read_bytes()
            with Image.open(io.BytesIO(actual)) as check: size=check.size
            sha=hashlib.sha256(actual).hexdigest()
            existing=next((v for v in gallery if v.get("file")=="images/"+x["file"]),None)
            if not existing:
                gallery.append(make_record(x,source,full,sha,size))
            photo_path=REL+"/images/"+x["file"]
            matched=[p for p in panels if p.get("source_page")==source["source_page"] and p.get("scientific_name")=="Bothriochloa ischaemum"]
            if x["id"]=="sl3" and not matched:
                panel={"label":"TRUE ATTACHED AWNED SPIKELETS — 5mm scale, Austrian species example",
                    "scientific_name":"Bothriochloa ischaemum","image_url":photo_path,
                    "image_fit":"contain","image_role":x["role"],
                    "caption":"Actual authenticated B. ischaemum spikelet-bearing flowering branches and bent awns with source 5mm scale. Austrian species-level reference, NOT an independently vouchered Texas KR spikelet pair. Individual glume/lemma or sessile/pedicelled member annotations require separate detailed photo verification.",
                    "why_it_matters":"The third distinctive reproductive image gives a different orientation to help find where spikelets attach to the flowering rachis.",
                    "creator":x["creator"],"license":source["license"],"license_url":source["license_url"],
                    "source_page":source["source_page"],"markers":[],"photo_status":"Actual locally archived verified photographic source, no new microscopic arrows"}
                panels.append(panel)
                matched=[panel]
            if not matched:
                raise RuntimeError("no existing precise source-matched panel")
            for panel in matched:
                panel.update({"image_url":photo_path,"license":source["license"],
                    "license_url":source["license_url"],"creator":x["creator"],
                    "photo_status":"LOCALLY STORED real species-reference photo, source/rights verified, EXIF removed; no invented microscopic arrows. Arizona/European material is NOT Texas-variety vouchered."})
                if "photo_id" in x:
                    panel.update({"source_photo_id":x["photo_id"],
                         "site_specific_public_permission":AZ_PERMISSION,
                         "source_permission_page":LICENSE_SITE,
                         "source_taxon_name":"Bothriochloa ischaemum",
                         "source_media_url":x["source"]})
            installed.append(x["id"])
            report["items"].append({"id":x["id"],"result":"ARCHIVED_AND_LINKED", "file":photo_path, "sha256":sha,"pixels":list(size),"license":source["license"]})
        except Exception as exc:
            report["items"].append({"id":x["id"],"result":"NOT_INSTALLED", "reason":str(exc)[:320]})
    if installed:
        species["images"]=gallery
        species["visual_comparison"]["items"]=panels
        species["curation_status"]["photo_files_present"]=len(gallery)
        species["curation_status"]["photo_metadata_count"]=len(gallery)
        species.setdefault("kr_photo_source_discovery_20261027",{})["physical_archive_confirmed_20261027"]={
            "installed":installed,"count":len(installed),"new_exif_free_photos":len(installed),
            "locally_archived_total":len(gallery),
            "true_texas_open_ligule_still_missing":True,
            "source_variation_notice":"Non-Texas species-level examples, not local var. songarica confirmation"}
        species["visual_comparison"]["subtitle"]=(
           str(len(panels))+" genuine botanical teaching photo panels; "+
           str(len(gallery))+" locally archived source-credited KR photographs. "+
           "Arizona photographed roots/spikelet pair and Austrian measured reproductive photo(s) are NOT local Texas songarica vouchers. "+
           "True opened Hays ligule edge, individual papilla hair base macro and local connected 1mm spikelet pair remain incomplete."
        )
        SPECIES.write_text(json.dumps(species,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        PUB.parent.mkdir(parents=True,exist_ok=True)
        PUB.write_text(json.dumps({"date":"2026-10-27","species_id":species["id"],
            "reason":"physically archived rights-audited actual KR photos sourced from user-provided original photo references",
            "installed_files":installed,"status":"FIELD_READY_PHOTO_GAPS",
            "no_new_anatomical_arrows":True,"original_rights_and_taxon_unchanged":True,
            "held_any":[x for x in report["items"] if x["result"]!="ARCHIVED_AND_LINKED"]},
            ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    report["installed_count"]=len(installed)
    report["status"]="ARCHIVED_VERIFIED_PHOTOS" if installed else "ACQUISITION_HOLD"
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
