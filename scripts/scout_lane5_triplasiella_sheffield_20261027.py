#!/usr/bin/env python3
"""Lane 5 second Triplasiella anatomy photo scouting:
Sheffield TX CC0 Eric Knight CC BY and Cleveland Powell CC BY.
All images are individually checked for accepted taxon, research grade,
open individual photo license and anatomical pixels. Scout ONLY.
"""
import io,base64,json,pathlib,re,time,urllib.request,urllib.error
from PIL import Image,ImageOps,ImageDraw
OUT=pathlib.Path("reports/lane5-triplasiella-sheffield-eric-collar-scout-20261027.json")
SPECIES="Triplasiella eragrostoides"
TARGETS=[
 (321843312,[582111334,582111370,582111406]),
 (322073807,[582570756,582570787,582570805,582570826,582570844]),
 (325327423,[589004501,589004515,589004518,589004519,589004478]),
 (210486821,[372289769,372289841,372289918])
]
REPORT={"taxon":SPECIES,"date":"2026-10-27","reviewed":[],"holds":[],"new_approved_photos":0}
def get(url):
 for n in range(4):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyCC0TexasGrassAnatomyPhotoReview/1.0 (educational public learner)"})
   with urllib.request.urlopen(req,timeout=45) as f:d=f.read(11000000)
   if len(d)>10600000:raise ValueError("Image or metadata too large")
   return d
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or n==3:raise
   time.sleep(3*(n+1))
sheet=Image.new("RGB",(1200,1500),"white");draw=ImageDraw.Draw(sheet)
i=0
for obsid,photoids in TARGETS:
 try:
  j=json.loads(get("https://api.inaturalist.org/v1/observations/"+str(obsid)))
  obs=next(iter(j.get("results",[])),None)
  if not obs or (obs.get("taxon") or {}).get("name")!=SPECIES or obs.get("quality_grade")!="research":
   raise ValueError("Current source does not confirm accepted species research-grade")
  region=obs.get("place_guess") or ""
  if not re.search(r"Texas|TX\b|Sheffield|San Antonio",region,re.I):raise ValueError("Observation outside Texas")
  for pid in photoids:
   if i>=16:break
   row,col=divmod(i,4);x=col*300;y=row*375
   rec={"observation":obsid,"photo_id":pid,"place":region}
   try:
    p=next((p for p in obs.get("photos",[]) if p.get("id")==pid),None)
    if not p:raise ValueError("Source photo no longer attached to this observation")
    lic=(p.get("license_code") or "").lower().replace("_","-")
    if lic not in ("cc0","cc-by","cc-by-sa"):raise ValueError("Image-specific license not open")
    uri=p.get("url") or ""
    src=re.sub(r"/(?:square|small|medium|thumb|large)\.(jpe?g|png)",r"/large.\1",uri)
    if src==uri:raise ValueError("Unrecognized image form")
    blob=get(src)
    with Image.open(io.BytesIO(blob)) as im:im.verify()
    with Image.open(io.BytesIO(blob)) as im:
     im=ImageOps.exif_transpose(im).convert("RGB")
     rec["image_dimensions"]=list(im.size)
     im.thumbnail((287,315))
     sheet.paste(im,(x+(300-im.width)//2,y+39+(315-im.height)//2))
    rec.update({"license":lic,"creator":p.get("attribution"),"photo_page":"https://www.inaturalist.org/photos/"+str(pid),"status":"PIXELS_AND_IMAGE_RIGHTS_VERIFIED_ANATOMY_UNCLASSIFIED"})
   except Exception as exc:rec.update({"status":"HELD","reason":str(exc)})
   draw.text((x+4,y+4),str(i)+"  "+str(pid)+" "+str(rec.get("license") or ""),fill="#111111")
   draw.text((x+4,y+22),region[:43],fill="#111111")
   REPORT["reviewed"].append(rec);i+=1
 except Exception as ex:REPORT["holds"].append({"observation":obsid,"reason":str(ex)})
if REPORT["reviewed"]:
 b=io.BytesIO();sheet.save(b,"JPEG",quality=69,optimize=True)
 print("TRIPLASIELLA_SECOND_START_"+base64.b64encode(b.getvalue()).decode()+"_TRIPLASIELLA_SECOND_END")
OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(REPORT,indent=2)+"\n")
print("TRIPLASIELLA_SECOND_SUMMARY="+json.dumps({"sampled":len(REPORT["reviewed"]),"holds":REPORT["holds"]}))
