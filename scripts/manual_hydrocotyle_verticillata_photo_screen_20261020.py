#!/usr/bin/env python3
"""Provisional contact sheet for individually public-licensed iNaturalist Hydrocotyle
verticillata observations in Texas. No edits to canonical species. Research grade
photo metadata is source identification, not organ-level verification. Current
Kew synonymy of var. triradiata to H. bonariensis is flagged in all reports."""
import json,io,hashlib,math,time
from pathlib import Path
import requests
from PIL import Image,ImageOps,ImageDraw,ImageFont
P=Path("workflow/photo-library/reviews/hydrocotyle-verticillata-20261020")
P.mkdir(parents=True,exist_ok=True)
s=requests.Session();s.headers.update({"User-Agent":"HaysCountyBotanyPhotoReview/1.0 (github.com/Crking92/Hays-County-Botany)"})
def get(url,params=None):
 for attempt in range(3):
  try:
   r=s.get(url,params=params,timeout=35)
   if r.status_code in (429,500,502,503,504):
    time.sleep(2+3*attempt);continue
   r.raise_for_status();return r.json()
  except Exception as e:
   if attempt==2: raise
   time.sleep(2+attempt*2)
taxa=get("https://api.inaturalist.org/v1/taxa/autocomplete",{"q":"Hydrocotyle verticillata","per_page":20})
taxonlist=[x for x in taxa.get("results",[]) if x.get("name")=="Hydrocotyle verticillata" and x.get("rank")=="species"]
if len(taxonlist)!=1: raise RuntimeError("Unable to resolve unique exact species taxon")
taxon=taxonlist[0]
observations=[];ids=set()
for page in range(1,5):
 data=get("https://api.inaturalist.org/v1/observations",{"taxon_id":taxon["id"],"place_id":18,"quality_grade":"research","photos":True,"per_page":100,"page":page,"order_by":"observed_on","order":"desc"})
 obs=data.get("results",[])
 for o in obs:
  if o.get("taxon",{}).get("id")==taxon["id"] and o["id"] not in ids:
   ids.add(o["id"]);observations.append(o)
 if len(obs)<100:break
rows=[]; per_observer={};per_obs={}
for o in observations:
 observer=o.get("user",{}).get("login") or "unknown"
 if per_observer.get(observer,0)>=12:continue
 for p in o.get("photos",[])[:8]:
  if per_observer.get(observer,0)>=12 or per_obs.get(o["id"],0)>=5:break
  lc=p.get("license_code")
  if lc not in ("cc-by","cc-by-sa","cc0"):continue
  url=p.get("url") or ""
  if "/photos/" not in url:continue
  row={"photo_id":p["id"],"observation_id":o["id"],"observer":observer,
   "photo_attribution":p.get("attribution"),"photo_license":lc,
   "taxon":"Hydrocotyle verticillata","quality_grade":"research",
   "identification_source":"https://www.inaturalist.org/observations/"+str(o["id"]),
   "photo_source":"https://www.inaturalist.org/photos/"+str(p["id"]),
   "photo_url":url.replace("/square.","/large.").replace("/small.","/large.").replace("/medium.","/large."),
   "taxonomic_warning":"Photo source says H. verticillata s.l.; Kew maps var. triradiata to H. bonariensis, not H. verticillata. Do not upgrade taxon certainty from leaves alone."}
  rows.append(row)
  per_observer[observer]=per_observer.get(observer,0)+1;per_obs[o["id"]]=per_obs.get(o["id"],0)+1
 if len(rows)>=40:break
rows=rows[:40]
w=320;h=285;columns=4
contact=Image.new("RGB",(columns*w,math.ceil(max(1,len(rows))/columns)*h),(243,245,238))
draw=ImageDraw.Draw(contact)
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",15)
downloaded=0
for i,x in enumerate(rows):
 xx=i%columns*w; yy=i//columns*h
 try:
  r=s.get(x["photo_url"],timeout=25);r.raise_for_status()
  if len(r.content)<8000:raise ValueError("tiny source")
  with Image.open(io.BytesIO(r.content)) as original:
   original.load();im=ImageOps.exif_transpose(original).convert("RGB")
  x["original_preview_size"]=list(im.size)
  im.thumbnail((w-14,h-57),Image.Resampling.LANCZOS)
  dst=P/(str(x["photo_id"])+".jpg");im.save(dst,quality=87,optimize=True)
  x["preview_file"]=str(dst);x["preview_sha256"]=hashlib.sha256(dst.read_bytes()).hexdigest()
  contact.paste(im,(xx+(w-im.width)//2,yy+(h-55-im.height)//2))
  downloaded+=1
 except Exception as e:
  x["error"]=str(e)[:180]; draw.text((xx+10,yy+70),"NOT DOWNLOADED",font=font,fill=(150,30,30))
 draw.text((xx+6,yy+h-44),str(x["photo_id"])+" / "+x["photo_license"],font=font,fill=(22,45,30))
 draw.text((xx+6,yy+h-23),x["observer"][:30],font=font,fill=(22,45,30))
contact.save(P/"contact.jpg",quality=88,optimize=True)
report={"target":"Hydrocotyle verticillata Thunb.","taxon_id":taxon["id"],
"texas_research_grade_observations":len(observations),"individual_licensed_candidates":len(rows),
"downloaded_photo_previews":downloaded,
"taxonomy_caution":"The UT Williamson County var. triradiata concept is not unambiguously accepted as H. verticillata under Kew 2026; Kew instead places this name under H. bonariensis. Do not use imprecise species-level images as diagnostic photo proof.",
"candidates":rows}
(P/"candidate-screen.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({k:v for k,v in report.items() if k!="candidates"},indent=2))
