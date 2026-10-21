#!/usr/bin/env python3
"""Add three individually-licensed real Commons photos to the existing Philadelphia fleabane card.
All-or-nothing, fail-safe exact-file download; never guess diagnostic arrows or county ranges.
"""
from __future__ import annotations
import csv
import hashlib
import io
import json
from pathlib import Path

import requests
from PIL import Image, ImageOps

ROOT=Path("content/taxa/Asteraceae/Erigeron")
P=ROOT/"erigeron-philadelphicus"
CARD=P/"species.json"
GENUS=ROOT/"genus.json"
LEDGER=P/"image-sources.csv"
REPORT=Path("reports/erigeron-philadelphicus-three-public-photos-20261021.json")
SOURCES=[
 dict(title="Erigeron_philadelphicus,_Beechview,_2025-05-17.jpg",
      file="commons-cbaile19-beechview-2025-flowers.jpg",creator="Cbaile19",license="CC0",
      source="https://commons.wikimedia.org/wiki/File:Erigeron_philadelphicus%2C_Beechview%2C_2025-05-17.jpg",
      role="Flowering Philadelphia fleabane photographed at Beechview, Pennsylvania; no Texas provenance implied."),
 dict(title="Erigeron_philadelphicus_(Philadelphia_fleabane)_(32051004951).jpg",
      file="commons-doug-mcgrady-32051004951.jpg",creator="Doug McGrady",license="CC BY 2.0",
      source="https://commons.wikimedia.org/wiki/File:Erigeron_philadelphicus_%28Philadelphia_fleabane%29_%2832051004951%29.jpg",
      role="Source-determined Philadelphia fleabane field view; check fresh heads and leaves before assigning anatomical markers."),
 dict(title="Erigeron_philadelphicus_s2.jpg",
      file="commons-alpsdake-s2-flower.jpg",creator="Alpsdake",license="CC BY-SA 4.0",
      source="https://commons.wikimedia.org/wiki/File:Erigeron_philadelphicus_s2.jpg",
      role="Source-determined flowering view from Mount Ibuki, Japan; no Hays native range inference."),
]
S=requests.Session()
S.headers.update({"User-Agent":"HaysCountyBotanyPhotoInstall/1.0 (educational field imagery; github.com/Crking92/Hays-County-Botany)"})

def download(x):
    api={"action":"query","format":"json","formatversion":"2",
         "titles":"File:"+x["title"],"prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":"960"}
    r=S.get("https://commons.wikimedia.org/w/api.php",params=api,timeout=45);r.raise_for_status()
    pages=r.json()["query"]["pages"]
    assert len(pages)==1 and "imageinfo" in pages[0], "Exact Commons file missing"
    info=pages[0]["imageinfo"][0]
    license_name=info.get("extmetadata",{}).get("LicenseShortName",{}).get("value","").strip().upper()
    if x["license"]=="CC0":
        assert "CC0" in license_name or "PUBLIC DOMAIN" in license_name, (x["title"],license_name)
    else:
        assert license_name==x["license"].upper(), (x["title"],license_name)
    url=info.get("thumburl")
    assert url and url.startswith("https://") and "wikimedia.org" in url
    img=S.get(url,timeout=60);img.raise_for_status()
    assert 19000<=len(img.content)<16000000
    with Image.open(io.BytesIO(img.content)) as source:
        source.load()
        assert source.format in ("JPEG","PNG")
        frame=ImageOps.exif_transpose(source).convert("RGB")
    assert min(frame.size)>=320
    frame.thumbnail((1450,1450), Image.Resampling.LANCZOS)
    b=io.BytesIO();frame.save(b,"JPEG",quality=90,optimize=True,progressive=True)
    data=b.getvalue()
    assert len(data)>19000
    with Image.open(io.BytesIO(data)) as test:test.verify()
    return data,hashlib.sha256(img.content).hexdigest(),list(frame.size),url

def main():
    manifest=json.loads(Path("data/manifest.json").read_text())
    assert sum(x.get("id")=="erigeron-philadelphicus" for x in manifest["species"])==1
    claims=json.loads(Path("workflow/work-claims.json").read_text()).get("claims",[])
    assert not any("erigeron-philadelphicus" in (x.get("taxa") or []) and
                   x.get("status") in ("active","claimed","in_progress") for x in claims)
    j=json.loads(CARD.read_text())
    assert j["id"]=="erigeron-philadelphicus" and j["scientific_name"]=="Erigeron philadelphicus"
    assert len(j["images"]) in (1,4)
    existing=[P/"images"/x["file"] for x in SOURCES]
    if all(x.exists() for x in existing):
        assert len(j["images"])==4
        print("Installed already; no-op")
        return
    assert not any(x.exists() for x in existing), "Partial install: manual audit required"
    assert len(j["images"])==1, "Photo inventory unexpectedly changed"
    prepared=[(x,*download(x)) for x in SOURCES]
    for x,data,sha,dim,url in prepared:
        dst=P/"images"/x["file"];dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
        j["images"].append({
            "file":"images/"+x["file"],"role":x["role"],"creator":x["creator"],
            "license":x["license"],
            "license_url":{"CC0":"https://creativecommons.org/publicdomain/zero/1.0/",
                           "CC BY 2.0":"https://creativecommons.org/licenses/by/2.0/",
                           "CC BY-SA 4.0":"https://creativecommons.org/licenses/by-sa/4.0/"}[x["license"]],
            "source_platform":"Wikimedia Commons identified original source", "source_page":x["source"],
            "downloaded_from":url,"source_file_sha256":sha,"image_dimensions":dim,
            "study_use":"Public educational photo learner under individual Commons license",
            "public_reuse":"Use exact license, credit creator, indicate JPG resizing and EXIF stripping, comply with ShareAlike where required",
            "modifications":"Downloaded 960px Commons thumbnail, JPEG normalized, EXIF removed",
            "photo_review":"Source species name and image license verified; detailed anatomical markers NOT yet pixel reviewed."
        })
    j["curation_status"].update({
        "photo_metadata_count":4,"photo_files_present":4,"photo_source_checked":True,
        "visual_reviewed":False,"physical_commons_install":"2026-10-21",
        "diagnostic_photo_review_pending":True
    })
    j["learner_visual_status"].update({
        "image_count":4,"status":"four_source_photos_diagnostic_annotation_pending",
        "note":"Four physically installed photographs: one previously licensed iNaturalist image and three added Commons images (CC0/CC BY/CC BY-SA). Real photos await pixel-level diagnostic arrow review. Do not claim stem clasping demonstrated without a clear leaf node."
    })
    j["photo_note"]="Four physical exact-source photos installed. Need anatomy-specific photo QA and correctly placed arrows: clasping stem leaf base, coarse stem hairs, 100+ slender rays, fresh head side, pappus. Do not infer native county from distant sources."
    CARD.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n")
    with LEDGER.open(newline="") as f:
        reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
    for x,data,sha,dim,url in prepared:
        row={k:"" for k in fields}
        vals={"file_name":x["file"],"role":x["role"],"creator":x["creator"],"license":x["license"],
              "source_page":x["source"],"direct_url":url,"study_use":"CC credited public botanical learner",
              "public_reuse":"Individual Commons license and author attribution; alteration noted"}
        row.update({k:v for k,v in vals.items() if k in row});rows.append(row)
    with LEDGER.open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=fields,lineterminator="\n");writer.writeheader();writer.writerows(rows)
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps({
        "taxon":"Erigeron philadelphicus","date":"2026-10-21",
        "files_added":len(prepared),"physical_photo_count":4,"annotated_new_photos":False,
        "sources":[{"name":x["file"],"creator":x["creator"],"license":x["license"],
                    "sha256":sha,"dimensions":dims} for x,data,sha,dims,url in prepared],
        "unresolved":"Inspect individual images for leaf-base clasping and stem hairs before adding arrows; fresh head and fruit side macros still needed.",
        "county_nativity_reviewed":False,"pages_success_not_yet_confirmed":True
    },indent=2)+"\n")
    print("Added 3 actual licensed Philadelphia fleabane photos: 4 total, arrow review pending")

if __name__=="__main__": main()
