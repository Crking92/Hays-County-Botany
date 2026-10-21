#!/usr/bin/env python3
"""Source license-checked original Euphorbia eriantha research-grade iNaturalist photos.

Existing source-verified single photo is kept. Only research-grade exact
accepted-taxon observations with PHOTO-specific CC public web licences may
contribute. No plant common name searches, ND/no-license or misleading macros.
"""
from pathlib import Path
from urllib.parse import urlparse
import csv, hashlib, io, json, time, re
import requests
from PIL import Image, ImageOps

BASE=Path("content/taxa/Euphorbiaceae/Euphorbia/euphorbia-eriantha")
CARD=BASE/"species.json"
CSV=BASE/"image-sources.csv"
REPORT=Path("reports/euphorbia-eriantha-photo-intake-20261021.json")
API="https://api.inaturalist.org/v1/observations"
TAXON=None  # Resolve from the exact accepted name at execution
LICENCES={
"cc0":("CC0 1.0","https://creativecommons.org/publicdomain/zero/1.0/"),
"cc-by":("CC BY 4.0","https://creativecommons.org/licenses/by/4.0/"),
"cc-by-sa":("CC BY-SA 4.0","https://creativecommons.org/licenses/by-sa/4.0/"),
"cc-by-nc":("CC BY-NC 4.0","https://creativecommons.org/licenses/by-nc/4.0/"),
"cc-by-nc-sa":("CC BY-NC-SA 4.0","https://creativecommons.org/licenses/by-nc-sa/4.0/")
}
def fetch_image(session,photo):
    small=photo.get("url","")
    assert small.startswith("https://"),small
    # iNat's photo response provides a signed original domain/photo id; replace
    # only its documented photo size segment, never its domain/id/extension.
    url=re.sub(r"/(?:square|small|medium|large|thumb)\.", "/original.",small)
    if url==small:
        url=re.sub(r"/(?:square|small|medium|large|thumb)/", "/original/",small)
    for candidate in (url, re.sub(r"/original\.", "/large.",url)):
        try:
            r=session.get(candidate,timeout=50)
            r.raise_for_status()
            raw=r.content
            assert 16000<len(raw)<20000000
            with Image.open(io.BytesIO(raw)) as i:
                i.load()
                assert i.format in ("JPEG","PNG")
                dims=list(i.size)
                im=ImageOps.exif_transpose(i).convert("RGB")
            assert min(im.size)>=500,dims
            im.thumbnail((1800,1800),Image.Resampling.LANCZOS)
            out=io.BytesIO();im.save(out,"JPEG",quality=90,optimize=True)
            data=out.getvalue()
            assert len(data)>16000
            with Image.open(io.BytesIO(data)) as check:check.verify()
            return data,{"image_source_sha256":hashlib.sha256(raw).hexdigest(),
                "original_dimensions":dims,"image_dimensions":list(im.size),
                "downloaded_from":r.url}
        except Exception as e:
            last=str(e)[:150]
    raise RuntimeError("No validated image for photo id "+str(photo["id"])+": "+last)

def main():
    j=json.loads(CARD.read_text(encoding="utf-8"))
    assert j["scientific_name"]=="Euphorbia eriantha"
    assert j["field_id_finalization"]["stage"]=="PASS_IN_PROGRESS"
    assert j["images"][0]["file"]=="images/inat-181384310.jpg" and j["images"][0]["license"]=="CC BY"
    if len(j["images"])>1:
        print("Existing new photos in canonical card; no duplicate intake");return
    session=requests.Session()
    session.headers["User-Agent"]="HaysBotanyPhotoReview/1.0 (https://github.com/Crking92/Hays-County-Botany)"
    resp_taxon=session.get("https://api.inaturalist.org/v1/taxa/autocomplete",params={"q":"Euphorbia eriantha","per_page":30},timeout=50)
    resp_taxon.raise_for_status()
    matches=[t for t in resp_taxon.json().get("results",[]) if t.get("name")=="Euphorbia eriantha" and t.get("rank")=="species" and t.get("is_active")]
    assert len(matches)==1,("EXACT_TAXON_HOLD",matches)
    taxon_id=matches[0]["id"]
    print("Matched exact species taxon ID",taxon_id)
    params={"taxon_id":taxon_id,"quality_grade":"research","photos":"true",
      "per_page":100,"order_by":"observed_on","order":"desc","page":1}
    response=session.get(API,params=params,timeout=70)
    response.raise_for_status()
    result=response.json()
    assert isinstance(result.get("results"),list)
    print("Exact species iNaturalist research observation count:",result.get("total_results"))
    eligible=[]
    seen_obs=set()
    for obs in result["results"]:
        taxon=obs.get("taxon") or {}
        if taxon.get("id")!=taxon_id or taxon.get("name")!="Euphorbia eriantha":
            continue
        if obs.get("quality_grade")!="research":continue
        if obs.get("id")==0:continue # no old observation excluded beyond matching existing photo id
        if obs["id"] in seen_obs:continue
        seen_obs.add(obs["id"])
        for ph in obs.get("photos",[]):
            if ph.get("id")==181384310:continue
            code=(ph.get("license_code") or "").lower()
            if code not in LICENCES:continue
            creator=ph.get("attribution") or ph.get("user",{}).get("login") or ""
            if not creator.strip():continue
            eligible.append((obs,ph,code,creator))
            break  # one candidate per observation before considering a second
    print("Source-licensed exact-species separate-observation candidates:",len(eligible))
    # Keep bounded; preview image still needs human anatomical QA.
    selected=[]
    for obs,ph,code,creator in eligible:
        if len(selected)>=4:break
        dest=BASE/("images/inat-"+str(ph["id"])+"-review.jpg")
        if dest.exists():continue
        try:
            data,meta=fetch_image(session,ph)
        except Exception as e:
            print("Photo candidate skipped",ph["id"],str(e)[:150]);continue
        selected.append((obs,ph,code,creator,meta,dest,data))
    print("Real original reviewed-source photo downloads:",len(selected))
    if not selected:
        REPORT.parent.mkdir(parents=True,exist_ok=True)
        REPORT.write_text(json.dumps({"species":"Euphorbia eriantha","status":"NO_NEW_VERIFIABLE_LICENCED_PHOTO","date":"2026-10-21",
          "research_grade_total":result.get("total_results"),"source_photo_candidates":len(eligible),
          "note":"Original Eric Knight CC BY photo unchanged. No made-up extra gallery count. Manual external search or photographer submissions needed."},indent=2)+"\n")
        return
    for obs,ph,code,creator,meta,dest,data in selected:
        dest.write_bytes(data)
        lic,url=LICENCES[code]
        j["images"].append({
          "file":"images/"+dest.name,
          "role":"Exact taxon research-grade iNaturalist supplementary field view; anatomy role PENDING manual saved-pixel inspection",
          "creator":creator,
          "license":lic,"license_url":url,
          "source_page":"https://www.inaturalist.org/photos/"+str(ph["id"]),
          "observation_url":"https://www.inaturalist.org/observations/"+str(obs["id"]),
          "observation_id":obs["id"],"photo_id":ph["id"],
          "source_platform":"iNaturalist API exact accepted species; individual photo-level licence",
          "study_use":"Botanical education","public_reuse":"yes",
          "public_site_use_scope":"noncommercial-only" if "-nc" in code else "Creative Commons terms as stated",
          "modifications":"Source original resized, EXIF stripped, JPEG recompression; no anatomical edits to photo bytes",
          "photo_review":"OBSERVED identity exact species at research grade and PHOTO license independently verified by iNaturalist; downloaded original JPEG checked. Diagnostic structures and arrow placement NOT yet visually assessed.",
          "anatomy_arrows":[],**meta
        })
    j["curation_status"].update({"photo_metadata_count":len(j["images"]),"photo_files_present":len(j["images"]),
       "photo_source_checked":True,"new_photo_source_verified_on":"2026-10-21"})
    j["learner_visual_status"].update({"image_count":len(j["images"]),
      "note":str(len(selected))+" supplementary separately licensed real photos added from exact research-grade taxon; photo-specific anatomy arrow QA pending, scientific plant key already drafted. No Hays native claim."})
    j["field_id_finalization"]["new_photo_source_count"]=len(selected)
    j["field_id_finalization"]["photo_review"]="Added exact-scientific-taxon research-grade licensed original JPEGs from independent iNat observations. No fine-anatomy assertions until each actual binary is manually inspected."
    CARD.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n")
    with CSV.open(newline="",encoding="utf-8") as f:
        reader=csv.DictReader(f);cols=reader.fieldnames;rows=list(reader)
    for obs,ph,code,creator,meta,dest,data in selected:
        license,_=LICENCES[code]
        values={"file_name":dest.name,"role":"Exact taxon candidate; structure verification pending","creator":creator,
           "license":license,"source_page":"https://www.inaturalist.org/photos/"+str(ph["id"]),
           "direct_url":meta["downloaded_from"],"study_use":"Noncommercial educational learner",
           "public_reuse":"yes with original license conditions","observation_id":str(obs["id"]),"photo_id":str(ph["id"])}
        rows.append({c:values.get(c,"") for c in cols})
    with CSV.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=cols,lineterminator="\n");writer.writeheader();writer.writerows(rows)
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps({"species":"Euphorbia eriantha","date":"2026-10-21",
      "research_grade_observations_returned":result.get("total_results"),"photo_candidates":len(eligible),
      "installed":[{"photo_id":ph["id"],"observation_id":obs["id"],"creator":creator,"license":LICENCES[code][0],
                    "path":str(dest),"sha":meta["image_source_sha256"]} for obs,ph,code,creator,meta,dest,data in selected],
      "photo_anatomy_status":"PENDING manual saved-JPEG pixel examination",
      "existing_original_photo_preserved":True,"county_nativeness":"unreviewed"},indent=2)+"\n")
    print("PASS:",len(selected),"licensed photos added, total",len(j["images"]))
if __name__=="__main__":main()
