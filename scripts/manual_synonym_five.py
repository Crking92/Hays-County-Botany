#!/usr/bin/env python3
"""First-time Master Pool cards using license-verified research-grade iNaturalist photos.
Not a visual/diagnostic identification certification. Does not rely on Joey's inventory.
"""
import csv
import hashlib
import io
import re
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
PLAN=ROOT/"workflow/manual-synonym-five-current.json"
BATCH_ID=json.loads(PLAN.read_text())["batch_id"]
if not re.fullmatch(r"[a-z0-9][a-z0-9-]{5,90}", BATCH_ID):
    raise RuntimeError("Invalid batch id")
MANIFEST=ROOT/"data/manifest.json"
PREFLIGHT=ROOT/"research-drafts/reconciliation/phase3-consolidated-card-workload-2026-10-15.json"
CLAIMS=ROOT/"workflow/work-claims.json"
STAGING=ROOT/"research-drafts/photo-imports"/BATCH_ID
BATCH=ROOT/"curation-inbox"/BATCH_ID
OUTPUT=ROOT/"reports"/(BATCH_ID+"-installed.json")
ALLOWED={
 "cc0":("CC0","Public domain dedication; verify attribution"),
 "public-domain":("Public Domain","Public domain US National Park Service government employee image"),
 "cc-by-4.0":("CC BY 4.0","Credit author; link license and state image has been resized, see https://creativecommons.org/licenses/by/4.0/"),
 "cc-by":("CC BY","Attribution required"),
 "cc-by-sa":("CC BY-SA","Attribution; ShareAlike requirements"),
 "cc-by-nc":("CC BY-NC","Attribution; noncommercial only"),
 "cc-by-nc-sa":("CC BY-NC-SA","Attribution; noncommercial and ShareAlike requirements")
}
UA={"User-Agent":"HaysBotanyPrivateEducationalFirstCard/1.0 (science photo curation)"}

def request(url, limit=3500000):
    last=None
    for attempt in range(3):
        try:
            with urlopen(Request(url,headers=UA),timeout=30) as rs:
                data=rs.read(limit+1)
            if len(data)>limit:raise ValueError("oversized response")
            return data
        except (HTTPError,URLError,TimeoutError) as e:
            last=e
            if isinstance(e,HTTPError) and e.code not in (429,500,502,503,504):
                raise
            time.sleep(2.5*(attempt+1))
    raise last

def api(route, params=None):
    url="https://api.inaturalist.org/v1/"+route
    if params:url+="?"+urlencode(params)
    return json.loads(request(url,5500000))

def exact_species_taxon(name, rank="species"):
    if rank not in ("species","subspecies","variety","hybrid"):
        raise ValueError("Unsupported source name rank: "+str(rank))
    data=api("taxa/autocomplete",{"q":name,"per_page":30}).get("results",[])
    hits=[x for x in data if x.get("name")==name and x.get("rank")==rank and x.get("is_active", True)]
    if len(hits)!=1:raise ValueError("No unique exact "+rank+" source taxon in live iNaturalist taxonomy for "+name)
    return hits[0]["id"]

def license_photo(name, taxon_id, issues):
    checked=0
    for page in (1,2,3,4):
        observations=api("observations",{
           "taxon_id":taxon_id,"quality_grade":"research",
           "photos":"true","per_page":12,"page":page,
           "order_by":"votes","order":"desc"
        }).get("results",[])
        if not observations:break
        for obs in observations:
            if (obs.get("taxon") or {}).get("name")!=name:continue
            if obs.get("quality_grade")!="research":continue
            for photo in obs.get("photos") or []:
                checked+=1
                code=(photo.get("license_code") or "").lower()
                if code not in ALLOWED:continue
                credit=photo.get("attribution") or ""
                if not credit or ("rights reserved" in credit.lower() and "some rights reserved" not in credit.lower()):
                    continue
                url=photo.get("url") or ""
                for sz in ("square","thumb","small","medium"):
                    url=url.replace("/"+sz+".","/large.")
                if not url.startswith("https://"):continue
                try:
                    imgbytes=request(url,12000000)
                    with Image.open(io.BytesIO(imgbytes)) as im:im.verify()
                    with Image.open(io.BytesIO(imgbytes)) as im:
                        if min(im.size)<350:raise ValueError("image below 350px")
                        resized=im.convert("RGB")
                        resized.thumbnail((1800,1800))
                        b=io.BytesIO()
                        resized.save(b,format="JPEG",quality=87,optimize=True)
                        payload=b.getvalue()
                    pid=str(photo["id"])
                    return {
                      "bytes":payload,"photo_id":pid,
                      "observation_id":str(obs["id"]),
                      "attribution":credit,"license_code":code,
                      "image_url":url,
                      "source_page":"https://www.inaturalist.org/photos/"+pid,
                      "observation_page":"https://www.inaturalist.org/observations/"+str(obs["id"]),
                      "width":resized.width,"height":resized.height,
                      "checked_candidates":checked
                    }
                except Exception as e:
                    issues.append("image "+str(photo.get("id"))+": "+str(e)[:130])
                if checked>=100:break
            if checked>=100:break
        if checked>=100:break
    return None

def commons_exact_image(item, candidate):
    """Retrieve a reviewer-identified, Wikimedia-licensed exact taxon photograph.

    Independently confirms file format, dimensions, origin and strips EXIF/GPS.
    Source taxon and copyright are declared from checked Wikimedia file description;
    this is NOT an iNaturalist RG observation or completed visual anatomy review.
    """
    exact_name=item["scientific_name"]
    source_taxon=candidate["name"]
    expected_rank=("variety" if item.get("infraspecific_rank")=="variety" else
                   "subspecies" if item.get("infraspecific_rank")=="subspecies" else "species")
    expected_source_name=(item["genus"]+" "+item["epithet"]+" "+item["infraspecific_epithet"]
                          if expected_rank!="species" else exact_name)
    if (candidate.get("rank")!=expected_rank or source_taxon!=expected_source_name
        or candidate.get("reviewed_exact_taxon") is not True):
        raise ValueError("Commons source is not checked to the exact target rank")
    source_page=candidate["source_page"]
    direct_url=candidate["direct_url"]
    if (urlparse(source_page).netloc!="commons.wikimedia.org"
        or urlparse(direct_url).netloc!="upload.wikimedia.org"
        or not urlparse(direct_url).path.lower().endswith((".jpg",".jpeg"))):
        raise ValueError("Photo URLs must resolve to official Wikimedia Commons upload source")
    code=candidate["license_code"]
    if code not in ("public-domain","cc-by-4.0"):
        raise ValueError("Unreviewed Commons license")
    credit=candidate.get("creator")
    if not credit or not candidate.get("photo_id") or not candidate.get("rights_reviewed"):
        raise ValueError("Missing manually reviewed source rights or provenance")
    if candidate.get("work_description") is None:
        raise ValueError("No taxon-identity source description")
    original=request(direct_url,12000000)
    with Image.open(io.BytesIO(original)) as im:
        im.verify()
    with Image.open(io.BytesIO(original)) as im:
        if im.format!="JPEG" or min(im.size)<500:
            raise ValueError("Commons image is not a usable verified JPEG")
        out=im.convert("RGB")
        out.thumbnail((1800,1800))
        buff=io.BytesIO()
        out.save(buff,format="JPEG",quality=87,optimize=True)
        payload=buff.getvalue()
    with Image.open(io.BytesIO(payload)) as safe:
        safe.verify()
    with Image.open(io.BytesIO(payload)) as safe:
        if safe.getexif():
            raise ValueError("Input EXIF persisted in safety-stripped working JPEG")
    return {
        "bytes":payload,"photo_id":candidate["photo_id"],
        "observation_id":candidate.get("observation_id","Commons sourced"),
        "attribution":credit,"license_code":code,"image_url":direct_url,
        "source_page":source_page,"observation_page":source_page,
        "width":out.width,"height":out.height,"checked_candidates":1
    }

def read_state():
    manifest=json.loads(MANIFEST.read_text())
    canonical={e["id"] for e in manifest["species"]}
    active=set()
    for claim in json.loads(CLAIMS.read_text()).get("claims",[]):
        if (claim.get("status") in ("active","queued","blocked") and
            (not claim.get("expires_at") or datetime.fromisoformat(claim["expires_at"].replace("Z","+00:00")) > datetime.now(timezone.utc)) and
            claim.get("claim_id") != ("manual-"+BATCH_ID)):
            active.update(claim.get("taxa") or [])
    queued={x.get("id") for x in json.loads((ROOT/"research-queue.json").read_text()).get("items",[]) if x.get("status") in ("taxonomy_hold","identity_hold","held_identity","pending_taxon_concept")}
    return canonical,active,queued

def build():
    plan=json.loads(PLAN.read_text())
    allowed={p["accepted_working_name"]:{"slug":p["slug"],"caution":None} for p in json.loads(PREFLIGHT.read_text())["concepts"] if any(d in p.get("decisions",[]) for d in ("CONFIRMED_ROUTE_TO_ACCEPTED_SPECIES","CONFIRMED_ACCEPTED_TARGET_NOT_IN_POOL","CONFIRMED_ROUTE_TO_ACCEPTED_DESTINATION","ACCEPTED_INSTALLER_PREFLIGHT_CANDIDATE","CONFIRMED_SYNONYM_TO_ACCEPTED_SPECIES_FRESH_CHECK","CONFIRMED_KEW_TARGET_WITH_REGIONAL_BACKBONE_CAUTION","CONFIRMED_TARGET_WITH_FERN_BACKBONE_CAUTION","CONFIRMED_KEW_TARGET_WITH_ALTERNATIVE_BACKBONE_CAUTION","CONFIRMED_TARGET_WITH_BRYOPHYTE_BACKBONE","PREFLIGHT","CONFIRMED_SYNONYM_TO_ACCEPTED_SUBSPECIES_FRESH_CHECK","CONFIRMED_ACCEPTED_TARGET_WITH_SOURCE_RANK_CAUTION"))}
    installed,active,queued=read_state()
    if BATCH.exists() or OUTPUT.exists():raise RuntimeError("Batch or report exists, refusing overwrite")
    results=[]
    prepared=[]
    for item in plan["selected"]:
        name,slug=item["scientific_name"],item["slug"]
        result={"name":name,"slug":slug,"status":"PENDING","attempts":[]}
        results.append(result)
        if allowed.get(name,{}).get("slug")!=slug or allowed[name].get("caution"):
            result["status"]="HOLD_NOT_PREFLIGHT_CLEARED";continue
        if slug in installed or slug in active or slug in queued:
            result["status"]="SKIP_INSTALLED_CLAIMED_OR_HELD";continue
        concept=next((x for x in json.loads(PREFLIGHT.read_text())["concepts"] if x.get("slug")==slug),None)
        if (concept and "CONFIRMED_ACCEPTED_TARGET_WITH_SOURCE_RANK_CAUTION" in concept.get("decisions",[])
            and not item.get("source_rank_caution_reviewed")):
            result["status"]="HOLD_SOURCE_RANK_CAUTION_UNRESOLVED";continue
        if item.get("source_rank_caution_reviewed"):
            concept=next((x for x in json.loads(PREFLIGHT.read_text())["concepts"] if x.get("slug")==slug),None)
            if (not concept or "CONFIRMED_ACCEPTED_TARGET_WITH_SOURCE_RANK_CAUTION" not in concept.get("decisions",[])
                or item.get("infraspecific_rank")!="subspecies"
                or item.get("photo_lookup_rank")!="subspecies"):
                result["status"]="HOLD_SOURCE_RANK_CAUTION_UNRESOLVED";continue
        # Accept a named variety/subspecies only with an explicitly spelled-out
        # Kew name crosswalk to the exact infraspecific concept. Species-level
        # photo names are never silently converted from the parent species.
        hybrid=item.get("is_hybrid", False)
        expected_base=item["genus"]+" "+("× " if hybrid else "")+item["epithet"]
        rank_label=item.get("infraspecific_rank")
        infra_epithet=item.get("infraspecific_epithet")
        suffix={"variety":"var.","subspecies":"subsp."}.get(rank_label)
        if hybrid and rank_label:
            result["status"]="HOLD_HYBRID_RANK_COMPLEXITY";continue
        expected_name=(expected_base+" "+suffix+" "+infra_epithet) if (suffix and infra_epithet) else expected_base
        normalized=expected_name.lower().replace(".","").replace("×","x").replace(" ","-")
        if name!=expected_name or slug!=normalized or (rank_label and not (suffix and infra_epithet)):
            result["status"]="HOLD_IDENTITY_OR_SLUG";continue
        try:
            if suffix and not (item.get("infraspecific_crosswalk_verified") and "powo.science.kew.org/taxon/" in item.get("synonym_source","")):
                result["status"]="HOLD_UNVERIFIED_INFRASPECIFIC_CROSSWALK";continue
            # Distinct, pre-verified Kew synonyms are alternatives, never
            # guesses based on a visually similar parent species. Each source
            # must be at its exact iNaturalist taxon rank and observation rank.
            candidates=item.get("photo_lookup_candidates") or [{
                "name":item["photo_lookup_name"],
                "rank":item.get("photo_lookup_rank","species"),
                "source":item["synonym_source"],
            }]
            p=None
            photo_name=None
            tid=None
            photo_relation="documented_synonym"
            for candidate in candidates:
                alias=candidate["name"]
                alias_rank=candidate.get("rank","species")
                source=candidate.get("source") or item["synonym_source"]
                relation=candidate.get("relation","documented_synonym")
                if relation=="accepted_child":
                    if (suffix or hybrid or alias_rank not in ("subspecies","variety")
                        or not alias.startswith(name+" ") or "powo.science.kew.org/taxon/" not in source):
                        result["attempts"].append(alias+": invalid accepted-child scope");continue
                elif relation!="documented_synonym":
                    result["attempts"].append(alias+": unreviewed taxon relationship");continue
                fna_bicornis=(slug=="persicaria-bicornis" and alias==name and alias_rank=="species"
                              and "efloras.org/florataxon.aspx?flora_id=1&taxon_id=250060696" in source)
                if "powo.science.kew.org/taxon/" not in source and not fna_bicornis:
                    result["attempts"].append(alias+": source lacks exact POWO or approved FNA species reference")
                    continue
                alias_slug=alias.lower().replace(".","").replace("×","x").replace(" ","-")
                if alias_slug in installed or alias_slug in active:
                    result["attempts"].append(alias+": existing canonical/claimed concept, skipping")
                    continue
                if alias==name and not item.get("exact_source_rank_reviewed"):
                    result["attempts"].append(alias+": direct name not explicitly preflighted")
                    continue
                try:
                    if candidate.get("type")=="commons_exact":
                        test_tid=None
                        test_photo=commons_exact_image(item,candidate)
                        relation="commons_identified_exact_taxon"
                    else:
                        test_tid=exact_species_taxon(alias, alias_rank)
                        test_photo=license_photo(alias,test_tid,result["attempts"])
                    if test_photo is None:
                        result["attempts"].append(alias+": no usable licensed exact-taxon photo")
                        continue
                    photo_name=alias
                    photo_relation=relation
                    tid=test_tid
                    p=test_photo
                    result["synonym_evidence_url"]=source
                    break
                except Exception as exc:
                    result["attempts"].append(alias+": "+str(exc)[:130])
            if p is None:
                result["status"]="NEEDS_FIRST_PHOTO_OR_SOURCE_CHECK";continue
            result["photo_lookup_name"]=photo_name
            result["photo_source_relation"]=photo_relation
            result["iNaturalist_taxon_id"]=tid
            path=STAGING/slug/("inat-"+p["photo_id"]+".jpg")
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(p["bytes"])
            digest=hashlib.sha256(path.read_bytes()).hexdigest()
            with Image.open(path) as im:im.verify()
            result.update(photo_id=p["photo_id"],observation_id=p["observation_id"],source_page=p["source_page"],
                          license_code=p["license_code"],credit=p["attribution"],sha256=digest,width=p["width"],height=p["height"])
            folder=BATCH/"taxa"/item["family"]/item["genus"]/slug
            (folder/"images").mkdir(parents=True,exist_ok=True)
            shutil.copy2(path,folder/"images"/path.name)
            status=ALLOWED[p["license_code"]]
            row={
                "file_name":path.name,"role":"Provisional species recognition photograph; exact source taxon reviewed, diagnostic anatomy not visually certified",
                "creator":p["attribution"],"license":status[0],"source_page":p["source_page"],
                "direct_url":p["image_url"],"study_use":"Noncommercial botanical education",
                "public_reuse":status[1],
                "observation_id":p["observation_id"],"photo_id":p["photo_id"],
            }
            with (folder/"image-sources.csv").open("w",newline="",encoding="utf-8") as f:
                w=csv.DictWriter(f,fieldnames=list(row))
                w.writeheader();w.writerow(row)
            species={
                "id":slug,"family":item["family"],"genus":item["genus"],"species":item["epithet"],
                **({"entry_type":"infraspecific_taxon","infraspecific_rank":rank_label,"infraspecific_epithet":infra_epithet} if suffix else {}),
                **({"entry_type":"hybrid_taxon","is_hybrid":True,"taxonomic_note":"Accepted hybrid × formula and scientific concept verified against Kew; the iNaturalist observation omits the multiplication symbol in its taxon label. Distinguishing hybrid anatomy requires separate visual review."} if hybrid else {}),
                "scientific_name":name,"common_name":item["common_name"],
                "look_here_first":item["look_here_first"],
                "curation_status":{"taxonomy_reviewed":False,"visual_reviewed":False,"photo_source_checked":True},
                "photo_note":("Wikimedia Commons image documented to the exact taxon rank " if photo_relation=="commons_identified_exact_taxon" else ("iNaturalist research-grade observation from accepted child taxon " if photo_relation=="accepted_child" else ("iNaturalist research-grade observation under exact accepted scientific name " if photo_name==name else "iNaturalist research-grade observation under independently documented synonym ")))+photo_name+"; credited license and bytes checked; photo resized and metadata stripped. Provisional recognition only; diagnostic visual review remains pending.",
                "taxonomy_source":item["taxonomy_source"],
                "synonyms":[] if photo_name==name or photo_relation in ("accepted_child","commons_identified_exact_taxon") else [photo_name],
                "photo_observed_taxon":photo_name,
                "photo_observed_taxon_relation":photo_relation,
                "photo_taxonomy_note":"Wikimedia file-level exact-taxonomy image source (not a live iNaturalist RG taxon) or independently reviewed scientific synonym; taxon rank preserved, visual anatomy still provisional.",
            }
            (folder/"species.json").write_text(json.dumps(species,indent=2)+"\n")
            (folder/"SOURCES.txt").write_text(
                "Approved Master Plant Pool preflight; accepted species: "+item["taxonomy_source"]+
                "\nTaxonomic name-synonym evidence: "+item["synonym_source"]+
                "\nObserved scientific name (accepted or documented alias): "+photo_name+
                ("\nWikimedia Commons reviewed source: " if photo_relation=="commons_identified_exact_taxon" else "\nSource research-grade observation: ")+p["observation_page"]+
                "\nPhoto: "+p["source_page"]+
                "\nAttribution: "+p["attribution"]+
                "\nLicense: "+status[0]+"; "+status[1]+
                "\nDiagnostic photo appearance and look-alikes: further visual review required. Native county research deferred.\n"
            )
            result["status"]="PREPARED"
            prepared.append(slug)
        except Exception as e:
            result["status"]="NEEDS_FIRST_PHOTO_OR_SOURCE_CHECK"
            result["attempts"].append(str(e)[:250])
    STAGING.mkdir(parents=True,exist_ok=True)
    (STAGING/"stage-report.json").write_text(json.dumps({"batch":plan["batch_id"],"results":results},indent=2)+"\n")
    if prepared:
        (BATCH/"batch.json").write_text(json.dumps({"batch_id":BATCH.name,"mode":"install","require_exact_images":True,"visual_mode":"learner_fast_fill"},indent=2)+"\n")
        (BATCH/"READY").write_text("First photo physically saved and exact species & license checked; provisional diagnostic review.\n")
        subprocess.run([sys.executable,str(ROOT/"scripts/curation_pipeline.py"),"--apply"],cwd=ROOT,check=True)
    current={x["id"]:x for x in json.loads(MANIFEST.read_text())["species"]}
    verified=[]
    for slug in prepared:
        item=current.get(slug)
        if item is None:raise ValueError("Prepared species absent from canonical manifest: "+slug)
        spath=ROOT/item["path"]
        obj=json.loads(spath.read_text())
        imgs=obj.get("images") or []
        if len(imgs)<1:raise ValueError("New card missing physical image: "+slug)
        for img in imgs:
            path=spath.parent/img["file"]
            with Image.open(path) as im:im.verify()
        next(x for x in results if x["slug"]==slug)["status"]="INSTALLED"
        verified.append(slug)
    report={"batch":plan["batch_id"],"starting_count":len(installed),"manifest_count":len(current),
            "installed_count":len(verified),"installed":verified,"physically_installed_photos":len(verified),
            "blocked":[x for x in results if x["status"]!="INSTALLED"],
            "all_results":results,
            "note":"Images were sourced under documented scientific synonym crosswalks and photo licenses/files checked. Accepted botanical concept saved with traceable alias. Independent image anatomy review and county nativity deferred."}
    OUTPUT.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"installed":verified,"manifest_count":len(current),"blocked_count":len(report["blocked"])}))
if __name__=="__main__":
    build()
