#!/usr/bin/env python3
"""Promote two individually licensed, visually inspected Gulf reed photographs.
One-time gallery change; source iNaturalist ID remains provisional, never genotype.
"""
import hashlib,json,shutil
from pathlib import Path
from PIL import Image
ROOT=Path("content/taxa/Poaceae/Phragmites/phragmites-australis")
FILE=ROOT/"species.json"
SCOUT=Path("reports/phragmites-gulf-photo-scout-20261026.json")
AUDIT=Path("reports/phragmites-gulf-verified-gallery-additions-20261026.json")
SELECTION=[
  {"obs":133905064,"photo":228158714,"dst":"gulf-josh-teyler-outer-sheath-228158714.jpg",
   "role":"Source-identified Gulf Coast reed: connected mature green culm with numerous attached leaf blades and outer leaf sheaths at the nodes; inner ligule NOT visible.",
   "label":"GULF COAST — living culm, leaf sheath and blade attachment (not true ligule)",
   "caption":"Josh Teyler's research-grade iNaturalist observation from Pensacola, Florida, identifies this reed as subsp. berlandieri. The source photo visibly shows the outer culm, several nodes and the encircling leaf sheaths where blades arise. The inner membranous ligule is NOT opened, exposed, measured or established in this photograph. No voucher/genotype or Hays County provenance.",
   "why":"Specific Gulf-coast source reference of actual connected culm and leaf sheaths, not an isolated leaf or distant stand.",
   "markers":[
     {"label":"Outer sheath wrapping culm","label_x":4,"label_y":85,"target_x":49,"target_y":82},
     {"label":"Leaf blade","label_x":78,"label_y":29,"target_x":76,"target_y":20}
   ]},
  {"obs":98558182,"photo":164109246,"dst":"gulf-james-douglass-attached-panicle-164109246.jpg",
   "role":"Source-identified Gulf Coast reed: close attached branching flowering panicle beside blade. Macro spikelet glumes and ligule remain unmeasured.",
   "label":"GULF COAST — closer flowering panicle and supporting leaf",
   "caption":"James G. Douglass's research-grade source-described Gulf Coast reed from Bonita Springs, Florida: real branched panicle held by a hand for general scale, with leaves visible. It demonstrates attached flowering architecture, NOT glume lengths, inner ligules or independent lineage/genotype proof.",
   "why":"Separate Gulf provenance of actual branched flowering architecture; improves source-specific comparison beyond a distant dry stand.",
   "markers":[
     {"label":"Branched flowering panicle","label_x":63,"label_y":69,"target_x":57,"target_y":47}
   ]}
]
def main():
  d=json.loads(FILE.read_text())
  audit=json.loads(SCOUT.read_text())
  candidates={(x["observation_id"],x["photo_id"]):x for x in audit.get("candidate_images",[])}
  selected=[]
  for it in SELECTION:
    md=candidates[(it["obs"],it["photo"])]
    assert md["license_code"]=="cc-by-nc" and md["grade"]=="research"
    assert md["taxon"].startswith("Phragmites australis") and "berlandieri" in md["taxon"]
    assert md["creator"] and md["source_observation_url"]
    src=Path(md["image_path"])
    assert src.is_file() and hashlib.sha256(src.read_bytes()).hexdigest()==md["sha256"]
    with Image.open(src) as img:
      img.verify()
    with Image.open(src) as img:
      assert min(img.size)>=500
    selected.append((it,md,src))
  new_photos=[]
  for it,md,src in selected:
    name="images/"+it["dst"]
    gallery_rel="content/taxa/Poaceae/Phragmites/phragmites-australis/"+name
    dest=ROOT/name
    if not dest.exists():shutil.copy2(src,dest)
    assert hashlib.sha256(dest.read_bytes()).hexdigest()==md["sha256"]
    existing=any(im.get("file")==name for im in d["images"])
    if existing:
      existing_panel=next((i for i,p in enumerate(d["visual_comparison"]["items"]) if p.get("image_url")==gallery_rel),None)
      if existing_panel is None:raise ValueError("Source image recorded but panel absent")
      new_photos.append({"photo_id":it["photo"],"status":"ALREADY_INSTALLED","panel_index":existing_panel})
      continue
    im={"file":name,"role":it["role"],"creator":md["creator"],"license":md["license"],
        "license_url":md["license_url"],"source_page":md["source_observation_url"],
        "individual_photo_page":md["source_photo_url"],
        "source_taxon_name":md["taxon"],"source_location":md["location"],
        "source_id_method":"Current iNaturalist research-grade identification ONLY, no voucher/molecular lineage confirmation",
        "source_observation_id":md["observation_id"],"source_photo_id":md["photo_id"],
        "archived_sha256":md["sha256"],
        "archived_dimensions":md["saved_size"],
        "modifications":"Derived RGB JPEG for public site; original EXIF/location stripped; client-side gross structure labels are separate",
        "public_reuse":"Individually verified CC BY-NC 4.0; only for current genuinely noncommercial public educational learner; preserve exact creator credit and link; new commercial use requires rights review",
        "photo_status":"LOCAL BYTES VERIFIED / PIXEL INSPECTED / GROSS STRUCTURE TEACHING ONLY",
        "lineage_caution":"Research-grade source determination is not a genotype or independently vouchered Texas lineage"}
    d["images"].append(im)
    panel={"label":it["label"],"scientific_name":"Phragmites australis subsp. berlandieri",
          "image_url":gallery_rel,"image_fit":"contain","image_role":it["role"],
          "caption":it["caption"],"why_it_matters":it["why"],
          "creator":md["creator"],"license":md["license"],"license_url":md["license_url"],
          "source_page":md["source_observation_url"],"individual_photo_page":md["source_photo_url"],
          "markers":it["markers"],
          "photo_status":"PIXEL REVIEWED 2026-10-26: arrows target gross visible sheath/blade or panicle; NOT true inner ligule, glume or measured lineage"}
    d["visual_comparison"]["items"].append(panel)
    idx=len(d["visual_comparison"]["items"])-1
    for row in d.get("field_id_short_tiles",[]):
      if row["heading"].startswith("02 ·") or (it["photo"]==228158714 and row["heading"].startswith(("03 ·","04 ·"))) or (it["photo"]==164109246 and row["heading"].startswith("01 ·")):
        row.setdefault("photo_panel_indices",[]).append(idx)
    d["field_photo_quickcheck"].setdefault("featured_photo_indices",[]).append(idx)
    if it["photo"]==228158714:
      ref=d["lineage_photo_readiness_20261026"]["gulf_reference"]
      ref.setdefault("existing_panels",[]).append(idx)
      ref["description"]+=" PLUS Pensacola research-grade CC BY-NC photograph of actual externally visible attached sheath and culm. No opened inner ligule, measured glume or genotype."
      d["three_lineage_photo_lesson_20261026"]["lineage_columns"][2].setdefault("documented_source_photos",[]).append(idx)
      d["three_lineage_photo_lesson_20261026"]["photo_panels"]["gulf_outer_sheath_source_only"]=idx
    else:
      d["lineage_photo_readiness_20261026"]["gulf_reference"].setdefault("existing_panels",[]).append(idx)
      d["three_lineage_photo_lesson_20261026"]["lineage_columns"][2].setdefault("documented_source_photos",[]).append(idx)
      d["three_lineage_photo_lesson_20261026"]["photo_panels"]["gulf_flowering_architecture_source_only"]=idx
    new_photos.append({"photo_id":it["photo"],"panel_index":idx,"file":str(dest),"markers":len(it["markers"]),"license":md["license"]})
  d["curation_status"]["photo_metadata_count"]=len(d["images"])
  d["curation_status"]["photo_files_present"]=len(d["images"])
  d["curation_status"]["genus_photo_panels"]=len(d["visual_comparison"]["items"])
  totalmarkers=sum(len(p.get("markers",[])) for p in d["visual_comparison"]["items"])
  d["curation_status"]["visible_gross_structure_arrows"]=totalmarkers
  d["field_id_finish_pass"]["visible_structure_arrows"]=totalmarkers
  d["visual_comparison"]["subtitle"]=f"{len(d['visual_comparison']['items'])} teaching panels: native americanus, introduced australis and source-identified Gulf berlandieri, now including actual Gulf external sheath/culm and attached flowering reference photographs. Source names do not prove Texas population lineage."
  d["photo_note"]=f"{len(d['images'])} individually licensed physical photographs, {len(d['visual_comparison']['items'])} teaching panels and {totalmarkers} visible organ arrows. New Gulf sources from Florida show external sheath/culm and attached panicle, NOT exposed true inner ligule nor calibrated lineage glumes. Subspecies not confirmed by DNA."
  d["phragmites_gulf_source_photos_20261026"]={
    "status":"PUBLIC NONCOMMERCIAL SOURCE-PROVISIONAL; OUTER SHEATH and PANICLE PHOTO ROLES INSTALLED",
    "archive_count_new":len([p for p in new_photos if p.get("file")]),
    "panels":new_photos,
    "remaining":"True OPEN inner ligule with 1-mm scale on independently determined Gulf lineage; mature lower/upper glumes; age-marked same-site sheath; expert voucher/haplotype where warranted",
    "rights":"individual CC BY-NC 4.0 permits genuinely noncommercial educational website use, requires credit/source and revisiting if monetized",
    "locality_warning":"All examples Florida, not Hays County or Texas"
  }
  FILE.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
  AUDIT.write_text(json.dumps({
     "date":"2026-10-26","result":"SOURCE-GROUNDED GULF PHOTO PANELS INSTALLED; NO GENOTYPE CLAIM",
     "photo_additions":new_photos,
     "images":len(d["images"]),"panels":len(d["visual_comparison"]["items"]),"arrows":totalmarkers,
     "scientific_holds":["No actually measured inner ligule / mature paired glumes from independent confirmed Gulf specimen","No genotype or Texas voucher identity","Arrows only for visible gross anatomy"],
     "source_audit":"reports/phragmites-gulf-photo-scout-20261026.json"
  },indent=2)+"\n")
if __name__=="__main__":main()
