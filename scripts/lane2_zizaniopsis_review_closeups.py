#!/usr/bin/env python3
import json,io,pathlib,hashlib,urllib.request,urllib.parse
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Zizaniopsis/zizaniopsis-miliacea");p=base/"species.json"
j=json.loads(p.read_text());assert j["id"]=="zizaniopsis-miliacea"
report={"taxon":j["id"],"results":[]}
def get(url):
 with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotany/1.0 grass photo-rights verifier"}),timeout=75) as r:return r.read()
for num in [264449047,264449079]:
 title=f"File:Zizaniopsis miliacea {num}.jpg";src=f"https://commons.wikimedia.org/wiki/File:Zizaniopsis_miliacea_{num}.jpg"
 result={"source":src,"status":"HOLD"}
 try:
  api="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","prop":"imageinfo","iiprop":"url|extmetadata","titles":title,"format":"json"})
  inf=next(iter(json.loads(get(api))["query"]["pages"].values()))["imageinfo"][0]
  lic=inf["extmetadata"]["LicenseShortName"]["value"];assert "CC BY 4.0" in lic,lic
  artist=inf["extmetadata"].get("Artist",{}).get("value","")
  assert "Abair" in artist,artist
  raw=get(inf["url"]);assert 20000<len(raw)<7000000
  im=Image.open(io.BytesIO(raw));im.verify();im=Image.open(io.BytesIO(raw)).convert("RGB");assert min(im.size)>800
  dest=base/f"images/giant-cutgrass-alex-abair-review-{num}.jpg";im.save(dest,quality=93,optimize=True)
  if not any(x.get("source_page")==src for x in j["images"]):
   j["images"].append({"file":"images/"+dest.name,"role":"New verified-license source-labelled exact species photograph: organ-level anatomical review pending","creator":"Alex Abair","license":"CC BY 4.0","license_url":"https://creativecommons.org/licenses/by/4.0/","source_page":src,"source_observation":"https://www.inaturalist.org/observations/153134793","public_reuse":"CC BY 4.0 with attribution and modification disclosure","modifications":"RGB JPEG re-encode; stripped EXIF/GPS","photo_review":"Original Commons license and creator confirmed; pixel anatomy NOT YET REVIEWED, no arrows; Florida source NOT Hays County"})
  result.update(status="ARCHIVED_REVIEW_PENDING",path=str(dest),dimensions=list(im.size),sha256=hashlib.sha256(dest.read_bytes()).hexdigest())
 except Exception as e:result["error"]=str(e)
 report["results"].append(result)
j["field_id_finish_pass"]["lane2_close_detail_20261023"]={"additional_local_review_photo_count":sum(x["status"]=="ARCHIVED_REVIEW_PENDING" for x in report["results"]),"gallery": "HOLD new uninspected photos out of teaching panels until pixel-level organ review","ligule":"MISSING measured opened membrane","sex_spikelets":"MISSING anther/stigma-confirmed same-branch views","arrows_added":0,"public_site":"NOT VERIFIED"}
p.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n")
q=pathlib.Path("reports/lane2-zizaniopsis-close-detail-photo-review-20261023.json");q.parent.mkdir(parents=True,exist_ok=True);q.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
