#!/usr/bin/env python3
"""Archive two already-approved Commons Hordeum pusillum photos and relink gallery."""
import io,json,pathlib,re,html,urllib.parse,urllib.request,hashlib
from PIL import Image
p=pathlib.Path("content/taxa/Poaceae/Hordeum/hordeum-pusillum/species.json")
s=json.loads(p.read_text());out=[]
def get(u):
 req=urllib.request.Request(u,headers={"User-Agent":"HaysBotany/1.0 licensed botany media archive"})
 with urllib.request.urlopen(req,timeout=45) as x:return x.read()
for item in s["visual_comparison"]["items"]:
 source=item.get("source_page","")
 if source not in ["https://commons.wikimedia.org/wiki/File:Hordeum_pusillum_(6180949841).jpg","https://commons.wikimedia.org/wiki/File:Hordeum_pusillum_(7495179082).jpg"]:continue
 if item["image_url"].startswith("content/"):continue
 try:
  name=urllib.parse.unquote(source.split("File:",1)[1]).replace("_"," ")
  q=urllib.parse.urlencode({"action":"query","prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":"1500","titles":"File:"+name,"format":"json"})
  info=next(iter(json.loads(get("https://commons.wikimedia.org/w/api.php?"+q))["query"]["pages"].values()))["imageinfo"][0]
  meta=info["extmetadata"];lic=re.sub("[^A-Z0-9]","",meta.get("LicenseShortName",{}).get("value","").upper())
  artist=html.unescape(re.sub("<[^>]+>","",meta.get("Artist",{}).get("value",""))).strip()
  if lic!="CCBYSA20" or "Matt Lavin" not in artist:raise ValueError("rights/author mismatch "+lic+" "+artist)
  raw=get(info.get("thumburl") or info["url"])
  im=Image.open(io.BytesIO(raw));im.verify()
  im=Image.open(io.BytesIO(raw)).convert("RGB")
  if min(im.size)<450:raise ValueError("image insufficient resolution")
  filename="commons-hordeum-pusillum-"+hashlib.sha256(source.encode()).hexdigest()[:12]+".jpg"
  dest=p.parent/"images"/filename;im.save(dest,"JPEG",quality=90,optimize=True)
  item["prior_external_image_url"]=item["image_url"];item["image_url"]=str(dest)
  item["photo_status"]="Commons source and rights verified; pixels reencoded and EXIF removed; original gross arrows retained pending local Pages alignment verification"
  s["images"].append({"file":"images/"+filename,"role":item.get("image_role","Source-labelled mature barley photograph"),"creator":"Matt Lavin","license":"CC BY-SA 2.0","license_url":"https://creativecommons.org/licenses/by-sa/2.0/","source_page":source,"photo_status":"ARCHIVED EXACT TAXON; microscopic node/ligule morphology not certified"})
  out.append({"source":source,"file":str(dest),"status":"archived"})
 except Exception as ex:out.append({"source":source,"status":"held","reason":str(ex)[:200]})
if any(x["status"]=="archived" for x in out):
 s["field_id_finish_pass"]["lane5_hordeum_archive_20261023"]={"results":out,"status":"FIELD_READY_PHOTO_GAPS","remaining":"Attached 3-spikelet rachis node; true membranous ligule at <1mm; fresh glumes and lemma measured with scale; rooted Hays specimen and arrows"}
 p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+"\n")
pathlib.Path("reports/lane5-hordeum-pusillum-photo-archive-20261023.json").write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps(out))
