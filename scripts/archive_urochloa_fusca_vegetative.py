#!/usr/bin/env python3
"""Add actual Urochloa fusca vegetative photo only with confirmed Commons license."""
import pathlib,json,urllib.parse,urllib.request,urllib.error,io,time,re,html
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Urochloa/urochloa-fusca");p=base/"species.json";d=json.loads(p.read_text());assert d["id"]=="urochloa-fusca"
fn="Vegetative Urochloa fusca.JPG";holds=[]
def get(url):
 for i in range(4):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotany/1.0 (grass education)"}),timeout=65) as r:return r.read()
  except urllib.error.HTTPError as e:
   if e.code not in (429,502,503,504) or i==3:raise
   time.sleep(25*(i+1))
try:
 title="File:"+fn
 api="https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url%7Cextmetadata&format=json&titles="+urllib.parse.quote(title)
 inf=next(iter(json.loads(get(api))["query"]["pages"].values()))["imageinfo"][0]
 meta=inf["extmetadata"];lic=meta["LicenseShortName"]["value"].upper().replace("-","").replace(" ","")
 assert lic in ("CC0","CCBY2.0","CCBY3.0","CCBY3.0US","CCBY4.0","CCBYSA2.0","CCBYSA3.0","CCBYSA4.0","PUBLICDOMAIN"),lic
 artist=html.unescape(re.sub("<[^>]+>","",meta.get("Artist",{}).get("value",""))).strip()
 assert artist and "Schnable" in artist,artist
 raw=get(inf["url"]);im=Image.open(io.BytesIO(raw));im.verify();im=Image.open(io.BytesIO(raw)).convert("RGB")
 assert im.width>800 and im.height>800
 out=base/"images"/"james-schnable-vegetative-urochloa-fusca.jpg";out.parent.mkdir(exist_ok=True,parents=True);im.save(out,"JPEG",quality=91,optimize=True)
 entry={"file":"images/"+out.name,"role":"Vegetative greenhouse-grown Urochloa fusca (LBJWC-52); no inflorescences; leaf/sheath habit reference, not spikelet anatomy","creator":"James Schnable","license":meta["LicenseShortName"]["value"],"source_page":"https://commons.wikimedia.org/wiki/File:Vegetative_Urochloa_fusca.JPG","photo_status":"PROVISIONAL — user visual review pending","public_reuse":"Attribution and applicable SA restrictions retained"}
 if not any(x.get("file")==entry["file"] for x in d["images"]):d["images"].append(entry)
 print("ARCHIVED",out)
except Exception as e:holds.append(str(e));print("HELD",str(e))
d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"]);d.setdefault("curation_status",{})["photo_metadata_count"]=len(d["images"])
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n")
rp=pathlib.Path("reports/urochloa-fusca-archive.json");rp.parent.mkdir(exist_ok=True);rp.write_text(json.dumps({"holds":holds,"gallery_count":len(d["images"])},indent=2)+"\n")
