#!/usr/bin/env python3
"""Save individually verified source-licensed Phalaris caroliniana high-res candidates for human review.
Does not modify canonical species card. Does not pre-certify a true ligule.
"""
import json, re, io, hashlib, pathlib, urllib.request
from PIL import Image, ImageOps
base=pathlib.Path("reports/lane5-phalaris-photo-scout-20261027")
items=json.loads((base/"candidates.json").read_text())["photos"]
by_id={x["id"]:x for x in items}
desired=["653998915","653998943","653014288","643034634","643034675","643034732"]
def download(u):
 req=urllib.request.Request(u,headers={"User-Agent":"HaysCountyBotanyPhotoAnatomyReview/1.0"})
 with urllib.request.urlopen(req,timeout=50) as f:return f.read()
out=[]
for pid in desired:
 item=by_id[pid]
 obs=json.loads(download("https://api.inaturalist.org/v1/observations/"+item["obs"]))
 rec=next((o for o in obs.get("results",[]) if str(o.get("id"))==item["obs"]),None)
 if not rec or (rec.get("taxon") or {}).get("name")!="Phalaris caroliniana" or rec.get("quality_grade")!="research":
  out.append({"photo_id":pid,"status":"HELD","reason":"Exact research-grade source identity changed"});continue
 photo=next((p for p in rec.get("photos",[]) if str(p.get("id"))==pid),None)
 license=(photo or {}).get("license_code") or ""
 license=license.replace("_","-").lower()
 if license not in ["cc0","cc-by","cc-by-sa"] or license!=item["license"]:
  out.append({"photo_id":pid,"status":"HELD","reason":"Source-specific open reuse rights changed"});continue
 raw=download(item["photo_direct"])
 with Image.open(io.BytesIO(raw)) as check:check.verify()
 with Image.open(io.BytesIO(raw)) as orig:
  img=ImageOps.exif_transpose(orig).convert("RGB")
  if min(img.size)<600:out.append({"photo_id":pid,"status":"HELD","reason":"Image too small"});continue
  img.thumbnail((1800,1800))
  buffer=io.BytesIO();img.save(buffer,"JPEG",quality=87,optimize=True)
  b=buffer.getvalue()
 out_file=base/("review-original-"+pid+".jpg")
 out_file.write_bytes(b)
 with Image.open(out_file) as verify:verify.verify()
 out.append({"photo_id":pid,"status":"REVIEW_ONLY_ARCHIVED","file":out_file.as_posix(),
  "pixel_dimensions":list(img.size),"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest(),
  "creator":item["creator"],"license":item["license"],"source_page":item["source_page"],
  "source_observation":item["observation_page"],"photo_region":item["place"],
  "visual_review":"Human pixel-level classification still required; not in Learner"})
(base/"detail-review-manifest.json").write_text(json.dumps({"status":"HI_RES_CANDIDATE_REVIEW_NOT_INSTALLED",
 "species":"Phalaris caroliniana","date":"2026-10-27","items":out,"requires":"Independently confirm correct collar/ligule boundaries and annotate visible actual structures only."},indent=2)+"\n")
print(json.dumps({"archived":len([x for x in out if x["status"]=="REVIEW_ONLY_ARCHIVED"]),"results":out}))
