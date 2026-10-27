#!/usr/bin/env python3
"""Lane 5 hairy woodland brome: Texas and if needed US exact taxon photos,
research-grade, individual open image CC license. Contact pixels in job logs.
No new photos committed until anatomy and source manually screened.
"""
import io,base64,json,pathlib,re,time,urllib.parse,urllib.request,urllib.error
from PIL import Image,ImageOps,ImageDraw
OUT=pathlib.Path("reports/lane5-bromus-pubescens-open-anatomy-scout-20261027.json")
report={"date":"2026-10-27","taxon":"Bromus pubescens","candidates":[],"holds":[],"photo_pool_count":0,"installed":0}
def get(url):
 for attempt in range(4):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotanyPublicSafeSpeciesPhotoScout/1.0 (nonprofit grass education)"})
   with urllib.request.urlopen(req,timeout=45) as f:data=f.read(10000000)
   if len(data)>9900000:raise ValueError("Research response oversize")
   return data
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or attempt==3:raise
   time.sleep(2*(attempt+1))
def api(path):return json.loads(get("https://api.inaturalist.org/v1/"+path))
pool=[]
try:
 taxa=api("taxa/autocomplete?"+urllib.parse.urlencode({"q":"Bromus pubescens","per_page":30})).get("results",[])
 tax=next((t for t in taxa if t.get("name")=="Bromus pubescens"),None)
 if not tax:raise ValueError("Exact species taxon unavailable")
 report["taxon_id"]=tax["id"]
 # iNaturalist place_id 18 is Texas; require textual locality validation as well.
 for mode in ["Texas","USA"]:
  if mode=="Texas" and len(pool)>=35:continue
  for page in range(1,4):
   args={"taxon_id":tax["id"],"photos":"true","quality_grade":"research","page":page,"per_page":150}
   if mode=="Texas":args["place_id"]=18
   obs=api("observations?"+urllib.parse.urlencode(args)).get("results",[])
   if not obs:break
   for o in obs:
    if (o.get("taxon") or {}).get("name")!="Bromus pubescens":continue
    if mode=="Texas" and not re.search(r"Texas|TX\b|Austin|San Antonio|Kyle|Dallas",o.get("place_guess") or "",re.I):continue
    for p in o.get("photos",[]):
     lic=(p.get("license_code") or "").lower().replace("_","-")
     if lic not in ("cc0","cc-by","cc-by-sa","cc-by-nc","cc-by-nc-sa"):continue
     pool.append({"photo_id":p.get("id"),"observation":o["id"],"grade":o.get("quality_grade"),
        "place":o.get("place_guess"),"date":o.get("observed_on"),"license":lic,
        "creator":p.get("attribution"),"url":p.get("url"),
        "source":"https://www.inaturalist.org/photos/"+str(p.get("id"))})
   if len(obs)<150:break
 report["photo_pool_count"]=len(pool)
except Exception as ex:report["holds"].append(str(ex))
seen=set();selected=[]
for p in sorted(pool,key=lambda a:(not re.search(r"Texas|TX\b|Austin|Dallas",a.get("place") or "",re.I),
                             a["license"] not in ("cc-by","cc0","cc-by-sa"),str(a["photo_id"]))):
 if p["license"] not in ("cc-by","cc0","cc-by-sa") or p["photo_id"] in seen:continue
 same=sum(x["observation"]==p["observation"] for x in selected)
 if same>=4:continue
 selected.append(p);seen.add(p["photo_id"])
 if len(selected)>=12:break
sheet=Image.new("RGB",(1200,1140),"white");draw=ImageDraw.Draw(sheet)
for i,p in enumerate(selected):
 row,col=divmod(i,4);x=col*300;y=row*380
 try:
  src=re.sub(r"/(?:square|small|medium|thumb|large)\.(jpe?g|png)",r"/large.\1",p["url"] or "")
  if src==(p.get("url") or ""):raise ValueError("Image URL size suffix invalid")
  blob=get(src)
  with Image.open(io.BytesIO(blob)) as im:im.verify()
  with Image.open(io.BytesIO(blob)) as im:
   im=ImageOps.exif_transpose(im).convert("RGB")
   p["preview_dimensions"]=list(im.size)
   im.thumbnail((290,322))
   sheet.paste(im,(x+(300-im.width)//2,y+40+(322-im.height)//2))
  p["screen"]="CONTACT_SHEET_REAL_PIXELS_LICENSE_VERIFIED_ANATOMY_REVIEW_PENDING"
 except Exception as ex:p["screen"]="HOLD: "+str(ex)
 draw.text((x+5,y+5),f"{i} photo {p['photo_id']}",fill="#151515")
 draw.text((x+5,y+23),str(p["place"] or "")[:42],fill="#151515")
 report["candidates"].append(p)
if selected:
 out=io.BytesIO();sheet.save(out,"JPEG",quality=69,optimize=True)
 print("PUBESCENS_CONTACT_START_"+base64.b64encode(out.getvalue()).decode()+"_PUBESCENS_CONTACT_END")
OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(report,indent=2)+"\n")
print("PUBESCENS_SUMMARY="+json.dumps({k:v for k,v in report.items() if k!="candidates"}))
