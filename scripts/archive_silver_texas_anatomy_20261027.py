#!/usr/bin/env python3
"""Archive TWO original TX iNaturalist B. torreyana macros under photo-specific CC BY-NC.

Original photographs were visually reviewed at 768x1024 in the 2026-10-27
Texas photo-only discovery. Only gross visible characters are arrowed.
The collar photograph DOES NOT resolve the actual free membranous ligule;
the hairy reproductive group DOES NOT expose a provable paired sessile and
pedicelled spikelet or lemma insertion. Preserve that exact limit.
"""
from __future__ import annotations
import hashlib,io,json
from pathlib import Path
import requests
from PIL import Image,ImageOps

ROOT=Path(__file__).resolve().parents[1]
REL="content/taxa/Poaceae/Bothriochloa/bothriochloa-torreyana"
CARD=ROOT/REL/"species.json"
REPORT=ROOT/"reports/silver-torreyana-texas-anatomy-macros-20261027.json"
MARKER=ROOT/"workflow/field-id-publication/2026-10-27-silver-two-texas-anatomy-macros.json"
TARGETS=[
 {"obs":398297406,"photo":730629825,"username":"calvinnering","name":"Denton leaf blade–sheath junction",
  "filename":"silver-denton-ccby-nc-blade-sheath-junction-730629825.jpg",
  "role":"Real Texas leaf blade–sheath junction, collar region, no resolved free membranous ligule",
  "label":"TEXAS SILVER — genuine leaf–sheath junction, membranous edge NOT resolved",
  "caption":"Source-labelled genuine B. torreyana, Denton, Texas, photographed August 29, 2026. The junction where the blade separates from the wrapping leaf sheath is plainly visible with a finger scale. The true free ligule membrane and measured rim are NOT separately resolved; do not claim this is a full ligule macro or a measured node. Research-grade iNaturalist ID is not an herbarium voucher.",
  "why":"First independently licensed, physically archivable Texas blade–sheath/collar-region macro, good for learning WHERE to open the ligule.",
  "markers":[{"label":"Blade–sheath junction","label_x":1,"label_y":67,"target_x":50,"target_y":47},
             {"label":"Wrapping sheath","label_x":54,"label_y":78,"target_x":66,"target_y":53}]},
 {"obs":407724136,"photo":749323175,"username":"sylshessa","name":"Deer Park mature reproductive close-up",
  "filename":"silver-deer-park-ccby-nc-spikelet-groups-749323175.jpg",
  "role":"Actual Texas spikelet-bearing hairy flowering segment; visible bodies/hairs, unclear pairs",
  "label":"TEXAS SILVER — mature spikelet-bearing flowering segment",
  "caption":"Genuine source-labelled Texas silver bluestem recorded at Deer Park on October 10, 2026. Several visible oblong golden spikelet bodies occur amid a dense tuft of long silky white hairs. Arrows point to actual visible bodies and hairs only. The pedicel connection and fertile sessile versus sterile pedicelled assignment cannot safely be established here, and no physical millimeter ruler is present.",
  "why":"Adds a true Texas attached reproductive-view counterpart to the existing Arizona isolated spikelet-and-awn macro without inventing minute spikelet attachments.",
  "markers":[{"label":"Visible spikelet bodies","label_x":1,"label_y":33,"target_x":28,"target_y":56},
             {"label":"Long silky hairs","label_x":52,"label_y":89,"target_x":48,"target_y":66}]},
]
SESSION=requests.Session()
SESSION.headers.update({"User-Agent":"Hays Botany Educational Manual Photo Audit/1.0"})
def obtain(obsid,photoid):
    response=SESSION.get("https://api.inaturalist.org/v1/observations/"+str(obsid),timeout=28)
    response.raise_for_status()
    observations=response.json().get("results",[])
    if len(observations)!=1:raise RuntimeError("observation missing")
    o=observations[0]
    if o.get("taxon",{}).get("id")!=1452295 or o.get("quality_grade")!="research":
        raise RuntimeError("source species or research-grade verification changed")
    if "TX" not in str(o.get("place_guess","")) and "Texas" not in str(o.get("place_guess","")):
        raise RuntimeError("not confidently Texas location")
    p=next((p for p in o.get("photos",[]) if p.get("id")==photoid),None)
    if not p or p.get("license_code")!="cc-by-nc":
        raise RuntimeError("individual photograph CC BY-NC or original photo missing")
    url=str(p.get("url",""))
    if not url.startswith("https://"):raise RuntimeError("bad source photo URL")
    url=url.replace("/square.","/large.").replace("/medium.","/large.")
    response=SESSION.get(url,timeout=30)
    if response.status_code==429:raise RuntimeError("source rate-limited, do not bypass")
    response.raise_for_status()
    if len(response.content)>10_000_000:raise RuntimeError("unexpectedly large")
    with Image.open(io.BytesIO(response.content)) as im:
        image=ImageOps.exif_transpose(im).convert("RGB")
        image.load()
    if min(image.size)<750 or max(image.size)>5000:raise RuntimeError("image size inconsistent with inspected original")
    return o,p,image,url
def main():
    s=json.loads(CARD.read_text(encoding="utf-8"))
    assert s["id"]=="bothriochloa-torreyana"
    assert s["native_target_zone_calculated"] is False
    basePhotos=len(s["images"])
    basePanels=len(s["visual_comparison"]["items"])
    report={"date":"2026-10-27","taxon":"Bothriochloa torreyana",
      "baseline_photos":basePhotos,"baseline_panels":basePanels,
      "items":[],"scientific_limit":"Actual free ligule, true culm node, exposed roots and connected measured pair NOT photographically established"}
    installed=[]
    for spec in TARGETS:
        try:
            o,p,img,url=obtain(spec["obs"],spec["photo"])
            if o.get("user",{}).get("login")!=spec["username"]:
                raise RuntimeError("observation photographer uploader mismatch")
            saved=ROOT/REL/"images"/spec["filename"]
            saved.parent.mkdir(parents=True,exist_ok=True)
            img.save(saved,"JPEG",quality=90,optimize=True,subsampling=0)
            with Image.open(saved) as confirm:
                if confirm.getexif() or confirm.size!=img.size:
                    raise RuntimeError("GPS/EXIF or pixel-size mismatch after archiving")
                confirm.verify()
            digest=hashlib.sha256(saved.read_bytes()).hexdigest()
            fileRel="images/"+spec["filename"]
            photo_url="https://www.inaturalist.org/photos/"+str(spec["photo"])
            attrib=str(p.get("attribution") or "")
            creator="Amanda Gabehart" if spec["photo"]==749323175 else spec["username"]
            if spec["photo"]==749323175 and "Amanda Gabehart" not in attrib:
                raise RuntimeError("unexpected credited original author")
            rec={"file":fileRel,"role":spec["role"],"creator":creator,
                "license":"CC BY-NC (photo-specific; iNaturalist version not independently verified)",
                "license_url":"https://creativecommons.org/licenses/by-nc/4.0/",
                "source_page":photo_url,"source_photo_id":spec["photo"],
                "source_observation_id":spec["obs"],
                "observation_page":"https://www.inaturalist.org/observations/"+str(spec["obs"]),
                "source_original_url":url,"source_user":spec["username"],
                "source_locality":o.get("place_guess"),"observed_on":o.get("observed_on"),
                "study_use":"yes","public_reuse":"yes, strictly noncommercial photo attribution with CC BY-NC terms",
                "archive_sha256":digest,"image_dimensions":list(img.size),
                "photo_status":"PHYSICALLY ARCHIVED CC BY-NC source-labelled Texas silver bluestem, individual-photo license checked, EXIF/GPS removed. Do not infer unseen microscopic organ or mm-scale anatomy.",
                "identification_certainty":"iNaturalist research grade source identification; not a separately identified voucher"}
            panel={"label":spec["label"],"scientific_name":"Bothriochloa torreyana",
                   "image_url":REL+"/"+fileRel,"image_fit":"contain","image_role":spec["role"],
                   "caption":spec["caption"],"why_it_matters":spec["why"],
                   "creator":creator,"license":rec["license"],"license_url":rec["license_url"],
                   "source_page":photo_url,"source_photo_id":spec["photo"],
                   "markers":spec["markers"],
                   "photo_status":"ACTUAL 2026 Texas photograph, visibly inspected exact pixel coordinates, no speculative ligule/spikelet pair labels, CC BY-NC for noncommercial website"}
            if not any(x.get("file")==fileRel for x in s["images"]):s["images"].append(rec)
            if not any(x.get("source_photo_id")==spec["photo"] for x in s["visual_comparison"]["items"]):
                s["visual_comparison"]["items"].append(panel)
            report["items"].append({"id":spec["photo"],"status":"PHYSICAL_ARCHIVE_VERIFIED",
                 "file":str(saved.relative_to(ROOT)),"pixels":list(img.size),
                 "SHA256":digest,"credit":creator,"license":"cc-by-nc","actual_new_arrows":2})
            installed.append(spec["photo"])
        except Exception as e:
            report["items"].append({"id":spec["photo"],"status":"HOLD","reason":str(e)[:300]})
    if installed:
        s["curation_status"]["photo_metadata_count"]=len(s["images"])
        s["curation_status"]["photo_files_present"]=len(s["images"])
        s["curation_status"]["visual_finish"]="FIELD_READY_PHOTO_GAPS — source-verified Texas leaf–sheath junction and flowering-spikelet-group macro physically archived; no proven true free ligule, culm node, exposed roots or fully connected measured fertile/pedicelled pair. Preserve noncommercial photo conditions and U.S. variety notes."
        s["visual_comparison"]["subtitle"]="Actual field/head, true Texas leaf–sheath junction and hairy flowering segments. New large-photo arrows mark visible structures only; the true free membrane, bare culm node, dug roots and confirmed attached mature pair remain missing."
        s["texas_silver_anatomy_20261027"]={
          "source_photo_ids":installed,
          "new_exact_photos":len(installed),
          "new_verified_arrows":len(installed)*2,
          "archived_total_image_metadata":len(s["images"]),
          "panel_count":len(s["visual_comparison"]["items"]),
          "rights":"individual-photo CC BY-NC, nonprofit education only",
          "locality_note":"Denton and Deer Park, TX, not Hays specimen vouchers",
          "true_free_membranous_ligule":"MISSING despite real photographed blade–sheath junction",
          "measured_culm_node":"MISSING",
          "exposed_root":"MISSING",
          "attached_mm_sessile_pedicelled_pair":"MISSING",
          "status":"FIELD_READY_PHOTO_GAPS"}
        if 730629825 in installed:
            oldscore=s.get("silver_six_role_photo_score_20261027")
            if oldscore and oldscore.get("total")==3:
                roles=oldscore["roles"]
                # Credit half a role for real actual inner collar/junction placement
                # but NEVER credit the free ligule membrane, still unphotographed.
                roles[2]["score"]=0.5
                roles[2]["reason"]="Source-verified 2026 Denton TX image shows actual blade–sheath junction and collar region with finger scale. Free membranous ligule rim is NOT resolved/measured; this is only a partial role."
                oldscore["total"]=3.5
                oldscore["pct"]=round(100*3.5/6,1)
                oldscore["remaining_pct"]=round(100*2.5/6,1)
                oldscore["target_70pct_needed_additional_role_points"]=0.7
                oldscore["target_80pct_needed_additional_role_points"]=1.3
                oldscore["target_90pct_needed_additional_role_points"]=1.9
                oldscore["status"]="3.5/6 partial diagnostic roles (58.3%). Junction photographed, true free ligule still missing."
        s["learner_visual_status"]["public_photographs_physically_archived"]=5+len(installed)
        s["learner_visual_status"]["image_count"]=len(s["images"])
        s["learner_visual_status"]["public_gallery_panels"]=len(s["visual_comparison"]["items"])
        s["learner_visual_status"]["total_photo_arrows"]=sum(len(x.get("markers",[])) for x in s["visual_comparison"]["items"])
        s["field_photo_quickcheck"]["featured_panel_indices"]=[0,8,5,9,6,4,7,2,3] if len(installed)==2 else s["field_photo_quickcheck"]["featured_panel_indices"]
        CARD.write_text(json.dumps(s,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        MARKER.parent.mkdir(parents=True,exist_ok=True)
        MARKER.write_text(json.dumps({"date":"2026-10-27","taxon":"bothriochloa-torreyana",
          "new_verified_Texas_CC_BY_NC_photo_ids":installed,
          "gross_only_arrows":len(installed)*2,
          "image_archive":str(ROOT/REL/"images"),
          "photo_completeness":"3.5/6 (58.3%) if collar photo archived, else unchanged",
          "rights_caution":"noncommercial Creative Commons image licenses, source credit retained; no true free membrane claim"},indent=2)+"\n")
    report["new_installed_count"]=len(installed)
    report["final_archived_metadata_count"]=len(s["images"])
    report["final_panel_count"]=len(s["visual_comparison"]["items"])
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
