#!/usr/bin/env python3
"""Lane 4: exact-source CC BY Polypogon collar photographs, verified original SHA-1.

Source identity and individual licenses were checked on Commons 2026-10-25.
Never treat outer sheath tissue as a measured inner ligule; only visible, gross
structures are arrowed. Preserve existing imagery and field science.
"""
import hashlib
import io
import json
import pathlib
import time
import urllib.request

from PIL import Image, ImageOps

base = pathlib.Path("content/taxa/Poaceae/Polypogon/polypogon-monspeliensis")
p = base/"species.json"
d = json.loads(p.read_text(encoding="utf-8"))
assert d["id"] == "polypogon-monspeliensis"
assert d["field_id_finish_pass"]["stage"] == "FIELD_READY_PHOTO_GAPS"

photos = [
    {
      "id":"07",
      "upload":"https://upload.wikimedia.org/wikipedia/commons/8/8e/Polypogon_monspeliensis_leaf_%2807%29.jpeg",
      "sha1":"c8279269b3b8d83d77d0c6ce3400c8d9fc202857",
      "source_photo":"https://www.inaturalist.org/photos/77696732",
      "role":"Actual closely photographed green blade-sheath collar region, translucent pale membrane and nearby blade, not a calibrated millimeter ligule",
      "label":"Annual beardgrass — translucent blade/sheath collar membrane",
      "caption":"Daniel Cahen's photo shows a pale transparent, pointed membrane rising at a green blade-sheath junction on an upright stem. An upper sheath margin overlaps part of the base, and a nearby grass panicle is blurred. The exact free inner ligule margin and length cannot be measured: this is a close collar-location lesson, not proof of a 2.5–16 mm ligule.",
      "why":"The crew can locate the sheath-blade intersection and its pale membranous tissue on a real species-determined plant. Follow up with a directly opened interior collar and ruler.",
      "markers":[
         {"label":"Pale membrane at collar","label_x":73,"label_y":25,"target_x":46,"target_y":41},
         {"label":"Blade/sheath junction","label_x":5,"label_y":76,"target_x":51,"target_y":60}
      ]
    },
    {
      "id":"08",
      "upload":"https://upload.wikimedia.org/wikipedia/commons/e/ef/Polypogon_monspeliensis_leaf_%2808%29.jpeg",
      "sha1":"cb1b687ad568fe9fbd7124e60e3e06b940136b28",
      "source_photo":"https://www.inaturalist.org/photos/77696797",
      "role":"Different orientation of same documented plant's inner collar area: pale elongated membranous tissue, attached ribbed blade and upright culm; no scale",
      "label":"Annual beardgrass — membrane and blade attachment from another angle",
      "caption":"Daniel Cahen's second image shows pale vertically elongated collar-region tissue, a short fold across the blade insertion, and a ribbed green leaf entering from the right. The view reveals where to look for the true membranous ligule, but does not supply a ruler or a fully unfolded confirmed free margin.",
      "why":"Shows the leaf junction from an additional orientation; avoid mistaking sheath flaps or blade edges for a measured inner ligule.",
      "markers":[
         {"label":"Pale collar-region tissue","label_x":5,"label_y":16,"target_x":48,"target_y":33},
         {"label":"Blade inserts at junction","label_x":6,"label_y":75,"target_x":51,"target_y":59},
         {"label":"Parallel-veined leaf blade","label_x":74,"label_y":83,"target_x":67,"target_y":73}
      ]
    }
]
report={
  "species":"Polypogon monspeliensis",
  "review_date":"2026-10-25",
  "source_licensing":"Exact two Wikimedia Commons source files checked: Daniel Cahen, CC BY 4.0; share/adapt with attribution, link and change notice.",
  "added":[],
  "held":[],
  "images_inspected":"Actual original-sized previews viewed before authoring visible-only markers; no measured inner ligule asserted",
}
header={"User-Agent":"HaysBotanyEducationalGrassLearner/1.0 (photo rights checked)"}
for item in photos:
    f="images/commons-daniel-cahen-leaf-"+item["id"]+".jpg"
    local=base/f
    source_page="https://commons.wikimedia.org/wiki/File:Polypogon_monspeliensis_leaf_("+item["id"]+").jpeg"
    if any(x.get("file")==f for x in d["images"]):
        if local.exists():
           report["held"].append({"source":source_page,"reason":"Already in gallery and physically archived; duplicate not installed"})
           continue
        else:
           report["held"].append({"source":source_page,"reason":"Metadata exists but local photo missing; manual reconciliation needed"})
           continue
    try:
       blob=None
       for attempt in range(3):
          try:
             req=urllib.request.Request(item["upload"],headers=header)
             with urllib.request.urlopen(req,timeout=35) as res:
                blob=res.read(8_000_001)
             if len(blob)>8_000_000 or len(blob)<50_000:raise ValueError("Unexpected file length")
             break
          except Exception:
             if attempt==2:raise
             time.sleep(3*(attempt+1))
       assert hashlib.sha1(blob).hexdigest()==item["sha1"], "Original file SHA-1 changed: HOLD"
       im=Image.open(io.BytesIO(blob))
       im.verify()
       im=ImageOps.exif_transpose(Image.open(io.BytesIO(blob))).convert("RGB")
       if tuple(im.size)!=(2048,1536):raise ValueError("Unexpected dimensions or orientation")
       if local.exists():raise RuntimeError("Existing file path would be overwritten")
       local.parent.mkdir(parents=True,exist_ok=True)
       im.save(local,format="JPEG",quality=92,optimize=True)
       archived_sha256=hashlib.sha256(local.read_bytes()).hexdigest()
       record={
         "file":f,"role":item["role"],"creator":"Daniel Cahen",
         "license":"CC BY 4.0","license_url":"https://creativecommons.org/licenses/by/4.0/",
         "source_page":source_page,"source_photo":item["source_photo"],
         "original_file_sha1":item["sha1"],"archived_file_sha256":archived_sha256,
         "modifications":"Original re-encoded RGB JPEG; EXIF/GPS removed; annotation arrows are separate web overlays",
         "public_reuse":"Public-site safe with creator attribution, source and license link, and modification notice",
         "photo_status":"PHYSICALLY ARCHIVED SHA1-MATCHED JPEG; pixels human-reviewed for visible junction/membrane only; numeric ligule and organ dissection still unverified"
       }
       d["images"].append(record)
       panel={
          "label":item["label"],"scientific_name":"Polypogon monspeliensis",
          "image_url":str(local).replace("\\","/"),"image_fit":"contain",
          "image_role":item["role"],"caption":item["caption"],
          "why_it_matters":item["why"],"creator":"Daniel Cahen",
          "license":"CC BY 4.0","license_url":"https://creativecommons.org/licenses/by/4.0/",
          "source_page":source_page,
          "modifications":"Original JPEG re-encoded and EXIF/GPS stripped; browser labels are overlaid separately.",
          "markers":item["markers"],
          "photo_status":"Verified source CC BY 4.0 and SHA1; actual source pixels reviewed 2026-10-25; no calibrated measurement or glume identity inferred."
       }
       # New diagnostic photographs appear first; original panels & arrows remain intact.
       other=d["visual_comparison"]["items"]
       other.insert(len(report["added"]),panel)
       report["added"].append({"path":str(local),"source":source_page,"sha256":archived_sha256,"dimensions":list(im.size),"arrows":len(item["markers"])})
    except Exception as error:
       if local.exists() and not any(x.get("file")==f for x in d["images"]):
          local.unlink()
       report["held"].append({"source":source_page,"reason":str(error)})

# Public gallery should not display a CC BY-NC image on a permissive-rights site:
# Preserve original records, including any annotations, in review_holds.
nc=[x for x in d["visual_comparison"]["items"] if ("CC BY-NC" in str(x.get("license","")).upper())]
if nc:
    # Keep a complete archival record of removed display panels, not lost user work.
    d["visual_comparison"]["items"]=[x for x in d["visual_comparison"]["items"] if x not in nc]
    hold=d.setdefault("field_id_finish_pass",{}).setdefault("public_gallery_license_holds",[])
    for x in nc:
       if not any(y.get("source_page")==x.get("source_page") for y in hold):
          hold.append(dict(x,rights_hold_reason="CC BY-NC photo retained in original images[] and archival panel hold; not displayed until independently authorized."))

if report["added"] or nc:
    d["curation_status"]["photo_metadata_count"]=len(d["images"])
    d["curation_status"]["photo_files_present"]=sum((base/x["file"]).is_file() for x in d["images"])
    d["curation_status"]["photo_panels"]=len(d["visual_comparison"]["items"])
    d["curation_status"]["gross_visible_arrows"]=sum(len(x.get("markers",[])) for x in d["visual_comparison"]["items"])
    d["learner_visual_status"]["image_count"]=len(d["images"])
    d["field_id_finish_pass"]["visible_structure_arrows"]=sum(len(x.get("markers",[])) for x in d["visual_comparison"]["items"])
    d["field_id_finish_pass"]["lane4_ligule_photos_20261025"]={
       "stage":"FIELD_READY_PHOTO_GAPS",
       "new_public_cc_by_photo_jpegs":len(report["added"]),
       "physically_archived_total":d["curation_status"]["photo_files_present"],
       "public_gallery_panels":len(d["visual_comparison"]["items"]),
       "new_visible_only_gross_arrows":sum(x["arrows"] for x in report["added"]),
       "photo_proof":"Membranous tissue at blade/sheath junction visually apparent, NO millimeter ruler, confirmed isolated inner ligule base or precise numeric measurement",
       "remaining":["Scale-verified fully unfolded inner ligule","Detached single mature spikelet showing 2 notched glumes with long awns at actual insertion","Dissected fertile lemma and its possible shorter awn with millimeter reference","Rooted annual specimen with stem and flowering head","Source-safe Setaria and Phalaris comparative organ attachment macros","Independent GitHub Pages mobile rendering QA"],
       "legacy_public_license_holds":len(nc),
       "source_photo_rights":"Each new photograph CC BY 4.0, author Daniel Cahen, Commons image-level permission checked; archival metadata records original SHA1",
       "site_verification":"NOT independently verified"
    }
    d["visual_comparison"]["subtitle"]="Two new public CC BY 4.0 leaf-junction macros before source-authenticated seedhead/habit photographs; older CC BY-NC recognition picture kept archived but withheld from public gallery. Spikelet/glume/lemma dissection and ligule-scale gaps remain."
    d["visual_comparison"]["overlay_note"]="All displayed photos link to real archived GitHub JPEGs. Arrows show only visible leaf collar/membrane and broad seedhead features. Source-endorsed but unverified CC0 library photo is provisional; CC BY-NC source remains archived but is not public-safe for webpage."
    d["photo_note"]+=" 2026-10-25 Lane 4: exact-source CC BY 4.0 Daniel Cahen collar macros verified at original SHA1 and archived in GitHub, with 5 visible-only junction/membrane arrows; exact ligule length still unmeasurable. Pre-existing CC BY-NC image withheld from public gallery, preserved in record."
    p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
rpath=pathlib.Path("reports/lane4-polypogon-ligule-20261025.json")
rpath.parent.mkdir(exist_ok=True)
rpath.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps(report))
