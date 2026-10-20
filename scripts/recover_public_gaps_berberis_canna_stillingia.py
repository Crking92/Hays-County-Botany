#!/usr/bin/env python3
"""Three-species exact taxon recovery: Berberis swaseyi, Canna glauca and Stillingia texana.

The existing privately sourced Joey video-frame research records remain untouched and excluded
from the rights-filtered public website. Select one iNaturalist observation
identified at EXACT species and Research Grade, then verify the individual
photo's own current Creative Commons license, creator attribution and physical
bytes. This is an educational, strictly noncommercial learner: CC BY and
CC BY-NC originals are eligible WITH conditions. No morphology arrow is claimed.
The existing Pages marker and public build remain separate; only this photo recovery lane installs images.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import time
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "reports/public-gap-berberis-canna-stillingia-20261020.json"

TARGETS = {
    "berberis-swaseyi": {
        "species_json": "content/taxa/Berberidaceae/Berberis/berberis-swaseyi/species.json",
        "scientific_name": "Berberis swaseyi",
        "filename_prefix": "images/public-inat-berberis-swaseyi",
        "role": "Provisional exact-species public first view of Swasey barberry. Check pinnately arranged stiff spine-toothed leaflets and fruit or flowers only when actually visible; fine anatomical arrows remain pending.",
    },
    "canna-glauca": {
        "species_json": "content/taxa/Cannaceae/Canna/canna-glauca/species.json",
        "scientific_name": "Canna glauca",
        "filename_prefix": "images/public-inat-canna-glauca",
        "role": "Provisional exact-species public first view of golden canna. Wetland habit, alternate broad glaucous leaves and floral staminodes require specific image confirmation before anatomy labels.",
    },
    "stillingia-texana": {
        "species_json": "content/taxa/Euphorbiaceae/Stillingia/stillingia-texana/species.json",
        "scientific_name": "Stillingia texana",
        "filename_prefix": "images/public-inat-stillingia-texana",
        "role": "Provisional exact-species public first view of Texas stillingia. Narrow leaves, separate male/female flower details and three-lobed capsules require future part-specific verified photos.",
    },
}
HOSTS = {"api.inaturalist.org", "static.inaturalist.org", "inaturalist-open-data.s3.amazonaws.com"}

def retrieve(url: str, cap: int = 5_000_000) -> bytes:
    if not url.startswith("https://") or urlparse(url).hostname not in HOSTS:
        raise ValueError("non-iNaturalist photo or redirect endpoint")
    err = None
    for attempt in range(2):
        try:
            req = Request(url, headers={"User-Agent": "HaysBotanyVisualLearner/1.0 (noncommercial education; individually credited research-grade photographs; github.com/Crking92/Hays-County-Botany)", "Accept": "application/json,image/jpeg,image/*;q=0.8"})
            with urlopen(req, timeout=27) as response:
                if urlparse(response.geturl()).hostname not in HOSTS:
                    raise RuntimeError("unexpected photo redirect host")
                content = response.read(cap + 1)
            if len(content) > cap:
                raise RuntimeError("image/API response exceeds file size limit")
            return content
        except Exception as exc:
            err = exc
            if attempt == 0:
                time.sleep(3)
    raise RuntimeError("Photo/API download failed: " + str(err)[:145])

def read_json(url: str) -> dict:
    obj = json.loads(retrieve(url, 3_000_000).decode("utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("unexpected iNaturalist JSON API response")
    return obj

def held_claim(taxon: str) -> bool:
    data = json.loads((ROOT / "workflow/work-claims.json").read_text(encoding="utf-8"))
    now = datetime.now(timezone.utc)
    for entry in data.get("claims", []):
        if entry.get("status") != "active":
            continue
        expiration = entry.get("expires_at")
        if expiration:
            try:
                if datetime.fromisoformat(expiration.replace("Z", "+00:00")) <= now:
                    continue
            except ValueError:
                pass
        if taxon in (entry.get("taxa") or []) or taxon in str(entry.get("scope_key") or ""):
            return True
    return False

def license_name(photo: dict) -> tuple[str, str]:
    code = str(photo.get("license_code") or "").lower()
    if code == "cc-by":
        return "CC BY 4.0", "https://creativecommons.org/licenses/by/4.0/"
    if code == "cc-by-nc":
        return "CC BY-NC 4.0", "https://creativecommons.org/licenses/by-nc/4.0/"
    raise ValueError("individual photograph license is not valid CC BY or CC BY-NC")

def url_for_photo(photo: dict) -> list[str]:
    url = str(photo.get("url") or "")
    if not url.startswith("https://"):
        return []
    # Use exact photo ID URL and full provenance. Do not substitute another observation.
    variants = []
    for size in ("large", "medium"):
        candidate = url
        for old in ("square", "small", "medium", "large", "thumb"):
            candidate = candidate.replace("/" + old + ".", "/" + size + ".")
        if candidate not in variants:
            variants.append(candidate)
    return [v for v in variants if urlparse(v).hostname in HOSTS]

def photo_bytes(photo: dict) -> tuple[bytes, list[int], str, str]:
    fail = []
    for url in url_for_photo(photo):
        try:
            data = retrieve(url, 12_000_000)
            if len(data) < 6_500:
                raise ValueError("downloaded photo too small to authenticate")
            with Image.open(BytesIO(data)) as original:
                if original.format not in {"JPEG", "PNG", "WEBP"} or min(original.size) < 420:
                    raise ValueError("invalid image format or insufficient resolution")
                clean = ImageOps.exif_transpose(original).convert("RGB")
                clean.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
                dimensions = list(clean.size)
                buf = BytesIO()
                clean.save(buf, format="JPEG", quality=88, optimize=True)
                jpeg = buf.getvalue()
            with Image.open(BytesIO(jpeg)) as verify:
                if verify.info.get("exif") or verify.getexif().get(34853):
                    raise ValueError("web image retains EXIF/GPS metadata")
                verify.verify()
            if len(jpeg) < 6_500:
                raise ValueError("resulting web image too small")
            return jpeg, dimensions, url, sha256(data).hexdigest()
        except Exception as e:
            fail.append(str(e)[:140])
    raise RuntimeError("image bytes not deployable: " + "; ".join(fail)[-360:])

def candidates(spec: dict) -> list[tuple[dict, dict]]:
    name = spec["scientific_name"]
    found = []
    for code in ("cc-by", "cc-by-nc"):
        # Use both photo-license filtering and SPECIES-level observation acceptance.
        url = "https://api.inaturalist.org/v1/observations?" + urlencode({
            "taxon_name": name, "quality_grade": "research",
            "photo_license": code, "per_page": 30, "order_by": "created_at", "order": "desc"})
        payload = read_json(url)
        for observation in payload.get("results", []):
            taxon = observation.get("taxon") or {}
            if taxon.get("name") != name or observation.get("quality_grade") != "research":
                continue
            if not isinstance(observation.get("photos"), list):
                continue
            for p in observation["photos"]:
                if not isinstance(p, dict) or str(p.get("license_code") or "") not in {"cc-by", "cc-by-nc"}:
                    continue
                author = str(p.get("attribution") or "").strip()
                if not author or "CC BY" not in author.upper().replace("-", " "):
                    continue
                if not p.get("id") or not url_for_photo(p):
                    continue
                found.append((observation,p))
        if found:
            break  # prefer CC BY; don't automatically use NC if a good BY exists
    return found

def install(taxon: str, spec: dict) -> dict:
    sp = ROOT / spec["species_json"]
    doc = json.loads(sp.read_text(encoding="utf-8"))
    if doc.get("id") != taxon:
        raise RuntimeError("canonical taxon ID differs from intended exact species")
    if held_claim(taxon):
        raise RuntimeError("unexpired taxon/photo claim; do not overwrite another worker")
    if doc.get("project_inclusion", {}).get("target_zone_status") in {"HOLD","FAIL"}:
        raise RuntimeError("identity/science project HOLD or FAIL; preserve record")
    for existing in doc.get("images") or []:
        if str(existing.get("file") or "").startswith(spec["filename_prefix"]):
            raise RuntimeError("photo already installed or in progress; skip duplicate")
    possibilities = candidates(spec)
    if not possibilities:
        raise RuntimeError("no research-grade exact-name photo with individual CC BY/NC license and photographer attribution surfaced in live iNaturalist")
    failed = []
    for observation, photo in possibilities[:12]:
        pid = str(photo["id"])
        try:
            lic, lic_url = license_name(photo)
            raw, dims, direct_url, source_hash = photo_bytes(photo)
            dest_rel = spec["filename_prefix"] + "-" + pid + ".jpg"
            dest = sp.parent / dest_rel
            if dest.exists() or any(x.get("source_photo_id") == pid for x in doc.get("images", [])):
                failed.append("candidate " + pid + " would duplicate existing photo")
                continue
            dest.parent.mkdir(exist_ok=True)
            dest.write_bytes(raw)
            credit = str(photo["attribution"]).strip()
            gallery = {
                "file": dest_rel,
                "role": spec["role"],
                "caption": "Individually licensed, research-grade iNaturalist observation photograph of " + spec["scientific_name"] + ". Plant-part diagnostic anatomy needs a separate visual check before precise arrows or FINALIZED marking.",
                "creator": credit,
                "license": lic,
                "license_url": lic_url,
                "source_page": "https://www.inaturalist.org/photos/" + pid,
                "source_observation_page": "https://www.inaturalist.org/observations/" + str(observation["id"]),
                "source_photo_id": pid,
                "source_observation_id": str(observation["id"]),
                "source_taxon": spec["scientific_name"],
                "source_quality_grade": "research",
                "source_photo_license_code": photo.get("license_code"),
                "source_type": "iNaturalist individually licensed exact-taxon photo verified by current photo API",
                "downloaded_from": direct_url,
                "public_reuse": "yes, conditional on recorded CC attribution/NC terms and noncommercial education",
                "changes": "Downloaded iNaturalist photo, resized and reencoded to JPEG without EXIF/GPS; no annotations added.",
                "source_sha256": source_hash,
                "published_jpeg_sha256": sha256(raw).hexdigest(),
                "published_jpeg_dimensions": dims,
                "annotation_pending": True,
                "photo_organ_validation": "pending independent anatomical visual review",
            }
            # Append a new separately licensed real image; never edit old, unknown-rights media.
            doc.setdefault("images", []).append(gallery)
            sp.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            return {
                "taxon": taxon, "species_json": spec["species_json"],
                "physical_file": str(dest.relative_to(ROOT)), "relative_photo_path": dest_rel,
                "photo_id": pid, "observation_id": str(observation["id"]),
                "creator": credit, "license": lic, "license_url": lic_url,
                "photo_sha256": sha256(raw).hexdigest(), "image_bytes": len(raw),
                "dimensions": dims, "status": "COMMIT_REQUIRED_THEN_VERIFY_ON_MAIN",
            }
        except Exception as exc:
            failed.append("candidate " + pid + ": " + str(exc)[:140])
    raise RuntimeError("Tried " + str(min(len(possibilities), 12)) + " photo candidates; " + "; ".join(failed)[:420])

def main() -> None:
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "attempted_taxa": list(TARGETS),
        "installed": [], "held": [],
        "purpose": "Recover one exact-name research-grade, individually licensed public photo for each of Berberis swaseyi, Canna glauca and Stillingia texana.",
        "science_rule": "Preserve current county nativity decisions, particularly the PROVISIONAL status of Canna glauca; do not edit the existing restricted video-frame research galleries, photographer credits or license flags.",
        "publication": "GitHub canonical commit does not prove public Pages deployment; public-readiness worker handles controlled marker.",
    }
    for taxon, spec in TARGETS.items():
        try:
            report["installed"].append(install(taxon, spec))
        except Exception as e:
            report["held"].append({"taxon": taxon, "reason": str(e)[:540]})
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"installed": [{"species": r["taxon"], "photo_id": r["photo_id"], "license": r["license"]} for r in report["installed"]], "held": report["held"]}, indent=2))

if __name__ == "__main__":
    main()
