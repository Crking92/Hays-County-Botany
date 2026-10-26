#!/usr/bin/env python3
"""Stage seven exact licensed Buckley tridentopsis anatomy photos for real-pixel review.
These are NOT installed into canonical species gallery until organ-level verification.
"""
import io,json,pathlib,hashlib,urllib.request
from PIL import Image,ImageOps
ROOT=pathlib.Path("reports/lane3-buckley-fullpixel-review-20261026")
ROOT.mkdir(parents=True,exist_ok=True)
SCOUT=pathlib.Path("reports/lane3-buckley-anatomy-scout-20261026/report.json")
IDS=[200379086,200379105,200379117,414398685,102622611,171787530,337291544]
ALLOWED={"cc0","cc-by","cc-by-sa","cc-by-nc","cc-by-nc-sa"}
HEADER={"User-Agent":"HaysCountyBotanyEducationalGrassFieldLearner/1.0","Accept":"application/json,image/*"}
def fetch(url,maxb=11_000_000):
  with urllib.request.urlopen(urllib.request.Request(url,headers=HEADER),timeout=30) as r:
    b=r.read(maxb+1)
    if len(b)>maxb:raise ValueError("over size cap")
    return b
def main():
  scout=json.loads(SCOUT.read_text())
  assert scout["species"]=="Tridentopsis buckleyana" and scout["source_taxon_id"]==169947
  db={x["photo_id"]:x for x in scout["licensed_photos"]}
  findings=[]
  for pid in IDS:
    p=db[pid]
    try:
      o=json.loads(fetch("https://api.inaturalist.org/v1/observations/"+str(p["observation_id"])))["results"][0]
      assert o["id"]==p["observation_id"] and o["quality_grade"]=="research"
      assert (o["taxon"] or {}).get("id")==169947
      ph=next(t for t in o["photos"] if t.get("id")==pid)
      lic=(ph.get("license_code") or "").lower()
      assert lic in ALLOWED and lic==p["photo_license"],(lic,p["photo_license"])
      assert ph["attribution"]==p["photographer"]
      raw_url=ph["url"]
      assert raw_url.startswith("https://")
      candidates=[raw_url.replace("/square.","/original."),raw_url.replace("/square.","/large.")]
      errors=[];saved=None;final_source=None
      for u in candidates:
        try:
          b=fetch(u,9_000_000)
          if len(b)<15_000:raise ValueError("small image bytes")
          with Image.open(io.BytesIO(b)) as im:
            assert im.format in ("JPEG","PNG","WEBP") and min(im.size)>=450,(im.format,im.size)
            rgb=ImageOps.exif_transpose(im).convert("RGB")
            rgb.thumbnail((1800,1800))
            out=io.BytesIO();rgb.save(out,"JPEG",quality=90,optimize=True,exif=b"")
            saved=out.getvalue();dim=list(rgb.size)
          final_source=u
          break
        except Exception as e:errors.append(repr(e)[:120])
      if saved is None:raise ValueError(str(errors))
      dest=ROOT/f"{pid}-review.jpg"
      dest.write_bytes(saved)
      with Image.open(dest) as im:
        assert im.format=="JPEG" and not im.getexif().get(34853) and min(im.size)>=450
        im.verify()
      findings.append({
        "photo_id":pid,"source_observation_id":o["id"],"status":"PHOTO_SOURCE_RIGHTS_VERIFIED_PIXEL_REVIEW_REQUIRED",
        "source_taxon":o["taxon"]["name"],"canonical_taxon":"Tridentopsis buckleyana",
        "file":str(dest),"sha256":hashlib.sha256(saved).hexdigest(),
        "size_px":dim,"license":lic,"attribution":ph["attribution"],"photo_page":p["source_photo"],
        "observation_page":p["source_observation"],"photo_source_url":final_source,
        "place_guess":o.get("place_guess"),"errors":errors,"published":False,
        "anatomy_status":"UNREVIEWED — no root, ligule, membrane, lemma, floret or calibrated identity asserted"
      })
    except Exception as e:findings.append({"photo_id":pid,"status":"SOURCE_LICENSE_OR_IMAGE_HOLD","error":repr(e)})
  report={
    "taxon":"Tridentopsis buckleyana","source_taxon_synonym":"Tridens buckleyanus",
    "status":"PHYSICAL_SOURCE_PIXELS_STAGED_IN_REPORTS_ONLY_NO_CANONICAL_GALLERY_CHANGES",
    "requested_photo_ids":IDS,"results":findings,
    "validated_downloads":sum(x["status"].startswith("PHOTO_SOURCE_") for x in findings),
    "photo_role_hold":"Must inspect each original JPEG pixels before truthful label/arrow; a node is not free inner ligule and a tuft is not excavated roots"
  }
  (ROOT/"report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
  print("STAGED",report["validated_downloads"],"of",len(IDS))
  assert report["validated_downloads"]>=2
if __name__=="__main__":main()
