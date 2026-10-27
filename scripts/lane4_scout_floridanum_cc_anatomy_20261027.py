#!/usr/bin/env python3
"""Create a license-checked, unpublished photo shortlist for real Paspalum floridanum pixels.

Does NOT install images into the species learner or grant photo roles.
Only exact photo-level CC0 / CC BY / CC BY-SA licenses, research-grade source
observations, and exact P. floridanum species identifications are shortlisted.
"""
import io, json, re, hashlib, pathlib, urllib.request, urllib.parse, time
from PIL import Image, ImageOps
ROOT=pathlib.Path("reports/lane4-floridanum-photo-candidates-20261027")
OUT=ROOT/"images"
TAXON_ID=166176
LEGAL={"cc0","cc-by","cc-by-sa"}
AGENT="Hays-County-Botany-public-license-review/1.0 (field identification educational photo validation)"
def load(url,limit=12500000):
    last=None
    for attempt in range(3):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":AGENT,"Accept":"application/json,image/*"})
            with urllib.request.urlopen(req,timeout=35) as r:
                v=r.read(limit+1)
                if len(v)>limit:raise ValueError("Oversized download")
                return v
        except Exception as e:
            last=e;time.sleep(2*(attempt+1))
    raise RuntimeError(str(last))
def fetch_page(place=None,page=1):
    params={"taxon_id":TAXON_ID,"quality_grade":"research","photos":"true","per_page":100,
      "page":page,"order_by":"observed_on","order":"desc","photo_license":"cc0,cc-by,cc-by-sa"}
    if place:params["place_id"]=place
    url="https://api.inaturalist.org/v1/observations?"+urllib.parse.urlencode(params)
    return json.loads(load(url,6000000)).get("results",[])
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    selected=[]; seen=set();notes=[]
    for place in (18,None):
        for page in (1,2,3):
            try:arr=fetch_page(place,page)
            except Exception as e:notes.append({"query_place_id":place,"page":page,"error":str(e)});continue
            notes.append({"query_place_id":place,"page":page,"received_observations":len(arr)})
            for o in arr:
                taxon=o.get("taxon") or {}
                if taxon.get("name")!="Paspalum floridanum":continue
                if o.get("quality_grade")!="research":continue
                if o.get("taxon_geoprivacy")=="private":continue
                for photo in (o.get("photos") or [])[:6]:
                    phid=photo.get("id");lic=(photo.get("license_code") or "").lower().strip()
                    if not phid or phid in seen or lic not in LEGAL:continue
                    url=photo.get("url") or ""
                    if not url.startswith("https://") or ("inaturalist" not in url and "amazonaws.com" not in url):continue
                    full=re.sub(r"/(square|small|medium|thumb|original)\.", "/large.",url)
                    try:
                        raw=load(full)
                        im=Image.open(io.BytesIO(raw));im.verify()
                        im=ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert("RGB")
                        if min(im.size)<420:continue
                        if max(im.size)>1700:
                            im.thumbnail((1700,1700),Image.Resampling.LANCZOS)
                        target=OUT/("inat-"+str(phid)+"-review.jpg")
                        im.save(target,"JPEG",quality=89,optimize=True)
                        blob=target.read_bytes()
                        check=Image.open(io.BytesIO(blob))
                        assert not check.getexif() and "exif" not in check.info
                        selected.append({"photo_id":phid,"observation_id":o.get("id"),
                         "license":lic.upper(),"photo_creator_attribution":photo.get("attribution"),
                         "taxon":taxon.get("name"),"observation_quality_grade":o.get("quality_grade"),
                         "observation_page":"https://www.inaturalist.org/observations/"+str(o.get("id")),
                         "photo_page":"https://www.inaturalist.org/photos/"+str(phid),
                         "image_original_url":full,"local_review_path":str(target),
                         "local_sha256":hashlib.sha256(blob).hexdigest(),"review_dimensions":list(im.size),
                         "review_status":"STAGED ONLY; exact plant photo role / true ligule / base / locality NOT determined from metadata. DO NOT display as finished."})
                        seen.add(phid)
                        print("STAGED",phid,lic,im.size,flush=True)
                    except Exception as e: notes.append({"photo_id":phid,"error":str(e)[:200]})
                    if len(selected)>=20:break
                if len(selected)>=20:break
            if len(selected)>=20:break
        if len(selected)>=20:break
    report={"created_on":"2026-10-27","target":"Paspalum floridanum",
      "status":"PHOTO_CANDIDATES_ONLY_NOT_IN_LEARNER","license_rule":"iNaturalist individual photo license in CC0, CC BY, CC BY-SA; research-grade exact taxon observation; no automatic anatomy role",
      "eligible_photos_physically_staged":len(selected),"candidates":selected,"query_notes":notes,
      "no_new_learner_photo_or_score_claim":True,"identity_note":"Research grade does not prove specimen ID. Inspect each exact photograph before species learner selection; close photos do not imply physical scale.",
      "license_note":"Photo license as of metadata request. Preserve actual photographer attribution and SA obligations. Do not adopt observation license in place of each photo's license."}
    (ROOT/"report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print("STAGING_COMPLETE",len(selected),flush=True)
if __name__=="__main__":main()
