#!/usr/bin/env python3
"""One-time per-photo source licensed seed micrograph intake for E. simulans / E. theriaca."""
from pathlib import Path
from PIL import Image, ImageOps
import requests, io, hashlib, json

OUTPUT=Path("photo-lab/2026-10-21-euphorbia-simulans-seed-scout")
OUTPUT.mkdir(parents=True,exist_ok=True)
S=requests.Session()
S.headers["User-Agent"]="HaysBotany/1.0 EducationalSourceQA"
OBSERVATIONS={4434982:"Euphorbia simulans",4435298:"Euphorbia theriaca"}
ALLOWED={"cc0","cc-by","cc-by-sa","cc-by-nc"}
rows=[]
for oid,expected in OBSERVATIONS.items():
 try:
  response=S.get(f"https://api.inaturalist.org/v1/observations/{oid}",timeout=30)
  response.raise_for_status()
  ob=response.json()["results"][0]
  taxon=(ob.get("taxon") or {}).get("name","")
  assert taxon==expected or (expected=="Euphorbia theriaca" and taxon=="Euphorbia theriaca var. theriaca"), f"Taxon is {taxon}, not {expected}"
  for ph in (ob.get("photos") or [])[:10]:
   pid=ph.get("id")
   lic=(ph.get("license_code") or "").lower()
   if lic not in ALLOWED or not pid:
    rows.append({"observation":oid,"photo_id":pid,"status":"not licensed","license":lic})
    continue
   url=ph.get("url") or ""
   if not url:
    rows.append({"observation":oid,"photo_id":pid,"status":"no URL"});continue
   url=url.replace("/square.","/large.").replace("/small.","/large.").replace("/medium.","/large.").replace("/thumb.","/large.")
   try:
    resp=S.get(url,timeout=30);resp.raise_for_status()
    with Image.open(io.BytesIO(resp.content)) as im:
     im.load(); w,h=im.size
     assert min(w,h)>=300 and max(w,h)>=500, f"Source too small {w}x{h}"
     im=ImageOps.exif_transpose(im).convert("RGB")
     im.thumbnail((1800,1800))
     output=io.BytesIO();im.save(output,"JPEG",quality=92,optimize=True)
     raw=output.getvalue()
    assert len(raw)>12000
    file=OUTPUT/f"obs-{oid}-photo-{pid}.jpg"
    file.write_bytes(raw)
    with Image.open(file) as check:check.verify()
    rows.append({
     "observation":oid,"taxon":taxon,"photo_id":pid,"license":lic,
     "attribution":ph.get("attribution") or f"iNaturalist photo {pid}",
     "iNaturalist_url":f"https://www.inaturalist.org/photos/{pid}",
     "observation_url":f"https://www.inaturalist.org/observations/{oid}",
     "photo_url":url,"file":str(file),"sha256":hashlib.sha256(raw).hexdigest(),
     "saved_dimensions":[im.width,im.height],
     "description":ob.get("description") or "",
     "quality_grade":ob.get("quality_grade"),
     "review_status":"exact API taxon + photo rights + decoded JPEG; visual morphology/arrow placement NOT YET reviewed"
    })
   except Exception as e:
    rows.append({"observation":oid,"photo_id":pid,"status":"download hold","reason":f"{type(e).__name__}: {str(e)[:200]}"})
 except Exception as e:
  rows.append({"observation":oid,"status":"observation hold","reason":f"{type(e).__name__}: {str(e)[:200]}"})
manifest={"stage":"PHOTO_LAB_SEED_MICRO_CANDIDATES_NOT_CANONICAL","date":"2026-10-21","records":rows,
 "guardrails":"No image shown as seed without manual saved-pixel review. Respect photographer-specific CC BY-NC and other CC licences. Observe E. theriaca is only a look-alike reference, never relabel it as E. simulans. No Hays nativity promotion."}
(OUTPUT/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
print(json.dumps({"staged_files":len([x for x in rows if x.get("file")]),"records":rows},indent=2))
assert any(x.get("taxon")=="Euphorbia simulans" and x.get("file") for x in rows),"No simulans photo staged"
