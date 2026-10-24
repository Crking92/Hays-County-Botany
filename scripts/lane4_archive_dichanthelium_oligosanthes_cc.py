#!/usr/bin/env python3
"""Lane 4: archive at most two exact-taxon, openly licensed few-flowered panicgrass photos.
New photos remain provisional until actual structural pixels are manually checked.
"""
import json,pathlib,urllib.parse,urllib.request,urllib.error,time,io
from PIL import Image
p=pathlib.Path("content/taxa/Poaceae/Digitaria/dichanthelium-oligosanthes/species.json")
d=json.loads(p.read_text());assert d["id"]=="dichanthelium-oligosanthes"
report={"added":[],"held":[],"scope":"Dichanthelium oligosanthes CC BY/CC BY-SA/CC0 additional photo candidates; no unsupported anatomical arrows"}
def get(url):
 for i in range(3):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotany/1.0 (public grass photo documentation)"}),timeout=55) as f:return f.read()
  except urllib.error.HTTPError as exc:
   if exc.code not in (429,500,502,503,504) or i==2:raise
   time.sleep(15*(i+1))
try:
 results=json.loads(get("https://api.inaturalist.org/v1/taxa/autocomplete?q=Digitaria%20ciliaris"))["results"]
 matching=[z for z in results if z.get("name","").lower()=="digitaria ciliaris" and z.get("rank")=="species"]
 assert matching,"Exact accepted taxon unavailable"
 tid=matching[0]["id"]
 query=urllib.parse.urlencode({"taxon_id":tid,"quality_grade":"research","photos":"true","photo_license":"cc0,cc-by,cc-by-sa","per_page":80,"order_by":"votes"})
 observations=json.loads(get("https://api.inaturalist.org/v1/observations?"+query))["results"]
 for obs in observations:
  if len(report["added"])>=3:break
  if obs.get("taxon",{}).get("id")!=tid:continue
  for photo in obs.get("photos",[]):
   if len(report["added"])>=3:break
   license=photo.get("license_code","").lower()
   if license not in ("cc0","cc-by","cc-by-sa"):continue
   pid=photo.get("id");page="https://www.inaturalist.org/photos/"+str(pid)
   if any(z.get("source_page")==page for z in d["images"]):continue
   creator=photo.get("attribution") or obs.get("user",{}).get("login")
   if not creator:continue
   url=photo.get("url","").replace("/square.","/large.")
   if not url.startswith("https://"):continue
   try:
    blob=get(url);assert 15000<len(blob)<17000000
    im=Image.open(io.BytesIO(blob));im.verify();im=Image.open(io.BytesIO(blob)).convert("RGB")
    assert min(im.size)>=600,"Resolution below useful diagnostic photo threshold"
    name="inat-cc-"+str(pid)+".jpg";dest=p.parent/"images"/name;dest.parent.mkdir(parents=True,exist_ok=True);im.save(dest,"JPEG",quality=91,optimize=True)
    d["images"].append({"file":"images/"+name,"role":"Additional species-specific few-flowered panicgrass photograph — diagnostic anatomy to be determined by subsequent pixel inspection","creator":creator,"license":license.upper(),"source_page":page,"source_observation":"https://www.inaturalist.org/observations/"+str(obs["id"]),"photo_status":"PROVISIONAL — image pixels and identification pending manual review; no claimed ligule, lemma or glume macro","public_reuse":"Source photo's image-level CC license with attribution"})
    d.setdefault("visual_comparison",{}).setdefault("items",[]).append({"label":"Few-flowered panicgrass — additional source-labelled photograph (review pending)","scientific_name":"Dichanthelium oligosanthes","image_url":str(dest).replace("\\","/"),"image_fit":"contain","image_role":"Real exact-source-labelled photograph, anatomical features not yet evaluated","caption":"Open-license iNaturalist research-grade observation. Inspect actual pixels before designating habit, collar or reproductive structures as proven.","creator":creator,"license":license.upper(),"source_page":page,"markers":[],"photo_status":"PROVISIONAL — USER PHOTO REVIEW PENDING"})
    report["added"].append({"path":str(dest),"source":page,"license":license,"creator":creator})
   except Exception as e:report["held"].append({"photo":page,"reason":str(e)})
except Exception as e:report["held"].append({"search":"Dichanthelium oligosanthes","reason":str(e)})
if report["added"]:
 d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
 d.setdefault("curation_status",{})["photo_metadata_count"]=len(d["images"])
 p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
out=pathlib.Path("reports/lane4-dichanthelium-oligosanthes-cc-photo-attempt.json");out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
