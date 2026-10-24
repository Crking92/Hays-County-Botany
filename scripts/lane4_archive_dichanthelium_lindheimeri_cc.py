#!/usr/bin/env python3
"""Lane 4: conservative iNaturalist CC photo harvest for Dichanthelium lindheimeri."""
import json,pathlib,urllib.parse,urllib.request,urllib.error,time,io,hashlib
from PIL import Image
p=pathlib.Path("content/taxa/Poaceae/Dichanthelium/dichanthelium-lindheimeri/species.json")
card=json.loads(p.read_text());assert card["id"]=="dichanthelium-lindheimeri"
report={"added":[],"held":[],"removed_misattributed_files":[],"scope":"STRICT D. lindheimeri taxon source; no anatomy claims or arrows"}
# Clean photos accidentally downloaded by an older script whose API query was D. pedicellatum.
for mistaken_id in ("632023937","632024018"):
 mistaken_file=p.parent/"images"/("inat-cc-"+mistaken_id+".jpg")
 if mistaken_file.exists():
  mistaken_file.unlink()
  report["removed_misattributed_files"].append(str(mistaken_file))

def get(u):
 for n in range(3):
  try:
   with urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Hays Botany photo learner (contact via GitHub repository)"}),timeout=50) as r:return r.read()
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or n==2:raise
   time.sleep(12*(n+1))
try:
 taxa=json.loads(get("https://api.inaturalist.org/v1/taxa/autocomplete?q=Dichanthelium%20lindheimeri"))["results"]
 matching=[x for x in taxa if x.get("name","").lower()=="dichanthelium lindheimeri" and x.get("rank")=="species"]
 assert matching,"Exact scientific taxon unavailable"
 tid=matching[0]["id"]
 query=urllib.parse.urlencode({"taxon_id":tid,"quality_grade":"research","photos":"true","photo_license":"cc0,cc-by,cc-by-sa","per_page":100,"order":"desc","order_by":"votes"})
 obs=json.loads(get("https://api.inaturalist.org/v1/observations?"+query))["results"]
 for row in obs:
  if len(report["added"])>=2:break
  if row.get("taxon",{}).get("id")!=tid or row.get("taxon",{}).get("name","").lower()!="dichanthelium lindheimeri":continue
  for item in row.get("photos",[]):
   if len(report["added"])>=2:break
   lic=item.get("license_code","").lower()
   if lic not in ("cc0","cc-by","cc-by-sa"):continue
   orig=item.get("url","").replace("/square.","/large.")
   if not orig.startswith("https://"):continue
   pid=item.get("id");page="https://www.inaturalist.org/photos/"+str(pid)
   if any(x.get("source_page")==page for x in card["images"]):continue
   try:
    data=get(orig);assert 10000<len(data)<14000000
    im=Image.open(io.BytesIO(data));im.verify();im=Image.open(io.BytesIO(data)).convert("RGB")
    assert min(im.size)>=600
    name="inat-cc-"+str(pid)+".jpg";out=p.parent/"images"/name;out.parent.mkdir(exist_ok=True,parents=True)
    im.save(out,"JPEG",quality=90,optimize=True)
    creator=item.get("attribution") or row.get("user",{}).get("login")
    assert creator,"Missing photographer credit"
    card["images"].append({"file":"images/"+name,"role":"Additional independently source-labelled D. lindheimeri field photograph; anatomy not yet pixel-certified","creator":creator,"license":lic.upper(),"source_page":page,"source_observation":"https://www.inaturalist.org/observations/"+str(row["id"]),"photo_status":"PROVISIONAL — user review pending; no collar or spikelet measurements inferred","public_reuse":"Image-level iNaturalist CC license; photographer attribution required"})
    card.setdefault("visual_comparison",{}).setdefault("items",[]).append({"label":"Additional D. lindheimeri field photograph — provisional","scientific_name":"Dichanthelium lindheimeri","image_url":str(out).replace("\\","/"),"image_fit":"contain","image_role":"Species-specific source-labelled reference; photograph's actual organ-level diagnostic content requires review","caption":"Research-grade observation source, open photo license. Compare to original species photo. Do not infer the tiny ligule, size of spikelet or identification solely from an unscaled view.","creator":creator,"license":lic.upper(),"source_page":page,"markers":[],"photo_status":"PROVISIONAL — USER PHOTO REVIEW PENDING"})
    report["added"].append({"file":str(out),"source":page,"license":lic})
   except Exception as e:report["held"].append({"photo":page,"reason":str(e)})
except Exception as e:report["held"].append({"search":"Dichanthelium lindheimeri","reason":str(e)})
if report["added"]:
 card.setdefault("learner_visual_status",{})["image_count"]=len(card["images"])
 card.setdefault("curation_status",{})["photo_metadata_count"]=len(card["images"])
 p.write_text(json.dumps(card,indent=2,ensure_ascii=False)+"\n")
r=pathlib.Path("reports/lane4-dichanthelium-lindheimeri-cc-photo-attempt.json")
r.parent.mkdir(exist_ok=True);r.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
