#!/usr/bin/env python3
"""Source exact-name, independently photo-licensed D. recurvata iNaturalist photographs.
Collect contact sheet and metadata only; never promote image IDs to canonical without manual pixel review.
Avoid genus-only, common-name searches and unlicensed photographs.
"""
import json, math, io, hashlib, csv, time
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import requests
OUT=Path("workflow/photo-library/reviews/dichondra-recurvata-20261019")
OUT.mkdir(parents=True,exist_ok=True)
SESSION=requests.Session();SESSION.headers.update({"User-Agent":"HaysBotanyLearner/1.0 (https://github.com/Crking92/Hays-County-Botany; science review)"})
def json_get(url,params):
 for attempt in range(3):
  r=SESSION.get(url,params=params,timeout=32)
  if r.status_code in (429,502,503):
   time.sleep(2+attempt*3);continue
  r.raise_for_status();return r.json()
 raise RuntimeError("Source API unavailable "+url)
results=json_get("https://api.inaturalist.org/v1/taxa/autocomplete",{"q":"Dichondra recurvata","per_page":20})["results"]
ids=[r for r in results if r.get("name")=="Dichondra recurvata" and r.get("rank")=="species"]
if len(ids)!=1:raise RuntimeError("Exact accepted iNaturalist taxon not unique: "+str(ids))
taxon=ids[0]
all_obs=[]; seen=set()
for quality in ("research","needs_id"):
 for pg in range(1,4):
  v=json_get("https://api.inaturalist.org/v1/observations/species_counts",{"taxon_id":taxon["id"],"quality_grade":quality,"per_page":1}) if False else None
  data=json_get("https://api.inaturalist.org/v1/observations",{"taxon_id":taxon["id"],"quality_grade":quality,
   "photos":True,"per_page":100,"page":pg,"order":"desc","order_by":"observed_on"})
  for o in data.get("results",[]):
   if o.get("taxon",{}).get("id")!=taxon["id"] or o["id"] in seen:continue
   seen.add(o["id"]);all_obs.append(o)
  if len(data.get("results",[]))<100 or len(all_obs)>180:break
photo_records=[]
for o in all_obs:
 for p in o.get("photos",[])[:8]:
  lc=p.get("license_code")
  if lc not in ("cc-by","cc-by-sa","cc0"):continue
  url=p.get("url","")
  if not url or "/photos/" not in url:continue
  purl=url.replace("/square.","/large.").replace("/small.","/large.").replace("/medium.","/large.")
  photo_records.append({"photo_id":p["id"],"observation_id":o["id"],"observer":o.get("user",{}).get("login"),
   "photo_attribution":p.get("attribution"),"photo_license":lc,"photo_source":"https://www.inaturalist.org/photos/"+str(p["id"]),
   "observation_source":"https://www.inaturalist.org/observations/"+str(o["id"]),
   "quality_grade":o.get("quality_grade"),"photo_url":purl,"observed_on":o.get("observed_on"),
   "taxon_id":taxon["id"],"taxon_name":"Dichondra recurvata","confidence":"Research Grade observation but independent anatomy ID unverified"})
photo_records.sort(key=lambda x:(x["quality_grade"]!="research",x["observer"] or "",x["observation_id"]))
# select photographic breadth across multiple observations, not duplicate bursts.
selected=[];counts={}; obs_count={}
for x in photo_records:
 obs=x["observation_id"]; user=x["observer"] or ""
 if counts.get(user,0)>=10 or obs_count.get(obs,0)>=6:continue
 selected.append(x);counts[user]=counts.get(user,0)+1;obs_count[obs]=obs_count.get(obs,0)+1
 if len(selected)==32:break
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",18)
canvas=Image.new("RGB",(1400,math.ceil(max(1,len(selected))/4)*280),(245,245,238))
d=ImageDraw.Draw(canvas)
downloads=0
for ix,x in enumerate(selected):
 cx=(ix%4)*350;cy=(ix//4)*280
 try:
  r=SESSION.get(x["photo_url"],timeout=28);r.raise_for_status()
  with Image.open(io.BytesIO(r.content)) as z:
   z.load();picture=ImageOps.exif_transpose(z).convert("RGB")
  x["downloaded_dimensions"]=list(picture.size)
  picture.thumbnail((336,225),Image.Resampling.LANCZOS)
  imagepath=OUT/(str(x["photo_id"])+".jpg")
  picture.save(imagepath,format="JPEG",quality=86,optimize=True)
  x["preview"]="workflow/photo-library/reviews/dichondra-recurvata-20261019/"+imagepath.name
  x["preview_sha256"]=hashlib.sha256(imagepath.read_bytes()).hexdigest()
  canvas.paste(picture,(cx+(350-picture.width)//2,cy+(225-picture.height)//2))
  downloads+=1
 except Exception as e:
  x["download_error"]=str(e)[:160]
  d.text((cx+12,cy+50),"NO IMAGE",font=font,fill=(160,15,15))
 d.text((cx+10,cy+235),str(x["photo_id"])+" "+x["photo_license"],font=font,fill=(22,48,34))
 d.text((cx+10,cy+257),(x["observer"] or "")[:27],font=font,fill=(22,48,34))
canvas.save(OUT/"contact.jpg",format="JPEG",quality=88,optimize=True)
report={"taxon":"Dichondra recurvata","source_taxon_id":taxon["id"],"total_exact_observations":len(all_obs),
        "photo_level_reusable_candidates":len(photo_records),"downloaded_preview_count":downloads,
        "note":"Photo-specific license comes from iNaturalist photo object, NOT observation license. Photos not botanically verified until visual review.",
        "candidates":selected}
(OUT/"screen.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({k:v for k,v in report.items() if k!="candidates"},indent=2))
