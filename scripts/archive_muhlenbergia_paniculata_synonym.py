#!/usr/bin/env python3
"""Archive photographed tumblegrass inflorescence under verified Schedonnardus synonym."""
import json,io,pathlib,urllib.request,urllib.error,urllib.parse,time
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Muhlenbergia/muhlenbergia-paniculata");p=base/"species.json";d=json.loads(p.read_text());assert d["id"]=="muhlenbergia-paniculata"
fn="Schedonnardus paniculatus (3884661542) (2).jpg"
holds=[]
def get(url):
 for i in range(5):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotany/1.0 (botanical educational photo archiver)"}),timeout=65) as r:return r.read()
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or i==4:raise
   time.sleep(25*(i+1))
try:
 title="File:"+fn
 api="https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url%7Cextmetadata&format=json&titles="+urllib.parse.quote(title)
 info=next(iter(json.loads(get(api))["query"]["pages"].values()))["imageinfo"][0]
 license=info["extmetadata"]["LicenseShortName"]["value"]
 assert license.upper().replace(" ","").replace("-","")=="CCBYSA2.0",license
 raw=get(info["url"]);assert 15000<len(raw)<20000000
 im=Image.open(io.BytesIO(raw));im.verify();im=Image.open(io.BytesIO(raw)).convert("RGB")
 assert min(im.size)>=500
 out=base/"images"/"matt-lavin-schedonnardus-paniculatus-inflorescence.jpg"
 out.parent.mkdir(parents=True,exist_ok=True);im.save(out,"JPEG",quality=91,optimize=True)
 record={"file":"images/"+out.name,"role":"Photographed long slender laterally arranged flowering branches; small appressed secund spikelets visible at source scale","creator":"Matt Lavin","license":"CC BY-SA 2.0","license_url":"https://creativecommons.org/licenses/by-sa/2.0/","source_page":"https://commons.wikimedia.org/wiki/"+urllib.parse.quote(title.replace(" ","_")),"source_taxon_name":"Schedonnardus paniculatus","taxonomic_basis":"USDA GRIN synonym of Muhlenbergia paniculata; https://npgsweb.ars-grin.gov/gringlobal/taxon/taxonomydetail?id=70635","photo_status":"SOURCE-LABELED, arrow placement and photographed spikelet anatomy not yet locally reviewed","public_reuse":"Credit Matt Lavin; derivative ShareAlike applies"}
 if not any(x.get("file")==record["file"] for x in d["images"]):d["images"].append(record)
 d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
 d.setdefault("curation_status",{})["photo_metadata_count"]=len(d["images"])
 p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
 print("ARCHIVED",out)
except Exception as e:holds.append(str(e));print("HELD",e)
rp=pathlib.Path("reports/muhlenbergia-paniculata-synonym-photo.json");rp.parent.mkdir(exist_ok=True);rp.write_text(json.dumps({"holds":holds,"gallery_count":len(d["images"])},indent=2)+"\n")
