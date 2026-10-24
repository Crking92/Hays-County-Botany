#!/usr/bin/env python3
import io,json,pathlib,urllib.parse,urllib.request,html,re,hashlib
from PIL import Image
p=pathlib.Path("content/taxa/Poaceae/Chloris/chloris-virgata/species.json")
s=json.loads(p.read_text())
names=["Chloris virgata spikelets young (6774152342).jpg","Chloris virgata spikelets4 (6923836344).jpg"]
def get(u):
 req=urllib.request.Request(u,headers={"User-Agent":"HaysBotany/1.0 (licensed botanical teaching archive)"})
 with urllib.request.urlopen(req,timeout=45) as r:return r.read()
results=[]
for name in names:
 source="https://commons.wikimedia.org/wiki/File:"+name.replace(" ","_")
 if any(x.get("source_page")==source for x in s["images"]):continue
 try:
  q=urllib.parse.urlencode({"action":"query","prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":"1600","titles":"File:"+name,"format":"json"})
  info=next(iter(json.loads(get("https://commons.wikimedia.org/w/api.php?"+q))["query"]["pages"].values()))["imageinfo"][0]
  md=info["extmetadata"];license=md.get("LicenseShortName",{}).get("value","")
  if re.sub(r"[^A-Z0-9]","",license.upper())!="CCBY20":raise ValueError("license mismatch "+license)
  artist=html.unescape(re.sub("<[^>]*>","",md.get("Artist",{}).get("value",""))).strip()
  if "Harry Rose" not in artist:raise ValueError("photographer unexpected "+artist)
  raw=get(info.get("thumburl") or info["url"]);image=Image.open(io.BytesIO(raw));image.verify()
  image=Image.open(io.BytesIO(raw)).convert("RGB")
  if min(image.size)<400:raise ValueError("photo below resolution threshold")
  out="commons-chloris-virgata-stage-"+hashlib.sha256(name.encode()).hexdigest()[:12]+".jpg"
  dest=p.parent/"images"/out;image.save(dest,"JPEG",quality=90,optimize=True)
  role="Young attached spikelets on species-labelled green raceme; no dissected floret and no ruler" if "young" in name else "Additional attached spikelet rows; no measured individual lemma or floret"
  s["images"].append({"file":"images/"+out,"role":role,"creator":"Harry Rose","license":"CC BY 2.0","license_url":"https://creativecommons.org/licenses/by/2.0/","source_page":source,"photo_status":"SOURCE-VERIFIED ARCHIVED; organ detail pending pixel review"})
  s["visual_comparison"]["items"].insert(4,{"label":"FEATHER FINGERGRASS — "+("young spikelets" if "young" in name else "additional spikelet rows"),"scientific_name":"Chloris virgata","image_url":str(dest),"image_fit":"contain","image_role":role,"caption":"Real species-labelled Harry Rose spikelet photograph. Compare maturity and arrangement; does not establish an isolated fertile lemma hair crown or sterile lemma identity.","why_it_matters":"Adds diagnostic reproductive-stage teaching without inventing fine-floret arrows.","creator":"Harry Rose","license":"CC BY 2.0","source_page":source,"markers":[],"photo_status":"ARCHIVED; anatomical pixel/scale QA pending"})
  results.append({"source":source,"status":"archived","path":str(dest)})
 except Exception as ex:results.append({"source":source,"status":"held","reason":str(ex)[:220]})
if any(x["status"]=="archived" for x in results):
 s.setdefault("field_id_finish_pass",{})["lane5_spikelet_stages_20261023"]={"results":results,"stage":"FIELD_READY_PHOTO_GAPS","remaining":"Measured mature separated fertile lemma hair crown and sterile lemma; real ligule with 1mm scale; specimen and live Pages QA"}
 p.write_text(json.dumps(s,indent=2,ensure_ascii=False)+"\n")
pathlib.Path("reports/lane5-chloris-virgata-spikelet-archive-20261023.json").write_text(json.dumps(results,indent=2)+"\n")
print(json.dumps(results))
