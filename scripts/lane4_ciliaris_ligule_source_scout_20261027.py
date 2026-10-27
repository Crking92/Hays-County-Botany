#!/usr/bin/env python3
"""Read-only photo-level source check; do not archive a wrong Digitaria photo."""
import json, pathlib, urllib.request, urllib.error, urllib.parse, time, re
ids={"469014483":"possible sheath/collar macro","469014500":"possible ligule/sheath macro","469014510":"hidden face / upper glume macro"}
out={"species":"Digitaria ciliaris","examined_photo_ids":ids,"results":[],"errors":[],"license_policy":"No copying or D. ciliaris gallery promotion without exact original observation determination and individual photo license; CC BY-NC possible only on genuinely noncommercial website."}
def get(url):
 for n in range(3):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"HaysBotany-Lane4 field-study source audit (github repository)"})
   with urllib.request.urlopen(req,timeout=35) as f:return json.loads(f.read(1_500_001))
  except Exception as e:
   if n==2:raise
   time.sleep(2*(n+1))
for photo_id in ids:
 for url in [f"https://api.inaturalist.org/v1/photos/{photo_id}",f"https://www.inaturalist.org/photos/{photo_id}.json"]:
  try:
   d=get(url)
   q=d.get("results",[d]) if isinstance(d,dict) else d
   if q and isinstance(q,list) and isinstance(q[0],dict):
    p=q[0]
    out["results"].append({"photo_id":photo_id,"method":url,"data":{k:p.get(k) for k in ["id","url","license_code","attribution","observation_id","user_id"] if k in p},"photo_with_observation":p.get("observation",{}).get("taxon",{}).get("name") if isinstance(p.get("observation"),dict) else None})
    break
  except Exception as e:out["errors"].append({"photo_id":photo_id,"path":url,"reason":repr(e)[:190]})
for species in ["Digitaria ciliaris","Digitaria sanguinalis"]:
 url="https://api.inaturalist.org/v1/observations?"+urllib.parse.urlencode({"user_id":"hrosenswdpi","taxon_name":species,"photos":"true","per_page":200,"order_by":"created_at","order":"desc"})
 try:
  j=get(url)
  hits=[]
  for o in j.get("results",[]):
   for p in o.get("photos",[]):
    if str(p.get("id")) in ids:
     hits.append({"photo_id":p.get("id"),"role":ids[str(p.get("id"))],"observation_id":o.get("id"),"taxon":o.get("taxon",{}).get("name"),"taxon_id":o.get("taxon",{}).get("id"),"photo_license":p.get("license_code"),"photographer":p.get("attribution"),"photo_url":p.get("url"),"observed_on":o.get("observed_on"),"quality_grade":o.get("quality_grade")})
  out["results"].append({"query":species,"total":j.get("total_results"),"returned":len(j.get("results",[])),"exact_target_photo_hits":hits})
 except Exception as e:out["errors"].append({"query":species,"reason":repr(e)[:220]})
p=pathlib.Path("reports/lane4-ciliaris-ligule-source-scout-20261027.json")
p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps(out,indent=2),flush=True)
