#!/usr/bin/env python3
"""One-time, fail-closed, wild seep muhly exact-photo intake. NO canonical card edit.

Match two visible WildflowerSearch taxon thumbnails back to actual iNaturalist
observation photo IDs before credit/license assignment. Only stage originals
if source taxon, copyright, wild status, thumbnail-to-original pHash, and
actual image bytes all pass. Never guess photographer from the gallery page.
"""
import hashlib, io, json, os, sys, time
from pathlib import Path
import requests
from PIL import Image, ImageOps
import imagehash

ROOT = Path(".")
BASE = ROOT / "workflow/photo-lab/muhlenbergia-reverchonii"
REPORT = ROOT / "reports/muhlenbergia-reverchonii-wild-macro-scout-20261021.json"
SPECIES = ROOT / "content/taxa/Poaceae/Muhlenbergia/muhlenbergia-reverchonii/species.json"
TAXON = "Muhlenbergia reverchonii"
TAXON_ID = 165570
SOURCES = [
    {"role":"open_panicle","observation":36950498,
     "thumbnail":"https://storage.googleapis.com/wildflowersearchv11.appspot.com/img/Muhlenbergia_reverchonii.jpg",
     "match_author":"Matt","user_login":"drbh2o","year":2025},
    {"role":"spikelet_detail","observation":4246792,
     "thumbnail":"https://storage.googleapis.com/wildflowersearchv11.appspot.com/sds/Muhlenbergia_reverchonii.jpg",
     "match_author":"Sam","user_login":"sambiology","year":2016},
]
ALLOWED={"cc0":"CC0","cc-by":"CC BY","cc-by-nc":"CC BY-NC","cc-by-sa":"CC BY-SA"}
session=requests.Session()
session.headers.update({"User-Agent":"HaysCountyBotanyNoncommercialPhotoQA/1.0 (github.com/Crking92/Hays-County-Botany)"})

def get(url, max_bytes=18_000_000):
    last=None
    for attempt in range(3):
        try:
            r=session.get(url, timeout=45)
            r.raise_for_status()
            assert 100 < len(r.content) < max_bytes, ("unexpected bytes",len(r.content),url)
            return r.content
        except Exception as e:
            last=str(e)
            print("fetch retry", attempt+1, url[:80],last[:200],flush=True)
            time.sleep(3)
    raise RuntimeError("fetch failed "+url+" "+str(last))

def valid_image(raw):
    with Image.open(io.BytesIO(raw)) as original:
        original.load()
        im=ImageOps.exif_transpose(original).convert("RGB")
    assert min(im.size) >= 280 and max(im.size) <= 18000, ("dimensions", im.size)
    return im

def variants(img):
    return [
        img,
        ImageOps.fit(img,(390,320),method=Image.Resampling.LANCZOS,centering=(.5,.5)),
        ImageOps.fit(img,(390,320),method=Image.Resampling.LANCZOS,centering=(.5,.35)),
        ImageOps.fit(img,(390,320),method=Image.Resampling.LANCZOS,centering=(.5,.65)),
        img.resize((390,320),Image.Resampling.LANCZOS)
    ]

def similarity(thumb, img):
    target=imagehash.phash(thumb)
    return min(int(target-imagehash.phash(v)) for v in variants(img))

def main():
    assert json.loads(SPECIES.read_text())["scientific_name"] == TAXON
    findings=[]
    additions=[]
    for src in SOURCES:
        result={"role":src["role"],"source_observation":f"https://www.inaturalist.org/observations/{src['observation']}",
                "thumbnail":src["thumbnail"],"status":"NOT_INSTALLED"}
        try:
            thumb=valid_image(get(src["thumbnail"],max_bytes=4_000_000))
            assert 280 <= min(thumb.size), ("tiny source",thumb.size)
            # Image-gallery links may point to an older observation even when
            # the currently displayed image is from a DIFFERENT same-author observation.
            # Search the author and photographed year; match actual pixels, not page order.
            records=[]
            original_api=json.loads(get(f"https://api.inaturalist.org/v1/observations/{src['observation']}",max_bytes=8_000_000))
            records += original_api.get("results") or []
            api_url=(f"https://api.inaturalist.org/v1/observations?taxon_id={TAXON_ID}"
                     f"&user_id={src['user_login']}&year={src['year']}&photos=true&per_page=100")
            matching_api=json.loads(get(api_url,max_bytes=12_000_000))
            records += (matching_api.get("results") or [])[:70]
            result["source_author"]=src["user_login"]
            result["author_year"]=src["year"]
            unique={}
            for obs in records:
                if obs.get("id") not in unique:
                    unique[obs.get("id")]=obs
            result["observations_considered"]=len(unique)
            hits=[]
            for obs in unique.values():
                if not obs.get("taxon") or obs["taxon"].get("id")!=TAXON_ID or obs["taxon"].get("name")!=TAXON:
                    continue
                if obs.get("captive") not in (False,None):
                    continue
                user=obs.get("user") or {}
                if user.get("login")!=src["user_login"]:
                    continue
                desc=(obs.get("description") or "").lower()
                if any(v in desc for v in ("'undaunted'","'autumn embers'","cultivar","garden planting")):
                    continue
                for p in (obs.get("photos") or []):
                    code=(p.get("license_code") or "").lower()
                    if code not in ALLOWED or not p.get("url"):
                        continue
                    attribution=(p.get("attribution") or "")
                    if src["match_author"].lower() not in attribution.lower() and src["match_author"].lower() not in (user.get("name") or "").lower() and src["match_author"].lower() not in user.get("login","").lower():
                        continue
                    medium=p["url"].replace("square.","medium.").replace("thumb.","medium.").replace("small.","medium.")
                    try:
                        raw=get(medium,max_bytes=8_000_000)
                        im=valid_image(raw)
                        score=similarity(thumb,im)
                        hits.append({"photo":p,"score":score,"image":im,"raw":raw,"source_url":medium,"observation_id":obs["id"]})
                    except Exception as exc:
                        print("photo skipped",p.get("id"),str(exc)[:150],flush=True)
            hits.sort(key=lambda x:x["score"])
            result["candidate_photos_checked"]=len(hits)
            result["closest_photo_id"]=hits[0]["photo"]["id"] if hits else None
            result["closest_observation_id"]=hits[0]["observation_id"] if hits else None
            result["closest_phash_distance"]=hits[0]["score"] if hits else None
            if not hits or hits[0]["score"]>10 or (len(hits)>1 and hits[1]["score"]-hits[0]["score"]<4):
                result["status"]="HOLD: No unambiguous exact-source photograph match; no image installed"
                findings.append(result)
                continue
            h=hits[0]; p=h["photo"]; license_code=p["license_code"].lower()
            assert license_code in ALLOWED
            # Download best available original after matching to verify the same file,
            # and only then strip EXIF/GPS and preserve the source reference.
            original=p["url"]
            for tag in ("square.","thumb.","small.","medium.","large."):
                original=original.replace(tag,"original.")
            original_raw=get(original,max_bytes=18_000_000)
            im=valid_image(original_raw)
            assert similarity(thumb,im)<=12
            im.thumbnail((1500,1500),Image.Resampling.LANCZOS)
            out=io.BytesIO()
            im.save(out,"JPEG",quality=91,optimize=True)
            data=out.getvalue()
            assert len(data)>=14_000
            with Image.open(io.BytesIO(data)) as check:check.verify()
            target=BASE/f"{src['role']}-inat-{p['id']}.jpg"
            assert not target.exists(), "already staged; do not overwrite"
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(data)
            result.update({"status":"STAGED_EXACT_MATCH_FOR_MANUAL_PIXEL_QA", "source_observation":f"https://www.inaturalist.org/observations/{h['observation_id']}","photo_id":p["id"],"creator":p.get("attribution"),
                           "license":ALLOWED[license_code],
                           "license_code":license_code,
                           "source_photo":f"https://www.inaturalist.org/photos/{p['id']}",
                           "original_url":original,
                           "source_sha256":hashlib.sha256(original_raw).hexdigest(),
                           "local_sha256":hashlib.sha256(data).hexdigest(),
                           "path":str(target),"dimensions":list(im.size),
                           "match_phash_distance":h["score"],
                           "arrow_status":"none; must inspect saved GitHub bytes manually before annotation",
                           "image_role_provisional":"Wild observation source-matched flowering structures; species determination follows source, not independently re-keyed",
                           "public_rights":"Noncommercial educational learner only; photographer/source/license and NC/SA terms must accompany any eventual public use."
                           })
            additions.append(str(target))
        except Exception as exc:
            result["status"]="HOLD: "+str(exc)[:400]
        findings.append(result)
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps({
        "taxon":TAXON,"intake":"one-time source-photo verification, not a finished species ID",
        "thumbnail_site":"https://wildflowersearch.org/search?tsn=164871_2",
        "images_staged":len(additions),
        "candidate_status":findings,
        "science_holds_or_existing_species_edited":False,
        "canonical_species_gallery_modified":False,
        "source_credit_must_follow_individual_photo":True,
        "needs":"manual QA of ORIGINAL staged pixels, then guarded update of species and genus with true visible arrows; do not infer any glume/ligule from thumbnails"
    },indent=2)+"\n")
    print(json.dumps({"staged":len(additions),"results":[{"role":x["role"],"status":x["status"],"distance":x.get("closest_phash_distance")} for x in findings]},indent=2))
if __name__=="__main__":
    main()
