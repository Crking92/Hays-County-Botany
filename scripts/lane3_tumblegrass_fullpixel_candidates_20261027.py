#!/usr/bin/env python3
"""Stage 6 individual photo license rechecked exact tumblegrass originals for pixel review.
No canonical species photo promotion until photographer photo pixels inspected by reviewer.
"""
import io,json,hashlib,pathlib,urllib.request
from PIL import Image,ImageOps
BASE=pathlib.Path("reports/lane3-tumblegrass-source-pixel-review-20261027")
BASE.mkdir(parents=True,exist_ok=True)
SCOUT=pathlib.Path("reports/lane3-tumblegrass-inat-anatomy-scout-20261027/report.json")
IDS=[652935046,655365125,655365156,638348984,638349021,635430310,690744881]
ALLOWED={"cc0","cc-by","cc-by-sa","cc-by-nc","cc-by-nc-sa"}
HEAD={"User-Agent":"HaysCountyBotanyEducationalNativeGrass/1.0","Accept":"application/json,image/*"}
def get(url,limit=11_000_000):
  with urllib.request.urlopen(urllib.request.Request(url,headers=HEAD),timeout=30) as r:
    blob=r.read(limit+1)
  if len(blob)>limit:raise ValueError("oversized source")
  return blob
def main():
  scout=json.loads(SCOUT.read_text())
  assert scout["canonical_taxon"]=="Muhlenbergia paniculata"
  candidates={x["photo_id"]:x for x in scout["selected"]}
  findings=[]
  for pid in IDS:
    try:
      x=candidates[pid]
      obs=json.loads(get("https://api.inaturalist.org/v1/observations/"+str(x["observation_id"])))["results"][0]
      assert obs["id"]==x["observation_id"] and obs["quality_grade"]=="research"
      assert obs["taxon"]["id"]==scout["iNat_taxon_id"]
      ph=next(p for p in obs["photos"] if p["id"]==pid)
      lic=(ph.get("license_code") or "").lower()
      assert lic in ALLOWED and lic==x["license"]
      assert ph.get("attribution")==x["attribution"] and lic!="all-rights-reserved"
      url=ph["url"]
      assert url.startswith("https://")
      possible=[url.replace("/square.","/original."),url.replace("/square.","/large.")]
      img=None;selected_url=None;failed=[]
      for source in possible:
        try:
          data=get(source,9_000_000)
          assert len(data)>10000
          with Image.open(io.BytesIO(data)) as im:
            assert im.format in ("JPEG","PNG","WEBP") and min(im.size)>=400
            rgb=ImageOps.exif_transpose(im).convert("RGB")
            rgb.thumbnail((1800,1800))
            b=io.BytesIO();rgb.save(b,format="JPEG",quality=90,optimize=True,exif=b"")
            img=b.getvalue()
            dims=list(rgb.size)
          selected_url=source;break
        except Exception as e:failed.append(repr(e)[:150])
      if img is None:raise ValueError(str(failed))
      f=BASE/(str(pid)+"-review.jpg")
      f.write_bytes(img)
      with Image.open(f) as im:
        assert im.format=="JPEG" and not im.getexif().get(34853)
        im.verify()
      findings.append({"id":pid,"status":"RIGHTS_VERIFIED_PHOTO_STAGED_NEEDS_ANATOMY_REVIEW",
        "file":str(f),"dimensions":dims,"sha256":hashlib.sha256(img).hexdigest(),
        "source":x["photo_page"],"observation_page":x["observation_page"],"source_taxon":obs["taxon"]["name"],
        "license":lic,"attribution":ph["attribution"],"locality":obs.get("place_guess"),
        "source_url":selected_url,"source_retry_failures":failed,
        "anatomical_role_not_certified":True,"published":False})
    except Exception as e:findings.append({"id":pid,"status":"SOURCE_OR_PHOTO_RIGHTS_HOLD","reason":repr(e)})
  report={"status":"EXACT_SPECIES_ORIGINAL_PIXELS_STAGED_ONLY","canonical":"Muhlenbergia paniculata",
    "iNat_taxon_id":scout["iNat_taxon_id"],"results":findings,
    "downloaded":sum(x["status"].startswith("RIGHTS_VERIFIED") for x in findings),
    "no_species_card_change":True,"missing_until_verified":["1-mm free ligule","mature unilateral spikelet macro","whole connected flowering crown"],
    "use":"Pixel inspection and license review before actual gallery and scoring"}
  (BASE/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
  print("full originals:",report["downloaded"],"of",len(IDS))
  assert report["downloaded"]>=2
if __name__=="__main__":main()
