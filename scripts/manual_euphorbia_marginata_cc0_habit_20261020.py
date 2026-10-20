#!/usr/bin/env python3
"""Install single public-domain exact-species marginata field-habit photograph.
Source: Wikimedia Commons CC0, Cbaile19, photographed Pennsylvania 2015.
Download and image validation must succeed before altering canonical species data.
"""
import hashlib, io, json, time
from pathlib import Path
from urllib.parse import quote
import requests
from PIL import Image, ImageOps

BASE=Path("content/taxa/Euphorbiaceae/Euphorbia/euphorbia-marginata")
CARD=BASE/"species.json"
NAME="Euphorbia marginata, 2015-07-22, Beechview, 01.jpg"
FILE="images/04-cbaile19-marginata-whole-habit-cc0.jpg"
DEST=BASE/FILE
SOURCE="https://commons.wikimedia.org/wiki/File:"+quote(NAME.replace(" ","_"),safe="(),_-")
CC0="https://creativecommons.org/publicdomain/zero/1.0/"
REPORT=Path("reports/euphorbia-marginata-cc0-habit-install-20261020.json")

def retrieve():
    fn=NAME.replace(" ","_")
    md=hashlib.md5(fn.encode("utf-8")).hexdigest()
    original="https://upload.wikimedia.org/wikipedia/commons/"+md[0]+"/"+md[:2]+"/"+quote(fn,safe="(),_-")
    redirect="https://commons.wikimedia.org/wiki/Special:Redirect/file/"+quote(fn,safe="(),_-")+"?width=1600"
    sess=requests.Session()
    sess.headers["User-Agent"]="HaysCountyBotanyFieldPhotos/1.0 (https://github.com/Crking92/Hays-County-Botany)"
    errors=[]
    for url in [redirect,original]:
        for attempt in range(2):
            try:
                response=sess.get(url,timeout=60)
                response.raise_for_status()
                data=response.content
                assert 30000<len(data)<14000000
                with Image.open(io.BytesIO(data)) as im:
                    im.load()
                    assert im.format in ("JPEG","PNG")
                    src_dims=list(im.size)
                    result=ImageOps.exif_transpose(im).convert("RGB")
                assert min(result.size)>=700
                sha=hashlib.sha256(data).hexdigest()
                result.thumbnail((1750,1750),Image.Resampling.LANCZOS)
                out=io.BytesIO()
                result.save(out,"JPEG",quality=92,optimize=True)
                rendered=out.getvalue()
                assert len(rendered)>30000
                with Image.open(io.BytesIO(rendered)) as check:check.verify()
                return rendered,sha,src_dims,list(result.size),response.url
            except Exception as err:
                errors.append([url,str(err)[:120]])
                time.sleep(2)
    raise RuntimeError("No verified public-source JPEG found. "+repr(errors))
def main():
    j=json.loads(CARD.read_text(encoding="utf-8"))
    assert j["scientific_name"]=="Euphorbia marginata"
    assert j["project_inclusion"]["target_zone_status"]=="PASS"
    assert j["field_id_finalization"]["stage"]=="PASS_IN_PROGRESS"
    if any(x["file"]==FILE for x in j["images"]):
        assert DEST.is_file() and DEST.stat().st_size>30000
        print("Already installed, no changes");return
    assert len(j["images"])==3 and not DEST.exists()
    assert j["images"][2]["license"]=="CC BY-NC 4.0"
    rendered,sha,srcdim,resdim,url=retrieve()
    DEST.parent.mkdir(parents=True,exist_ok=True)
    DEST.write_bytes(rendered)
    j["images"].append({
       "file":FILE,
       "role":"WHOLE-PLANT recognition: externally photographed complete Euphorbia marginata habit in Pennsylvania, not Hays County provenance; photo only proves plant growth form.",
       "creator":"Cbaile19 (Wikimedia Commons)",
       "license":"CC0 1.0",
       "license_url":CC0,
       "source_page":SOURCE,
       "source_platform":"Wikimedia Commons — individually licensed exact species",
       "downloaded_from":url,
       "public_reuse":"yes",
       "study_use":"public botanical education, optional photographer attribution",
       "original_image_sha256":sha,
       "original_image_dimensions":srcdim,
       "image_dimensions":resdim,
       "modifications":"EXIF stripped and JPEG resized; no anatomical arrows have been added yet",
       "anatomy_arrows":"none; saved-pixel manual inspection pending",
       "photo_review":"Original Commons source labels E. marginata photographed in Pennsylvania and explicitly publishes under CC0. Whole-habit teaching only pending image-pixel review."
    })
    j["curation_status"]["photo_metadata_count"]=4
    j["curation_status"]["photo_files_present"]=4
    j["curation_status"]["cc0_whole_plant_installed"]="2026-10-20"
    j["learner_visual_status"]["image_count"]=4
    j["learner_visual_status"]["note"]+=" CC0 exact-species full-habit source is physically installed, pending arrow pixel QA."
    CARD.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps({
     "species":j["scientific_name"],"source":SOURCE,"creator":"Cbaile19",
     "source_license":"CC0 1.0","rights_url":CC0,
     "saved_file":FILE,"sha256_source":sha,"source_url":url,
     "source_dimensions":srcdim,"render_dimensions":resdim,
     "existing_joey_cc_by_nc_unchanged":True,
     "annotated_arrows_added":0
    },indent=2)+"\n",encoding="utf-8")
    print("PASS CC0 E. marginata true original habit photo installed:",FILE)
if __name__=="__main__":main()
