#!/usr/bin/env python3
"""Lane 3 Muhlenbergia utilis: source-specific open-license photo inventory.

This generates a source manifest ONLY: no photos added to the canonical card.
"""
import datetime,json,pathlib,time,urllib.parse,urllib.request
dest=pathlib.Path("reports/lane3-utilis-inat-open-license-scout-20261026.json")
taxon="Muhlenbergia utilis"
result={"searched_at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"taxon":taxon,"status":"HOLD","sources":[],"errors":[],"notes":"Sources are provisional exact-observation names only, not verified plant or cropped root anatomy. Only CC0/CC BY/CC BY-SA/CC BY-NC/CC BY-NC-SA are considered potentially usable on current noncommercial credited public learner."}
def get_json(url):
 req=urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotanyPhotoSourceAudit/1.0 (github.com/Crking92/Hays-County-Botany)","Accept":"application/json"})
 with urllib.request.urlopen(req,timeout=25) as h:return json.loads(h.read(8000000))
taxon_id=None
try:
 taxa=get_json("https://api.inaturalist.org/v1/taxa/autocomplete?q=Muhlenbergia%20utilis")
 exact=[t for t in taxa.get("results",[]) if t.get("name")==taxon and t.get("rank")=="species"]
 if not exact:raise ValueError("Exact iNaturalist taxon unresolved; never query broad genus as same species")
 taxon_id=exact[0]["id"]
 result["inaturalist_taxon_id"]=taxon_id
except Exception as e:result["errors"].append("Taxon lookup: "+str(e)[:200])
if taxon_id:
 for page in [1,2]:
  params={"taxon_id":taxon_id,"quality_grade":"research","photos":"true","per_page":100,"page":page,"order":"desc","order_by":"observed_on"}
  url="https://api.inaturalist.org/v1/observations?"+urllib.parse.urlencode(params)
  try:
   observations=get_json(url)
   result["total_matching_observations"]=observations.get("total_results")
   for o in observations.get("results",[]):
    determined=(o.get("taxon") or {}).get("name")
    if determined!=taxon:continue
    for p in o.get("photos",[]):
     id=p.get("id")
     lic=str(p.get("license_code") or "").lower()
     if lic not in ["cc0","cc-by","cc-by-sa","cc-by-nc","cc-by-nc-sa"]:continue
     creator=p.get("attribution") or o.get("user",{}).get("login")
     row={
      "photo_id":id,"license_code":lic,"creator_source":creator,
      "source_page":f"https://www.inaturalist.org/photos/{id}",
      "observation":f"https://www.inaturalist.org/observations/{o['id']}",
      "observation_id":o["id"],"taxon":determined,
      "quality_grade":o.get("quality_grade"),"place_guess":o.get("place_guess"),
      "taxon_determination_only":"Research grade name from original observation; still needs anatomy and expert checks.",
      "photo_url":p.get("url"),"width":p.get("width"),"height":p.get("height")
     }
     result["sources"].append(row)
   if len(observations.get("results",[]))<100:break
  except Exception as e:result["errors"].append("Observations page "+str(page)+": "+str(e)[:220])
  time.sleep(1)
result["sources"]=sorted(result["sources"],key=lambda o:({"cc0":0,"cc-by":1,"cc-by-sa":2,"cc-by-nc":3,"cc-by-nc-sa":4}.get(o["license_code"],10),str(o["photo_id"])))
result["source_count"]=len(result["sources"])
result["status"]="SOURCES_FOUND_NEEDS_PIXELS_AND_IMAGE_LEVEL_REVIEW" if result["sources"] else "NO_OPEN_LICENSE_EXACT_OBSERVATIONS_CONFIRMED"
dest.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({"status":result["status"],"source_count":len(result["sources"]),"inaturalist_taxon_id":taxon_id,"errors":result["errors"],"first":result["sources"][:12]}))
