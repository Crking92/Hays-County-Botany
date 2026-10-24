#!/usr/bin/env python3
"""Archive the exact CC0 seep muhly Commons photo, preserving wild-vs-garden warning."""
import pathlib,json,urllib.request,urllib.parse,io,hashlib
from PIL import Image,ImageOps
root=pathlib.Path("content/taxa/Poaceae/Muhlenbergia/muhlenbergia-reverchonii");p=root/"species.json";d=json.loads(p.read_text())
report={"added":[],"holds":[]}
name="Muhlenbergia reverchonii - Coastal Maine Botanical Gardens - DSC03134.jpg"
def get(url):
 req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyVisualLearner/1.0 (attributed botany learning; github.com/Crking92/Hays-County-Botany)"})
 with urllib.request.urlopen(req,timeout=40) as r:return r.read(16000001)
try:
 api="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo","iiprop":"url|extmetadata","titles":"File:"+name})
 info=next(iter(json.loads(get(api))["query"]["pages"].values()))["imageinfo"][0]
 license=info["extmetadata"].get("LicenseShortName",{}).get("value","")
 if "CC0" not in license and "Public domain" not in license:raise ValueError("no public-domain license: "+license)
 source="https://commons.wikimedia.org/wiki/File:"+name.replace(" ","_")
 match=next((z for z in d["images"] if z.get("source_page")==source),None)
 if match is None:raise ValueError("exact Commons source missing in canonical")
 raw=get(info["url"])
 with Image.open(io.BytesIO(raw)) as im:im.verify()
 with Image.open(io.BytesIO(raw)) as im:
  im=ImageOps.exif_transpose(im).convert("RGB")
  if min(im.size)<450:raise ValueError("source small")
  im.thumbnail((2000,2000));buf=io.BytesIO();im.save(buf,"JPEG",quality=88,optimize=True);blob=buf.getvalue()
 file="images/seep-muhly-maine-botanical-garden-cc0.jpg";dest=root/file
 if dest.exists():raise ValueError("already locally archived")
 dest.write_bytes(blob);match["file"]=file;match["original_media_url"]=info["url"];match["sha256"]=hashlib.sha256(blob).hexdigest()
 match["role"]="CC0 cultivated garden habit comparison, NOT evidence of local wild provenance or microscopic anatomy"
 d["visual_comparison"]["items"].append({"label":"Seep muhly — documented cultivated garden habit (not wild Texas evidence)","scientific_name":"Muhlenbergia reverchonii","image_url":str(dest),"image_fit":"contain","image_role":"Additional source-labelled CC0 plant-scale garden habit; no precise ligule/spikelet diagnosis","caption":"CC0 botanical garden reference from Coastal Maine. Use only for whole-plant recognition; the wild Texas flowering photographs remain the regional evidence.","creator":match.get("creator",""),"license":license,"source_page":source,"markers":[]})
 d["learner_visual_status"]["image_count"]=len(d["images"]);d["learner_visual_status"]["note"]="Six local source-credited photos (five wild, one separate CC0 cultivated garden habit) after archive; true measured ligule and dissected spikelet still missing.";d["curation_status"]["photo_files_present"]=sum(x.get("file","").startswith("images/") for x in d["images"])
 p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
 report["added"].append({"file":str(dest),"license":license,"sha256":hashlib.sha256(blob).hexdigest()})
except Exception as e:report["holds"].append(str(e)[:300])
pathlib.Path("reports/lane3-seep-muhly-commons-20261023.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
