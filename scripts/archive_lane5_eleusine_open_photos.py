#!/usr/bin/env python3
"""Archive three independently checked Commons goosegrass photographs."""
import io,json,pathlib,re,html,urllib.parse,urllib.request,hashlib
from PIL import Image
p=pathlib.Path("content/taxa/Poaceae/Eleusine/eleusine-indica/species.json")
s=json.loads(p.read_text());out=[]
wanted={"https://commons.wikimedia.org/wiki/File:Eleusine_indica_plant1_(7120802953).jpg","https://commons.wikimedia.org/wiki/File:Eleusine_indica_ligule2_(7120807323).jpg","https://commons.wikimedia.org/wiki/File:Eleusine_indica_spikelet2_annotated_(6974711762).jpg"}
def get(u):
 req=urllib.request.Request(u,headers={"User-Agent":"HaysBotany/1.0 open-license botanical photo archive"})
 with urllib.request.urlopen(req,timeout=45) as r:return r.read()
for panel in s["visual_comparison"]["items"]:
 source=panel.get("source_page","")
 if source not in wanted or panel.get("image_url","").startswith("content/"):continue
 try:
  name=urllib.parse.unquote(source.split("File:",1)[1]).replace("_"," ")
  q=urllib.parse.urlencode({"action":"query","prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":"1600","titles":"File:"+name,"format":"json"})
  info=next(iter(json.loads(get("https://commons.wikimedia.org/w/api.php?"+q))["query"]["pages"].values()))["imageinfo"][0]
  meta=info["extmetadata"];license=re.sub("[^A-Z0-9]","",meta.get("LicenseShortName",{}).get("value","").upper())
  artist=html.unescape(re.sub("<[^>]+>","",meta.get("Artist",{}).get("value",""))).strip()
  if license!="CCBY20" or "Harry Rose" not in artist:raise ValueError("Rights/creator not approved "+license+" / "+artist)
  raw=get(info.get("thumburl") or info["url"]);im=Image.open(io.BytesIO(raw));im.verify()
  im=Image.open(io.BytesIO(raw)).convert("RGB")
  if min(im.size)<300:raise ValueError("Image too small")
  filename="commons-goosegrass-"+hashlib.sha256(source.encode()).hexdigest()[:12]+".jpg"
  dest=p.parent/"images"/filename;im.save(dest,"JPEG",quality=90,optimize=True)
  panel["original_external_image_url"]=panel["image_url"];panel["image_url"]=str(dest)
  panel["photo_status"]="Licensed Commons photograph physically archived; existing panel arrows retained where present. Fine anatomical membrane/glume arrows withheld pending native-pixel QA."
  role="Same-species plant habit" if "plant1" in source else "Actual collar/ligule-region photograph" if "ligule2" in source else "Source annotated true multi-flowered spikelet; independently verify each label"
  s["images"].append({"file":"images/"+filename,"role":role,"creator":"Harry Rose (Macleay Grass Man)","license":"CC BY 2.0","license_url":"https://creativecommons.org/licenses/by/2.0/","source_page":source,"photo_status":"RIGHTS CHECKED; local JPEG; fine anatomical review pending"})
  out.append({"source":source,"file":str(dest),"status":"archived"})
 except Exception as ex:out.append({"source":source,"status":"held","reason":str(ex)[:200]})
if any(z["status"]=="archived" for z in out):
 s["field_id_finish_pass"]["lane5_commons_open_20261023"]={"results":out,"status":"FIELD_READY_PHOTO_GAPS","remaining":"Validated real free ligule rim with 1mm scale; local specimen provenance and segmented florets with measured glumes; final mobile arrow QA"}
 p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+"\n")
pathlib.Path("reports/lane5-eleusine-indica-commons-20261023.json").write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps(out))
