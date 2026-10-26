#!/usr/bin/env python3
"""Lane 4: source-licensed Paspalum distichum base photograph, one species only.

Harry Rose's exact Commons file was inspected at actual pixels and its own
CC BY 2.0 FlickrReviewR history on 2026-10-26. This specimen shows a connected
rhizome and roots at apparent nodes, NOT a proven soil-surface stolon bearing
a same-plant panicle. The original site metadata/license remain unchanged.
"""
import hashlib, io, json, pathlib, urllib.request, urllib.parse
from PIL import Image, ImageOps

base=pathlib.Path("content/taxa/Poaceae/Paspalum/paspalum-distichum")
p=base/"species.json"
j=json.loads(p.read_text(encoding="utf-8"))
assert j["id"]=="paspalum-distichum"
assert j["field_id_finish_pass"]["stage"]=="FIELD_READY_PHOTO_GAPS"
source="https://commons.wikimedia.org/wiki/File:Paspalum_distichum_rhizomes1_(8251311954).jpg"
original="https://upload.wikimedia.org/wikipedia/commons/d/dc/Paspalum_distichum_rhizomes1_%288251311954%29.jpg"
photo_id="8251311954"
fname="images/harry-rose-rhizomes1-8251311954.jpg"
out=base/fname
report={"id":j["id"],"source":source,"license":"CC BY 2.0 Generic, Harry Rose, reviewed by Wikimedia FlickrReviewR 2015-05-20","added":[],"held":[],"photo_roles":["rhizome and nodal roots"],"photo_status":"not yet added"}
if any(x.get("file")==fname for x in j["images"]):
    report["held"].append("Already indexed; skip duplicate")
    report["photo_status"]="already indexed in canonical metadata"
else:
    try:
        if out.exists():raise ValueError("Unexpected existing photo path; no overwrite")
        req=urllib.request.Request(original, headers={"User-Agent":"HaysCountyBotanyVisualLearner/1.0 (credited science education image archive)"})
        with urllib.request.urlopen(req,timeout=50) as resp:
            payload=resp.read(6_000_001)
        if not(50_000<len(payload)<6_000_000):raise ValueError("Original bytes length outside trusted bounds")
        with Image.open(io.BytesIO(payload)) as verify: verify.verify()
        original_image=ImageOps.exif_transpose(Image.open(io.BytesIO(payload))).convert("RGB")
        if original_image.size!=(2592,1944):raise ValueError("Source image dimensions differ from verified original Commons file; hold")
        source_sha256=hashlib.sha256(payload).hexdigest()
        out.parent.mkdir(parents=True,exist_ok=True)
        original_image.save(out,format="JPEG",quality=91,optimize=True)
        dest_sha256=hashlib.sha256(out.read_bytes()).hexdigest()
        j["images"].append({
          "file":fname,
          "role":"Actual long horizontal rhizome with fibrous roots at successive branch/node regions and attached green shoots; not a rooted above-ground soil-surface stolon, no flowering panicle",
          "creator":"Harry Rose (Macleay Grass Man)",
          "license":"CC BY 2.0",
          "license_url":"https://creativecommons.org/licenses/by/2.0/",
          "source_page":source,
          "original_source":"https://www.flickr.com/photos/73840284@N04/8251311954",
          "source_original_sha256":source_sha256,
          "archived_sha256":dest_sha256,
          "modifications":"Re-encoded RGB JPEG (91% quality) with EXIF/GPS removed; image-only arrows are separate site overlays",
          "public_reuse":"Individual exact image CC BY 2.0 FlickrReviewR confirmed; author/source/license and re-encoding notice mandatory",
          "photo_status":"PHYSICALLY ARCHIVED source-verified and pixels visually reviewed 2026-10-26; rhizome/rooted-node photograph not a connected same-specimen flowering head"
        })
        panel={
          "label":"ROOTING BASE — actual rhizome with nodal root masses",
          "scientific_name":"Paspalum distichum",
          "image_url":str(out).replace("\\","/"),
          "image_fit":"contain",
          "image_role":"Genuine Harry Rose Paspalum distichum photographed rhizome with two dense root-bearing positions, green attached internodes and developing shoot; soil line NOT present",
          "caption":"Harry Rose's specimen shows a continuous green horizontal rhizome or creeping basal stem, with branching fibrous roots descending from two regions and a fresh green shoot rising near the right-hand root mass. This is real underground vegetative spread, NOT a photo showing a surface stolon rooted into undisturbed moist soil. Root bases are visible; same-individual flowering architecture is not.",
          "why_it_matters":"Separates mat-forming knotgrass growth from tufted bahiagrass or thin paspalum when combined with the two-raceme head and true membranous ligule. A two-armed seedhead alone cannot establish knotgrass.",
          "creator":"Harry Rose (Macleay Grass Man)",
          "license":"CC BY 2.0",
          "license_url":"https://creativecommons.org/licenses/by/2.0/",
          "source_page":source,
          "modifications":"Original color photograph re-encoded without EXIF/GPS; three browser-overlay gross visible arrows added",
          "markers":[
            {"label":"Horizontal connected rhizome","label_x":12,"label_y":20,"target_x":35,"target_y":36},
            {"label":"Roots below central node","label_x":9,"label_y":74,"target_x":51,"target_y":42},
            {"label":"Root mass and green shoot","label_x":73,"label_y":8,"target_x":56,"target_y":22}
          ],
          "photo_status":"Pixel-reviewed actual original 2592×1944 JPEG; rooted bases are visible but no intact same-plant flowering head, true stolon at soil line or calibrated cm rule; taxon credited to source identification"
        }
        # The true base image comes before flowering head; preserve each existing panel.
        j["visual_comparison"]["items"].insert(0,panel)
        j["curation_status"]["photo_metadata_count"]=len(j["images"])
        j["curation_status"]["photo_files_present"]=sum((base/x["file"]).is_file() for x in j["images"])
        j["learner_visual_status"]["image_count"]=len(j["images"])
        j["field_id_finish_pass"]["lane4_real_rhizome_archive_20261026"]={
          "stage":"FIELD_READY_PHOTO_GAPS",
          "new_image_files":1,
          "verified_own_species_image_count":j["curation_status"]["photo_files_present"],
          "new_gallery_panels":1,
          "new_actual_pixel_arrows":3,
          "verified_role":"rhizome/base with visible roots descending from two nodal regions and emerging shoot",
          "still_missing":["same identified live plant's aboveground soil-surface stolon with roots touching/entering moist soil, centimeter scale","same plant's terminal attached 2-raceme flowering head","mature upper glume + sterile and fertile lemma separately photographed to mm scale","true short membranous ligule free edge under 1-mm bar","matched Paspalum notatum rooting habit and spikelet panel","live GitHub Pages card mobile QA"],
          "source_rights":"Individual Harry Rose CC BY 2.0 verified at Commons FlickrReviewR; NOT CC0 or anonymous stock",
          "image_provenance_note":"Australian voucher-labelled taxon; not proof of Hays County provenance nor county-native status",
          "site_deployment":"NOT VERIFIED"
        }
        j["visual_comparison"]["subtitle"]="Five real locally archived Paspalum distichum photographs: rhizome/root masses, flowering V, actual membranous collar, spikelet-bearing rachis and wet-ground habit, plus separate Paspalum setaceum comparison. Same-plant rooted surface stolon, mature spikelet dissection and Pages QA remain unconfirmed."
        j["photo_note"]+=" 2026-10-26: archived a new CC BY 2.0 Harry Rose actual rhizome with nodal fibrous roots, EXIF-free JPEG and 3 visible-only root/base arrows. Distinguish photographed underground rhizome from still-missing aboveground rooted stolon attached to flowering culm."
        p.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        report["added"].append({"file":str(out),"source_original_sha256":source_sha256,"archive_sha256":dest_sha256,"dims":list(original_image.size),"arrows":3,"source_rights":source})
        report["photo_status"]="archived and linked, pending actual Pages deployment"
    except Exception as error:
        if out.exists() and not any(x.get("file")==fname for x in j["images"]):
            out.unlink()
        report["held"].append(str(error))
        report["photo_status"]="held, uninstalled, no photo count increment"
rp=pathlib.Path("reports/lane4-paspalum-distichum-root-photo-20261026.json")
rp.parent.mkdir(exist_ok=True)
rp.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps(report))
