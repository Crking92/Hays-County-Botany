#!/usr/bin/env python3
"""Exact-taxon iNaturalist photo-level license preflight and recovery.

This script independently checks *current photo-specific* Creative Commons
permissions in iNaturalist observation API; never assumes that observation
licensing or a project source flag grants photo reuse. The user has confirmed
a stand-alone strictly noncommercial educational GitHub Pages website.
Newly downloaded copies are resized as JPEG with EXIF/GPS stripped.
Never bypass active claims, identity holds, unverified photo rights, or pages QA.
"""
from __future__ import annotations

from datetime import datetime,timezone
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import re
import time
from urllib.parse import urlencode,urlparse
from urllib.request import Request,urlopen

from PIL import Image,ImageOps

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/"reports/public-gap-inat-verified-20261020.json"
SRC={
 "arbutus-xalapensis":{
  "species_json":"content/taxa/Ericaceae/Arbutus/arbutus-xalapensis/species.json",
  "scientific_name":"Arbutus xalapensis",
  "photo_role":"Provisional independently licensed research-grade exact-species photograph; confirm diagnostic organs and bark in later field-ID pass",
  "file_prefix":"images/public-inat-texas-madrone",
 },
 "dalea-purpurea":{
  "species_json":"content/taxa/Fabaceae/Dalea/dalea-purpurea/species.json",
  "scientific_name":"Dalea purpurea",
  "photo_role":"Provisional independently licensed research-grade exact-species flowering plant photo; confirm inflorescence and leaf anatomy before arrows",
  "file_prefix":"images/public-inat-purple-prairie-clover",
 }
}
TINANTIA_PATH="content/taxa/Commelinaceae/Tinantia/tinantia-anomala/species.json"
TINANTIA_OBSERVATION=202298891
TINANTIA_PHOTO=357260447

def fetch(url:str,max_size=6_000_000)->bytes:
    allowed={"api.inaturalist.org","inaturalist-open-data.s3.amazonaws.com","static.inaturalist.org"}
    if not url.startswith("https://") or urlparse(url).hostname not in allowed:
        raise ValueError("unapproved iNaturalist source domain")
    request=Request(url,headers={
        "User-Agent":"HaysBotanyVisualLearner/1.0 (education, attributed iNaturalist images; github.com/Crking92/Hays-County-Botany)",
        "Accept":"application/json,image/jpeg,image/*;q=0.8",
    })
    last=None
    for attempt in range(2):
        try:
            with urlopen(request,timeout=30) as r:
                if urlparse(r.geturl()).hostname not in allowed:
                    raise RuntimeError("unapproved host redirect")
                b=r.read(max_size+1)
            if len(b)>max_size:
                raise RuntimeError("response exceeds size cap")
            return b
        except Exception as e:
            last=e
            if attempt==0:time.sleep(3)
    raise RuntimeError("iNaturalist source unavailable: "+str(last)[:160])

def getjson(url:str)->dict:
    data=fetch(url,2_000_000)
    j=json.loads(data.decode("utf-8"))
    if not isinstance(j,dict):
        raise RuntimeError("unexpected JSON shape")
    return j

def live_claim(taxon:str)->bool:
    claims=json.loads((ROOT/"workflow/work-claims.json").read_text()).get("claims",[])
    now=datetime.now(timezone.utc)
    for item in claims:
        if item.get("status")!="active":continue
        end=item.get("expires_at")
        if end:
            try:
                if datetime.fromisoformat(end.replace("Z","+00:00"))<=now:continue
            except Exception:pass
        if taxon in (item.get("taxa") or []) or taxon in (item.get("scope_key") or ""):
            return True
    return False

def clean_image(source_url:str)->tuple[bytes,list[int],str]:
    orig=fetch(source_url,12_000_000)
    if len(orig)<6500:
        raise RuntimeError("photo download suspiciously small")
    with Image.open(BytesIO(orig)) as im:
        if im.format not in {"JPEG","PNG","WEBP"}:
            raise RuntimeError("unexpected photo format")
        if min(im.size)<400:
            raise RuntimeError("image dimensions too small for field learner")
        px=ImageOps.exif_transpose(im).convert("RGB")
        px.thumbnail((1600,1600),Image.Resampling.LANCZOS)
        dims=list(px.size)
        b=BytesIO()
        px.save(b,format="JPEG",quality=88,optimize=True)
        out=b.getvalue()
    with Image.open(BytesIO(out)) as verified:
        if verified.info.get("exif") or verified.getexif().get(34853):
            raise RuntimeError("saved JPEG still contains EXIF or GPS")
        verified.verify()
    return out,dims,sha256(orig).hexdigest()

def parse_photo_license(photo:dict)->tuple[str,str]:
    l=str(photo.get("license_code") or "").strip().lower()
    if l=="cc-by":return "CC BY 4.0","https://creativecommons.org/licenses/by/4.0/"
    if l=="cc-by-nc":return "CC BY-NC 4.0","https://creativecommons.org/licenses/by-nc/4.0/"
    raise RuntimeError("photo itself does not carry verified usable BY/NC license")

def obs_exact(j:dict, scientific:str)->list[dict]:
    return [o for o in j.get("results",[])
        if isinstance(o,dict)
        and o.get("taxon",{}).get("name")==scientific
        and o.get("quality_grade")=="research"
        and isinstance(o.get("photos"),list)]

def choose_candidate(spec:dict)->tuple[dict,dict]:
    name=spec["scientific_name"]
    results=[]
    for code in ("cc-by","cc-by-nc"):
        url="https://api.inaturalist.org/v1/observations?"+urlencode({
            "taxon_name":name,"quality_grade":"research","photo_license":code,
            "per_page":30,"order_by":"created_at","order":"desc"})
        payload=getjson(url)
        results.extend(obs_exact(payload,name))
        if results:break
    for obs in results:
        for photo in obs.get("photos",[]):
            if not isinstance(photo,dict):continue
            lic=str(photo.get("license_code") or "").lower()
            if lic not in {"cc-by","cc-by-nc"}:continue
            attribution=str(photo.get("attribution") or "")
            if not attribution or not any(t in attribution.lower() for t in ["cc by","cc-by","creativecommons"]):
                # Photo credit is mandatory. Some iNat responses provide a
                # copyright holder but no formatted credit; don't invent it.
                continue
            image_url=str(photo.get("url") or "")
            if "/square." in image_url:
                image_url=image_url.replace("/square.","/large.")
            elif "/medium." in image_url:
                image_url=image_url.replace("/medium.","/large.")
            elif "/small." in image_url:
                image_url=image_url.replace("/small.","/large.")
            if not image_url.startswith("https://"):
                continue
            return obs,{**photo,"candidate_image_url":image_url}
    raise RuntimeError("no verified research-grade exact-species photos with independent BY/NC and creator attribution returned")

def install_one(taxon:str,spec:dict)->dict:
    if live_claim(taxon):raise RuntimeError("unexpired foreign work claim")
    species_path=ROOT/spec["species_json"]
    j=json.loads(species_path.read_text(encoding="utf-8"))
    if j.get("id")!=taxon:raise RuntimeError("canonical taxon identity mismatch")
    for img in j.get("images",[]):
        if isinstance(img,dict) and str(img.get("file","")).startswith("images/public-inat-"):
            raise RuntimeError("existing new photo candidate found; not overwrite or duplicate")
    obs,photo=choose_candidate(spec)
    license_name,license_url=parse_photo_license(photo)
    id_=int(photo["id"])
    author=str(photo["attribution"])
    path_field=spec["file_prefix"]+"-"+str(id_)+".jpg"
    output=species_path.parent/path_field
    if output.exists():raise RuntimeError("target image name already exists")
    data,dims,input_digest=clean_image(photo["candidate_image_url"])
    output.parent.mkdir(exist_ok=True)
    output.write_bytes(data)
    image={
      "file":path_field,
      "role":spec["photo_role"],
      "caption":"Exact-species research-grade iNaturalist photograph. Photo-specific anatomy and look-alike arrow labels are pending visual review.",
      "creator":author,
      "license":license_name,"license_url":license_url,
      "source_page":"https://www.inaturalist.org/photos/"+str(id_),
      "observation_source_page":"https://www.inaturalist.org/observations/"+str(obs["id"]),
      "source_photo_id":str(id_),"source_observation_id":str(obs["id"]),
      "source_taxon":spec["scientific_name"],"source_quality_grade":"research",
      "source_photo_license_code":photo["license_code"],
      "source_type":"iNaturalist individual photo copyright data verified live by API",
      "public_reuse":"yes with photo-specific CC terms on current strictly noncommercial educational site",
      "changes":"Downloaded from iNaturalist, resized and reencoded to JPEG; EXIF/GPS removed; no drawn arrows",
      "published_jpeg_sha256":sha256(data).hexdigest(),
      "source_sha256":input_digest,"published_jpeg_dimensions":dims,
      "annotation_pending":True,
      "photo_organ_validation":"pending manual anatomical visual review",
    }
    j.setdefault("images",[]).append(image)
    species_path.write_text(json.dumps(j,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return {
        "taxon":taxon,
        "species_json":spec["species_json"],
        "physical_file":str(output.relative_to(ROOT)),
        "relative_photo_path":path_field,
        "creator":author,"license":license_name,
        "source_photo_id":str(id_),"source_observation_id":str(obs["id"]),
        "sha256":sha256(data).hexdigest(),
        "image_bytes":len(data),"dimensions":dims,
        "status":"READY_AFTER_GITHUB_COMMIT_VERIFICATION"
    }

def tinantia_reconcile()->dict:
    if live_claim("tinantia-anomala"):raise RuntimeError("Tinantia has an unexpired claim")
    sp=ROOT/TINANTIA_PATH
    j=json.loads(sp.read_text(encoding="utf-8"))
    if j.get("id")!="tinantia-anomala":
        raise RuntimeError("Tinantia canonical ID changed")
    api=getjson("https://api.inaturalist.org/v1/observations/"+str(TINANTIA_OBSERVATION))
    observations=obs_exact(api,"Tinantia anomala")
    if len(observations)!=1:
        raise RuntimeError("Tinantia exact research-grade observation unavailable or wrong taxon")
    obs=observations[0]
    matches=[p for p in obs["photos"] if int(p.get("id",0))==TINANTIA_PHOTO]
    if len(matches)!=1:
        raise RuntimeError("Tinantia photo ID is not in the exact observation")
    p=matches[0]
    if str(p.get("license_code") or "").lower()!="cc-by-nc":
        raise RuntimeError("Tinantia current original image license is not CC BY-NC")
    attribution=str(p.get("attribution") or "")
    if not attribution or ("joey" not in attribution.lower() and "santore" not in attribution.lower()):
        raise RuntimeError("Tinantia credited author identity not independently corroborated")
    matches_local=[x for x in j.get("images",[]) if x.get("photo_id")==TINANTIA_PHOTO and x.get("creator")=="Joey Santore"]
    if len(matches_local)!=1:
        raise RuntimeError("Tinantia canonical source image record missing or duplicated")
    target=matches_local[0]
    if target.get("license")!="CC BY-NC" or str(target.get("public_reuse")).lower()!="no":
        raise RuntimeError("Tinantia original historical restrictions do not match expected record; review")
    file_path=sp.parent/target["file"]
    if not file_path.is_file() or file_path.stat().st_size<6000:
        raise RuntimeError("Tinantia local JPEG missing")
    with Image.open(file_path) as im:
        im.verify()
    # Retain literal historical project permission field rather than rewrite
    # the image's license; only update publication eligibility after independent
    # photo-specific proof on iNaturalist + owner's noncommercial site policy.
    target["historical_public_reuse_flag"]="no — recorded under prior private-use-only learner policy"
    target["public_reuse"]="yes for strictly noncommercial educational GitHub Pages use under existing photo-specific CC BY-NC 4.0"
    target["license_url"]="https://creativecommons.org/licenses/by-nc/4.0/"
    target["current_photo_rights_verification"]={
        "checked_utc":datetime.now(timezone.utc).isoformat(),
        "source":"https://www.inaturalist.org/photos/"+str(TINANTIA_PHOTO),
        "photo_id":TINANTIA_PHOTO,
        "photo_license_code":"cc-by-nc",
        "photo_attribution":attribution,
        "condition":"Retain attribution and CC BY-NC; re-audit before any commercial website use; no rights waiver or license change",
        "historical_reuse_record_preserved":True,
    }
    sp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return {
      "taxon":"tinantia-anomala","species_json":TINANTIA_PATH,
      "physical_file":str(file_path.relative_to(ROOT)),
      "relative_photo_path":target["file"],
      "creator":target["creator"],"license":"CC BY-NC 4.0",
      "source_photo_id":str(TINANTIA_PHOTO),
      "status":"EXISTING_IMAGE_PERMISSIONS_RECONCILED_WHILE_PRESERVING_HISTORICAL_FLAG",
    }

def main()->None:
    result={"utc":datetime.now(timezone.utc).isoformat(),
        "installed":[],"held":[],
        "site":"stand-alone strictly noncommercial educational Github Pages",
        "scope":"exact-photo live rights verification; no family/taxonomy/website changes or direct publishing",
        "note":"The source report is based on live iNaturalist photo licenses. Every photo still needs future visual-anatomy QA."}
    jobs=[
        ("tinantia-anomala",None),
        *[(key,val) for key,val in SRC.items()]
    ]
    for taxon,spec in jobs:
        try:
            if spec is None:
                result["installed"].append(tinantia_reconcile())
            else:
                result["installed"].append(install_one(taxon,spec))
        except Exception as e:
            result["held"].append({"taxon":taxon,"reason":str(e)[:500]})
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"ready":[x["taxon"] for x in result["installed"]],"held":result["held"]},indent=2))

if __name__=="__main__":
    main()
