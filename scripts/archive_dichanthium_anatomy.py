#!/usr/bin/env python3
"""Archive real Dichanthium anatomy photos after file-level Commons licensing."""
import pathlib,json,io,time,urllib.request,urllib.error,urllib.parse,html,re,hashlib
from PIL import Image
items=[
("annulatum","Dichanthium annulatum ligule1 (6955112994).jpg","Actual leaf-junction/ligule detail"),
("annulatum","Dichanthium annulatum spikelet pair3 (7101179421).jpg","Paired spikelets; sessile vs pedicelled units"),
("sericeum","Dichanthium sericeum leaf sheath5 NWS - Flickr - Macleay Grass Man.jpg","Leaf sheath close-up"),
("sericeum","Dichanthium sericeum node3 (14157759518).jpg","Node hairs, possible look-alike distinction")]
holds=[]
def load(url):
 for n in range(5):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotany/1.0 (public botanical learning image archive)"}),timeout=70) as r:return r.read()
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or n==4:raise
   time.sleep(25*(n+1))
for slug,fn,role in items:
 try:
  base=pathlib.Path("content/taxa/Poaceae/Dichanthium")/("dichanthium-"+slug)
  p=base/"species.json";d=json.loads(p.read_text());assert d["id"]=="dichanthium-"+slug
  title="File:"+fn
  api="https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url%7Cextmetadata&format=json&titles="+urllib.parse.quote(title)
  info=next(iter(json.loads(load(api))["query"]["pages"].values()))["imageinfo"][0]
  md=info["extmetadata"]; lic=md["LicenseShortName"]["value"].upper().replace(" ","").replace("-","")
  assert lic=="CCBY2.0",(fn,lic)
  author=html.unescape(re.sub("<[^>]*>","",md.get("Artist",{}).get("value",""))).strip()
  assert "Rose" in author or "Macleay" in author,(fn,author)
  b=load(info["url"]);assert 12000<len(b)<18000000
  im=Image.open(io.BytesIO(b));im.verify();im=Image.open(io.BytesIO(b)).convert("RGB")
  assert min(im.size)>=450
  name="harry-rose-"+hashlib.sha256(fn.encode()).hexdigest()[:12]+".jpg"
  dest=base/"images"/name;dest.parent.mkdir(parents=True,exist_ok=True);im.save(dest,"JPEG",quality=91,optimize=True)
  source="https://commons.wikimedia.org/wiki/"+urllib.parse.quote(title.replace(" ","_"))
  entry={"file":"images/"+name,"role":role,"creator":"Harry Rose (Macleay Grass Man)","license":"CC BY 2.0","license_url":"https://creativecommons.org/licenses/by/2.0/","source_page":source,"public_reuse":"Credit photographer, source and license; locally re-encoded JPEG","photo_status":"PROVISIONAL: photo anatomy/arrow coordinates await visual review"}
  if not any(x.get("file")==entry["file"] or x.get("source_page")==source for x in d.get("images",[])):d.setdefault("images",[]).append(entry)
  d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
  d.setdefault("curation_status",{})["photo_metadata_count"]=len(d["images"])
  p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
  print("ARCHIVED",slug,fn)
 except Exception as e:
  holds.append({"taxon":slug,"file":fn,"reason":str(e)});print("HELD",slug,fn,e)
report=pathlib.Path("reports/dichanthium-anatomy-archive.json");report.parent.mkdir(exist_ok=True);report.write_text(json.dumps({"holds":holds},indent=2)+"\n")
