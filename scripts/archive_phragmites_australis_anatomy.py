#!/usr/bin/env python3
"""Archive exact-species Phragmites anatomy; do not infer native/introduced lineage."""
import io,json,pathlib,urllib.request,urllib.error,urllib.parse,time
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Phragmites/phragmites-australis")
p=base/"species.json";d=json.loads(p.read_text());assert d["id"]=="phragmites-australis"
items=[("Phragmites australis ligule1 (8253945012).jpg","Photographed hair-fringed ligule and collar region","harry-rose-ligule-8253945012.jpg"),("Phragmites australis spikelet1 annotated (6966477736).jpg","Annotated reproductive spikelet and flower structures","harry-rose-spikelet-6966477736.jpg")]
holds=[]
def get(url):
 for i in range(5):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotany/1.0 (grass educational archive)"}),timeout=70) as f:return f.read()
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or i==4:raise
   time.sleep(25*(i+1))
for filename,role,local in items:
 try:
  title="File:"+filename
  api="https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url%7Cextmetadata&format=json&titles="+urllib.parse.quote(title)
  info=next(iter(json.loads(get(api))["query"]["pages"].values()))["imageinfo"][0]
  lic=info["extmetadata"]["LicenseShortName"]["value"].upper().replace("-","").replace(" ","")
  assert lic=="CCBY2.0",(filename,lic)
  raw=get(info["url"]);assert 12000<len(raw)<15000000
  im=Image.open(io.BytesIO(raw));im.verify();im=Image.open(io.BytesIO(raw)).convert("RGB");assert min(im.size)>600
  dst=base/"images"/local;dst.parent.mkdir(parents=True,exist_ok=True);im.save(dst,"JPEG",quality=91,optimize=True)
  source="https://commons.wikimedia.org/wiki/"+urllib.parse.quote(title.replace(" ","_"))
  entry={"file":"images/"+local,"role":role,"creator":"Harry Rose (Macleay Grass Man)","license":"CC BY 2.0","source_page":source,"public_reuse":"Attribution required; retain source's existing annotations","photo_status":"SOURCE-IDENTIFIED STRUCTURE; arrow review pending","lineage_caution":"No subspecies, native/introduced lineage, or genotype established by this photograph"}
  if not any(x.get("file")==entry["file"] or x.get("source_page")==source for x in d["images"]):d["images"].append(entry)
  print("ARCHIVED",filename)
 except Exception as e:holds.append({"file":filename,"reason":str(e)});print("HELD",filename,e)
d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
d.setdefault("curation_status",{})["photo_metadata_count"]=len(d["images"])
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n")
rp=pathlib.Path("reports/phragmites-australis-anatomy-archive.json");rp.parent.mkdir(exist_ok=True);rp.write_text(json.dumps({"holds":holds,"gallery_count":len(d["images"])},indent=2)+"\n")
