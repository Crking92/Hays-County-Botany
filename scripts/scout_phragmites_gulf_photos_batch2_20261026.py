#!/usr/bin/env python3
"""Find license-cleared photos for provisional Gulf Phragmites anatomical review.
One-shot source review; candidate JPEGs NOT inserted in learner galleries.
No bypass of image host limits and no new lineage/genotype claims.
"""
import hashlib, html, io, json, re, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont

SOURCE_IDS=[106877308,111946695,103014382,102377603,67757920,38089670,107265890,67160886]
DEST=Path("reports/phragmites-gulf-photo-scout-batch2-focused-20261026")
REPORT=Path("reports/phragmites-gulf-photo-scout-batch2-focused-20261026.json")
DEST.mkdir(parents=True,exist_ok=True)
ALLOWED={"cc0","cc-by","cc-by-sa","cc-by-nc","cc-by-nc-sa"}
USER_AGENT="HaysCountyBotanyVisualLearner/1.0 (noncommercial educational research; https://github.com/Crking92/Hays-County-Botany)"
def request(url,accept="application/json"):
    req=urllib.request.Request(url,headers={"User-Agent":USER_AGENT,"Accept":accept})
    with urllib.request.urlopen(req,timeout=25) as r:
        if r.status!=200:raise ValueError("unexpected status "+str(r.status))
        return r.read(14000000)
def norm_license(code):
    return "CC0 1.0" if code=="cc0" else code.upper().replace("CC-","CC ").replace("-","-") + " 4.0"
def resize_jpg(raw):
    if not raw.startswith(bytes.fromhex("ffd8")):raise ValueError("not valid JPEG signature")
    with Image.open(io.BytesIO(raw)) as im:im.verify()
    with Image.open(io.BytesIO(raw)) as im:
        if im.format!="JPEG" or min(im.size)<400:raise ValueError("image too small")
        photo=ImageOps.exif_transpose(im).convert("RGB")
        origin=photo.size
        photo.thumbnail((1200,1200))
        buf=io.BytesIO();photo.save(buf,format="JPEG",quality=87,optimize=True)
        return buf.getvalue(),origin,list(photo.size)
results=[];held=[]
for obs_id in SOURCE_IDS:
    url=f"https://www.inaturalist.org/observations/{obs_id}"
    try:
        doc=json.loads(request(f"https://api.inaturalist.org/v1/observations/{obs_id}"))
        obs=doc["results"][0]
        tax=(obs.get("taxon") or {})
        taxon=tax.get("name","")
        if not ("Phragmites australis" in taxon and "berlandieri" in taxon):
            held.append({"observation":obs_id,"source":url,"reason":"Current observation identified differently: "+taxon})
            continue
        grade=obs.get("quality_grade")
        photos=obs.get("photos") or []
        readable=[]
        for photo in photos:
            lic=str(photo.get("license_code") or "").lower()
            if lic not in ALLOWED:
                held.append({"observation":obs_id,"photo_id":photo.get("id"),"reason":"Individual photo license absent or disallowed"})
                continue
            raw_url=photo.get("url") or ""
            if not raw_url.startswith("https://"):continue
            uri=urllib.parse.urlparse(raw_url)
            if not (uri.hostname and (uri.hostname.endswith("inaturalist.org") or uri.hostname.endswith("inaturalist-open-data.s3.amazonaws.com") or uri.hostname.endswith("inaturalist-open-data.s3.us-east-1.amazonaws.com"))):
                held.append({"observation":obs_id,"photo_id":photo.get("id"),"reason":"Unexpected host"})
                continue
            observer=obs.get("user") or {}
            creator=photo.get("attribution") or observer.get("name") or observer.get("login")
            if not creator:continue
            # Scope to existing obs photos, don't assume source identification is DNA proven
            readable.append((photo,lic,creator))
        for ph,lic,creator in readable[:2]:
            photo_id=ph["id"]
            imgurl=ph["url"]
            for low in ("/square.","/thumb.","/small.","/medium."):
                imgurl=imgurl.replace(low,"/large.")
            target=DEST/f"gulf-observation-{obs_id}-photo-{photo_id}.jpg"
            try:
                raw=request(imgurl,accept="image/jpeg")
                jpg,original,scaled=resize_jpg(raw)
                target.write_bytes(jpg)
                results.append({
                    "observation_id":obs_id,"photo_id":photo_id,"image_path":str(target),
                    "taxon":taxon,"grade":grade,"location":obs.get("place_guess"),
                    "source_observation_url":url,"source_photo_url":f"https://www.inaturalist.org/photos/{photo_id}",
                    "creator":creator,"license":norm_license(lic),
                    "license_code":lic,"license_url":"https://creativecommons.org/"+("publicdomain/zero/1.0/" if lic=="cc0" else "licenses/"+lic.removeprefix("cc-")+"/4.0/"),
                    "original_size":original,"saved_size":scaled,"sha256":hashlib.sha256(jpg).hexdigest(),
                    "photo_review_status":"IMAGE_BYTES_PRESENT; OWNER/MODEL VISUAL STRUCTURE CHECK PENDING",
                    "lineage_certification":"iNaturalist current taxon identification only; no specimen genotype or independent voucher"
                })
            except Exception as e:
                held.append({"observation":obs_id,"photo_id":photo_id,"reason":"Image byte acquisition failed: "+str(e)[:180]})
    except Exception as e:
        held.append({"observation":obs_id,"reason":"Observation lookup failed: "+type(e).__name__+": "+str(e)[:220]})
# contact sheet of only explicitly licensed images, for clinician/crew-level visible-anatomy screening
if results:
    tw,th=340,320
    cols=3
    rows=(len(results)+cols-1)//cols
    sheet=Image.new("RGB",(cols*tw,rows*th),"#ffffff")
    draw=ImageDraw.Draw(sheet)
    for i,info in enumerate(results):
        x=(i%cols)*tw;y=(i//cols)*th
        with Image.open(info["image_path"]) as im:
            im.thumbnail((tw-12,th-70))
            ox=x+(tw-im.width)//2;oy=y+6
            sheet.paste(im,(ox,oy))
        draw.text((x+8,y+th-59),f"obs {info['observation_id']} / photo {info['photo_id']}",fill="#222222")
        credit=re.sub(r"<[^>]*>","",html.unescape(info["creator"]))
        draw.text((x+8,y+th-42),credit[:48],fill="#222222")
        draw.text((x+8,y+th-25),info["license"],fill="#222222")
    sheet.save(DEST/"contact-sheet.jpg",quality=88)
REPORT.write_text(json.dumps({
 "date":"2026-10-26","source":"iNaturalist individual observations and photo license metadata",
 "scope":"GULF REFERENCE PHOTO SCOUT, NOT CANONICAL GALLERY / NOT GENETIC EVIDENCE",
 "source_ids":SOURCE_IDS,"candidate_images":results,"held":held,"count":len(results),
 "gallery_changes":0,"site_deployment":False,
 "next_action":"Human pixel review of each candidate for actual collar/sheath, true inner ligule or glumes; only then promote allowed image with existing photo/license conditions."
},indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print("GULF_SCOUT_COUNT",len(results),"HELD",len(held))
