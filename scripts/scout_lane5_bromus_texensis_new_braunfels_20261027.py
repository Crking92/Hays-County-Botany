#!/usr/bin/env python3
"""Lane 5: look at complete exact-species, CC BY, research-grade 2023 New Braunfels
Bromus texensis observations (Eric Knight) for REAL root, collar, glumes.
Metadata scout only. No JPEG added until pixel review and actual anatomy role.
"""
import io,base64,json,pathlib,re,time,urllib.parse,urllib.request,urllib.error
from PIL import Image,ImageOps,ImageDraw
REPORT=pathlib.Path("reports/lane5-bromus-texensis-new-braunfels-scout-20261027.json")
OBSID=[154120544,154121022]
rep={"species":"Bromus texensis","date":"2026-10-27","source_observations":OBSID,"photos":[],"held":[],"new_photos":0}
def get(url):
 for n in range(4):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyTexasBromeDiagnosticPhotoResearch/1.0 (educational botanical photo archive)"})
   with urllib.request.urlopen(req,timeout=43) as f: data=f.read(12000000)
   if len(data)>11500000:raise ValueError("too large")
   return data
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or n==3:raise
   time.sleep(2+n*2)
photos=[]
for obsid in OBSID:
 try:
  j=json.loads(get("https://api.inaturalist.org/v1/observations/"+str(obsid)))
  obs=next(iter(j.get("results",[])),None)
  if not obs or (obs.get("taxon") or {}).get("name")!="Bromus texensis" or obs.get("quality_grade")!="research":
   raise ValueError("Not research-grade exact Bromus texensis")
  if not re.search(r"(TX\b|Texas|New Braunfels)",obs.get("place_guess") or "",re.I):raise ValueError("Not TX")
  for p in obs.get("photos",[]):
   if p.get("license_code")!="cc-by":continue
   if not p.get("attribution","").lower().find("eric knight")>=0:raise ValueError("Photographer credit mismatch")
   photos.append({"id":p["id"],"observation":obsid,"license":p["license_code"],
    "creator":p.get("attribution"),"source":"https://www.inaturalist.org/photos/"+str(p["id"]),
    "url":p.get("url"),"place":obs.get("place_guess")})
 except Exception as e:rep["held"].append({"observation":obsid,"reason":str(e)})
sheet=Image.new("RGB",(1200,1000),"white");draw=ImageDraw.Draw(sheet)
for i,p in enumerate(photos[:12]):
 row,col=divmod(i,4);x=col*300;y=row*333
 try:
  uri=re.sub(r"/(?:square|small|medium|thumb|large)\.(jpe?g|png)",r"/large.\1",p["url"])
  raw=get(uri)
  with Image.open(io.BytesIO(raw)) as im:im.verify()
  with Image.open(io.BytesIO(raw)) as im:
   im=ImageOps.exif_transpose(im).convert("RGB")
   p["preview_size"]=list(im.size)
   im.thumbnail((290,293))
   sheet.paste(im,(x+(300-im.width)//2,y+34+(293-im.height)//2))
  p["status"]="REVIEW_CONTACT_PIXELS"
 except Exception as ex:p["status"]="HOLD "+str(ex)
 draw.text((x+5,y+8),str(i)+" "+str(p["id"])+" "+str(p["observation"]),fill="#000000")
 rep["photos"].append(p)
if photos:
 out=io.BytesIO();sheet.save(out,"JPEG",quality=69,optimize=True)
 print("NEW_BRAUNFELS_CONTACT_START_"+base64.b64encode(out.getvalue()).decode()+"_NEW_BRAUNFELS_CONTACT_END")
REPORT.parent.mkdir(exist_ok=True)
REPORT.write_text(json.dumps(rep,indent=2)+"\n")
print("SCOUT_REPORT="+json.dumps({k:v for k,v in rep.items() if k!="photos"}))
