#!/usr/bin/env python3
"""Scout Commons images of inland sea oats for rooted base and true collar.
Previews only, no original binaries added to public gallery until pixel review.
"""
import base64,html,io,json,pathlib,re,urllib.parse,urllib.request,urllib.error,time
from PIL import Image
OUT=pathlib.Path("reports/lane5-inland-sea-oats-base-collar-scout-20261026.json")
NAMES=["Chasmanthium latifolium"+str(i)+".jpg" for i in range(1,17)]
def get(u):
 request=urllib.request.Request(u,headers={"User-Agent":"HaysCountyBotanyPhotoScout/1.0 (educational field identification)"})
 for attempt in range(5):
  try:
   with urllib.request.urlopen(request,timeout=40) as response:return response.read()
  except urllib.error.HTTPError as e:
   if e.code not in (429,502,503) or attempt==4:raise
   time.sleep(2*(attempt+1))
params=urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo|categories","cllimit":"max","iiprop":"url|extmetadata","iiurlwidth":"850","titles":"|".join("File:"+n for n in NAMES)})
pages=json.loads(get("https://commons.wikimedia.org/w/api.php?"+params))["query"]["pages"]
out={"date":"2026-10-26","species":"Chasmanthium latifolium","photos":[],"notes":"Photo licensing and taxonomy screened; images must be reviewed visually before choosing anatomical role; no archival commit."}
for page in pages.values():
 title=page.get("title")
 x={"title":title}
 if "imageinfo" not in page:
  x["hold"]="No Commons media";out["photos"].append(x);continue
 info=page["imageinfo"][0];m=info.get("extmetadata",{})
 artist=html.unescape(re.sub(r"<[^>]+>"," ",m.get("Artist",{}).get("value",""))).strip()
 lic=re.sub(r"[^A-Z0-9]","",m.get("LicenseShortName",{}).get("value","").upper())
 desc=html.unescape(re.sub(r"<[^>]+>"," ",m.get("ImageDescription",{}).get("value",""))).strip()
 categories=[v.get("title") for v in page.get("categories",[])]
 x.update({"artist":artist,"license":lic,"description":desc[:350],"dimensions":[info.get("width"),info.get("height")],"source_page":"https://commons.wikimedia.org/wiki/"+urllib.parse.quote(title.replace(" ","_"),safe=":") ,"original_url":info.get("url"),"taxon_category":"Category:Chasmanthium latifolium" in categories})
 if lic!="CCBYSA40" or "Douglas" not in artist or not x["taxon_category"]:
  x["hold"]="Rights/author/taxon category unclear"
 else:
  try:
   raw=get(info.get("thumburl") or info["url"])
   im=Image.open(io.BytesIO(raw));im.verify()
   im=Image.open(io.BytesIO(raw)).convert("RGB")
   im.thumbnail((380,310))
   buf=io.BytesIO();im.save(buf,"JPEG",quality=70)
   x["preview_base64"]=base64.b64encode(buf.getvalue()).decode("ascii")
   x["preview_size"]=list(im.size)
  except Exception as e:x["hold"]="Preview download failed: "+str(e)[:120]
 out["photos"].append(x)
 time.sleep(0.1)
OUT.write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps({"count":len(out["photos"]),"photos":[{k:v for k,v in x.items() if k!="preview_base64"} for x in out["photos"]]}))
