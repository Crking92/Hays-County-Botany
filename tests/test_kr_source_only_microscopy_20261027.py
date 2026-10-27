"""Guard against treating copyrighted North Hays DigFlora photos as publishable.
Supports the 2026-10-27 KR anatomy link-only research feature.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPECIES=ROOT/"content/taxa/Poaceae/Bothriochloa/bothriochloa-ischaemum/species.json"

class KRSourceOnlyMicroscopy(unittest.TestCase):
    def test_exact_local_research_with_rights_holds(self):
        s=json.loads(SPECIES.read_text(encoding="utf-8"))
        l=s["kr_final_anatomy_photo_review_20261027"]
        self.assertTrue(l["source_link_only"])
        self.assertEqual(len(l["public_study_sources"]),4)
        self.assertEqual(s["id"],"bothriochloa-ischaemum")
        self.assertGreaterEqual(len(s["images"]),12)
        self.assertGreaterEqual(len(s["visual_comparison"]["items"]),25)
        self.assertIn("FIELD_READY_PHOTO_GAPS",s["curation_status"]["visual_finish"])
        self.assertIn("HOLD",l["status"])
        hays=[p for p in l["public_study_sources"] if p["photographer"]=="Bob Harms"]
        self.assertEqual(len(hays),3)
        for record in hays:
            self.assertTrue(record["direct_original"].startswith("https://w3.biosci.utexas.edu/prc/DigFlora/KR/"))
            self.assertIn("permission",record["release"].lower())
        forbidden=("BOISS-LX-21Jul-A.JPG","BOISS-papbashairs.JPG","BOISS-2spksegs-23Jul-A.JPG")
        for p in s["visual_comparison"]["items"]:
            image=p.get("image_url","")
            self.assertFalse(any(x in image for x in forbidden),
                             "Rights-held DigFlora JPEG must never become a displayed image")
        for p in s["images"]:
            self.assertFalse(any(x in p.get("file","") for x in forbidden),
                             "Rights-held DigFlora original must not enter physical archive")

    def test_real_az_crown_and_paired_spikelet_arrows(self):
        s=json.loads(SPECIES.read_text(encoding="utf-8"))
        panels=s["visual_comparison"]["items"]
        pair=next(p for p in panels if p.get("image_url","").endswith("kr-az-thayer-spikelet-pair-20261027.jpg"))
        crown=next(p for p in panels if p.get("image_url","").endswith("kr-az-thayer-root-crown-20261027.jpg"))
        self.assertEqual(len(pair["markers"]),2)
        self.assertEqual(len(crown["markers"]),2)
        for p in (pair,crown):
            self.assertEqual(p["creator"],"Dave Thayer")
            self.assertEqual(p["scientific_name"],"Bothriochloa ischaemum")
            self.assertIn("NOT",p["caption"])
            for a in p["markers"]:
                self.assertTrue(all(0<=a[k]<=100 for k in
                    ("label_x","label_y","target_x","target_y")))
        indices=s["field_photo_quickcheck"]["featured_photo_indices"]
        self.assertIn(panels.index(pair),indices)
        self.assertIn(panels.index(crown),indices)

    def test_learner_links_originals_not_embedded_images(self):
        js=(ROOT/"assets/js/app.js").read_text(encoding="utf-8")
        self.assertIn("function speciesSourceOnlyMacroReferences(",js)
        self.assertIn('source.direct_original',js)
        self.assertIn('studyDrawer("KR research photos',js)
        self.assertIn("source-only",js.lower())
        for field in ("source_page","creator","license"):
            self.assertIn(field,js)

if __name__=="__main__":
    unittest.main()
