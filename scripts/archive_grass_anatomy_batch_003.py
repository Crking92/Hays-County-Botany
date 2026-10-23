#!/usr/bin/env python3
"""Strict source-reviewed anatomy archive; one failure does not stop remaining taxa."""
import json,urllib.parse,urllib.request,io,pathlib,hashlib
from PIL import Image
items=[{"genus":"Poa","id":"poa-annua","file":"Poa annua spikelet6 (8038355821).jpg","creator":"Harry Rose","license":"CC BY 2.0","role":"Close photographed spikelet with florets and visible anthers"},{"genus":"Poa","id":"poa-annua","file":"Poa annua spikelet9 (8038350836).jpg","creator":"Harry Rose","license":"CC BY 2.0","role":"Floret detail showing actual palea"},{"genus":"Hordeum","id":"hordeum-pusillum","file":"Hordeum pusillum (6180951213).jpg","creator":"Matt Lavin","license":"CC BY-SA 2.0","role":"True central and lateral spikelets; glumes and floret structure"},{"genus":"Festuca","id":"festuca-octoflora","file":"Vulpia octoflora (6243569951).jpg","creator":"Matt Lavin","license":"CC BY-SA 2.0","role":"Closely spaced lemmas and shorter awns, taxon labeled Vulpia octoflora"},{"genus":"Festuca","id":"festuca-octoflora","file":"Vulpia octoflora (6243565745).jpg","creator":"Matt Lavin","license":"CC BY-SA 2.0","role":"One-sided inflorescence and actual projecting lemma awns"}]
errors=[]
for it in items:
 try:
  base=pathlib.Path("content/taxa/Poaceae")/it["genus"]/it["id"]
  p=base/"species.json";d=json.loads(p.read_text());assert d["id"]==it["id"]
  title="File:"+it["file"]
  url="https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url%7Cextmetadata&format=json&titles="+urllib.parse.quote(title)
  req=urllib.request.Request(url,headers={"User-Agent":"Hays-County-Botany/1.0 (botanical educational archive)"})
  with urllib.request.urlopen(req,timeout=50) as response: pages=json.load(response)["query"]["pages"]
  info=next(iter(pages.values()))["imageinfo"][0]
  actual=info.get("extmetadata",{}).get("LicenseShortName",{}).get("value","").upper().replace("-","").replace(" ","")
  expected=it["license"].upper().replace("-","").replace(" ","")
  assert expected in actual,(title,actual,expected)
  with urllib.request.urlopen(urllib.request.Request(info["url"],headers={"User-Agent":"Hays-County-Botany/1.0"}),timeout=70) as response: raw=response.read()
  assert 12000<len(raw)<19000000
  im=Image.open(io.BytesIO(raw));im.verify(); im=Image.open(io.BytesIO(raw)).convert("RGB")
  assert im.width>=350 and im.height>=350
  name="commons-"+hashlib.sha256(it["file"].encode()).hexdigest()[:12]+".jpg"
  dest=base/"images"/name;dest.parent.mkdir(parents=True,exist_ok=True)
  im.save(dest,"JPEG",quality=91,optimize=True)
  page="https://commons.wikimedia.org/wiki/"+urllib.parse.quote(title.replace(" ","_"))
  entry={"file":"images/"+name,"role":it["role"],"creator":it["creator"],"license":it["license"],"source_page":page,"public_reuse":"Source checked at image-level; attribution and share alike as applicable","photo_status":"PROVISIONAL — USER PHOTO REVIEW PENDING"}
  if not any(x.get("file")==entry["file"] or x.get("source_page")==page for x in d.get("images",[])): d.setdefault("images",[]).append(entry)
  d.setdefault("curation_status",{})["photo_metadata_count"]=len(d["images"])
  d["curation_status"]["photo_files_present"]=sum(str(x.get("file","")).startswith("images/") for x in d["images"])
  d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
  p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n")
  print("ARCHIVED",it["id"],name)
 except Exception as e:
  errors.append({"species":it["id"],"filename":it["file"],"error":str(e)})
  print("HELD",it["id"],str(e))
pathlib.Path("reports/grass-anatomy-archive-003-result.json").write_text(json.dumps({"holds":errors},indent=2)+"\n")
