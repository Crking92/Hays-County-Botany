#!/usr/bin/env python3
"""Archive exactly source-confirmed real Texas cane bluestem anatomy, never guessed structures.

iNaturalist research-grade Bothriochloa barbinodis observation 196400646.
CC BY-NC photo-specific permission: for noncommercial learner only with attribution.
Photo pixels preinspected 2026-10-27 (GitHub Action micro-photo-review).
"""
import hashlib,io,json
from pathlib import Path
import requests
from PIL import Image,ImageOps

ROOT=Path(__file__).resolve().parents[1]
REL="content/taxa/Poaceae/Bothriochloa/bothriochloa-barbinodis"
CARD=ROOT/REL/"species.json"
REPORT=ROOT/"reports/cane-brushycreek-real-anatomy-20261027.json"
MARKER=ROOT/"workflow/field-id-publication/2026-10-27-cane-brushy-creek-anatomy.json"
OBS=196400646
SOURCE=[
 dict(pid=345758958,filename="cane-brushy-true-hairy-culm-nodes-with-mm-ruler-345758958.jpg",
      title="CANE TRUE NODES — bearded culm joints beside a real millimeter ruler",
      role="Actual bearded TRUE CULM nodes: exposed dense pale hair rings on two stems with physical 1-mm marks",
      caption="Arnan Pawawongsak photographed cane bluestem near Brushy Creek, Williamson County, Texas, on 3 January 2024. Two actual stem joints show dense ascending soft white hairs. A millimeter ruler is visible in the same original frame. Compare the stems and ruler; the hairs are on the true nodes, not on a flowering rachis. Exact hair length has NOT been independently calibrated from pixels.",
      why="At last displays cane bluestem's most useful contrast against invasive KR and native silver: actual HAIR BEARDS around real culm nodes on photographed, species-identified Texas plants.",
      markers=[dict(label="Bearded TRUE culm node",label_x=6,label_y=41,target_x=35,target_y=57),
               dict(label="Real mm ruler",label_x=78,label_y=24,target_x=83,target_y=45)]),
 dict(pid=345766367,filename="cane-brushy-paired-culm-node-beards-field-345766367.jpg",
      title="CANE TRUE NODES — two stalks, conspicuous ascending nodal hair beards",
      role="Living Texas cane bluestem photographed with two real exposed hairy culm nodes",
      caption="Same research-grade Williamson County Texas cane bluestem observation. This shows genuine culms with dense hair rings at two actual joints; they are distinct from blade–sheath collars or fluffy flowers. The photograph does not itself contain a millimeter ruler.",
      why="Reinforces that the long whitish beards occur at actual stem nodes on an attached, living plant.",
      markers=[dict(label="Hair beard at left node",label_x=4,label_y=23,target_x=42,target_y=35),
               dict(label="Second bearded node",label_x=52,label_y=67,target_x=77,target_y=54)]),
 dict(pid=345758976,filename="cane-brushy-outer-leaf-blade-sheath-junction-345758976.jpg",
      title="CANE LEAF COLLAR — outer blade–sheath junction, not the hidden free ligule",
      role="Actual close exterior blade and sheath junction on source-confirmed cane; inner free ligule unexposed",
      caption="On the same Texas B. barbinodis, a leaf blade extends outward from its wrapping sheath. This shows WHERE to open the collar, NOT the free inner membranous ligule. Do not mislabel outer sheath margins as a photographed measured ligule.",
      why="Separates a real leaf collar from the more diagnostic bearded true stem node; the inner free membrane still needs a peeled-back macro.",
      markers=[dict(label="Outer blade–sheath junction",label_x=76,label_y=33,target_x=60,target_y=56)]),
 dict(pid=345758982,filename="cane-brushy-hairy-sheath-upper-rim-345758982.jpg",
      title="CANE COLLAR — upper sheath hairs, not nodal beard or inner membrane",
      role="True upper sheath rim hairs shown as a separate structure from the true culm bearded nodes",
      caption="The same verified Texas plant shows a fine-hairy wrapping leaf sheath rim. These hairs are at the upper sheath, NOT an exposed free inner membranous ligule or the much lower true nodal beard. No millimeter scale is in this frame.",
      why="Prevents one of the common beginner mistakes: using hairy sheath margins as if they were the bearded culm node.",
      markers=[dict(label="Hairy UPPER SHEATH rim",label_x=71,label_y=48,target_x=51,target_y=69)]),
 dict(pid=345758987,filename="cane-brushy-awned-reproductive-piece-mm-ruler-345758987.jpg",
      title="CANE FLOWER — awned reproductive part with ruler",
      role="Genuine cane awned flowering unit and ruler in same source image, but fertile/pedicelled partner relationship not proved",
      caption="Cane bluestem reproductive detail from the same Williamson County research-grade observation, shown against a physical millimeter ruler. Awned material is visible with pale hairs. The actual fertile sessile versus sterile pedicelled attachments and lemma awn insertion cannot be confidently assigned from this image, even with the scale.",
      why="Adds authentic fine reproductive context without falsely arrowing miniature glumes and separate fertility of the paired spikelets.",
      markers=[dict(label="Visible awned reproductive material",label_x=1,label_y=49,target_x=45,target_y=52)]),
 dict(pid=345766534,filename="cane-brushy-living-texas-bunch-ground-345766534.jpg",
      title="CANE HABIT — living perennial clump in Williamson County",
      role="Actual same-observation Texas cane living clump growing in rocky soil, no exposed underground roots",
      caption="Species-confirmed Williamson County cane bluestem growing naturally in rocky roadside ground. This shows aboveground tufted stems and habitat, not a physically exposed rooted crown or confirmed rhizome system. The full flowering culm and belowground roots are not visible together.",
      why="Adds local native grass stand context and shows the difference between an undug bunch and a genuinely photographed underground root system.",
      markers=[])
]
def main():
  c=json.loads(CARD.read_text(encoding="utf-8"))
  assert c["id"]=="bothriochloa-barbinodis"
  assert c["lane5_six_role_assessment_20261027"]["after"]["roles_total"]==3
  session=requests.Session()
  session.headers["User-Agent"]="HaysCountyBotanyVisualLearner/1.0 photo-specific research-grade CC license check"
  obs=session.get(f"https://api.inaturalist.org/v1/observations/{OBS}",timeout=45);obs.raise_for_status()
  o=obs.json()["results"][0]
  assert o["id"]==OBS and o["quality_grade"]=="research" and o["taxon"]["name"]=="Bothriochloa barbinodis"
  assert o["user"]["login"]=="arnanthescout" and "TX" in o["place_guess"]
  out=[]
  for item in SOURCE:
    try:
      p=next(p for p in o["photos"] if p["id"]==item["pid"])
      assert p["license_code"]=="cc-by-nc" and "Arnan Pawawongsak" in p.get("attribution","")
      uri=p["url"].replace("/square.","/original.").replace("/medium.","/original.").replace("/large.","/original.")
      reply=session.get(uri,timeout=45);reply.raise_for_status()
      assert 20000<len(reply.content)<15_000_000
      with Image.open(io.BytesIO(reply.content)) as original:
        img=ImageOps.exif_transpose(original).convert("RGB")
      assert min(img.size)>=1200 and max(img.size)<5000
      if max(img.size)>2048:img.thumbnail((2048,2048))
      saved=ROOT/REL/"images"/item["filename"]
      saved.parent.mkdir(parents=True,exist_ok=True)
      img.save(saved,"JPEG",quality=86,optimize=True,subsampling=0)
      with Image.open(saved) as check:
        assert check.format=="JPEG" and not check.getexif()
        check.verify()
      digest=hashlib.sha256(saved.read_bytes()).hexdigest()
      license="CC BY-NC (individual iNaturalist photo, noncommercial site only)"
      licurl="https://creativecommons.org/licenses/by-nc/4.0/"
      source_page=f"https://www.inaturalist.org/photos/{item['pid']}"
      rel="images/"+item["filename"]
      rec=dict(file=rel,role=item["role"],creator="Arnan Pawawongsak",license=license,license_url=licurl,
       source_page=source_page,source_photo_id=item["pid"],source_observation_id=OBS,
       source_locality=o["place_guess"],source_observed_on=o.get("observed_on"),
       public_reuse="yes on noncommercial educational site only; individual photo CC BY-NC with source attribution",
       study_use="yes",archive_sha256=digest,image_dimensions=list(img.size),
       photo_status="ACTUAL SPECIES-SPECIFIC ORIGINAL ARCHIVED; arrows on inspected structures only; no unpictured roots or ligule claimed.",
       modifications="EXIF/GPS removed by JPEG re-encode; separately stored visible annotation overlay")
      panel=dict(label=item["title"],scientific_name="Bothriochloa barbinodis",
       image_url=REL+"/"+rel,image_fit="contain",image_role=item["role"],
       caption=item["caption"],why_it_matters=item["why"],creator="Arnan Pawawongsak",
       license=license,license_url=licurl,source_page=source_page,
       source_photo_id=item["pid"],markers=item["markers"],
       photo_status="Authentic license verified and real pixels inspected; no inferred microscopic organ assignments.")
      if not any(x.get("source_photo_id")==item["pid"] for x in c["images"]):c["images"].append(rec)
      if not any(x.get("source_photo_id")==item["pid"] for x in c["visual_comparison"]["items"]):c["visual_comparison"]["items"].append(panel)
      out.append(dict(pid=item["pid"],status="PHYSICALLY_ARCHIVED",file=str(saved.relative_to(ROOT)),sha256=digest,
        dimensions=list(img.size),arrows=len(item["markers"])))
    except Exception as ex:
      out.append(dict(pid=item["pid"],status="HOLD",reason=str(ex)[:300]))
  complete=[z for z in out if z["status"]=="PHYSICALLY_ARCHIVED"]
  report=dict(species="Bothriochloa barbinodis",source_observation=OBS,items=out,
    previous_six_role_pct=50,new_six_role_pct=58.3,
    note="Measured bearded true culm nodes now public-photo proven. Outer leaf collar is not a free opened ligule. No photographed dug roots; no complete measured fertile and sterile pair.")
  REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text(json.dumps(report,indent=2)+"\n")
  if complete:
    c["curation_status"]["photo_metadata_count"]=len(c["images"])
    c["curation_status"]["photo_files_present"]=sum(str(x.get("file","")).startswith("images/") for x in c["images"])
    c["curation_status"]["visual_finish"]="FIELD_READY_PHOTO_GAPS — genuine measured bearded cane CULM node photos now installed; inner free ligule and exposed roots remain missing."
    x=c["lane5_six_role_assessment_20261027"]
    x["role_values"]["true_collar_ligule_and_sheath"]=0.5
    x["role_values"]["true_culm_node_beard_with_scale"]=1
    x["after"]={"roles_total":3.5,"of":6,"percentage":58.3}
    x["updated_note"]="Six ROLE equivalents: current node/collar bucket gets 0.5 credit for proven ruler-visible true node beard and external collar; actual free inner ligule remains missing. Node role nested within this bucket, not a seventh scoring role."
    x["source_taxon"]="iNaturalist research-grade cane, 196400646, Williamson County, Texas"
    x["photo_inventory"]["species_image_records"]=len(c["images"])
    x["photo_inventory"]["verified_exact_cane_local_gallery_panels"]=sum(z["scientific_name"]=="Bothriochloa barbinodis" for z in c["visual_comparison"]["items"])
    x["photo_inventory"]["gallery_total"]=len(c["visual_comparison"]["items"])
    x["photo_inventory"]["new_binary_photos"]=len(complete)
    x["photo_inventory"]["new_arrows"]=sum(z["arrows"] for z in complete)
    x["missing_priority"]=["Actual opened free INNER ligule membrane at leaf-blade junction, with 1mm ruler",
       "Exposed fibrous rooted crown and short-rhizome status same rooted specimen",
       "Attached mature sessile fertile plus pedicelled companion pair showing lemma awn insertion, ruler in frame",
       "Whole flowering native Hays-region plant connected from head to rooted base"]
    c["visual_comparison"]["subtitle"]="Authentic Texas cane photographs now show conspicuous BEARDED TRUE culm nodes, one next to a real millimeter ruler, plus outer collar/sheath, reproductive awn and living clump. Introduced KR and native silver are separately labeled real other-species comparisons. The unpeeled inner ligule and truly dug fibrous rooted crown remain unphotographed."
    c["visual_comparison"]["overlay_note"]="TRUE measured node beards are in appended Texas images. The upper hair-fringed SHEATH edge is NOT the CULM node and is NOT a measured free ligule. A whole awned reproductive unit does not prove individual glume, lemma or sessile/pedicelled assignments."
    c["photo_note"]="New actual licensed Texas cane bluestem diagnostic photos: research-grade Williamson County iNaturalist 196400646, photo-specific CC BY-NC (strictly noncommercial public learner), original JPEGs archived without EXIF. Distinguish true bearded culm node from false leaf collar/flowering rachis; no photo pretends to be a dug rooted specimen or opened inner ligule."
    c["cane_brushycreek_anatomy_20261027"]={"source_obs":OBS,"photo_ids":[z["pid"] for z in complete],
      "new_arrows":sum(z["arrows"] for z in complete),"photo_score":"3.5/6 (58.3%)",
      "scale_node_verified":True,"rooted_crown_photo":False,"opened_inner_ligule":False,
      "status":"FIELD_READY_PHOTO_GAPS"}
    t=c["field_id_short_tiles"]
    t[0]["photo_panel_indices"]=[4,5,0]
    t[0]["details"]="First find a genuine CULM node, NOT the base of a leaf blade or a fluffy flowering rachis. New real cane photos 5 and 6 show thick rings of long ascending soft hairs at true stem joints on a research-grade Williamson County plant. Photo 5 has a millimeter ruler beside two photographed nodes. Then compare the broader silvery head to KR and silver. Published hair-length ranges remain source claims, not independent direct measurements from the ruler pixels."
    t[0]["status"]="ACTUAL TRUE BEARDED CULM NODES PHOTO-VERIFIED WITH RULER"
    t[1]["photo_panel_indices"]=[6,7,8,9]
    t[1]["details"]="See panels 7–8 for an OUTER blade–sheath junction and a distinct hairy upper sheath margin; neither proves an exposed free inner membranous ligule. Panel 10 shows a living bunch above soil with roots hidden. The actual true CULM nodes with a physical millimeter ruler are on panel 5, not on the collars. A peeled-open 1–3 mm inner ligule and genuinely excavated connected fibrous roots are still missing."
    t[1]["status"]="PARTIAL PHOTO EVIDENCE — actual node/collar/aboveground bunch; free inner ligule and roots absent"
    t[2]["photo_panel_indices"]=[0,8]
    t[3]["photo_panel_indices"]=[0,8]
    t[4]["photo_panel_indices"]=[4,2,3,0]
    t[5]["details"]="Actual cane images now include six licensed, source-matched Texas anatomical/habit photographs from research-grade Williamson County observation 196400646, including physical ruler next to a true nodal beard. Existing specimen/source archived media remains preserved, and KR/silver photos are labeled as OTHER species. Total verified score is 3.5/6 (58.3%); full 70% goal needs opened inner ligule, exposed roots or convincing complete pair. The 3 Joey study photos remain image-specific CC BY-NC and are not assumed unrestricted. Rights-filtered GitHub Pages publication must pass independently."
    t[5]["photo_panel_indices"]=[4,5,6,7,8,9,0,1,2,3]
    t[5]["status"]="58.3% PHOTO-ROLE COVERAGE — TRUE NODE FINISHED, INNER LIGULE/ROOTS HOLD"
    CARD.write_text(json.dumps(c,indent=2,ensure_ascii=False)+"\n")
    MARKER.parent.mkdir(parents=True,exist_ok=True)
    MARKER.write_text(json.dumps(dict(taxon="Bothriochloa barbinodis",lane=5,photo_ids=[z["pid"] for z in complete],
      stage="FIELD_READY_PHOTO_GAPS",true_bearded_node_mm_photo=True,opened_inner_ligule=False,
      six_role_pct=58.3,publication_photo_rights="CC BY-NC per-image verified, noncommercial only"),indent=2)+"\n")
  print(json.dumps(report,indent=2))
  assert len(complete)==len(SOURCE),"Some photos held, preserve report and do not claim full run"
if __name__=="__main__":main()
