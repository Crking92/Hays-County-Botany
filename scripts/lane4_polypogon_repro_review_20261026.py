#!/usr/bin/env python3
"""Hold-first archive of exact-species reproductive photo candidates.

This is NOT a species-card installer. Candidates go to a separate review lane
until individual reproductive parts are visibly inspected. Never count these
as public gallery panels or add speculative anatomical arrows.
"""
from __future__ import annotations
import hashlib
import html
import io
import json
import pathlib
import re
import time
import urllib.parse
import urllib.request
from PIL import Image, ImageOps

dest = pathlib.Path("workflow/photo-reviews/lane4-polypogon-reproductive-20261026")
dest.mkdir(parents=True, exist_ok=True)

candidates = [
    ("45", "jpg", "Mary K. Hanson", "77266184"),
    ("46", "jpg", "Mary K. Hanson", "77266157"),
    ("47", "jpeg", "Daniel Cahen", "77696614"),
    ("48", "jpeg", "Daniel Cahen", "77696674"),
    ("49", "jpeg", "Daniel Cahen", "77866402"),
]

UA = {"User-Agent":"HaysCountyBotanyVisualLearner/1.0 (botanical educational photo source verification)"}
def download(url, limit=12_000_000):
    last=None
    for attempt in range(3):
        try:
            req=urllib.request.Request(url,headers=UA)
            with urllib.request.urlopen(req, timeout=45) as r:
                out=r.read(limit+1)
            if len(out)>limit: raise ValueError("Remote source exceeds byte safety limit")
            return out
        except Exception as e:
            last=e
            if attempt<2:time.sleep((attempt+1)*4)
    raise RuntimeError(str(last))

titles=["File:Polypogon monspeliensis flower ("+n+")."+ext for n,ext,_,_ in candidates]
query=urllib.parse.urlencode({
    "action":"query","prop":"imageinfo","iiprop":"url|sha1|size|extmetadata",
    "format":"json","titles":"|".join(titles)
})
report={
 "species":"Polypogon monspeliensis", "scope":"rights-screen candidate originals ONLY; none yet linked to gallery",
 "source_review":"2026-10-26; Wikimedia image-level CC BY 4.0 source pages and their iNaturalist review bots inspected",
 "added":[],"held":[], "live_card_changes":0, "public_gallery_panel_changes":0,
 "markers_added":0
}
try:
    response=json.loads(download("https://commons.wikimedia.org/w/api.php?"+query))
    pages={p["title"]:p for p in response.get("query",{}).get("pages",{}).values()}
except Exception as error:
    pages={}
    report["held"].append({"stage":"Commons API metadata","reason":str(error)})
for n,ext,creator,photo_id in candidates:
    title="File:Polypogon monspeliensis flower ("+n+")."+ext
    source="https://commons.wikimedia.org/wiki/"+urllib.parse.quote(title.replace(" ","_"),safe=":/()")
    out=dest/("polypogon-repro-commons-"+n+".jpg")
    try:
        page=pages.get(title)
        if not page or "imageinfo" not in page:
            raise ValueError("No original metadata; do not guess exact original URL or source license")
        info=page["imageinfo"][0]
        meta=info.get("extmetadata") or {}
        license_short=meta.get("LicenseShortName",{}).get("value","")
        license_url=meta.get("LicenseUrl",{}).get("value","")
        author=html.unescape(re.sub(r"<[^>]+>"," ",meta.get("Artist",{}).get("value","")))
        if license_short.strip().upper()!="CC BY 4.0":
            raise ValueError("Not exactly pre-approved CC BY 4.0: "+license_short)
        if "creativecommons.org/licenses/by/4.0" not in license_url:
            raise ValueError("Version mismatch in license URL")
        if creator.lower() not in author.lower():
            raise ValueError("Unexpected actual photo creator: "+author)
        src=info.get("url","")
        if not src.startswith("https://upload.wikimedia.org/wikipedia/commons/"):
            raise ValueError("Untrusted original photo host")
        orig=download(src)
        if hashlib.sha1(orig).hexdigest()!=info.get("sha1",""):
            raise ValueError("Original JPEG bytes do not match Commons recorded SHA-1")
        Image.open(io.BytesIO(orig)).verify()
        image=ImageOps.exif_transpose(Image.open(io.BytesIO(orig))).convert("RGB")
        if image.width<900 or image.height<900:raise ValueError("Insufficient resolution for reproductive macro")
        if out.exists():
            raise ValueError("Candidate already staged, don't clobber")
        image.save(out,format="JPEG",quality=90,optimize=True)
        sha256=hashlib.sha256(out.read_bytes()).hexdigest()
        report["added"].append({
          "id":n,"file":str(out),"dimensions":list(image.size),
          "photo_author":creator,"license":"CC BY 4.0",
          "license_url":"https://creativecommons.org/licenses/by/4.0/",
          "source_page":source,"original_inaturalist_photo":"https://www.inaturalist.org/photos/"+photo_id,
          "original_sha1":info["sha1"],"local_sha256":sha256,
          "modifications":"JPEG RGB re-encoded without EXIF/GPS; no annotations or cropping",
          "review_status":"UNREVIEWED ANATOMY - DO NOT LINK TO PUBLIC GALLERY YET",
          "target":"Are two notched glumes, their awn origin, or fertile lemma visibly distinguishable? Do not infer."
        })
    except Exception as error:
        report["held"].append({"id":n,"source":source,"reason":str(error)})
(dest/"manifest.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps({"archived":len(report["added"]),"held":len(report["held"]),"manifest":str(dest/"manifest.json")}))
