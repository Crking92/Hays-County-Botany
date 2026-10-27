#!/usr/bin/env python3
"""Read-only iNaturalist source licensing audit, no media copied."""
import json,urllib.parse,urllib.request,urllib.error,pathlib,time
IDS=[538508085,538508110,439180815,429206275,410714681,217798219]
OUT={"species":"Dichanthelium oligosanthes","source":"https://www.inaturalist.org/posts/86386-photo-guide-to-dichanthelium-of-missouri","candidate_photos":[],"rights_rule":"No archive unless license and exact species taxon are independently checked, including original photo, rather than blog permission.","errors":[]}
def get(url):
 for i in range(3):
  try:
   r=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyLane4PhotoRights/1.0 (educational botanical CC audit)"})
   with urllib.request.urlopen(r,timeout=35) as f:return json.loads(f.read(1500000))
  except Exception as e:
   if i==2:raise
   time.sleep(2*(i+1))
for pid in IDS:
 candidate={"photo_id":pid}
 try:
  obj=get(f"https://api.inaturalist.org/v1/photos/{pid}")
  rows=obj.get("results",[])
  candidate["api_photo"]={k:rows[0].get(k) for k in ["id","license_code","attribution","observation_id","url","original_dimensions"]} if rows else {"keys":list(obj)[:15]}
  oid=candidate["api_photo"].get("observation_id")
  if oid:
   ob=get(f"https://api.inaturalist.org/v1/observations/{oid}").get("results",[])
   if ob:
    o=ob[0]
    candidate["observation"]={"id":oid,"taxon":(o.get("taxon") or {}).get("name"),"quality":o.get("quality_grade"),"photos":{str(p.get("id")):{"license":p.get("license_code"),"attribution":p.get("attribution"),"url":p.get("url")} for p in o.get("photos",[]) if p.get("id")==pid}}
 except Exception as e:candidate["error"]=repr(e)
 OUT["candidate_photos"].append(candidate)
p=pathlib.Path("reports/lane4-oligosanthes-expert-photo-license-20261027.json")
p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(OUT,indent=2)+"\n")
print(json.dumps(OUT,indent=2),flush=True)
