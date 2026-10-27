#!/usr/bin/env python3
"""Lane 5 source-specific anatomical photo scout for uninstalled Douglas Goldman
Chloris verticillata frames V3,V6,V7,V8. This DOES NOT count new anatomy roles.
Print a small review contact-sheet JPEG as base64 in run log for pixel inspection.
"""
import base64,hashlib,html,io,json,pathlib,re,time,urllib.parse,urllib.request,urllib.error
from PIL import Image,ImageOps,ImageDraw
names=["ChlorisV3.jpg","ChlorisV6.jpg","ChlorisV7.jpg","ChlorisV8.jpg"]
OUT=pathlib.Path("reports/lane5-chloris-verticillata-remaining-four-scout-20261027.json")
report={"species":"Chloris verticillata","date":"2026-10-27","type":"PHOTO_RESEARCH_ONLY_NOT_ADDED","candidates":[]}
def get(url):
 for n in range(4):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyLicensedImageScout/1.0 (educational grass field ID)"})
   with urllib.request.urlopen(req,timeout=40) as resp: data=resp.read(9000000)
   if len(data)>8500000:raise ValueError("too large")
   return data
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or n==3:raise
   time.sleep(2*(n+1))
sheet=Image.new("RGB",(900,720),"#ffffff")
draw=ImageDraw.Draw(sheet)
for i,name in enumerate(names):
 record={"source":"https://commons.wikimedia.org/wiki/File:"+name}
 try:
  url="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","prop":"imageinfo|categories","cllimit":"max","iiprop":"url|extmetadata","iiurlwidth":"900","format":"json","titles":"File:"+name})
  page=next(iter(json.loads(get(url))["query"]["pages"].values()))
  meta=page["imageinfo"][0];ext=meta["extmetadata"]
  lic=re.sub(r"[^A-Z0-9]","",ext.get("LicenseShortName",{}).get("value","").upper())
  artist=html.unescape(re.sub("<[^>]+>"," ",ext.get("Artist",{}).get("value",""))).strip()
  desc=html.unescape(re.sub("<[^>]+>"," ",ext.get("ImageDescription",{}).get("value",""))).strip()
  cat={c["title"] for c in page.get("categories",[])}
  record.update({"license":lic,"creator":artist,"description":desc[:350],
   "in_exact_species_category":"Category:Chloris verticillata" in cat,"original_url":meta["url"],"original_dimensions":[meta.get("width"),meta.get("height")]})
  if lic!="CCBYSA40" or "Douglas" not in artist or "Category:Chloris verticillata" not in cat:
    raise ValueError("Cannot use without exact Commons rights/author/species verification")
  raw=get(meta.get("thumburl") or meta["url"])
  with Image.open(io.BytesIO(raw)) as im:im.verify()
  with Image.open(io.BytesIO(raw)) as im:
   im=ImageOps.exif_transpose(im).convert("RGB")
   record["preview_dimensions"]=list(im.size)
   im.thumbnail((434,328))
   x=(i%2)*450+(450-im.width)//2
   y=(i//2)*360+25+(328-im.height)//2
   sheet.paste(im,(x,y))
  record["status"]="LICENSE_VERIFIED_REVIEW_PIXELS_PENDING"
 except Exception as ex:record.update({"status":"HELD","reason":str(ex)})
 draw.text(((i%2)*450+10,(i//2)*360+5),name+" "+record["status"][:20],fill="#111111")
 report["candidates"].append(record)
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(report,indent=2)+"\n")
b=io.BytesIO();sheet.save(b,"JPEG",quality=67,optimize=True)
print("REVIEW_SHEET_START_"+base64.b64encode(b.getvalue()).decode()+"_REVIEW_SHEET_END")
print("SCOUT_SUMMARY="+json.dumps([{k:v for k,v in r.items() if k!="original_url"} for r in report["candidates"]]))
