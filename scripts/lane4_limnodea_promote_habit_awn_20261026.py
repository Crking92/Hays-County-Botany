#!/usr/bin/env python3
"""Promote actual CC0 source-labeled Limnodea with visible gross-only markers."""
import json,pathlib,hashlib,shutil
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Limnodea/limnodea-arkansana")
p=base/"species.json"
j=json.loads(p.read_text(encoding="utf-8"))
assert j["id"]=="limnodea-arkansana"
mp=pathlib.Path("workflow/photo-reviews/lane4-limnodea-basal-20261026/manifest.json")
data=json.loads(mp.read_text(encoding="utf-8"))
photos={
"671201197":{
 "label":"Ozarkgrass — flowering tufts emerging from one compact aboveground basal clump",
 "role":"Genuine CC0 species-identified whole clump in North Texas thin rocky soil; narrow basal leaves and fine dry flower stems from close ground region; no exposed roots.",
 "caption":"Actual Dallas field photograph reveals a cluster of small narrow leafy shoots and wiry stems emerging together through rocky disturbed soil. The base where the stems meet the ground is visible, but the lower fibrous roots are still underground and cannot be confidently traced.",
 "why":"Crew sees realistic aboveground basal habit and how small thin grass stems gather near soil surface. Not sufficient to claim a connected rooted annual specimen.",
 "arrows":[
 {"label":"Leafy basal cluster","label_x":76,"label_y":76,"target_x":47,"target_y":65},
 {"label":"Wiry flowering culm","label_x":72,"label_y":15,"target_x":55,"target_y":38}
 ]},
"671201150":{
 "label":"Ozarkgrass — isolated awned flowering units against fingertip",
 "role":"Actual CC0 iNaturalist species photo of green elongated attached flowering unit and long very fine pale awn; NOT calibrated lemma-tooth dissection.",
 "caption":"Dallas close-up shows narrow pale-green flowering units on a fine axis, with a very long hairlike awn extending beyond them. One elongated green body and pale awn are visible, but the 0.5-mm paired lemma teeth and exact awn insertion cannot be separately established at this resolution.",
 "why":"A true close structure photo supporting where to inspect the one-awn floret character. Do not mistake single-awn morphology text for an actual proved two-tooth lemma dissection.",
 "arrows":[
 {"label":"Elongated green flowering unit","label_x":5,"label_y":23,"target_x":42,"target_y":48},
 {"label":"Long fine awn","label_x":71,"label_y":7,"target_x":37,"target_y":46}
 ]}
}
report={"species":"Limnodea arkansana","added":[],"held":[]}
for id,role in photos.items():
 hits=[x for x in data["added"] if x["photo_id"]==id]
 assert len(hits)==1,"No image-level rights record"
 m=hits[0]
 assert m["license"]=="cc0"
 src=pathlib.Path(m["local"])
 assert hashlib.sha256(src.read_bytes()).hexdigest()==m["sha256"]
 with Image.open(src) as im:assert im.format=="JPEG"
 file="images/inat-cc0-limnodea-"+id+".jpg"
 dest=base/file
 if any(x.get("file")==file for x in j["images"]):
    report["held"].append({"id":id,"reason":"Previously installed"});continue
 if dest.exists():raise RuntimeError("Original file path conflict")
 shutil.copyfile(src,dest)
 j["images"].append({
  "file":file,"role":role["role"],"creator":"iNaturalist CC0 photographer (record did not include creator name)",
  "license":"CC0 1.0","license_url":"https://creativecommons.org/publicdomain/zero/1.0/",
  "source_page":m["source"],"source_observation":m["observation_page"],"source_photo_id":id,
  "archived_sha256":m["sha256"],"original_photo_license_code":m["license"],
  "public_reuse":"CC0 photo-level license, link to original observation and photo for provenance",
  "modifications":"Source large JPEG re-encoded RGB with EXIF/GPS removed and separately displayed arrows",
  "photo_status":"Pixels personally reviewed 2026-10-26, visible-only aboveground basal clump and awned gross flowering units. No exposed roots or two-tooth lemma morphology confirmed."
 })
 j["visual_comparison"]["items"].insert(len(report["added"]),{
  "label":role["label"],"scientific_name":"Limnodea arkansana",
  "image_url":str(dest).replace("\\","/"),"image_fit":"contain",
  "image_role":role["role"],"caption":role["caption"],"why_it_matters":role["why"],
  "creator":"iNaturalist CC0 source photographer","license":"CC0 1.0",
  "license_url":"https://creativecommons.org/publicdomain/zero/1.0/","source_page":m["source"],
  "markers":role["arrows"],
  "photo_status":"Pixel reviewed 2026-10-26; source-identified species; no exposed root or microscopically separated glume/lemma."
 })
 report["added"].append({"id":id,"path":str(dest),"arrows":len(role["arrows"])})
if report["added"]:
 j["curation_status"]["photo_metadata_count"]=len(j["images"])
 j["curation_status"]["photo_files_present"]=sum((base/x["file"]).exists() for x in j["images"])
 j["learner_visual_status"]["image_count"]=len(j["images"])
 j["field_id_finish_pass"]["lane4_source_clump_spikelet_20261026"]={
  "stage":"FIELD_READY_PHOTO_GAPS",
  "new_public_cc0_jpegs":len(report["added"]),
  "new_gross_arrows":sum(q["arrows"] for q in report["added"]),
  "rooted_base":"MISSING: photo 671201197 shows basal leaf tuft but not fibrous roots. No rooting node claim.",
  "true_ligule":"PARTIAL: existing Chet Burrier CC BY photo and collection-specific Harms tissue plate; no fully isolated free membrane with scale",
  "whole_habitat":"YES source-identified live population photo with basal clump",
  "attached_flowers":"YES existing author-credited panicle and new gross awn closeup",
  "repro_species_discriminator":"ONE lemma awn inserted between TWO lemma teeth — published botanical character, NOT yet photo-separated in these new frames. Compare three Aristida awn branches.",
  "critical_missing":["Actual same plant basal connected fibrous roots fully exposed","Measured lemma's two teeth and single awn insertion with 1mm scale","Free inner true ligule height and texture with mm bar","Individual rights reconciliation of existing Harms archived JPEGs","Deployed Pages and mobile image/arrow verification"],
  "photo_rights":"Two new original photo-level CC0 images; old NC photos conditionally allowed only with individual photo-license proof for genuinely noncommercial site; Bob Harms educational display does not equate to blanket CC or independent local copying rights."
 }
 j["visual_comparison"]["subtitle"]="Real CC0 source-identified Ozarkgrass clump and a close awned floral unit added. All original reproductive/ligule panels preserved. ROOTS still unexposed; exact one-awn-in-two-teeth dissection still not photographically proven."
 j["photo_note"]+=" 2026-10-26: two actual individual CC0 licensed Ozarkgrass original JPEGs archived with 4 structure arrows: live basal clump (unexposed roots) and narrow awned unit (no proved glume/lemma insertion). Existing rights retained."
 p.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n")
path=pathlib.Path("reports/lane4-limnodea-promote-20261026.json")
path.parent.mkdir(exist_ok=True)
path.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
