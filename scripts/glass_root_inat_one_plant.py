#!/usr/bin/env python3
"""FAST lane: pull and preview a single exact iNaturalist species for a private reviewer.
No species files modified; source photo's native license preserved separately from user
photographer's direct CC BY license grant. No observation coordinates saved.
"""
import argparse
import collections
import csv
import datetime as dt
import json
import pathlib
import sys
import time
import urllib.parse
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent.parent))
from scripts.glass_root_inat_photo_metadata import API, FIELDS, get_json, photo_rows, save_csv
from scripts.glass_root_inat_review_previews_batch006 import choose, draw_sheet, retrieve, safe_url, owner_credit

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--species",default="Sambucus canadensis")
    p.add_argument("--id",default="sambucus-canadensis")
    p.add_argument("--canonical-path",default="content/taxa/Viburnaceae/Sambucus/sambucus-canadensis/species.json")
    p.add_argument("--user",default="calvinking")
    p.add_argument("--out",default="workflow/glass-root-inat/one-plant-001")
    p.add_argument("--limit",type=int,default=8)
    a=p.parse_args()
    started=time.monotonic()
    out=pathlib.Path(a.out);out.mkdir(parents=True,exist_ok=True)
    canonical=pathlib.Path(a.canonical_path)
    if not canonical.exists():raise RuntimeError("Existing canonical species not found")
    species=json.loads(canonical.read_text(encoding="utf-8"))
    if species["id"]!=a.id or species.get("scientific_name")!=a.species:
        raise RuntimeError("Exact canonical species mismatch")
    # Exact species by observer and Texas; typically a single API request.
    observations=[];page=1
    while page<=3:
        q=urllib.parse.urlencode({
            "user_id":a.user,"taxon_name":a.species,"place_id":18,
            "quality_grade":"research","per_page":100,"page":page,
            "order_by":"id","order":"asc"
        })
        data=get_json(API+"?"+q)
        batch=data.get("results",[])
        observations.extend(o for o in batch if (o.get("user") or {}).get("login","").lower()==a.user.lower() and
                            (o.get("taxon") or {}).get("name")==a.species)
        total=data.get("total_results",len(batch))
        print("Exact species API page",page,"results",len(batch),"total",total,flush=True)
        if page*100>=total or not batch:break
        page+=1
        time.sleep(1)
    if page==3 and page*100<total:
        raise RuntimeError("Safety page cap reached; incomplete observation retrieval")
    if not observations:
        raise RuntimeError("No exact-species observations were returned: check iNaturalist taxon name")
    all_rows,nobs,nophoto=photo_rows(observations,{a.id},a.user)
    rows=[r for r in all_rows if r["canonical_id"]==a.id and owner_credit(r)]
    save_csv(out/"photo-candidates.csv",FIELDS,rows)
    ids_already={str(x.get("photo_id")) for x in species.get("images",[]) if x.get("photo_id")}
    remaining=[r for r in rows if r["photo_id"] not in ids_already]
    selections=choose(remaining, min(a.limit,12))
    pictures=[]; candidates=[]
    preview_root=out/"previews"/a.id
    preview_root.mkdir(parents=True,exist_ok=True)
    for r in selections:
        image_url=safe_url(r["image_url"])
        if not image_url:continue
        im=retrieve(image_url)
        if im is None:continue
        im.thumbnail((800,800))
        name="inat-"+r["photo_id"]+".jpg"
        im.save(preview_root/name,format="JPEG",quality=85,optimize=True)
        c={k:r.get(k,"") for k in ["scientific_name","canonical_id","observation_id","observation_url","photo_id","photo_page","source_license","source_attribution","rights_gate","observed_on","quality_grade"]}
        c.update({"review_preview_path":str(preview_root/name),"diagnostic_role":"needs_photo_review",
                  "not_canonical_photo":True})
        candidates.append(c);pictures.append((r,im))
        time.sleep(0.3)
    if pictures:
        draw_sheet(pictures,a.species,out/"previews"/(a.id+"-contact-sheet.jpg"))
    result={"purpose":"One-species fast preview; no species files edited", "taxon":a.species,
        "canonical_id":a.id,"installed_photo_count_before":len(species.get("images",[])),
        "observations_retrieved":nobs,"photo_records_found":len(rows),
        "candidate_photo_previews":len(candidates),"photo_ids":[r["photo_id"] for r in candidates],
        "license_counts":dict(collections.Counter(r["source_license"] for r in rows)),
        "owner_stated_license":"Glass Root Garden CC BY 4.0 direct photo-owner authorization",
        "elapsed_seconds_in_script":round(time.monotonic()-started,2),
        "source_note":"iNaturalist per-photo source metadata retained; no automatic license overwrite",
        "guardrails":["Existing canonical photos preserved","No EXIF/location data exported",
                      "Requires botanical visual review before installation"]}
    (out/"result.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    (out/"priority-candidates.json").write_text(json.dumps({"taxa":{a.id:{"taxon":a.species,"previews_created":len(candidates),"candidates":candidates}}},indent=2)+"\n",encoding="utf-8")
    print("ONE PLANT FAST RESULT",json.dumps(result),flush=True)
if __name__=="__main__":main()
