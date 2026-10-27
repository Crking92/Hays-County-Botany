#!/usr/bin/env python3
"""Install FOUR original-pixel-inspected exact iNaturalist Muhlenbergia paniculata photos.
Definitive source photo rights checked at individual-ID level. Do not claim true
inner free ligule, full rooted crown, scale measured glumes, or voucher identity.
"""
import json,pathlib,hashlib,shutil
from PIL import Image
DIR=pathlib.Path("content/taxa/Poaceae/Muhlenbergia/muhlenbergia-paniculata")
SRC=pathlib.Path("reports/lane3-tumblegrass-source-pixel-review-20261027/report.json")
REPORT=pathlib.Path("reports/lane3-tumblegrass-actual-photo-install-20261027.json")
PHOTOS=[
 {"id":652935046,"name":"tumblegrass-aspen-sawyer-unilateral-spikelets-652935046-ccby-nc.jpg",
  "label":"TUMBLEGRASS — close actual appressed spikelets on thin lateral flowering branch",
  "role":"Close, actual source-identified mature one-sided narrow lateral flowering branch bearing tightly appressed spikelets, with a visible branch attachment to main axis; individual glumes/lemmas not separated, finger is approximate scale",
  "caption":"Research-grade source-determined tumblegrass (*Muhlenbergia paniculata*), photographed by Aspen Sawyer in Denton, Texas, on an individual plant in a container. Narrow spikelet-like units are visible along the slender lateral branch, and the branch attachment to the upright axis is visible. This is genuine aboveground reproductive detail rather than just a distant panicle. Do not claim individual measured glumes or a detached single floret: no actual millimeter scale and source determination not independently vouchered.",
  "why":"At field scale, the thin lateral flowering branch bears very small appressed reproductive units on one face—an important architectural contrast with a fluffy muhly panicle.",
  "arrows":[{"label":"Narrow lateral rachis carrying actual attached spikelets","label_x":2,"label_y":13,"target_x":70,"target_y":56},
            {"label":"Visible branch attachment to main axis","label_x":3,"label_y":82,"target_x":45,"target_y":50}]},
 {"id":655365125,"name":"tumblegrass-aspen-sawyer-container-basal-sheaths-655365125-ccby-nc.jpg",
  "label":"TUMBLEGRASS — actual connected leafy tillers with persistent old basal sheaths",
  "role":"Close source-labeled container-grown clump, multiple narrow green live shoots entering the basal cluster among tan persistent leaf sheath remains, NO excavated soil roots, no native wild Texas location proof",
  "caption":"Aspen Sawyer photographed a source-identified tumblegrass clump in a plant container in Denton, Texas. Multiple slender green tillers enter the dense area of pale, dry basal sheaths at the soil surface. Their belowground connections and true fibrous roots are NOT visible. This is good basal growth context only, not a fully documented connected rooted crown or wild county nativity proof.",
  "why":"Makes the dense collection of basal shoots visible and teaches where the crown should be traced before digging or identifying a vegetative plant.",
  "arrows":[{"label":"Living narrow green tillers","label_x":70,"label_y":12,"target_x":54,"target_y":42},
            {"label":"Dense persistent tan lower sheaths; roots hidden","label_x":1,"label_y":86,"target_x":57,"target_y":85}]},
 {"id":635430310,"name":"tumblegrass-kin8man-outer-blade-sheath-collar-635430310-ccby-nc.jpg",
  "label":"TUMBLEGRASS — real blade–sheath junction; free inner ligule NOT exposed",
  "role":"Actual source-labeled green flattened blade ending at sheathing leaf base, pale outer blade-sheath junction and parallel-veined green sheath surface visibly present; no independent peeled-open 1-mm eciliate membrane",
  "caption":"Texas wild source-determined tumblegrass photographed by Kin8man. The flattened leaf blade and narrow sheathing basal tissue meet beside the observer's finger, with pale tissue at the attachment. This is where to look for the species' true membrane ligule, but the free adaxial upper lip is NOT opened, isolated, or measured, and no scale is present.",
  "why":"Shows precisely where the crew should pull the blade away to find the true short membranous ligule; collar and sheath can be learned without inventing hidden ligule anatomy.",
  "arrows":[{"label":"Visible blade–sheath transition, not measured inner ligule","label_x":2,"label_y":9,"target_x":51,"target_y":57},
            {"label":"Folded, parallel-veined green sheathing tissue","label_x":68,"label_y":69,"target_x":72,"target_y":62}]},
 {"id":638348984,"name":"tumblegrass-cody-stricker-spring-branch-flowering-tuft-638348984-ccby.jpg",
  "label":"SPRING BRANCH TEXAS — flowering grass plus living leaves and ground-level bunch",
  "role":"Source-labeled wild in-situ Texas tumblegrass: attached divergent flowering branches on narrow culms directly above green living leaves and a leafy tuft; full root origin is soil-hidden",
  "caption":"Cody Stricker photographed a source-identified wild tumblegrass in Spring Branch, Texas. Several long, slender flowering branches and narrow attached leafy stems rise from the patch of living basal shoots at ground level. This is a real same-field-context whole-plant view, not a lifted root system, and individual spathes/glumes and ligule cannot be measured here.",
  "why":"Gives Central Texas crews an in-place, local-region view of both the living leaf bunch and the distinctive wide-angle branch pattern on the same plant grouping.",
  "arrows":[{"label":"Divergent narrow flowering branch","label_x":3,"label_y":10,"target_x":58,"target_y":21},
            {"label":"Green lower leafy shoots; roots concealed by soil","label_x":3,"label_y":84,"target_x":47,"target_y":85}]}
]
def main():
  s=json.loads((DIR/"species.json").read_text(encoding="utf-8"))
  assert s["id"]=="muhlenbergia-paniculata"
  assert len(s["visual_comparison"]["items"])>=3
  inventory={x["id"]:x for x in json.loads(SRC.read_text())["results"]}
  existing={x.get("source_photo_id") for x in s["visual_comparison"]["items"]}
  new=[]
  for x in PHOTOS:
    pid=x["id"]
    if pid in existing:continue
    a=inventory[pid]
    assert a["status"]=="RIGHTS_VERIFIED_PHOTO_STAGED_NEEDS_ANATOMY_REVIEW"
    assert a["source_taxon"] in ("Schedonnardus paniculatus","Muhlenbergia paniculata")
    assert a["license"] in ("cc-by","cc-by-nc","cc0","cc-by-sa","cc-by-nc-sa")
    src=pathlib.Path(a["file"])
    assert src.exists() and hashlib.sha256(src.read_bytes()).hexdigest()==a["sha256"]
    with Image.open(src) as im:
      assert im.format=="JPEG" and min(im.size)>=1000 and not im.getexif().get(34853)
      im.verify()
    dest=DIR/"images"/x["name"]
    assert not dest.exists(),"Prevent duplicate files"
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(src,dest)
    assert hashlib.sha256(dest.read_bytes()).hexdigest()==a["sha256"]
    license_name={"cc-by":"CC BY","cc-by-nc":"CC BY-NC","cc0":"CC0","cc-by-sa":"CC BY-SA","cc-by-nc-sa":"CC BY-NC-SA"}[a["license"]]
    licurl={"cc-by":"https://creativecommons.org/licenses/by/","cc-by-nc":"https://creativecommons.org/licenses/by-nc/","cc0":"https://creativecommons.org/publicdomain/zero/1.0/","cc-by-sa":"https://creativecommons.org/licenses/by-sa/","cc-by-nc-sa":"https://creativecommons.org/licenses/by-nc-sa/"}[a["license"]]
    panel={"label":x["label"],"scientific_name":"Muhlenbergia paniculata",
      "image_url":dest.as_posix(),"image_fit":"contain","image_role":x["role"],
      "caption":x["caption"],"why_it_matters":x["why"],
      "creator":a["attribution"].split(", some rights")[0].replace("(c) ","").strip(),
      "attribution":a["attribution"],"license":license_name,"license_url":licurl,
      "license_version_note":"Photo-level source license code individually verified; precise license version not independently asserted",
      "source_page":a["source"],"observation_source":a["observation_page"],
      "source_photo_id":pid,"source_place":a["locality"],
      "source_taxon":"Muhlenbergia paniculata (source iNaturalist observation; historical synonym Schedonnardus paniculatus)",
      "modification_note":"Previously validated original iNaturalist JPEG resized to 1800px and reencoded with EXIF/GPS removed; only separate web browser arrows added (not baked into image)",
      "public_reuse":"Conditional CC BY-NC photos only on user-confirmed genuinely noncommercial educational website; attribution and license/changes visible",
      "photo_status":"SOURCE_DETERMINATION_AND_EXACT_LICENSE_VERIFIED; PIXELS_INSPECTED_20261027; TRUE_FREE_LIGULE_NOT_CERTIFIED",
      "markers":x["arrows"]}
    s["visual_comparison"]["items"].append(panel)
    s["images"].append({"file":"images/"+x["name"],"role":x["role"],"creator":panel["creator"],
      "attribution":a["attribution"],"license":license_name,"license_url":licurl,
      "source_page":a["source"],"observation_source":a["observation_page"],
      "source_photo_id":pid,"source_place":a["locality"],"sha256":a["sha256"],
      "modifications":panel["modification_note"],"public_reuse":panel["public_reuse"],
      "photo_status":panel["photo_status"]})
    new.append({"id":pid,"path":dest.as_posix(),"sha256":a["sha256"],"arrows":len(x["arrows"]),"license":license_name})
  assert new,"No newly installed pixels, leave card as-is"
  s["visual_comparison"]["subtitle"]="Seven actually archived source-attributed species photos include Texas unilateral spikelets, close collar location, basal clustered shoots and a wild Spring Branch flowering leaf bunch. True inner ligule and 1-mm glume macro STILL missing. Four recent source-level anatomical additions; old photos preserved."
  s["visual_comparison"]["overlay_note"]+=" 2026-10-27: Four individually licensed source-confirmed iNaturalist images physically archived with eight conservative browser arrows on visible appressed reproductive units, external sheath junction, and live grass growth only. Roots, true free ligule, glume, lemma and voucher remain open."
  s["learner_visual_status"]["image_count"]=len(s["images"])
  s["learner_visual_status"]["note"]="Seven physically stored source-labeled grass images, seven teaching panels. New Texas photos show true lateral branch and attached small spikelets at finger scale, actual outer blade–sheath transition, basal shoots and wild aboveground flowering tuft. True inner membranous ligule, scaled glume/lemma, roots remain missing. FIELD_READY_PHOTO_GAPS."
  s["learner_visual_status"]["status"]="FIELD_READY_PHOTO_GAPS"
  s["field_photo_quickcheck"]["featured_photo_indices"]=[3,6,5,4,0,1]
  s["field_photo_quickcheck"]["steps"].append("In new gallery panel 4, observe actual tiny units appressed to one side of the lateral flowering branch (finger is NOT a 1-mm ruler); panel 5 shows a potted basal bunch with roots underground, panel 6 shows outer leaf/sheath junction without isolated true ligule, panel 7 shows flowering wild Spring Branch plants in habitat.")
  s["field_photo_quickcheck"]["warning"]="2026-10-27 new pixel-inspected source JPEGS document a close unilateral spikelet branch and true outer sheath junction. No sub-mm free ligule, actual fibrous root origin, calibrated separated glumes/lemmas or specimen voucher has been established. Individual NC images are conditioned on actual noncommercial reuse."
  s.setdefault("field_id_finish_pass",{})["lane3_tumblegrass_visible_anatomy_20261027"]={
    "new_local_photos":[x["id"] for x in new],
    "new_browser_arrows":sum(z["arrows"] for z in new),
    "roles_now_shown":["actual close appressed spikelets on flowering raceme","external blade/sheath junction","living connected lower leaf bunch with dry sheaths","attached flowering wild Texas bunch context"],
    "strict_photo_role_provisional":[1,.5,.5,1,.5,0],
    "photo_score_preliminary":"3.5 / 6 = 58.3%; source-attributed image identities remain provisional until voucher",
    "not_showing":["raised free membranous ligule with 1mm scale","mature single spikelet with separated glumes/lemma","exposed linked root crown","verified matched species lookalike anatomy"],
    "status":"FIELD_READY_PHOTO_GAPS","rights":"CC BY and conditional individually verified CC BY-NC, no all rights reserved"
  }
  (DIR/"species.json").write_text(json.dumps(s,ensure_ascii=False,indent=2)+"\n")
  REPORT.parent.mkdir(parents=True,exist_ok=True)
  REPORT.write_text(json.dumps({"species":"Muhlenbergia paniculata","status":"FOUR_TRUE_SOURCE_PHOTOS_PHYSICALLY_INSTALLED_NO_FALSE_LIGULE",
    "new":new,"local_images":len(s["images"]),"panels":len(s["visual_comparison"]["items"]),
    "new_arrows":sum(x["arrows"] for x in new),"six_role_before":1.5,"six_role_after":3.5,
    "percent_before":25,"percent_after":58.3,
    "not_proven":["true inner free ligule","true fibrous roots","separated mature glume/lemma with mm scale","matched look-alike anatomy"],
    "web_site":"Pending existing rights-filtered Pages release and mobile arrow QA"},indent=2)+"\n")
  print("Installed",len(new),"originals,",sum(x["arrows"] for x in new),"arrows. True ligule, roots, glumes held.")
if __name__=="__main__":main()
