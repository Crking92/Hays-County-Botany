"""Final three-reed source/teaching audit: licenses, actual JPEG bytes,
full lesson references, plain-language vs specialist consistency.

Does NOT claim lineage-certified Gulf images, missing macros, or mobile
pixel-alignment review. Run on source checkout before website publication.
"""
import json
import unittest
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
FILES={
  "arundo-donax":"content/taxa/Poaceae/Arundo/arundo-donax/species.json",
  "phragmites-australis":"content/taxa/Poaceae/Phragmites/phragmites-australis/species.json",
  "zizaniopsis-miliacea":"content/taxa/Poaceae/Zizaniopsis/zizaniopsis-miliacea/species.json"
}
EXPECTED={"arundo-donax":(7,10,5),"phragmites-australis":(17,21,23),"zizaniopsis-miliacea":(5,3,6)}
def load(id):return json.loads((ROOT/FILES[id]).read_text(encoding="utf8"))
class ReedFinal(unittest.TestCase):
  def test_every_archived_photo(self):
    for taxon in FILES:
      with self.subTest(taxon=taxon):
        d=load(taxon)
        self.assertEqual(len(d["images"]),EXPECTED[taxon][0])
        self.assertEqual(len(d["visual_comparison"]["items"]),EXPECTED[taxon][1])
        self.assertEqual(d["curation_status"]["photo_metadata_count"],len(d["images"]))
        self.assertEqual(d["curation_status"]["photo_files_present"],len(d["images"]))
        base=(ROOT/FILES[taxon]).parent
        seen=set()
        for im in d["images"]:
          rel=im["file"];self.assertNotIn(rel,seen);seen.add(rel)
          self.assertTrue(rel.startswith("images/") and '..' not in rel)
          p=base/rel;self.assertTrue(p.is_file(),str(p))
          self.assertGreater(p.stat().st_size,15000)
          with Image.open(p) as jpeg:
            self.assertIn(jpeg.format,("JPEG","PNG","WEBP"))
            jpeg.verify()
          self.assertTrue(im.get("creator") and im.get("license") and im.get("source_page"))
          self.assertTrue(str(im["source_page"]).startswith("https://"))
          self.assertNotIn("Neil Reese",str(im["creator"]))
          self.assertFalse("SDSU" in str(im.get("file","")))
          self.assertTrue(
             any(marker in str(im["license"]).lower() for marker in
                 ["cc by","cc0","public domain"]),
             "Unexpected rights designation: "+str(im["license"]))
  def test_panels_and_gross_arrows(self):
    for taxon,path in FILES.items():
      d=load(taxon)
      count=0
      for panel in d["visual_comparison"]["items"]:
        src=panel.get("image_url","")
        self.assertTrue(src.startswith(("content/","https://")))
        if src.startswith("content/"):self.assertTrue((ROOT/src).is_file(),src)
        for marker in panel.get("markers",[]):
          count+=1
          self.assertTrue(str(marker.get("label","")).strip())
          for key in ("label_x","label_y","target_x","target_y"):
            self.assertLessEqual(0,float(marker[key]));self.assertLessEqual(float(marker[key]),100)
      self.assertEqual(count,EXPECTED[taxon][2],taxon)
  def test_beginner_and_advanced_both_available(self):
    for id in ("arundo-donax","phragmites-australis"):
      d=load(id);b=d["beginner_learning_path"]
      self.assertEqual(len(b["steps"]),4)
      self.assertEqual(len(d["field_photo_quickcheck"]["steps"]),5)
      self.assertTrue(b["intro"] and b["safety_note"])
      self.assertTrue(len(d["morphology_keys"]["best_field_traits"])>=4)
    p=load("phragmites-australis")
    assert p["comparisons"]["lineage_matrix"]
    assert len(p["comparisons"]["lineage_matrix"])==3
    self.assertTrue(p["three_lineage_photo_lesson_20261026"].get("study_means_genetic_lineages_2004"))
    self.assertIn("lineage unresolved",p["beginner_learning_path"]["safety_note"].lower()
        +" "+p["field_photo_quickcheck"]["steps"][-1].lower())
    a=load("arundo-donax")
    self.assertIn("rachilla",json.dumps(a["field_id_finish_pass"]["diagnostic_species_finalization_20261023"]).lower())
    z=load("zizaniopsis-miliacea")
    self.assertIn("not",z["field_id_finish_pass"]["measured_reproductive_key_20261023"]["measured_diagnostic_key"][3].lower())
    self.assertEqual(len(z["reed_lookalike_final_audit_20261027"]["review_only_images"]),2)
  def test_layered_ui_links_and_source_checks(self):
    field=(ROOT/"assets/js/field-id-tiles.js").read_text()
    quiz=(ROOT/"assets/js/quiz-tiles.js").read_text()
    learner=(ROOT/"assets/js/app.js").read_text()
    for phrase in ("fieldAdvancedReedNotes(sp)","fieldBeginnerPath(sp,entry.path)",
                   "data-compare-species","field-compare-detail-photo","photo.steps,mor.crew_20_second_sequence"):
      self.assertIn(phrase,field)
    for phrase in ("function reedResults()","HaysReedQuiz.build","Retry the ten questions"):
      self.assertIn(phrase,quiz)
    self.assertIn("speciesBeginnerPhotoPath(sp)",learner)
if __name__=="__main__":unittest.main()
