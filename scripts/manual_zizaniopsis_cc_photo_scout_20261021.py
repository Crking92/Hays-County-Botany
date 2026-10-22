#!/usr/bin/env python3
"""Small source-exact CC BY 4.0 review of 3 photos of the ALREADY INSTALLED giant cutgrass.
Never alter species/genus/gallery before actually inspecting the downloaded pixels.
Wikimedia files and Alex Abair credit:
https://commons.wikimedia.org/wiki/Category:Zizaniopsis_miliacea
"""
import io, json, hashlib, re, time
from pathlib import Path
from PIL import Image, ImageOps
import requests

PHOTOS=[264449018,264449037,264449047]
OUT=Path("workflow/photo-lab/zizaniopsis-miliacea/cc-by-alex-abair-20261021")
REPORT=Path("reports/zizaniopsis-cc-by-photo-review-20261021.json")
s=requests.Session()
s.headers.update({"User-Agent":"HaysCountyBotanyEducationalPhotoReview/1.0 (public CC BY identification archive)"})
def get(url):
    err=None
    for attempt in range(3):
        try:
            r=s.get(url,timeout=35)
            r.raise_for_status()
            return r
        except Exception as e:err=str(e);print("retry",attempt+1,url,err[:100],flush=True);time.sleep(3)
    raise RuntimeError(str(err))
def main():
    c=json.loads(Path("content/taxa/Poaceae/Zizaniopsis/zizaniopsis-miliacea/species.json").read_text())
    assert c["scientific_name"]=="Zizaniopsis miliacea"
    assert len(c["images"])==1, "Concurrent photo worker added images: stop"
    result={"taxon":"Zizaniopsis miliacea","original_taxon_image_count":1,"physically_staged":0,"canonical_gallery_changed":False,"candidates":[]}
    for pid in PHOTOS:
        p={"photo_id":pid,"status":"HOLD — unavailable","creator":"Alex Abair",
           "file_page":f"https://commons.wikimedia.org/wiki/File:Zizaniopsis_miliacea_{pid}.jpg",
           "observation":"https://www.inaturalist.org/observations/153134793"}
        try:
            title=f"File:Zizaniopsis miliacea {pid}.jpg"
            r=get("https://commons.wikimedia.org/w/api.php",).json() if False else None
            api=get("https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url%7Csha1%7Csize%7Cextmetadata&format=json&titles="+requests.utils.quote(title))
            data=api.json()["query"]["pages"]
            page=list(data.values())[0]
            assert "imageinfo" in page
            info=page["imageinfo"][0]
            m=info.get("extmetadata") or {}
            license_short=m.get("LicenseShortName",{}).get("value","")
            rights=m.get("LicenseUrl",{}).get("value","")
            artist=m.get("Artist",{}).get("value","")
            assert "CC BY 4.0" in license_short or rights.endswith("/by/4.0/"),("Not CC BY 4.0",license_short,rights)
            assert "Abair" in re.sub("<[^>]+>"," ",artist) or "Alex" in re.sub("<[^>]+>"," ",artist),("Wrong author",artist)
            assert f"{pid}" in (page.get("title","")) and "commons.wikimedia.org" in info["url"]
            raw=get(info["url"]).content
            assert len(raw)>20000 and len(raw)<10000000
            assert hashlib.sha1(raw).hexdigest()==info["sha1"],"Source bytes SHA1 mismatch"
            with Image.open(io.BytesIO(raw)) as im:
                im.load(); assert im.format=="JPEG"
                img=ImageOps.exif_transpose(im).convert("RGB")
            assert min(img.size)>650
            img.thumbnail((1400,1400),Image.Resampling.LANCZOS)
            buf=io.BytesIO();img.save(buf,"JPEG",quality=90,optimize=True)
            b=buf.getvalue()
            with Image.open(io.BytesIO(b)) as check:
                assert not check.getexif().get(34853)
                check.verify()
            dest=OUT/f"REVIEW-ONLY-alex-abair-{pid}.jpg"
            dest.parent.mkdir(parents=True,exist_ok=True)
            if not dest.exists():dest.write_bytes(b)
            p.update({"status":"PHYSICALLY_STAGED_FOR_PIXEL_REVIEW_ONLY","path":str(dest),
             "size":list(img.size),"creator":"Alex Abair","license":"CC BY 4.0",
             "source_original_url":info["url"],"source_sha1":info["sha1"],
             "sanitized_sha256":hashlib.sha256(b).hexdigest(),
             "taxonomy":"Source observation; NOT independently re-vouchered",
             "public_gallery_imported":False,"arrow_count":0})
            result["physically_staged"]+=1
        except Exception as e:p["status"]="HOLD — "+str(e)[:300]
        result["candidates"].append(p)
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="candidates"},indent=2))
if __name__=="__main__":main()
