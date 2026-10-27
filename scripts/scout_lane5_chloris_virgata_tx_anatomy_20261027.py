#!/usr/bin/env python3
"""Lane5 exact Chloris virgata individual-image-licensed anatomy search.
Texas CC0/CC BY/CC BY-SA iNaturalist photos, diverse voucher series.
Returns preview contact sheet and metadata; NEVER installs unchecked photos.
"""
import base64,io,json,pathlib,re,time,urllib.parse,urllib.request,urllib.error
from PIL import Image,ImageOps,ImageDraw
OUT=pathlib.Path("reports/lane5-chloris-virgata-texas-anatomy-scout-20261027.json")
R={"species":"Chloris virgata","date":"2026-10-27","candidates":[],"photo_pool":[],"holds":[],"installed":0}
def get(url):
 for a in range(4):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyPublicSafeGrassPhotoScout/1.0 (education; individual photo licenses)"})
   with urllib.request.urlopen(req,timeout=44) as f:b=f.read(10800000)
   if len(b)>10700000:raise ValueError("Response too big")
   return b
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or a==3:raise
   time.sleep((a+1)*2)
def api(x):return json.loads(get("https://api.inaturalist.org/v1/"+x))
try:
 taxa=api("taxa/autocomplete?"+urllib.parse.urlencode({"q":"Chloris virgata","per_page":30})).get("results",[])
 tax=next((x for x in taxa if x.get("name")=="Chloris virgata"),None)
 if not tax:raise ValueError("No exact iNat taxon")
 R["taxon_id"]=tax["id"]
 for page in range(1,5):
  arg={"taxon_id":tax["id"],"place_id":18,"photos":"true","quality_grade":"research","page":page,"per_page":150,"order_by":"observed_on","order":"desc"}
  obs=api("observations?"+urllib.parse.urlencode(arg)).get("results",[])
  for ob in obs:
   if (ob.get("taxon") or {}).get("name")!="Chloris virgata":continue
   for p in ob.get("photos",[]):
    lic=str(p.get("license_code") or "").lower().replace("_","-")
    if lic not in ("cc-by","cc0","cc-by-sa","cc-by-nc","cc-by-nc-sa"):continue
    R["photo_pool"].append({"photo_id":p.get("id"),"observation_id":ob.get("id"),"license":lic,
        "attribution":p.get("attribution"),"url":p.get("url"),"place":ob.get("place_guess"),
        "quality":ob.get("quality_grade"),"observed_on":ob.get("observed_on"),
        "source":"https://www.inaturalist.org/photos/"+str(p.get("id"))})
  if len(obs)<150:break
except Exception as ex:R["holds"].append(str(ex))
R["candidate_count"]=len(R["photo_pool"])
used=set();perobs={};selected=[]
for p in sorted(R["photo_pool"],key=lambda x:(x["license"] not in ("cc0","cc-by","cc-by-sa"),
 not re.search(r"Hays|Kyle|Bexar|Comal|San Antonio|San Marcos|Austin|Guadalupe|Travis|Texas|TX\b",x["place"] or "",re.I),str(x["observed_on"] or ""),str(x["photo_id"]))):
 if p["license"] not in ("cc0","cc-by","cc-by-sa") or p["photo_id"] in used:continue
 if perobs.get(p["observation_id"],0)>=4:continue
 selected.append(p);used.add(p["photo_id"]);perobs[p["observation_id"]]=perobs.get(p["observation_id"],0)+1
 if len(selected)>=16:break
im=Image.new("RGB",(1200,1500),"white");draw=ImageDraw.Draw(im)
for i,p in enumerate(selected):
 row,col=divmod(i,4);x=col*300;y=row*375
 try:
  uri=re.sub(r"/(?:square|small|medium|thumb|large)\.(jpe?g|png)",r"/large.\1",p.get("url") or "")
  if uri==p.get("url") or not uri.startswith("https://"):raise ValueError("Invalid source thumbnail")
  raw=get(uri)
  with Image.open(io.BytesIO(raw)) as a:a.verify()
  with Image.open(io.BytesIO(raw)) as a:
   a=ImageOps.exif_transpose(a).convert("RGB");p["preview_pixels"]=list(a.size)
   a.thumbnail((288,312));im.paste(a,(x+(300-a.width)//2,y+43+(312-a.height)//2))
  p["status"]="SOURCE_IMAGE_PIXEL_VERIFIED_ANATOMY_PENDING"
 except Exception as e:p["status"]="HELD "+str(e)
 draw.text((x+3,y+5),str(i)+" "+str(p["photo_id"])+" "+p["license"],fill="#111")
 draw.text((x+3,y+22),(p["place"] or "")[:40],fill="#111")
 R["candidates"].append(p)
if selected:
 b=io.BytesIO();im.save(b,"JPEG",quality=68,optimize=True)
 print("CHLORIS_VIRGATA_SHEET_START_"+base64.b64encode(b.getvalue()).decode()+"_CHLORIS_VIRGATA_SHEET_END")
OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(R,indent=2)+"\n")
print("SCOUT_SUMMARY="+json.dumps({"taxon_id":R.get("taxon_id"),"candidate_count":R.get("candidate_count"),"reviewed":len(R["candidates"]),"holds":R["holds"]}))
