#!/usr/bin/env python3
"""Lane 5 Triplasiella eragrostoides (syn. Tridens eragrostoides):
actual source-identified, individually open-licensed photographic candidates.
Scout-only contact sheet, no images published until anatomical pixel review.
"""
import io,base64,json,pathlib,re,time,urllib.parse,urllib.request,urllib.error
from PIL import Image,ImageOps,ImageDraw
OUT=pathlib.Path("reports/lane5-triplasiella-real-anatomy-scout-20261027.json")
REPORT={"taxon":"Triplasiella eragrostoides","synonym":"Tridens eragrostoides",
"candidate_pool":[],"reviewed":[],"holds":[],"installed":0}
def get(url):
 for n in range(4):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotanyIndividuallyLicensedImageScout/1.0 (educational grasses)"})
   with urllib.request.urlopen(req,timeout=42) as f:b=f.read(11000000)
   if len(b)>10500000:raise ValueError("Response over 10.5MB")
   return b
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or n==3:raise
   time.sleep(2*(n+1))
def api(path):return json.loads(get("https://api.inaturalist.org/v1/"+path))
try:
 taxa=api("taxa/autocomplete?"+urllib.parse.urlencode({"q":"Triplasiella eragrostoides","per_page":30})).get("results",[])
 for t in taxa[:12]:REPORT.setdefault("taxon_matches",[]).append({"id":t.get("id"),"name":t.get("name"),"observations_count":t.get("observations_count")})
 tax=next((t for t in taxa if t.get("name")=="Triplasiella eragrostoides"),None)
 if not tax:
  taxa=api("taxa/autocomplete?"+urllib.parse.urlencode({"q":"Tridens eragrostoides","per_page":30})).get("results",[])
  tax=next((t for t in taxa if t.get("name") in ("Triplasiella eragrostoides","Tridens eragrostoides")),None)
 if not tax:raise ValueError("Exact current iNat source taxon not returned")
 REPORT["taxon_id"]=tax["id"]
 for place in ["18",None]:
  for page in range(1,4):
   args={"taxon_id":tax["id"],"photos":"true","per_page":160,"page":page,"order_by":"observed_on","order":"desc"}
   if place:args["place_id"]=place
   obs=api("observations?"+urllib.parse.urlencode(args)).get("results",[])
   for ob in obs:
    if (ob.get("taxon") or {}).get("name") not in ("Triplasiella eragrostoides","Tridens eragrostoides"):continue
    for p in ob.get("photos",[]):
     lic=(p.get("license_code") or "").lower().replace("_","-")
     if lic not in ("cc-by","cc0","cc-by-sa","cc-by-nc","cc-by-nc-sa"):continue
     REPORT["candidate_pool"].append({
      "photo_id":p.get("id"),"observation_id":ob.get("id"),
      "photo_license":lic,"attribution":p.get("attribution"),
      "current_taxon":ob["taxon"]["name"],"quality_grade":ob.get("quality_grade"),
      "place":ob.get("place_guess"),"date_observed":ob.get("observed_on"),
      "photo_url":p.get("url"),"source_page":"https://www.inaturalist.org/photos/"+str(p.get("id"))})
   if len(obs)<160:break
except Exception as e:REPORT["holds"].append(str(e))
REPORT["found"]=len(REPORT["candidate_pool"])
uniq={}
for p in REPORT["candidate_pool"]:
 if p["photo_id"]:uniq[p["photo_id"]]=p
photos=list(uniq.values())
photos.sort(key=lambda p:(p["photo_license"] not in ("cc-by","cc0","cc-by-sa"),
 not re.search(r"Texas|TX\b|Austin|Kyle|San Marcos|San Antonio",p["place"] or "",re.I),
 p["quality_grade"]!="research",str(p["photo_id"])))
selected=[];byobs={}
for p in photos:
 if p["photo_license"] not in ("cc-by","cc0","cc-by-sa"):continue
 if byobs.get(p["observation_id"],0)>=5:continue
 selected.append(p);byobs[p["observation_id"]]=byobs.get(p["observation_id"],0)+1
 if len(selected)>=16:break
sheet=Image.new("RGB",(1200,1500),"white");draw=ImageDraw.Draw(sheet)
for i,p in enumerate(selected):
 row,col=divmod(i,4);x=col*300;y=row*375
 try:
  url=re.sub(r"/(?:square|small|medium|thumb|large)\.(jpe?g|png)",r"/large.\1",p["photo_url"] or "")
  if url==p.get("photo_url") or not url.startswith("https://"):raise ValueError("Source URL form not compatible")
  raw=get(url)
  with Image.open(io.BytesIO(raw)) as im:im.verify()
  with Image.open(io.BytesIO(raw)) as im:
   im=ImageOps.exif_transpose(im).convert("RGB")
   p["preview_pixels"]=list(im.size);im.thumbnail((290,310))
   sheet.paste(im,(x+(300-im.width)//2,y+40+(310-im.height)//2))
  p["status"]="SOURCE_PIXEL_VERIFIED_PENDING_ANATOMY_REVIEW"
 except Exception as ex:p["status"]="HELD: "+str(ex)[:150]
 draw.text((x+4,y+5),str(i)+" "+str(p["photo_id"])+" "+str(p["photo_license"]),fill="#111111")
 draw.text((x+4,y+23),(p["place"] or "")[:45],fill="#111111")
 REPORT["reviewed"].append(p)
if selected:
 buf=io.BytesIO();sheet.save(buf,"JPEG",quality=68,optimize=True)
 print("TRIPLASIELLA_CONTACT_START_"+base64.b64encode(buf.getvalue()).decode()+"_TRIPLASIELLA_CONTACT_END")
OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(REPORT,indent=2)+"\n")
print("TRIPLASIELLA_SUMMARY="+json.dumps({k:v for k,v in REPORT.items() if k not in ("candidate_pool","reviewed")}))
