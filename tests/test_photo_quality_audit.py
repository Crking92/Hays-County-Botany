"""Tests for photo_quality_audit; run with python -m unittest discover -s tests."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from datetime import datetime, timezone

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/photo_quality_audit.py"
SPEC = importlib.util.spec_from_file_location("photo_quality_audit", SCRIPT)
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


class PhotoAuditTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "data").mkdir()
        (self.root / "workflow").mkdir()
        self.entries = [
            ("helianthus-annuus", "Asteraceae", "Helianthus",
             [{"file": "images/leaf.jpg", "role": "diagnostic broad leaf, basal veins and petiole",
               "creator": "A. Test", "license": "cc-by-2.0", "source_page": "https://example.org/source",
               "public_reuse": "yes with license terms", "visual_role_reviewed": "2026-10-08"},
              {"file": "https://example.org/phyllary.jpg", "role": "diagnostic mature phyllary macro",
               "creator": "B. Test", "license": "cc-by-sa", "source_page": "https://example.org/view",
               "external_reference": True, "public_reuse": "yes with terms"}]),
            ("asclepias-sample", "Apocynaceae", "Asclepias", []),
            ("quercus-sample", "Fagaceae", "Quercus",
             [{"file": "images/missing.jpg", "role": "curated taxon reference",
               "creator": "C. Test", "license": "cc-by-nc", "source_page": "https://example.org/2",
               "public_reuse": "review"}]),
        ]
        species = []
        for id, family, genus, images in self.entries:
            path = f"content/taxa/{family}/{genus}/{id}/species.json"
            folder = self.root / Path(path).parent
            folder.mkdir(parents=True, exist_ok=True)
            (folder / "species.json").write_text(json.dumps({
                "id": id, "family": family, "genus": genus, "scientific_name": genus + " example",
                "images": images,
            }))
            if id == "helianthus-annuus":
                (folder / "images").mkdir()
                (folder / "images/leaf.jpg").write_bytes(b"fake image bytes")
            species.append({"id": id, "path": path})
        (self.root / "data/manifest.json").write_text(json.dumps({"species": species}))
        self.original_data = (self.root / "data/manifest.json").read_bytes()

    def tearDown(self):
        self.temp.cleanup()

    def test_role_and_license_preservation(self):
        entry = self.entries[0]
        path = f"content/taxa/{entry[1]}/{entry[2]}/{entry[0]}/species.json"
        sp = audit.load(self.root / path)
        row = audit.audit({"id": entry[0], "path": path}, sp, self.root, {"claims": []},
                          datetime.now(timezone.utc))
        self.assertIn("leaf", row["role_metadata_coverage"])
        self.assertIn("phyllary", row["role_metadata_coverage"])
        self.assertIn("flower", row["missing_role_metadata"])
        self.assertEqual(row["broken_local_references"], 0)
        self.assertEqual(row["external_references"], 1)
        self.assertEqual(row["best_canonical_image_index"], 0)
        self.assertEqual(sp["images"][0]["creator"], "A. Test")

    def test_plural_botanical_terms_are_detected(self):
        checks = {
            "broad phyllaries beneath flowering heads": ["phyllary", "flower"],
            "mature acorns in cups": ["fruit"],
            "dense florets and corollas": ["flower"],
            "hairy stems and buds": ["stem"],
            "milkweed hoods and horns": ["corona"],
            "grasses with short ligules": ["ligule"],
        }
        for role, expected in checks.items():
            detected = audit.image_roles({"role": role})
            for item in expected:
                self.assertIn(item, detected, role)

    def test_avoid_claimed_species_and_honor_expiry(self):
        claim = {"claims": [{
            "status": "active", "lane": "photo-fast-fill",
            "claim_id": "photo-installer-working",
            "taxa": ["asclepias-sample"],
            "expires_at": "2099-01-01T00:00:00Z",
        }]}
        (self.root / "workflow/work-claims.json").write_text(json.dumps(claim))
        result = audit.write_reports(self.root, self.root / "out", 25, 0)
        self.assertEqual(result["species_audited"], 3)
        self.assertEqual(result["with_no_gallery_photos"], 1)
        self.assertEqual(result["blocked_by_current_photo_claim"], 1)
        queue = audit.load(self.root / "out/queue.json")
        self.assertNotIn("asclepias-sample", [x["id"] for x in queue["selected"]])
        self.assertEqual((self.root / "data/manifest.json").read_bytes(), self.original_data)
        self.assertTrue((self.root / "out/queue.md").exists())

    def test_missing_local_media_flag_and_role_no_guess(self):
        result = audit.write_reports(self.root, self.root / "audit", 25, 0)
        by_id = {r["id"]: r for r in result["rows"]}
        self.assertEqual(by_id["quercus-sample"]["broken_local_references"], 1)
        self.assertEqual(by_id["quercus-sample"]["photos_with_noncommercial_or_review_reuse"], 1)
        self.assertFalse(by_id["quercus-sample"]["role_metadata_coverage"])
        self.assertGreater(by_id["asclepias-sample"]["priority_score"], by_id["helianthus-annuus"]["priority_score"])

    def test_reject_incomplete_manifest(self):
        manifest = audit.load(self.root / "data/manifest.json")
        manifest["species"].append({"id": "missing", "path": "content/taxa/nothing.json"})
        (self.root / "data/manifest.json").write_text(json.dumps(manifest))
        with self.assertRaises(RuntimeError):
            audit.write_reports(self.root, self.root / "out", 25, 0)

if __name__ == "__main__":
    unittest.main()
