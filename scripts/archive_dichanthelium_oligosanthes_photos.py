#!/usr/bin/env python3
"""Archive verified licensed rosette grass spikelets; never guess photo ownership."""
import io,json,pathlib,time,urllib.request,urllib.parse,urllib.error,re,html
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Dichanthelium/dichanthelium-oligosanthes")
p=base/"species.json";d=json.loads(p.read_text());assert d["id"]=="dichanthelium-oligosanthes"
candidates=[("Dichanthelium oligosanthes spikelets.JPG","True spikelets close-up; morphology awaits human pixel review"),("Dichanthelium oligosanthes (as Panicum scribnerianum) HC-1950.png","Historical botanical illustration of flowering and vegetative structures; not a photograph")]
holds=[]
def get(url):
 for i in range(4):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Hays-County-Botany/1.0 (botanical education, attribution archived)"}),timeout=60) as f:return f.read()
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or i==3:raise
   time.sleep(25*(i+1))
for index,(filename,role) in enumerate(candidates):
 try:
  title="File:"+filename
  api="https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url%7Cextmetadata&format=json&titles="+urllib.parse.quote(title)
  q=next(iter(json.loads(get(api))["query"]["pages"].values()))
  info=q["imageinfo"][0];meta=info.get("extmetadata",{})
  license=meta.get("LicenseShortName",{}).get("value","").upper().replace("-","").replace(" ","")
  assert license in ("CC0","CCBY2.0","CCBY3.0","CCBY3.0US","CCBY4.0","CCBYSA2.0","CCBYSA3.0","CCBYSA4.0","PUBLICDOMAIN"),(filename,license)
  author=html.unescape(re.sub("<[^>]+>","",meta.get("Artist",{}).get("value",""))).strip()
  if not author and license=="PUBLICDOMAIN":author="Historical source; attribution details on Commons file page"
  assert author,"No author credit found"
  raw=get(info["url"]);assert len(raw)>8000 and len(raw)<25000000
  im=Image.open(io.BytesIO(raw));im.verify();im=Image.open(io.BytesIO(raw)).convert("RGB")
  assert im.width>=400 and im.height>=400
  destname="commons-oligosanthes-"+str(index+1)+".jpg"
  dest=base/"images"/destname;dest.parent.mkdir(parents=True,exist_ok=True);im.save(dest,"JPEG",quality=92,optimize=True)
  page="https://commons.wikimedia.org/wiki/"+urllib.parse.quote(title.replace(" ","_"))
  entry={"file":"images/"+destname,"role":role,"creator":author,"license":meta["LicenseShortName"]["value"],"source_page":page,"public_reuse":"Image-level Commons license confirmed; preserve attribution and share-alike","photo_status":"PROVISIONAL — photo anatomy and arrow placement not yet visually certified"}
  if not any(x.get("file")==entry["file"] or x.get("source_page")==page for x in d["images"]):d["images"].append(entry)
  print("ARCHIVED",filename)
 except Exception as e:
  holds.append({"file":filename,"reason":str(e)});print("HELD",filename,str(e))
d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
d.setdefault("curation_status",{})["photo_metadata_count"]=len(d["images"])
d["curation_status"]["photo_files_present"]=sum(str(x.get("file","")).startswith("images/") for x in d["images"])
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n")
rp=pathlib.Path("reports/dichanthelium-oligosanthes-photo-archive.json");rp.parent.mkdir(exist_ok=True);rp.write_text(json.dumps({"holds":holds,"gallery_entries":len(d["images"])},indent=2)+"\n")
