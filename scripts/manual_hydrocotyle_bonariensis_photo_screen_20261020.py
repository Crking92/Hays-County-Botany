#!/usr/bin/env python3
"""Exact-name, individual-photo-license candidate screen; review-only.
Do not treat iNaturalist taxon labels as reproductive voucher determinations.
"""
import json,io,hashlib,time,math
from pathlib import Path
import requests
from PIL import Image, ImageDraw, ImageOps, ImageFont
OUT=Path("workflow/photo-library/reviews/hydrocotyle-bonariensis-20261020")
OUT.mkdir(parents=True,exist_ok=True)
S=requests.Session()
S.headers.update({"User-Agent":"HaysCountyBotanyLicensePhotoScreen/1.0 (https://github.com/Crking92/Hays-County-Botany)"})
def get(url,params=None):
 for attempt in range(3):
  try:
   r=S.get(url,params=params,timeout=32)
   if r.status_code in (429,500,502,503,504):time.sleep(2+3*attempt);continue
   r.raise_for_status();return r.json()
  except Exception:
   if attempt==2:raise
   time.sleep(2+attempt*2)
t=get("https://api.inaturalist.org/v1/taxa/autocomplete",{"q":"Hydrocotyle bonariensis","per_page":20})
match=[x for x in t.get("results",[]) if x.get("name")=="Hydrocotyle bonariensis" and x.get("rank")=="species"]
assert len(match)==1,"Exact iNat species not uniquely resolved"
taxon=match[0]
obs=[];seen=set()
for page in range(1,5):
 data=get("https://api.inaturalist.org/v1/observations",{
 "taxon_id":taxon["id"],"place_id":18,"quality_grade":"research",
 "photos":True,"per_page":100,"page":page,"order_by":"observed_on","order":"desc"})
 items=data.get("results",[])
 for o in items:
  if o.get("taxon",{}).get("id")==taxon["id"] and o["id"] not in seen:
   seen.add(o["id"]);obs.append(o)
 if len(items)<100:break
cands=[];per_user={};per_obs={}
for o in obs:
 user=o.get("user",{}).get("login") or "unknown"
 if per_user.get(user,0)>=12:continue
 for pic in o.get("photos",[])[:7]:
  if per_user.get(user,0)>=12 or per_obs.get(o["id"],0)>=5:break
  lic=pic.get("license_code")
  if lic not in ("cc-by","cc0","cc-by-sa"):continue
  url=pic.get("url") or ""
  if "/photos/" not in url:continue
  cands.append({"photo_id":pic["id"],"user":user,"observation_id":o["id"],
   "photo_attribution":pic.get("attribution"),"photo_license_code":lic,
   "photo_source_page":"https://www.inaturalist.org/photos/"+str(pic["id"]),
   "observation_page":"https://www.inaturalist.org/observations/"+str(o["id"]),
   "photo_url":url.replace("/square.","/large.").replace("/small.","/large.").replace("/medium.","/large."),
   "taxon":"Hydrocotyle bonariensis","grade":o["quality_grade"],
   "caution":"Photo by licensed iNaturalist observer, name is research-grade source ID, not species-vouchered reproductive analysis."})
  per_user[user]=per_user.get(user,0)+1;per_obs[o["id"]]=per_obs.get(o["id"],0)+1
 if len(cands)>=40:break
cands=cands[:40]
W,H,COLS=320,280,4
sheet=Image.new("RGB",(W*COLS,H*max(1,math.ceil(len(cands)/COLS))),(242,245,236))
d=ImageDraw.Draw(sheet)
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",15)
n=0
for i,x in enumerate(cands):
 a=i%COLS*W;b=i//COLS*H
 try:
  response=S.get(x["photo_url"],timeout=32);response.raise_for_status()
  with Image.open(io.BytesIO(response.content)) as im:
   im.load();pic=ImageOps.exif_transpose(im).convert("RGB")
  x["preview_original_size"]=list(pic.size)
  pic.thumbnail((W-14,H-55),Image.Resampling.LANCZOS)
  dest=OUT/(str(x["photo_id"])+".jpg");pic.save(dest,quality=87,optimize=True)
  x["preview_sha256"]=hashlib.sha256(dest.read_bytes()).hexdigest()
  sheet.paste(pic,(a+(W-pic.width)//2,b+(H-55-pic.height)//2));n+=1
 except Exception as e:
  x["preview_error"]=str(e)[:160];d.text((a+12,b+90),"PHOTO ERROR",font=font,fill=(139,29,29))
 d.text((a+8,b+H-45),str(x["photo_id"])+" / "+x["photo_license_code"],font=font,fill=(20,45,32))
 d.text((a+8,b+H-22),x["user"][:28],font=font,fill=(20,45,32))
sheet.save(OUT/"contact.jpg",quality=88,optimize=True)
report={"taxon":"Hydrocotyle bonariensis","taxon_id":taxon["id"],"texas_observations_screened":len(obs),
 "individually_cc_license_candidates":len(cands),"preview_download_success":n,
 "critical_photo_targets":["whole branching primary umbel","secondary ray bearing its own spaced whorls","peltate leaf underside","fruit macro"],
 "no_county_native_claim":True,"candidates":cands}
(OUT/"photo-screen.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({k:v for k,v in report.items() if k!="candidates"},indent=2))
