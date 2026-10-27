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
        self.assertGreaterEqual(len(s["images"]),16)
        self.assertGreaterEqual(len(self.panels),16)
        self.assertEqual(s["curation_status"]["visual_finish"][:22],"FIELD_READY_PHOTO_GAPS")
        for i in (5,6,7,8,9,10,11,12,13,14,15):
            x=self.panels[i]
            self.assertTrue(x["image_url"].startswith("content/taxa/Poaceae/Bothriochloa/bothriochloa-torreyana/images/"))
            self.assertTrue((ROOT/x["image_url"]).is_file())
            self.assertTrue(x["source_page"] and x["creator"] and x["license"])
            self.assertEqual(x["scientific_name"],s["scientific_name"])
        self.assertGreaterEqual(len([x for x in s["images"] if "20261027" in x["file"] or "smallcurio-austin" in x["file"]]),7)
        self.assertEqual({p.get("source_photo_id") for p in s["images"] if p.get("source_photo_id") in (730629825,749323175,102682516,292594065)}, {730629825,749323175,102682516,292594065})
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
        self.assertGreaterEqual(sum(len(x.get("markers",[])) for x in self.panels),21)
        self.assertIn("NOT",liz["caption"])
        self.assertIn("NOT",maxp["caption"])


    def test_new_Texas_anatomy_verified_but_unfinished(self):
        s=self.s
        self.assertEqual(s["silver_six_role_photo_score_20261027"]["total"],4.5)
        self.assertEqual(s["silver_six_role_photo_score_20261027"]["pct"],75.0)
        self.assertEqual(s["silver_six_role_photo_score_20261027"]["roles"][2]["score"],0.5)
        self.assertIn("NOT",s["silver_six_role_photo_score_20261027"]["roles"][2]["reason"])
        self.assertEqual(s["texas_silver_anatomy_20261027"]["source_photo_ids"],[730629825,749323175])
        self.assertEqual(s["texas_silver_anatomy_20261027"]["new_verified_arrows"],4)
        self.assertEqual(s["field_photo_quickcheck"]["featured_panel_indices"][:4],[0,16,17,18])
        for i,photo_id in [(8,730629825),(9,749323175)]:
            p=self.panels[i]
            self.assertEqual(p["source_photo_id"],photo_id)
            self.assertIn("CC BY-NC",p["license"])
            self.assertEqual(p["scientific_name"],"Bothriochloa torreyana")
            self.assertEqual(len(p["markers"]),2)
            self.assertTrue((ROOT/p["image_url"]).is_file())
            self.assertTrue("not" in p["caption"].lower() or "cannot" in p["caption"].lower())
            for marker in p["markers"]:
                self.assertTrue(all(0<=marker[k]<=100 for k in ("label_x","label_y","target_x","target_y")))
        self.assertFalse(s["native_target_zone_calculated"])

    def test_actual_Texas_true_nodes_without_false_mm_claim(self):
        s=self.s
        self.assertEqual(s["silver_texas_true_culm_nodes_20261027"]["source_photo_ids"],[102682516,292594065])
        self.assertFalse(s["silver_texas_true_culm_nodes_20261027"]["calibrated_mm_scale_visible"])
        self.assertFalse(s["silver_texas_true_culm_nodes_20261027"]["true_free_ligule_visible"])
        self.assertEqual(s["silver_six_role_photo_score_20261027"]["roles"][3]["score"],0.5)
        for i,photo_id in ((10,102682516),(11,292594065)):
            p=self.panels[i]
            self.assertEqual(p["source_photo_id"],photo_id)
            self.assertEqual(p["scientific_name"],"Bothriochloa torreyana")
            self.assertEqual(len(p["markers"]),1)
            self.assertTrue((ROOT/p["image_url"]).is_file())
            self.assertIn("no",p["caption"].lower())
            for mark in p["markers"]:
                self.assertTrue(all(0<=mark[k]<=100 for k in ("label_x","label_y","target_x","target_y")))
        self.assertFalse(s["native_target_zone_calculated"])

    def test_source_vouchered_Texas_rooted_plant_and_75_percent(self):
        s=self.s
        root=s["silver_preserved_rooted_texas_vouchers_20261027"]
        self.assertEqual(root["new_verified_herbarium_sheet_keys"],[3921136348,6158969001])
        self.assertEqual(root["new_public_licensed_real_rooted_plant_photos"],2)
        self.assertTrue(root["real_roots_visible"])
        self.assertEqual(root["rhizome_presence_absence_from_sheet"],"NOT PROVEN")
        self.assertEqual(s["silver_six_role_photo_score_20261027"]["roles"][0]["score"],1)
        self.assertEqual(s["silver_six_role_photo_score_20261027"]["total"],4.5)
        self.assertEqual(s["silver_six_role_photo_score_20261027"]["pct"],75)
        for i,key in ((12,3921136348),(13,6158969001)):
            panel=self.panels[i]
            self.assertEqual(panel["source_page"],"https://www.gbif.org/occurrence/"+str(key))
            self.assertEqual(panel["license"],"CC BY 4.0")
            self.assertEqual(panel["creator"],"The University of Texas at Austin, TEX Herbarium")
            self.assertTrue((ROOT/panel["image_url"]).is_file())
            self.assertEqual(len(panel["markers"]),2)
            self.assertIn("roots",panel["caption"].lower())
            for marker in panel["markers"]:
                self.assertTrue(all(0<=marker[k]<=100 for k in ("label_x","label_y","target_x","target_y")))
        self.assertFalse(s["native_target_zone_calculated"])

    def test_new_public_domain_rooted_vouchers_and_rights_hold(self):
        s=self.s
        source=s["silver_public_domain_rooted_vouchers_20261027"]
        self.assertTrue(source["real_attached_exposed_roots"])
        self.assertTrue(source["ut_sheets_rights_conflict_hold"])
        self.assertEqual(source["archived_gbif_ids"],[2242356292,4976689107])
        self.assertEqual(s["silver_six_role_photo_score_20261027"]["pct"],75)
        self.assertEqual(s["silver_six_role_photo_score_20261027"]["roles"][0]["score"],1)
        self.assertEqual(s["silver_six_role_photo_score_20261027"]["roles"][2]["score"],0.5)
        self.assertEqual(s["silver_six_role_photo_score_20261027"]["roles"][4]["score"],0.5)
        for key in (2242356292,4976689107):
            panel=next(p for p in self.panels if p.get("source_gbif_id")==key)
            rec=next(p for p in s["images"] if p.get("source_gbif_id")==key)
            self.assertIn("CC0",panel["license"])
            self.assertIn("CC0",rec["license"])
            self.assertEqual(len(panel["markers"]),2)
            self.assertIn("root",panel["caption"].lower())
            self.assertTrue((ROOT/panel["image_url"]).is_file())
            self.assertEqual(panel["creator"],rec["creator"])
            self.assertTrue(panel["source_page"].startswith("https://www.gbif.org/occurrence/"))
            for marker in panel["markers"]:
                self.assertTrue(all(0<=marker[t]<=100 for t in ("label_x","label_y","target_x","target_y")))
        self.assertFalse(s["native_target_zone_calculated"])

    def test_beginner_four_steps_and_source_only_research(self):
        s=self.s
        beginner=s["beginner_learning_path"]
        self.assertEqual(len(beginner["steps"]),7)
        self.assertTrue(beginner["safety_note"])
        self.assertTrue((CARD.parent/beginner["hero_photo_file"]).is_file())
        self.assertEqual([step["panel_index"] for step in beginner["steps"]],[0,6,14,16,17,5,4])
        self.assertEqual(len(s["field_photo_quickcheck"]["steps"]),5)
        self.assertTrue(s["silver_milam_beginner_path_20261027"]["seven_photo_steps"])
        self.assertEqual(s["silver_milam_ccby_field_anatomy_20261027"]["photo_ids"],[648930178,648929751,648930211])
        self.assertEqual([self.panels[i]["source_photo_id"] for i in (16,17,18)],[648930178,648929751,648930211])
        self.assertTrue(all((ROOT/self.panels[i]["image_url"]).is_file() for i in (16,17,18)))
        self.assertEqual([self.panels[i]["markers"][0]["target_y"] for i in (16,17,18)],[32,47,48])
        self.assertEqual(len(s["silver_research_only_photos_20261027"]["public_study_sources"]),4)
        protected=s["silver_research_only_photos_20261027"]["public_study_sources"]
        for rec in protected:
            self.assertTrue("©" in rec["copyright"] or "Crown copyright" in rec["copyright"])
            self.assertIn("Link",rec["release"])
            self.assertTrue(rec["direct_original"].startswith(("https://www.missouriplants.com/images/","https://inspection.canada.ca/")))
            for p in self.panels:
                self.assertNotEqual(p.get("image_url"),rec["direct_original"])
            for im in s["images"]:
                self.assertFalse(im["file"].endswith(rec["direct_original"].split("/")[-1]))
        js=(ROOT/"assets/js/app.js").read_text(encoding="utf-8")
        self.assertIn("sp.silver_research_only_photos_20261027",js)
        self.assertIn("www\\.missouriplants\\.com",js)
        self.assertIn("inspection\\.canada\\.ca",js)
        self.assertIn('studyDrawer("Silver bluestem — source-only ligule and node photos"',js)

if __name__=="__main__":
    unittest.main()
