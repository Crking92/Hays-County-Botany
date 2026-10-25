#!/usr/bin/env python3
"""Screen additional Commons Chloris verticillata exact-species images.
Photo rights and low resolution PREVIEWS only, no species/gallery publication.
"""
import io, json, pathlib, urllib.parse, urllib.request, re, html, hashlib, base64, time
from PIL import Image
OUT=pathlib.Path("reports/lane5-tumble-commons-macro-scout-20261025.json")
names=[f"ChlorisV{i}.jpg" for i in range(1,9)] + [f"Chloris verticillata - windmillgrass - {i}.jpg" for i in ["51679981431","51680235078","51680653829","51680867945"]]
def get(url):
 req=urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotany/1.0 (CC media rights review)"})
 with urllib.request.urlopen(req,timeout=50) as response:return response.read()
q={"action":"query","prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":"1200","titles":"|".join("File:"+name for name in names),"format":"json"}
pages=json.loads(get("https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(q)))["query"]["pages"]
result={"species":"Chloris verticillata","photos":[],"errors":[]}
for page in pages.values():
 title=page.get("title","")
 if "imageinfo" not in page:
  result["errors"].append({"title":title,"reason":"Commons image info missing"})
  continue
 info=page["imageinfo"][0];meta=info.get("extmetadata",{})
 lic=html.unescape(re.sub("<[^>]+>","",meta.get("LicenseShortName",{}).get("value","")))
 artist=html.unescape(re.sub("<[^>]+>"," ",meta.get("Artist",{}).get("value",""))).strip()
 description=html.unescape(re.sub("<[^>]+>"," ",meta.get("ImageDescription",{}).get("value",""))).strip()
 entry={"title":title,"license":lic,"artist":artist[:300],"description":description[:550],
 "source_page":"https://commons.wikimedia.org/wiki/"+title.replace(" ","_"),"image_url":info.get("url"),
 "width":info.get("width"),"height":info.get("height"),"thumburl":info.get("thumburl"),"thumb_width":info.get("thumbwidth")}
 if re.sub(r"[^A-Z0-9]","",lic.upper()) not in ("CCBY20","CCBYSA20","CCBYSA30","CCBYSA40","CCBY30","CCBY40","CC0","CC010","PUBLICDOMAIN"):
  entry["hold"]="No supported CC/public-domain image license"
 else:
  try:
   raw=get(info.get("thumburl") or info["url"])
   im=Image.open(io.BytesIO(raw));im.verify()
   im=Image.open(io.BytesIO(raw)).convert("RGB")
   im.thumbnail((320,260))
   buf=io.BytesIO();im.save(buf,"JPEG",quality=67,optimize=True)
   entry["preview_base64"]=base64.b64encode(buf.getvalue()).decode("ascii")
   entry["preview_size"]=list(im.size)
  except Exception as exc:
   entry["hold"]="Failed to retrieve preview: "+str(exc)[:160]
 result["photos"].append(entry)
 time.sleep(0.15)
OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"count":len(result["photos"]),"entries":[{k:v for k,v in x.items() if k not in ["preview_base64","thumburl","image_url"]} for x in result["photos"]],"errors":result["errors"]}))
