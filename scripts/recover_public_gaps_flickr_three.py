#!/usr/bin/env python3
"""Recover up to three image-level verified original Flickr photos into held species.

Photo attribution, exact Flickr photo ID, taxon and CC BY 2.0 rights are separately
supported by individually reviewed Wikimedia Commons file pages (2026-10-20).
This script only downloads the identified image itself, checks Flickr photo+license
metadata when available, decodes/resizes JPEG and removes EXIF, then appends
the source-specific public first-photo reference to existing canonical cards.
DO NOT copy/relabel older restricted study images. No website publication.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import time
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

from PIL import Image, ImageOps

ROOT=Path(__file__).resolve().parent.parent
REPORT=ROOT/"reports/public-gap-flickr-three-20261020.json"
LICENSE_URL="https://creativecommons.org/licenses/by/2.0/"
DATA={
 "arbutus-xalapensis":{
   "species_json":"content/taxa/Ericaceae/Arbutus/arbutus-xalapensis/species.json",
   "flickr":"https://www.flickr.com/photos/cwsteeds/5120818041/",
   "flickr_id":"5120818041",
   "commons":"https://commons.wikimedia.org/wiki/File:Arbutus_xalapensis_Guadalupe_Mountains.jpg",
   "creator":"Clinton Steeds",
   "role":"Texas madrone in the Guadalupe Mountains: full evergreen woody habit",
   "filename":"images/public-clinton-steeds-texas-madrone.jpg",
   "caption":"Texas madrone (Arbutus xalapensis) photographed in McKittrick Canyon, Texas. Use to learn broad upright evergreen habit; examine separate bark close-ups for diagnostic smooth peeling bark."
 },
 "tinantia-anomala":{
   "species_json":"content/taxa/Commelinaceae/Tinantia/tinantia-anomala/species.json",
   "flickr":"https://www.flickr.com/photos/wefi_official/11657312984/",
   "flickr_id":"11657312984",
   "commons":"https://commons.wikimedia.org/wiki/File:Tinantia_anomala_(Anne_Worner).jpg",
   "creator":"Anne Worner",
   "role":"False dayflower open flower, side and front floral anatomy",
   "filename":"images/public-anne-worner-false-dayflower.jpg",
   "caption":"False dayflower (Tinantia anomala), open flower. Examine petal and stamen positions in the photo; detailed structure arrows remain pending."
 },
 "dalea-purpurea":{
   "species_json":"content/taxa/Fabaceae/Dalea/dalea-purpurea/species.json",
   "flickr":"https://www.flickr.com/photos/usfwsmtnprairie/5988196396/",
   "flickr_id":"5988196396",
   "commons":"https://commons.wikimedia.org/wiki/File:Purple_Prairie_Clover_(5988196396).jpg",
   "creator":"Jennifer Jewett / U.S. Fish and Wildlife Service",
   "flickr_author":"USFWS Mountain-Prairie",
   "role":"Purple prairie clover flowering spike and field habit",
   "filename":"images/public-jennifer-jewett-purple-prairie-clover.jpg",
   "caption":"Purple prairie clover (Dalea purpurea), USFWS Des Lacs National Wildlife Refuge, North Dakota. Compare slender flower head and narrow pinnately compound foliage; do not infer detailed traits not visible."
 }
}

def get(url:str, limit:int, allowed:set[str]) -> bytes:
    if not url.startswith("https://") or urlparse(url).hostname not in allowed:
        raise RuntimeError("source or redirect not on permitted photo hosts")
    req=Request(url,headers={
        "User-Agent":"HaysCountyBotanyEducationalLearner/1.0 (source-attributed Commons-confirmed CC-BY 2.0; repository github.com/Crking92/Hays-County-Botany)",
        "Accept":"application/json,image/jpeg,image/*;q=0.8"})
    with urlopen(req,timeout=35) as r:
        if urlparse(r.geturl()).hostname not in allowed:
            raise RuntimeError("redirected to unapproved media host")
        data=r.read(limit+1)
    if len(data)>limit:
        raise RuntimeError("source exceeded data cap")
    return data

def current_foreign_claim(taxon:str)->bool:
    j=json.loads((ROOT/"workflow/work-claims.json").read_text())
    now=datetime.now(timezone.utc)
    for x in j.get("claims",[]):
        if x.get("status")!="active":continue
        expiration=x.get("expires_at")
        if expiration:
            try:
                if datetime.fromisoformat(expiration.replace("Z","+00:00"))<=now:
                    continue
            except ValueError:pass
        if taxon in (x.get("taxa") or []) or taxon in (x.get("scope_key") or ""):
            return True
    return False

def flickr_photo(spec:dict)->tuple[bytes,str,dict]:
    endpoint="https://www.flickr.com/services/oembed/?"+urlencode({
        "url":spec["flickr"],"format":"json","maxwidth":1600,"maxheight":1600})
    errors=[]
    for attempt in range(2):
        try:
            raw=get(endpoint,180_000,{"www.flickr.com","flickr.com"})
            meta=json.loads(raw.decode("utf-8"))
            if str(meta.get("type")).lower()!="photo":
                raise RuntimeError("Flickr oEmbed did not return a still photograph")
            link=str(meta.get("url") or "")
            host=urlparse(link).hostname or ""
            if not (host=="live.staticflickr.com" or host=="farm4.staticflickr.com" or host.endswith(".staticflickr.com")):
                raise RuntimeError("Flickr returned unfamiliar photo media host")
            if spec["flickr_id"] not in link:
                raise RuntimeError("Flickr returned a different photo ID; abort")
            lic_id=str(meta.get("license_id",""))
            # Flickr CC BY ID=4. When not returned, independently verified
            # Commons preserved its CC BY 2.0 license; never substitute another photo ID.
            if lic_id and lic_id!="4":
                raise RuntimeError("current Flickr license ID differs from verified CC BY 2.0")
            lic_text=str(meta.get("license") or "")
            if lic_text and ("noncommercial" in lic_text.lower() or "no derivatives" in lic_text.lower() or "all rights reserved" in lic_text.lower()):
                raise RuntimeError("Flickr reported restrictive current terms; hold")
            if str(meta.get("author_name") or "").strip() and spec.get("flickr_author"):
                if spec["flickr_author"].lower().split("-")[0] not in str(meta["author_name"]).lower():
                    raise RuntimeError("Flickr source account does not match creator's original")
            pic=get(link,14_000_000,{"live.staticflickr.com",host})
            if len(pic)<6000:raise RuntimeError("photograph content too small")
            return pic,link,meta
        except Exception as e:
            errors.append(str(e)[:240])
            if attempt==0:time.sleep(7)
    raise RuntimeError("Flickr oEmbed or photo download failed: "+" | ".join(errors)[:400])

def recover(taxon:str,spec:dict)->dict:
    if current_foreign_claim(taxon):
        raise RuntimeError("unexpired ownership claim; don't compete")
    path=ROOT/spec["species_json"]
    j=json.loads(path.read_text(encoding="utf-8"))
    if j.get("id")!=taxon:raise RuntimeError("canonical ID mismatch")
    dest=path.parent/spec["filename"]
    if dest.exists():
        if any(x.get("file")==spec["filename"] for x in j.get("images",[])):
            return {"taxon":taxon,"status":"already installed"}
        raise RuntimeError("output exists but species.json not linked")
    originals=[x for x in j.get("images",[]) if x.get("source_page")==spec["commons"]]
    if taxon=="tinantia-anomala" and len(originals)!=1:
        raise RuntimeError("existing Commons image record no longer unique")
    raw,url,meta=flickr_photo(spec)
    with Image.open(BytesIO(raw)) as im:
        if im.format not in {"JPEG","PNG"}:
            raise RuntimeError("original photo not an expected image type")
        if min(im.size)<380:
            raise RuntimeError("original photo lacks usable diagnostic resolution")
        pixels=ImageOps.exif_transpose(im).convert("RGB")
        pixels.thumbnail((1600,1600),Image.Resampling.LANCZOS)
        data=BytesIO()
        pixels.save(data,"JPEG",quality=87,optimize=True)
        jpeg=data.getvalue()
        dims=list(pixels.size)
    with Image.open(BytesIO(jpeg)) as probe:
        if probe.info.get("exif") or probe.getexif().get(34853):
            raise RuntimeError("GPS/EXIF survived web-copy conversion")
        probe.verify()
    if len(jpeg)<5000:
        raise RuntimeError("resulting image too small")
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_bytes(jpeg)
    photo={
        "file":spec["filename"],
        "role":spec["role"],"caption":spec["caption"],
        "creator":spec["creator"],
        "license":"CC BY 2.0",
        "license_url":LICENSE_URL,
        "source_page":spec["commons"],
        "original_source_page":spec["flickr"],
        "source_photo_id":spec["flickr_id"],
        "downloaded_photo_url":url,
        "source_platform":"Flickr original photo; Commons image-level license independently verified",
        "public_reuse":"yes, subject to individual CC BY 2.0 license and credit",
        "study_use":"yes",
        "changes":"Source Flickr image resized/reencoded as JPEG for educational website and EXIF/GPS removed; no anatomy arrows or labels added",
        "source_sha256":sha256(raw).hexdigest(),
        "published_jpeg_sha256":sha256(jpeg).hexdigest(),
        "published_jpeg_dimensions":dims,
        "annotation_pending":True,
        "source_verification":"Individually named exact species, photographer and CC BY 2.0 photo license checked on linked Commons file page 2026-10-20; Flickr photo ID confirmed by Flickr oEmbed response."
    }
    if originals:
        # The exact same image already exists as a remote Commons link; change
        # only its file pointer to the newly verified physical photo bytes.
        target=originals[0]
        target["original_external_media_link"]=target.get("file")
        target.update(photo)
    else:
        # Do not touch the historic private-study galleries or their licenses.
        j.setdefault("images",[]).append(photo)
    path.write_text(json.dumps(j,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return {"taxon":taxon,"status":"local staged pending commit",
       "species_json":spec["species_json"],
       "physical_file":str(dest.relative_to(ROOT)),
       "relative_photo_path":spec["filename"],
       "creator":spec["creator"],"license":photo["license"],
       "source_page":spec["commons"],"flickr_id":spec["flickr_id"],
       "image_dimensions":dims,"image_bytes":len(jpeg),
       "sha256":sha256(jpeg).hexdigest()}

def main()->None:
    result={
        "date_utc":datetime.now(timezone.utc).isoformat(),
        "note":"No Pages publication; installs only independently verified source-specific public photo bytes, preserves original private images.",
        "installed":[],"held":[]
    }
    for taxon,spec in DATA.items():
        try:
            r=recover(taxon,spec)
            if r["status"]=="already installed":
                result["held"].append({"taxon":taxon,"reason":"already installed, no duplicate"})
            else:result["installed"].append(r)
        except Exception as exc:
            result["held"].append({"taxon":taxon,"reason":str(exc)[:600]})
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"installed":[x["taxon"] for x in result["installed"]],"held":result["held"]},indent=2))

if __name__=="__main__":
    main()
