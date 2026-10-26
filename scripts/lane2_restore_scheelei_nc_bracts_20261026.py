#!/usr/bin/env python3
"""One-shot restoration of EXACT Kyla Miller Setaria scheelei licensed photograph.
No downloads or new photo bytes; verify live iNaturalist photo-level license and stored
JPEG, preserve previous rights-hold statements as historical evidence, fail closed.
"""
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "content/taxa/Poaceae/Setaria/setaria-scheelei/species.json"
REPORT = ROOT / "reports/lane2-scheelei-kyla-nc-gallery-reconciliation-20261026.json"
PHOTO_ID = 237392332
SOURCE = f"https://www.inaturalist.org/photos/{PHOTO_ID}"
EXPECTED_REL = "content/taxa/Poaceae/Setaria/setaria-scheelei/images/inat-237392332.jpg"
USER_AGENT = {"User-Agent": "HaysCountyBotanyVisualLearner/1.0 (photo-license verification; github public learner)"}
ALLOWED = {"cc0", "cc-by", "cc-by-sa", "cc-by-nc", "cc-by-nc-sa"}

def get_json(url):
    with urlopen(Request(url, headers=USER_AGENT), timeout=45) as response:
        return json.load(response)

def verify_photo():
    failures = []
    # Observation source already linked in public photo catalog for user 'kylamill'.
    for obs_id in (138856189,):
        try:
            data = get_json(f"https://api.inaturalist.org/v1/observations/{obs_id}")
            for obs in data.get("results", []):
                if obs.get("taxon", {}).get("name") != "Setaria scheelei":
                    failures.append(f"observation {obs_id} species now {obs.get('taxon', {}).get('name')}")
                    continue
                if obs.get("user", {}).get("login", "").lower() != "kylamill":
                    failures.append(f"observation {obs_id} user != kylamill")
                    continue
                for photo in obs.get("photos", []):
                    if photo.get("id") != PHOTO_ID:
                        continue
                    code = (photo.get("license_code") or "").lower()
                    if code not in ALLOWED:
                        raise RuntimeError(f"Photo {PHOTO_ID} is NOT safely reusable: {code}")
                    if code != "cc-by-nc":
                        raise RuntimeError(f"Photo license changed to {code}; manual terms review required")
                    return {"photo_id": PHOTO_ID, "observation_id": obs_id,
                            "obs_taxon": obs["taxon"]["name"], "user": obs["user"]["login"],
                            "photo_license_code": code, "attribution": photo.get("attribution"),
                            "source": SOURCE}
            failures.append(f"observation {obs_id} lacked exact licensed target photo")
        except Exception as exc:
            failures.append(f"{obs_id}: {exc}")
    # Fall back to photo-specific API when the observation has moved/changed.
    try:
        data = get_json(f"https://api.inaturalist.org/v1/photos/{PHOTO_ID}")
        rows = data.get("results", [])
        for photo in rows:
            if photo.get("id") != PHOTO_ID:
                continue
            # Do NOT infer a taxon from a photo endpoint; needs intact source observation.
            failures.append("Photo endpoint available, but no exact-species observation confirmed")
    except Exception as exc:
        failures.append("photo endpoint: " + str(exc))
    raise RuntimeError("FAIL CLOSED: live exact-photo rights/taxon unverified: " + "; ".join(failures))

def main():
    evidence = verify_photo()
    photo = ROOT / EXPECTED_REL
    if not photo.is_file():
        raise RuntimeError(f"Expected exact archived JPEG absent: {photo}")
    with Image.open(photo) as image:
        if image.format != "JPEG" or min(image.size) < 350:
            raise RuntimeError("JPEG missing/corrupt/too small")
        pixels = list(image.size)
    card = json.loads(CARD.read_text())
    if card.get("scientific_name") != "Setaria scheelei":
        raise RuntimeError("Wrong canonical species")
    gallery = card["visual_comparison"]
    held = gallery.get("rights_held_comparison_items", [])
    matching = [p for p in held if p.get("source_page") == SOURCE and p.get("image_url") == EXPECTED_REL]
    if len(matching) != 1:
        if any(p.get("image_url") == EXPECTED_REL for p in gallery["items"]):
            print("ALREADY_RESTORED: no changes")
            return
        raise RuntimeError("Expected single rights-held panel not found")
    panel = copy.deepcopy(matching[0])
    if "Kyla Miller" not in panel.get("creator", "") or "CC BY-NC" not in panel.get("license", ""):
        raise RuntimeError("Photographer/license metadata mismatch")
    if len(panel.get("markers", [])) != 3:
        raise RuntimeError("Expected three original pixel-reviewed annotation markers")
    entry = next((i for i in card["images"] if i.get("file") == "images/inat-237392332.jpg"), None)
    if not entry or "Kyla Miller" not in entry.get("creator", ""):
        raise RuntimeError("Original photo rights metadata changed")
    panel["historic_public_site_hold"] = panel.pop("public_site_hold", None)
    panel["public_reuse"] = "yes — conditional CC BY-NC use on genuinely noncommercial educational Pages only"
    panel["license_url"] = "https://creativecommons.org/licenses/by-nc/4.0/"
    panel["photo_status"] = panel.get("photo_status", "") + " Original individually cc-by-nc photo license live-rechecked before restoration; intact source JPEG and original three validated gross arrows preserved. NOT a true ligule/root/attached bristle measurement."
    panel["rights_review"] = {
        "date_utc": datetime.now(timezone.utc).isoformat(),
        "photo_id": PHOTO_ID,
        "verified_observation_id": evidence["observation_id"],
        "license": "CC BY-NC 4.0",
        "limitation": "Use only on confirmed noncommercial standalone educational website; maintain visible license link and photographer credit",
        "site_policy": "workflow/PUBLIC_PHOTO_REUSE_POLICY_20261019.md (October 20 update)",
        "no_derivatives": False,
        "physical_jpeg_sha256": hashlib.sha256(photo.read_bytes()).hexdigest(),
        "physical_jpeg_dimensions": pixels
    }
    gallery["items"].insert(1, panel)
    gallery["rights_held_comparison_items"] = [p for p in held if p is not matching[0]]
    gallery["subtitle"] = (
        "Three locally archived exact-species photographs, including Kyla Miller's individually verified "
        "CC BY-NC original with its three gross-form arrows, conditionally reusable only on this "
        "stand-alone noncommercial educational website; plus three distinct-species look-alikes. "
        "Inner ligule, connected rhizomes and measured bristle-spikelet junction still missing."
    )
    entry["historical_public_reuse"] = entry.get("public_reuse")
    entry["historical_publication_hold"] = entry.get("publication_hold")
    entry["public_reuse"] = "yes — conditional on noncommercial public educational website and CC BY-NC compliance"
    entry["publication_hold"] = None
    entry["license_url"] = panel["license_url"]
    entry["public_site_note"] = "CC BY-NC original license, not a public domain or commercial-use image; retain creator/source and recheck if website monetizes"
    card["curation_status"]["lane2_scheelei_nc_license_reconciliation_20261026"] = {
        "stage": "FIELD_READY_PHOTO_GAPS",
        "source_checked": True, "archived_same_species_jpegs": 3,
        "same_species_gallery_panels": 3, "lookalike_panels": 3,
        "restored_panels": 1, "original_arrows_preserved": 3,
        "new_photo_bytes": 0, "new_anatomy_claims": 0,
        "still_missing": ["attached rooted/rhizomatous plant", "true inner ligule with mm scale", "bristle-spikelet attachment with mm scale"],
        "site_deployment": "Unverified until controlled rights-filtered Pages publication succeeds"
    }
    card["photo_note"] += "\n2026-10-26: restored already archived Kyla Miller CC BY-NC photo to the ordinary noncommercial educational teaching gallery after live exact-photo license recheck; original three verified gross markers, original license metadata and historic rights hold retained; no new photo or fine anatomy inferred."
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({"type":"NC rights reclamation, no new media download", "verification": evidence,
                                   "photo_path": EXPECTED_REL, "photo_sha256": panel["rights_review"]["physical_jpeg_sha256"],
                                   "photo_dimensions":pixels, "new_photo_bytes":0, "restored_ordinary_gallery_panels":1,
                                   "original_markers_preserved":3, "status":"FIELD_READY_PHOTO_GAPS",
                                   "publication_check":"pending", "rights":"CC BY-NC 4.0 strictly noncommercial and credited",
                                   "historical_hold_preserved":True},indent=2)+"\n")
    CARD.write_text(json.dumps(card,indent=2,ensure_ascii=False)+"\n")
    print("RESTORED source verified", evidence, "JPEG", pixels, "remaining FIELD_READY_PHOTO_GAPS")

if __name__ == "__main__":
    main()
