#!/usr/bin/env python3
"""Promote three visually inspected, SHA-pinned D. commutatum media without disturbing existing rights."""
import json,pathlib,shutil,hashlib
from PIL import Image
card_dir=pathlib.Path("content/taxa/Poaceae/Dichanthelium/dichanthelium-commutatum")
cardpath=card_dir/"species.json"
j=json.loads(cardpath.read_text(encoding="utf-8"))
assert j["id"]=="dichanthelium-commutatum"
assert j["field_id_finish_pass"]["stage"]=="FIELD_READY_PHOTO_GAPS"
source_dir=pathlib.Path("workflow/photo-reviews/lane4-commutatum-rooted-20261026")
manifest=json.loads((source_dir/"manifest.json").read_text(encoding="utf-8"))
reviews={
"363938835":{
 "label":"Variable panicgrass — live woodland habit with leafy flowering shoots",
 "role":"Actual multi-shoot forest-understory field habit; broad attached stem leaves and flowering panicles above forest litter. Soil-contact region partly visible, but roots and true crown are NOT exposed",
 "caption":"Alex Abair's exact-species field image shows upright branching grassy shoots, attached broad stem blades, terminal airy flowering panicles and an understory floor of leaf litter. Multiple plants overlap, so do not claim every nearby blade belongs to one rooted plant. Roots, tillering crown, true inner ligule and connected belowground structures are not visible.",
 "why":"Crew sees real whole-plant context and leaf-bearing flowering habit rather than a detached seedhead. Does not resolve rooted habit or prove which surrounding blades connect underground.",
 "markers":[
 {"label":"Airy flowering head","label_x":4,"label_y":15,"target_x":25,"target_y":22},
 {"label":"Broad stem leaf","label_x":66,"label_y":49,"target_x":37,"target_y":45}
 ]},
"363938836":{
 "label":"Variable panicgrass — entire attached spring panicle above stem leaf",
 "role":"Actual source-labelled flowering culm with open attached terminal panicle, individually stalked green oval spikelets, and green stem leaves below",
 "caption":"The open flowering head remains attached to the green culm above a pointed green stem blade. Individual small green spikelets sit at the tips of fine branched pedicels. This photograph demonstrates attached panicle architecture but not the true inner ligule, roots, or measured spikelet dimensions.",
 "why":"Makes the flowering architecture traceable from a living shoot rather than an isolated branch, important for field confirmation against other rosette-grasses.",
 "markers":[
 {"label":"Open attached panicle","label_x":71,"label_y":15,"target_x":66,"target_y":33},
 {"label":"Individual oval spikelet","label_x":3,"label_y":28,"target_x":47,"target_y":38},
 {"label":"Attached pointed stem leaf","label_x":72,"label_y":85,"target_x":51,"target_y":77}
 ]},
"259295899":{
 "label":"Variable panicgrass — closed and partly opened spikelets",
 "role":"Two actual source-described attached spikelets at close range; upper spikelet visibly split/partly opened revealing pale internal surfaces, lower green spikelet closed with longitudinal exterior veins; precise glume and lemma identities unresolved",
 "caption":"Alex Abair's macro clearly shows two differently oriented small attached oval spikelets. The upper spikelet opens to expose pale inner surfaces, while the lower green spikelet has several longitudinal veins on its outer face. There is no ruler, and the exact glumes, sterile lemma and fertile floret cannot be independently assigned from these pixels alone.",
 "why":"One of the few genuine reproductive-structure lessons available for this difficult genus. Teaches why an exterior grass spikelet and a partly opened one look so different, without pretending that the organs have been dissected and measured.",
 "markers":[
 {"label":"Partly opened spikelet","label_x":3,"label_y":13,"target_x":32,"target_y":33},
 {"label":"Closed green spikelet","label_x":73,"label_y":88,"target_x":61,"target_y":74}
 ]}
}
rep={"id":"dichanthelium-commutatum","added":[],"held":[],"rights_check":"Each exact Wikimedia Commons photo CC BY 4.0 by Alex Abair; source-image SHA from checked manifest"}
for id,details in reviews.items():
    found=[x for x in manifest["added"] if x["id"]==id]
    assert len(found)==1,"Original rights record missing"
    x=found[0]
    assert x["license"]=="CC BY 4.0" and "Abair" in x["creator"]
    src=pathlib.Path(x["path"])
    assert hashlib.sha256(src.read_bytes()).hexdigest()==x["archived_sha256"],"Staged original fingerprint changed"
    with Image.open(src) as img: assert img.format=="JPEG"
    rel="images/commons-abair-reviewed-"+id+".jpg"
    dst=card_dir/rel
    if any(z.get("file")==rel for z in j["images"]):
       rep["held"].append({"id":id,"reason":"Already canonically installed; skipped"})
       continue
    if dst.exists():raise RuntimeError("Existing file not listed; refuse overwrite")
    shutil.copyfile(src,dst)
    j["images"].append({
       "file":rel,"role":details["role"],"creator":"Alex Abair","license":"CC BY 4.0",
       "license_url":"https://creativecommons.org/licenses/by/4.0/",
       "source_page":x["source_page"],"source_original_sha1":x["source_original_sha1"],
       "archive_sha256":x["archived_sha256"],
       "modifications":"Commons original photographed pixels re-encoded as RGB JPEG with EXIF/GPS stripped; web arrows are separate overlays",
       "public_reuse":"CC BY 4.0: show Alex Abair credit, linked source, CC BY 4.0 license, modification notice",
       "photo_status":"Exact specimen source + license independently verified; 2026-10-26 stored full pixels reviewed; visible-only gross teaching arrows; no rooted crown or measured ligule claim"
    })
    j["visual_comparison"]["items"].insert(sum(1 for r in rep["added"]),{
      "label":details["label"],"scientific_name":"Dichanthelium commutatum",
      "image_url":str(dst).replace("\\","/"),"image_fit":"contain",
      "image_role":details["role"],"caption":details["caption"],"why_it_matters":details["why"],
      "creator":"Alex Abair","license":"CC BY 4.0","license_url":"https://creativecommons.org/licenses/by/4.0/",
      "source_page":x["source_page"],
      "modifications":"RGB JPEG derived EXIF-free, separate image overlay arrows",
      "markers":details["markers"],
      "photo_status":"2026-10-26 visually inspected original pixels. The rootstock, true ligule and glume organ IDs are not claimed to be shown."
    })
    rep["added"].append({"id":id,"photo":str(dst),"arrows":len(details["markers"]),"role":details["label"]})
if rep["added"]:
    j["curation_status"]["photo_metadata_count"]=len(j["images"])
    j["curation_status"]["photo_files_present"]=sum((card_dir/m["file"]).is_file() for m in j["images"])
    j["curation_status"]["own_photo_arrows"]=sum(len(x.get("markers",[])) for x in j["visual_comparison"]["items"] if x.get("scientific_name")=="Dichanthelium commutatum")
    j["learner_visual_status"]["image_count"]=len(j["images"])
    j["field_id_finish_pass"]["visible_photo_arrows"]=j["curation_status"]["own_photo_arrows"]
    j["field_id_finish_pass"]["lane4_role_completion_pass_20261026"]={
      "stage":"FIELD_READY_PHOTO_GAPS",
      "new_exact_species_cc_by_images":len(rep["added"]),
      "public_local_own_photos":j["curation_status"]["photo_files_present"],
      "own_species_arrows":j["curation_status"]["own_photo_arrows"],
      "role_whole_in_habitat":"YES — whole visible leafy flowering shoots and litter habitat, albeit no one fully isolated plant",
      "role_rooted_base":"MISSING — no confirmed exposed connected perennial crown or roots, soil-contact alone insufficient",
      "role_true_collar":"PARTIAL — sheath margin hairs and outer blade junction visible from existing photos; true INNER short ligule remains unmeasured/unexposed",
      "role_attached_flowers":"YES — entire attached spring open panicle with separate stalked spikelets",
      "lookalike":"Lindheimeri/pedicellatum NC photo comparisons retained with original exact image rights; eligible on genuinely NC education site ONLY after individual image CC license terms validated",
      "remaining":["Connected rooted basal tillers and exposed crown of same specimen","Inner ligule photographed cleanly against 1mm scale","Vouchered mature spikelet glume/lemma dissection with ruler","Confirm conditional NC photo-level permissions and site noncommercial status","Live rights-filtered GitHub Pages release and mobile photo-arrow QA"],
      "public_license_policy":"Policy dated 2026-10-20, CC BY-NC images conditionally usable; retain not remove existing photos solely for NC terms",
      "strict_finished":False
    }
    j["visual_comparison"]["subtitle"]="Eight actual own-species CC BY photos now span live woodland habit, entire attached panicle, flower/stigma, leaf junction and two spikelet orientations. True exposed rooted crown and inner ligule measurements remain unshown; NC lookalikes preserved conditionally."
    j["photo_note"]+=" 2026-10-26 Lane 4: three additional CC BY 4.0 real original JPEGs archived with 7 gross arrows, including woodland habit, full attached panicle and partially open spikelet. No exposed rooted crown or measured inner ligule; NC comparisons preserved per noncommercial policy."
    cardpath.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
rpath=pathlib.Path("reports/lane4-commutatum-promote-three-20261026.json")
rpath.parent.mkdir(parents=True,exist_ok=True)
rpath.write_text(json.dumps(rep,indent=2,ensure_ascii=False)+"\n")
print(json.dumps(rep))
