#!/usr/bin/env python3
"""One-time contact sheet of explicitly CC-licensed individual iNaturalist images
of research-grade Texas Sorghum halepense. Candidate only; no canonical changes."""
import io,json,math,hashlib,time
from pathlib import Path
import requests
from PIL import Image,ImageDraw,ImageOps,ImageFont
OUT=Path("workflow/photo-library/reviews/sorghum-halepense-20261020")
OUT.mkdir(parents=True,exist_ok=True)
S=requests.Session();S.headers.update({"User-Agent":"HaysBotanyCrewGrassPhotoScreen/1.0 (https://github.com/Crking92/Hays-County-Botany)"})
def jget(url,params):
 for i in range(3):
  r=S.get(url,params=params,timeout=37)
  if r.status_code in (429,502,503,504):
   time.sleep(2+i*3);continue
  r.raise_for_status();return r.json()
 raise RuntimeError("iNat unavailable")
j=jget("https://api.inaturalist.org/v1/taxa/autocomplete",{"q":"Sorghum halepense","per_page":20})
exact=[x for x in j.get("results",[]) if x.get("name")=="Sorghum halepense" and x.get("rank")=="species"]
if len(exact)!=1:raise RuntimeError("Exact taxon not unique")
taxon=exact[0]
candidates=[];observations=[];per_user={};per_obs={};seen=set()
for sort in ("asc","desc"):
 for pg in range(1,5):
  data=jget("https://api.inaturalist.org/v1/observations",{"taxon_id":taxon["id"],"place_id":18,"quality_grade":"research",
       "photos":True,"per_page":100,"page":pg,"order_by":"observed_on","order":sort})
  obs=data.get("results",[])
  for o in obs:
   if o.get("taxon",{}).get("id")!=taxon["id"] or o["id"] in seen:continue
   seen.add(o["id"]);observations.append(o)
   user=o.get("user",{}).get("login") or "unknown"
   if per_user.get(user,0)>=10:continue
   for p in o.get("photos",[])[:7]:
    if per_obs.get(o["id"],0)>=5 or per_user.get(user,0)>=10:break
    lic=p.get("license_code")
    if lic not in ("cc-by","cc-by-sa","cc0"):continue
    url=p.get("url") or ""
    if "/photos/" not in url:continue
    candidates.append({"photo_id":p["id"],"observation_id":o["id"],"photographer":user,
      "credit":p.get("attribution"),"license_code":lic,
      "source_page":"https://www.inaturalist.org/photos/"+str(p["id"]),
      "observation_page":"https://www.inaturalist.org/observations/"+str(o["id"]),
      "photo_url":url.replace("/square.","/large.").replace("/small.","/large.").replace("/medium.","/large."),
      "source_taxon":"Sorghum halepense","grade":"research","source_year":o.get("observed_on"),
      "caution":"An exact research-grade iNat ID supports sourcing, not certainty of hybrid-vs-species or micro-anatomy."})
    per_user[user]=per_user.get(user,0)+1;per_obs[o["id"]]=per_obs.get(o["id"],0)+1
  if len(obs)<100 or len(candidates)>=48:break
 if len(candidates)>=48:break
candidates=candidates[:48]
W,H,COL=330,287,4
sheet=Image.new("RGB",(COL*W,math.ceil(max(1,len(candidates))/COL)*H),(243,248,238))
d=ImageDraw.Draw(sheet)
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",16)
good=0
for i,x in enumerate(candidates):
 xx=i%COL*W; yy=i//COL*H
 try:
  r=S.get(x["photo_url"],timeout=37);r.raise_for_status()
  with Image.open(io.BytesIO(r.content)) as raw:
   raw.load();im=ImageOps.exif_transpose(raw).convert("RGB")
  x["preview_original_size"]=list(im.size)
  im.thumbnail((W-12,H-55),Image.Resampling.LANCZOS)
  out=OUT/(str(x["photo_id"])+".jpg");im.save(out,"JPEG",quality=88,optimize=True)
  x["preview_sha256"]=hashlib.sha256(out.read_bytes()).hexdigest()
  sheet.paste(im,(xx+(W-im.width)//2,yy+(H-55-im.height)//2));good+=1
 except Exception as e:
  x["error"]=str(e)[:160];d.text((xx+8,yy+70),"DOWNLOAD FAILURE",font=font,fill=(150,32,32))
 d.text((xx+7,yy+H-48),str(x["photo_id"])+" "+x["license_code"],font=font,fill=(20,48,34))
 d.text((xx+7,yy+H-23),x["photographer"][:30],font=font,fill=(20,48,34))
sheet.save(OUT/"contact.jpg","JPEG",quality=89,optimize=True)
report={"species":"Sorghum halepense","taxon_id":taxon["id"],"texas_exact_research_observations_examined":len(observations),
"photo_cc_candidates":len(candidates),"downloaded_previews":good,
"wanted":["tall standing coarse-vegetation habit","white leaf midrib","exposed scaly rhizome with nodes","2–6 mm ciliate membranous ligule macro","branched loose terminal panicle","sessile spikelet plus stalked paired spikelet macro"],
"notes":"Individual CC license from photo metadata; feral shattercane and related Sorghum varieties can overlap; macro and rhizomes must be verified.",
"candidates":candidates}
(OUT/"screen.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({k:v for k,v in report.items() if k!="candidates"},indent=2))
