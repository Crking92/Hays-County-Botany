#!/usr/bin/env python3
"""Promote two source-verified, pixel-reviewed actual Phalaris caroliniana anatomy photos.

Conservative arrows target visible joints/membranes; preserve old science and rights.
"""
import csv, hashlib, io, json, pathlib, shutil, urllib.request
from PIL import Image
R=pathlib.Path("reports/lane5-phalaris-photo-scout-20261027")
T=pathlib.Path("content/taxa/Poaceae/Phalaris/phalaris-caroliniana")
S=T/"species.json";L=T/"image-sources.csv"
O=pathlib.Path("reports/lane5-phalaris-two-actual-cc0-anatomy-20261027.json")
d=json.loads(S.read_text(encoding="utf-8"))
assert d["id"]=="phalaris-caroliniana"
review=json.loads((R/"detail-review-manifest.json").read_text())
sources={x["photo_id"]:x for x in review["items"] if x["status"]=="REVIEW_ONLY_ARCHIVED"}
specs=[
 {"photo":"643034634",
  "name":"texas-cc0-phalaris-caroliniana-true-culm-node-643034634.jpg",
  "label":"REAL CULM NODE — actual stem joint above and below green internodes",
  "role":"Actual source-identified Phalaris caroliniana node showing a distinct pale-purple, slightly swollen circumferential joint between two connected green culm internodes; NOT leaf collar/ligule or rooting node.",
  "caption":"An actual same-species, CC0 Texas close-up of a cylindrical stem, conspicuous banded joint and adjoining internodes. This is a true culm node, NOT an inner leaf ligule. No roots grow from this pictured joint.",
  "why":"Allows the crew to separate a true stem NODE from the leaf blade–sheath junction that houses the ligule. A colored band on a culm is not proof of a rhizome.",
  "markers":[
   {"label":"Visible culm node — stem joint","label_x":5,"label_y":31,"target_x":46,"target_y":45},
   {"label":"Green culm internode","label_x":64,"label_y":77,"target_x":42,"target_y":69}],
  "tiles":[1]},
 {"photo":"643034675",
  "name":"texas-cc0-phalaris-caroliniana-exposed-inner-collar-643034675.jpg",
  "label":"INNER COLLAR PHOTO — real translucent membrane at blade–sheath junction",
  "role":"Actual photographed source-identified Phalaris caroliniana blade/sheath attachment with a translucent inner tissue flap and unfolded leaf blade. Visible inner pale tissue is real, but its exact free ligule edge/length is NOT independently established or measured.",
  "caption":"A Texas grass leaf deliberately held open so the blade, overlapping green sheath and pale translucent inner collar tissue can be inspected. The visible whitish flap is in the correct ligular region, but is not a fully spread or 1-mm-calibrated ligule measurement. Do not interpret the entire sheath margin as the ligule.",
  "why":"Much clearer practical anatomy than an ordinary head view: shows where to open the leaf to look for the true membranous ligule. Species ID and ligule dimensions still require the complete plant and measured dissection.",
  "markers":[
   {"label":"Exposed pale inner collar tissue","label_x":4,"label_y":39,"target_x":44,"target_y":53},
   {"label":"Leaf blade","label_x":76,"label_y":13,"target_x":72,"target_y":37}],
  "tiles":[4]}
]
def fetch(u):
 req=urllib.request.Request(u,headers={"User-Agent":"HaysCountyBotanyBotanicalPhotoArchive/1.0"})
 with urllib.request.urlopen(req,timeout=40) as resp:return resp.read()
done=[]
for spec in specs:
 pid=spec["photo"];source=sources[pid]
 assert source["license"]=="cc0" and source["sha256"] and source["source_page"].endswith(pid)
 obj=json.loads(fetch("https://api.inaturalist.org/v1/observations/"+source["source_observation"].rsplit("/",1)[-1]))
 obs=next((x for x in obj.get("results",[]) if str(x["id"])==source["source_observation"].rsplit("/",1)[-1]),None)
 assert obs and (obs.get("taxon") or {}).get("name")=="Phalaris caroliniana" and obs.get("quality_grade")=="research"
 photo=next((x for x in obs.get("photos",[]) if str(x.get("id"))==pid),None)
 assert photo and (photo.get("license_code") or "").lower().replace("_","-")=="cc0", "Individual photo CC0 rights changed"
 rawpath=R/("review-original-"+pid+".jpg")
 raw=rawpath.read_bytes()
 assert hashlib.sha256(raw).hexdigest()==source["sha256"], "Candidate byte integrity mismatch"
 with Image.open(io.BytesIO(raw)) as img:
  img.verify()
 with Image.open(io.BytesIO(raw)) as img:
  assert min(img.size)>=1000
  assert not img.getexif() and not img.info.get("exif")
 rel="images/"+spec["name"];dest=T/rel
 if not dest.exists():shutil.copy2(rawpath,dest)
 assert dest.read_bytes()==raw
 if not any(x.get("source_page")==source["source_page"] for x in d["images"]):
  d["images"].append({
   "file":rel,"role":spec["role"],"creator":"iNaturalist photo contributor (recorded CC0)",
   "license":"CC0 1.0","license_url":"https://creativecommons.org/publicdomain/zero/1.0/",
   "source_page":source["source_page"],"source_observation":source["source_observation"],
   "source_photo_attribution":photo.get("attribution") or "no rights reserved",
   "place_reported":source["photo_region"],"source_taxon":"Phalaris caroliniana",
   "photo_grade":"iNaturalist Research Grade; exact species source; not independently vouchered",
   "photo_review":"Full-resolution real photo pixel-inspected before selection; precise microscopic ligule/glume detail NOT certified; no artificial botanically visible features added.",
   "public_reuse":"Photo-level CC0 recorded and rechecked; original pixel data re-encoded, EXIF/GPS stripped.",
   "sha256":source["sha256"],"pixels":source["pixel_dimensions"],
   "photo_status":"FIELD_READY_PHOTO_GAPS — locally archived authentic vegetative anatomical photograph"
  })
 panelidx=next((i for i,p in enumerate(d["visual_comparison"]["items"]) if p.get("source_page")==source["source_page"]),None)
 if panelidx is None:
  panelidx=len(d["visual_comparison"]["items"])
  d["visual_comparison"]["items"].append({
   "label":spec["label"],"scientific_name":"Phalaris caroliniana",
   "image_url":(T/rel).as_posix(),"image_fit":"contain",
   "image_role":spec["role"],"caption":spec["caption"],"why_it_matters":spec["why"],
   "creator":"iNaturalist photo contributor (recorded CC0)","license":"CC0 1.0",
   "license_url":"https://creativecommons.org/publicdomain/zero/1.0/",
   "source_page":source["source_page"],"source_observation":source["source_observation"],
   "markers":spec["markers"],
   "modifications":"EXIF/GPS stripped from local review copy; browser-only annotation overlays",
   "photo_status":"Exact source and full-resolution visible structure verified. No actual root crown or measured free ligule margin shown."
  })
 for ti in spec["tiles"]:
  idxs=d["field_id_short_tiles"][ti].setdefault("photo_panel_indices",[])
  if panelidx not in idxs:idxs.append(panelidx)
 done.append({"photo_id":pid,"stored":rel,"panel":panelidx,"license":"CC0 1.0",
    "source":source["source_page"],"pixel_shown_role":spec["role"],"arrows":len(spec["markers"])})
assert len(done)==2
d["curation_status"]["photo_metadata_count"]=len(d["images"])
d["curation_status"]["photo_files_present"]=len(d["images"])
d["curation_status"]["visual_photo_panels"]=len(d["visual_comparison"]["items"])
d["curation_status"]["visual_finish"]=(
 "FIELD_READY_PHOTO_GAPS — two new CC0 source-determined Texas anatomy photos: actual exposed inner blade/sheath transition and true culm node. No exposed connected fibrous root crown or individually measured two sterile lemmas. Existing source-specific Bob Harms photo rights not broadened.")
d["learner_visual_status"]["image_count"]=len(d["images"])
d["learner_visual_status"]["status"]="field_ready_photo_gaps"
d["learner_visual_status"]["note"]=(
 "8 archived same-species real photos and 8 same-species Learner panels, plus one explicitly DIFFERENT species P. minor comparison panel. Two newly archived Texas CC0 anatomical macro photographs are an external true culm node and exposed inner blade/sheath collar tissue. Do NOT treat partial pale tissue as a measured ligule free edge. Two reduced sterile lemmas and real exposed fibrous roots remain unphotographed. Pages live status not confirmed.")
d["lane5_phalaris_two_cc0_anatomy_20261027"]={
 "status":"FIELD_READY_PHOTO_GAPS","two_new_exact_photos":done,
 "true_inner_ligule_status":"PARTIAL — tissue at junction photographed but free membrane fully spread and measured remains absent",
 "rooted_crown_status":"MISSING — no root photo installed",
 "spikelet_status":"PARTIAL — fertile vs both sterile lemmas not separately verified",
 "new_arrows":4,"source_rights":"Two CC0 originals; historical copyrighted/NC sources unchanged",
 "public_site":"NEEDS_PUBLICATION_READBACK"}
S.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
with L.open(newline="",encoding="utf-8") as f:
 reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
existing={x["file_name"] for x in rows}
for x in done:
 basename=pathlib.Path(x["stored"]).name
 if basename in existing:continue
 row={k:"" for k in fields}
 for k,v in {"file_name":basename,"role":x["pixel_shown_role"],"creator":"iNaturalist photo contributor (recorded CC0)",
  "license":"CC0 1.0","source_page":x["source"],
  "direct_url":next(p["file"] for p in review["items"] if p["photo_id"]==x["photo_id"]),
  "study_use":"Visually checked exact species field anatomy","public_reuse":"Open CC0, copy was EXIF stripped"}.items():
  if k in row:row[k]=v
 rows.append(row);existing.add(basename)
with L.open("w",newline="",encoding="utf-8") as f:
 writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
O.write_text(json.dumps({"date":"2026-10-27","status":"FIELD_READY_PHOTO_GAPS",
 "stored_same_species":len(d["images"]),"gallery_total":len(d["visual_comparison"]["items"]),
 "new":done,"remaining":["Real rooted same-plant crown","Fully exposed measured true free ligule","Two sterile florets separately identified and calibrated","Public Pages deployment QA"]},indent=2)+"\n")
print(json.dumps({"new":done,"physical_species_photos":len(d["images"]),"gallery_panels":len(d["visual_comparison"]["items"])}))
