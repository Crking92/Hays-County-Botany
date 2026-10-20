#!/usr/bin/env python3
"""Recover four ALREADY-STAGED exact species Wikimedia Commons images.

Only these four individual photo records are selected, and their source pages,
authors and licensing were externally examined on 2026-10-20. Exact-source
JPEGs are downloaded to local images/, decoded, EXIF removed, and the existing
remote image records are re-pointed to real bytes with intact provenance.
No provisional Joey/private-source images are installed or relicensed.
No native/taxonomy/site/publishing changes. The Pages worker publishes later.
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
REPORT_PATH = ROOT / "reports/public-gap-commons-recovery-20261020.json"

TARGETS = {
    "arbutus-xalapensis": {
        "species_json": "content/taxa/Ericaceae/Arbutus/arbutus-xalapensis/species.json",
        "source_page": "https://commons.wikimedia.org/wiki/File:Texas_madrone_tree_arbutus_xalapensis.jpg",
        "expected_license": "Public Domain",
        "expected_creator": "Gary M. Stolz",
        "filename": "images/public-gary-stolz-texas-madrone.jpg",
        "license_url": "https://creativecommons.org/publicdomain/mark/1.0/",
    },
    "ludwigia-octovalvis": {
        "species_json": "content/taxa/Onagraceae/Ludwigia/ludwigia-octovalvis/species.json",
        "source_page": "https://commons.wikimedia.org/wiki/File:Ludwigia_octovalvis_50612016.jpg",
        "expected_license": "CC BY 4.0",
        "expected_creator": "Alex Abair",
        "filename": "images/public-alex-abair-ludwigia-fruit.jpg",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
    },
    "symphyotrichum-ericoides": {
        "species_json": "content/taxa/Asteraceae/Symphyotrichum/symphyotrichum-ericoides/species.json",
        "source_page": "https://commons.wikimedia.org/wiki/File:Symphyotrichum_ericoides_97520834.jpg",
        "expected_license": "CC BY 4.0",
        "expected_creator": "Annika Lindqvist",
        "filename": "images/public-annika-lindqvist-heath-aster.jpg",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
    },
    "tinantia-anomala": {
        "species_json": "content/taxa/Commelinaceae/Tinantia/tinantia-anomala/species.json",
        "source_page": "https://commons.wikimedia.org/wiki/File:Tinantia_anomala_(Anne_Worner).jpg",
        "expected_license": "CC BY 2.0",
        "expected_creator": "Anne Worner",
        "filename": "images/public-anne-worner-false-dayflower.jpg",
        "license_url": "https://creativecommons.org/licenses/by/2.0/",
    },
}


def claimed_elsewhere(taxon: str) -> bool:
    claims_path = ROOT / "workflow/work-claims.json"
    if not claims_path.is_file():
        return True  # fail closed rather than race on a missing tracker
    claims = json.loads(claims_path.read_text()).get("claims", [])
    now = datetime.now(timezone.utc)
    for item in claims:
        if item.get("status") != "active":
            continue
        expiry = item.get("expires_at")
        if expiry:
            try:
                until = datetime.fromisoformat(expiry.replace("Z", "+00:00"))
                if until < now:
                    continue
            except ValueError:
                pass
        text = json.dumps({"taxa": item.get("taxa", []), "scope_key": item.get("scope_key", "")})
        if taxon in text:
            return True
    return False


def retrieve(url: str) -> bytes:
    allowed = {"upload.wikimedia.org", "commons.wikimedia.org"}
    if urlparse(url).hostname not in allowed or not url.startswith("https://"):
        raise ValueError("unapproved source host, not Wikimedia Commons")
    last_error = None
    for attempt in range(3):
        try:
            req = Request(url, headers={
                "User-Agent": "HaysBotanyLearner/1.0 (educational Wikimedia Commons file attribution; GitHub Crking92/Hays-County-Botany)",
                "Accept": "image/jpeg,image/*;q=0.9",
            })
            with urlopen(req, timeout=35) as response:
                final_host = urlparse(response.geturl()).hostname
                if final_host not in allowed:
                    raise ValueError("redirect to unapproved image host")
                data = response.read(16_000_001)
            if len(data) > 16_000_000:
                raise ValueError("source image exceeds 16 MB input safety cap")
            if len(data) < 5000:
                raise ValueError("source image too small to be a useful photograph")
            return data
        except Exception as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(5 + attempt * 7)
    raise RuntimeError("source photo download failed after 3 tries: " + str(last_error)[:200])


def recover(taxon: str, spec: dict) -> dict:
    path = ROOT / spec["species_json"]
    j = json.loads(path.read_text(encoding="utf-8"))
    if j.get("id") != taxon:
        raise ValueError("identity/ID mismatch; do not select another taxon")
    if claimed_elsewhere(taxon):
        raise RuntimeError("unexpired active claim belongs to another lane; skip")
    selected = [
        x for x in j.get("images", [])
        if isinstance(x, dict) and x.get("source_page") == spec["source_page"]
    ]
    if len(selected) != 1:
        raise RuntimeError("expected exactly one existing exact Commons source record")
    image = selected[0]
    if image.get("file") == spec["filename"]:
        real = (path.parent / spec["filename"]).resolve()
        if real.is_file() and real.stat().st_size > 5000:
            return {"species":taxon,"status":"ALREADY_INSTALLED","physical_file":str(real.relative_to(ROOT))}
        raise RuntimeError("record already points to local filename but bytes are missing")
    url = image.get("file") or ""
    if not url.startswith("https://"):
        raise RuntimeError("source field is not the expected original external URL")
    if spec["expected_license"].lower() not in (image.get("license") or "").lower():
        raise RuntimeError("existing individual photo license changed; review before publishing")
    if spec["expected_creator"].lower() not in (image.get("creator") or "").lower():
        raise RuntimeError("existing creator mismatch; do not relabel")
    raw = retrieve(url)
    with Image.open(BytesIO(raw)) as input_photo:
        if input_photo.format != "JPEG":
            raise RuntimeError("source file is not JPEG")
        width, height = input_photo.size
        if min(width, height) < 350:
            raise RuntimeError("too few pixels for identification photo")
        # Pixel-preserving orientation and JPG copy without GPS/EXIF metadata.
        image_pixels = ImageOps.exif_transpose(input_photo).convert("RGB")
        image_pixels.thumbnail((1800, 1800), Image.Resampling.LANCZOS)
        output = path.parent / spec["filename"]
        output.parent.mkdir(exist_ok=True)
        if output.exists():
            raise RuntimeError("new output filename already exists; no overwrite")
        buffer = BytesIO()
        image_pixels.save(buffer, format="JPEG", quality=88, optimize=True)
        jpeg = buffer.getvalue()
    if len(jpeg) < 5000:
        raise RuntimeError("converted JPEG suspiciously small")
    with Image.open(BytesIO(jpeg)) as clean:
        if clean.getexif().get(34853) is not None or clean.info.get("exif"):
            raise RuntimeError("published JPG copy still contains EXIF/GPS")
        clean.verify()
    output.write_bytes(jpeg)
    image["original_remote_photo_url"] = url
    image["file"] = spec["filename"]
    image["source_platform"] = "Wikimedia Commons (individually checked photo page)"
    image["license_url"] = spec["license_url"]
    image["public_reuse"] = "yes, with source-specific license and credits"
    image["changes"] = "Downloaded original/Commons preview, resized for field learner and reencoded to JPEG; EXIF/GPS stripped; no anatomy arrows added."
    image["photo_review"] = "Original Commons image author, photo-level license and exact taxon source page checked 2026-10-20. Distinguishing anatomy and accepted taxon interpretation still require field-card review."
    image["annotation_pending"] = True
    image["source_sha256"] = sha256(raw).hexdigest()
    image["published_jpeg_sha256"] = sha256(jpeg).hexdigest()
    image["published_jpeg_dimensions"] = list(image_pixels.size)
    image.pop("remote_only", None)
    image["local_file_present"] = True
    path.write_text(json.dumps(j, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {
        "species": taxon, "status": "INSTALLED_ON_LOCAL_CHECKOUT_AWAITING_PUSH",
        "species_json": spec["species_json"],
        "physical_file": str(output.relative_to(ROOT)),
        "relative_image_path": spec["filename"],
        "photo_creator": image.get("creator"),
        "photo_license": image.get("license"),
        "photo_source_page": image.get("source_page"),
        "source_sha256": image["source_sha256"],
        "published_jpeg_sha256": image["published_jpeg_sha256"],
        "image_bytes": len(jpeg),
        "image_dimensions": list(image_pixels.size),
    }


def main() -> None:
    report = {
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Recover four already recorded, manually source/license checked exact Commons photo candidates",
        "installed": [], "held": [],
        "no_website_deployment": True,
        "no_original_private_frame_or_license_rewritten": True,
    }
    for taxon, spec in TARGETS.items():
        try:
            result = recover(taxon, spec)
            if result["status"] == "ALREADY_INSTALLED":
                report["held"].append({"species":taxon,"reason":"already locally installed; no duplicate"})
            else:
                report["installed"].append(result)
        except Exception as exc:
            report["held"].append({"species":taxon,"reason":str(exc)[:350]})
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    print(json.dumps({"installed":[i["species"] for i in report["installed"]],"held":report["held"]},indent=2))


if __name__ == "__main__":
    main()
