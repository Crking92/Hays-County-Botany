#!/usr/bin/env python3
"""Strict, provisional first-image check for Joey's Research Grade variety observation.
Kew accepts Thelesperma megapotamicum var. ambiguum, with Thelesperma ambiguum
as homotypic synonym. Do not alter native-range/taxonomy and do not install if source
no longer explicitly identifies THIS variety.
"""
import copy,csv,datetime,hashlib,io,json,pathlib,re,sys,urllib.parse
from PIL import Image,ImageOps
ROOT=pathlib.Path(".");sys.path.insert(0,str(ROOT.resolve()))
from scripts.joey_photo_quick_batch import get
ID="thelesperma-megapotamicum-var-ambiguum"
OBS="124681747"
CANON=ROOT/"content/taxa/Asteraceae/Thelesperma/thelesperma-megapotamicum-var-ambiguum/species.json"
REPORT=ROOT/"reports/joey-thelesperma-ambiguum-first-photo.json"
ALLOWED={"Thelesperma megapotamicum ambiguum","Thelesperma megapotamicum var. ambiguum"}
def science(obj):
    a=copy.deepcopy(obj)
    for k in ("images","photo_note","learner_visual_status"):a.pop(k,None)
    for k in ("photo_metadata_count","photo_files_present","joey_ambiguum_photo_date"):
        (a.get("curation_status") or {}).pop(k,None)
    return a
def csv_add(f,r):
    content=f.read_text(encoding="utf-8-sig") if f.exists() else ""
    read=csv.DictReader(io.StringIO(content));fields=list(read.fieldnames or []);items=list(read)
    for k in r:
        if k not in fields:fields.append(k)
    b=io.StringIO();wr=csv.DictWriter(b,fieldnames=fields,lineterminator="\n");wr.writeheader();wr.writerows(items+[r])
    f.write_text(b.getvalue(),encoding="utf-8")
def main():
    now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    report={"at":now,"id":ID,"observation_id":OBS,"status":"not_installed","reason":"","photos":[],"science_preserved":True}
    manifest=json.loads((ROOT/"data/manifest.json").read_text())
    if {r["id"]:r["path"] for r in manifest["species"]}.get(ID)!=str(CANON):
        report["reason"]="Not matching canonical manifest; no edit"
    claims=json.loads((ROOT/"workflow/work-claims.json").read_text())
    if not report["reason"] and any(ID in (c.get("taxa") or []) and c.get("status") in ("active","queued","blocked") for c in claims["claims"]):
        report["reason"]="Active claim; no edit"
    for x in (ROOT/"curation-inbox").rglob("species.json"):
        try:
            if json.loads(x.read_text()).get("id")==ID:report["reason"]="In curation inbox; no edit"
        except (ValueError,OSError):pass
    sp=json.loads(CANON.read_text(encoding="utf-8"))
    if not report["reason"] and ((sp.get("images") or []) or (CANON.parent/"images").exists() and any((CANON.parent/"images").iterdir())):
        report["reason"]="Gallery/file already exists; no edit"
    if not report["reason"]:
        try:
            data=json.loads(get("https://api.inaturalist.org/v1/observations/"+OBS))
            obs=data["results"][0]
            tax=obs.get("taxon") or {}
            report["live_taxon"]={"name":tax.get("name"),"rank":tax.get("rank"),"quality_grade":obs.get("quality_grade"),"observer":(obs.get("user") or {}).get("login")}
            if (obs.get("user") or {}).get("login")!="joeysantore":raise ValueError("Not Joey observation")
            if tax.get("name") not in ALLOWED or tax.get("rank") not in ("variety","subspecies","subspecies_group"):
                raise ValueError("Not an explicitly identified variety: "+str(report["live_taxon"]))
            if obs.get("quality_grade")!="research":raise ValueError("Observation not Research Grade")
            valid=[]
            for p in obs.get("photos") or []:
                if p.get("license_code")!="cc-by-nc":continue
                credit=p.get("attribution") or ""
                if not any(w in credit.lower() for w in ("joey santore","joseph santore","joeysantore")):continue
                url=p.get("url") or ""
                parsed=urllib.parse.urlparse(url)
                if parsed.scheme!="https" or parsed.hostname not in ("static.inaturalist.org","inaturalist-open-data.s3.amazonaws.com","inaturalist-open-data.s3.us-east-1.amazonaws.com"):continue
                if not re.search(r"/(?:square|thumb|small|medium|large|original)\.(?:jpg|jpeg|png|webp)$",parsed.path,re.I):continue
                url=re.sub(r"/(?:square|thumb|small|medium|large|original)\.(jpg|jpeg|png|webp)$",lambda m:"/large."+m.group(1).lower(),url,flags=re.I)
                raw=get(url)
                with Image.open(io.BytesIO(raw)) as img:
                    img.load();rgb=ImageOps.exif_transpose(img).convert("RGB")
                if min(rgb.size)<400 or max(rgb.size)<740:continue
                rgb.thumbnail((1600,1600),Image.Resampling.LANCZOS)
                buf=io.BytesIO();rgb.save(buf,format="JPEG",quality=90,optimize=True,progressive=True)
                if len(buf.getvalue())<16000:continue
                valid.append((p,url,credit,buf.getvalue(),list(rgb.size)))
            if not valid:raise ValueError("No source-licensed Joey photograph available")
            p,url,credit,binary,dim=valid[0]
            before=science(sp)
            photo_id=str(p["id"]);filename="joey-inat-"+photo_id+".jpg"
            dest=CANON.parent/"images"/filename
            dest.parent.mkdir(parents=True,exist_ok=True)
            if dest.exists():raise ValueError("Existing media file, refused overwrite")
            dest.write_bytes(binary)
            image={"file":"images/"+filename,"role":"First-pass photo of Kew-mapped variety concept; floral diagnostic features unverified",
                   "creator":"Joey Santore","license":"CC BY-NC 4.0","license_url":"https://creativecommons.org/licenses/by-nc/4.0/",
                   "source_platform":"iNaturalist","source_page":"https://www.inaturalist.org/photos/"+photo_id,
                   "observation_url":"https://www.inaturalist.org/observations/"+OBS,"observation_id":OBS,"photo_id":photo_id,
                   "source_recorded_photo_attribution_at_download":credit,"source_recorded_photo_license_at_download":"cc-by-nc",
                   "downloaded_from":url,"image_dimensions":dim,"study_use":"noncommercial education","public_reuse":"no commercial reuse; retain Joey attribution",
                   "photo_review":"iNaturalist Research Grade at exact variety rank, mapped to Kew accepted Thelesperma megapotamicum var. ambiguum; visual field diagnostic confirmation pending"}
            sp["images"]=[image]
            status=sp.setdefault("curation_status",{})
            status["photo_metadata_count"]=1;status["photo_files_present"]=1;status["joey_ambiguum_photo_date"]=now[:10]
            sp["learner_visual_status"]={"status":"provisional_learner_ready","mode":"learner_fast_fill","image_count":1,
                                         "note":"Exact infraspecific iNaturalist taxon concept photo installed; flower/morphology differences not yet verified",
                                         "missing_diagnostic_views":["Corroborate flowers, foliage, and species look-alikes"]}
            sp["photo_note"]=((sp.get("photo_note") or "")+" Joey Santore noncommercial CC BY-NC first photograph provisionally installed from exact variety-level observation; do not use to infer range.").strip()
            if science(sp)!=before:raise AssertionError("Science fields altered")
            csv_add(CANON.parent/"image-sources.csv",{"file_name":filename,"role":image["role"],"creator":"Joey Santore",
                "license":"CC BY-NC 4.0","license_url":image["license_url"],"source_page":image["source_page"],"direct_url":url,
                "observation_id":OBS,"photo_id":photo_id,"study_use":"yes — noncommercial educational",
                "public_reuse":"no commercial reuse","modifications":"Resized JPG with EXIF removed"})
            with (CANON.parent/"SOURCES.txt").open("a",encoding="utf-8") as f:
                f.write("\nTHELESPERMA AMBIGUUM VARIETY FIRST PHOTO "+now+"\nJoey Santore CC BY-NC 4.0 "+image["source_page"]+"\n"+image["observation_url"]+"\nKew accepted name: https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:250998-2\nInfraspecific matching based on live iNaturalist taxon/rank. Morphological diagnostic verification pending. No range inference.\n")
            CANON.write_text(json.dumps(sp,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
            from scripts.curation_pipeline import rebuild_photo_fast_fill_queue
            rebuild_photo_fast_fill_queue()
            report.update(status="installed_provisional",reason="Exact variety taxon+Research Grade+license verified",photos=[{"photo_id":photo_id,"bytes":len(binary),"sha256":hashlib.sha256(binary).hexdigest(),"dimensions":dim}],image_count=1)
        except Exception as e:
            report["reason"]=str(e)[:300]
            # If an unexpected error occurs after writing image bytes, fail loudly for action QA.
            if CANON.parent.joinpath("images").is_dir() and list(CANON.parent.joinpath("images").glob("joey-inat-*")) and report["status"]!="installed_provisional":
                raise
    REPORT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
