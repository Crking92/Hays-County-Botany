#!/usr/bin/env python3
"""Exact species iNaturalist per-photo-public-license Sorghastrum elliottii photo candidate scout.
Scouts only; never installs nor scores thumbnails. OBSERVATION photograph license,
not observer's profile and not collection-level default, controls each candidate.
"""
import io,json,math,pathlib,time,urllib.request,urllib.error,urllib.parse
from PIL import Image,ImageOps,ImageDraw,ImageFont
ROOT=pathlib.Path("reports/lane4-elliottii-licensed-source-photo-scout-20261027")
ROOT.mkdir(parents=True,exist_ok=True)
def request(url,limit=8_000_000):
 err=None
 for i in range(3):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotanyVisualLearner/1.0 (exact species source/CC audit; github.com/Crking92/Hays-County-Botany)","Accept":"application/json,image/*;q=0.8"})
   with urllib.request.urlopen(req,timeout=40) as rsp:
    d=rsp.read(limit+1)
   if len(d)>limit:raise ValueError("File too large")
   return d
  except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as e:
   err=e
   if isinstance(e,urllib.error.HTTPError) and e.code not in (429,500,502,503,504):raise
   time.sleep(2+i)
 raise RuntimeError(str(err))
def api(path,params):
 return json.loads(request("https://api.inaturalist.org/v1/"+path+"?"+urllib.parse.urlencode(params),6_000_000))
taxa=api("taxa/autocomplete",{"q":"Sorghastrum elliottii","per_page":20}).get("results",[])
taxon=next((x for x in taxa if x.get("name","").lower()=="sorghastrum elliottii" and x.get("rank")=="species"),None)
assert taxon, "iNat did not resolve exact accepted Sorghastrum elliottii taxon"
rawobs=[]
for params in [
 {"taxon_id":taxon["id"],"photos":"true","quality_grade":"research","per_page":100,"order_by":"observed_on","order":"desc"},
 {"taxon_id":taxon["id"],"photos":"true","quality_grade":"research","per_page":100,"order_by":"observed_on","order":"asc"},
 {"taxon_id":taxon["id"],"photos":"true","per_page":100,"order_by":"votes","order":"desc"}]:
 try:rawobs.extend(api("observations",params).get("results",[]))
 except Exception as e:print("Observation query held "+repr(e),flush=True)
seenset=set();obs=[]
for o in rawobs:
 if o.get("id") in seenset:continue
 seenset.add(o.get("id"))
 if o.get("taxon",{}).get("name","").lower()!="sorghastrum elliottii":continue
 obs.append(o)
allowed={"cc0","cc-by","cc-by-sa"}
photos=[]
for o in obs:
 for position,p in enumerate(o.get("photos",[])):
  license=p.get("license_code")
  if license not in allowed:continue
  target=p.get("url","")
  # thumb resolution; do not copy ORIGINAL and do not use as a hosted species JPEG.
  thumbnail=target.replace("/square.","/medium.") if "/square." in target else target
  if not thumbnail.startswith("https://") or "inaturalist" not in urllib.parse.urlparse(thumbnail).hostname:continue
  photos.append({"observation_id":o["id"],"photo_id":p["id"],"license_code":license,"photographer":p.get("attribution",""),
                 "observation_grade":o.get("quality_grade"),"observed_on":o.get("observed_on"),
                 "place_guess":(o.get("place_guess") or "")[:150],
                 "photo_url":f'https://www.inaturalist.org/photos/{p["id"]}',
                 "observation_url":f'https://www.inaturalist.org/observations/{o["id"]}',
                 "preview":thumbnail,"image_description":p.get("original_dimensions"),"position":position,
                 "photos_same_observation":len(o.get("photos",[])),
                 "taxon_name":o["taxon"]["name"]})
photos.sort(key=lambda x:(-(x["photos_same_observation"]>=3),-x["photos_same_observation"],-(x["place_guess"].lower().find("texas")>=0),x["position"]))
photos=photos[:60]
cols=6;cw=220;ch=243;rows=math.ceil(len(photos)/cols)
sheet=Image.new("RGB",(cols*cw,max(ch,rows*ch)),(251,249,242))
draw=ImageDraw.Draw(sheet);font=ImageFont.load_default()
for i,p in enumerate(photos):
 x=i%cols*cw;y=i//cols*ch
 draw.rectangle((x+2,y+2,x+cw-2,y+ch-2),outline=(110,110,110))
 try:
  src=request(p["preview"],2_000_000)
  im=ImageOps.exif_transpose(Image.open(io.BytesIO(src))).convert("RGB")
  im.thumbnail((210,190),Image.Resampling.LANCZOS)
  sheet.paste(im,(x+5+(210-im.width)//2,y+5+(190-im.height)//2))
  p["preview_verified"]=True
 except Exception as e:p["preview_error"]=str(e)[:100]
 draw.text((x+8,y+197),str(i)+" "+str(p["photo_id"])+"  "+p["license_code"],font=font,fill=(25,25,25))
 draw.text((x+8,y+212),(p["place_guess"] or "unknown locality")[:32],font=font,fill=(25,25,25))
file=ROOT/"licensed-exact-species-contact-sheet.jpg"
sheet.save(file,"JPEG",quality=84,optimize=True)
report={"source":"iNaturalist observed exact species Sorghastrum elliottii API result; record could still be taxonomically incorrect; independently inspect original photo and specimen/context.",
 "species_taxon_id":taxon["id"],"accepted_taxon":taxon["name"],
 "observations_queried":len(obs),"individually_public_CC_candidates":len(photos),
 "media_status":"NOT INSTALLED, NOT SCORED. Thumbnail review collage is a SOURCE SCOUT only.",
 "photo_rights":"Individual photo record license codes CC0/CC BY/CC BY-SA, exact version not audited. Preserve source identification, photographer attribution; photos without source-level rights excluded.",
 "photos":photos}
(ROOT/"metadata.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps({"taxon":taxon["id"],"count":len(photos),"observations":len(obs),"top_candidates":[{k:p.get(k) for k in ("photo_id","license_code","photographer","place_guess","photos_same_observation","observation_id")} for p in photos[:45]]},ensure_ascii=False,indent=2),flush=True)
