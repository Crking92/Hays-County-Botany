#!/usr/bin/env python3
"""Targeted noncommercial Pages first-photo recovery from original iNaturalist IDs.

Photo-level source/copyright was independently checked on current iNaturalist
photo pages and Wikimedia Commons on 2026-10-20. Use existing canonical photo
records, no license changes or taxonomy updates, and save actual EXIF-free JPEGs.
Commons returned 429 for the identical images; fetch iNaturalist's actual source.
This rerun uses the corrected GitHub commit step; the prior Action downloaded both
images but mistakenly staged the older Commons report rather than these galleries.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import time
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "reports/public-gap-inat-recovery-20261020.json"

TARGETS = {
    "ludwigia-octovalvis": {
        "species_json": "content/taxa/Onagraceae/Ludwigia/ludwigia-octovalvis/species.json",
        "source_page": "https://commons.wikimedia.org/wiki/File:Ludwigia_octovalvis_50612016.jpg",
        "photo_page": "https://www.inaturalist.org/photos/50612016",
        "photo_id": "50612016",
        "creator": "Alex Abair",
        "license": "CC BY 4.0",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "direct_variants": [
            "https://inaturalist-open-data.s3.amazonaws.com/photos/50612016/large.jpg",
            "https://inaturalist-open-data.s3.amazonaws.com/photos/50612016/medium.jpg",
        ],
        "new_file": "images/public-alex-abair-ludwigia-fruit.jpg",
    },
    "symphyotrichum-ericoides": {
        "species_json": "content/taxa/Asteraceae/Symphyotrichum/symphyotrichum-ericoides/species.json",
        "source_page": "https://commons.wikimedia.org/wiki/File:Symphyotrichum_ericoides_97520834.jpg",
        "photo_page": "https://www.inaturalist.org/photos/97520834",
        "photo_id": "97520834",
        "creator": "Annika Lindqvist",
        "license": "CC BY 4.0",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "direct_variants": [
            "https://inaturalist-open-data.s3.amazonaws.com/photos/97520834/large.jpeg",
            "https://inaturalist-open-data.s3.amazonaws.com/photos/97520834/medium.jpeg",
        ],
        "new_file": "images/public-annika-lindqvist-heath-aster.jpg",
    },
}


def safe_download(spec: dict) -> tuple[bytes, str]:
    failure = []
    for url in spec["direct_variants"]:
        if urlparse(url).hostname != "inaturalist-open-data.s3.amazonaws.com":
            raise RuntimeError("source outside approved iNaturalist open photo bucket")
        for attempt in range(2):
            try:
                req = Request(url, headers={"User-Agent":"HaysBotanyEducationalLearner/1.0 (attributed CC-BY photographs; github.com/Crking92/Hays-County-Botany)"})
                with urlopen(req, timeout=35) as resp:
                    if urlparse(resp.geturl()).hostname != "inaturalist-open-data.s3.amazonaws.com":
                        raise RuntimeError("unexpected redirect host")
                    content = resp.read(12_000_001)
                if len(content) < 5000 or len(content) > 12_000_000:
                    raise RuntimeError("image outside allowed size window")
                return content, url
            except Exception as e:
                failure.append(str(e)[:100])
                if attempt == 0:
                    time.sleep(4)
    raise RuntimeError("iNaturalist exact-photo originals unavailable: "+"; ".join(failure)[-360:])


def unexpired_foreign_claim(taxon: str) -> bool:
    j = json.loads((ROOT / "workflow/work-claims.json").read_text())
    for claim in j.get("claims", []):
        if claim.get("status") != "active":
            continue
        expiration = claim.get("expires_at")
        if expiration:
            try:
                if datetime.fromisoformat(expiration.replace("Z","+00:00")) < datetime.now(timezone.utc):
                    continue
            except Exception:
                pass
        if taxon in (claim.get("taxa") or []):
            return True
    return False


def do_one(taxon: str, spec: dict) -> dict:
    sp = ROOT / spec["species_json"]
    j = json.loads(sp.read_text(encoding="utf-8"))
    if j.get("id") != taxon or unexpired_foreign_claim(taxon):
        raise RuntimeError("wrong taxon or currently claimed by another worker")
    candidates = [x for x in j.get("images", []) if isinstance(x,dict) and x.get("source_page")==spec["source_page"]]
    if len(candidates) != 1:
        raise RuntimeError("exact canonical original Commons record changed or missing")
    img = candidates[0]
    if img.get("file")==spec["new_file"]:
        p=sp.parent/spec["new_file"]
        if p.is_file() and p.stat().st_size>5000:
            return {"species":taxon,"status":"ALREADY_PRESENT"}
        raise RuntimeError("missing bytes for existing local record")
    if not str(img.get("file","")).startswith("https://"):
        raise RuntimeError("image no longer external; do not overwrite")
    if spec["creator"].lower() not in str(img.get("creator","")).lower():
        raise RuntimeError("photographer doesn't match independently verified source")
    if spec["license"].lower() not in str(img.get("license","")).lower():
        raise RuntimeError("license differs from the individual photo's verified copyright")
    if spec["photo_id"] not in str(img.get("file")):
        raise RuntimeError("mismatch between intended image ID and existing source photo")
    raw, downloaded_url = safe_download(spec)
    with Image.open(BytesIO(raw)) as im:
        if im.format != "JPEG":
            raise RuntimeError("downloaded bytes not JPEG")
        if min(im.size)<350:
            raise RuntimeError("downloaded photo too small")
        clean=ImageOps.exif_transpose(im).convert("RGB")
        clean.thumbnail((1600,1600),Image.Resampling.LANCZOS)
        b=BytesIO()
        clean.save(b,"JPEG",quality=88,optimize=True)
        jpg=b.getvalue()
        dims=list(clean.size)
    with Image.open(BytesIO(jpg)) as verify:
        if verify.info.get("exif") or verify.getexif().get(34853):
            raise RuntimeError("JPEG has uncleared EXIF or location metadata")
        verify.verify()
    dest=sp.parent/spec["new_file"]
    if dest.exists():
        raise RuntimeError("local filename already exists")
    dest.parent.mkdir(exist_ok=True)
    dest.write_bytes(jpg)
    img["original_remote_photo_url"]=img["file"]
    img["file"]=spec["new_file"]
    img["source_photo_id"]=spec["photo_id"]
    img["inaturalist_photo_page"]=spec["photo_page"]
    img["downloaded_from"]=downloaded_url
    img["license_url"]=spec["license_url"]
    img["public_reuse"]="yes — individual CC BY 4.0 source verified with attribution"
    img["source_file_sha256"]=sha256(raw).hexdigest()
    img["published_jpeg_sha256"]=sha256(jpg).hexdigest()
    img["published_jpeg_dimensions"]=dims
    img["modifications"]="Original iNaturalist image resized for learner and reencoded as JPEG with EXIF/GPS removed; no arrows applied."
    img["photo_review"]="Original iNaturalist photo page verified exact photographer, CC BY, observation identity on 2026-10-20; no detailed floral/fruit anatomy arrow approval."
    img["annotation_pending"]=True
    img.pop("remote_only",None)
    img["local_file_present"]=True
    sp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return {
        "species":taxon,
        "species_json":spec["species_json"],
        "physical_file":str(dest.relative_to(ROOT)),
        "relative_image_path":spec["new_file"],
        "source_photo_id":spec["photo_id"],
        "source_url":spec["photo_page"],
        "creator":spec["creator"],
        "license":spec["license"],
        "physical_jpeg_bytes":len(jpg),
        "published_jpeg_sha256":sha256(jpg).hexdigest(),
        "status":"LOCAL_READY_AWAITING_GITHUB_PUSH",
    }


def main():
    out={"utc":datetime.now(timezone.utc).isoformat(),
         "installed":[],"held":[],"never_published_pages_directly":True,
         "note":"Exact photo ID, CC BY and photographer verified from original iNaturalist photo page and Commons; no private footage used."}
    for taxon, spec in TARGETS.items():
        try:
            got=do_one(taxon,spec)
            if got.get("status")=="ALREADY_PRESENT":
                out["held"].append({"species":taxon,"reason":"already present"})
            else:
                out["installed"].append(got)
        except Exception as e:
            out["held"].append({"species":taxon,"reason":str(e)[:500]})
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"installed":[x["species"] for x in out["installed"]],"held":out["held"]},indent=2))


if __name__=="__main__":
    main()
