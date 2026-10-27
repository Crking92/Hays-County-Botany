#!/usr/bin/env python3
"""Lane5 Bromus lanceolatus: real source-specific image research for collar,
root crown and floret anatomy. iNaturalist v1 exact taxon 159463; individual
licensing, 12-screen thumbnails across different observations. Scout only.
"""
import io,base64,json,pathlib,re,time,urllib.parse,urllib.request,urllib.error
from PIL import Image,ImageOps,ImageDraw
OUT=pathlib.Path("reports/lane5-bromus-lanceolatus-real-photo-scout-20261027.json")
report={"date":"2026-10-27","species":"Bromus lanceolatus","taxon_id":159463,"source":"iNaturalist exact taxon observation/photo APIs","candidates":[],"holds":[],"installed":0}
def get(url):
 for n in range(4):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyLicenseCheckedNativeGrassResearch/1.0 (educational Botanical learner)"})
   with urllib.request.urlopen(req,timeout=48) as f:b=f.read(10500000)
   if len(b)>10000000:raise ValueError("Photo size exceeds research gate")
   return b
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or n==3:raise
   time.sleep(2*(n+1))
def api(q):return json.loads(get("https://api.inaturalist.org/v1/"+q))
pool=[]
try:
 for page in range(1,5):
  query=urllib.parse.urlencode({"taxon_id":159463,"photos":"true","page":page,"per_page":160,"order_by":"observed_on","order":"desc"})
  observations=api("observations?"+query).get("results",[])
  for obs in observations:
   if (obs.get("taxon") or {}).get("name")!="Bromus lanceolatus":continue
   for p in obs.get("photos",[]):
    lic=(p.get("license_code") or "").lower().replace("_","-")
    if lic not in ("cc-by","cc0","cc-by-sa","cc-by-nc","cc-by-nc-sa"):continue
    pool.append({"photo_id":p["id"],"observation_id":obs["id"],"grade":obs.get("quality_grade"),
       "place":obs.get("place_guess"),"date_observed":obs.get("observed_on"),
       "license":lic,"creator":p.get("attribution"),"photo_url":p.get("url"),
       "source_page":"https://www.inaturalist.org/photos/"+str(p["id"])})
  if len(observations)<160:break
except Exception as e:report["holds"].append(str(e))
report["pool_count"]=len(pool)
report["regional_cc_candidates"]=[p for p in pool if p["license"] in ("cc-by","cc0","cc-by-sa")][:120]
allowed=[p for p in pool if p["license"] in ("cc-by","cc0","cc-by-sa")]
# Prefer US/Texas, research, and diversify observation; usually a wide variety matters.
allowed.sort(key=lambda p:(not re.search(r"Texas|TX\b|United States|USA|US\b",p.get("place") or "",re.I),p["grade"]!="research",str(p["date_observed"] or ""),p["photo_id"]))
selected=[];counts={}
for p in allowed:
 n=counts.get(p["observation_id"],0)
 if n>=4:continue
 if len(selected)>=12:break
 counts[p["observation_id"]]=n+1;selected.append(p)
sheet=Image.new("RGB",(1200,1140),"white");draw=ImageDraw.Draw(sheet)
for i,p in enumerate(selected):
 row,col=divmod(i,4);x=col*300;y=row*380
 try:
  uri=re.sub(r"/(?:square|small|medium|thumb|large)\.(jpe?g|png)",r"/large.\1",p["photo_url"] or "")
  if uri==p["photo_url"] or not uri.startswith("https://"):raise ValueError("URL shape mismatch")
  raw=get(uri)
  with Image.open(io.BytesIO(raw)) as im:im.verify()
  with Image.open(io.BytesIO(raw)) as im:
   im=ImageOps.exif_transpose(im).convert("RGB")
   p["preview_dimensions"]=list(im.size)
   im.thumbnail((288,320))
   sheet.paste(im,(x+(300-im.width)//2,y+44+(320-im.height)//2))
  p["review_status"]="PHOTO_PIXELS_VISIBLE_LICENSE_VERIFIED_PENDING_ANATOMY_ROLE"
 except Exception as e:p["review_status"]="HELD: "+str(e)
 draw.text((x+4,y+4),str(i)+" photo "+str(p["photo_id"])+" "+p["license"],fill="#222")
 draw.text((x+4,y+19),str(p["place"] or "")[:43],fill="#222")
 report["candidates"].append(p)
if selected:
 buf=io.BytesIO();sheet.save(buf,"JPEG",quality=67,optimize=True)
 print("LANCEOLATUS_SHEET_START_"+base64.b64encode(buf.getvalue()).decode()+"_LANCEOLATUS_SHEET_END")
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(report,indent=2)+"\n")
print("LANCEOLATUS_SUMMARY="+json.dumps({k:v for k,v in report.items() if k not in ("regional_cc_candidates",)}))
