#!/usr/bin/env python3
"""Pixel-review three individually licensed exact-species Harry Rose Chloris
virgata culm node photos on Wikimedia Commons. Metadata-only scouting.
"""
import urllib.parse,urllib.request,urllib.error,json,re,html,io,time,base64,pathlib
from PIL import Image,ImageOps,ImageDraw
NAMES=["Chloris virgata node (6920191777).jpg",
       "Chloris virgata node3 (6923835606).jpg",
       "Chloris virgata node4 NWS - Flickr - Macleay Grass Man.jpg"]
OUT=pathlib.Path("reports/lane5-chloris-virgata-harry-rose-node-scout-20261027.json")
report={"date":"2026-10-27","taxon":"Chloris virgata","reviewed":[]}
def get(url):
 for n in range(4):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotanyExactWikimediaGrassAnatomyScout/1.0"})
   with urllib.request.urlopen(req,timeout=44) as f:b=f.read(10000000)
   if len(b)>9800000:raise ValueError("Source exceeded limit")
   return b
  except urllib.error.HTTPError as ex:
   if ex.code not in (429,500,502,503,504) or n==3:raise
   time.sleep(2+n*2)
sheet=Image.new("RGB",(1200,530),"white");draw=ImageDraw.Draw(sheet)
for i,name in enumerate(NAMES):
 result={"name":name,"page":"https://commons.wikimedia.org/wiki/File:"+urllib.parse.quote(name.replace(" ","_"))}
 try:
  params={"action":"query","format":"json","prop":"imageinfo|categories","cllimit":"max","iiprop":"url|extmetadata","iiurlwidth":"950","titles":"File:"+name}
  u="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(params)
  page=next(iter(json.loads(get(u))["query"]["pages"].values()))
  info=page["imageinfo"][0];meta=info["extmetadata"]
  lic=re.sub(r"[^A-Z0-9]","",meta.get("LicenseShortName",{}).get("value","").upper())
  artist=html.unescape(re.sub("<[^>]+>"," ",meta.get("Artist",{}).get("value",""))).strip()
  category={c["title"] for c in page.get("categories",[])}
  result.update({"license":lic,"creator":artist,"categories":list(category)[:10],
    "source_url":info["url"],"original_dimensions":[info.get("width"),info.get("height")]})
  if lic!="CCBY20" or "Harry Rose" not in artist or "Category:Chloris virgata" not in category:
   raise ValueError("Individual Wikimedia Commons source taxon, photographer and license mismatch")
  raw=get(info.get("thumburl") or info["url"])
  with Image.open(io.BytesIO(raw)) as im:im.verify()
  with Image.open(io.BytesIO(raw)) as im:
   im=ImageOps.exif_transpose(im).convert("RGB")
   result["preview_dimensions"]=list(im.size)
   im.thumbnail((390,470));sheet.paste(im,(i*400+(400-im.width)//2,33+(470-im.height)//2))
  result["status"]="SOURCE_LICENSE_AND_PIXELS_VERIFIED"
 except Exception as ex:result.update({"status":"HELD","error":str(ex)})
 draw.text((i*400+4,4),name[:44],fill="#111111")
 report["reviewed"].append(result)
b=io.BytesIO();sheet.save(b,"JPEG",quality=71,optimize=True)
print("CHLORIS_NODE_SHEET_START_"+base64.b64encode(b.getvalue()).decode()+"_CHLORIS_NODE_SHEET_END")
OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(report,indent=2)+"\n")
print("NODE_SUMMARY="+json.dumps([{k:r.get(k) for k in ("name","license","status","original_dimensions","error")} for r in report["reviewed"]]))
