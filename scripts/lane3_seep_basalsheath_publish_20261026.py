#!/usr/bin/env python3
"""Install two pixel-reviewed wild seep-muhly basal/sheath photos, retain all diagnostic holds.
Source JPEGs already rights-validated at photo ID level, EXIF-stripped, staged in repo.
"""
import json,pathlib,hashlib,shutil
from PIL import Image
BASE=pathlib.Path("content/taxa/Poaceae/Muhlenbergia/muhlenbergia-reverchonii")
REPORT=pathlib.Path("reports/lane3-seep-source-pixel-review-20261026/report.json")
OUT=pathlib.Path("reports/lane3-seep-basal-sheath-install-20261026.json")
LICENSE="https://creativecommons.org/licenses/by-nc/"
CHOICES=[
  dict(id=748546772,filestem="seep-muhly-kate-morgan-basal-shoots-748546772-ccby-nc.jpg",
    label="SEEP MUHLY — green new shoots among persistent dry basal sheaths",
    role="In-ground basal growth with narrow fresh blades and pale old sheathing material; connected underground rhizome and roots not visible",
    caption="Wild research-grade source-identified seep muhly photographed by kate morgan in Fort Worth, Texas. Real fresh green blades emerge among persistent pale, curling dry lower sheaths against limestone and moss. Visible base is partly hidden by litter; do NOT count this as an excavated crown, an exposed rhizome, or a scaled ligule.",
    why="Shows where to look among persistent old basal sheaths for living shoots on a naturally growing seep muhly rather than only relying on its flowering plume.",
    marks=[{"label":"New green leafy shoots","label_x":59,"label_y":10,"target_x":58,"target_y":37},
           {"label":"Dry lower sheaths; underground base hidden","label_x":2,"label_y":76,"target_x":51,"target_y":66}]),
  dict(id=751511302,filestem="seep-muhly-tfrehman-lower-sheath-751511302-ccby-nc.jpg",
    label="SEEP MUHLY — ridged lower sheath/culm and peeling outer tissue (NOT ligule)",
    role="Gross leaf-sheath/culm surface with parallel longitudinal ridges and dry papery outer material; NOT a blade–sheath junction or exposed inner ligule",
    caption="Texas wild source photo by tfrehman. A green longitudinally ribbed lower grass axis sits beside a pale peeling dry outer sheath remnant and fingers. This photo does NOT reveal the exact inner blade–sheath collar, true membranous ligule, an underground rhizome, or millimeter anatomy. Use as a cautionary outer-sheath view.",
    why="Crew can learn why a dry sheath flap or green culm ridge cannot be labeled the true grass ligule. The actual inner collar must be opened separately.",
    marks=[{"label":"Visible longitudinal ridges; inner ligule not shown","label_x":3,"label_y":33,"target_x":61,"target_y":53},
           {"label":"Pale peeling old outer tissue, not ligule","label_x":1,"label_y":79,"target_x":40,"target_y":85}])
]
def main():
    j=json.loads((BASE/"species.json").read_text())
    assert j["id"]=="muhlenbergia-reverchonii"
    existing=j["visual_comparison"]["items"]
    if any("748546772" in x.get("image_url","") for x in existing):
        print("Already installed");return
    assert len(existing)==10,"Review changed gallery indices before shifting!"
    a=json.loads(REPORT.read_text())
    byid={x["id"]:x for x in a["results"]}
    selected=[]
    for spec in CHOICES:
        src=byid[spec["id"]]
        assert src["status"]=="REVIEW_SOURCE_BYTES_AVAILABLE_NOT_DIAGNOSTICALLY_PASSED"
        assert src["license"]=="cc-by-nc" and src["attribution"] and src["species"]=="Muhlenbergia reverchonii"
        f=pathlib.Path(src["file"])
        assert f.is_file() and hashlib.sha256(f.read_bytes()).hexdigest()==src["sha256"]
        with Image.open(f) as im:
            assert im.format=="JPEG" and min(im.size)>=700 and not im.getexif().get(34853)
            im.verify()
        dest=BASE/"images"/spec["filestem"]
        if dest.exists():raise RuntimeError("Destination already exists "+str(dest))
        shutil.copyfile(f,dest)
        assert hashlib.sha256(dest.read_bytes()).hexdigest()==src["sha256"]
        imgpath=dest.as_posix()
        panel={
            "label":spec["label"],"scientific_name":"Muhlenbergia reverchonii",
            "image_url":imgpath,"image_fit":"contain","image_role":spec["role"],
            "caption":spec["caption"],"why_it_matters":spec["why"],
            "creator":src["attribution"].split(", some rights")[0].replace("(c) ","").strip(),
            "attribution":src["attribution"],"license":"CC BY-NC","license_url":LICENSE,
            "license_version_note":"iNaturalist photo-level cc-by-nc code verified; specific license version unverified",
            "source_page":src["photo_page"],
            "observation_source":"https://www.inaturalist.org/observations/"+str(src["observation_id"]),
            "source_observation_id":src["observation_id"],"source_photo_id":src["id"],
            "source_place":src["place_guess"],
            "modification_note":"Original iNaturalist JPEG resized to fit 1700px and re-encoded with EXIF/GPS removed in review; arrows are separate browser overlays, no new pixel markings.",
            "reuse_scope":"Properly attributed only on this genuinely noncommercial educational learner; reassess NC if monetization or promotion changes",
            "photo_status":"PIXEL_REVIEWED_LOCAL_JPEG; broad structures only, NOT true inner ligule, exposed rhizome or rooted crown",
            "markers":spec["marks"]}
        j["images"].append({"file":"images/"+spec["filestem"],"role":spec["role"],
            "creator":panel["creator"],"attribution":src["attribution"],
            "license":"CC BY-NC","license_url":LICENSE,"source_page":src["photo_page"],
            "observation_source":panel["observation_source"],
            "source_photo_id":src["id"],"source_observation_id":src["observation_id"],
            "source_place":src["place_guess"],"sha256":src["sha256"],
            "modifications":panel["modification_note"],"public_reuse":panel["reuse_scope"],
            "photo_status":"LOCAL_EXIF_STRIPPED_ANATOMY_CAUTION; inner ligule and rhizome roots not pictured"})
        selected.append(panel)
    # First 2 panels: tuft. Insert base and sheath next, before 2 Harms external images.
    j["visual_comparison"]["items"]=existing[:2]+selected+existing[2:]
    for tile in j["field_id_short_tiles"]:
        tile["photo_panel_indices"]=[v+2 if v>=2 else v for v in tile["photo_panel_indices"]]
    j["field_id_short_tiles"][0]["photo_panel_indices"]=[0,1,2,4,11]
    j["field_id_short_tiles"][1]["photo_panel_indices"]=[3,5]
    for tile in j["field_id_short_tiles"]:
        t=tile["details"]
        if tile["heading"].startswith("01"):
            t=t.replace("gallery panel 3","gallery panel 5")
            t += " New gallery panel 3 shows fresh blades and dead basal sheaths among moss and limestone; roots remain hidden."
        elif tile["heading"].startswith("02"):
            t=t.replace("gallery panel 4","gallery panel 6")
            t += " New gallery panel 4 shows ribbed outer tissue and dry sheath, NOT the free inner ligule."
        elif tile["heading"].startswith("04"):
            t=t.replace("gallery panel 7","gallery panel 9")
        elif tile["heading"].startswith("06"):
            t=t.replace("Gallery panels 5–6","Gallery panels 7–8").replace("panel 8","panel 10").replace("panel 9","panel 11").replace("Panel 7","Panel 9")
        tile["details"]=t
    check=j["field_photo_quickcheck"]
    updated=[]
    for num,step in enumerate(check["steps"]):
        if num==0:
            step=step.replace("Gallery panels 1–2","Gallery panels 1–3")
            step=step.replace("(panel 3)","(panel 5)").replace("(panel 10)","(panel 12)")
            step+=" New panel 4 shows dried OUTER sheath material, NOT opened true ligule."
        elif num==1:step=step.replace("Gallery panel 4","Gallery panel 6")
        elif num==2:step=step.replace("Gallery panels 5–7","Gallery panels 7–9")
        elif num==3:
            step=step.replace("Gallery panels 8–9","Gallery panels 10–11")
            step=step.replace("Panel 8","Panel 10").replace("panel 9","panel 11")
        updated.append(step)
    check["steps"]=updated
    check["featured_photo_indices"]=[(n+2 if n>=2 else n) for n in check["featured_photo_indices"]]
    check["warning"]=check["warning"].replace("Six exact species images","Eight exact species images")
    j["visual_comparison"]["subtitle"]=j["visual_comparison"]["subtitle"].replace("Six locally archived","Eight locally archived")
    j["visual_comparison"]["overlay_note"]+=" 2026-10-26: two conditional CC BY-NC original wild Texas basal/sheath photos added with four gross-structure arrows only. No roots, condensed rhizome, inner ligule measurement, or measured glumes claimed."
    j["learner_visual_status"]["image_count"]=len(j["images"])
    j["learner_visual_status"]["note"]="Eight physically archived exact-species source images including two new wild basal/sheath teaching photos; true opened measured ligule and exposed connected short rhizome/root crown still missing. FIELD_READY_PHOTO_GAPS."
    j["curation_status"]["photo_metadata_count"]=len(j["images"])
    j["curation_status"]["photo_files_present"]=len(j["images"])
    j["curation_status"]["lane3_basal_sheath_photo_install_20261026"]="Two wild Texas conditional CC BY-NC source photos physically archived and gallery-linked; four externally rendered broad arrows only. Current 8 local species images / 12 gallery panels. Root, rhizome, inner ligule and microdissection holds preserved."
    j["field_id_finish_pass"]["stage"]="FIELD_READY_PHOTO_GAPS — eight local species images include two new verified wild basal/sheath views and three wild flowering photographs; Bob Harms two remote copyright-retained references remain external. Actual extracted connected rhizome/root crown and measured inner ligule unavailable."
    j["field_id_finish_pass"]["lane3_basal_sheath_20261026"]={
      "status":"EIGHT_LOCAL_IMAGES_12_PANELS_WITH_FIELD_ANATOMY_HOLDS",
      "photos_added":[x["source_photo_id"] for x in selected],
      "arrows_added":sum(len(x["markers"]) for x in selected),
      "roles_added":["visible living blades emerging among persistent old basal sheaths",
        "outer sheath/culm ribbing and old papery tissue as NON-LIGULE caution"],
      "roles_not_proven":["connected underground condensed rhizome with attached roots","opened actual inner ligule with millimeter ruler","dissected glume lemma awn at scale"],
      "license":"CC BY-NC licensed exact photos, allowed conditionally on genuinely noncommercial credited educational site",
      "different_species_panels_preserved":2,
      "old_photo_panels_preserved":10}
    (BASE/"species.json").write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n")
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps({
       "status":"TWO_WILD_BASAL_AND_SHEATH_IMAGES_INSTALLED_NO_MICRO_ROLE_CLOSED",
       "photo_ids":[x["source_photo_id"] for x in selected],"local_same_species_images":len(j["images"]),
       "gallery_panels":len(j["visual_comparison"]["items"]),
       "new_arrows":4,"source_review":str(REPORT),
       "remaining":["whole live wild flowering specimen with exposed attached condensed rhizome/root crown with scale","true peeled-inner ligule with mm ruler","mature floret dissection if species unresolved"],
       "public_site":"PUBLISH_VIA_EXISTING_RIGHTS_FILTERED_PAGES_WORKFLOW_NOT_AUTOMATICALLY_LIVE"},indent=2)+"\n")
    print("SUCCESS: 2 field basal/sheath JPEGs, 4 conservative arrows, gallery indexed, all science holds retained")
if __name__=="__main__":main()
