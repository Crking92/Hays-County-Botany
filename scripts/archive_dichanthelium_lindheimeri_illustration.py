#!/usr/bin/env python3
"""Archive rights-checked illustration of the Lindheimer rosette-grass taxon."""
import io,json,pathlib,urllib.parse,urllib.request,urllib.error,time
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Dichanthelium/dichanthelium-lindheimeri");p=base/"species.json"
d=json.loads(p.read_text());assert d["id"]=="dichanthelium-lindheimeri"
name="Dichanthelium acuminatum var lindheimeri (as Panicum lindheimeri) HC-1950.png"
def fetch(url):
 for n in range(5):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotany/1.0 (public botanical education archive)"}),timeout=60) as r:return r.read()
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or n==4:raise
   time.sleep((n+1)*25)
holds=[]
try:
 title="File:"+name
 api="https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url%7Cextmetadata&format=json&titles="+urllib.parse.quote(title)
 info=next(iter(json.loads(fetch(api))["query"]["pages"].values()))["imageinfo"][0]
 md=info["extmetadata"];lic=md.get("LicenseShortName",{}).get("value","").upper().replace(" ","").replace("-","")
 assert lic in ("PUBLICDOMAIN","CC0"),"License held: "+lic
 raw=fetch(info["url"]); im=Image.open(io.BytesIO(raw));im.verify();im=Image.open(io.BytesIO(raw)).convert("RGB")
 assert im.width>700 and im.height>700
 out=base/"images"/"hitchcock-chase-lindheimeri-1950.jpg";out.parent.mkdir(parents=True,exist_ok=True);im.save(out,"JPEG",quality=93,optimize=True)
 record={"file":"images/"+out.name,"role":"Historical morphological illustration of Dichanthelium acuminatum var. lindheimeri (as Panicum lindheimeri), not a photograph; verify taxonomic concept against canonical D. lindheimeri before anatomical arrows","creator":"A. S. Hitchcock and A. Chase, Manual of the Grasses of the United States (1950)","license":md["LicenseShortName"]["value"],"source_page":"https://commons.wikimedia.org/wiki/"+urllib.parse.quote(title.replace(" ","_")),"photo_status":"REFERENCE ILLUSTRATION — taxonomic concept pending verification"}
 if not any(z.get("file")==record["file"] for z in d["images"]):d["images"].append(record)
 print("ARCHIVED",out)
except Exception as e:holds.append(str(e));print("HELD",e)
d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
d.setdefault("curation_status",{})["photo_metadata_count"]=len(d["images"])
p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
rp=pathlib.Path("reports/dichanthelium-lindheimeri-archive.json");rp.parent.mkdir(exist_ok=True);rp.write_text(json.dumps({"holds":holds,"images":len(d["images"])},indent=2)+"\n")
