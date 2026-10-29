#!/usr/bin/env python3
"""Install one explicitly approved user-owned iNaturalist image batch into canonical learner.

Idempotent, exact photo+taxon gated, provenance preserved, EXIF/location stripped.
This script is designed for a GitHub Actions runner; requires Pillow.
"""
import csv
import io
import json
import pathlib
import re
import sys
import urllib.parse
import urllib.request
from PIL import Image, ImageOps, UnidentifiedImageError

ROOT=pathlib.Path(".")
BATCH=ROOT/"workflow/glass-root-inat/one-plant-001/approved-photo-install-001.json"
HEADERS={"User-Agent":"HaysBotany-GlassRootGarden-CanonicalInstall/1.0 (https://github.com/Crking92/Hays-County-Botany)",
         "Accept":"application/json,image/jpeg,image/png,image/webp,*/*"}
PHOTO_SITES={"static.inaturalist.org","inaturalist-open-data.s3.amazonaws.com","inaturalist-open-data.s3.us-east-1.amazonaws.com"}
def fetch(url,limit=14000000):
    req=urllib.request.Request(url,headers=HEADERS)
    with urllib.request.urlopen(req,timeout=35) as r:
        data=r.read(limit+1)
    if len(data)>limit: raise ValueError("Download too large: "+url)
    return data
def validated_photo(target,photo):
    observation_id=photo["observation_id"]
    data=json.loads(fetch("https://api.inaturalist.org/v1/observations/"+str(observation_id)).decode("utf-8"))
    matches=data.get("results") or []
    if len(matches)!=1: raise ValueError("Observation not found: "+str(observation_id))
    obs=matches[0]
    username=(obs.get("user") or {}).get("login","").lower()
    scientific=(obs.get("taxon") or {}).get("name","")
    if username!="calvinking": raise ValueError("Photo not under known observer: "+str(observation_id))
    if scientific!=target["scientific_name"]:
        raise ValueError("Taxon mismatch, expected %s got %s" % (target["scientific_name"],scientific))
    matching=[p for p in (obs.get("photos") or []) if str(p.get("id"))==str(photo["id"])]
    if len(matching)!=1: raise ValueError("Exact photo not attached to its observation")
    source=matching[0]
    credit=(source.get("attribution") or "").lower()
    if not any(s in credit for s in ("calvin king","calvinking","glass root garden")):
        raise ValueError("Photographer attribution mismatch: "+str(photo["id"]))
    src=source.get("url") or ""
    parsed=urllib.parse.urlparse(src)
    if parsed.scheme!="https" or parsed.hostname not in PHOTO_SITES:
        raise ValueError("Untrusted source domain: "+src)
    best=re.sub(r"/(?:square|thumb|small|medium|large|original)\.(?:jpg|jpeg|png)$",
                "/large.jpg",src,flags=re.I)
    if best==src: raise ValueError("Unexpected photo URL format: "+src)
    raw=fetch(best)
    try:
        with Image.open(io.BytesIO(raw)) as im:
            im.load()
            rgb=ImageOps.exif_transpose(im).convert("RGB")
    except (UnidentifiedImageError,OSError) as err:
        raise ValueError("Invalid image data: "+str(photo["id"])) from err
    if max(rgb.size)<900 or min(rgb.size)<500:
        raise ValueError("Resolution too low (%r) for canonical image %s" % (rgb.size,photo["id"]))
    # Re-encode to remove EXIF and embedded geolocation before publishing.
    rgb.thumbnail((2048,2048),Image.Resampling.LANCZOS)
    b=io.BytesIO()
    rgb.save(b,format="JPEG",quality=91,optimize=True,progressive=True)
    if len(b.getvalue())<20000: raise ValueError("Unexpectedly small JPEG output")
    return b.getvalue(),best,source.get("license_code") or "none_recorded",source.get("attribution") or "",rgb.size

def make_csv(existing, records):
    r=csv.DictReader(io.StringIO(existing))
    columns=list(r.fieldnames or [])
    items=list(r)
    for x in records:
        rec={k:"" for k in columns}
        extra={
            "file_name":x["file_name"],
            "role":x["role"],
            "platform":"iNaturalist (photo owner authorized CC BY 4.0)",
            "observation_id":str(x["observation_id"]),
            "photo_id":str(x["photo_id"]),
            "creator":"Glass Root Garden",
            "license":"CC BY 4.0 (direct photographer grant)",
            "source_page":x["photo_page"],
            "direct_image_url":x["downloaded_from"],
            "study_use":"yes",
            "public_reuse":"yes",
            "license_url":"https://creativecommons.org/licenses/by/4.0/",
            "source_context":"Owner confirmed photographs are personally taken; direct license permission in project conversation 2026-10-14. iNaturalist legacy API source license preserved separately in species image metadata."
        }
        for k,val in extra.items():
            if k in rec:rec[k]=val
        if not any(x["file_name"]==old.get("file_name") for old in items):
            items.append(rec)
    buff=io.StringIO()
    w=csv.DictWriter(buff,fieldnames=columns,lineterminator="\n")
    w.writeheader()
    w.writerows(items)
    return buff.getvalue()

def main():
    # Retired direct-to-original-hub photo installer. Photos now belong only
    # in the approved destination family repo, under exact per-image rights.
    # Block before any iNaturalist/network calls or source-file mutation.
    from resolve_new_plant_write import load_and_validate
    load_and_validate()
    raise SystemExit(
        "ROUTING_BLOCKED: legacy Glass Root photo installer targets the old "
        "read-only learner. Route only manually reviewed images, with their "
        "source/creator/license, into the active family repository branch. "
        "No photos downloaded or imported."
    )
    batch=json.loads(BATCH.read_text(encoding="utf-8"))
    manifest=json.loads((ROOT/"data/manifest.json").read_text(encoding="utf-8"))
    canonical={s["id"]:s["path"] for s in manifest["species"]}
    operations=[]
    for target in batch["targets"]:
        path=target["path"]
        if canonical.get(target["id"])!=path:
            raise ValueError("Canonical manifest mismatch: "+target["id"])
        species_path=ROOT/path
        species=json.loads(species_path.read_text(encoding="utf-8"))
        if species.get("id")!=target["id"]:
            raise ValueError("Species ID mismatch")
        folder=species_path.parent
        if not folder.joinpath("image-sources.csv").is_file() or not folder.joinpath("SOURCES.txt").is_file():
            raise ValueError("Missing required species provenance files")
        seen={str(x.get("photo_id")) for x in species.get("images",[]) if x.get("photo_id") is not None}
        seen_names={x.get("file") for x in species.get("images",[])}
        new=[]
        for p in target["photos"]:
            rel="images/"+p["filename"]
            if str(p["id"]) in seen:
                print("Already installed:",str(p["id"]),flush=True)
                continue
            if rel in seen_names or folder.joinpath(rel).exists():
                raise ValueError("Would overwrite canonical image "+rel)
            data,download_url,api_license,api_credit,dim=validated_photo(target,p)
            op={"target":target,"photo":p,"binary":data,
                "downloaded_from":download_url,"api_license":api_license,
                "api_credit":api_credit,"size":dim,"species_path":species_path,
                "file_name":p["filename"],"folder":folder,
                "photo_page":"https://www.inaturalist.org/photos/"+str(p["id"]),
                "role":p["role"],"observation_id":p["observation_id"],"photo_id":p["id"]}
            new.append(op)
        operations.append((species,new))
    # All files verified before modifying any canonical content.
    edits=0
    for species,new in operations:
        if not new:continue
        folder=new[0]["folder"]
        for item in new:
            dest=folder/"images"/item["file_name"]
            dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_bytes(item["binary"])
            species.setdefault("images",[]).append({
                "file":"images/"+item["file_name"],"role":item["role"],
                "creator":"Glass Root Garden", "license":"CC BY 4.0",
                "license_url":"https://creativecommons.org/licenses/by/4.0/",
                "license_basis":"Direct license from photographer confirmed in user conversation 2026-10-14",
                "source_platform":"iNaturalist",
                "source_page":item["photo_page"],
                "observation_url":"https://www.inaturalist.org/observations/"+str(item["observation_id"]),
                "observation_id":item["observation_id"],"photo_id":item["photo_id"],
                "source_recorded_photo_license_at_download":item["api_license"],
                "source_recorded_photo_attribution_at_download":item["api_credit"],
                "downloaded_from":item["downloaded_from"],
                "image_dimensions":list(item["size"]),
                "study_use":"yes","public_reuse":"yes",
                "photo_review":"hand-reviewed and exact-species observation verified",
                "anatomy_arrows":"not yet installed; only label directly observed structures"
            })
            print("INSTALL",species["id"],item["photo_id"],item["size"],flush=True)
            edits+=1
        sources=folder/"image-sources.csv"
        sources.write_text(make_csv(sources.read_text(encoding="utf-8-sig"),new),
                           encoding="utf-8")
        src=folder/"SOURCES.txt"
        additions="\nGLASS ROOT GARDEN DIRECT-PHOTOGRAPHER PHOTO INSTALL (2026-10-14)\n"
        additions+="Public learner credit: Glass Root Garden. CC BY 4.0 licensed directly by photographer.\n"
        additions+="iNaturalist observation/photo links and image files:\n"
        for item in new:
            additions+="- "+str(item["photo_id"])+" "+item["photo_page"]+" | "+str(item["observation_id"])+" | images/"+item["file_name"]+"\n"
        additions+="Original iNaturalist photo license state, when different, is retained in species images[] provenance; do not attribute the owner grant to iNaturalist.\n"
        src.write_text(src.read_text(encoding="utf-8")+additions,encoding="utf-8")
        s=species.setdefault("curation_status",{})
        s["photo_metadata_count"]=len(species["images"])
        s["photo_files_present"]=len(species["images"])
        s["glass_root_garden_photo_install"]="2026-10-14"
        if isinstance(species.get("learner_visual_status"),dict):
            species["learner_visual_status"]["image_count"]=len(species["images"])
            species["learner_visual_status"]["status"]="photo_enriched_diagnostic_macros_pending"
        species["photo_note"]=(species.get("photo_note","")+" Glass Root Garden owned-photo additions installed 2026-10-14; more diagnostic macros remain useful.").strip()
        new[0]["species_path"].write_text(json.dumps(species,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    requested=sum(len(t["photos"]) for t in batch["targets"])
    if edits!=requested:
        existing=requested-edits
        if edits==0:print("All requested photos already installed; idempotent no-op",flush=True)
        else:print("Partial existing gallery; installed remaining %d photos (%d already present)" %(edits,existing),flush=True)
    print("Installed files:",edits,flush=True)
if __name__=="__main__":
    main()
