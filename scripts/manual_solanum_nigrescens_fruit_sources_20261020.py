#!/usr/bin/env python3
"""Stage exact S. nigrescens scholarly fruit figure candidates for visual verification.
Does NOT install species gallery photos or fabricate anatomical annotations.
Scientific source: https://doi.org/10.3390/plants12081645, Figures 3 and 14.
Figures are credited, CC BY 4.0 by article authors; per-figure photographers retained.
"""
import json,io,hashlib
from pathlib import Path
import requests
from PIL import Image
OUT=Path("workflow/photo-library/candidates/solanum-nigrescens-fruit-20261020")
REPORT=Path("reports/solanum-nigrescens-scholarly-fruit-candidates-20261020.json")
ARTICLE="https://www.mdpi.com/2223-7747/12/8/1645"
LICENSE="https://creativecommons.org/licenses/by/4.0/"
FIGURES=[
 ("003","Figure 3","Sara Monzerrat Ramírez-Olvera (a,d); Jorge Manuel Valdez-Carrasco (b,c,e)","Mature fruit cluster with appressed/spreading green calyx lobes; green and black single berries with scales"),
 ("014","Figure 14","Sara Monzerrat Ramírez-Olvera","Ripening pigmentation stages and green to brown sepals")
]
HOSTS=[
 "https://mdpi-res.com/plants/plants-12-01645/article_deploy/html/images/plants-12-01645-g{f}.png",
 "https://www.mdpi.com/plants/plants-12-01645/article_deploy/html/images/plants-12-01645-g{f}.png",
 "https://europepmc.org/articles/PMC10145186/bin/plants-12-01645-g{f}.jpg",
 "https://pmc.ncbi.nlm.nih.gov/articles/PMC10145186/bin/plants-12-01645-g{f}.jpg"
]
UA={"User-Agent":"HaysBotanyEducationPhotoRightsReview/1.0 (source attribution / no bulk scraping)","Accept":"image/avif,image/webp,image/png,image/jpeg;q=0.9,*/*;q=0.5"}
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    saved=[];held=[];errors=[]
    for f,fig,creators,role in FIGURES:
        result=None
        for pattern in HOSTS:
            url=pattern.format(f=f)
            try:
                res=requests.get(url,timeout=22,headers=UA)
                if res.status_code==429:
                    errors.append({"figure":fig,"url":url,"error":"HTTP 429 rate limited: no retry"})
                    continue
                res.raise_for_status()
                if len(res.content)<18000 or len(res.content)>20000000:raise ValueError("Image bytes outside valid size budget")
                pic=Image.open(io.BytesIO(res.content))
                pic.verify()
                pic=Image.open(io.BytesIO(res.content))
                if pic.width<600 or pic.height<250:raise ValueError("Image too small to identify fruit and calyx")
                result=(pic.convert("RGB"),url)
                break
            except (requests.RequestException,ValueError,OSError) as ex:
                errors.append({"figure":fig,"url":url,"error":str(ex)[:160]})
        if result is None:
            held.append(fig)
            continue
        pic,url=result
        dest=OUT/("solanum-nigrescens-paper-fig"+f+".png")
        pic.save(dest,format="PNG",optimize=True)
        with Image.open(dest) as p:p.verify()
        item={"figure":fig,"candidate_image":str(dest),"image_dimensions":list(pic.size),
           "sha256":hashlib.sha256(dest.read_bytes()).hexdigest(),
           "license":"CC BY 4.0","license_url":LICENSE,"creator":creators,
           "article_authors":"Sara Monzerrat Ramírez-Olvera; Manuel Sandoval-Villa",
           "source_page":ARTICLE,"image_url_used":url,
           "role":role,"review_status":"CANDIDATE_IMAGE_DOWNLOADED_NEEDS_ANATOMY_REVIEW",
           "photo_geography":"Texcoco, State of Mexico research greenhouse, not a Hays occurrence",
           "derivative_notes":"Published figure downloaded unchanged as archival PNG; do not crop/relabel without inspected pixels."}
        saved.append(item);print("STAGED",fig,dest,pic.size,url)
    report={"species":"Solanum nigrescens","date":"2026-10-20","purpose":"Exact scholarly fruit-image scouting only; not canonical",
      "published_license":"CC BY 4.0","source_article":ARTICLE,"files":saved,"held_figures":held,"errors":errors,
      "status":"PHOTOS_STAGED_PENDING_ACTUAL_PIXEL_REVIEW" if saved else "NEEDS_SOURCE_RECOVERY",
      "no_install_until_review":True}
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    if not saved:raise SystemExit("No figures staged; see runner errors. No canonical species changes allowed.")
if __name__=="__main__":main()
