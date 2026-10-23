#!/usr/bin/env python3
"""Archive licensed species-specific Setaria images without fabricating diagnostic labels."""
import pathlib,json,urllib.request,urllib.parse,urllib.error,time,io,re,html,hashlib
from PIL import Image
taxa=["setaria-reverchonii","setaria-scheelei"]
def get(url):
 for n in range(5):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotany/1.0 (educational image archive)"}),timeout=65) as f:return f.read()
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or n==4:raise
   time.sleep(25*(n+1))
def api(params):
 return json.loads(get("https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(params)))
report={}
for slug in taxa:
 base=pathlib.Path("content/taxa/Poaceae/Setaria")/slug;path=base/"species.json"
 d=json.loads(path.read_text());assert d["id"]==slug
 species=slug.replace("setaria-","");category="Category:Setaria "+species
 holds=[];added=[]
 try:
  cat=api({"action":"query","list":"categorymembers","cmtitle":category,"cmtype":"file","cmlimit":50,"format":"json"})
  titles=[x["title"] for x in cat.get("query",{}).get("categorymembers",[])]
  assert titles,"No exact taxon image files in Commons category"
  print("CANDIDATES",slug,len(titles),flush=True)
  for title in titles:
   if len(added)>=2:break
   try:
    item=api({"action":"query","prop":"imageinfo","iiprop":"url|extmetadata","titles":title,"format":"json"})
    entry=next(iter(item["query"]["pages"].values()))
    info=entry["imageinfo"][0];md=info["extmetadata"];license=md.get("LicenseShortName",{}).get("value","")
    normalized=license.upper().replace(" ","").replace("-","")
    if normalized not in ("CC0","PUBLICDOMAIN","CCBY2.0","CCBY3.0","CCBY3.0US","CCBY4.0","CCBYSA2.0","CCBYSA3.0","CCBYSA4.0"):continue
    artist=html.unescape(re.sub("<[^>]*>","",md.get("Artist",{}).get("value",""))).strip()
    if not artist:continue
    url=info["url"];raw=get(url);assert 10000<len(raw)<16000000
    img=Image.open(io.BytesIO(raw));img.verify();img=Image.open(io.BytesIO(raw)).convert("RGB")
    assert min(img.size)>=500
    filename="commons-"+hashlib.sha256(title.encode()).hexdigest()[:12]+".jpg"
    src="https://commons.wikimedia.org/wiki/"+urllib.parse.quote(title.replace(" ","_"))
    if any(x.get("source_page")==src or x.get("file")=="images/"+filename for x in d.get("images",[])):continue
    dest=base/"images"/filename;dest.parent.mkdir(parents=True,exist_ok=True);img.save(dest,"JPEG",quality=91,optimize=True)
    d.setdefault("images",[]).append({"file":"images/"+filename,"role":"Exact-species source photo, morphological structure and suitability require visual inspection","creator":artist,"license":license,"source_page":src,"photo_status":"PROVISIONAL — species and anatomical arrows require human photo verification","public_reuse":"Individual Commons file license checked; creator credit retained"})
    added.append(title);print("ADDED",slug,title)
   except Exception as exc: holds.append({"title":title,"reason":str(exc)})
 except Exception as exc:holds.append({"category":category,"reason":str(exc)})
 if added:
  d.setdefault("curation_status",{})["photo_metadata_count"]=len(d["images"])
  d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
  path.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
 report[slug]={"added":added,"holds":holds,"gallery_count":len(d.get("images",[]))}
out=pathlib.Path("reports/setaria-one-photo-batch-archive.json");out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(report,indent=2)+"\n")
