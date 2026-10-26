#!/usr/bin/env python3
"""Fetch full pixels of four exact-source iNaturalist M. reverchonii photographs.
Photo-level CC license and RG taxon checked on live API; no species gallery writes.
"""
import io,json,hashlib,pathlib,urllib.request
from PIL import Image,ImageOps
IDS=[751511302,637435651,744879309,748546772]
ALLOWED={"cc0","cc-by","cc-by-sa","cc-by-nc","cc-by-nc-sa"}
ROOT=pathlib.Path("reports/lane3-seep-source-pixel-review-20261026")
ROOT.mkdir(parents=True,exist_ok=True)
UA={"User-Agent":"HaysCountyBotanyEducationalLearner/1.0","Accept":"application/json,image/*"}
def fetch(url,maximum=10_000_000):
    req=urllib.request.Request(url,headers=UA)
    with urllib.request.urlopen(req,timeout=27) as r:return r.read(maximum+1)
def main():
    scout=json.loads(pathlib.Path("reports/lane3-seep-observation-scout-20261026/report.json").read_text())
    src={x["id"]:x for x in scout["photos"]}
    findings=[]
    for pid in IDS:
        p=src[pid]
        obs=json.loads(fetch("https://api.inaturalist.org/v1/observations/"+str(p["observation"])))["results"][0]
        try:
            assert obs["id"]==p["observation"]
            assert obs["quality_grade"]=="research" and obs["taxon"]["id"]==165570
            ph=next(a for a in obs["photos"] if a["id"]==pid)
            lic=(ph.get("license_code") or "").lower()
            assert lic in ALLOWED and lic==p["license"]
            assert ph.get("attribution")==p["attribution"]
            base=ph.get("url","")
            assert base.startswith("https://")
            attempts=[base.replace("/square.","/original."),base.replace("/square.","/large.")]
            good=None; url_used=None; bad=[]
            for u in attempts:
                try:
                    b=fetch(u,8_000_000)
                    if len(b)>8_000_000 or len(b)<15_000:raise ValueError("unreasonable image bytes")
                    with Image.open(io.BytesIO(b)) as im:
                        assert im.format in ("JPEG","PNG","WEBP") and min(im.size)>=500
                        rgb=ImageOps.exif_transpose(im).convert("RGB")
                        rgb.thumbnail((1700,1700))
                        buff=io.BytesIO();rgb.save(buff,"JPEG",quality=91,exif=b"",optimize=True)
                        good=buff.getvalue()
                    url_used=u;break
                except Exception as e:bad.append(str(e)[:120])
            if good is None:raise RuntimeError(";".join(bad))
            target=ROOT/(str(pid)+"-review.jpg");target.write_bytes(good)
            with Image.open(target) as im:
                dims=list(im.size)
                assert im.format=="JPEG" and not im.getexif().get(34853)
                im.verify()
            findings.append({"id":pid,"status":"REVIEW_SOURCE_BYTES_AVAILABLE_NOT_DIAGNOSTICALLY_PASSED",
                "file":str(target),"size_px":dims,"sha256":hashlib.sha256(good).hexdigest(),
                "photo_page":p["photo_page"],"observation_id":obs["id"],"species":"Muhlenbergia reverchonii",
                "license":lic,"attribution":p["attribution"],"place_guess":obs.get("place_guess"),
                "original_source":url_used,"original_attempt_errors":bad,"published":False,
                "organs":"UNASSESSED_BY_FULL_PIXEL_REVIEW; do not annotate until inspected"})
        except Exception as e:
            findings.append({"id":pid,"status":"SOURCE_OR_RIGHTS_OR_DOWNLOAD_HOLD","error":repr(e)})
    report={"scope":"Stage licensed full-source images in REPORTS only for human pixel inspection, not canonical gallery",
            "source":"iNaturalist API exact photo/observation/research species verification",
            "taxon":"Muhlenbergia reverchonii",
            "photo_ids_requested":IDS,"results":findings,
            "status":"PENDING_PIXEL_REVIEW_NOT_FIELD_READY_COMPLETION"}
    (ROOT/"report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print("Staged",sum(x["status"].startswith("REVIEW_") for x in findings),"of",len(IDS),"for manual anatomical pixel verification")
    assert any(x["status"].startswith("REVIEW_") for x in findings),"No right-cleared JPEG downloaded"
if __name__=="__main__":main()
