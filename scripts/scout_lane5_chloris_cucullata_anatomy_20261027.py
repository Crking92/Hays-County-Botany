#!/usr/bin/env python3
"""Lane 5 hooded windmillgrass exact Chloris cucullata source-licensed photos.
Search Texas first then other exact species; collect diverse actual specimen
photographs. Save source rights and print a visual contact sheet for review.
Do NOT archive photos to species card until independently examined.
"""
import io,json,base64,re,time,pathlib,urllib.request,urllib.parse,urllib.error
from PIL import Image,ImageOps,ImageDraw
OUT=pathlib.Path("reports/lane5-chloris-cucullata-exact-anatomy-scout-20261027.json")
R={"species":"Chloris cucullata","date":"2026-10-27","source":"iNaturalist exact accepted taxon + individual photo rights", "taxon":None,"sample":[],"candidate_count":0,"holds":[],"new_licensed_photos":0}
def get(url):
 for n in range(4):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyExactGrassPhotoReview/1.0 (source attribution and photographer rights checked)"})
   with urllib.request.urlopen(req,timeout=38) as f:b=f.read(10000000)
   if len(b)>9600000:raise ValueError("source too large")
   return b
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or n==3:raise
   time.sleep(2+n*2)
def api(path):return json.loads(get("https://api.inaturalist.org/v1/"+path))
photos=[]
try:
 tax=next((x for x in api("taxa/autocomplete?"+urllib.parse.urlencode({"q":"Chloris cucullata","per_page":25})).get("results",[]) if x.get("name")=="Chloris cucullata"),None)
 if not tax:raise ValueError("Exact accepted source taxon absent")
 R["taxon"]=tax["id"]
 for page in range(1,5):
  args={"taxon_id":tax["id"],"place_id":18,"photos":"true","per_page":160,"page":page,"order_by":"observed_on","order":"desc"}
  o=api("observations?"+urllib.parse.urlencode(args)).get("results",[])
  if not o:break
  for ob in o:
   if (ob.get("taxon") or {}).get("name")!="Chloris cucullata":continue
   for p in ob.get("photos",[]):
    lic=str(p.get("license_code") or "").lower().replace("_","-")
    if lic not in ("cc0","cc-by","cc-by-sa","cc-by-nc","cc-by-nc-sa"):continue
    photos.append({"photo_id":p["id"],"observation":ob.get("id"),"region":ob.get("place_guess"),
     "grade":ob.get("quality_grade"),"attribution":p.get("attribution"),"license":lic,"url":p.get("url"),
     "observed_on":ob.get("observed_on"),"source":"https://www.inaturalist.org/photos/"+str(p["id"])})
  if len(o)<160:break
except Exception as e:R["holds"].append(str(e))
R["candidate_count"]=len(photos)
licensed=[p for p in photos if p["license"] in ("cc0","cc-by","cc-by-sa")]
licensed.sort(key=lambda p:(p["grade"]!="research", not re.search(r"San Marcos|Hays|Kyle|Comal|Guadalupe|Uvalde|Austin|Bexar|Burnet|TX\b|Texas",p["region"] or "",re.I),p["photo_id"]))
seen=set();per_ob={};selected=[]
for p in licensed:
 if p["photo_id"] in seen or per_ob.get(p["observation"],0)>=4:continue
 selected.append(p);seen.add(p["photo_id"]);per_ob[p["observation"]]=per_ob.get(p["observation"],0)+1
 if len(selected)>=16:break
sheet=Image.new("RGB",(1200,1500),"white");draw=ImageDraw.Draw(sheet)
for i,p in enumerate(selected):
 row,col=divmod(i,4);x=col*300;y=row*375
 try:
  url=re.sub(r"/(?:square|small|medium|thumb|large)\.(jpe?g|png)",r"/large.\1",p["url"] or "")
  if not url.startswith("https://") or url==p["url"]:raise ValueError("Unexpected iNat photo media URL")
  raw=get(url)
  with Image.open(io.BytesIO(raw)) as im:im.verify()
  with Image.open(io.BytesIO(raw)) as im:
   im=ImageOps.exif_transpose(im).convert("RGB")
   p["preview_dimensions"]=list(im.size)
   im.thumbnail((287,312));sheet.paste(im,(x+(300-im.width)//2,y+40+(315-im.height)//2))
  p["preview_status"]="DECODED_AND_SOURCE_RIGHTS_VERIFIED_ANATOMY_PENDING"
 except Exception as e:p["preview_status"]="HELD "+str(e)[:200]
 draw.text((x+4,y+4),str(i)+" "+str(p["photo_id"])+" "+str(p["license"]),fill="#111111")
 draw.text((x+4,y+22),(p["region"] or "")[:44],fill="#111111")
 R["sample"].append(p)
if selected:
 buf=io.BytesIO();sheet.save(buf,"JPEG",quality=67,optimize=True)
 print("CHLORIS_CUCULLATA_CONTACT_START_"+base64.b64encode(buf.getvalue()).decode()+"_CHLORIS_CUCULLATA_CONTACT_END")
OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(R,indent=2)+"\n")
print("SCOUT_SUMMARY="+json.dumps({"taxon":R["taxon"],"candidate_count":R["candidate_count"],"sampled":len(R["sample"]),"holds":R["holds"]}))
