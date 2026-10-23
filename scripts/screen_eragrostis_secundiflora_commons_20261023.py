#!/usr/bin/env python3
"""Audit Commons exact-taxon red lovegrass files; no image publication or auto IDs."""
import json,urllib.request,urllib.parse,time,pathlib,re,html
cat="Category:Eragrostis secundiflora"
report={"taxon":"Eragrostis secundiflora","category":"https://commons.wikimedia.org/wiki/Category:Eragrostis_secundiflora","status":"HOLD","candidates":[],"note":"File-level rights/name inventory only: never automatically archive or publish. Separate actual image pixel and anatomical verification required."}
def get(url):
 for n in range(3):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotany/1.0 (field morphology educational curation)"}),timeout=45) as f:return json.loads(f.read())
  except Exception:
   if n==2:raise
   time.sleep(8*(n+1))
try:
 u="https://commons.wikimedia.org/w/api.php?action=query&list=categorymembers&cmlimit=100&cmtype=file&format=json&cmtitle="+urllib.parse.quote(cat)
 listing=get(u)["query"]["categorymembers"]
 for f in listing:
  title=f["title"]
  detail_url="https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url%7Cextmetadata%7Csize&format=json&titles="+urllib.parse.quote(title)
  row={"title":title,"commons_url":"https://commons.wikimedia.org/wiki/"+urllib.parse.quote(title.replace(" ","_")),"status":"PHOTO_PIXEL_REVIEW_REQUIRED"}
  try:
   result=get(detail_url); info=next(iter(result["query"]["pages"].values()))["imageinfo"][0]
   meta=info.get("extmetadata",{})
   strip=lambda x:html.unescape(re.sub("<[^>]*>","",x or "")).strip()
   lic=strip(meta.get("LicenseShortName",{}).get("value",""))
   creator=strip(meta.get("Artist",{}).get("value",""))
   row.update(license=lic,creator=creator,width=info.get("width"),height=info.get("height"),bytes=info.get("size"),description_url=info.get("descriptionurl"))
   row["license_candidate"]=bool(re.match(r"(?i)^(CC0|CC BY(?:-SA)?(?: |-|$)|Public domain)",lic))
   row["role_guess_from_filename"]=[z for z in ("ligule","collar","spikelet","sheath","floret","glume","lemma") if z in title.lower()]
  except Exception as e:row["metadata_error"]=str(e)
  report["candidates"].append(row)
 report["status"]="INVENTORIED"
except Exception as e:report["error"]=str(e)
p=pathlib.Path("reports/eragrostis-secundiflora-commons-file-screen-20261023.json")
p.parent.mkdir(parents=True,exist_ok=True)
p.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({"status":report["status"],"count":len(report["candidates"]),"error":report.get("error")}))
