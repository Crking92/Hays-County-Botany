#!/usr/bin/env python3
"""Add only four exact-photo-licensed, pixel-screened Buckley tridens basal/collar photos.
All original learner photo records, IDs, arrows, scientific name/range holds preserved.
Do not certify roots, inner free ligule, glumes or dissection that aren't visible.
"""
import json,pathlib,hashlib,shutil
from PIL import Image
ROOT=pathlib.Path("content/taxa/Poaceae/Tridentopsis/tridentopsis-buckleyana")
SOURCE=pathlib.Path("reports/lane3-buckley-fullpixel-review-20261026/report.json")
OUTPUT=pathlib.Path("reports/lane3-buckley-basal-collar-install-20261026.json")
PICKS=[
 {"id":200379117,"role":"Hand-held small vegetative bunch with connected narrow leaf bases and several persistent straw-colored basal sheaths; short rootlike basal strands visible, but NOT an excavated root network",
  "filename":"buckley-eric-keith-handheld-bunch-200379117-cc-by-nc.jpg",
  "label":"BUCKLEY — hand-held compact rooted-base candidate; root network NOT exposed",
  "caption":"Actual wild source-labeled Buckley's tridens from Bandera, Texas (photo Eric Keith). A small clustered bunch of living green and dry blades is held at its attached pale basal sheaths, and short dark basal strands protrude from the bottom. This is useful plant-base context, but their precise root attachment and any rhizome cannot be independently confirmed or measured here. No flowering head or mm scale in frame.",
  "why":"Shows the compact bunch and how individual basal shoots gather at one lower structure, unlike wide field panicle-only photos.",
  "markers":[{"label":"Living and dry narrow blades emerging together","label_x":69,"label_y":10,"target_x":53,"target_y":55},
             {"label":"Tight sheathed lower shoot base; roots not fully exposed","label_x":70,"label_y":86,"target_x":48,"target_y":79}]},
 {"id":200379086,"role":"Close view of multiple attached living tillers and pale fibrous/brown lower sheath bases held in hand, with very short dark rootlike strands at lower edge; no entire cleaned root system",
  "filename":"buckley-eric-keith-tillers-sheath-200379086-cc-by-nc.jpg",
  "label":"BUCKLEY — true connected lower tillers, dry sheath bases, and basal fibers",
  "caption":"High-resolution Eric Keith wild Bandera Texas photograph clearly shows several still-attached green lower leafy tillers among pale persistent sheath fibers at the compact bottom. A few short dark threadlike extensions leave the bottom, but no dissected perennial rhizome, definite root origin, or centimeter ruler is resolved. The shoots are not proven connected to the panicles shown elsewhere.",
  "why":"Shows actual persistent dry lower sheaths and the multiple live shoots entering one compact basal cluster. Better for training than an unexcavated mound of leaves.",
  "markers":[{"label":"Living green tillers emerge among pale basal sheaths","label_x":68,"label_y":7,"target_x":55,"target_y":55},
             {"label":"Basal convergence and brown fibers, no proven rhizome","label_x":72,"label_y":89,"target_x":47,"target_y":92}]},
 {"id":200379105,"role":"True leaf blade/sheath transition closeup, pale inner-facing collar-edge tissue visible but individual free ciliate ligule cannot be measured or certified",
  "filename":"buckley-eric-keith-leaf-transition-200379105-cc-by-nc.jpg",
  "label":"BUCKLEY — pale blade/sheath transition; TRUE ligule not certified",
  "caption":"Wild Bandera Buckley's tridens photographed by Eric Keith. The slender green blade widens above a pale split-edged transition into its lower sheath beside the observer's finger. This is a useful precise location for opening the actual inner collar, but the free 0.4–1 mm ciliate membrane is not exposed and no millimeter scale is shown. Do not mistake a pale sheath margin for a measured ligule.",
  "why":"Directly teaches where to look for the ligule on this species without mislabeling a blade/culm node.",
  "markers":[{"label":"Blade to lower sheath transition; membrane NOT measured","label_x":68,"label_y":13,"target_x":53,"target_y":57}]},
 {"id":414398685,"role":"Hays County living leaf blade and enclosing longitudinally ribbed sheath at blade-sheath collar region; actual inner ligule not exposed",
  "filename":"buckley-andy-blair-woodcreek-sheath-414398685-cc-by-nc.jpg",
  "label":"HAYS COUNTY — real blade/sheath junction, not measured inner ligule",
  "caption":"Actual source-identified Buckley's tridens observed by Andy Blair in Woodcreek, Hays County. The blade narrows into the sheath and pale side tissue frames the junction against a fingertip. This is a genuine local sheath reference, not a peeled-open inner ligule or free measured ciliate membrane; no submillimeter annotation is claimed.",
  "why":"Adds an actual Hays County specimen photographed at the location where a field worker would peel open the sheath to inspect the ligule.",
  "markers":[{"label":"Blade–sheath junction; inner free ligule obscured","label_x":1,"label_y":13,"target_x":52,"target_y":55}]},
]
def main():
    sj=json.loads((ROOT/"species.json").read_text())
    assert sj["id"]=="tridentopsis-buckleyana"
    prior=sj["visual_comparison"]["items"]
    if any(x.get("source_photo_id")==200379117 for x in prior):
        print("Already installed, no duplicate");return
    assert len(prior)==11 and len(sj["images"])==8,"Prior canonical gallery changed, stop safely"
    report=json.loads(SOURCE.read_text())
    assert report["status"].startswith("PHYSICAL_SOURCE_PIXELS_")
    staged={x["photo_id"]:x for x in report["results"]}
    gallery=[]
    for spec in PICKS:
        src=staged[spec["id"]]
        assert src["status"]=="PHOTO_SOURCE_RIGHTS_VERIFIED_PIXEL_REVIEW_REQUIRED"
        assert src["license"]=="cc-by-nc" and src["attribution"] and src["source_taxon"]=="Tridens buckleyanus"
        p=pathlib.Path(src["file"])
        assert p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==src["sha256"]
        with Image.open(p) as im:
            assert im.format=="JPEG" and min(im.size)>=1000 and not im.getexif().get(34853)
            im.verify()
        dest=ROOT/"images"/spec["filename"]
        assert not dest.exists()
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(p,dest)
        assert hashlib.sha256(dest.read_bytes()).hexdigest()==src["sha256"]
        creator=src["attribution"].replace("(c) ","").split(", some rights")[0].strip()
        panel={
          "label":spec["label"],"scientific_name":"Tridentopsis buckleyana",
          "image_url":dest.as_posix(),"image_fit":"contain","image_role":spec["role"],
          "caption":spec["caption"],"why_it_matters":spec["why"],
          "creator":creator,"attribution":src["attribution"],"license":"CC BY-NC",
          "license_url":"https://creativecommons.org/licenses/by-nc/",
          "license_version_note":"Original iNaturalist source photo-level license_code cc-by-nc; exact version not independently certified",
          "source_page":src["photo_page"],"observation_source":src["observation_page"],
          "source_photo_id":spec["id"],"source_observation_id":src["source_observation_id"],
          "source_place":src["place_guess"],
          "source_taxon_name":"Tridens buckleyanus (accepted Tridentopsis buckleyana); research-grade observation, not independently herbarium-vouchered",
          "public_reuse":"CONDITIONAL CC BY-NC credited noncommercial educational learner only, subject to no monetization/affiliate commercialization",
          "modification_note":"Original source photograph downsampled/re-encoded to JPEG 1800px max with EXIF/GPS removed; no crop, arrows are separate website overlays.",
          "photo_status":"FULL_ORIGINAL_PIXEL_REVIEWED_20261026, macro gross structures only, no measured free ligule or independently root-vouchered rhizome.",
          "markers":spec["markers"]
        }
        sj["images"].append({
          "file":"images/"+spec["filename"],"role":spec["role"],"creator":creator,"attribution":src["attribution"],
          "license":"CC BY-NC","license_url":"https://creativecommons.org/licenses/by-nc/",
          "source_page":src["photo_page"],"observation_source":src["observation_page"],
          "source_photo_id":spec["id"],"source_observation_id":src["source_observation_id"],
          "source_place":src["place_guess"],"original_source_url":src["photo_source_url"],
          "sha256":src["sha256"],"modifications":panel["modification_note"],
          "public_reuse":panel["public_reuse"],"photo_status":panel["photo_status"]
        })
        gallery.append(panel)
    # Previously Buckley panels 0..7; comparison T. mutica panels 8..10. Add after exact species.
    sj["visual_comparison"]["items"]=prior[:8]+gallery+prior[8:]
    assert len(sj["visual_comparison"]["items"])==15
    key=sj["field_id_short_tiles"]
    key[0]["photo_panel_indices"]=[0,8,9,1,2,6]
    key[0]["details"]+=" Gallery panels 9–10 add a physically collected Bandera compact leafy base and exposed dry sheaths; short rootlike strands are not a cleaned measured root network."
    key[1]["photo_panel_indices"]=[3,10,11]
    key[1]["details"]+=" Gallery panel 11 is a Bandera blade/sheath transition, panel 12 is a separate Hays County local collar region. Neither actually isolates or measures the short true inner ciliate ligule."
    key[4]["photo_panel_indices"]=[1,2,12,13,14]
    key[4]["details"]=key[4]["details"].replace("Panels 9–11","Panels 13–15")
    key[5]["photo_panel_indices"]=list(range(15))
    key[5]["details"]=key[5]["details"].replace("all 8 real JPEGs","all 12 real JPEGs")
    key[5]["short"]="FIELD_READY_PHOTO_GAPS: twelve archived source-licensed species photographs; true measured ligule and rooted crown dissection still open."
    quick=sj["field_photo_quickcheck"]
    quick["featured_photo_indices"]=[0,8,9,10,11,2,4,12]
    quick["steps"][0]+=" New panels 9–10 show close hand-held basal sheaths and basal fibers from the same Bandera source observation, but no rooted crown/rhizome with a scale."
    quick["steps"][2]+=" See panels 11–12 for exact-species blade/sheath transitions, including Woodcreek in Hays County; do not claim a fully exposed ligule."
    quick["steps"][4]=quick["steps"][4].replace("panels 9–11","panels 13–15")
    quick["steps"][6]=quick["steps"][6].replace("seven CC BY 4.0 originals","seven CC BY 4.0 originals plus four new image-level CC BY-NC originals")
    quick["warning"]="Fifteen comparison gallery panels = twelve archived same-species photos including conditional CC BY-NC + three DIFFERENT-SPECIES slim Tridentopsis photos. Original panel 4 is culm/node, newer panels 11–12 show blade/sheath transitions but not a measured free 0.4–1 mm ligule. New hand-held basal photos show tight live/dry tillers and short basal strands, NOT exposed same-vouchered roots/rhizome plus cm scale. FIELD_READY_PHOTO_GAPS."
    sj["visual_comparison"]["subtitle"]="Twelve archived exact-source Buckley photos (including credited conditional NC Bandera/Hays sheath and base macros) plus three genuine mutica look-alike panels. True free 0.4–1 mm ciliate ligule, cleaned rooted crown, and dissection remain missing."
    sj["visual_comparison"]["overlay_note"]+=" 2026-10-26 four licensed in-repository same-species originals added after pixel review (two connected basal-tiller views, two sheath-transition views), six conservative browser arrows. No measured true ligule or exposed root/rhizome claim."
    sj["learner_visual_status"]["image_count"]=len(sj["images"])
    sj["learner_visual_status"]["note"]="12 physically archived same-species images including 4 new BY-NC Bandera/Hays exact-photo-rights source references; 15 gallery panels including 3 actual other-species slim tridentopsis comparisons. New base shows short basal fibers, still no complete roots/rhizome or peeled calibrated 0.4–1 mm free ciliate ligule. FIELD_READY_PHOTO_GAPS."
    sj["curation_status"]["photo_metadata_count"]=12
    sj["curation_status"]["photo_files_present"]=12
    sj["curation_status"]["lane3_buckley_basalsheath_20261026"]={
      "status":"12_LOCAL_PHOTOS_15_GALLERY_PANELS_ONLY_PARTIAL_FOUR_ROLE",
      "verified_source_ids":[x["source_photo_id"] for x in gallery],
      "new_browser_arrows":sum(len(x["markers"]) for x in gallery),
      "photo_rights":"CC BY-NC photo-level independent source verified, conditionally accepted only for noncommercial educational site",
      "lookalikes":"Three distinct T. mutica comparison panels preserved; note index shift from 8–10 to 12–14",
      "source_taxonomy_and_county_holds_preserved":True
    }
    sj["field_id_finish_pass"]["stage"]="FIELD_READY_PHOTO_GAPS — twelve exact-source local images include 4 new hand-held basal tiller and leaf–sheath junction photos; small rootlike basal extensions and collar edges visible, but no clean connected rhizome/root crown with mm scale or separated/fully measured 0.4–1 mm ciliate inner ligule."
    sj["field_id_finish_pass"]["practical_four_role_20261026"]["photo_count_local"]=12
    sj["field_id_finish_pass"]["practical_four_role_20261026"]["same_species_gallery_panels"]=12
    sj["field_id_finish_pass"]["practical_four_role_20261026"]["rooted_whole_plant"]="PARTIAL — hand-held Bandera plant photos now show connected live/dry tillers converging at lower basal sheaths with short dark rootlike fibers, but no separately verified complete root network or whole rooted flowering stem from one vouchered plant."
    sj["field_id_finish_pass"]["practical_four_role_20261026"]["inner_collar_ligule"]="PARTIAL — two real exact-species blade/sheath transitions now physically photographed (Bandera + Hays). Pale edge tissue is visible but free 0.4–1 mm ciliate membrane is not separated/measurement certified."
    sj["field_id_finish_pass"]["practical_four_role_20261026"]["new_original_photos"]=4
    sj["field_id_finish_pass"]["practical_four_role_20261026"]["new_arrows"]=6
    sj["field_id_finish_pass"]["lane3_basalsheath_20261026"]={
      "new_photo_ids":[x["source_photo_id"] for x in gallery],
      "photo_roles":["hand-held basal live/dry tiller convergence","persistent basal dry sheaths close-up","blade/sheath transition against finger","actual Hays County blade/sheath outer collar"],
      "new_browser_arrows":6,
      "not_yet_proven":["clean connected root crown including buried short rhizome and roots","peeled inner ciliate 0.4–1 mm membrane beside mm scale","floret glume and lemma underside anatomy for mutica overlap"],
      "status":"FIELD_READY_PHOTO_GAPS",
      "license_condition":"Current genuinely noncommercial learner with credited image-specific CC BY-NC licenses"}
    (ROOT/"species.json").write_text(json.dumps(sj,indent=2,ensure_ascii=False)+"\n")
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps({
      "status":"FOUR_SOURCE_JPEGS_INSTALLED_6_GROSS_ARROWS_WITH_ANATOMY_HOLDS",
      "species":"Tridentopsis buckleyana","photo_ids":[x["source_photo_id"] for x in gallery],
      "local_species_images":len(sj["images"]),"gallery_panels":len(sj["visual_comparison"]["items"]),
      "new_arrows":6,"lookalike_panels":3,
      "source_pixel_review":"reports/lane3-buckley-fullpixel-review-20261026/report.json",
      "remaining":["one full same-plant flowering intact rooted crown, cleaned/photographed with cm or mm ruler",
                   "peeled TRUE ciliate membrane 0.4–1 mm under 10x with scale",
                   "measured glume/lemma pubescence only as needed to separate T. mutica"],
      "status_notice":"FIELD_READY_PHOTO_GAPS, physical archive does NOT equal successful public Pages deployment"
    },indent=2)+"\n")
    print("SUCCESS: Four source-licensed same-species photographs, six truthful arrows, 12 local species JPEGs, 15 panels.")
if __name__=="__main__":
    main()
