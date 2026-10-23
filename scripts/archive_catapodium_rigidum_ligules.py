#!/usr/bin/env python3
"""Archive Catapodium rigidum collar photographs with source license and rate-limit gates."""
import io,json,pathlib,time,urllib.request,urllib.parse,urllib.error,html,re
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Catapodium/catapodium-rigidum");p=base/"species.json";d=json.loads(p.read_text());assert d["id"]=="catapodium-rigidum"
candidates=[("Catapodium rigidum sl15.jpg","Source-category ligule image, leaf-collar macro"),("Catapodium rigidum sl16.jpg","Second source-category ligule image, collar and membranous ligule")]
holds=[]
def get(url):
 for n in range(5):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Hays-County-Botany/1.0 (educational botanical image archive)"}),timeout=65) as resp:return resp.read()
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or n==4:raise
   time.sleep(25*(n+1))
for i,(filename,role) in enumerate(candidates):
 try:
  title="File:"+filename
  api="https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url%7Cextmetadata&format=json&titles="+urllib.parse.quote(title)
  info=next(iter(json.loads(get(api))["query"]["pages"].values()))["imageinfo"][0]
  md=info["extmetadata"];lic=md.get("LicenseShortName",{}).get("value","").upper().replace("-","").replace(" ","")
  assert lic in ("CC0","CCBY2.0","CCBY3.0","CCBY3.0US","CCBY4.0","CCBYSA2.0","CCBYSA3.0","CCBYSA4.0","PUBLICDOMAIN"),lic
  artist=html.unescape(re.sub("<[^>]+>","",md.get("Artist",{}).get("value",""))).strip()
  assert artist,"Missing author credit"
  raw=get(info["url"]);assert 12000<len(raw)<17000000
  im=Image.open(io.BytesIO(raw));im.verify();im=Image.open(io.BytesIO(raw)).convert("RGB")
  assert im.width>=500 and im.height>=500
  out=base/"images"/("commons-catapodium-ligule-"+str(i+1)+".jpg");out.parent.mkdir(exist_ok=True,parents=True);im.save(out,"JPEG",quality=91,optimize=True)
  page="https://commons.wikimedia.org/wiki/"+urllib.parse.quote(title.replace(" ","_"))
  entry={"file":"images/"+out.name,"role":role,"creator":artist,"license":md["LicenseShortName"]["value"],"source_page":page,"photo_status":"PROVISIONAL — source-indexed ligule, actual arrow placement pending review","public_reuse":"Individual Commons license checked; attribution and SA preserved"}
  if not any(z.get("file")==entry["file"] or z.get("source_page")==page for z in d["images"]):d["images"].append(entry)
  print("ARCHIVED",filename)
 except Exception as e:holds.append({"file":filename,"error":str(e)});print("HELD",filename,str(e))
d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"]);d.setdefault("curation_status",{})["photo_metadata_count"]=len(d["images"])
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n")
rp=pathlib.Path("reports/catapodium-rigidum-ligule-archive.json");rp.parent.mkdir(exist_ok=True);rp.write_text(json.dumps({"holds":holds,"gallery_count":len(d["images"])},indent=2)+"\n")
