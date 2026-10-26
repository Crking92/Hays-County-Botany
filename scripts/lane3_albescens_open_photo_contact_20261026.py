#!/usr/bin/env python3
"""Tridens albescens Lane 3: photo-specific CC0/CC BY source and contact-sheet scout.

No species changes or invented root/collar morphology. Contact is an audit derivative
of source photos, with creator, source ID and exact observed license in report.
"""
import json,datetime,pathlib,urllib.request,urllib.parse,io,hashlib
from PIL import Image,ImageOps,ImageDraw,ImageFont
root=pathlib.Path("reports")
report={"taxon":"Tridens albescens","status":"HOLD","timestamp_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
 "sources":[],"visual_shortlist":[],"failed":[],"strict_claim":"Research grade source determination only; no independent mature spikelet/collar voucher"}
def get(u,maxlen=8000000):
 req=urllib.request.Request(u,headers={"User-Agent":"HaysCountyBotanyLane3PhotoAudit/1.0 (github.com/Crking92/Hays-County-Botany)","Accept":"application/json,image/jpeg,image/*"})
 with urllib.request.urlopen(req,timeout=35) as res:return res.read(maxlen+1)
taxa=json.loads(get("https://api.inaturalist.org/v1/taxa/autocomplete?q=Tridens%20albescens"))
t=next((x for x in taxa["results"] if x.get("name")=="Tridens albescens" and x.get("rank")=="species"),None)
assert t,"Exact taxon not present; stop rather than guess"
report["taxon_id"]=t["id"]
for page in (1,2):
 query=urllib.parse.urlencode({"taxon_id":t["id"],"quality_grade":"research","photos":"true","per_page":100,"page":page,"order":"desc","order_by":"observed_on"})
 try:d=json.loads(get("https://api.inaturalist.org/v1/observations?"+query))
 except Exception as exc:report["failed"].append({"page":page,"error":str(exc)[:160]});continue
 report["matching_observations"]=d.get("total_results")
 for o in d.get("results",[]):
  if (o.get("taxon") or {}).get("name")!="Tridens albescens":continue
  for p in o.get("photos",[]):
   license=str(p.get("license_code") or "").lower()
   if license not in ["cc0","cc-by","cc-by-sa"]:continue
   report["sources"].append({
    "photo_id":p.get("id"),"source_page":f"https://www.inaturalist.org/photos/{p['id']}",
    "observation_id":o["id"],"observation_url":f"https://www.inaturalist.org/observations/{o['id']}",
    "taxon":"Tridens albescens","license_code":license,
    "creator":p.get("attribution") or (o.get("user") or {}).get("login"),
    "place_guess":o.get("place_guess"),"photo_url":p.get("url"),
    "determination":"iNaturalist research grade, unvouchered by this crew"
   })
 if len(d.get("results",[]))<100:break
report["total_source_images"]=len(report["sources"])
def priority(p):
 city=str(p.get("place_guess") or "").lower()
 score=0
 for w in ["hays","kyle","san marcos","austin","travis","bexar","blanco","burnet","llano","comal","kerr","bandera","uvalde","williamson","gillespie","san antonio"]: 
  if w in city:score-=40;break
 if "texas" in city or "tx" in city:score-=20
 if p["license_code"]=="cc0":score-=10
 return (score,str(p["photo_id"]))
obs_seen=set()
for p in sorted(report["sources"],key=priority):
 if p["observation_id"] not in obs_seen:
  report["visual_shortlist"].append(p)
  obs_seen.add(p["observation_id"])
 if len(report["visual_shortlist"])>=12:break
cols=3;w=420;h=348;rows=4
sheet=Image.new("RGB",(cols*w,rows*h),(245,245,245));draw=ImageDraw.Draw(sheet)
try:font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",12)
except:font=ImageFont.load_default()
for i,p in enumerate(report["visual_shortlist"]):
 x=(i%cols)*w;y=(i//cols)*h
 draw.rectangle((x,y,x+w-1,y+h-1),outline=(130,130,130),width=1)
 try:
  data=get(p["photo_url"].replace("/square.","/large."),maxlen=6000000)
  with Image.open(io.BytesIO(data)) as im: im.verify()
  with Image.open(io.BytesIO(data)) as im: im=ImageOps.exif_transpose(im).convert("RGB")
  im.thumbnail((w-16,h-75),Image.Resampling.LANCZOS)
  sheet.paste(im,(x+(w-im.width)//2,y+10+(h-75-im.height)//2))
  p["preview_displayed"]=True
 except Exception as exc:
  draw.text((x+10,y+120),"IMAGE DOWNLOAD HELD",font=font,fill=(40,40,40))
  p["preview_displayed"]=False
  report["failed"].append({"photo_id":p["photo_id"],"error":str(exc)[:160]})
 draw.text((x+9,y+h-55),str(p["photo_id"])+" "+p["license_code"]+"  "+str(p["place_guess"])[:35],font=font,fill=(0,0,0))
 draw.text((x+9,y+h-33),str(p["creator"])[:45],font=font,fill=(30,30,30))
buf=io.BytesIO();sheet.save(buf,"JPEG",quality=74,optimize=True)
imgfile=root/"lane3-albescens-open-license-contact-20261026.jpg"
imgfile.write_bytes(buf.getvalue())
report["contact_sheet"]=str(imgfile)
report["contact_sha256"]=hashlib.sha256(buf.getvalue()).hexdigest()
report["preview_count"]=sum(1 for p in report["visual_shortlist"] if p.get("preview_displayed"))
report["status"]="REUSABLE_SOURCE_CONTACT_READY" if report["preview_count"]>=4 else "SHORTLIST_NEEDS_FURTHER_SOURCE_RESEARCH"
(root/"lane3-albescens-open-license-contact-20261026.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({"status":report["status"],"source_images":len(report["sources"]),"preview_count":report["preview_count"],"photo_ids":[x["photo_id"] for x in report["visual_shortlist"]],"holds":report["failed"]}))
