#!/usr/bin/env python3
"""Stage Bob Harms / UT Austin seep-muhly ligule and spikelet images for manual pixel QA.

Photo rights evidence: https://w3.biosci.utexas.edu/prc/Monocots/
"All Selected Monocots images and web pages are copyrighted by Bob Harms.
They are free for scientific and educational uses provided that Bob Harms is
properly credited." NOT a Creative Commons license; public educational reuse only.
Never add directly to species.json until actual photo and rights review.
"""
import io, hashlib, json, re, time
from pathlib import Path
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageOps

OUT=Path("workflow/photo-lab/muhlenbergia-reverchonii/bob-harms-diagnostics")
REPORT=Path("reports/muhlenbergia-reverchonii-bob-harms-diagnostics-20261021.json")
PERMISSION="https://w3.biosci.utexas.edu/prc/Monocots/"
ROLES={
  "ligule_sheath":"https://w3.biosci.utexas.edu/prc/Monocots/GrassHTML/data/pages/MURE2-L.html",
  "spikelet_detail":"https://w3.biosci.utexas.edu/prc/Monocots/GrassHTML/data/pages/MURE2-S.html",
}
session=requests.Session()
session.headers.update({"User-Agent":"HaysCountyBotany-educational-macro-review/1.0 (github.com/Crking92/Hays-County-Botany)"})
def get(url, binary=False):
    err=None
    for i in range(3):
        try:
            r=session.get(url,timeout=35)
            r.raise_for_status()
            assert 100<=len(r.content)<=16000000, (len(r.content),url)
            return r.content if binary else r.text
        except Exception as e:
            err=repr(e)
            print("source retry",url,i+1,err[:200],flush=True)
            time.sleep(2)
    raise RuntimeError(f"Unable to reach {url}: {err}")
def page(url):
    variations=[url,url.replace("w3.biosci.utexas.edu","www.biosci.utexas.edu"),
                    url.replace("w3.biosci.utexas.edu","biosci.utexas.edu")]
    problems=[]
    for u in variations:
        try:
            html=get(u)
            s=BeautifulSoup(html,"html.parser")
            text=s.get_text(" ",strip=True).lower()
            if "muhlenbergia" not in text or "reverchonii" not in text:
                raise ValueError("page is not clearly labeled Muhlenbergia reverchonii")
            return u,s
        except Exception as e:problems.append(str(e))
    raise RuntimeError("; ".join(problems)[:450])
def candidates(source,soup):
    urls=[]
    for tag in soup.find_all(["img","a","source"]):
        src=(tag.get("src") if tag.name!="a" else tag.get("href")) or tag.get("data-src")
        if not src:continue
        full=urljoin(source,src)
        if not full.startswith("https://") and not full.startswith("http://"):continue
        if urlparse(full).netloc not in ("w3.biosci.utexas.edu","www.biosci.utexas.edu","biosci.utexas.edu"):continue
        if re.search(r"\.(jpe?g|png|gif|webp)(?:\?.*)?$",urlparse(full).path,re.I):
            urls.append(full)
    return list(dict.fromkeys(urls))
def main():
    report={"species":"Muhlenbergia reverchonii","creator":"Bob Harms",
       "permission_scope":"scientific/educational with attribution; not CC; public site only if noncommercial educational and credit retained",
       "permission_evidence":PERMISSION,"gallery_modified":False,"taxonomy_native_range_changed":False,
       "candidates":[]}
    for role,url in ROLES.items():
        rec={"role":role,"page_url":url,"status":"HOLD_UNVERIFIED","files":[]}
        try:
            resolved,html=page(url)
            rec["resolved_page_url"]=resolved
            options=candidates(resolved,html)
            rec["source_image_links"]=len(options)
            valid=[]
            for link in options[:20]:
                try:
                    b=get(link,binary=True)
                    with Image.open(io.BytesIO(b)) as im:
                        im.load()
                        im=ImageOps.exif_transpose(im).convert("RGB")
                    if min(im.size)<320:continue
                    valid.append((len(b),link,b,im))
                except Exception as e:
                    rec.setdefault("skipped_links",[]).append({"url":link,"reason":str(e)[:120]})
            valid.sort(key=lambda t:t[0],reverse=True)
            if not valid: raise RuntimeError("No photo >=320 pixels in page media candidates; image-specific source not proven")
            # These are REVIEW-ONLY not identity-final. Stage at most 2 large images.
            for idx,(_,link,raw,im) in enumerate(valid[:2]):
                im.thumbnail((1800,1800),Image.Resampling.LANCZOS)
                buf=io.BytesIO()
                im.save(buf,format="JPEG",quality=92,optimize=True)
                data=buf.getvalue()
                assert len(data)>13000
                with Image.open(io.BytesIO(data)) as check:check.verify()
                dst=OUT/f"review-only-{role}-{idx+1}.jpg"
                dst.parent.mkdir(parents=True,exist_ok=True)
                if not dst.exists():
                    dst.write_bytes(data)
                rec["files"].append({
                    "path":str(dst),"source_image":link,
                    "sha256_original":hashlib.sha256(raw).hexdigest(),
                    "sha256_local":hashlib.sha256(data).hexdigest(),
                    "actual_dimensions":list(im.size),
                    "creator":"Bob Harms",
                    "rights":"Educational/scientific use with Bob Harms attribution; not Creative Commons",
                    "permission_evidence":PERMISSION,
                    "license_verified_for_commercial_use":False,
                    "status":"SOURCE_PAGE_DERIVED; HOLD for saved-byte botanical + fine anatomical review"
                })
            rec["status"]="STAGED_SOURCE_IMAGES_FOR_MANUAL_PIXEL_REVIEW"
        except Exception as e:
            rec["status"]="HOLD_"+str(e)[:410]
        report["candidates"].append(rec)
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"staged":sum(len(r["files"]) for r in report["candidates"]),
                      "roles":[{"role":r["role"],"status":r["status"],"files":len(r["files"])} for r in report["candidates"]]},indent=2))
if __name__=="__main__": main()
