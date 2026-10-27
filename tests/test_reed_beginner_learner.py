"""Protect the photo-first Arundo/Phragmites lessons against broken links,
misleading transferred annotations, and accidental restricted-photo admission.
Run: python -m unittest discover -s tests -p 'test_reed_beginner_learner.py'
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATHS = {
    "arundo-donax": ROOT / "content/taxa/Poaceae/Arundo/arundo-donax/species.json",
    "phragmites-australis": ROOT / "content/taxa/Poaceae/Phragmites/phragmites-australis/species.json",
}

class BeginnerReedLessonTests(unittest.TestCase):
    def test_photo_first_lesson_integrity(self):
        for species_id, path in PATHS.items():
            with self.subTest(species=species_id):
                doc = json.loads(path.read_text(encoding="utf-8"))
                lesson = doc["beginner_learning_path"]
                self.assertEqual(doc["id"], species_id)
                self.assertEqual(len(lesson["steps"]), 4)
                self.assertEqual(lesson["hero_photo_file"], doc["images"][0]["file"])
                self.assertTrue((path.parent / lesson["hero_photo_file"]).is_file())
                self.assertTrue(lesson["safety_note"])
                panels = doc["visual_comparison"]["items"]
                selected_indices = []
                for step in lesson["steps"]:
                    index = step["panel_index"]
                    self.assertIsInstance(index, int)
                    self.assertTrue(0 <= index < len(panels))
                    selected_indices.append(index)
                    self.assertTrue(step.get("title") and step.get("look_for") and step.get("why_it_matters"))
                    panel = panels[index]
                    src = panel["image_url"]
                    self.assertTrue(src.startswith("content/"), "Starter must be an installed, rights-reviewed image")
                    self.assertTrue((ROOT / src).is_file(), src)
                    self.assertTrue(panel.get("creator") and panel.get("license") and panel.get("source_page"))
                    name = panel.get("scientific_name", "")
                    self.assertTrue(name == doc["scientific_name"] or
                                    name.startswith(doc["scientific_name"] + " subsp. "))
                    for marker in panel.get("markers", []):
                        self.assertTrue(all(0 <= float(marker[k]) <= 100 for k in
                                ["label_x", "label_y", "target_x", "target_y"]))
                self.assertEqual(len(set(selected_indices)), 4)
                self.assertEqual(len(doc["field_photo_quickcheck"]["steps"]), 5)
                self.assertTrue(doc["field_photo_quickcheck"].get("featured_photo_indices"))
                for item in doc["images"]:
                    self.assertNotIn("Phau ", item["file"])
                    self.assertNotIn("Neil Reese", item.get("creator", ""))
                    self.assertNotIn("SDSU", item.get("creator", ""))

    def test_phragmites_safety_and_source_ids(self):
        d=json.loads(PATHS["phragmites-australis"].read_text(encoding="utf-8"))
        beginner=d["beginner_learning_path"]
        text=" ".join([beginner["safety_note"], beginner["intro"], d["look_here_first"],
                       *[row["why_it_matters"] for row in beginner["steps"]]]).lower()
        for term in ["native", "introduced", "gulf", "lineage"]:
            self.assertIn(term,text)
        self.assertGreaterEqual(len(d["images"]),17)
        self.assertGreaterEqual(len(d["visual_comparison"]["items"]),21)
        self.assertGreaterEqual(d["curation_status"]["visible_gross_structure_arrows"],23)

    def test_arundo_safety_and_counts(self):
        d=json.loads(PATHS["arundo-donax"].read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(d["images"]),7)
        self.assertGreaterEqual(len(d["visual_comparison"]["items"]),10)
        self.assertGreaterEqual(d["curation_status"]["verified_visible_structure_arrows"],5)
        beginner=d["beginner_learning_path"]
        self.assertIn("Phragmites",beginner["steps"][3]["why_it_matters"])
        self.assertIn("tentative",beginner["safety_note"].lower())

if __name__ == "__main__":
    unittest.main()
