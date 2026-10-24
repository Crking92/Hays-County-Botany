#!/usr/bin/env python3
"""Inventory exact-name Commons Eragrostis hirsuta images for rights and anatomy review."""
import json,urllib.request,urllib.parse,html,re,pathlib
category="Category:Eragrostis hirsuta"
def query(params):
 url="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(params)
 req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyID/1.0 (photo rights inventory)"})
 with urllib.request.urlopen(req,timeout=50) as r:return json.load(r)
report={"taxon":"Eragrostis hirsuta","status":"HOLD","images":[],"policy":"No automatic publication or diagnosis from metadata"}
try:
 listing=query({"action":"query","list":"categorymembers","cmtitle":category,"cmtype":"file","cmlimit":"100","format":"json"})["query"]["categorymembers"]
 for x in listing:
  row={"title":x["title"],"status":"PIXEL_REVIEW_REQUIRED"}
  try:
   page=next(iter(query({"action":"query","prop":"imageinfo","iiprop":"url|extmetadata|size","titles":x["title"],"format":"json"})["query"]["pages"].values()))
   info=page["imageinfo"][0];meta=info.get("extmetadata",{})
   strip=lambda v:html.unescape(re.sub("<[^>]+>","",v.get("value",""))).strip()
   row.update(creator=strip(meta.get("Artist",{})),license=strip(meta.get("LicenseShortName",{})),width=info.get("width"),height=info.get("height"),source=info.get("descriptionurl"),eligible=False)
   row["eligible"]=bool(re.match(r"^(CC0|CC BY(?:-SA)?(?: |-|$)|Public domain)",row["license"],re.I))
  except Exception as e:row["error"]=str(e)
  report["images"].append(row)
 report["status"]="INVENTORIED"
except Exception as e:report["error"]=str(e)
path=pathlib.Path("reports/eragrostis-hirsuta-commons-candidates-20261023.json");path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({"status":report["status"],"count":len(report["images"])}))
