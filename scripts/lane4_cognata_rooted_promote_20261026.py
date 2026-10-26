#!/usr/bin/env python3
"""Promote photo-level licensed real rooted Digitaria cognata with pixels reviewed.

Proof is rooted crown, not an inferred perennial base from a leaf tuft. No
microscopic ligule claim, no botanical author determination falsely created.
"""
import json,pathlib,hashlib,shutil
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Digitaria/digitaria-cognata")
cp=base/"species.json"
j=json.loads(cp.read_text(encoding="utf-8"))
assert j["id"]=="digitaria-cognata"
p=pathlib.Path("workflow/photo-reviews/lane4-cognata-basal-20261026/manifest.json")
manifest=json.loads(p.read_text(encoding="utf-8"))
w={
"677363763":{
  "label":"Fall witchgrass — exposed knotty basal crown and attached roots",
  "role":"Actual source-identified photographed dug-up basal grass crown with short roots hanging below, multiple sheathing shoots and narrow blades; not a microscope verified rhizome structure",
  "caption":"A Spring Branch, Texas observation by Cody Stricker shows a small tightly gathered base bearing several shoots, old dried sheaths, and short fibrous roots clearly hanging out at the bottom. These are genuinely attached roots, not leaf litter or guessed underground runners. Crown details are visible but this photo does not prove subterranean rhizomes or stolons.",
  "why":"Provides the first actual rooted-base photograph for the public crew card, allowing a comparison of knotty crown and emerging shoots rather than guessing from flowering stems alone.",
  "markers":[
    {"label":"Exposed rooted crown","label_x":69,"label_y":89,"target_x":18,"target_y":84},
    {"label":"Visible attached roots","label_x":69,"label_y":99,"target_x":16,"target_y":95},
    {"label":"Sheathed leafy shoots","label_x":71,"label_y":35,"target_x":33,"target_y":48}
  ]},
"677363921":{
  "label":"Fall witchgrass — connected roots, leaves and full airy flowering culm",
  "role":"Actual full original source-identified collected plant with fibrous roots at basal crown and wiry hair-thin flowering stems ending in sparse spikelets; root and panicle demonstrably on same specimen",
  "caption":"Another frame of the same Spring Branch specimen shows the rooted crown at the base of the held plant, living green basal blades and one or more fine reddish flowering stalks extending above the hand into a very sparse panicle. Multiple neighboring weeds remain in the ground behind the specimen and are not part of it. The photo has no millimeter scale for spikelets or ligule.",
  "why":"This is the long-missing connected whole plant and growth-base demonstration: roots, leafy crown and flowering stem in a single credible source photograph.",
  "markers":[
    {"label":"Connected rooted crown","label_x":67,"label_y":91,"target_x":31,"target_y":93},
    {"label":"Airy flowering culm","label_x":5,"label_y":21,"target_x":44,"target_y":31},
    {"label":"Basal green blades","label_x":76,"label_y":73,"target_x":41,"target_y":79}
  ]},
"676177661":{
  "label":"Fall witchgrass — narrow blade with conspicuous pale uneven edge",
  "role":"Source-identified Texas photo shows an attached narrow blade with visibly pale, crimped-looking leaf margin beside other grass leaves; true ligule not uncovered or measured",
  "caption":"Cody Stricker's Hunt, Texas photograph isolates several long thin grass blades against fingers. The short darker green central blade has a visibly pale, irregular wavy margin on the side facing right. This is a photographic reference for the published one-sided undulate margin; it does not prove that each visible irregularity is intact rather than minor leaf damage, or show the internal 0.5-mm membranous ligule.",
  "why":"Lets the crew inspect the unusual pale crinkled leaf-edge clue on a real grass, instead of mistaking stem hairs or a wound for the blade margin. Confirm on an intact opposite edge and source-verified plant.",
  "markers":[
    {"label":"Pale irregular blade edge","label_x":74,"label_y":30,"target_x":25,"target_y":48},
    {"label":"Narrow attached blade","label_x":4,"label_y":12,"target_x":15,"target_y":27}
  ]}
}
report={"id":"digitaria-cognata","added":[],"held":[]}
for id,description in w.items():
    matches=[v for v in manifest["added"] if v["photo_id"]==id]
    assert len(matches)==1,"Original photo-level license record missing"
    item=matches[0]
    assert item["license"]=="cc-by" and "Cody Stricker" in item["attribution"]
    src=pathlib.Path(item["local"])
    assert hashlib.sha256(src.read_bytes()).hexdigest()==item["sha256"]
    with Image.open(src) as im:assert im.format=="JPEG"
    rel="images/inat-open-cody-stricker-"+id+".jpg"
    dst=base/rel
    if any(x.get("file")==rel for x in j["images"]):
       report["held"].append({"photo":id,"reason":"Already installed"})
       continue
    if dst.exists():raise RuntimeError("File conflict")
    shutil.copyfile(src,dst)
    j["images"].append({
      "file":rel,"role":description["role"],
      "creator":"Cody Stricker","license":"CC BY",
      "license_url":"https://creativecommons.org/licenses/by/4.0/",
      "license_verification":"Individual iNaturalist photo-level API license_code=cc-by on 2026-10-26; exact per-photo license version not independently confirmed",
      "source_page":item["source"],"source_observation":item["observation_page"],
      "photo_id":id,"archived_sha256":item["sha256"],
      "modifications":"Original photo served at iNaturalist large resolution, re-encoded JPEG with EXIF/GPS stripped, separate gallery arrows",
      "public_reuse":"CC BY photo-level licensed; credit photographer and source with license, state re-encoding change",
      "photo_status":"REAL PIXELS inspected; actual connected roots/crown shown in images 677363763 and 677363921; no true ligule or dissected spikelet claims"
    })
    j["visual_comparison"]["items"].insert(len(report["added"]),{
      "label":description["label"],"scientific_name":"Digitaria cognata",
      "image_url":str(dst).replace("\\","/"),"image_fit":"contain",
      "image_role":description["role"],"caption":description["caption"],
      "why_it_matters":description["why"],"creator":"Cody Stricker","license":"CC BY",
      "license_url":"https://creativecommons.org/licenses/by/4.0/",
      "source_page":item["source"],"source_observation":item["observation_page"],
      "modifications":"RGB JPEG EXIF-stripped from source iNaturalist large photo; arrows are overlay labels",
      "markers":description["markers"],
      "photo_status":"2026-10-26 pixel review: annotates only real crown, roots, flowering culms, blades, and leaf margin. No inner ligule or microscopic glume label."
    })
    report["added"].append({"photo_id":id,"local":str(dst),"arrows":len(description["markers"]),"role":description["label"]})
if report["added"]:
    own=j["visual_comparison"]["items"]
    own_arrows=sum(len(x.get("markers",[])) for x in own if x.get("scientific_name")=="Digitaria cognata")
    j["curation_status"]["photo_metadata_count"]=len(j["images"])
    j["curation_status"]["photo_files_present"]=sum((base/x["file"]).is_file() for x in j["images"])
    j["curation_status"]["verified_visible_arrows"]=own_arrows
    j["learner_visual_status"]["image_count"]=len(j["images"])
    j["field_id_finish_pass"]["verified_gross_structure_arrows"]=own_arrows
    j["field_id_finish_pass"]["lane4_rooted_roles_20261026"]={
      "stage":"FIELD_READY_PHOTO_GAPS",
      "new_public_use_photos":len(report["added"]),
      "own_species_local_photos":j["curation_status"]["photo_files_present"],
      "own_species_markers":own_arrows,
      "whole_plant":"YES source-identified leafy crown, attached flowering culm and roots in one photo, although plant held out of soil rather than intact in habitat",
      "root_base":"YES actual exposed rooted knotty base, attached fibrous roots and leafy tillers photographed on original specimen",
      "true_collar":"MISSING true inner membrane ~0.5 mm with scale; lower sheaths and blade margins alone are insufficient",
      "entire_attached_flowering":"YES airy fine branched panicle on same rooted plant, but minute reproductive anatomy unresolved",
      "local_comparison":"Already present CC BY and CC0 southern crabgrass look-alike panels, not misidentified as same taxon",
      "remaining":["Actual inner ligule at blade/sheath opening with 1-mm scale","Precisely focused swollen hairy branch axil","Three measured mature spikelets and separated glumes/lemmas","Confirm leaf-margin asymmetry on undamaged specimen","Rights-filtered live Pages mobile QA","Source geographic provenance is not BONAP county nativity certification"],
      "source_public_license":"Individual photo license_code=cc-by by Cody Stricker, iNaturalist observations 370764833 and 370143466. Source version to be checked for exact license link."
    }
    j["visual_comparison"]["subtitle"]="Seven physically archived true Digitaria cognata photo views now include source-authenticated exposed fibrous roots and knotty perennial crown, full connected plant, leaf margin, and open panicle. Lookalike D. ciliaris galleries kept. True inner ligule and microscopic branch-axil hairs remain gaps."
    j["photo_note"]+=" 2026-10-26 Lane 4: three photo-level CC BY source records of actual Texas fall witchgrass installed, eight gross-only arrows. Two show connected fibrous roots/leafy crown, one illustrates pale crimped blade-edge candidate; true ligule still missing."
    cp.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
rp=pathlib.Path("reports/lane4-cognata-rooted-promote-20261026.json")
rp.parent.mkdir(exist_ok=True)
rp.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
print(json.dumps(report))
