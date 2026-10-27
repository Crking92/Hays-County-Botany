#!/usr/bin/env python3
"""Lane 5: discover real, individually licensed Texas brome photographs on iNaturalist.
This job is research ONLY: no photos promoted without contact-sheet visual inspection.
Source exact taxon, geographic region and individual photo license required for each.
"""
import base64,io,json,pathlib,urllib.parse,urllib.request,urllib.error,time,re
from PIL import Image,ImageOps,ImageDraw
OUT=pathlib.Path("reports/lane5-bromus-texensis-open-photo-scout-20261027.json")
report={"date":"2026-10-27","species":"Bromus texensis","new_photo_files":0,
        "source":"iNaturalist v1 exact-taxon observations with individual licensed photos",
        "valid_candidates":[],"holds":[],"taxon":None,"photo_review_gate":"not installed, inspect contact sheet before archive"}
def get(url):
 for n in range(4):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyGrassPhotoScout/1.0 (educational plant-identification; source rights respected)","Accept":"application/json,image/jpeg,*/*"})
   with urllib.request.urlopen(req,timeout=45) as f:raw=f.read(9000000)
   if len(raw)>8500000:raise ValueError("Over 8.5MB")
   return raw
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or n==3:raise
   time.sleep((n+1)*2)
def api(url):return json.loads(get("https://api.inaturalist.org/v1/"+url))
photos=[]
try:
 taxa=api("taxa/autocomplete?"+urllib.parse.urlencode({"q":"Bromus texensis","per_page":30})).get("results",[])
 exact=next((x for x in taxa if x.get("name")=="Bromus texensis"),None)
 if not exact:raise ValueError("Taxon not found, no photo installation")
 taxon_id=exact["id"];report["taxon"]={"id":taxon_id,"name":exact["name"]}
 for page in range(1,5):
  params={"taxon_id":taxon_id,"photos":"true","per_page":150,"page":page,"order_by":"observed_on","order":"desc"}
  obs=api("observations?"+urllib.parse.urlencode(params)).get("results",[])
  if not obs:break
  for o in obs:
   if (o.get("taxon") or {}).get("name")!="Bromus texensis":continue
   for p in o.get("photos",[]):
    lic=str(p.get("license_code") or "").lower().replace("_","-")
    if lic not in ("cc0","cc-by","cc-by-sa","cc-by-nc","cc-by-nc-sa"):continue
    url=p.get("url") or ""
    pid=p.get("id")
    if not url or not pid:continue
    photos.append({"id":pid,"observation_id":o.get("id"),
      "observation_quality":o.get("quality_grade"),"observed_on":o.get("observed_on"),
      "license":lic,"creator":p.get("attribution"),"photo_url":url,
      "place":o.get("place_guess"),"observation_page":"https://www.inaturalist.org/observations/"+str(o.get("id")),
      "photo_page":"https://www.inaturalist.org/photos/"+str(pid)})
  if len(obs)<150:break
 report["total_open_license_photo_candidates"]=len(photos)
 report["photo_candidate_pool"]=photos[:80]
except Exception as e:report["holds"].append(str(e))
# Best photographed Texas/nearby exact source. A preview's age/location cannot validate
# whether it captures inner ligule, roots, glumes or lemma; inspect explicitly.
licensed=[p for p in photos if p["license"] in ("cc0","cc-by","cc-by-sa")]
licensed.sort(key=lambda p:(not (p["place"] and re.search("Texas|TX\\b",p["place"],re.I)),p["observation_quality"]!="research",p["id"]))
selected=licensed[:8]
sheet=Image.new("RGB",(1200,900),"white")
draw=ImageDraw.Draw(sheet)
for i,p in enumerate(selected):
 row,col=divmod(i,4);boxw=300;boxh=450
 x=col*boxw;y=row*boxh
 try:
  uri=re.sub(r"/(?:square|small|medium|thumb|large)\.(jpe?g|png)",r"/large.\1",p["photo_url"])
  raw=get(uri)
  with Image.open(io.BytesIO(raw)) as im:im.verify()
  with Image.open(io.BytesIO(raw)) as im:
   im=ImageOps.exif_transpose(im).convert("RGB")
   p["preview_size"]=list(im.size)
   im.thumbnail((290,380))
   sheet.paste(im,(x+(boxw-im.width)//2,y+39+(380-im.height)//2))
  p["contact_index"]=i
  p["preview_status"]="RETRIEVED_PIXELS_PENDING_ANNOTATION"
 except Exception as e:p["preview_status"]="HELD: "+str(e)
 draw.text((x+4,y+5),str(i)+" "+str(p["id"])+" "+p["license"],fill="#111111")
 draw.text((x+4,y+22),str(p["place"] or "")[:42],fill="#111111")
 report["valid_candidates"].append(p)
if selected:
 buf=io.BytesIO();sheet.save(buf,"JPEG",quality=66,optimize=True)
 print("BROMUS_TEXENSIS_CONTACT_START_"+base64.b64encode(buf.getvalue()).decode()+"_BROMUS_TEXENSIS_CONTACT_END")
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(report,indent=2)+"\n")
print("BROMUS_SCOUT_SUMMARY="+json.dumps({k:v for k,v in report.items() if k!="photo_candidate_pool"}))
