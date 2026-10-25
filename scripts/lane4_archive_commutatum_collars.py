#!/usr/bin/env python3
"""Archive two individually verified CC BY 4.0 photographs of D. commutatum.

On live GitHub Actions download the ORIGINAL JPEG and check its published SHA-1
against its source-file record. If Commons changes an original, hold rather than
guess. Preserve all other species-card work. EXIF/GPS metadata is discarded.
"""
import hashlib
import io
import json
import pathlib
import time
import urllib.request
from PIL import Image, ImageOps

repo_root = pathlib.Path(".")
species = pathlib.Path("content/taxa/Poaceae/Dichanthelium/dichanthelium-commutatum")
path = species / "species.json"
card = json.loads(path.read_text(encoding="utf-8"))
assert card["id"] == "dichanthelium-commutatum"
assert card["field_id_finish_pass"]["stage"] == "FIELD_READY_PHOTO_GAPS"

# The Commons source pages were examined individually on 2026-10-25. Both
# identify Alex Abair, the species and CC BY 4.0, with the original file SHA-1.
files = [
    {
      "id": "363938843",
      "url": "https://upload.wikimedia.org/wikipedia/commons/d/da/Dichanthelium_commutatum_363938843.jpg",
      "sha1": "6c4dd7676aff4e0bf8b0c1389b99e7b6c5c6e0ce",
      "role": "Natural leaf/sheath junction, long hairs along the collar and sheath margins; true inner membranous/hair ligule edge not separately identified or measured",
      "label": "Variable panicgrass — leaf sheath hairs and blade junction",
      "caption": "Alex Abair's actual macro resolves conspicuous hairs lining the sheath and leaf-attachment margins on an intact flowering culm. The narrow stem continues above the junction. This is NOT a calibrated 0.5-mm TRUE INNER ligule image: do not confuse outer sheath-margin hair tufts or cobweb filaments with the inner ligule.",
      "markers": [
         {"label":"Leaf/sheath junction","label_x":7,"label_y":58,"target_x":49,"target_y":55},
         {"label":"Hairs along sheath margin","label_x":74,"label_y":77,"target_x":41,"target_y":72},
         {"label":"Stem above attachment","label_x":72,"label_y":12,"target_x":52,"target_y":24}
      ],
      "why": "Locate the collar region to inspect under a hand lens; documentation of the visible hair placement, NOT proof of inner ligule dimensions."
    },
    {
      "id": "363938844",
      "url": "https://upload.wikimedia.org/wikipedia/commons/c/c8/Dichanthelium_commutatum_363938844.jpg",
      "sha1": "5f580bc141c616999796b250c8f045436a22f60b",
      "role": "Attached broad lanceolate blade with visible blade base at stem and tapering tip; exact cordate/clasping degree and true inner ligule remain unresolved",
      "label": "Variable panicgrass — broad attached stem blade",
      "caption": "This photographed leaf has a relatively broad lanceolate blade, acute tapering tip, and its base visibly attaching to the stem at the upper right. Fine parallel venation and subtle blade-edge texture are visible. DO NOT diagnose a measurable clasping/heart-shaped base or a 0.5-mm inner ligule from these exterior pixels alone.",
      "markers": [
         {"label":"Broad lanceolate blade","label_x":48,"label_y":8,"target_x":48,"target_y":38},
         {"label":"Blade base attaches to stem","label_x":64,"label_y":88,"target_x":90,"target_y":16},
         {"label":"Tapering blade tip","label_x":5,"label_y":75,"target_x":20,"target_y":73}
      ],
      "why": "Provides the missing real blade silhouette and point of stem attachment for comparison against slender-bladed Dichanthelium; verify the exact basal shape separately."
    }
]
headers={"User-Agent":"HaysCountyBotanyEducationalVisualLearner/1.0 (respectful credited photo archival)"}
report={"species":"dichanthelium-commutatum","license_basis":"Each exact Commons file page CC BY 4.0, author Alex Abair, matching known original SHA-1","added":[],"held":[],"date":"2026-10-25"}
for cand in files:
    dest_rel = "images/commons-abair-" + cand["id"] + ".jpg"
    dest = species / dest_rel
    source_page = "https://commons.wikimedia.org/wiki/File:Dichanthelium_commutatum_" + cand["id"] + ".jpg"
    if any(z.get("file")==dest_rel for z in card["images"]):
       report["held"].append({"id":cand["id"],"reason":"Already in canonical image metadata; duplicate skipped"})
       continue
    blob=None
    try:
       for trial in range(3):
           try:
               req=urllib.request.Request(cand["url"],headers=headers)
               with urllib.request.urlopen(req,timeout=40) as response:
                   blob=response.read(10_000_001)
                   if len(blob)>10_000_000: raise RuntimeError("Unreasonably large original")
               break
           except Exception:
               if trial==2: raise
               time.sleep(5*(trial+1))
       if hashlib.sha1(blob).hexdigest()!=cand["sha1"]:
           raise ValueError("SOURCE SHA-1 MISMATCH: hold rather than publish changed photo")
       img = Image.open(io.BytesIO(blob))
       img.verify()
       img = ImageOps.exif_transpose(Image.open(io.BytesIO(blob))).convert("RGB")
       if min(img.size)<900: raise ValueError("Photo too small for chosen macro role")
       if dest.exists(): raise ValueError("New path already has bytes, inspect first")
       dest.parent.mkdir(exist_ok=True,parents=True)
       img.save(dest,format="JPEG",quality=92,optimize=True)
       img_sha = hashlib.sha256(dest.read_bytes()).hexdigest()
       card["images"].append({
         "file":dest_rel,
         "role":cand["role"],
         "creator":"Alex Abair",
         "license":"CC BY 4.0",
         "license_url":"https://creativecommons.org/licenses/by/4.0/",
         "source_page":source_page,
         "source_image":cand["url"],
         "source_observation":"https://www.inaturalist.org/observations/205805006",
         "original_sha1":cand["sha1"],
         "archived_sha256":img_sha,
         "modifications":"JPEG re-encoded, EXIF/GPS stripped; annotated in gallery overlays (JPEG itself not marked)",
         "public_reuse":"CC BY 4.0, requires attribution, license link and modification statement",
         "photo_status":"ORIGINAL PIXELS INSPECTED BEFORE INSTALL; visible-only gross anatomy markers; still no measured TRUE ligule"
       })
       item={
         "label":cand["label"],"scientific_name":"Dichanthelium commutatum",
         "image_url":str(dest).replace("\\","/"),"image_fit":"contain",
         "image_role":cand["role"],"caption":cand["caption"],
         "why_it_matters":cand["why"],"creator":"Alex Abair",
         "license":"CC BY 4.0","license_url":"https://creativecommons.org/licenses/by/4.0/",
         "source_page":source_page,"markers":cand["markers"],
         "photo_status":"Verified source, pixel-inspected human-review source preview, original JPEG byte-fingerprint checked; no measured true ligule/glume claims"
       }
       existing=card["visual_comparison"]["items"]
       first_comparison=next((i for i,x in enumerate(existing) if x.get("scientific_name")!="Dichanthelium commutatum"),len(existing))
       existing.insert(first_comparison,item)
       report["added"].append({"id":cand["id"],"local":str(dest),"source":source_page,"dims":list(img.size),"sha256":img_sha,"arrows":len(cand["markers"])})
    except Exception as exc:
       # Failed photos are NOT linked and no unlicensed/unverified source is counted.
       if dest.exists() and not any(z.get("file")==dest_rel for z in card["images"]):
          dest.unlink()
       report["held"].append({"id":cand["id"],"reason":str(exc)})
if report["added"]:
    card["curation_status"]["photo_metadata_count"]=len(card["images"])
    card["curation_status"]["photo_files_present"]=sum((species/x["file"]).is_file() for x in card["images"])
    card["curation_status"]["own_photo_arrows"]=sum(len(x.get("markers",[])) for x in card["visual_comparison"]["items"] if x.get("scientific_name")=="Dichanthelium commutatum")
    card["learner_visual_status"]["image_count"]=len(card["images"])
    card["field_id_finish_pass"]["visible_photo_arrows"]=card["curation_status"]["own_photo_arrows"]
    card["field_id_finish_pass"]["lane4_archived_collars_20261025"]={
       "local_additions":len(report["added"]),
       "actual_species_local_photo_count":card["curation_status"]["photo_files_present"],
       "new_annotations":sum(z["arrows"] for z in report["added"]),
       "status":"FIELD_READY_PHOTO_GAPS",
       "remaining":["True inner 0.5-mm ligule measured","Fully revealed basal leaf shape of vouchered same plant","Ripe mature 2.1–3.2-mm spikelet and separated glumes/lemmas","Rooted crown and same-specimen phases","GitHub Pages visual QA"],
       "site_qa":"not independently verified"
    }
    card["visual_comparison"]["subtitle"]="Locally archived species-specific flower, panicle, living plant and new publicly licensed sheath/leaf macros with visible-only arrows. No measured inner ligule or dissected mature glumes; CC BY-NC look-alike images need separate permission."
    card["photo_note"] += " 2026-10-25 source SHA1-verified CC BY 4.0 Alex Abair leaf/sheath anatomy photographs physically archived as stripped-JPEG and connected to gallery with gross arrows; no measured true ligule claimed."
    path.write_text(json.dumps(card,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
rp=pathlib.Path("reports/lane4-commutatum-collar-archive.json")
rp.parent.mkdir(exist_ok=True)
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(report))
