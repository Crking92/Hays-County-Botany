#!/usr/bin/env python3
"""Lane 4: exact-photo rights-checked archive of Paspalum distichum creeping habit."""
import json,pathlib,urllib.request,urllib.parse,io
from PIL import Image
p=pathlib.Path("content/taxa/Poaceae/Paspalum/paspalum-distichum/species.json")
d=json.loads(p.read_text());assert d["id"]=="paspalum-distichum"
name="Paspalum distichum habit5 (8250226941).jpg"
report={"added":[],"held":[]}
try:
 q=urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":1400,"titles":"File:"+name})
 def get(url):
  req=urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotany Visual Learner/1.0 educational image repository"})
  with urllib.request.urlopen(req,timeout=60) as response:return response.read()
 result=json.loads(get("https://commons.wikimedia.org/w/api.php?"+q))
 info=next(iter(result["query"]["pages"].values()))["imageinfo"][0]
 license=info["extmetadata"]["LicenseShortName"]["value"]
 assert "".join(k for k in license.lower() if k.isalnum())=="ccby20",license
 blob=get(info.get("thumburl") or info["url"])
 pic=Image.open(io.BytesIO(blob));pic.verify()
 pic=Image.open(io.BytesIO(blob)).convert("RGB");assert min(pic.size)>600
 local="images/harry-rose-knotgrass-wetland-habit5.jpg";out=p.parent/local;out.parent.mkdir(parents=True,exist_ok=True)
 pic.save(out,"JPEG",quality=91,optimize=True)
 page="https://commons.wikimedia.org/wiki/File:"+urllib.parse.quote(name.replace(" ","_"),safe="()")
 if not any(x.get("file")==local for x in d["images"]):
  d["images"].append({"file":local,"role":"Wetland mat habit of true Paspalum distichum photographed in NSW; rooting nodes not independently pixel certified","creator":"Harry Rose (Macleay Grass Man)","license":"CC BY 2.0","license_url":"https://creativecommons.org/licenses/by/2.0/","source_page":page,"modifications":"Commons resized 1400px derivative and EXIF-stripped JPEG conversion","photo_status":"PHYSICALLY ARCHIVED; no arrows to unresolved root-node structures"})
 linked=0
 for panel in d.get("visual_comparison",{}).get("items",[]):
  if "8250226941" in panel.get("image_url",""):
   panel["image_url"]=str(out).replace("\\","/");panel["creator"]="Harry Rose";panel["license"]="CC BY 2.0";panel["source_page"]=page;linked+=1
 d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
 d.setdefault("field_id_finish_pass",{})["lane4_20261023"]={"stage":"FIELD_READY_PHOTO_GAPS","photo_added":1,"gallery_relinked":linked,"new_arrows":0,"confirmed_views":["two-raceme flowering V","source-labeled collar/ligule macro","source-labeled paired spikelet rows","wetland colony habit"],"critical_holds":["same-plant genuinely rooting stolon node at soil line with ruler","mature glume and sterile/fertile lemmas dissected with 1 mm scale","ligule membrane free edge measured and annotated after source-pixel review","matched Paspalum notatum actual rootstock and spikelets"],"public_pages":"NOT VERIFIED"}
 p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
 report["added"].append({"image":str(out),"source":page,"panels_relinked":linked,"dimensions":pic.size})
except Exception as e:report["held"].append({"source":name,"reason":str(e)})
rp=pathlib.Path("reports/lane4-paspalum-distichum-habit-archive.json");rp.parent.mkdir(exist_ok=True);rp.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
