#!/usr/bin/env python3
"""Review-only iNaturalist photo inventory for Joey Santore, limited to project counties.
No photographs downloaded, no canonical pages or nativity classifications modified.
"""
import argparse, collections, csv, datetime, json, pathlib, re, time, urllib.parse, urllib.request, urllib.error
API="https://api.inaturalist.org/v1"
USER="joeysantore"
COUNTIES="Tom Green,Concho,McCulloch,San Saba,Burnet,Llano,Mason,Menard,Schleicher,Sutton,Kimble,Gillespie,Blanco,Travis,Hays,Comal,Bexar,Kendall,Kerr,Edwards,Real,Bandera,Uvalde,Medina".split(",")
HEADERS={"User-Agent":"Hays-County-Botany-Joey-Photo-Inventory/1.0","Accept":"application/json"}
PHOTOS=["scientific_name","taxon_rank","common_name","canonical_id","taxon_match","county_matches","observation_id","observation_url","observed_on","quality_grade","photo_id","photo_url","image_url","source_attribution","source_license","photographer_gate","permission_basis","display_credit","already_installed_photo_id","visual_review","diagnostic_role"]
SPECIES=["scientific_name","taxon_rank","canonical_id","observations","photo_count","joey_credited_photos","unverified_credit_photos","already_installed_photo_ids","source_observation","priority"]

def get(path,params):
    url=API+path+"?"+urllib.parse.urlencode(params)
    for i in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers=HEADERS),timeout=45) as r:
                data=json.load(r)
            if not isinstance(data.get("results"),list): raise ValueError("Unexpected API data: "+path)
            return data
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as e:
            if isinstance(e,urllib.error.HTTPError) and e.code not in (429,500,502,503,504): raise
            if i==4: raise
            time.sleep(min(30,2**i+2))

def norm(s):
    return re.sub("[^a-z0-9]","",re.sub(r"\bcounty\b","",s.lower()))
def slug(s):
    return re.sub("[^a-z0-9]+","-",s.lower()).strip("-")
def large(url):
    if not url.startswith("https://"):return ""
    return re.sub(r"/(?:square|thumb|small|medium)\.(jpg|jpeg|png|webp)(?=\?|$)",r"/large.\1",url,count=1,flags=re.I)
def safe(v):
    v=str(v if v is not None else "")
    return "'"+v if v and v[0] in "=+-@\t\r" else v
def write_csv(path,columns,rows):
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=columns);w.writeheader()
        for row in rows:w.writerow({k:safe(row.get(k,"")) for k in columns})
def ids_for_counties(counties,pause):
    found={};unresolved=[]
    for county in counties:
        res=get("/places/autocomplete",{"q":county,"per_page":100})
        options=[]
        for place in res["results"]:
            nm=place.get("name") or ""
            dn=place.get("display_name") or ""
            anc=[str(x) for x in (place.get("ancestor_place_ids") or [])]
            texas="18" in anc or bool(re.search(r"(?:^|[, ])(?:TX|Texas)(?:[, ]|$)",dn,re.I))
            if norm(nm)==norm(county) and texas and place.get("id"): options.append(int(place["id"]))
        options=list(dict.fromkeys(options))
        if len(options)==1 and options[0] not in found:found[options[0]]=county
        else:unresolved.append({"county":county,"matching_ids":options})
        time.sleep(pause)
    if unresolved:raise RuntimeError("County IDs unresolved; refused incomplete data: "+json.dumps(unresolved))
    return found
def installed_index(manifest_path):
    data=json.loads(manifest_path.read_text(encoding="utf-8"))
    ids=set();photoids=set()
    for obj in data.get("species",[]):
        ids.add(obj["id"])
        file=manifest_path.parent.parent / obj["path"]
        if not file.is_file():continue
        try:raw=json.loads(file.read_text(encoding="utf-8"))
        except (OSError,ValueError):continue
        for im in raw.get("images",[]):
            if im.get("photo_id"):photoids.add(str(im["photo_id"]))
            for key in ("photo_page","source_url","source_page","url"):
                v=im.get(key)
                if isinstance(v,str):
                    match=re.search(r"inaturalist\.org/photos/(\d+)",v)
                    if match:photoids.add(match.group(1))
    return ids,photoids
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",default="data/manifest.json")
    p.add_argument("--out",default="workflow/joey-inat-photo-inventory")
    p.add_argument("--pause",type=float,default=.3)
    p.add_argument("--max-pages",type=int,default=40)
    a=p.parse_args()
    placeids=ids_for_counties(COUNTIES,a.pause)
    known,previous=installed_index(pathlib.Path(a.manifest))
    rows=[];obsids=set();taxa=set()
    page=1
    while page<=a.max_pages:
        data=get("/observations",{"user_id":USER,"taxon_id":47126,"place_id":",".join(map(str,placeids)),"photos":"true","per_page":200,"page":page,"order_by":"id","order":"asc"})
        items=data["results"];total=int(data.get("total_results",len(items)))
        print("Page",page,":",len(items),"of",total,"observations",flush=True)
        for obs in items:
            if (obs.get("user") or {}).get("login","").lower()!=USER:continue
            oid=str(obs.get("id") or "")
            if not oid or oid in obsids:continue
            obsids.add(oid)
            t=obs.get("taxon") or {};name=t.get("name") or obs.get("species_guess") or ""
            if not name:continue
            taxa.add(name);sid=slug(name)
            counties="; ".join(sorted({placeids[int(x)] for x in obs.get("place_ids",[]) if str(x).isdigit() and int(x) in placeids})) or "in county union; no exact county inferred"
            pics=obs.get("photos") or [x.get("photo",{}) for x in (obs.get("observation_photos") or [])]
            for photo in pics:
                if not photo.get("id"):continue
                pid=str(photo["id"]);credit=photo.get("attribution") or ""
                joey=any(v in credit.lower() for v in ("joeysantore","joey santore","joseph santore"))
                rows.append({"scientific_name":name,"taxon_rank":t.get("rank") or "","common_name":t.get("preferred_common_name") or "",
                  "canonical_id":sid if sid in known else "","taxon_match":"exact_slug_requires_identity_check" if sid in known else "unmatched_or_alias",
                  "county_matches":counties,"observation_id":oid,"observation_url":"https://www.inaturalist.org/observations/"+oid,
                  "observed_on":obs.get("observed_on") or "","quality_grade":obs.get("quality_grade") or "",
                  "photo_id":pid,"photo_url":"https://www.inaturalist.org/photos/"+pid,"image_url":large(photo.get("url") or ""),
                  "source_attribution":credit,"source_license":photo.get("license_code") or "none_recorded",
                  "photographer_gate":"joey_credited_candidate" if joey else "HOLD_photographer_unconfirmed",
                  "permission_basis":"Joey profile: non-commercial educational use with credit" if joey else "individual rights not confirmed",
                  "display_credit":"Photo: Joey Santore / iNaturalist" if joey else "verify photographer",
                  "already_installed_photo_id":"yes" if pid in previous else "not_detected",
                  "visual_review":"pending","diagnostic_role":"not_assessed"})
        if not items or 200*page>=total:break
        page+=1;time.sleep(a.pause)
    else:raise RuntimeError("Pagination safety limit reached; no partial results saved")
    if not rows:raise RuntimeError("No photos returned; refused misleading empty catalog")
    rows.sort(key=lambda x:(x["scientific_name"].lower(),x["observation_id"],x["photo_id"]))
    grouped=collections.defaultdict(list)
    for row in rows:grouped[row["scientific_name"]].append(row)
    summaries=[]
    for name,photos in grouped.items():
        x=photos[0];credited=sum(y["photographer_gate"]=="joey_credited_candidate" for y in photos)
        summaries.append({"scientific_name":name,"taxon_rank":x["taxon_rank"],"canonical_id":x["canonical_id"],
          "observations":len({y["observation_id"] for y in photos}),"photo_count":len(photos),
          "joey_credited_photos":credited,"unverified_credit_photos":len(photos)-credited,
          "already_installed_photo_ids":sum(y["already_installed_photo_id"]=="yes" for y in photos),
          "source_observation":x["observation_url"],"priority":"existing_species_enrichment" if x["canonical_id"] else "verify_alias_or_pool"})
    summaries.sort(key=lambda x:(not bool(x["canonical_id"]),-x["joey_credited_photos"],x["scientific_name"]))
    out=pathlib.Path(a.out);out.mkdir(parents=True,exist_ok=True)
    write_csv(out/"photo-candidates.csv",PHOTOS,rows)
    write_csv(out/"species-photo-summary.csv",SPECIES,summaries)
    report={"date_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"observer":USER,"profile":"https://www.inaturalist.org/people/joeysantore",
      "region":"24 Central/West Texas project-rule counties","counties":COUNTIES,"county_place_ids":{str(k):v for k,v in placeids.items()},
      "observations":len(obsids),"taxa":len(taxa),"taxa_with_photos":len(summaries),"photos":len(rows),
      "photos_credited_to_joey":sum(x["photographer_gate"]=="joey_credited_candidate" for x in rows),
      "photos_with_other_or_unclear_credit":sum(x["photographer_gate"]!="joey_credited_candidate" for x in rows),
      "photo_rows_matching_installed_species":sum(bool(x["canonical_id"]) for x in rows),
      "existing_gallery_photo_id_duplicates":sum(x["already_installed_photo_id"]=="yes" for x in rows),
      "license_counts":dict(collections.Counter(x["source_license"] for x in rows)),
      "guardrails":"Only metadata inventoried. No photograph installed or downloaded. Joey's public grant covers his own photos for non-commercial educational use with credit; preserve per-photo license. No nativity or taxonomy change; no coordinates stored."}
    (out/"summary.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2),flush=True)
if __name__=="__main__":main()
