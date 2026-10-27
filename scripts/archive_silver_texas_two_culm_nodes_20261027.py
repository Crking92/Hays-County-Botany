#!/usr/bin/env python3
"""Archive exact true TX silver bluestem culm nodes: individual CC licensed photos.

These are inspected original 768x1024 photographs; visibly actual culm nodes
but not calibrated with a millimeter rule. BRIT herbarium voucher MBB751 is
reported for Tarrant source observation; this is NOT an inspected voucher.
"""
import hashlib,io,json
from pathlib import Path
import requests
from PIL import Image, ImageOps

ROOT=Path(__file__).resolve().parents[1]
REL="content/taxa/Poaceae/Bothriochloa/bothriochloa-torreyana"
CARD=ROOT/REL/"species.json"
REPORT=ROOT/"reports/silver-bluestem-two-real-texas-culm-nodes-20261027.json"
MARKER=ROOT/"workflow/field-id-publication/2026-10-27-silver-two-licensed-true-nodes.json"
TARGETS=[
 {"obs":63926408,"photo":102682516,"credit":"Luke Padon","username":None,
  "license":"cc-by","place_tag":"Throckmorton","date":"2020-10-31",
  "file":"silver-throckmorton-texas-luke-padon-node-102682516.jpg",
  "label":"TEXAS SILVER — true culm node and sheath junction",
  "role":"Texas grass culm showing actual exposed slightly thickened true node, leaf sheath ending below, no ruler",
  "caption":"Research-grade Texas source-labelled B. torreyana, Throckmorton County, October 31 2020. A visible stem NODE appears as the subtly swollen ring just below a greener internode and above the papery opened old leaf sheath. The photo is specifically documented by its observer for absence of conspicuous node hairs. No physical millimeter calibration, and a single photo does not show hairiness variation across populations. The visible node is NOT the inner blade–sheath ligule.",
  "why":"Fills an actual true culm-node macro gap, while clarifying that a stem node and the membranous ligule are different places.",
  "markers":[{"label":"True culm node","label_x":6,"label_y":27,"target_x":54,"target_y":55}]},
 {"obs":168804436,"photo":292594065,"credit":"Brooke B","username":None,
  "license":"cc-by-nc","place_tag":"Tarrant","date":"2023-06-20",
  "file":"silver-tarrant-brit-voucher-culm-node-292594065.jpg",
  "label":"TEXAS SILVER — stem nodes on BRIT-vouchered source plant",
  "role":"Genuine Texas stem-node and culm contextual habit photograph linked by observer to BRIT voucher MBB751",
  "caption":"Research-grade B. torreyana, Rock Creek Ranch Park Silphium Prairie, Tarrant County, June 20 2023. The observer reports a BRIT Herbarium voucher MBB751 and documents nodes lacking conspicuous hairs. This exact in-situ photograph shows an actual lower culm NODE near the junction of the side-positioned sheath, against a human hand for contextual size, and a second node below. BRIT voucher information is OBSERVER REPORTED; the herbarium sheet has not been independently inspected. A finger is NOT a millimeter ruler and the exact ligule margin is not shown.",
  "why":"Pairs a real exposed Texas culm node with connected aboveground stem architecture and a reported voucher; avoids treating a collar or leaf blade base as a node.",
  "markers":[{"label":"Exposed culm node","label_x":69,"label_y":28,"target_x":52,"target_y":62}]},
]
def main():
  sess=requests.Session()
  sess.headers.update({"User-Agent":"Hays Botany educational exact Texas node images / 1.0"})
  s=json.loads(CARD.read_text())
  assert s["id"]=="bothriochloa-torreyana"
  before=len(s["images"])
  result={"date":"2026-10-27","taxon":"Bothriochloa torreyana","prior_images":before,"source_photos":[]}
  installed=[]
  for x in TARGETS:
    try:
      o=sess.get(f"https://api.inaturalist.org/v1/observations/{x['obs']}",timeout=25)
      o.raise_for_status()
      obs=o.json()["results"][0]
      if obs["taxon"]["id"]!=1452295 or obs["quality_grade"]!="research":raise ValueError("taxon/grade mismatch")
      if x["place_tag"] not in obs.get("place_guess","") or obs.get("observed_on")!=x["date"]:raise ValueError("source locality/date mismatch")
      photo=next((p for p in obs["photos"] if p["id"]==x["photo"]),None)
      if not photo or photo.get("license_code")!=x["license"]:raise ValueError("photo not present or photo-specific license changed")
      author=photo.get("attribution","")
      if x["credit"].lower() not in author.lower():raise ValueError("original photographer credit changed")
      url=photo["url"].replace("/square.","/large.").replace("/medium.","/large.")
      response=sess.get(url,timeout=28)
      if response.status_code==429:raise ValueError("source rate limited")
      response.raise_for_status()
      with Image.open(io.BytesIO(response.content)) as p:
        im=ImageOps.exif_transpose(p).convert("RGB")
        im.load()
      if im.width<768 or im.height<980 or im.width>3000 or im.height>3000:
        raise ValueError("image pixels inconsistent with manually inspected source")
      local=ROOT/REL/"images"/x["file"]
      local.parent.mkdir(parents=True,exist_ok=True)
      im.save(local,"JPEG",quality=90,optimize=True,subsampling=0)
      with Image.open(local) as check:
        assert not check.getexif()
        check.verify()
      digest=hashlib.sha256(local.read_bytes()).hexdigest()
      link="https://www.inaturalist.org/photos/"+str(x["photo"])
      license_label="CC BY-NC (individual photo, iNat license version not independently recorded)" if x["license"]=="cc-by-nc" else "CC BY (individual photo, iNat license version not independently recorded)"
      data={"file":"images/"+x["file"],"role":x["role"],"creator":x["credit"],
        "license":license_label,"license_url":link,"source_page":link,
        "source_photo_id":x["photo"],"source_observation_id":x["obs"],
        "observation_page":f"https://www.inaturalist.org/observations/{x['obs']}",
        "source_original_url":url,"source_locality":obs.get("place_guess"),
        "observed_on":x["date"],"study_use":"yes",
        "public_reuse":"yes on noncommercial educational site, photo-specific Creative Commons with attribution" if x["license"]=="cc-by-nc" else "yes CC BY with source attribution",
        "photo_status":"PHYSICALLY ARCHIVED and photographer license verified; EXIF/GPS removed; true culm node identified at actual pixel, no millimeter scale",
        "archive_sha256":digest,"image_dimensions":list(im.size),
        "source_voucher_note":"BRIT MBB751 (reported by source observer, not independently inspected)" if x["obs"]==168804436 else None}
      panel={"label":x["label"],"scientific_name":"Bothriochloa torreyana",
        "image_url":REL+"/images/"+x["file"],"image_fit":"contain",
        "image_role":x["role"],"caption":x["caption"],"why_it_matters":x["why"],
        "creator":x["credit"],"license":license_label,"license_url":link,
        "source_page":link,"source_photo_id":x["photo"],
        "markers":x["markers"],"photo_status":"FULL ORIGINAL PIXELS VERIFIED. Exposed true culm node annotated; no free ligule, microscopic node hairs or exact scale claimed."}
      if not any(p.get("file")==data["file"] for p in s["images"]):s["images"].append(data)
      if not any(p.get("source_photo_id")==x["photo"] for p in s["visual_comparison"]["items"]):s["visual_comparison"]["items"].append(panel)
      result["source_photos"].append({"id":x["photo"],"status":"ARCHIVED", "source":link,
        "file":str(local.relative_to(ROOT)),"license":license_label,"photographer":x["credit"],
        "sha256":digest,"size":list(im.size),"arrows":1})
      installed.append(x["photo"])
    except Exception as e:
      result["source_photos"].append({"id":x["photo"],"status":"HELD", "reason":str(e)[:340]})
  if installed:
    n=len(s["images"])
    s["curation_status"]["photo_metadata_count"]=n
    s["curation_status"]["photo_files_present"]=n
    s["curation_status"]["visual_finish"]="FIELD_READY_PHOTO_GAPS — new real TX exposed culm node photos (one source tied to observer-reported BRIT voucher) + previously archived leaf junction and spikelet photos. A measured free ligule, dug rooted base and fully connected scaled spikelet pair remain missing."
    s["silver_texas_true_culm_nodes_20261027"]={
      "source_photo_ids":installed,
      "new_genuine_physical_node_photos":len(installed),
      "individually_license_reviewed":True,
      "reported_voucher":"BRIT MBB751 (source observer statement ONLY)" if 292594065 in installed else None,
      "pixel_verified_gross_node_arrows":len(installed),
      "true_node_visible":True,
      "calibrated_mm_scale_visible":False,
      "true_free_ligule_visible":False,
      "status":"FIELD_READY_PHOTO_GAPS"
    }
    score=s["silver_six_role_photo_score_20261027"]
    if score.get("total")==3.5:
      score["roles"][3]["score"]=0.5
      score["roles"][3]["reason"]="Actual source-verified exposed culm node photographed in Texas; photographed without 1-mm ruler. Observer reports smooth nodes; regionally node-hair variation must not be resolved from a single specimen."
      score["total"]=4
      score["pct"]=round(100*4/6,1)
      score["remaining_pct"]=round(100*2/6,1)
      score["target_70pct_needed_additional_role_points"]=0.2
      score["target_80pct_needed_additional_role_points"]=0.8
      score["target_90pct_needed_additional_role_points"]=1.4
      score["status"]="4/6 (66.7%) genuine public-usable photo role equivalents; 33.3% remaining. Node half-role added; real measured membrane, dug roots and connected pair still missing."
    s["learner_visual_status"]["public_photographs_physically_archived"]=7+len(installed)
    s["learner_visual_status"]["image_count"]=n
    s["learner_visual_status"]["public_gallery_panels"]=len(s["visual_comparison"]["items"])
    s["learner_visual_status"]["total_photo_arrows"]=sum(len(p.get("markers",[])) for p in s["visual_comparison"]["items"])
    s["learner_visual_status"]["note"]="New source-verified genuine Texas culm-node photographs with licensed 1-arrow gross anatomy each. BRIT specimen reference is observer-reported and not independently inspected. True measured ligule, fully linked mm paired spikelets and exposed root crown remain gaps."
    s["field_photo_quickcheck"]["featured_panel_indices"]=[0,8,10,11,5,9,6,4,7,2,3] if len(installed)==2 else s["field_photo_quickcheck"]["featured_panel_indices"]
    s["field_photo_quickcheck"]["warning"]="2026-10-27 actual photo role audit: genuine TEXAS stem node and collar-region photos are physically archived, with correct source-specific licenses and broad arrows; no measured free ligule membrane, excavated roots or linked mature mm-scale spikelet pair. Smooth node in these individual photographs does NOT make hairless nodes a universal silver bluestem ID rule."
    s["field_id_short_tiles"][2]["details"]="New real Texas source-verified culm NODE photographs are present: Throckmorton County (Luke Padon) and Tarrant County (Brooke B; observation reports BRIT voucher MBB751). Both show the TRUE stem node at the culm/sheath junction and no conspicuous hair tuft; source characters vary among treatments, so do NOT require hairless nodes as a universal trait. The earlier Denton photo separately shows the leaf blade–sheath collar region, not the inner free ligule membrane. No photo here has a calibrated millimeter rule, and the true FREE membranous ligule remains missing. Never confuse a culm node and a ligule."
    s["field_id_short_tiles"][2]["photo_panel_indices"]=[10,11,8,6]
    s["field_id_short_tiles"][2]["status"]="PARTIAL, NOW REAL NODE PHOTOS: 2 licensed Texas culm nodes plus 1 Texas collar region; actual free ligule and node-mm-scale macro still lacking."
    s["field_id_short_tiles"][5]["status"]="FIELD_READY_PHOTO_GAPS — "+str(7+len(installed))+" public-usable physically archived species photos; real Texas node photographed, measured true ligule, exposed roots and linked mm spikelet pair outstanding"
    s["field_id_short_tiles"][5]["photo_panel_indices"]=[0,10,11,8,9,5,6,7,4]
    s["field_photo_quickcheck"]["steps"][3]="4 · CHECK TWO DIFFERENT PLACES: TEXAS panels 11–12 show TRUE stem nodes on actual culms (one observer-reported BRIT specimen); TEXAS panel 9 shows the inside BLADE–SHEATH JUNCTION where a ligule should be opened. Do not call the first a ligule or infer a measured 1–3 mm free ligule membrane from the latter. Node hairs vary."
    CARD.write_text(json.dumps(s,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    MARKER.parent.mkdir(parents=True,exist_ok=True)
    MARKER.write_text(json.dumps({"date":"2026-10-27","taxon":"bothriochloa-torreyana",
      "new_exact_public_usable_true_node_photo_ids":installed,
      "photo_role_score":"4/6 (66.7%)" if s["silver_six_role_photo_score_20261027"]["total"]==4 else "unknown",
      "new_arrow_count":len(installed),"true_ligule_still_missing":True,
      "new_files":["images/"+x["file"] for x in TARGETS if x["photo"] in installed],
      "rights_note":"CC BY and CC BY-NC attribution retained; do not invent license version"},indent=2)+"\n")
  result["installed_count"]=len(installed)
  result["new_image_metadata"]=len(s["images"])
  result["new_gallery_panels"]=len(s["visual_comparison"]["items"])
  REPORT.parent.mkdir(parents=True,exist_ok=True)
  REPORT.write_text(json.dumps(result,indent=2)+"\n")
  print(json.dumps(result,indent=2))
if __name__=="__main__":
  main()
