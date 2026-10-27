#!/usr/bin/env python3
"""Follow-up photographic anatomy review. Only research grade, individually open
licensed Bromus lanceolatus photos from Texas observations. Do not install or
claim a ligule/root until actual pixels demonstrate one.
"""
import io,base64,json,pathlib,re,time,urllib.request,urllib.error
from PIL import Image,ImageOps,ImageDraw
OUT=pathlib.Path("reports/lane5-bromus-lanceolatus-texas-second-scout-20261027.json")
PHOTO_MAP=[
 (40865149,64786436),
 (115574351,195058582),(115574351,195058597),
 (158184458,273410241),
 (208568395,369033454),(208568395,369033493),
 (209839149,371262329),
 (220918622,391179324),(220918622,391179398),
 (273361381,491670197),
 (275022465,494284843),
 (355243235,647931588)
]
report={"species":"Bromus lanceolatus","date":"2026-10-27","reviewed":[],"holds":[],"published_photos":0}
def get(url):
 for n in range(4):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotanyPhotoRightsScout/1.0 (licensed educational botany)"})
   with urllib.request.urlopen(req,timeout=45) as f:b=f.read(11000000)
   if len(b)>10800000:raise ValueError("Response oversize")
   return b
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or n==3:raise
   time.sleep(2+n*2)
OBS={}
sheet=Image.new("RGB",(1200,1140),"white");draw=ImageDraw.Draw(sheet)
for i,(oid,pid) in enumerate(PHOTO_MAP):
 rec={"observation_id":oid,"photo_id":pid}
 row,col=divmod(i,4);x=col*300;y=row*380
 try:
  if oid not in OBS:
   j=json.loads(get(f"https://api.inaturalist.org/v1/observations/{oid}"))
   OBS[oid]=next(iter(j.get("results",[])),None)
  obs=OBS[oid]
  if not obs or (obs.get("taxon") or {}).get("name")!="Bromus lanceolatus":raise ValueError("Exact species mismatch")
  if obs.get("quality_grade")!="research":raise ValueError("Observation not research grade")
  place=obs.get("place_guess") or ""
  if not re.search(r"Texas|TX\b|Austin|Seguin|San Antonio|Burnet",place,re.I):raise ValueError("Texas locality not confirmed")
  p=next((p for p in obs.get("photos",[]) if p.get("id")==pid),None)
  if not p:raise ValueError("No image under same voucher")
  lic=p.get("license_code")
  if lic not in ("cc-by","cc0","cc-by-sa"):raise ValueError("Photo license not cleared")
  orig=p.get("url") or ""
  src=re.sub(r"/(?:square|small|medium|thumb|large)\.(jpe?g|png)",r"/large.\1",orig)
  if src==orig:raise ValueError("Cannot request original size")
  raw=get(src)
  with Image.open(io.BytesIO(raw)) as im:im.verify()
  with Image.open(io.BytesIO(raw)) as im:
   im=ImageOps.exif_transpose(im).convert("RGB")
   rec["preview_size"]=list(im.size)
   im.thumbnail((290,324))
   sheet.paste(im,(x+(300-im.width)//2,y+43+(324-im.height)//2))
  rec.update({"place":place,"photo_license":lic,"creator":p.get("attribution"),"source":"https://www.inaturalist.org/photos/"+str(pid),"status":"IMAGE_SOURCE_AND_PIXELS_CHECKED_REQUIRES_ANATOMY_INSPECTION"})
 except Exception as ex:rec.update({"status":"HELD","reason":str(ex)})
 draw.text((x+4,y+4),f"{i} photo {pid}",fill="#111111")
 draw.text((x+4,y+22),str(rec.get("place") or "")[:40],fill="#111111")
 report["reviewed"].append(rec)
if any(x["status"].startswith("IMAGE_") for x in report["reviewed"]):
 buf=io.BytesIO();sheet.save(buf,"JPEG",quality=70,optimize=True)
 print("LANCEOLATUS_TX_SHEET_START_"+base64.b64encode(buf.getvalue()).decode()+"_LANCEOLATUS_TX_SHEET_END")
OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(report,indent=2)+"\n")
print("LANCEOLATUS_TX_REPORT="+json.dumps({k:v for k,v in report.items() if k!="reviewed"}))
