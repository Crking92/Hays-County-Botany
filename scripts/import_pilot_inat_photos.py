#!/usr/bin/env python3
"""Download exact iNaturalist pilot photos into a *review-only* staging directory.

No learner cards, manifest, READY markers, or public image approvals are changed.
"""
import hashlib
import io
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "workflow/photo-first-install-pilot-20261015-001.json"
OUT = ROOT / "research-drafts/photo-imports/pilot-20261015"
OUT.mkdir(parents=True, exist_ok=True)
UA = "HaysCountyBotanyResearchPhotoImporter/1.0 (photo review; iNaturalist API)"
ALLOWED_LICENSES = {"cc-by", "cc-by-nc", "cc-by-sa", "cc-by-nc-sa", "cc0", "pd"}
MAX_BYTES = 12_000_000

def fetch(url):
    with urlopen(Request(url, headers={"User-Agent": UA}), timeout=25) as r:
        data = r.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("image exceeds 12MB safety limit")
    return data

def api(url):
    return json.loads(fetch(url).decode("utf-8"))

report = {"source": str(SOURCE.relative_to(ROOT)), "records": [],
          "warning": "STAGED PHOTO CANDIDATES ONLY. Visually review taxon/diagnostic content before learner installation. No READY marker."}
for plant in json.loads(SOURCE.read_text(encoding="utf-8"))["records"]:
    result = {"scientific_name": plant["scientific_name"], "slug": plant["slug"], "photos": []}
    for candidate in plant["user_photo_candidates"]:
        photo_id = str(candidate["photo_id"])
        observation_id = str(candidate["observation_id"])
        item = {"photo_id": photo_id, "observation_id": observation_id, "status": "blocked"}
        try:
            obs_data = api(f"https://api.inaturalist.org/v1/observations/{observation_id}")
            obs = obs_data["results"][0]
            photo = next((p for p in obs.get("photos", []) if str(p["id"]) == photo_id), None)
            if photo is None:
                raise ValueError("photo not present on expected observation")
            observed_name = (obs.get("taxon") or {}).get("name")
            if observed_name != plant["scientific_name"]:
                raise ValueError(f"observation taxon mismatch: {observed_name}")
            lic = (photo.get("license_code") or "").lower()
            item["license_code"] = lic or "unspecified"
            item["attribution"] = photo.get("attribution")
            item["observation_url"] = f"https://www.inaturalist.org/observations/{observation_id}"
            item["photo_url"] = f"https://www.inaturalist.org/photos/{photo_id}"
            item["observed_taxon"] = observed_name
            if lic not in ALLOWED_LICENSES:
                raise ValueError(f"photo license not explicitly reusable: {lic or 'none'}")
            url = photo.get("url") or ""
            if not url.startswith("https://"):
                raise ValueError("missing HTTPS photo URL")
            url = url.replace("/square.", "/large.").replace("/thumb.", "/large.").replace("/small.", "/large.").replace("/medium.", "/large.")
            raw = fetch(url)
            image = Image.open(io.BytesIO(raw))
            image.verify()
            image = Image.open(io.BytesIO(raw))
            if image.width < 300 or image.height < 300:
                raise ValueError("image below 300px")
            image = image.convert("RGB")
            dest = OUT / plant["slug"] / f"inat-{photo_id}.jpg"
            dest.parent.mkdir(parents=True, exist_ok=True)
            image.save(dest, format="JPEG", quality=88, optimize=True)
            item.update(status="downloaded_pending_visual_review", file=str(dest.relative_to(ROOT)),
                        sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),
                        width=image.width, height=image.height, image_source=url)
        except (Exception) as exc:
            item["blocker"] = str(exc)[:300]
        result["photos"].append(item)
    report["records"].append(result)
(OUT / "import-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"plants": len(report["records"]), "downloaded": sum(p["status"].startswith("downloaded") for r in report["records"] for p in r["photos"]), "blocked": sum(p["status"]=="blocked" for r in report["records"] for p in r["photos"])}))
