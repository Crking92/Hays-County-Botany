#!/usr/bin/env python3
"""Find original iNaturalist media for Muhlenbergia dubia without importing unknown rights."""
import json,pathlib,urllib.request,urllib.parse,time
report={"taxon_id":165548,"species":"Muhlenbergia dubia","records":[],"errors":[],"eligible":[],"observations_count":0}
def get(u):
 req=urllib.request.Request(u,headers={"User-Agent":"HaysBotanyVisualLearner/1.0 (noncommercial botanical image citation; github.com/Crking92/Hays-County-Botany)"})
 with urllib.request.urlopen(req,timeout=40) as r:return json.load(r)
for page in range(1,4):
 try:
  url="https://api.inaturalist.org/v1/observations?"+urllib.parse.urlencode({"taxon_id":165548,"taxon_is_active":"true","quality_grade":"research,needs_id","per_page":100,"page":page,"order_by":"observed_on","order":"desc"})
  data=get(url);records=data.get("results",[])
  report["observations_count"]=data.get("total_results",0)
  for ob in records:
   if not ob.get("taxon") or ob["taxon"].get("id")!=165548:continue
   photos=[]
   for row in ob.get("photos",[]):
    photo={"id":row.get("id"),"license_code":row.get("license_code"),"attribution":row.get("attribution",""),"original_url":row.get("url","").replace("square.","original."),"dimensions":row.get("original_dimensions"),"caption":row.get("caption","")}
    photos.append(photo)
    if row.get("license_code") in ("cc0","cc-by","cc-by-sa"):
     report["eligible"].append({"observation":ob["id"],"taxon":165548,"photo":photo})
   report["records"].append({"id":ob.get("id"),"grade":ob.get("quality_grade"),"taxon":ob["taxon"].get("name"),"observer":ob.get("user",{}).get("login"),"observation_notes":ob.get("description","")[:400],"photo_count":len(photos),"photos":photos[:16],"url":"https://www.inaturalist.org/observations/"+str(ob["id"])})
  if len(records)<100:break
  time.sleep(1)
 except Exception as e:report["errors"].append(str(e)[:250]);break
pathlib.Path("reports/lane3-pine-muhly-inat-sources-20261025.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"total_observations":report["observations_count"],"found":len(report["records"]),"eligible_photos":len(report["eligible"]),"errors":report["errors"],"Joey_source_photos":[r for r in report["records"] if any(t in str(r).lower() for t in ["joey","crimepays","botanydoesnt"])]},ensure_ascii=False))
