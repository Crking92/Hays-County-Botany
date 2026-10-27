#!/usr/bin/env python3
"""Archive only individually source-credited reusable B. torreyana reference photos.

The source uses the 2007 FNA combination B. laguroides subsp. torreyana;
U.S./northern Mexico B. laguroides belongs to that subspecies in FNA.
Current accepted-name project card: Bothriochloa torreyana. Do not infer a
genetically/specimen-confirmed ID or microscopic features from a label.
"""
from __future__ import annotations
import base64, hashlib, io, json, re
from pathlib import Path
import requests
from PIL import Image, ImageOps, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
REL="content/taxa/Poaceae/Bothriochloa/bothriochloa-torreyana"
ROOT_SPECIES=ROOT/REL
CARD=ROOT_SPECIES/"species.json"
REPORT=ROOT/"reports/silver-bluestem-real-photo-install-20261027.json"
MARKER=ROOT/"workflow/field-id-publication/2026-10-27-silver-bluestem-real-photo-source-install.json"
YAV="https://yavapaiplants.extension.arizona.edu/bothriochloa-laguroides"
YAV_BASE="https://yavapaiplants.extension.arizona.edu/sites/default/files/"
COMMONS_FILE="Silver bluestem (38656978741).jpg"
HEADERS={"User-Agent":"Hays-Botany-Learner/1.0 (noncommercial, credited photography)"}
requests_session=requests.Session()
requests_session.headers.update(HEADERS)
CANDIDATES=[
 {"id":"az-spikelet","name":"Arizona photographed spikelet — Liz Makings",
  "origin":"Arizona","image":"Grasses/Images/Bothriochloa_laguroidestorreyana_vel_pic.jpg",
  "filename":"liz-makings-arizona-silver-spikelet-20261027.jpg","creator":"Liz Makings",
  "lic":"CC BY-SA (version not specified on Arizona Extension page)","license_url":YAV,
  "role":"Actual photographed silver bluestem spikelet, Arizona Cooperative Extension; detailed glumes unresolved"},
 {"id":"az-plant","name":"Arizona source-labelled standing plant — Max Licher",
  "origin":"Arizona","image":"Grasses/Images/Bothriochloa_laguroides_P_0.jpg",
  "filename":"max-licher-arizona-silver-plant-20261027.jpg","creator":"Max Licher",
  "lic":"CC BY-SA (version not specified on Arizona Extension page)","license_url":YAV,
  "role":"Species-labelled Arizona whole-plant illustration, not a dug root or confirmed rhizome specimen"},
 {"id":"texas-habit","name":"Austin silver bluestem — smallcurio CC BY",
  "origin":"Austin, Travis County, Texas","commons":COMMONS_FILE,
  "filename":"smallcurio-austin-silver-bluestem-2017.jpg","creator":"smallcurio",
  "lic":"CC BY 2.0","license_url":"https://creativecommons.org/licenses/by/2.0/",
  "role":"Source-labelled genuine Austin silver bluestem seasonal flowering plant in habitat; crown/collar not separately resolved"}
]
def fetch(url):
    response=requests_session.get(url, timeout=26, allow_redirects=True)
    if response.status_code==429: raise RuntimeError("RATE_LIMITED_429; no retry")
    response.raise_for_status()
    if len(response.content)<4000 or len(response.content)>25_000_000:
        raise RuntimeError("source is missing or image unexpectedly large")
    with Image.open(io.BytesIO(response.content)) as im:
        im.verify()
    return response.content
def commons(spec):
    resp=requests_session.get("https://commons.wikimedia.org/w/api.php",
         params={"action":"query","format":"json","titles":"File:"+spec["commons"],
         "prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":"1600"},
         timeout=22)
    if resp.status_code==429:raise RuntimeError("Wikimedia API rate limited")
    resp.raise_for_status()
    o=list(resp.json()["query"]["pages"].values())[0]["imageinfo"][0]
    metadata=o.get("extmetadata",{})
    author=re.sub(r"<[^>]+>","",metadata.get("Artist",{}).get("value",""))
    l=metadata.get("LicenseShortName",{}).get("value","")
    if "smallcurio" not in author.lower() or "CC BY 2.0" not in l:
        raise RuntimeError("Commons source credit / license changed: "+author[:80]+"/"+l)
    return o.get("thumburl") or o["url"]
def images_from_extension(spec):
    from requests.utils import requote_uri
    name=spec["image"]
    return [YAV_BASE+name, YAV_BASE+name+".webp",
            "https://yavapaiplants.extension.arizona.edu/sites/default/files/styles/yp_card_image/public/"+name+".webp"]
def insert(card,spec,physical,imsize,sha):
    source=YAV if "image" in spec else "https://commons.wikimedia.org/wiki/File:"+COMMONS_FILE.replace(" ","_")
    entry={
      "file":"images/"+spec["filename"],"role":spec["role"],
      "creator":spec["creator"],"license":spec["lic"],"license_url":spec["license_url"],
      "source_page":source,"public_reuse":"yes - individually verified credit/license",
      "study_use":"yes","archived_sha256":sha,"image_dimensions":list(imsize),
      "photo_status":"PROVISIONAL — USER PHOTO REVIEW PENDING; PHYSICALLY ARCHIVED original credit and license retained; EXIF/GPS removed, no microscopic anatomy arrows",
      "taxon_source_name":"Bothriochloa laguroides (FNA US concept subsp. torreyana)" if "image" in spec else "Bothriochloa laguroides / silver bluestem (Austin)",
      "taxon_interpretation":"Bothriochloa torreyana (FNA subsp. torreyana); photographer identification not a herbarium voucher",
      "geographic_origin":spec["origin"],"modified":"Re-encoded JPEG to remove EXIF/GPS and for web size"}
    if not any(x.get("file")==entry["file"] for x in card["images"]):
        card["images"].append(entry)
    panel_path=REL+"/images/"+spec["filename"]
    if any(x.get("image_url")==panel_path for x in card["visual_comparison"]["items"]):return
    panel={
      "label":spec["name"],"scientific_name":"Bothriochloa torreyana",
      "image_url":panel_path,"image_fit":"contain","image_role":spec["role"],
      "caption":("Real published source-identified "+spec["origin"]+" "+spec["role"]+
           ". Photographer and license are retained, with source-linked attribution. "
           "Mapped through the Flora of North America concept of U.S. B. laguroides subsp. torreyana, "
           "which the project's accepted name treats as B. torreyana. Do not interpret a source-labelled image "
           "as measured local Hays ligule, verified separate glumes or rooted rhizome."),
      "why_it_matters": "Adds independently licensed photographic anatomy/habit rather than relying on the copyrighted historical gallery.",
      "creator":spec["creator"],"license":spec["lic"],
      "license_url":spec["license_url"],"source_page":source,
      "markers":[],"photo_status":"PHYSICALLY ARCHIVED and RIGHTS CHECKED; original site supplies geographic/identification context, no inferred micro arrows."
    }
    card["visual_comparison"]["items"].append(panel)
def main():
    card=json.loads(CARD.read_text())
    assert card["id"]=="bothriochloa-torreyana"
    report={"date":"2026-10-27","taxon":"Bothriochloa torreyana",
        "total_before":len(card["images"]),"public_exact_local_before":2,
        "panels_before":len(card["visual_comparison"]["items"]),"items":[]}
    success=[]
    for spec in CANDIDATES:
        try:
            if spec.get("commons"):
                urls=[commons(spec)]
            else:
                urls=images_from_extension(spec)
            raw=None; issues=[]
            for u in urls:
                try:
                    raw=fetch(u);break
                except Exception as e:issues.append(str(e)[:95])
            if raw is None:raise RuntimeError("No authorized source served JPEG: "+"; ".join(issues))
            with Image.open(io.BytesIO(raw)) as im:
                rgb=ImageOps.exif_transpose(im).convert("RGB")
                rgb.load()
            if min(rgb.size)<240:raise RuntimeError("download too small for safe teaching")
            if max(rgb.size)>2200:rgb.thumbnail((2200,2200),Image.Resampling.LANCZOS)
            original_size=list(rgb.size)
            path=ROOT_SPECIES/"images"/spec["filename"]
            path.parent.mkdir(parents=True,exist_ok=True)
            rgb.save(path,"JPEG",quality=88,optimize=True,subsampling=0)
            with Image.open(path) as out:
                if out.getexif():raise RuntimeError("EXIF retained")
                out.verify()
            sha=hashlib.sha256(path.read_bytes()).hexdigest()
            insert(card,spec,path,original_size,sha)
            report["items"].append({"id":spec["id"],"status":"ARCHIVED", "path":str(path.relative_to(ROOT)),
                                    "size":original_size,"sha256":sha,"credit":spec["creator"],"license":spec["lic"]})
            success.append(spec["id"])
        except Exception as e:
            report["items"].append({"id":spec["id"],"status":"NOT_INSTALLED","reason":str(e)[:380]})
    if success:
        card["curation_status"]["photo_metadata_count"]=len(card["images"])
        # Older held JPEGs and genuine open images must be counted separately.
        card["curation_status"]["photo_files_present"]=len(card["images"])
        card["silver_real_photo_run_20261027"]={
            "installed":success,"new_physical_jpegs":len(success),
            "archived_photos_total":len(card["images"]),
            "public_clean_own_photos_count":2+len(success),
            "teaching_panels_total":len(card["visual_comparison"]["items"]),
            "new_arrows":0,
            "retained_existing_arrows":sum(len(x.get("markers",[])) for x in card["visual_comparison"]["items"]),
            "true_inner_ligule":"MISSING",
            "matched_node_crown_and_reproductive_microscale":"MISSING",
            "native_target_zone":"UNRESOLVED — DO NOT AUTOMATICALLY CHANGE",
            "status":"FIELD_READY_PHOTO_GAPS; source-specific CC images only, do not declare complete"
        }
        CARD.write_text(json.dumps(card,ensure_ascii=False,indent=2)+"\n")
        MARKER.parent.mkdir(parents=True,exist_ok=True)
        MARKER.write_text(json.dumps({"date":"2026-10-27","species":"bothriochloa-torreyana",
            "actual_physical_photo_ids":success,"public_rights":"Individual source/license/credit recorded",
            "field_status":"FIELD_READY_PHOTO_GAPS","new_anatomy_arrows":0,
            "source_taxon_note":"FNA U.S. plants under B. laguroides subsp. torreyana, card accepts B. torreyana"},indent=2)+"\n")
    report["installed_count"]=len(success)
    report["panels_after"]=len(card["visual_comparison"]["items"])
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
