#!/usr/bin/env python3
"""Archive two license-checked macro photographs for rye, rate-limit aware."""
import io,json,pathlib,time,urllib.request,urllib.parse,urllib.error,hashlib,html,re
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Secale/secale-cereale");p=base/"species.json";d=json.loads(p.read_text());assert d["id"]=="secale-cereale"
files=["Secale cereale (3873574298).jpg","Secale cereale (3872788475).jpg"]
holds=[]
def get(url):
 for n in range(5):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotany/1.0 (educational photo archive)"}),timeout=65) as r:return r.read()
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or n==4:raise
   time.sleep(25*(n+1))
for fn in files:
 try:
  title="File:"+fn
  api="https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url%7Cextmetadata&format=json&titles="+urllib.parse.quote(title)
  info=next(iter(json.loads(get(api))["query"]["pages"].values()))["imageinfo"][0]
  md=info["extmetadata"];lic=md.get("LicenseShortName",{}).get("value","").upper().replace(" ","").replace("-","")
  assert lic in ("CCBYSA2.0","CCBYSA3.0","CCBYSA4.0","CCBY2.0","CCBY3.0","CCBY4.0"),lic
  artist=html.unescape(re.sub("<[^>]*>","",md.get("Artist",{}).get("value",""))).strip()
  assert artist and "Matt Lavin" in artist,(fn,artist)
  raw=get(info["url"]);assert 12000<len(raw)<16000000
  img=Image.open(io.BytesIO(raw));img.verify();img=Image.open(io.BytesIO(raw)).convert("RGB")
  assert img.width>=500 and img.height>=500
  name="matt-lavin-"+hashlib.sha256(fn.encode()).hexdigest()[:10]+".jpg"
  dest=base/"images"/name;dest.parent.mkdir(parents=True,exist_ok=True);img.save(dest,"JPEG",quality=91,optimize=True)
  page="https://commons.wikimedia.org/wiki/"+urllib.parse.quote(title.replace(" ","_"))
  record={"file":"images/"+name,"role":"Individual rye spikelets: small pair of glumes and two large florets; source-labelled anatomy, local review pending","creator":"Matt Lavin","license":md["LicenseShortName"]["value"],"source_page":page,"public_reuse":"Credit creator and obey stated Commons license including ShareAlike","photo_status":"PROVISIONAL anatomy photo; arrows not yet added"}
  if not any(z.get("file")==record["file"] or z.get("source_page")==page for z in d["images"]):d["images"].append(record)
  print("ARCHIVED",fn)
 except Exception as err:
  holds.append({"file":fn,"error":str(err)});print("HELD",fn,str(err))
d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
d.setdefault("curation_status",{})["photo_metadata_count"]=len(d["images"])
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n")
rp=pathlib.Path("reports/secale-cereale-anatomy-archive.json");rp.parent.mkdir(exist_ok=True);rp.write_text(json.dumps({"holds":holds,"gallery_entries":len(d["images"])},indent=2)+"\n")
