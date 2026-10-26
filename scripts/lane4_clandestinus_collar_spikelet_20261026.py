#!/usr/bin/env python3
"""Install source-vouched CC0 macro imagery of Sporobolus clandestinus without speculative dissection."""
import pathlib,json,hashlib,shutil
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Sporobolus/sporobolus-clandestinus")
path=base/"species.json"
j=json.loads(path.read_text(encoding="utf-8"))
assert j["id"]=="sporobolus-clandestinus"
manifest=json.loads(pathlib.Path("workflow/photo-reviews/lane4-sporobolus-clandestinus-basal-20261026/manifest.json").read_text(encoding="utf-8"))
selected={
"603360049":{
 "label":"Rough dropseed — true blade/sheath junction and visible fine hairs",
 "role":"Real taxon-determined CC0 close-up of actual sheath mouth and leaf blade crossing at node; fringe of individual fine pale hairs visible around junction but tiny free inner ligule unmeasured.",
 "caption":"The greenish sheath wraps a fingertip, and a dried blade angles to the right from its mouth. Very fine pale hairs are visible along the margin of the blade/sheath junction. They can guide the crew to where the true short hair-fringe ligule belongs, but the inner free edge and the published 0.2–0.3 mm length cannot be proven with this unscaled exterior view.",
 "why":"Genuine anatomy-focused image with actual thin hairs and correct collar location; usable independent CC0 alternative to copyrighted collection photos.",
 "markers":[
  {"label":"Blade/sheath junction","label_x":5,"label_y":24,"target_x":53,"target_y":59},
  {"label":"Fine hairs near collar","label_x":77,"label_y":48,"target_x":56,"target_y":61}
 ]},
"603360014":{
 "label":"Rough dropseed — tiny detached dark reproductive units",
 "role":"Real CC0 source photograph of two minute pointed detached dry units on palm; exact glumes, fertile floret or wet pericarp identity not independently resolved.",
 "caption":"Two small dark pointed units from a source-labelled rough dropseed observation are placed against a palm. This gives a genuine size-context lesson and shows how unlike the whole contracted flowerhead the separated units look. The photograph does not prove glume, lemma, caryopsis, gelatinization, or a calibrated measurement.",
 "why":"Shows actual separated reproductive objects, but final comparison against S. compositus still requires botanically separated ripe units and wet/dry pericarp response with a millimeter reference.",
 "markers":[
  {"label":"Upper detached dark unit","label_x":70,"label_y":10,"target_x":33,"target_y":24},
  {"label":"Lower detached dark unit","label_x":6,"label_y":77,"target_x":60,"target_y":77}
 ]}
}
report={"species":"Sporobolus clandestinus","added":[],"held":[]}
for id,detail in selected.items():
 data=[z for z in manifest["added"] if z["photo_id"]==id]
 assert len(data)==1
 x=data[0]
 assert x["license"]=="cc0"
 src=pathlib.Path(x["local"])
 assert hashlib.sha256(src.read_bytes()).hexdigest()==x["sha256"]
 with Image.open(src) as im:assert im.format=="JPEG"
 rel="images/inat-cc0-reviewed-"+id+".jpg"
 dst=base/rel
 if any(y.get("file")==rel for y in j["images"]):
    report["held"].append({"id":id,"reason":"Previously installed"});continue
 if dst.exists():raise RuntimeError("Do not overwrite conflicting image")
 shutil.copyfile(src,dst)
 j["images"].append({
  "file":rel,"role":detail["role"],"creator":"iNaturalist CC0 photographer (name not present in source API attribution)",
  "license":"CC0 1.0","license_url":"https://creativecommons.org/publicdomain/zero/1.0/",
  "source_page":x["source"],"source_observation":x["observation_page"],
  "image_photo_id":id,"source_photo_license_code":"cc0",
  "archived_sha256":x["sha256"],"public_reuse":"Individually verified CC0 public use; retain provenance source link",
  "modifications":"Original source large JPEG re-encoded RGB EXIF/GPS removed; arrows displayed separately",
  "photo_status":"Actual full pixels examined. Hairs at exterior collar and detached dark objects visible. True inner 0.2 mm ligule, isolated glume/lemma, wet pericarp and roots NOT certified."
 })
 j["visual_comparison"]["items"].insert(len(report["added"]),{
  "label":detail["label"],"scientific_name":"Sporobolus clandestinus",
  "image_url":str(dst).replace("\\","/"),"image_fit":"contain",
  "image_role":detail["role"],"caption":detail["caption"],"why_it_matters":detail["why"],
  "creator":"iNaturalist CC0 source photographer","license":"CC0 1.0",
  "license_url":"https://creativecommons.org/publicdomain/zero/1.0/",
  "source_page":x["source"],"markers":detail["markers"],
  "photo_status":"Human pixel checked 2026-10-26; no inferred seed organ ID or actual separated inner ligule."
 })
 report["added"].append({"id":id,"local":str(dst),"arrows":len(detail["markers"])})
if report["added"]:
 j["curation_status"]["photo_metadata_count"]=len(j["images"])
 j["curation_status"]["photo_files_present"]=sum(1 for i in j["images"] if i.get("file","").startswith("images/") and (base/i["file"]).is_file())
 j["learner_visual_status"]["image_count"]=len(j["images"])
 j["field_id_finish_pass"]["lane4_cc0_collar_seed_20261026"]={
  "stage":"FIELD_READY_PHOTO_GAPS",
  "new_own_source_CC0_photos":len(report["added"]),
  "new_visible_only_arrows":sum(x["arrows"] for x in report["added"]),
  "actual_local_photo_files":j["curation_status"]["photo_files_present"],
  "whole_habitat":"Existing true source-labelled Central Texas field photo (Bob Harms), visible tuft but no exposed crown",
  "root_base":"MISSING actual connected roots from one perennial shoot",
  "true_collar":"PARTIAL new CC0 photograph shows real sheath mouth and tiny hairs, but inner short hair fringe at 0.2–0.3 mm not isolated",
  "attached_flowering":"Existing Harms source narrow contracted attached panicle, plus several proper spikelet views",
  "critical_reproductive_photo":"Detached dark dry units NOT equal to verified loose/non-gelatinous pericarp; wet- vs dry-grain response photographed and measured still essential versus S. compositus",
  "rightscaveat":"Existing copyright © Bob Harms scientific selected Monocots uses collection-limited external educational display permission, not blanket public CC or documented right to newly archive; preserve existing images and flag for license reconciliation.",
  "remaining":["Exposed connected perennial root crown","20–40× inner short hair ligule with 1mm graduations","Individual measured glume, fertile lemma and palea from voucher","Wet pericarp comparison against S. compositus","Original color+microscope lemmal prickles, rights verified","Live Pages/mobile QA"]
 }
 j["photo_note"]+=" 2026-10-26: two source-verified CC0 iNaturalist macros physically installed and linked with four arrow overlays on actual exterior hairline collar and loose dark units; roots, free ligule and wet pericarp not proven."
 path.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n")
r=pathlib.Path("reports/lane4-clandestinus-macro-20261026.json")
r.parent.mkdir(exist_ok=True)
r.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
