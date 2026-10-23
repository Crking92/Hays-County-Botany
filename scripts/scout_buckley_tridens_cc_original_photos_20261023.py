#!/usr/bin/env python3
"""Scout EXACT Buckley's tridens source-photo licenses under old iNat taxonomy.
Read-only on canonical species, contact preview sheets live only under reports.
"""
import io,json,re,hashlib,time
from pathlib import Path
import requests
from PIL import Image,ImageOps,ImageDraw
S=requests.Session()
S.headers.update({"User-Agent":"HaysBotany-BuckleyTridens-SourcePhotoReview/1.0", "Accept":"application/json"})
BASE="https://api.inaturalist.org/v1/"
name="Tridens buckleyanus"
res=S.get(BASE+"taxa/autocomplete",params={"q":name,"per_page":30},timeout=30);res.raise_for_status()
taxa=res.json().get("results",[])
exact=[t for t in taxa if (t.get("name") or "").lower()==name.lower()]
if len(exact)!=1:raise RuntimeError("Exact synonym taxon ID not resolved; refuse broader Tridens images")
taxon=exact[0]
observations=[]
query_log=[]
for grade in ("research","needs_id"):
 for page in (1,2):
  v=S.get(BASE+"observations",params={"taxon_id":taxon["id"],"photos":"true","quality_grade":grade,
   "per_page":100,"page":page,"order":"desc","order_by":"observed_on"},timeout=34)
  v.raise_for_status();body=v.json()
  query_log.append({"quality":grade,"page":page,"results":len(body.get("results",[])),"total":body.get("total_results")})
  observations.extend(body.get("results",[]))
  if len(body.get("results",[]))<100: break
for ob in observations:
 if (ob.get("taxon") or {}).get("id")!=taxon["id"]:
  raise RuntimeError("Observed iNaturalist taxon mismatch")
cands=[]
for ob in observations:
 photos=ob.get("photos") or []
 for i,p in enumerate(photos):
  lic=(p.get("license_code") or "").lower()
  if lic not in {"cc0","cc-by","cc-by-sa"}:continue
  url=p.get("url") or ""
  if not url.startswith("https://"):continue
  cands.append({"observation_id":ob["id"],"quality":ob.get("quality_grade"),"date":ob.get("observed_on"),
   "photo_id":p.get("id"),"position":i,"original_url":re.sub(r"/(?:square|small|medium|large)\.","/original.",url),
   "preview_url":re.sub(r"/(?:square|small|medium|large)\.","/medium.",url),
   "creator":p.get("attribution") or "", "license":lic,"observation_url":f"https://www.inaturalist.org/observations/{ob['id']}",
   "photo_url":f"https://www.inaturalist.org/photos/{p.get('id')}","observation_photo_count":len(photos),
   "place":ob.get("place_guess") or "","taxon":"Tridens buckleyanus",
   "license_role":"Public license eligible only if the exact original photo and botanical subject are independently confirmed"})
cands.sort(key=lambda c:(c["quality"]!="research", -c["observation_photo_count"], -c["position"]))
out=Path("reports/buckley-tridens-inat-original-photo-scout-20261023")
out.mkdir(parents=True,exist_ok=True)
metadata={"accepted_taxon":"Tridentopsis buckleyana","iNaturalist_name":"Tridens buckleyanus",
 "inat_taxon_id":taxon["id"],"queries":query_log,"candidates":cands,
 "note":"Research-grade source determination and CC license still require original pixel inspection, no gallery installed"}
selected=cands[:64]
pages=[]
for start in range(0,len(selected),16):
 panel=Image.new("RGB",(1360,1480),"#f8f8f6");draw=ImageDraw.Draw(panel)
 shown=[]
 for slot,rec in enumerate(selected[start:start+16]):
  try:
   a=S.get(rec["preview_url"],timeout=24);a.raise_for_status()
   with Image.open(io.BytesIO(a.content)) as raw:
    raw.load();im=ImageOps.exif_transpose(raw).convert("RGB")
    im.thumbnail((326,293))
   x=(slot%4)*340;y=(slot//4)*370
   panel.paste(im,(x+(340-im.width)//2,y+4))
   draw.text((x+5,y+303),f"#{start+slot+1} obs {rec['observation_id']}",fill="#111")
   draw.text((x+5,y+321),f"photo {rec['photo_id']} {rec['license']}",fill="#111")
   draw.text((x+5,y+338),f"{rec['quality']} frame {rec['position']+1}/{rec['observation_photo_count']}",fill="#111")
   shown.append(rec["photo_id"])
  except Exception as ex: print("preview skipped",rec["photo_id"],str(ex)[:90])
 target=out/f"sheet-{start//16+1:02d}.jpg"
 panel.save(target,"JPEG",quality=86,optimize=True)
 pages.append({"path":str(target),"photo_ids":shown})
metadata["preview_sheets"]=pages
(out/"index.json").write_text(json.dumps(metadata,indent=2,ensure_ascii=False)+"\n")
print("SCOUT SUCCESS",taxon["id"],"observations",len(observations),"CC-photo candidates",len(cands),"sheets",len(pages),flush=True)
