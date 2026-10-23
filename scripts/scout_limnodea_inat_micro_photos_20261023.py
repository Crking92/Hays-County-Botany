#!/usr/bin/env python3
"""Read-only iNaturalist research grade Limnodea photo metadata scout.
Only original source/license evidence; does NOT install or claim new JPEGs.
"""
from pathlib import Path
import json,requests,time
URL="https://api.inaturalist.org/v1/observations/species_counts"
TAXON=223773
s=requests.Session();s.headers.update({"User-Agent":"HaysBotany-LimnodeaLicensedMicroSourceScout/1.0","Accept":"application/json"})
report={"taxon":"Limnodea arkansana","taxon_id":TAXON,"queries":[],"observations":[],"candidate_photos":[],"note":"Source taxonomy, exact original photo license and pixel proof still independently required; no images installed"}
for quality,pg in [("research",1),("research",2),("needs_id",1)]:
 url="https://api.inaturalist.org/v1/observations"
 args={"taxon_id":TAXON,"photos":"true","quality_grade":quality,"per_page":100,"page":pg,"order":"desc","order_by":"created_at"}
 try:
  resp=s.get(url,params=args,timeout=36);resp.raise_for_status()
  d=resp.json();items=d.get("results",[])
  report["queries"].append({"quality":quality,"page":pg,"total":d.get("total_results"),"count":len(items)})
  for o in items:
   ps=o.get("photos") or []
   ob={"observation_id":o.get("id"),"url":f"https://www.inaturalist.org/observations/{o.get('id')}","quality":o.get("quality_grade"),"taxon":(o.get("taxon") or {}).get("name"),"observer":(o.get("user") or {}).get("login"),"date":o.get("observed_on"),"region":o.get("place_guess"),"photo_count":len(ps),"description":(o.get("description") or "")[:180]}
   report["observations"].append(ob)
   for i,p in enumerate(ps):
    l=p.get("license_code") or "unknown"
    if l.lower() not in ["cc0","cc-by","cc-by-sa","cc-by-nc","cc-by-nc-sa"]:continue
    report["candidate_photos"].append({"observation_id":o.get("id"),"photo_id":p.get("id"),"position":i,"license":l,"attribution":p.get("attribution"),"url":p.get("url"),"original_url":p.get("url","").replace("/square.","/original.").replace("/small.","/original.").replace("/medium.","/original.").replace("/large.","/original."),"observation_url":ob["url"],"observation_photo_count":len(ps),"photo_source_organ_guess":"UNKNOWN — needs visual pixel inspection before describing glumes/lemma/ligule"})
 except Exception as error:
  report["queries"].append({"quality":quality,"page":pg,"error":str(error)[:250]})
for q in report["candidate_photos"]:
 q["priority"]=int(q["observation_photo_count"]>=3)*10 + int(q["observation_photo_count"]>=5)*12 + int(q["position"]>0)*4 + int(q["license"].lower() in {"cc0","cc-by","cc-by-sa"})*8
report["candidate_photos"].sort(key=lambda p:p["priority"],reverse=True)
p=Path("reports/limnodea-inat-potential-fine-macro-scout-20261023.json")
p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
print("done: queries",report["queries"],"candidate licensed photos",len(report["candidate_photos"]))
