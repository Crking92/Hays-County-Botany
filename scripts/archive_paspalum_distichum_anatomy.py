#!/usr/bin/env python3
"""Archive two source-licensed Paspalum distichum anatomical photographs."""
import io,json,pathlib,urllib.request,urllib.error,urllib.parse,hashlib,time
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Paspalum/paspalum-distichum")
p=base/"species.json"; d=json.loads(p.read_text());assert d["id"]=="paspalum-distichum"
for filename,role in [
 ("Paspalum distichum ligule1 (8251276202).jpg","True membranous ligule at the blade/sheath collar; source reports 0.5–1.5 mm"),
 ("Paspalum distichum spikelets1 (8250207803).jpg","Source-labelled close-up of two-rowed elliptic spikelets; use to distinguish actual spikelets from raceme branches")
]:
 try:
  title="File:"+filename
  url="https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url%7Cextmetadata&format=json&titles="+urllib.parse.quote(title)
  for attempt in range(5):
   try:
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Hays-County-Botany/1.0 (grass field education)"}),timeout=55) as response: pages=json.load(response)["query"]["pages"]
    break
   except urllib.error.HTTPError as e:
    if e.code!=429 or attempt==4: raise
    time.sleep(25*(attempt+1))
  info=next(iter(pages.values()))["imageinfo"][0]
  license=info.get("extmetadata",{}).get("LicenseShortName",{}).get("value","").upper().replace("-","").replace(" ","")
  assert "CCBY2.0" in license,(filename,license)
  for attempt in range(5):
   try:
    with urllib.request.urlopen(urllib.request.Request(info["url"],headers={"User-Agent":"Hays-County-Botany/1.0"}),timeout=70) as response: raw=response.read()
    break
   except urllib.error.HTTPError as e:
    if e.code!=429 or attempt==4: raise
    time.sleep(25*(attempt+1))
  image=Image.open(io.BytesIO(raw));image.verify()
  image=Image.open(io.BytesIO(raw)).convert("RGB")
  assert image.width>=300 and image.height>=300
  name="harry-rose-"+hashlib.sha256(filename.encode()).hexdigest()[:12]+".jpg"
  dest=base/"images"/name;dest.parent.mkdir(parents=True,exist_ok=True)
  image.save(dest,"JPEG",quality=91,optimize=True)
  page="https://commons.wikimedia.org/wiki/"+urllib.parse.quote(title.replace(" ","_"))
  record={"file":"images/"+name,"role":role,"creator":"Harry Rose","license":"CC BY 2.0","license_url":"https://creativecommons.org/licenses/by/2.0/","source_page":page,"public_reuse":"Attribution required","photo_status":"PROVISIONAL — USER PHOTO REVIEW PENDING; source-identified anatomy, no new unverified arrows"}
  if not any(x.get("file")==record["file"] or x.get("source_page")==record["source_page"] for x in d.get("images",[])):d["images"].append(record)
  print("ARCHIVED",filename)
 except Exception as e: print("HELD",filename,repr(e))
d.setdefault("curation_status",{})["photo_metadata_count"]=len(d["images"])
d["curation_status"]["photo_files_present"]=sum(str(x.get("file","")).startswith("images/") for x in d["images"])
d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n")
