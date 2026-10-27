#!/usr/bin/env python3
"""Exact Central/West TX preserved silver bluestem crowns and fibrous roots.

GBIF accepted name B. torreyana; original TEX sheets labelled B. laguroides
subsp/var torreyana. The UNIVERSITY OF TEXAS herbarium's INDIVIDUAL MEDIA
license is CC BY 4.0; GBIF record metadata CC0 is NOT the image license.
Photographed specimen roots are attached. No proof of absent rhizomes.
"""
import hashlib,io,json
from pathlib import Path
import requests
from PIL import Image,ImageOps

ROOT=Path(__file__).resolve().parents[1]
REL="content/taxa/Poaceae/Bothriochloa/bothriochloa-torreyana"
CARD=ROOT/REL/"species.json"
REPORT=ROOT/"reports/silver-torreyana-texas-two-rooted-herbarium-20261027.json"
MARKER=ROOT/"workflow/field-id-publication/2026-10-27-silver-genuine-texas-roots-75pct.json"
JOBS=[
 {"key":3921136348,"catalog":"TEX00570934","county":"Guadalupe","year":2019,
  "filename":"silver-guadalupe-tex-herbarium-rooted-crowns-20261027.jpg",
  "label":"TEXAS SILVER — preserved rooted flowering plants, Guadalupe County",
  "role":"Three collected source-verified central Texas B. torreyana flowering plants with real basal crowns, attached roots and centimeter-scale specimen header",
  "caption":"Real preserved University of Texas (TEX) herbarium specimen TEX00570934 of Bothriochloa laguroides subsp. torreyana (accepted here as B. torreyana), collected 4 November 2019 near Seguin, GUADALUPE COUNTY, Texas. Several flowering stems are shown with three rooted basal tufts and genuine fibrous roots attached; broad arrows show an actual crown and its extending roots. This is a PRESSED sheet, not a living plant in habitat. The centimeter ruler printed at the top gives general whole-sheet scale; it does NOT establish the exact length of an individual ligule, node hair or root internode. Presence or absence of short underground rhizomes cannot be determined from this photograph.",
  "why":"Finally shows a genuine Central Texas source-vouchered entire flowering plant with actual crown and roots, covering the formerly missing rooted habit role without substituting a distant generic grass.",
  "markers":[{"label":"Joined basal crown","label_x":3,"label_y":67,"target_x":23,"target_y":70},
             {"label":"Attached fibrous roots","label_x":4,"label_y":89,"target_x":22,"target_y":79}]},
 {"key":6158969001,"catalog":"TEX00597022","county":"Gaines","year":2018,
  "filename":"silver-gaines-tex-herbarium-rooted-bunch-20261027.jpg",
  "label":"TEXAS SILVER — connected crown and roots, Gaines County",
  "role":"Dense source-vouchered West Texas silver bluestem perennial crown, natural fibrous roots and attached flowering culms in one pressed original",
  "caption":"Original photographed TEX herbarium specimen TEX00597022 of Bothriochloa laguroides var. torreyana (accepted B. torreyana), collected 1 November 2018 in GAINES COUNTY, Texas. The dense preserved basal crown has genuine connected flowering stems and multiple fine roots visible along the lower part of the sheet. The arrows identify only that visible crown/root system, not an individually resolved rhizome or buried root architecture. Whole sheet with original 10 cm reference bar; species-level original specimen, not a Texas Hays field photograph.",
  "why":"Second genuine rooted Texas specimen validates that crowded basal shoots and attached thin roots are real structures rather than a mistaken tuft of unrelated grasses.",
  "markers":[{"label":"Dense basal crown","label_x":3,"label_y":64,"target_x":41,"target_y":72},
             {"label":"Visible fibrous roots","label_x":57,"label_y":89,"target_x":49,"target_y":78}]}
]
HEADERS={"User-Agent":"City Kyle Hays Botany source-credited open educational photo verification/1.0"}

def main():
  s=json.loads(CARD.read_text(encoding="utf-8"))
  if s.get("id")!="bothriochloa-torreyana":raise RuntimeError("incorrect taxon")
  old_score=s["silver_six_role_photo_score_20261027"]["total"]
  result={"date":"2026-10-27","taxon":"Bothriochloa torreyana",
          "before_images":len(s["images"]),"before_panels":len(s["visual_comparison"]["items"]),
          "original_role_score":old_score,"items":[]}
  session=requests.Session();session.headers.update(HEADERS)
  ok=[]
  for spec in JOBS:
    try:
      r=session.get(f"https://api.gbif.org/v1/occurrence/{spec['key']}",timeout=27);r.raise_for_status()
      o=r.json()
      if o.get("acceptedScientificName")!="Bothriochloa torreyana (Steud.) Scrivanti & Anton":
        raise ValueError("not species-verified accepted-name record")
      if "torreyana" not in str(o.get("scientificName","")).lower() or o.get("basisOfRecord")!="PRESERVED_SPECIMEN":
        raise ValueError("not exact labelled original subsp/var")
      if o.get("institutionCode")!="TEX" or o.get("catalogNumber")!=spec["catalog"]:
        raise ValueError("catalogue identity changed")
      if o.get("stateProvince")!="Texas" or o.get("county")!=spec["county"]:
        raise ValueError("original Texas locality mismatch")
      matches=[m for m in o.get("media",[]) if m.get("license")=="http://creativecommons.org/licenses/by/4.0/"]
      if len(matches)!=1 or matches[0].get("rightsHolder")!="The University of Texas at Austin":
        raise ValueError("individual photograph CC BY 4.0 university rights missing")
      link=matches[0]["identifier"]
      raw=session.get(link,timeout=50)
      if raw.status_code==429:raise ValueError("source rate limited, no bypass")
      raw.raise_for_status()
      if not (1_000_000<=len(raw.content)<=24_000_000):raise ValueError("unexpected specimen image bytes")
      with Image.open(io.BytesIO(raw.content)) as im:
        image=ImageOps.exif_transpose(im).convert("RGB")
        original_size=list(image.size)
      if min(image.size)<4000:raise ValueError("insufficient original specimen resolution")
      image.thumbnail((3400,3400),Image.Resampling.LANCZOS)
      filepath=ROOT/REL/"images"/spec["filename"]
      filepath.parent.mkdir(parents=True,exist_ok=True)
      image.save(filepath,"JPEG",quality=89,optimize=True,subsampling=0)
      with Image.open(filepath) as ck:
        if ck.getexif():raise ValueError("metadata not cleared")
        ck.verify()
      sha=hashlib.sha256(filepath.read_bytes()).hexdigest()
      credit="The University of Texas at Austin, TEX Herbarium"
      source="https://www.gbif.org/occurrence/"+str(spec["key"])
      license_url="https://creativecommons.org/licenses/by/4.0/"
      record={
         "file":"images/"+spec["filename"],"role":spec["role"],
         "creator":credit,"license":"CC BY 4.0","license_url":license_url,
         "source_page":source,"source_original_url":link,
         "source_gbif_key":spec["key"],"source_catalog_number":spec["catalog"],
         "scientific_name_source":o["scientificName"],"accepted_name":"Bothriochloa torreyana",
         "source_locality":spec["county"]+" County, Texas","study_use":"yes",
         "public_reuse":"yes individual source image explicitly CC BY 4.0; whole photographed sheet with source credit",
         "photo_status":"PHYSICALLY ARCHIVED exact vouchered B. torreyana preserved specimen with attached fibrous roots; rights checked per GBIF media record; no free ligule or rhizome microclaim",
         "image_dimensions":list(image.size),"source_image_dimensions":original_size,
         "archived_sha256":sha,"EXIF_removed":True
      }
      panel={
        "label":spec["label"],"scientific_name":"Bothriochloa torreyana",
        "image_url":REL+"/images/"+spec["filename"],"image_fit":"contain",
        "image_role":spec["role"],"caption":spec["caption"],"why_it_matters":spec["why"],
        "creator":credit,"license":"CC BY 4.0","license_url":license_url,"source_page":source,
        "markers":spec["markers"],
        "photo_status":"VERIFIED AUTHENTIC TEX HERBARIUM PRESSED REAL ROOTED PLANT; two arrows aimed at genuine visible crown and roots, not anatomical microdetails."
      }
      if not any(x.get("source_gbif_key")==spec["key"] for x in s["images"]):s["images"].append(record)
      if not any(x.get("source_page")==source for x in s["visual_comparison"]["items"]):s["visual_comparison"]["items"].append(panel)
      result["items"].append({"key":spec["key"],"catalog":spec["catalog"],"status":"ARCHIVED",
          "source":source,"file":str(filepath.relative_to(ROOT)),"sha256":sha,
          "original_size":original_size,"archived_size":list(image.size),
          "media_license":"CC BY 4.0","root_photo_arrows":2})
      ok.append(spec["key"])
    except Exception as e:
      result["items"].append({"key":spec["key"],"catalog":spec["catalog"],"status":"HOLD","reason":str(e)[:300]})
  if ok:
    n=len(s["images"])
    s["curation_status"]["photo_files_present"]=n
    s["curation_status"]["photo_metadata_count"]=n
    s["curation_status"]["visual_finish"]="FIELD_READY_PHOTO_GAPS — 2 real photographed TEX herbarium silver bluestem rooted flowering specimens archived under CC BY 4.0. Open FREE ligule edge and intact measurable 1mm paired spikelets remain unphotographed; root photo does not determine rhizome absence."
    s["silver_preserved_rooted_texas_vouchers_20261027"]={
      "new_verified_herbarium_sheet_keys":ok,
      "new_public_licensed_real_rooted_plant_photos":len(ok),
      "texas_herbarium_catalogues":[x["catalog"] for x in JOBS if x["key"] in ok],
      "taxon_crosswalk":"B. laguroides var./subsp. torreyana = B. torreyana (GBIF accepted) for this exact US sheet",
      "authoritative_image_license":"The University of Texas at Austin original-media CC BY 4.0 (NOT GBIF record metadata CC0)",
      "real_roots_visible":True,"rhizome_presence_absence_from_sheet":"NOT PROVEN",
      "free_membranous_ligule_edge":"MISSING","connected_mm_spikelet_pair":"MISSING",
      "new_verified_gross_arrows":2*len(ok),
      "state":"FIELD_READY_PHOTO_GAPS"
    }
    score=s["silver_six_role_photo_score_20261027"]
    if score.get("total")==4 and 3921136348 in ok:
      score["roles"][0]["score"]=1
      score["roles"][0]["reason"]="Multiple flowering B. torreyana plants with genuinely attached fibrous roots and basal crowns in a TEX-vouchered Guadalupe County preserved specimen sheet, plus Max Licher's living standing bunch. Rhizome condition not resolved by sheet."
      score["total"]=4.5
      score["pct"]=75.0
      score["remaining_pct"]=25.0
      score["target_70pct_needed_additional_role_points"]=0
      score["target_80pct_needed_additional_role_points"]=0.3
      score["target_90pct_needed_additional_role_points"]=0.9
      score["status"]="Photo-complete role equivalent 4.5/6 (75%). Source-vouchered Texas rooted plant now present; true open mm ligule and attached 1mm pair remain."
    s["learner_visual_status"]["public_photographs_physically_archived"]=9+len(ok)
    s["learner_visual_status"]["image_count"]=n
    s["learner_visual_status"]["public_gallery_panels"]=len(s["visual_comparison"]["items"])
    s["learner_visual_status"]["total_photo_arrows"]=sum(len(x.get("markers",[])) for x in s["visual_comparison"]["items"])
    s["learner_visual_status"]["note"]="New original TEX Herbarium CC BY 4.0 rooted flowering specimens in Guadalupe and Gaines County, Texas; authentic attached crowns and roots. Pressed sheets, not living field photographs. A real calibrated open ligule and sessile/pedicelled paired-spikelet macro still missing."
    s["field_photo_quickcheck"]["featured_panel_indices"]=[0,12,13,8,10,11,5,9,6,4,7,2,3] if len(ok)==2 else s["field_photo_quickcheck"]["featured_panel_indices"]
    s["field_id_short_tiles"][1]["details"]="The new TEX Herbarium photographs (Guadalupe County sheet TEX00570934 and Gaines County sheet TEX00597022) finally show REAL B. torreyana flowering stems with multiple connected basal CROWNS and fine ROOTS extending from them. Two broad, visibly verified arrows mark crown and roots on each pressed sheet. The original specimens have a whole-sheet centimeter ruler, but the root systems are pressed, not excavated in soil; rhizome presence or absence is NOT established from these sheets. Compare with Max Licher's living Arizona bunch to recognize a natural basal clump."
    s["field_id_short_tiles"][1]["photo_panel_indices"]=[12,13,6,1] if len(ok)==2 else [len(s["visual_comparison"]["items"])-1,6,1]
    s["field_id_short_tiles"][1]["status"]="ROOTED PLANT PHOTOGRAPHIC ROLE COMPLETE — real connected source-vouchered Texas crowns and roots, plus live habit; rhizome variation still scientifically unresolved"
    s["field_id_short_tiles"][5]["details"]+=" NEW TWO TEX Herbarium real rooted flowering plants with attached fibrous roots and clear CC BY 4.0 image permissions add the previously missing basal/root anatomy; these are pressed specimens (Guadalupe/Gaines County), not field-grown comparison photographs. No claim of absent rhizomes or photographed free ligule.";
    s["field_id_short_tiles"][5]["photo_panel_indices"]=[0,12,13,10,11,8,9,5,6,7,4] if len(ok)==2 else s["field_id_short_tiles"][5]["photo_panel_indices"]
    s["field_photo_quickcheck"]["steps"][1]="2 · FOLLOW THE ACTUAL CROWN AND ROOTS: real Texas University of Texas specimen sheets now show multiple flowering stems joined at a perennial basal CROWN with genuine extending FIBROUS ROOTS. Those preserved sheets document the rooted clump; they cannot prove rhizome absence or standing field habit. Contrast with Max Licher's real living Arizona bunch."
    s["field_photo_quickcheck"]["warning"]+=" New CC BY 4.0 Guadalupe/Gaines TEX-vouchered whole rooted flowering specimens are PRESSED sheets, not invented living photos. Genuine attached roots confirmed; don't mark local Hays ligule or rhizome condition complete."
    CARD.write_text(json.dumps(s,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    MARKER.parent.mkdir(parents=True,exist_ok=True)
    MARKER.write_text(json.dumps({"date":"2026-10-27","taxon":"bothriochloa-torreyana",
       "actual_TEX_GBIF_rooted_photo_keys":ok,"vouchered_TEX_CC_BY_4":True,
       "new_gross_arrows":len(ok)*2,
       "six_role_score":"4.5/6 (75%)" if score.get("total")==4.5 else "unchanged due different baseline",
       "source_truth":"PRESSED flowering and fibrous-rooted plants, NO photographed mm ligule/entire pair; rhizome condition not established"},indent=2)+"\n")
  result["installed_count"]=len(ok)
  result["images_after"]=len(s["images"])
  result["panels_after"]=len(s["visual_comparison"]["items"])
  result["arrow_count"]=sum(len(x.get("markers",[])) for x in s["visual_comparison"]["items"])
  result["photo_roles"]=s["silver_six_role_photo_score_20261027"]["total"]
  REPORT.parent.mkdir(parents=True,exist_ok=True)
  REPORT.write_text(json.dumps(result,indent=2)+"\n")
  print(json.dumps(result,indent=2))
if __name__=="__main__":main()
