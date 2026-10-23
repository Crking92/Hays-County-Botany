#!/usr/bin/env python3
"""Create diagnostic review contact sheet from eight licensed exact-source Commons photos."""
import json,io,time,pathlib,urllib.request,urllib.parse,hashlib
from PIL import Image,ImageDraw
inp=pathlib.Path("reports/eragrostis-secundiflora-commons-file-screen-20261023.json")
inventory=json.loads(inp.read_text())
assert inventory["taxon"]=="Eragrostis secundiflora"
rows=inventory["candidates"]
assert len(rows)==8
outdir=pathlib.Path("reports/red-lovegrass-photo-review")
outdir.mkdir(parents=True,exist_ok=True)
report={"taxon":"Eragrostis secundiflora","status":"SCREEN_PENDING","images":[],"public_gallery_changed":False,
"disclaimer":"Source-named provisional review only. No diagnostic pixel/lineage certification. Oxylepis images correspond to a subspecies concept, do not silently assign all specimens."}
def get(url):
 for n in range(4):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotany/1.0 botany photo screening"})
   with urllib.request.urlopen(req,timeout=70) as res:return res.read()
  except Exception:
   if n==3:raise
   time.sleep(10*(n+1))
tiles=[]
for i,row in enumerate(rows):
 entry={"index":i+1,"title":row["title"],"source":row["commons_url"],"creator":row.get("creator"),"license":row.get("license"),"status":"HOLD"}
 try:
  title=row["title"]
  api="https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url%7Cextmetadata&format=json&titles="+urllib.parse.quote(title)
  detail=next(iter(json.loads(get(api))["query"]["pages"].values()))["imageinfo"][0]
  license=row.get("license","").upper()
  assert ("CC0" in license or "CC BY-SA 4.0" in license)
  raw=get(detail["url"]);assert 20000<len(raw)<16000000
  img=Image.open(io.BytesIO(raw));img.verify()
  img=Image.open(io.BytesIO(raw)).convert("RGB")
  img.thumbnail((500,390))
  entry.update(status="REVIEW_READY",dimensions=[img.width,img.height],source_bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
  tile=Image.new("RGB",(560,480),"white")
  tile.paste(img,((560-img.width)//2,10))
  draw=ImageDraw.Draw(tile)
  label=f"{i+1}. {title.replace('File:','')[:61]}"
  draw.text((12,404),label,fill="black")
  draw.text((12,428),f"{row.get('creator','unknown')[:45]}  |  {row.get('license','unknown')}",fill="black")
  tiles.append((i,tile))
 except Exception as e:entry["error"]=str(e)
 report["images"].append(entry)
sheet=Image.new("RGB",(1120,480*4),"#eeeeee")
for index,tile in tiles:sheet.paste(tile,((index%2)*560,(index//2)*480))
target=outdir/"eight-commons-photo-review.jpg"
sheet.save(target,"JPEG",quality=85,optimize=True)
report.update(status="REVIEW_SHEET_CREATED",photo_tiles=len(tiles),sheet=str(target),
license_note="Review composite contains CC BY-SA 4.0 credited images and should be treated as CC BY-SA 4.0 derivative; CC0 creator credits voluntarily retained.",sheet_sha256=hashlib.sha256(target.read_bytes()).hexdigest())
(outdir/"inventory.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({"status":report["status"],"tiles":len(tiles),"sheet":str(target)}))
