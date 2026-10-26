#!/usr/bin/env python3
"""Promote inspected CC BY 4.0 Polypogon reproductive cluster macro, no unsupported claims."""
import hashlib,json,pathlib,shutil
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Polypogon/polypogon-monspeliensis")
p=base/"species.json"
d=json.loads(p.read_text(encoding="utf-8"))
assert d["id"]=="polypogon-monspeliensis"
manifest=pathlib.Path("workflow/photo-reviews/lane4-polypogon-reproductive-20261026/manifest.json")
m=json.loads(manifest.read_text(encoding="utf-8"))
matches=[x for x in m["added"] if x["id"]=="48"]
assert len(matches)==1
q=matches[0]
assert q["license"]=="CC BY 4.0" and q["photo_author"]=="Daniel Cahen"
assert q["original_sha1"]=="3e0847a88248c56a0f4b81570819e2dfde4d89d2"
assert q["source_page"]=="https://commons.wikimedia.org/wiki/File:Polypogon_monspeliensis_flower_(48).jpeg"
source=pathlib.Path(q["file"])
assert source.exists()
assert hashlib.sha256(source.read_bytes()).hexdigest()==q["local_sha256"]
with Image.open(source) as im:
    assert im.size==(2048,1536) and im.format=="JPEG"
new_name="images/commons-daniel-cahen-reproductive-48.jpg"
dest=base/new_name
report={"species":"Polypogon monspeliensis","source":q["source_page"],"added":[],"held":[]}
if any(x.get("file")==new_name for x in d["images"]):
    report["held"].append("Already in metadata: idempotent skip")
elif dest.exists():
    raise RuntimeError("Existing destination bytes; refuse clobber")
else:
    shutil.copyfile(source,dest)   # already stripped EXIF/GPS and source sha checked
    d["images"].append({
      "file":new_name,
      "role":"Species-authenticated macro of small awn-bearing reproductive clusters branching from a close panicle axis; individual glume notch and fertile lemma not isolated",
      "creator":"Daniel Cahen",
      "license":"CC BY 4.0",
      "license_url":"https://creativecommons.org/licenses/by/4.0/",
      "source_page":q["source_page"],
      "source_photo":q["original_inaturalist_photo"],
      "source_original_sha1":q["original_sha1"],
      "archive_sha256":q["local_sha256"],
      "modifications":"Source photo RGB JPEG re-encoded without EXIF/GPS; visible-only webpage overlay labels",
      "public_reuse":"CC BY 4.0 attribution, license link and modification statement required",
      "photo_status":"ARCHIVED AND PIXEL INSPECTED for reproductive branching and awn halo; precise glume insertion NOT actually resolvable"
    })
    item={
      "label":"Annual beardgrass — real close reproductive branch and awns",
      "scientific_name":"Polypogon monspeliensis",
      "image_url":str(dest).replace("\\","/"),
      "image_fit":"contain",
      "image_role":"Actual species-specific close reproductive clusters: several pointed green spikelet-scale bodies crowded near branch tips plus a dense halo of long pale awns. No individual glume dissection.",
      "caption":"Daniel Cahen's original photo shows two adjacent branchlets bearing narrow green reproductive structures with very long pale awns. The long projections are consistent with beardgrass's diagnostic awned glumes, but the attachment notch of each awn on a single isolated glume is NOT clear. Do not label a fertile lemma or claim verified paired glumes from this image.",
      "why_it_matters":"Shows the fuzzy head resolved into actual reproductive clusters, closer to the true awn-bearing units than a whole seedhead portrait. Follow with a detached measured spikelet for final anatomical separation from Setaria.",
      "creator":"Daniel Cahen",
      "license":"CC BY 4.0",
      "license_url":"https://creativecommons.org/licenses/by/4.0/",
      "source_page":q["source_page"],
      "modifications":"Source JPEG re-encoded RGB and EXIF-free; three on-page anatomical gross-form arrows only",
      "markers":[
        {"label":"Awn-bearing units","label_x":71,"label_y":74,"target_x":49,"target_y":48},
        {"label":"Long pale awns","label_x":76,"label_y":13,"target_x":66,"target_y":27},
        {"label":"Flowering branch junction","label_x":5,"label_y":77,"target_x":44,"target_y":69}
      ],
      "photo_status":"2026-10-26 source original SHA-1 and reviewed license passed; re-encoded candidate SHA-256 checked; original full JPEG pixels visually inspected; no glume notch or lemma declared visible"
    }
    current=d["visual_comparison"]["items"]
    current.insert(0,item)
    d["curation_status"]["photo_metadata_count"]=len(d["images"])
    d["curation_status"]["photo_files_present"]=sum((base/x["file"]).exists() for x in d["images"])
    d["curation_status"]["photo_panels"]=len(current)
    d["curation_status"]["gross_visible_arrows"]=sum(len(x.get("markers",[])) for x in current)
    d["field_id_finish_pass"]["visible_structure_arrows"]=d["curation_status"]["gross_visible_arrows"]
    d["learner_visual_status"]["image_count"]=len(d["images"])
    d["field_id_finish_pass"]["lane4_reproductive_cluster_20261026"]={
       "stage":"FIELD_READY_PHOTO_GAPS",
       "local_source_confirmed":new_name,
       "new_gallery_panels":1,"new_visible_only_arrows":3,
       "source_license":"CC BY 4.0, Daniel Cahen",
       "verified_by_pixels":["reproductive clusters on two attached panicle branches","long thin pale awns extending well beyond green reproductive bodies"],
       "not_verifiable":["double notched glumes separated","glume awn arising from individual notch","smaller fertile lemma and shorter lemma awn","individual units measurable with mm bar"],
       "public_pages_QA":"Not independently verified"
    }
    d["photo_note"] += " 2026-10-26: Full original species-specific CC BY 4.0 reproductive cluster JPEG promoted from source-verified review with 3 gross-only arrows. Critical glume/lemma dissection gap remains."
    p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    report["added"].append({"path":str(dest),"sha256":q["local_sha256"],"panels":1,"new_arrows":3})
rp=pathlib.Path("reports/lane4-polypogon-reproductive-promotion-20261026.json")
rp.parent.mkdir(exist_ok=True)
rp.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
print(json.dumps(report))
