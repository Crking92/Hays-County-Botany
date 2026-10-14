#!/usr/bin/env python3
"""Inventory iNaturalist photos for Glass Root Garden; NEVER installs them.
Reads public iNaturalist API data, records each photo's own license and credit,
and cross-references the canonical Hays Botany manifest. No coordinates stored.
"""
import argparse
import collections
import csv
import datetime as dt
import json
import math
import pathlib
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.inaturalist.org/v1/observations"
HEADERS = {"User-Agent": "HaysBotany-GlassRootGarden-PhotoInventory/1.0 (GitHub: Crking92/Hays-County-Botany)", "Accept": "application/json"}
FIELDS = ["observation_id","observation_url","scientific_name","canonical_id","in_manifest",
          "photo_id","photo_page","image_url","source_license","source_attribution",
          "proposed_learner_credit","proposed_learner_license","rights_gate",
          "observed_on","quality_grade","image_width","image_height",
          "diagnostic_role","image_review","learner_installed"]
def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", (name or "").lower()).strip("-")
def get_json(url):
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.loads(r.read().decode("utf-8"))
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            status = getattr(e, "code", None)
            if status is not None and status not in (429,500,502,503,504):
                raise
            if attempt == 4:
                raise
            time.sleep(min(30, 2 ** attempt + 2))
    raise RuntimeError("unreachable")
def all_observations(user, place_id, taxon_id, max_pages, pause):
    page = 1
    while page <= max_pages:
        args = dict(user_id=user, taxon_id=taxon_id, place_id=place_id,
                    quality_grade="research", per_page=200, page=page,
                    order_by="id", order="asc")
        url = API + "?" + urllib.parse.urlencode(args)
        data = get_json(url)
        results = data.get("results", [])
        if not isinstance(results, list):
            raise ValueError("Unexpected iNaturalist API response")
        total = int(data.get("total_results", len(results)))
        print("Fetched page %s: %s observations (API reports %s)" %
              (page, len(results), total), flush=True)
        for obs in results:
            if (obs.get("user") or {}).get("login","").lower() == user.lower():
                yield obs
        if not results or page * 200 >= total:
            break
        if page == max_pages:
            raise RuntimeError("Page safety cap reached: results incomplete; raise --max-pages")
        page += 1
        time.sleep(pause)
def csv_observations(path, user, pause):
    """Exact observation IDs from an export, batched per iNat recommendations."""
    with open(path, newline="", encoding="utf-8-sig") as f:
        r = csv.DictReader(f)
        ids = list(dict.fromkeys(x["id"] for x in r
                                if x.get("id") and x.get("user_login","").lower()==user.lower()
                                and x.get("iconic_taxon_name","")=="Plantae"))
    for offset in range(0,len(ids),75):
        chunk = ids[offset:offset+75]
        url = API + "/" + ",".join(chunk)
        data = get_json(url)
        results = data.get("results",[])
        observed = {str(x.get("id")) for x in results}
        absent = set(chunk) - observed
        if absent:
            print("WARNING: IDs not returned:", sorted(absent), file=sys.stderr)
        print("Fetched batch %d: %d/%d IDs" %
              (offset//75+1,len(observed),len(chunk)), flush=True)
        for obs in results:
            if (obs.get("user") or {}).get("login","").lower() == user.lower():
                yield obs
        if offset + 75 < len(ids):
            time.sleep(pause)
def own_credit(attribution, user):
    a = (attribution or "").lower()
    return any(word in a for word in (user.lower(),"calvin king","glass root garden"))
def photo_rows(observations, ids, username):
    result=[]; observation_count=0; missing_photos=0; seen=set()
    for obs in observations:
        oid = str(obs.get("id",""))
        if not oid or oid in seen:
            continue
        seen.add(oid)
        observation_count += 1
        scientific = (obs.get("taxon") or {}).get("name") or obs.get("species_guess") or ""
        sid = slug(scientific)
        canonical = sid if sid in ids else ""
        photos = obs.get("photos") or []
        if not photos and obs.get("observation_photos"):
            photos = [x.get("photo",{}) for x in obs["observation_photos"]]
        if not photos:
            missing_photos += 1
        for p in photos:
            if not isinstance(p,dict) or not p.get("id"):
                continue
            credit = p.get("attribution") or ""
            code = (p.get("license_code") or "").lower()
            owner_match = own_credit(credit, username)
            gate = ("candidate_for_visual_review" if code=="cc-by" and owner_match
                    else "verify_license_or_update_pending" if owner_match
                    else "verify_other_photographer_or_source")
            photo_url = p.get("url") or ""
            if re.match(r"^https://(static\.inaturalist\.org|inaturalist-open-data\.s3\.amazonaws\.com)/",photo_url):
                photo_url = re.sub(r"/(square|thumb|small|medium|large)\.(jpg|jpeg|png)",r"/large.\2",photo_url, count=1)
            dims = p.get("original_dimensions") or {}
            result.append({
                "observation_id":oid,
                "observation_url":"https://www.inaturalist.org/observations/"+oid,
                "scientific_name":scientific,
                "canonical_id":canonical,
                "in_manifest":"yes" if canonical else "no_taxonomy_review",
                "photo_id":str(p["id"]),
                "photo_page":"https://www.inaturalist.org/photos/"+str(p["id"]),
                "image_url":photo_url,
                "source_license":code or "none_recorded",
                "source_attribution":credit,
                "proposed_learner_credit":"Glass Root Garden" if owner_match else "",
                "proposed_learner_license":"CC BY 4.0" if owner_match and code=="cc-by" else "",
                "rights_gate":gate,
                "observed_on":obs.get("observed_on") or "",
                "quality_grade":obs.get("quality_grade") or "",
                "image_width":dims.get("width") or "",
                "image_height":dims.get("height") or "",
                "diagnostic_role":"not_yet_assessed",
                "image_review":"pending",
                "learner_installed":"no",
            })
    return result,observation_count,missing_photos
def save_csv(path,fieldnames,rows):
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fieldnames,extrasaction="ignore")
        w.writeheader(); w.writerows(rows)
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--user",default="calvinking")
    parser.add_argument("--place-id",type=int,default=18,help="iNaturalist place ID for Texas")
    parser.add_argument("--taxon-id",type=int,default=47126,help="iNaturalist Plantae")
    parser.add_argument("--csv",help="Use precise observation IDs from the user's export")
    parser.add_argument("--manifest",default="data/manifest.json")
    parser.add_argument("--out",default="workflow/glass-root-inat/output")
    parser.add_argument("--max-pages",type=int,default=45)
    parser.add_argument("--pause",type=float,default=1.25)
    a=parser.parse_args()
    manifest=json.loads(pathlib.Path(a.manifest).read_text(encoding="utf-8"))
    installed={x["id"] for x in manifest.get("species",[])}
    observations=(csv_observations(a.csv,a.user,a.pause) if a.csv
                  else all_observations(a.user,a.place_id,a.taxon_id,a.max_pages,a.pause))
    rows, obs_count, n_no_photos = photo_rows(observations,installed,a.user)
    out=pathlib.Path(a.out); out.mkdir(parents=True,exist_ok=True)
    save_csv(out/"photo-candidates.csv", FIELDS, rows)
    per_species=collections.defaultdict(list)
    for row in rows:
        per_species[(row["scientific_name"],row["canonical_id"])].append(row)
    summary_rows=[]
    for (name,sid), photos in sorted(per_species.items(),key=lambda z:(-len(z[1]),z[0][0])):
        summary_rows.append({
            "scientific_name":name,"canonical_id":sid,
            "in_manifest":"yes" if sid else "no_taxonomy_review",
            "photo_count":len(photos),
            "observation_count":len({p["observation_id"] for p in photos}),
            "cc_by_attributed_candidates":sum(p["rights_gate"]=="candidate_for_visual_review" for p in photos),
            "photo_rights_review":sum(p["rights_gate"]!="candidate_for_visual_review" for p in photos),
            "example_observation":photos[0]["observation_url"]})
    save_csv(out/"species-photo-summary.csv",
             ["scientific_name","canonical_id","in_manifest","photo_count",
              "observation_count","cc_by_attributed_candidates",
              "photo_rights_review","example_observation"],summary_rows)
    s={"generated_at_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
       "user":a.user,"source":"exact CSV observation IDs" if a.csv else "iNaturalist public API; Texas / Plantae / Research Grade",
       "observations_retrieved":obs_count,"observations_without_photos":n_no_photos,
       "photographs_inventoried":len(rows),"distinct_photo_ids":len({x["photo_id"] for x in rows}),
       "species_with_photos":len(summary_rows),
       "photos_of_installed_species":sum(x["in_manifest"]=="yes" for x in rows),
       "candidate_cc_by_with_expected_attribution":sum(x["rights_gate"]=="candidate_for_visual_review" for x in rows),
       "photos_requiring_rights_review":sum(x["rights_gate"]!="candidate_for_visual_review" for x in rows),
       "licenses":dict(collections.Counter(x["source_license"] for x in rows)),
       "limitations":["No photo quality or botanical structures assessed yet.",
                      "Attribution text is not definitive proof of ownership.",
                      "Taxonomy names and photos need visual human review before learner installation.",
                      "No exact or private observation coordinates are stored.",
                      "No photographs downloaded or species cards modified by this metadata-only step."]}
    (out/"summary.json").write_text(json.dumps(s,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(s,indent=2),flush=True)
if __name__=="__main__":
    main()
