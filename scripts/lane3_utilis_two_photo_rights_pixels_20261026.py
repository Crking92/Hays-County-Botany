#!/usr/bin/env python3
"""Exact Uvalde County M. utilis observation / original photo-ID 410577695, 410577679.
Licence and image bytes MUST be individually verified; report and contact sheet only.
Scientific identity remains source determined until an expert voucher audit.
"""
import io, json, pathlib, hashlib, urllib.request
from PIL import Image, ImageOps, ImageDraw
DIR=pathlib.Path("reports")
DIR.mkdir(exist_ok=True)
REP=DIR/"lane3-utilis-two-photo-scout-20261026.json"
SHEET=DIR/"lane3-utilis-two-photo-scout-20261026.jpg"
IDS=(410577695,410577679)
URL="https://api.inaturalist.org/v1/observations/231187884"
out={"taxon":"Muhlenbergia utilis","observation_id":231187884,
"source_observation":"https://www.inaturalist.org/observations/231187884",
"purpose":"Licensing+pixel scout of two reserved prior candidate IDs. NOT physical install to canonical photo gallery.",
"candidates":[],"errors":[]}
def request(url):
  headers={"User-Agent":"HaysCountyBotany/1.0 (noncommercial open biodiversity photo curation; github.com/Crking92/Hays-County-Botany)","Accept":"application/json,image/jpeg,image/*"}
  with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=38) as f:
    b=f.read(15000001)
    if len(b)>15000000: raise ValueError("Too-large source payload")
    return b
try:
  d=json.loads(request(URL))
  assert len(d.get("results",[]))==1
  obs=d["results"][0]
  assert obs["id"]==231187884 and obs["taxon"]["name"]=="Muhlenbergia utilis"
  out["source_quality"]=obs.get("quality_grade")
  out["observed_on"]=obs.get("observed_on")
  out["source_place"]=obs.get("place_guess")
  photos={x["id"]:x for x in obs["photos"]}
  sheet=Image.new("RGB",(1200,740),"white")
  draw=ImageDraw.Draw(sheet)
  for i,pid in enumerate(IDS):
    photo=photos[pid]
    lic=(photo.get("license_code") or "").lower()
    assert lic in ("cc0","cc-by","cc-by-sa","cc-by-nc"),f"uncleared license: {pid} {lic}"
    record={"photo_id":pid,"source_photo_page":f"https://www.inaturalist.org/photos/{pid}",
      "license_code":lic,"attribution":photo.get("attribution"),
      "source_url":photo.get("url"),
      "observed_taxon":obs["taxon"]["name"],
      "observed_on":obs.get("observed_on"),
      "restriction":"No use or final confirmation without reviewing exact original pixels and actual noncommercial usage obligations"}
    for suffix in ("original.jpg","original.jpeg"):
      original_url=f"https://inaturalist-open-data.s3.amazonaws.com/photos/{pid}/{suffix}"
      try:
        b=request(original_url)
        with Image.open(io.BytesIO(b)) as im:
          assert im.format=="JPEG"
          im.verify()
        with Image.open(io.BytesIO(b)) as im:
          im=ImageOps.exif_transpose(im).convert("RGB")
          record["source_size"]=[im.width,im.height]
          record["sha256_original"]=hashlib.sha256(b).hexdigest()
          record["valid_source_jpeg"]=True
          im.thumbnail((580,630),Image.Resampling.LANCZOS)
          sheet.paste(im,(600*i+(600-im.width)//2,8+(630-im.height)//2))
          record["original_url"]=original_url
          break
      except Exception as e:
        record.setdefault("source_errors",[]).append({"url":original_url,"error":str(e)[:120]})
    draw.text((600*i+8,646),f"Photo {pid}  - {lic}",fill="black")
    draw.text((600*i+8,669),(photo.get("attribution") or "(no required attribution)")[:78],fill="black")
    draw.text((600*i+8,695),f"Observation 231187884, {obs.get('observed_on','')}",fill="black")
    out["candidates"].append(record)
  sheet.save(SHEET,"JPEG",quality=88,optimize=True)
  out["contact_sheet"]=str(SHEET)
  out["contact_sheet_sha256"]=hashlib.sha256(SHEET.read_bytes()).hexdigest()
except Exception as e:
  out["errors"].append(str(e)[:300])
REP.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({"candidates":len(out["candidates"]),"valid_originals":sum(bool(x.get("valid_source_jpeg")) for x in out["candidates"]),"errors":out["errors"]},indent=2))
