#!/usr/bin/env python3
"""Archive exact taxon source-checked Dichanthelium commutatum photos."""
import io,json,time,pathlib,urllib.parse,urllib.request,urllib.error,re,html
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Dichanthelium/dichanthelium-commutatum")
p=base/"species.json"; d=json.loads(p.read_text()); assert d["id"]=="dichanthelium-commutatum"
candidates=["Dichanthelium commutatum 1120320.jpg","Dichanthelium commutatum 259295916.jpg"]
holds=[]
def get(url):
 for n in range(4):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Hays-County-Botany/1.0 (educational botanical photo archive)"}),timeout=60) as x:return x.read()
  except urllib.error.HTTPError as e:
   if e.code not in (429,503) or n==3:raise
   time.sleep(25*(n+1))
for i,fn in enumerate(candidates):
 try:
  title="File:"+fn
  api="https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url%7Cextmetadata&format=json&titles="+urllib.parse.quote(title)
  info=next(iter(json.loads(get(api))["query"]["pages"].values()))["imageinfo"][0]
  meta=info["extmetadata"]; license=meta.get("LicenseShortName",{}).get("value","").upper().replace("-","").replace(" ","")
  assert license in ("CC0","CCBY2.0","CCBY3.0","CCBY3.0US","CCBY4.0","CCBYSA2.0","CCBYSA3.0","CCBYSA4.0","PUBLICDOMAIN"),license
  author=html.unescape(re.sub("<[^>]+>","",meta.get("Artist",{}).get("value",""))).strip()
  assert author
  raw=get(info["url"]); assert 12000<len(raw)<15000000
  im=Image.open(io.BytesIO(raw));im.verify();im=Image.open(io.BytesIO(raw)).convert("RGB")
  assert im.width>=500 and im.height>=500
  name="commons-dichanthelium-commutatum-"+str(i+1)+"-archive.jpg"
  dest=base/"images"/name; dest.parent.mkdir(parents=True,exist_ok=True);im.save(dest,"JPEG",quality=91,optimize=True)
  page="https://commons.wikimedia.org/wiki/"+urllib.parse.quote(title.replace(" ","_"))
  if not any(x.get("file")=="images/"+name or x.get("source_page")==page for x in d["images"]):
   d["images"].append({"file":"images/"+name,"role":"Additional exact-taxon photograph, pending confirmation of useful whole-plant or flowering structures","creator":author,"license":meta["LicenseShortName"]["value"],"source_page":page,"photo_status":"PROVISIONAL — USER PHOTO REVIEW PENDING; no unverified anatomical arrows","public_reuse":"Commons file-specific reuse rights checked"})
  print("ARCHIVED",fn)
 except Exception as err:
  holds.append({"file":fn,"reason":str(err)}); print("HELD",fn,str(err))
d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
d.setdefault("curation_status",{})["photo_metadata_count"]=len(d["images"])
d["curation_status"]["photo_files_present"]=sum(str(x.get("file","")).startswith("images/") for x in d["images"])
p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
report=pathlib.Path("reports/dichanthelium-commutatum-photo-archive.json");report.parent.mkdir(exist_ok=True);report.write_text(json.dumps({"holds":holds,"photos":len(d["images"])},indent=2)+"\n")
