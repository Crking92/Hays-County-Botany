#!/usr/bin/env python3
"""Install three visually reviewed, individually licensed *provisional* photo views.
Never edit taxon/range decisions or deploy the public website. Idempotent and
meant to run after resetting to the latest main in a bounded push-retry loop.
"""
import csv, hashlib, io, json, re, sys, zipfile
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageOps

ARCHIVE=Path(sys.argv[1])
EXPECTED_ARCHIVE="bc240efe530afd361a33049468e12520d15be61202654dc5e1cfd40f68e7d80c"
REVIEW=Path("workflow/photo-library/reviews/diagnostic-004-contact-visual-roles-20261018.json")
SELECTION=[
 ("asclepias-viridiflora","staged_images/asclepias-viridiflora/gbif-e0e54287c08f97.jpg",
  "d2673a900ef903ac6bcb28d5e995d495bd48cfc1ef3b2d7e8348f1ef55274b55",
  "diagnostic004-648395540-juvenile-habit.jpg","Wendy A","CC0",
  "Young whole-plant habit: opposite broad leaves, erect stem and developing upper buds; flower corona not resolved",
  "Sharp flower corona and mature follicle still required"),
 ("cyperus-ochraceus","staged_images/cyperus-ochraceus/plantnet-via-gbif-02cd0dbff9743a.jpg",
  "97c33809c94da1de5b2b810112801b447d78b457313a141113c14668b8073e7f",
  "diagnostic004-plantnet-5109507665-spikelets.jpg","Trap Hers","CC BY-SA",
  "Close-up of ochraceous radiating spikelet clusters and leaflike bracts; achenes not shown",
  "Mature achene and stem cross-section still required"),
 ("salvia-texana","staged_images/salvia-texana/gbif-9dce3550803eb5.jpg",
  "84813bf06d2fd73b7840bff842930a71217467171ca2350eabd9980fcd3a9608",
  "diagnostic004-627129092-purple-flower-calyx.jpg","Russell Pfau","CC BY",
  "Purple bilabiate corollas, hairy calyces, upper bracts and flowering axis; gland pits not resolved",
  "Close-up of sunken leaf glands and basal foliage still required")
]
if hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()!=EXPECTED_ARCHIVE:
    raise SystemExit("Source Release archive hash mismatch")
source=json.loads(REVIEW.read_text())
if source["summary"]["total_photo_candidates_reviewed"]!=54:
    raise SystemExit("Review contract changed")
reviews={r["archive_file"]:r for r in source["photo_recommendations"]}
manifest={r["id"]:r["path"] for r in json.loads(Path("data/manifest.json").read_text())["species"]}
claims=json.loads(Path("workflow/work-claims.json").read_text()).get("claims",[])
for claim in claims:
    if claim.get("status") not in {"active","claimed","in_progress"}:continue
    expiry=claim.get("expires_at")
    if not expiry:continue
    if datetime.fromisoformat(expiry.replace("Z","+00:00"))>datetime.now(timezone.utc):
        blocked=set(claim.get("taxa") or [])&{x[0] for x in SELECTION}
        if blocked:raise SystemExit("Active claim collision: "+",".join(sorted(blocked)))

report={"batch":"diagnostic-004-first3","source_archive":"diagnostic-39139862679",
        "source_review":str(REVIEW),"state":"PHYSICAL_PROVISIONAL_INSTALL_VERIFIED",
        "photos_installed":[],"skipped_previously_installed":[],
        "taxon_and_native_metadata_unchanged":True,"other_gallery_entries_preserved":True,
        "deployment_performed":False,"license_status":"source individual media license from archived candidate records",
        "species_identity":"PROVISIONAL: morphology consistent with source-recorded identification; not independent species voucher verification"}
with zipfile.ZipFile(ARCHIVE) as z:
    for sid,arch,sha,name,creator,license,role,need in SELECTION:
        match=reviews.get(arch)
        if not match or match["visual_decision"]!="PRIORITY_PIXEL_REVIEW" or match["creator"]!=creator or match["license_metadata"]!=license:
            raise SystemExit("Metadata/pixel review mismatch for "+sid)
        if sid not in manifest:raise SystemExit("Target not canonical "+sid)
        jsonpath=Path(manifest[sid])
        species=json.loads(jsonpath.read_text())
        images=species.get("images",[])
        target=jsonpath.parent/"images"/name
        imgurl=match["image_url"]
        photom=re.search(r"/photos/(\d+)/",imgurl)
        photoid=photom.group(1) if photom else ""
        duplicate=any(
            str(e.get("file","")).endswith(name) or
            (photoid and str(e.get("photo_id",""))==photoid) or
            str(e.get("direct_image_url",e.get("downloaded_from","")))==imgurl
            for e in images)
        if duplicate:
            report["skipped_previously_installed"].append(sid)
            continue
        if target.exists():raise SystemExit("Output path collision: "+str(target))
        entries=[p for p in z.namelist() if p==arch or p.endswith("/"+arch)]
        if len(entries)!=1:raise SystemExit("Archive path not unique: "+arch)
        raw=z.read(entries[0])
        if hashlib.sha256(raw).hexdigest()!=sha:raise SystemExit("Individual image digest mismatch "+sid)
        with Image.open(io.BytesIO(raw)) as initial:
            if initial.format!="JPEG":raise SystemExit("Not JPEG "+sid)
            im=ImageOps.exif_transpose(initial).convert("RGB")
            if min(im.size)<600:raise SystemExit("Resolution below provisional teaching threshold "+sid)
            if max(im.size)>1800:im.thumbnail((1800,1800),Image.Resampling.LANCZOS)
            rendered=io.BytesIO()
            im.save(rendered,format="JPEG",quality=91,progressive=True,optimize=True,subsampling=0)
        webbytes=rendered.getvalue()
        with Image.open(io.BytesIO(webbytes)) as check:
            check.verify()
        source_platform="Pl@ntNet via GBIF" if "plantnet" in arch else "iNaturalist via GBIF"
        lic_url="" if license in ("CC BY","CC BY-SA") else "https://creativecommons.org/publicdomain/zero/1.0/"
        entry={"file":"images/"+name,"role":role,"creator":creator,"license":license,
          "license_url":lic_url,"source_platform":source_platform,"source_page":match["source_page"],
          "direct_image_url":imgurl,"photo_id":photoid,
          "study_use":"yes","public_reuse":"yes with attribution; preserve ShareAlike if applicable",
          "photo_review":"Full-size photo reviewed; anatomical view confirmed. Species-level identity remains provisional.",
          "photo_validation_status":"provisional source-taxon agreement, not specimen-confirmed",
          "modifications":"JPEG display copy, EXIF/GPS removed; original retained in private immutable archive",
          "source_archive":"diagnostic-39139862679"}
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(webbytes)
        images.append(entry)
        species["images"]=images
        status=species.get("curation_status")
        if isinstance(status,dict):
            status["photo_metadata_count"]=len(images)
            status["photo_files_present"]=sum(
                (jsonpath.parent/i["file"]).is_file() for i in images
                if i.get("file") and not str(i["file"]).startswith(("http://","https://")))
            status["diagnostic_b004_provisional_installed"]="2026-10-19"
        jsonpath.write_text(json.dumps(species,indent=2,ensure_ascii=False)+"\n")
        csvpath=jsonpath.parent/"image-sources.csv"
        if csvpath.exists():
            with csvpath.open(newline="",encoding="utf-8") as f:
                headers=next(csv.reader(f))
            line={"file_name":name,"role":role,"platform":source_platform,
                  "creator":creator,"license":license,"source_page":match["source_page"],
                  "direct_url":imgurl,"direct_image_url":imgurl,"photo_id":photoid,
                  "study_use":"yes","public_reuse":"yes with attribution / ShareAlike",
                  "review":"provisional species ID; full-resolution visible role reviewed",
                  "modifications":"EXIF stripped; resized JPEG copy; original private archive"}
            with csvpath.open("a",newline="",encoding="utf-8") as f:
                writer=csv.DictWriter(f,fieldnames=headers,extrasaction="ignore")
                writer.writerow(line)
        report["photos_installed"].append({"species_id":sid,"photo":str(target),
            "bytes":len(webbytes),"sha256":hashlib.sha256(webbytes).hexdigest(),
            "role":role,"creator":creator,"license":license,"source_page":match["source_page"],
            "source_original":imgurl,"remaining_need":need,
            "gallery_count_after":len(images)})
out=Path("reports/photo-batch004-first3-provisional-installer.json")
out.parent.mkdir(parents=True,exist_ok=True)
report["installed_count"]=len(report["photos_installed"])
out.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({"installed_count":report["installed_count"],
    "species":[x["species_id"] for x in report["photos_installed"]],
    "skipped":report["skipped_previously_installed"]},indent=2))
