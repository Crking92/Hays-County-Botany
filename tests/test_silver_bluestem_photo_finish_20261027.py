"""Silver bluestem real-source photo/arrow/publication guardrails."""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CARD=ROOT/"content/taxa/Poaceae/Bothriochloa/bothriochloa-torreyana/species.json"

class SilverPhotoFinish(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s=json.loads(CARD.read_text(encoding="utf-8"))
        cls.panels=cls.s["visual_comparison"]["items"]

    def test_archive_and_photo_rights(self):
        s=self.s
        self.assertEqual(s["id"],"bothriochloa-torreyana")
        self.assertFalse(s["native_target_zone_calculated"])
        self.assertEqual(len(s["images"]),8)
        self.assertEqual(len(self.panels),8)
        self.assertEqual(s["curation_status"]["visual_finish"][:22],"FIELD_READY_PHOTO_GAPS")
        for i in (5,6,7):
            x=self.panels[i]
            self.assertTrue(x["image_url"].startswith("content/taxa/Poaceae/Bothriochloa/bothriochloa-torreyana/images/"))
            self.assertTrue((ROOT/x["image_url"]).is_file())
            self.assertTrue(x["source_page"] and x["creator"] and x["license"])
            self.assertEqual(x["scientific_name"],s["scientific_name"])
        self.assertEqual(len([x for x in s["images"] if "20261027" in x["file"] or "smallcurio-austin" in x["file"]]),3)
        self.assertEqual(len([x for x in s["images"] if x.get("public_reuse") in {"no","NO — photographer authorization required"}]),2)

    def test_annotated_only_visible_macro_and_clump(self):
        liz=self.panels[5]
        maxp=self.panels[6]
        self.assertEqual(liz["creator"],"Liz Makings")
        self.assertEqual(maxp["creator"],"Max Licher")
        self.assertEqual(len(liz["markers"]),3)
        self.assertEqual(len(maxp["markers"]),2)
        for p in (liz,maxp):
            for marker in p["markers"]:
                self.assertTrue(marker["label"])
                self.assertTrue(all(0<=marker[k]<=100 for k in ("label_x","label_y","target_x","target_y")))
        self.assertEqual(sum(len(x.get("markers",[])) for x in self.panels),7)
        self.assertIn("NOT",liz["caption"])
        self.assertIn("NOT",maxp["caption"])

    def test_beginner_four_steps_and_source_only_research(self):
        s=self.s
        beginner=s["beginner_learning_path"]
        self.assertEqual(len(beginner["steps"]),4)
        self.assertTrue(beginner["safety_note"])
        self.assertTrue((CARD.parent/beginner["hero_photo_file"]).is_file())
        self.assertEqual([step["panel_index"] for step in beginner["steps"]],[0,6,5,4])
        self.assertEqual(len(s["field_photo_quickcheck"]["steps"]),5)
        self.assertEqual(len(s["silver_research_only_photos_20261027"]["public_study_sources"]),3)
        protected=s["silver_research_only_photos_20261027"]["public_study_sources"]
        for rec in protected:
            self.assertIn("©",rec["copyright"])
            self.assertIn("Link",rec["release"])
            self.assertTrue(rec["direct_original"].startswith("https://www.missouriplants.com/images/"))
            for p in self.panels:
                self.assertNotEqual(p.get("image_url"),rec["direct_original"])
            for im in s["images"]:
                self.assertFalse(im["file"].endswith(rec["direct_original"].split("/")[-1]))
        js=(ROOT/"assets/js/app.js").read_text(encoding="utf-8")
        self.assertIn("sp.silver_research_only_photos_20261027",js)
        self.assertIn("www\\.missouriplants\\.com",js)
        self.assertIn('studyDrawer("Silver bluestem — source-only ligule and node photos"',js)

if __name__=="__main__":
    unittest.main()
