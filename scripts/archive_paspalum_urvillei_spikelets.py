#!/usr/bin/env python3
"""Archive two exact-species, distinct anatomical photos for Paspalum urvillei."""
import io,json,time,pathlib,urllib.request,urllib.error,urllib.parse
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Paspalum/paspalum-urvillei")
p=base/"species.json";d=json.loads(p.read_text());assert d["id"]=="paspalum-urvillei"
photos=[("Paspalum urvillei spikelet3 annotated (7391787304).jpg","Annotated macro showing upper glume, sterile lemma and spikelet hairs","harry-rose-spikelet-annotated.jpg"),("Paspalum urvillei spikelets1 (7391789558).jpg","Attached spikelets on flowering branch, comparison with individual isolated spikelet","harry-rose-spikelets-attached.jpg")]
def get(req):
 for i in range(5):
  try:
   with urllib.request.urlopen(req,timeout=65) as f:return f.read()
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or i==4:raise
   time.sleep(25*(i+1))
for filename,role,name in photos:
 try:
  title="File:"+filename
  url="https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url%7Cextmetadata&format=json&titles="+urllib.parse.quote(title)
  obj=next(iter(json.loads(get(urllib.request.Request(url,headers={"User-Agent":"Hays-County-Botany/1.0 (educational botanical photo archive)"})))["query"]["pages"].values()))
  info=obj["imageinfo"][0]
  license=info["extmetadata"]["LicenseShortName"]["value"].upper().replace("-","").replace(" ","")
  assert "CCBY2.0" in license,(filename,license)
  b=get(urllib.request.Request(info["url"],headers={"User-Agent":"Hays-County-Botany/1.0"}))
  assert 12000<len(b)<18000000
  im=Image.open(io.BytesIO(b));im.verify();im=Image.open(io.BytesIO(b)).convert("RGB")
  assert im.width>=500 and im.height>=500
  dest=base/"images"/name;dest.parent.mkdir(parents=True,exist_ok=True);im.save(dest,"JPEG",quality=92,optimize=True)
  record={"file":"images/"+name,"role":role,"creator":"Harry Rose","license":"CC BY 2.0","license_url":"https://creativecommons.org/licenses/by/2.0/","source_page":"https://commons.wikimedia.org/wiki/"+urllib.parse.quote(title.replace(" ","_")),"public_reuse":"Creator, source, license required","photo_status":"PROVISIONAL — USER PHOTO REVIEW PENDING; existing source annotation is not a locally verified added arrow"}
  if not any(x.get("file")==record["file"] for x in d["images"]):d["images"].append(record)
  print("ARCHIVED",filename)
 except Exception as e:print("HELD",filename,str(e))
d.setdefault("curation_status",{})["photo_metadata_count"]=len(d["images"])
d["curation_status"]["photo_files_present"]=sum(str(x.get("file","")).startswith("images/") for x in d["images"])
d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n")
