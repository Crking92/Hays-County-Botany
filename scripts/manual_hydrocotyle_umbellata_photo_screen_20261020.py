#!/usr/bin/env python3
"""Licensed exact-species Hydrocotyle umbellata photos: view-only contact sheet and
independent archived GBIF media-rights check. No canonical photo installation."""
import json,math,io,hashlib,time
from pathlib import Path
import requests
from PIL import Image,ImageOps,ImageDraw,ImageFont
DEST=Path("workflow/photo-library/reviews/hydrocotyle-umbellata-20261020")
DEST.mkdir(parents=True,exist_ok=True)
s=requests.Session();s.headers.update({"User-Agent":"HaysCountyBotanyDiagnosticPhotoScreen/1.0 (github.com/Crking92/Hays-County-Botany)"})
def get(url,params=None):
 for t in range(3):
  try:
   r=s.get(url,params=params,timeout=34)
   if r.status_code in (429,502,503,504):
    time.sleep(3+t*3);continue
   r.raise_for_status();return r.json()
  except Exception as e:
   if t==2:return {"error":str(e)}
   time.sleep(1+t*2)
 return {"error":"unavailable"}
rights=get("https://api.gbif.org/v1/occurrence/6234372459")
sam={"gbif_occurrence":6234372459,"source_page":"https://www.gbif.org/occurrence/6234372459",
 "rights_holder":rights.get("rightsHolder"),"record_license":rights.get("license"),
 "media":[{"identifier":m.get("identifier"),"license":m.get("license"),"rightsHolder":m.get("rightsHolder"),"creator":m.get("creator")} for m in rights.get("media",[])],
 "error":rights.get("error")}
(DEST/"archived-sam-gbif-license.json").write_text(json.dumps(sam,indent=2)+"\n")
print("ORIGINAL ARCHIVED PHOTO MEDIA RIGHTS:",json.dumps(sam))
taxa=get("https://api.inaturalist.org/v1/taxa/autocomplete",{"q":"Hydrocotyle umbellata","per_page":20})
matches=[x for x in taxa.get("results",[]) if x.get("name")=="Hydrocotyle umbellata" and x.get("rank")=="species"]
if len(matches)!=1:raise RuntimeError("No unique exact taxon "+str(taxa)[:400])
taxon=matches[0]
photos=[];obsn=0;users={};per_obs={}
for place in ("Texas",):
 for page in (1,2,3):
  data=get("https://api.inaturalist.org/v1/observations",{"taxon_id":taxon["id"],"place_id":18,
  "quality_grade":"research","photos":True,"per_page":100,"page":page,"order_by":"observed_on","order":"desc"})
  if data.get("error"):raise RuntimeError("Observations API: "+data["error"])
  obs=data.get("results",[])
  if not obs:break
  obsn+=len(obs)
  for o in obs:
   if o.get("taxon",{}).get("id")!=taxon["id"]:continue
   user=o.get("user",{}).get("login") or "unknown"
   if users.get(user,0)>=12:continue
   if per_obs.get(o["id"],0)>=5:continue
   for p in o.get("photos",[])[:8]:
    lc=p.get("license_code","")
    if lc not in ("cc-by","cc-by-sa","cc0"):continue
    if users.get(user,0)>=12 or per_obs.get(o["id"],0)>=5:break
    url=p.get("url") or ""
    if "/photos/" not in url:continue
    photos.append({"photo_id":p["id"],"photo_license_code":lc,
      "photo_attribution":p.get("attribution"),"photographer_account":user,
      "observation_id":o["id"],"observed_on":o.get("observed_on"),
      "observation_source":"https://www.inaturalist.org/observations/"+str(o["id"]),
      "source_page":"https://www.inaturalist.org/photos/"+str(p["id"]),
      "url":url.replace("/square.","/large.").replace("/small.","/large.").replace("/medium.","/large."),
      "taxon":"Hydrocotyle umbellata","quality_grade":o.get("quality_grade"),
      "exact_taxon":o.get("taxon",{}).get("name")})
    users[user]=users.get(user,0)+1;per_obs[o["id"]]=per_obs.get(o["id"],0)+1
  if len(photos)>=32 or len(obs)<100:break
 if len(photos)>=32:break
# Prefer different dates/observers; sorted by API recency. Contact sheet <= 32.
photos=photos[:32]
cols=4;tile_w=340;tile_h=290
sheet=Image.new("RGB",(cols*tile_w,math.ceil(max(1,len(photos))/cols)*tile_h),(243,245,238))
d=ImageDraw.Draw(sheet)
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",16)
fetched=0
for k,p in enumerate(photos):
 x=(k%cols)*tile_w;y=(k//cols)*tile_h
 try:
  r=s.get(p["url"],timeout=35);r.raise_for_status()
  with Image.open(io.BytesIO(r.content)) as original:
   original.load();im=ImageOps.exif_transpose(original).convert("RGB")
  p["original_preview_dimensions"]=list(im.size)
  im.thumbnail((325,236),Image.Resampling.LANCZOS)
  sheet.paste(im,(x+(tile_w-im.width)//2,y+(235-im.height)//2))
  file=DEST/(str(p["photo_id"])+".jpg")
  im.save(file,quality=86,optimize=True)
  p["preview_sha256"]=hashlib.sha256(file.read_bytes()).hexdigest()
  p["preview_file"]=str(file)
  fetched+=1
 except Exception as e:
  p["error"]=str(e)[:180]
  d.text((x+10,y+50),"PHOTO FAILED",font=font,fill=(144,35,22))
 d.text((x+8,y+246),str(p["photo_id"])+" / "+p["photo_license_code"],font=font,fill=(20,55,38))
 d.text((x+8,y+268),p["photographer_account"][:28],font=font,fill=(20,55,38))
sheet.save(DEST/"contact.jpg",quality=91,optimize=True)
report={"species":"Hydrocotyle umbellata","inat_exact_taxon_id":taxon["id"],
"research_grade_texas_observations_examined":obsn,"photo_specific_licensed_candidates":len(photos),
"downloaded_previews":fetched,
"rule":"Individual photo license from iNaturalist observation photo object; taxon observation research-grade, not independent anatomical voucher review.",
"candidates":photos}
(DEST/"candidate-screen.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({k:v for k,v in report.items() if k!="candidates"},indent=2))
