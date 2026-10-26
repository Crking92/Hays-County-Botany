#!/usr/bin/env python3
"""Promote one basal view and two examined CC BY / CC0 collar photographs.

No claim of rooted crown where only base of aboveground tillers is visible.
No unlicensed Bob Harms photo changes or speculative true ligule dimensions.
"""
import json,pathlib,hashlib,shutil
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Disakisperma/disakisperma-dubium")
cardpath=base/"species.json"
card=json.loads(cardpath.read_text(encoding="utf-8"))
assert card["id"]=="disakisperma-dubium"
manifest=json.loads(pathlib.Path("workflow/photo-reviews/lane4-disakisperma-basal-20261026/manifest.json").read_text(encoding="utf-8"))
reviews={
"684867239":{
 "label":"Green sprangletop — pale collar tissue at true blade/sheath junction",
 "role":"Exact taxon iNaturalist CC0 real macro of a grass blade inserted into green sheath and a visibly pale curved tissue lip at their junction; not independently measured inner free ligule.",
 "caption":"Source photograph shows the actual green blade attached to its vertical sheath. At the intersection a pale narrow raised lip and nearby sheath seam are visible. Do not confuse the curved outer sheath fold with a fully measured free inner ligule; this exterior view has no millimeter scale.",
 "why":"Guides the crew to the true collar location instead of attempting to identify a ligule somewhere down the stem.",
 "arrows":[
  {"label":"Blade/sheath junction","label_x":7,"label_y":53,"target_x":45,"target_y":56},
  {"label":"Pale collar-region lip","label_x":68,"label_y":83,"target_x":42,"target_y":63},
  {"label":"Blade above junction","label_x":71,"label_y":8,"target_x":47,"target_y":25}
 ]},
"748603011":{
 "label":"Green sprangletop — outer leaf-collar and upright sheath",
 "role":"CC BY source-identified same-species photographed open V junction, slender green leaf blade and enclosing lower sheath. Inner ligule cannot be certified by exterior view alone.",
 "caption":"Annika Lindqvist's image clearly shows a pointed green blade joining an upright ribbed culm and enclosing sheath, with pale tissue at the V-shaped junction. There is no interior unfolded membrane or millimeter bar; do not measure this pale fold as a ligule.",
 "why":"Second actual collar orientation lets a crew member find the blade–sheath seam; visual verification of the free ligule remains a higher magnification task.",
 "arrows":[
  {"label":"Leaf blade attachment","label_x":4,"label_y":26,"target_x":59,"target_y":51},
  {"label":"Upright lower sheath","label_x":72,"label_y":86,"target_x":60,"target_y":77}
 ]},
"680380456":{
 "label":"Green sprangletop — basal leaf clump in rocky limestone habitat",
 "role":"Original CC BY Edwards County source shows a tuft of multiple green leafy shoots emerging among dead basal blades and limestone rock; no exposed connected rootstock or fibrous roots.",
 "caption":"Jo Roberts photographed a patch of narrow green blades emerging from a gathered basal clump at the edge of limestone. Dead strawlike blades and a flowering culm remain associated with the clump. Although the crown position is suggested, the photograph does NOT expose roots or distinguish belowground crown branches.",
 "why":"A local-west Texas habitat and basal-tiller clue, useful alongside the whole plant. This is NOT counted as completing the rooted-base requirement.",
 "arrows":[
  {"label":"Gathered basal leaf bases","label_x":7,"label_y":80,"target_x":20,"target_y":71},
  {"label":"Narrow live blades","label_x":75,"label_y":15,"target_x":27,"target_y":24}
 ]}
}
report={"species":"Disakisperma dubium","added":[],"held":[],"source_rights":"Each individual photo license checked against photo-level iNaturalist API; no Bob Harms images modified."}
for id,details in reviews.items():
 recs=[r for r in manifest["added"] if r["photo_id"]==id]
 assert len(recs)==1
 rec=recs[0]
 assert rec["license"] in ["cc0","cc-by"], "No public license"
 assert hashlib.sha256(pathlib.Path(rec["local"]).read_bytes()).hexdigest()==rec["sha256"]
 with Image.open(rec["local"]) as pic: assert pic.format=="JPEG"
 rel="images/inat-reviewed-"+id+".jpg"
 dst=base/rel
 if any(p.get("file")==rel for p in card["images"]):
    report["held"].append({"id":id,"reason":"Already archived"}); continue
 if dst.exists(): raise RuntimeError("Path conflict")
 shutil.copyfile(rec["local"],dst)
 lic="CC0 1.0" if rec["license"]=="cc0" else "CC BY (source version not independently confirmed)"
 url="https://creativecommons.org/publicdomain/zero/1.0/" if rec["license"]=="cc0" else None
 creator="Jo Roberts" if id=="680380456" else ("Annika Lindqvist" if id=="748603011" else "Source-recorded public-domain photographer")
 image={
   "file":rel,"role":details["role"],"creator":creator,
   "license":lic,"source_page":rec["source"],"source_observation":rec["observation_page"],
   "archived_sha256":rec["sha256"],"license_evidence":"Source iNaturalist photo license_code "+rec["license"]+" retrieved 2026-10-26",
   "modifications":"Source image converted to RGB JPEG with EXIF/GPS removed, overlay markers separate",
   "public_reuse":"Photo-level "+lic+", preserve creator/source/conditions",
   "photo_status":"Actual pixels inspected; label only true outside collar, upper sheath, green basal blades; no exposed roots or scaled inner ligule"
 }
 if url:image["license_url"]=url
 card["images"].append(image)
 panel={
   "label":details["label"],"scientific_name":"Disakisperma dubium",
   "image_url":str(dst).replace("\\","/"),"image_fit":"contain",
   "image_role":details["role"],"caption":details["caption"],"why_it_matters":details["why"],
   "creator":creator,"license":lic,"source_page":rec["source"],"source_observation":rec["observation_page"],
   "markers":details["arrows"],
   "photo_status":"Pixel reviewed 2026-10-26. Root crown and free inner measured ligule NOT shown; no borrowed lookalike photo.",
   "modifications":"Photo re-encoded EXIF-free; browser annotation overlays separate"
 }
 if url:panel["license_url"]=url
 card["visual_comparison"]["items"].insert(len(report["added"]),panel)
 report["added"].append({"id":id,"local":str(dst),"arrows":len(details["arrows"]),"role":details["label"]})
if report["added"]:
 card["curation_status"]["photo_metadata_count"]=len(card["images"])
 card["curation_status"]["photo_files_present"]=sum((base/x["file"]).is_file() for x in card["images"])
 card["curation_status"]["photo_panels"]=len(card["visual_comparison"]["items"])
 card["learner_visual_status"]["image_count"]=len(card["images"])
 card["field_id_finish_pass"]["lane4_current_photo_roles_20261026"]={
  "stage":"FIELD_READY_PHOTO_GAPS",
  "local_exact_species_images":card["curation_status"]["photo_files_present"],
  "new_public_images":len(report["added"]),
  "new_pixel_verified_arrows":sum(x["arrows"] for x in report["added"]),
  "habitat":"YES regional flowering shoots in limestone and other prior existing whole bunch views",
  "rooted_base":"NOT YET — basal green tillers visible but no exposed connected roots; keep highest priority.",
  "collar":"PARTIAL — two new real source-identified external leaf/sheath junction images, plus older Jim Conrad true ligule-area view. Free edge without 1mm bar not proven.",
  "entire_flowering_head":"YES prior real full attached panicle and 1-sided multi-flowered reproductive branches",
  "lookalike":"Preserve existing NC Dinebra comparison conditionally for genuinely noncommercial use after individual license/version check.",
  "Bob_Harms_permission":"Five existing physical Bob Harms scientific images retained for history while archive-rights scope needs reconciliation. No new copies, relabelings or arrows.",
  "remaining":["Actual exposed joined crown and attached fibrous roots","True inner ligule isolated with mm ruler","Lookalike head comparison with independent rights and calibrated units","Public website rights-filtered deployment/image QA"]
 }
 card["visual_comparison"]["subtitle"]="Public CC BY/CC0 views of actual collar and basal shoots supplement rich existing reproductive lesson. Root crown STILL not exposed; no measured inner ligule claim; preserve source attribution and conditionally licensed references."
 card["photo_note"]+=" 2026-10-26 Lane 4: three CC0/CC BY original photo-level rights screened JPEGs archived with seven visible-only arrows for true external collar, sheath and basal tillers; root crown not exposed, no false completion."
 cardpath.write_text(json.dumps(card,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
rp=pathlib.Path("reports/lane4-disakisperma-collar-promotion-20261026.json")
rp.parent.mkdir(exist_ok=True)
rp.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
