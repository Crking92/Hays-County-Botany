#!/usr/bin/env python3
"""Build an attributed pixel-review sheet. Never insert unreviewed images in species gallery."""
import json,io,pathlib,urllib.parse,urllib.request,time
from PIL import Image,ImageDraw
records=json.loads(pathlib.Path("reports/eragrostis-hirsuta-commons-candidates-20261023.json").read_text())["images"]
out=pathlib.Path("reports/eragrostis-hirsuta-photo-review");out.mkdir(parents=True,exist_ok=True)
sheet=Image.new("RGB",(1200,4*480),"white");statuses=[]
for i,r in enumerate(records):
 entry={"filename":r["title"],"creator":r["creator"],"license":r["license"],"status":"HOLD"}
 try:
  assert r["eligible"] and r["license"]=="CC BY-SA 4.0"
  api="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","prop":"imageinfo","iiprop":"url","titles":r["title"],"format":"json"})
  def fetch(url):
   for retry in range(3):
    try:
     with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotany/1.0 (photo rights contact review)"}),timeout=70) as resp:return resp.read()
    except Exception:
     if retry==2:raise
     time.sleep((retry+1)*12)
  item=next(iter(json.loads(fetch(api))["query"]["pages"].values()))["imageinfo"][0]
  im=Image.open(io.BytesIO(fetch(item["url"]))).convert("RGB");im.thumbnail((570,402))
  x=(i%2)*600;y=(i//2)*480
  sheet.paste(im,(x+(600-im.width)//2,y+4))
  d=ImageDraw.Draw(sheet)
  d.text((x+10,y+413),r["title"],fill="black")
  d.text((x+10,y+436),"Douglas Goldman | CC BY-SA 4.0 | PRELIMINARY",fill="black")
  entry["status"]="INCLUDED_FOR_PIXEL_REVIEW"
 except Exception as e:entry["error"]=str(e)
 statuses.append(entry)
target=out/"seven-candidates.jpg";sheet.save(target,"JPEG",quality=88,optimize=True)
report={"status":"REVIEW_READY","candidate_count":len(records),"included":sum(s["status"]=="INCLUDED_FOR_PIXEL_REVIEW" for s in statuses),"photo_gallery_changed":False,"license":"CC BY-SA 4.0 with creator/source credit","images":statuses}
(out/"inventory.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({"included":report["included"]}))
