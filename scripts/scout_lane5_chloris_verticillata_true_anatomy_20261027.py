#!/usr/bin/env python3
"""Lane5 Chloris verticillata exact-species missing ligule/lemma scout.
Research source only: iNat individual photo CC0/BY/BY-SA rights and true
source taxon; check extra Wikimedia Goldman ChlorisV8 photo. Contact-sheet
pixels are inspected before any promotion to a species anatomy role.
"""
import base64,html,io,json,pathlib,re,time,urllib.parse,urllib.request,urllib.error
from PIL import Image,ImageOps,ImageDraw
OUT=pathlib.Path("reports/lane5-chloris-verticillata-inner-ligule-scout-20261027.json")
R={"species":"Chloris verticillata","reviewed":[],"holds":[],"total_candidates":0,"installed":0}
def get(uri):
 for attempt in range(4):
  try:
   req=urllib.request.Request(uri,headers={"User-Agent":"HaysBotanyGrassPhotoScout/1.0 (educational; individual image license checks)"})
   with urllib.request.urlopen(req,timeout=43) as f:b=f.read(12000000)
   if len(b)>11800000:raise ValueError("Oversized response")
   return b
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or attempt==3:raise
   time.sleep(2*(attempt+1))
def api(uri):return json.loads(get("https://api.inaturalist.org/v1/"+uri))
pool=[]
try:
 # Individual photo-level license and US TX geolocation search
 for page in range(1,5):
  params=urllib.parse.urlencode({"taxon_id":76294,"place_id":18,"photos":"true","quality_grade":"research","page":page,"per_page":160,"order_by":"observed_on","order":"desc"})
  obs=api("observations?"+params).get("results",[])
  if not obs:break
  for o in obs:
   if (o.get("taxon") or {}).get("name")!="Chloris verticillata":continue
   for p in o.get("photos",[]):
    lic=(p.get("license_code") or "").lower().replace("_","-")
    if lic not in ("cc0","cc-by","cc-by-sa"):continue
    pool.append({"source":"iNaturalist","photo_id":p["id"],"observation":o["id"],
     "place":o.get("place_guess"),"grade":o.get("quality_grade"),"license":lic,
     "author":p.get("attribution"),"photo_url":p.get("url"),
     "photo_page":"https://www.inaturalist.org/photos/"+str(p["id"])})
  if len(obs)<160:break
except Exception as e:R["holds"].append("iNat: "+str(e))
R["total_candidates"]=len(pool)
# First 12 slots, diversify; sort counties then observation and photo
pool.sort(key=lambda p:(not bool(re.search(r"Hays|Comal|Guadalupe|Bexar|Williamson|Travis|Burnet|Austin|Kyle|San Marcos|New Braunfels|San Antonio",p.get("place") or "",re.I)),str(p["photo_id"])))
chosen=[];per_ob={};seen=set()
for p in pool:
 if p["photo_id"] in seen or per_ob.get(p["observation"],0)>=3:continue
 chosen.append(p);per_ob[p["observation"]]=per_ob.get(p["observation"],0)+1;seen.add(p["photo_id"])
 if len(chosen)>=15:break
# First slot is candidate uninstalled Goldman V8
try:
 name="ChlorisV8.jpg"
 args={"action":"query","format":"json","prop":"imageinfo|categories",
       "titles":"File:"+name,"cllimit":"max","iiprop":"url|extmetadata","iiurlwidth":"800"}
 page=next(iter(json.loads(get("https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(args)))["query"]["pages"].values()))
 inf=page["imageinfo"][0];md=inf["extmetadata"]
 lic=re.sub("[^A-Z0-9]","",md.get("LicenseShortName",{}).get("value","").upper())
 artist=html.unescape(re.sub("<[^>]+>"," ",md.get("Artist",{}).get("value",""))).strip()
 cats=[c["title"] for c in page.get("categories",[])]
 R["extra_commons"]={"file":name,"license":lic,"artist":artist,"categories":cats,
  "page":"https://commons.wikimedia.org/wiki/File:ChlorisV8.jpg",
  "url":inf.get("thumburl") or inf["url"],"original":inf["url"]}
 if lic!="CCBYSA40" or "Douglas Goldman" not in artist or "Category:Chloris verticillata" not in cats:
  R["holds"].append("V8 source exact category or license unverified")
 else:
  chosen=[{"source":"Commons","photo_id":"GoldmanV8","place":"Wikimedia exact taxon",
      "license":"CC BY-SA 4.0","photo_url":inf.get("thumburl") or inf["url"],
      "photo_page":"https://commons.wikimedia.org/wiki/File:ChlorisV8.jpg",
      "author":artist}]+chosen[:15]
except Exception as e:R["holds"].append("V8: "+str(e))
sheet=Image.new("RGB",(1200,1480),"white");draw=ImageDraw.Draw(sheet)
for i,p in enumerate(chosen[:16]):
 row,col=divmod(i,4);x=col*300;y=row*370
 try:
  rawurl=p["photo_url"]
  if p["source"]=="iNaturalist":
   rawurl=re.sub(r"/(?:square|small|medium|thumb|large)\.(jpe?g|png)",r"/large.\1",rawurl)
  b=get(rawurl)
  with Image.open(io.BytesIO(b)) as im:im.verify()
  with Image.open(io.BytesIO(b)) as im:
   im=ImageOps.exif_transpose(im).convert("RGB")
   p["pixels"]=list(im.size)
   im.thumbnail((287,307))
   sheet.paste(im,(x+(300-im.width)//2,y+40+(307-im.height)//2))
  p["status"]="INDIVIDUAL_LICENSE_SOURCE_PIXELS_OK_ANATOMY_NOT_YET_CERTIFIED"
 except Exception as e:p["status"]="HELD "+str(e)
 draw.text((x+4,y+4),str(i)+" "+str(p["photo_id"])+" "+str(p["license"]),fill="#111111")
 draw.text((x+4,y+20),(p["place"] or "")[:46],fill="#111111")
 R["reviewed"].append(p)
if R["reviewed"]:
 b=io.BytesIO();sheet.save(b,"JPEG",quality=68,optimize=True)
 print("VERTICILLATA_CONTACT_START_"+base64.b64encode(b.getvalue()).decode()+"_VERTICILLATA_CONTACT_END")
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(R,indent=2)+"\n")
print("VERTICILLATA_REPORT="+json.dumps({"candidate_pool":R["total_candidates"],"sample":len(R["reviewed"]),"extra":R.get("extra_commons"),"holds":R["holds"]}))
