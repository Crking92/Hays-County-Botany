#!/usr/bin/env python3
"""Small one-shot Ophthalmica source scout. REVIEW candidates before any canonical promotion."""
import io,json,hashlib,time
from pathlib import Path
import requests
from PIL import Image,ImageOps

BASE=Path("photo-lab/2026-10-21-euphorbia-ophthalmica-scout")
BASE.mkdir(parents=True,exist_ok=True)
S=requests.Session()
S.headers.update({"User-Agent":"HaysBotanyFieldPhotoQA/1.0 (educational plant images; rate-limited)"})
ALLOW={"cc0","cc-by","cc-by-sa","cc-by-nc"}
OUTPUT=[]
SEEN=set()
def get_json(url,params=None):
 r=S.get(url,params=params,timeout=25);r.raise_for_status();return r.json()
def inspect_obs(obs,priority):
 name=(obs.get("taxon") or {}).get("name","")
 if name!="Euphorbia ophthalmica":return
 oid=obs["id"]
 images=obs.get("photos") or []
 # Pick up to 3 photos per observation, first or close series; avoid bulk copies.
 num=0
 for p in images:
  pid=p.get("id")
  license_code=(p.get("license_code") or "").lower()
  if not pid or license_code not in ALLOW or pid in SEEN:continue
  SEEN.add(pid)
  url=p.get("url") or ""
  if not url:continue
  url=url.replace("/square.","/large.").replace("/small.","/large.").replace("/medium.","/large.")
  # iNat photo source URL stays unchanged from metadata aside from selecting its supplied large variant.
  try:
   rr=S.get(url,timeout=30);rr.raise_for_status()
   with Image.open(io.BytesIO(rr.content)) as im:
    im.load()
    w,h=im.size
    if w<500 or h<350:continue
    im=ImageOps.exif_transpose(im).convert("RGB")
    im.thumbnail((1400,1400))
    output=io.BytesIO();im.save(output,"JPEG",quality=88,optimize=True)
    raw=output.getvalue()
   assert len(raw)>16000
   with Image.open(io.BytesIO(raw)) as check: check.verify()
   fn=f"obs-{oid}-photo-{pid}.jpg"
   (BASE/fn).write_bytes(raw)
   record={
    "observation_id":oid,"photo_id":pid,"file":str(BASE/fn),"taxon_from_api":name,
    "priority":priority,"photo_license_code":license_code,
    "photo_attribution":p.get("attribution"),
    "photo_src_page":f"https://www.inaturalist.org/photos/{pid}",
    "observation_url":f"https://www.inaturalist.org/observations/{oid}",
    "quality_grade":obs.get("quality_grade"),
    "taxon_matched":True,"source_url":url,"saved_dimensions":list(im.size),
    "saved_sha256":hashlib.sha256(raw).hexdigest(),
    "annotation_status":"UNREVIEWED do not publish as diagnostic anatomy or assume mature fruit/seed"
   }
   OUTPUT.append(record);num+=1
   if num>=3 or len(OUTPUT)>=14:break
  except Exception as e:
   OUTPUT.append({"photo_id":pid,"observation_id":oid,"status":"download_hold","reason":str(e)[:250]})
  time.sleep(.18)
def records(params):
 results=get_json("https://api.inaturalist.org/v1/observations",params=params).get("results",[])
 return [o for o in results if (o.get("taxon") or {}).get("name")=="Euphorbia ophthalmica"]
for oid in [15150734,15705647,14038301]:
 try:
  ob=get_json(f"https://api.inaturalist.org/v1/observations/{oid}").get("results",[])
  if ob: inspect_obs(ob[0],"expert-or-referenced-observation")
 except Exception as e: OUTPUT.append({"observation_id":oid,"status":"API_hold","reason":str(e)[:250]})
 if len(OUTPUT)>=14:break
try:
 # Confirm taxon ID via exact string, no synonyms allowed for media.
 tax=get_json("https://api.inaturalist.org/v1/taxa/autocomplete",{"q":"Euphorbia ophthalmica"}).get("results",[])
 ids=[t["id"] for t in tax if t.get("name")=="Euphorbia ophthalmica"]
 assert ids,"Exact species absent from current iNat API"
 for ob in records({"taxon_id":ids[0],"quality_grade":"research","photos":True,"per_page":15,"order_by":"votes","order":"desc"}):
  if len([x for x in OUTPUT if x.get("file")])>=14: break
  inspect_obs(ob,"research-grade-ranked-photo-set")
except Exception as e: OUTPUT.append({"status":"research-scout-hold","reason":str(e)[:250]})
report={"date":"2026-10-21","taxon":"Euphorbia ophthalmica","stage":"PHOTO_LAB_UNREVIEWED_CANDIDATES_ONLY","candidate_photos":OUTPUT,
"policy":"No candidate is a verified fruit/seed/stipule macro until actual saved JPEG pixel inspection. Individual photo CC license and exact taxon API checked; photo rights may only be exercised with attribution and noncommercial restrictions where applicable. No county nativity decision."}
(BASE/"manifest.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({"downloaded":len([x for x in OUTPUT if x.get("file")]),"failed":len([x for x in OUTPUT if not x.get("file")]),"photo_ids":[x.get("photo_id") for x in OUTPUT if x.get("file")]},indent=2))
assert any(x.get("file") for x in OUTPUT), "No candidate files selected; only scout report written locally"
