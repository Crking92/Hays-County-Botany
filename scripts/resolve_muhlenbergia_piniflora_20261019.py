#!/usr/bin/env python3
"""Resolve the erroneous M. piniflora learner source label to M. dubia.
Retain provenance, do not treat the misspelling as a taxonomic synonym.
Promote only actual licensed photos that are fetched, decoded, and de-EXIFed.
"""
import csv
import hashlib
import io
import json
import shutil
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageOps
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/"content/taxa/Poaceae/Muhlenbergia/muhlenbergia-piniflora"
NEW=ROOT/"content/taxa/Poaceae/Muhlenbergia/muhlenbergia-dubia"
GENUS=ROOT/"content/taxa/Poaceae/Muhlenbergia/genus.json"
DRAFT=ROOT/"research-drafts/muhlenbergia-piniflora/draft.json"
MANIFEST=ROOT/"data/manifest.json"
REPORT=ROOT/"reports/muhlenbergia-name-repair-20261019.json"
POWO="https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:408994-1"
FNA="https://openherbarium.org/portal/taxa/index.php?clid=0&taxauthid=1&tid=630304"
PHOTO=[
 {
 "id":"commons-patrick-alexander-muhlenbergia-dubia",
 "filename":"pine-muhly-patrick-alexander-cc0.jpg",
 "role":"Recognize · wild clump in dry rocky habitat with slender flowering stalks; exact ligule/spikelet structures not resolved",
 "url":"https://upload.wikimedia.org/wikipedia/commons/7/7d/Muhlenbergia_dubia_-_Flickr_-_aspidoscelis.jpg",
 "source_page":"https://commons.wikimedia.org/wiki/File:Muhlenbergia_dubia_-_Flickr_-_aspidoscelis.jpg",
 "creator":"Patrick Alexander",
 "license":"CC0 1.0",
 "license_url":"https://creativecommons.org/publicdomain/zero/1.0/",
 "evidence":"Wikimedia Commons records author, exact species and FlickrReviewR 2 verified CC0 on 2020-12-07; wild New Mexico field view"
 },
 {
 "id":"commons-stickpen-muhlenbergia-dubia-001",
 "filename":"pine-muhly-stickpen-public-domain.jpg",
 "role":"Recognize · cultivated tufted bunchgrass and narrow blades from above; no detailed ligule/spikelet confirmation",
 "url":"https://upload.wikimedia.org/wikipedia/commons/3/34/Muhlenbergia_dubia_001.jpg",
 "source_page":"https://commons.wikimedia.org/wiki/File:Muhlenbergia_dubia_001.jpg",
 "creator":"Stickpen",
 "license":"Public Domain (PD-self)",
 "license_url":"https://commons.wikimedia.org/wiki/Template:PD-self",
 "evidence":"Original photographer Stickpen dedicated image to the public domain on Wikimedia Commons; labelled M. dubia, Cuyamaca College garden"
 }
]
def load(path):
    return json.loads(path.read_text(encoding="utf-8"))
def save(path, obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def fetch_exact(item):
    if not item["url"].startswith("https://upload.wikimedia.org/wikipedia/commons/"):
        raise RuntimeError("Unapproved image domain")
    raw=None
    for attempt in range(3):
        try:
            req=urllib.request.Request(item["url"],headers={"User-Agent":"HaysBotanyExactTaxonPhoto/1.0 (botany learner)", "Accept":"image/jpeg,image/*"})
            with urllib.request.urlopen(req,timeout=35) as response:
                raw=response.read(12500001)
            if len(raw)>12500000:raise ValueError("Original image exceeds size limit")
            break
        except Exception:
            if attempt==2:raise
            import time
            time.sleep(3*(attempt+1))
    with Image.open(io.BytesIO(raw)) as im:
        im.verify()
    with Image.open(io.BytesIO(raw)) as im:
        if im.format not in {"JPEG","PNG","WEBP"} or min(im.size)<700:
            raise RuntimeError("Source raster cannot be used: "+str((im.format,im.size)))
        image=ImageOps.exif_transpose(im).convert("RGB")
        image.thumbnail((1800,1800))
        mem=io.BytesIO()
        image.save(mem,format="JPEG",quality=86,optimize=True)
    payload=mem.getvalue()
    with Image.open(io.BytesIO(payload)) as final:
        final.verify()
    with Image.open(io.BytesIO(payload)) as final:
        if final.getexif():
            raise RuntimeError("Source EXIF/GPS persisted")
        size=list(final.size)
    return payload,size,hashlib.sha256(payload).hexdigest()
def go():
    original=load(MANIFEST)
    installed={x["id"] for x in original["species"]}
    if "muhlenbergia-dubia" in installed:
        if "muhlenbergia-piniflora" in installed:
            raise RuntimeError("Collision: both old invalid and real accepted grass present")
        print("Already repaired; no duplicate migration")
        return
    if "muhlenbergia-piniflora" not in installed:
        raise RuntimeError("Missing original source concept; avoid stomping another worker")
    if NEW.exists():
        raise RuntimeError("Destination directory unexpectedly exists")
    old=load(OLD/"species.json")
    if old["id"]!="muhlenbergia-piniflora" or old.get("images"):
        raise RuntimeError("Source taxon changed or has images; abort to protect another worker")
    claims=load(ROOT/"workflow/work-claims.json").get("claims",[])
    now=datetime.now(timezone.utc)
    for claim in claims:
        if claim.get("status") not in {"active","queued","blocked"}:continue
        if claim.get("expires_at"):
            try:
                if datetime.fromisoformat(claim["expires_at"].replace("Z","+00:00"))<=now:continue
            except ValueError:
                pass
        if {"muhlenbergia-dubia","muhlenbergia-piniflora"}.intersection(claim.get("taxa") or []):
            raise RuntimeError("Species actively claimed in another workflow")
    images=[]
    checks=[]
    prepared=[]
    for item in PHOTO:
        payload,size,digest=fetch_exact(item)
        prepared.append((item,payload,size,digest))
    NEW.mkdir(parents=True)
    (NEW/"images").mkdir()
    for item,payload,size,digest in prepared:
        rel="images/"+item["filename"]
        (NEW/rel).write_bytes(payload)
        images.append({
            "file":rel,"role":item["role"],"creator":item["creator"],"license":item["license"],
            "license_url":item["license_url"],"source_page":item["source_page"],
            "media_source_url":item["url"],"source_determination":"Muhlenbergia dubia",
            "source_photo_id":item["id"],"publication_scope":"PUBLIC-WEB-CLEARED",
            "study_use":"Public botanical teaching material; retain original source and photographer credit",
            "public_reuse":"Public website permitted (CC0/public domain); credited voluntarily",
            "commercial_use_allowed":True,
            "modifications":"Resized, converted to RGB JPEG, re-encoded, EXIF and GPS removed; no anatomical arrows",
            "sha256":digest,"image_dimensions":size,
            "photo_review":"Original Commons file documents the exact species. File bytes validated, actual visual diagnostic details not yet expert-certified."
        })
        checks.append({"file":rel,"sha256":digest,"dimensions":size,"creator":item["creator"],"license":item["license"]})
    with (NEW/"image-sources.csv").open("w",newline="",encoding="utf-8") as fh:
        cols=["file_name","role","creator","license","license_url","source_page","direct_url","source_determination","publication_scope","modifications","image_sha256","source_identity_evidence"]
        writer=csv.DictWriter(fh,fieldnames=cols)
        writer.writeheader()
        for (item,payload,size,digest) in prepared:
            writer.writerow(dict(file_name=item["filename"],role=item["role"],creator=item["creator"],
                license=item["license"],license_url=item["license_url"],source_page=item["source_page"],
                direct_url=item["url"],source_determination="Muhlenbergia dubia",
                publication_scope="PUBLIC-WEB-CLEARED",modifications="Resized and stripped EXIF/GPS",
                image_sha256=digest,source_identity_evidence=item["evidence"]))
    repaired=dict(old)
    repaired.update({
      "id":"muhlenbergia-dubia","entry_type":"species",
      "species":"dubia","scientific_name":"Muhlenbergia dubia",
      "authority":"E.Fourn.","common_name":"Pine muhly",
      "synonyms":[],
      "source_label_correction":{
          "original_source_label":"Muhlenbergia piniflora",
          "original_source_common_name":"Pine Muhly",
          "resolution":"Source label is erroneous/untraceable and is NOT a botanical synonym. Project provenance points to accepted Muhlenbergia dubia. Retain history in research-drafts/muhlenbergia-piniflora/draft.json.",
          "supporting_sources":[POWO,"https://www.itis.gov/servlet/SingleRpt/SingleRpt?search_topic=TSN&search_value=41906","https://www.npsot.org/posts/native-plant/muhlenbergia-dubia/","https://www.austintexas.gov/watershed-protection/plant-guide/muhly-pine"]
      },
      "taxonomic_note":"Muhlenbergia dubia E.Fourn. is accepted by POWO and ITIS for pine muhly. 'Muhlenbergia piniflora' has no verified taxonomic standing and is a CORRECTED SOURCE TYPO, not an accepted synonym.",
      "look_here_first":"Recognize a densely tufted perennial pine muhly with narrow often inward-rolled leaves and erect wiry culms. Look closer: the narrow gray-green contracted panicle, not an open pink plume. Confirm: membranous ligule 4–10 mm, blades generally 1–2 mm wide, narrow panicles 10–40 cm long, and 3.8–5 mm spikelets; use magnification for glumes, lemma tips and ligule. Compare especially with M. rigens and other upright muhlies.",
      "project_inclusion":{
        "target_zone_status":"UNRESOLVED",
        "range_basis":"Pine muhly from the user-approved source-pool concept corrected from an untraceable spelling. POWO lists Arizona to Southwest Texas and Mexico; no county-level native range verified here.",
        "range_guardrail":"No county-native approval from this name correction. Native-range and 3-county audits remain paused."
      },
      "county_occurrences_target_zone":[],
      "target_zone_count":0,
      "native_target_zone_calculated":False,
      "native_metrics_excluded":True,
      "morphology_keys":{
        "best_field_traits":[
          "densely cespitose perennial, not rhizomatous",
          "culms 30–100 cm, upright",
          "leaf blades 1–2 mm wide, often involute",
          "membranous ligules about 4–10 mm",
          "narrow contracted panicle 10–40 cm long, 0.6–2.4 cm wide",
          "spikelets 3.8–5 mm; examine with hand lens"
        ],
        "morphology_reference":FNA
      },
      "comparisons":[{"taxon":"Muhlenbergia rigens","key_difference":"FNA notes M. dubia has more loosely contracted panicles, longer ligules, longer lemmas and olivaceous anthers."},
                     {"taxon":"Muhlenbergia lindheimeri","key_difference":"Compare culm habit, ligule, leaf width and panicle; do not distinguish by clump outline alone."}],
      "curation_status":{
          "taxonomy_reviewed":True,"taxon_name_verified":True,"visual_reviewed":False,
          "photo_source_checked":True,"user_approved":True,"provisional":True,
          "county_range_reviewed":False,"source_concept_reconciled":True,
          "last_reviewed":"2026-10-19"
      },
      "photo_note":"Two publicly reusable Commons images physically installed and licensed; one wild flowering habit, one garden tuft. Both are provisional recognition photos, NOT final close-up ligule/spikelet diagnosis.",
      "learner_visual_status":"provisional_learner_ready",
      "images":images,
      "taxonomy_source":POWO,
      "morphology_source":FNA
    })
    save(NEW/"species.json",repaired)
    (NEW/"SOURCES.txt").write_text(
        "Accepted name and range: "+POWO+"\n"
        "Pine muhly authoritative name: https://www.npsot.org/posts/native-plant/muhlenbergia-dubia/\n"
        "Verified ITIS name: https://www.itis.gov/servlet/SingleRpt/SingleRpt?search_topic=TSN&search_value=41906\n"
        "FNA diagnostic morphology: "+FNA+"\n"
        "Source typo is NOT botanical synonym: 'Muhlenbergia piniflora'; historical record retained in research-drafts/muhlenbergia-piniflora/draft.json.\n"
        "Wikimedia photo sources:\n"+ "\n".join(p["source_page"]+" | "+p["creator"]+" | "+p["license"]+" | "+p["license_url"] for p in PHOTO)+"\n"
        "Photos saved in local JPEG with EXIF/GPS removed. Native county audit still deferred.\n"
    ,encoding="utf-8")
    draft=load(DRAFT)
    draft["draft_status"]="RESOLVED_SOURCE_TYPO_CORRECTED_CANONICAL"
    draft["taxonomy"]["status"]="RESOLVED_ORIGINAL_LABEL_ERRONEOUS"
    draft["taxonomy"]["accepted_taxon"]="Muhlenbergia dubia E.Fourn."
    draft["taxonomy"]["original_label_is_botanical_synonym"]=False
    draft["taxonomy"]["resolution_sources"]=[POWO,"https://www.npsot.org/posts/native-plant/muhlenbergia-dubia/"]
    draft["provisional_promotion"]["status"]="CORRECTED_REPLACED_BY_ACCEPTED_TAXON"
    draft["provisional_promotion"]["canonical_path"]=str((NEW/"species.json").relative_to(ROOT))
    draft["provisional_promotion"]["original_provisional_path"]="content/taxa/Poaceae/Muhlenbergia/muhlenbergia-piniflora/species.json"
    draft["provisional_promotion"]["resolved_at"]="2026-10-19"
    save(DRAFT,draft)
    genus=load(GENUS)
    scope=genus["project_scope"]
    scope["species_ids"]=["muhlenbergia-dubia" if x=="muhlenbergia-piniflora" else x for x in scope["species_ids"]]
    scope["species_count"]=len(scope["species_ids"])
    scope["flags"]=[x for x in scope.get("flags",[]) if "piniflora" not in x.lower()]
    scope["note"]="Source concept historically labelled M. piniflora was taxonomically resolved as pine muhly M. dubia on 2026-10-19; do not list misspelling as a botanical synonym. Photo gallery remains provisional pending ligule/spikelet diagnostic macro work."
    comp=genus.get("comparison_lesson",{})
    comp["quick_split"]=[("M. dubia — pine muhly; tight upright bunchgrass, usually involute narrow leaves, narrow contracted gray-green panicle; check 4–10 mm ligule and 3.8–5 mm spikelets." if "M. piniflora" in x else x) for x in comp.get("quick_split",[])]
    genus["visual_needs"]=[("M. dubia — add expert-verified ligule 4–10 mm, blades, glumes and single-spikelet macro alongside two credited provisional habit photos" if "M. piniflora" in x else x) for x in genus.get("visual_needs",[])]
    genus.setdefault("visual_anchors",[]).append({"species_id":"muhlenbergia-dubia","roles":["Wild narrow-panicle habit (CC0)", "Cultivated tufted habit (public domain)"],"status":"provisional; no verified macro ligule/spikelet arrows"})
    genus["fast_fill_note"]=str(genus.get("fast_fill_note","")).replace("M. piniflora remains excluded from fast-fill because its canonical record is scientifically PROVISIONAL and likely represents an erroneous source name. Do not pad wild-type lessons with named cultivars or uncertain-rights media.","M. dubia source-label correction completed; two public-reuse-approved photos installed and physically verified; macro ligule/spikelet details still needed.")
    save(GENUS,genus)
    shutil.rmtree(OLD)
    sys.path.insert(0,str(ROOT))
    from scripts.curation_pipeline import rebuild_manifest,rebuild_photo_fast_fill_queue
    status={}
    rebuild_manifest(status)
    rebuild_photo_fast_fill_queue()
    subprocess.run([sys.executable,str(ROOT/"scripts/refresh_photo_coverage_snapshot.py")],cwd=ROOT,check=True)
    new_ids={x["id"] for x in load(MANIFEST)["species"]}
    if len(new_ids)!=len(installed) or "muhlenbergia-piniflora" in new_ids or "muhlenbergia-dubia" not in new_ids:
        raise RuntimeError("Post-migration manifest invalid")
    for row in images:
        item=NEW/row["file"]
        if hashlib.sha256(item.read_bytes()).hexdigest()!=row["sha256"]:
            raise RuntimeError("Final image checksum mismatch")
        with Image.open(item) as im:
            im.verify()
    report={
      "status":"INSTALLED_TAXON_CORRECTION","original_name":"Muhlenbergia piniflora",
      "corrected_name":"Muhlenbergia dubia","original_is_valid_synonym":False,
      "count_before":len(installed),"count_after":len(new_ids),
      "physical_photos_added":len(images),"photo_licensing":["CC0 1.0","Public Domain (PD-self)"],
      "photo_files":checks,"taxonomy_backbone":POWO,"morphology_source":FNA,
      "source_provenance_retained":str(DRAFT.relative_to(ROOT)),
      "county_nativity_status":"UNRESOLVED: county audit deferred",
      "visual_status":"provisional; diagnostic macros still needed"
    }
    save(REPORT,report)
    print(json.dumps(report,indent=2))
if __name__=="__main__":
    go()
