#!/usr/bin/env python3
"""Withhold two rights-restricted E. dentata study photos in the PUBLIC dist copy only.

Never change canonical source species.json or original research images.
Public gallery retains three credited CC BY-SA photographs and field photo overlays.
"""
import argparse
import json
from pathlib import Path

REL = Path("content/taxa/Euphorbiaceae/Euphorbia/euphorbia-dentata")
RESTRICTED = {
    "images/04-abaxial-hairs-private-study.jpg",
    "images/05-fruit-seeds-private-study.jpg",
}
EXPECTED_PUBLIC = {
    "images/01-flower-fruit.webp",
    "images/02-leaves.webp",
    "images/03-whole-plant.webp",
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--site-dir", required=True)
    args = parser.parse_args()
    site = Path(args.site_dir).resolve()
    assert site.name == "dist", "Only a staged public site is allowed"
    folder = site / REL
    card_path = folder / "species.json"
    assert card_path.is_file(), card_path
    j = json.loads(card_path.read_text(encoding="utf-8"))
    assert j["scientific_name"] == "Euphorbia dentata"
    assert j["project_inclusion"]["target_zone_status"] == "PASS"
    assert j["field_id_finalization"]["stage"] == "PASS_IN_PROGRESS"
    images = j["images"]
    assert len(images) == 5
    assert {x["file"] for x in images} == EXPECTED_PUBLIC | RESTRICTED
    retained = [x for x in images if x["file"] in EXPECTED_PUBLIC]
    excluded = [x for x in images if x["file"] in RESTRICTED]
    assert len(retained) == 3 and len(excluded) == 2
    assert all(x.get("license") == "CC BY-SA" and x.get("public_reuse") == "yes" for x in retained)
    assert all(x.get("public_reuse") == "review" and "copyrighted" in x.get("license", "").lower() for x in excluded)
    for x in retained:
        assert (folder / x["file"]).is_file(), x["file"]
    for x in excluded:
        target = folder / x["file"]
        assert target.is_file(), target
        target.unlink()
    j["images"] = retained
    j["curation_status"]["photo_metadata_count"] = 3
    j["curation_status"]["photo_files_present"] = 3
    j["curation_status"]["public_gallery_restricted_study_photos_withheld"] = 2
    j["learner_visual_status"]["image_count"] = 3
    j["learner_visual_status"]["public_copy_rights_guard"] = "3 reusable photos; 2 restricted images excluded only from public deployment"
    j["public_restricted_photo_references"] = [{
        "creator":x["creator"],
        "license":x["license"],
        "source_page":x["source_page"],
        "reason":"Original-site reference only, not displayed on the public website"
    } for x in excluded]
    assert len(j["visual_comparison"]["items"]) == 4
    assert sum(len(x.get("markers",[])) for x in j["visual_comparison"]["items"]) == 8
    assert all((site / x["image_url"]).is_file() for x in j["visual_comparison"]["items"])
    card_path.write_text(json.dumps(j, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    for name in RESTRICTED:
        assert not (folder / name).exists()
    print("PASS: Staged dentata public gallery has 3 CC BY-SA files; 2 restricted study photos removed from dist only. Canonical originals unmodified.")

if __name__ == "__main__":
    main()
