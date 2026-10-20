#!/usr/bin/env python3
"""Install verified Wikimedia CC BY/CC BY-SA Euphorbia maculata photo set.

Original private-study iNaturalist photo is NOT relicensed or overwritten.
Image files must download and validate before species record is changed.
"""
from pathlib import Path
from urllib.parse import quote
import requests, hashlib, io, json, time
from PIL import Image, ImageOps

BASE=Path("content/taxa/Euphorbiaceae/Euphorbia/euphorbia-maculata")
CARD=BASE/"species.json"
REPORT=Path("reports/euphorbia-maculata-commons-install-20261020.json")
SOURCES=[
 ("Euphorbia maculata plant3 (16180597798).jpg","images/02-harry-rose-habit.jpg","Harry Rose","CC BY 2.0","Whole growing plant, leaves and mat habit (not local Hays County provenance)"),
 ("Euphorbia maculata sl13.jpg","images/03-stefan-leaf-stipule.jpg","Stefan.lefnaer","CC BY-SA 4.0","Microscopic paired leaves, stipules and hairy stem at node"),
 ("Euphorbia maculata sl18.jpg","images/04-stefan-fruit-entirely-hairy.jpg","Stefan.lefnaer","CC BY-SA 4.0","Infructescence and capsule hairs across the faces, unlike prostrata keel-concentrated hairs"),
 ("Euphorbia maculata sl20.jpg","images/05-stefan-seeds-shallow-furrows.jpg","Stefan.lefnaer","CC BY-SA 4.0","Exact species seeds with LOW transverse ridges and shallow crosswise furrows; NOT longitudinal ribs"),
]
def get(session,name):
    filename=name.replace(" ","_")
    h=hashlib.md5(filename.encode("utf-8")).hexdigest()
    direct="https://upload.wikimedia.org/wikipedia/commons/"+h[0]+"/"+h[:2]+"/"+quote(filename,safe="._-()")
    special="https://commons.wikimedia.org/wiki/Special:Redirect/file/"+quote(filename,safe="._-()")+"?width=1600"
    failures=[]
    for url in (special,direct):
        for attempt in range(2):
            try:
                res=session.get(url,timeout=65);res.raise_for_status()
                raw=res.content
                assert len(raw)>18000 and len(raw)<14000000
                with Image.open(io.BytesIO(raw)) as f:
                    f.load()
                    assert f.format in ("JPEG","PNG")
                    original=list(f.size)
                    img=ImageOps.exif_transpose(f).convert("RGB")
                assert min(img.size)>=600
                sha=hashlib.sha256(raw).hexdigest()
                img.thumbnail((1700,1700),Image.Resampling.LANCZOS)
                b=io.BytesIO();img.save(b,"JPEG",quality=90,optimize=True)
                cleaned=b.getvalue()
                assert len(cleaned)>14000
                with Image.open(io.BytesIO(cleaned)) as check:check.verify()
                return cleaned,res.url,sha,original,list(img.size)
            except Exception as e:
                failures.append(str(e)[:130])
                time.sleep(1)
    raise RuntimeError("No image source for "+name+": "+str(failures))
def main():
    card=json.loads(CARD.read_text(encoding="utf-8"))
    assert card["scientific_name"]=="Euphorbia maculata"
    assert len(card["images"]) in (1,5)
    assert card["images"][0]["license"]=="CC BY-NC"
    assert card["images"][0]["file"]=="images/inat-91881491.jpg"
    if len(card["images"])==5:
        assert all((BASE/x["file"]).is_file() for x in card["images"])
        print("Already installed; preserving installed files");return
    session=requests.Session()
    session.headers["User-Agent"]="HaysBotanyLearner/1.0 (https://github.com/Crking92/Hays-County-Botany)"
    checked=[]
    for name,relative,creator,license,role in SOURCES:
        dest=BASE/relative
        assert not dest.exists()
        blob,download,sha,source_dimensions,published_dimensions=get(session,name)
        checked.append((name,relative,creator,license,role,blob,download,sha,source_dimensions,published_dimensions))
    for name,relative,creator,license,role,blob,download,sha,source_dimensions,published_dimensions in checked:
        dest=BASE/relative
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(blob)
        card["images"].append({
           "file":relative,"role":role,"creator":creator,"license":license,
           "license_url":"https://creativecommons.org/licenses/by-sa/4.0/" if license=="CC BY-SA 4.0" else "https://creativecommons.org/licenses/by/2.0/",
           "source_page":"https://commons.wikimedia.org/wiki/File:"+quote(name.replace(" ","_"),safe="._-()"),
           "source_platform":"Wikimedia Commons exact species file page",
           "downloaded_from":download,"source_sha256":sha,
           "original_image_dimensions":source_dimensions,
           "image_dimensions":published_dimensions,
           "public_reuse":"yes",
           "modifications":"Downscaled for GitHub Pages, re-encoded JPEG, EXIF stripped; morphology untouched. Educational arrow overlays only in site UI.",
           "anatomy_arrows":[],
           "photo_review":"Identified as Euphorbia maculata by Wikimedia source file with named creator and verified CC license; exact saved photograph needs manual visual arrow QA."
        })
    assert len(card["images"])==5
    card["curation_status"]["photo_metadata_count"]=5
    card["curation_status"]["photo_files_present"]=5
    card["curation_status"]["commons_licensed_gallery_installed"]="2026-10-20"
    card["learner_visual_status"]["image_count"]=5
    card["photo_note"]+=" Four original, public reusable exact-name Commons photos installed. Old noncommercial image remains a research record (not publicly reused); saved-pixel annotations pending."
    CARD.write_text(json.dumps(card,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps({"species":"Euphorbia maculata","review":"2026-10-20","photos":[{"source_page":"https://commons.wikimedia.org/wiki/File:"+quote(n.replace(" ","_"),safe="._-()"),"file":rel,"creator":c,"license":lic,"source_hash":sha,"original_size":og,"saved_size":sv} for n,rel,c,lic,_,_,_,sha,og,sv in checked],"legacy_noncommercial_photo":"Preserved source-only, NOT public reuse","photo_arrow_review":"pending direct JPEG pixel inspection","range_status":"No county nativity conclusions made"},indent=2)+"\n")
    print("PASS 4 exact-name CC BY/CC BY-SA image files installed, original NC photo left untouched.")
if __name__=="__main__":main()
