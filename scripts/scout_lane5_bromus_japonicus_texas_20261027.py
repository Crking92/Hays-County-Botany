#!/usr/bin/env python3
"""Lane 5 Japanese brome: scout true Texas growing habit/roots and opened
inner ligule. Research-grade exact species, individual CC0/CC BY/CC BY-SA
photo rights. This first pass installs zero photos: every image role is
pixel-reviewed on a contact sheet before promotion.
"""
import base64,io,json,pathlib,re,time,urllib.parse,urllib.request,urllib.error
from PIL import Image,ImageOps,ImageDraw
OUT=pathlib.Path("reports/lane5-bromus-japonicus-texas-field-photo-scout-20261027.json")
R={"species":"Bromus japonicus","date":"2026-10-27","candidate_pool":[],"reviewed":[],"holds":[],"installed":0}
def get(uri):
 for n in range(4):
  try:
   req=urllib.request.Request(uri,headers={"User-Agent":"HaysBotanyExactJapaneseBromeTexasPhotoResearch/1.0 (rights-respecting educational plant learner)"})
   with urllib.request.urlopen(req,timeout=48) as f:b=f.read(11500000)
   if len(b)>11200000:raise ValueError("Over preview/JSON limit")
   return b
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or n==3:raise
   time.sleep(2*(n+1))
def api(path):return json.loads(get("https://api.inaturalist.org/v1/"+path))
try:
 taxa=api("taxa/autocomplete?"+urllib.parse.urlencode({"q":"Bromus japonicus","per_page":30})).get("results",[])
 tax=next((z for z in taxa if z.get("name")=="Bromus japonicus"),None)
 if tax is None:raise ValueError("Exact accepted species missing")
 R["taxon_id"]=tax["id"]
 for page in range(1,5):
  par={"taxon_id":tax["id"],"place_id":18,"photos":"true","quality_grade":"research","per_page":150,"page":page,"order_by":"observed_on","order":"desc"}
  obs=api("observations?"+urllib.parse.urlencode(par)).get("results",[])
  for ob in obs:
   if (ob.get("taxon") or {}).get("name")!="Bromus japonicus":continue
   region=ob.get("place_guess") or ""
   for p in ob.get("photos",[]):
    license_=(p.get("license_code") or "").lower().replace("_","-")
    if license_ not in ("cc0","cc-by","cc-by-sa","cc-by-nc","cc-by-nc-sa"):continue
    R["candidate_pool"].append({"photo_id":p.get("id"),"observation":ob.get("id"),"region":region,
       "license":license_,"creator":p.get("attribution"),"url":p.get("url"),
       "source":"https://www.inaturalist.org/photos/"+str(p.get("id")),
       "grade":ob.get("quality_grade"),"date":ob.get("observed_on")})
  if len(obs)<150:break
except Exception as e:R["holds"].append(str(e))
R["photo_pool_size"]=len(R["candidate_pool"])
# Select varied source observations in TX, favor directly around Central Texas.
opened=[p for p in R["candidate_pool"] if p["license"] in ("cc0","cc-by","cc-by-sa")]
opened.sort(key=lambda p:(not re.search(r"Travis|Williamson|Hays|Comal|Bexar|Austin|San Antonio|San Marcos|Texas|TX\b",p["region"],re.I),
 p["grade"]!="research",str(p["photo_id"])))
selected=[];seen=set();per_ob={}
for p in opened:
 if p["photo_id"] in seen or per_ob.get(p["observation"],0)>=4:continue
 selected.append(p);seen.add(p["photo_id"]);per_ob[p["observation"]]=per_ob.get(p["observation"],0)+1
 if len(selected)>=16:break
sheet=Image.new("RGB",(1200,1500),"white");draw=ImageDraw.Draw(sheet)
for i,p in enumerate(selected):
 row,col=divmod(i,4);x=300*col;y=375*row
 try:
  u=re.sub(r"/(?:square|small|medium|thumb|large)\.(jpe?g|png)",r"/large.\1",p.get("url") or "")
  if not u.startswith("https://") or u==p.get("url"):raise ValueError("Image URL invalid")
  b=get(u)
  with Image.open(io.BytesIO(b)) as im:im.verify()
  with Image.open(io.BytesIO(b)) as im:
   im=ImageOps.exif_transpose(im).convert("RGB");p["dimensions"]=list(im.size)
   im.thumbnail((284,316));sheet.paste(im,(x+(300-im.width)//2,y+40+(316-im.height)//2))
  p["status"]="SOURCE_BYTES_VERIFIED_ROLE_REVIEW_PENDING"
 except Exception as ex:p["status"]="HELD "+str(ex)
 draw.text((x+4,y+4),f"{i} {p['photo_id']} {p['license']}",fill="#111")
 draw.text((x+4,y+21),(p["region"] or "")[:43],fill="#111")
 R["reviewed"].append(p)
if selected:
 b=io.BytesIO();sheet.save(b,"JPEG",quality=68,optimize=True)
 print("JAPANESE_BROME_TEXAS_SHEET_START_"+base64.b64encode(b.getvalue()).decode()+"_JAPANESE_BROME_TEXAS_SHEET_END")
OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(R,indent=2)+"\n")
print("SCOUT_SUMMARY="+json.dumps({"taxon_id":R.get("taxon_id"),"pool_count":R["photo_pool_size"],"reviewed":len(R["reviewed"]),"holds":R["holds"]}))
