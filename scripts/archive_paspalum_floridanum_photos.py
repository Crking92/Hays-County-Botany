#!/usr/bin/env python3
"""Conservative photo-only archive for one-photo Florida paspalum."""
import io,json,pathlib,urllib.parse,urllib.request,urllib.error,time
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Paspalum/paspalum-floridanum")
p=base/"species.json"; d=json.loads(p.read_text()); assert d["id"]=="paspalum-floridanum"
for filename in ["Paspalum floridanum 10zz.jpg","Paspalum floridanum 8zz.jpg"]:
 try:
  title="File:"+filename
  url="https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url%7Cextmetadata&format=json&titles="+urllib.parse.quote(title)
  def get(url):
   for i in range(4):
    try:
     with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"HaysBotanyPhotoArchive/1.0 (educational plant photo review)"}),timeout=60) as f:return f.read()
    except urllib.error.HTTPError as e:
     if e.code not in (429,503) or i==3:raise
     time.sleep(25*(i+1))
  pages=json.loads(get(url))["query"]["pages"]; info=next(iter(pages.values()))["imageinfo"][0]
  md=info["extmetadata"]; license=md.get("LicenseShortName",{}).get("value","").upper().replace("-","").replace(" ","")
  assert license in ("CC0","CCBY2.0","CCBY3.0","CCBY4.0","CCBYSA2.0","CCBYSA3.0","CCBYSA4.0","PUBLICDOMAIN"),license
  creator=md.get("Artist",{}).get("value","").strip()
  # Do not falsely infer authorship from Commons uploader
  assert creator, "missing recorded creator"
  raw=get(info["url"]);assert 10000<len(raw)<15000000
  image=Image.open(io.BytesIO(raw));image.verify(); image=Image.open(io.BytesIO(raw)).convert("RGB")
  assert image.width>=550 and image.height>=550
  name="commons-"+filename.replace(" ","-").lower()
  dest=base/"images"/name;dest.parent.mkdir(parents=True,exist_ok=True);image.save(dest,"JPEG",quality=91,optimize=True)
  page="https://commons.wikimedia.org/wiki/"+urllib.parse.quote(title.replace(" ","_"))
  if not any(x.get("source_page")==page for x in d["images"]):
   d["images"].append({"file":"images/"+name,"role":"Additional exact-source Florida paspalum photo; flowering and sheath detail require actual pixel review","creator":creator,"license":md["LicenseShortName"]["value"],"source_page":page,"public_reuse":"Image-level Commons rights verified; preserve attribution and ShareAlike if present","photo_status":"PROVISIONAL — USER PHOTO REVIEW PENDING; no unverified anatomy claims"})
  print("ARCHIVED",filename)
 except Exception as e: print("HELD",filename,str(e))
d.setdefault("curation_status",{})["photo_metadata_count"]=len(d["images"])
d["curation_status"]["photo_files_present"]=sum(str(x.get("file","")).startswith("images/") for x in d["images"])
d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n")
