import io,json,re,html,pathlib,urllib.parse,urllib.request,hashlib
from PIL import Image
p=pathlib.Path("content/taxa/Poaceae/Poa/poa-annua/species.json");s=json.loads(p.read_text());results=[]
def get(u):
 req=urllib.request.Request(u,headers={"User-Agent":"HaysBotany/1.0 Commons archival"})
 with urllib.request.urlopen(req,timeout=45) as f:return f.read()
for panel in s["visual_comparison"]["items"]:
 source=panel.get("source_page","")
 if source not in ["https://commons.wikimedia.org/wiki/File:Annual_Bluegrass_(1294505418).jpg","https://commons.wikimedia.org/wiki/File:Poa_annua_(subsp._annua)_sl11.jpg"]:continue
 try:
  name=urllib.parse.unquote(source.split("File:",1)[1]).replace("_"," ")
  url="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":"1600","titles":"File:"+name,"format":"json"})
  info=next(iter(json.loads(get(url))["query"]["pages"].values()))["imageinfo"][0];md=info["extmetadata"]
  lic=re.sub("[^A-Z0-9]","",md.get("LicenseShortName",{}).get("value","").upper())
  artist=html.unescape(re.sub("<[^>]*>","",md.get("Artist",{}).get("value","")))
  expected="CCBY20" if "Annual_Bluegrass_" in source else "CCBYSA40"
  author="Jason Hollinger" if "Annual_Bluegrass_" in source else "Stefan"
  if lic!=expected or author.lower() not in artist.lower():raise ValueError("rights/artist hold: "+lic+" "+artist)
  raw=get(info.get("thumburl") or info["url"]);im=Image.open(io.BytesIO(raw));im.verify();im=Image.open(io.BytesIO(raw)).convert("RGB")
  if min(im.size)<350:raise ValueError("insufficient pixels")
  dst=p.parent/"images"/("commons-poa-annua-"+hashlib.sha256(source.encode()).hexdigest()[:12]+".jpg");im.save(dst,"JPEG",quality=90,optimize=True)
  panel["previous_external_image_url"]=panel["image_url"];panel["image_url"]=str(dst);panel["photo_status"]="Source and image license verified; local JPEG archived, EXIF removed; previous gross arrows kept for site alignment QA."
  s["images"].append({"file":"images/"+dst.name,"role":panel["image_role"],"creator":panel["creator"],"license":panel["license"],"license_url":panel.get("license_url"),"source_page":source,"photo_status":"LOCAL ARCHIVE; microscopy not independently specimen vouched"})
  results.append({"source":source,"file":str(dst),"status":"archived"})
 except Exception as exc:results.append({"source":source,"status":"held","reason":str(exc)[:160]})
if any(x["status"]=="archived" for x in results):
 s["field_id_finish_pass"]["lane5_annua_commons_archive_20261023"]={"results":results,"status":"FIELD_READY_PHOTO_GAPS","remaining":"Local rooted crown and mature bisexual floret with proper magnification and scale; no unseen microscopic arrows"}
 p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+"\n")
pathlib.Path("reports/lane5-poa-annua-open-20261023.json").write_text(json.dumps(results,indent=2)+"\n")
print(json.dumps(results))
