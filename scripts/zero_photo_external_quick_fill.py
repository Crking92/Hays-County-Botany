#!/usr/bin/env python3
"""One-photo breadth-first Central Texas learner fill from external CC-licensed iNaturalist.
Only true-zero canonical species; preserve taxonomy/range/scientific data and all claims.
"""
import argparse,collections,copy,csv,datetime as dt,hashlib,io,json,pathlib,re,sys,time,urllib.error,urllib.parse,urllib.request
from PIL import Image,ImageOps
ROOT=pathlib.Path(".")
sys.path.insert(0,str(ROOT.resolve()))
API="https://api.inaturalist.org/v1/observations"
HEAD={"User-Agent":"HaysBotany-ZeroPhoto-SourceFastFill/1.0 (Crking92/Hays-County-Botany)","Accept":"application/json,image/*"}
LICENSE={"cc0":("CC0 1.0","https://creativecommons.org/publicdomain/zero/1.0/"),
         "cc-by":("CC BY 4.0","https://creativecommons.org/licenses/by/4.0/"),
         "cc-by-sa":("CC BY-SA 4.0","https://creativecommons.org/licenses/by-sa/4.0/")}
HOSTS={"static.inaturalist.org","inaturalist-open-data.s3.amazonaws.com","inaturalist-open-data.s3.us-east-1.amazonaws.com"}
QUEUE=ROOT/"reports/photo-fast-fill-zero-queue.json"
REPORT=ROOT/"reports/external-first-photo-batch-latest.json"
def fetch(url,limit=14000000):
    for attempt in range(3):
        try:
            req=urllib.request.Request(url,headers=HEAD)
            with urllib.request.urlopen(req,timeout=27) as r:data=r.read(limit+1)
            if len(data)>limit:raise ValueError("large source skipped")
            return data
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as e:
            if isinstance(e,urllib.error.HTTPError) and e.code not in (429,500,502,503,504):raise
            if attempt==2:raise
            time.sleep(2**attempt)
def observation_candidates(name,texas=True):
    param={"taxon_name":name,"quality_grade":"research","photos":"true",
           "photo_license":"cc0,cc-by,cc-by-sa","per_page":15,
           "order_by":"observed_on","order":"desc"}
    if texas:param["place_id"]=18
    url=API+"?"+urllib.parse.urlencode(param)
    data=json.loads(fetch(url))
    return [o for o in data.get("results",[]) if
            o.get("quality_grade")=="research" and
            (o.get("taxon") or {}).get("name")==name]
def photo_image(p):
    url=p.get("url") or ""
    parsed=urllib.parse.urlparse(url)
    if parsed.scheme!="https" or parsed.hostname not in HOSTS:raise ValueError("untrusted image host")
    if not re.search(r"/(?:square|thumb|small|medium|large|original)\.(?:jpg|jpeg|png|webp)$",parsed.path,re.I):
        raise ValueError("unknown image format")
    url=re.sub(r"/(?:square|thumb|small|medium|large|original)\.(jpg|jpeg|png|webp)$",
               lambda m:"/large."+m.group(1).lower(),url,flags=re.I)
    raw=fetch(url)
    with Image.open(io.BytesIO(raw)) as im:
        im.load(); rgb=ImageOps.exif_transpose(im).convert("RGB")
    if min(rgb.size)<420 or max(rgb.size)<740:raise ValueError("too low resolution")
    rgb.thumbnail((1500,1500),Image.Resampling.LANCZOS)
    out=io.BytesIO();rgb.save(out,format="JPEG",quality=89,optimize=True,progressive=True)
    if len(out.getvalue())<17000:raise ValueError("tiny jpeg")
    return out.getvalue(),url,list(rgb.size)
def license_creator(photo):
    code=photo.get("license_code")
    if code not in LICENSE:return None
    original=photo.get("attribution") or ""
    if code!="cc0" and len(original.strip())<8:return None
    creator=re.sub(r"^\s*(?:\(c\)|©)\s*","",original,flags=re.I)
    creator=re.split(r",?\s+some rights reserved",creator,maxsplit=1,flags=re.I)[0]
    if code=="cc0" and (not creator or creator.lower()=="no rights reserved"):
        creator="iNaturalist photo contributor (CC0)"
    if len(creator)>130:creator=creator[:130]
    return code,creator,original
def add_csv(path,new):
    t=path.read_text(encoding="utf-8-sig") if path.exists() else ""
    r=csv.DictReader(io.StringIO(t));columns=list(r.fieldnames or []);old=list(r)
    for key in new:
        if key not in columns:columns.append(key)
    if not any(str(v.get("photo_id"))==str(new["photo_id"]) for v in old):old.append(new)
    buff=io.StringIO();w=csv.DictWriter(buff,fieldnames=columns,lineterminator="\n");w.writeheader();w.writerows(old)
    path.write_text(buff.getvalue(),encoding="utf-8")
def science(species):
    obj=copy.deepcopy(species)
    for k in ("images","photo_note","learner_visual_status"):obj.pop(k,None)
    if isinstance(obj.get("curation_status"),dict):
        for k in ("photo_metadata_count","photo_files_present","external_first_photo_install"):
            obj["curation_status"].pop(k,None)
    return obj
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--batch-size",type=int,default=8)
    p.add_argument("--max-attempts",type=int,default=22,help="Limit searches, not installed count")
    args=p.parse_args()
    if not (1<=args.batch_size<=12 and args.batch_size<=args.max_attempts<=40):raise ValueError("Batch cap")
    manifest=json.loads((ROOT/"data/manifest.json").read_text(encoding="utf-8"))
    canonical={t["id"]:t["path"] for t in manifest["species"]}
    queue=json.loads(QUEUE.read_text(encoding="utf-8"))
    claimdata=json.loads((ROOT/"workflow/work-claims.json").read_text(encoding="utf-8"))
    busy=set()
    for cl in claimdata.get("claims",[]):
        if cl.get("status") in ("active","queued","blocked"):
            busy.update(cl.get("taxa") or [])
    inbox=set()
    for f in (ROOT/"curation-inbox").rglob("species.json"):
        try: inbox.add(json.loads(f.read_text(encoding="utf-8"))["id"])
        except (ValueError,KeyError,OSError):pass
    report={"generated_at_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
            "batch_kind":"one first-pass photo per exact species from licensed non-Joey or other public photo sources",
            "requested_species":args.batch_size,"attempts":0,"installed":[],"skipped":[],
            "source_policy":"iNaturalist Research Grade exact taxon, individual photo CC0/CC BY/CC BY-SA, public source, attribution recorded; verification of photographed morphology pending",
            "scientific_data_unchanged":True}
    prepared=[]
    for item in queue["items"]:
        if len(prepared)>=args.batch_size or report["attempts"]>=args.max_attempts:break
        sid=item["id"];pathval=canonical.get(sid)
        if not pathval:continue
        if sid in busy or sid in inbox or item.get("in_curation_inbox") or item.get("active_claims"):
            report["skipped"].append({"id":sid,"reason":"busy claim/inbox"});continue
        path=ROOT/pathval;sp=json.loads(path.read_text(encoding="utf-8"))
        if sp.get("id")!=sid or (sp.get("images") or []):
            report["skipped"].append({"id":sid,"reason":"not currently true-zero"});continue
        imdir=path.parent/"images"
        if imdir.exists() and any(imdir.iterdir()):
            report["skipped"].append({"id":sid,"reason":"physical photo exists; do not overwrite"});continue
        if not (path.parent/"SOURCES.txt").is_file():
            report["skipped"].append({"id":sid,"reason":"missing provenance file"});continue
        name=sp.get("scientific_name") or ""
        if not name:continue
        report["attempts"]+=1
        picked=None
        for texas in (True,False):
            try: observations=observation_candidates(name,texas)
            except Exception as ex:
                report["skipped"].append({"id":sid,"reason":"observation search error: "+str(ex)[:95]})
                continue
            for obs in observations[:12]:
                for photo in (obs.get("photos") or [])[:5]:
                    rights=license_creator(photo)
                    if not rights:continue
                    code,creator,sourceattr=rights
                    # photo attribution is authoritative; observer and photographer may differ
                    if code!="cc0" and ("all rights reserved" in sourceattr.lower()):continue
                    try:binary,url,dimensions=photo_image(photo)
                    except Exception:continue
                    picked=(obs,photo,rights,binary,url,dimensions)
                    break
                if picked:break
            if picked:break
        if not picked:
            report["skipped"].append({"id":sid,"reason":"no immediately valid research-grade exact-taxon CC photo"});continue
        prepared.append((sid,path,sp,picked))
        print("READY",sid,picked[1]["id"],flush=True)
    # No canonical edits before all selected media pass the source and pixel gates.
    for sid,path,sp,picked in prepared:
        obs,photo,rights,binary,url,dimensions=picked
        code,creator,attribution=rights; lic,urllic=LICENSE[code]
        pid=str(photo["id"]);oid=str(obs["id"])
        filename="inat-first-"+pid+".jpg"
        dest=path.parent/"images"/filename
        if dest.exists() or (sp.get("images") or []):raise RuntimeError("source/gallery collision")
        before=science(sp);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(binary)
        public="yes, no attribution legally required (CC0)" if code=="cc0" else ("yes, attribution required" if code=="cc-by" else "yes, attribution and ShareAlike terms apply")
        record={"file":"images/"+filename,"role":"Exact-taxon first-pass recognition photo; visible diagnostic parts not yet personally verified",
                "creator":creator,"license":lic,"license_url":urllic,
                "source_platform":"iNaturalist","source_page":"https://www.inaturalist.org/photos/"+pid,
                "observation_url":"https://www.inaturalist.org/observations/"+oid,
                "photo_id":pid,"observation_id":oid,
                "source_recorded_photo_license_at_download":code,
                "source_recorded_photo_attribution_at_download":attribution,"downloaded_from":url,
                "image_dimensions":dimensions,"study_use":"yes","public_reuse":public,
                "photo_review":"Automated source/license/Research Grade/identity match and image-byte verification; provisional, anatomical features unverified",
                "anatomy_arrows":"none; targets unverified"}
        sp["images"]=[record]
        s=sp.setdefault("curation_status",{})
        s["photo_metadata_count"]=1;s["photo_files_present"]=1;s["external_first_photo_install"]=report["generated_at_utc"][:10]
        lv=sp.setdefault("learner_visual_status",{})
        lv["status"]="provisional_learner_ready";lv["mode"]="learner_fast_fill";lv["image_count"]=1
        lv["note"]="One exact-taxon Research Grade photo provisionally installed; morphological teaching views need visual review."
        lv["missing_diagnostic_views"]=["Species-diagnostic macros and visually checked morphology"]
        sp["photo_note"]=((sp.get("photo_note") or "")+" First-pass CC-licensed observation photo installed; precise anatomy and image quality require visual review.").strip()
        if science(sp)!=before:raise AssertionError("Science modified: "+sid)
        add_csv(path.parent/"image-sources.csv",{
            "file_name":filename,"role":record["role"],"creator":creator,"license":lic,"license_url":urllic,
            "source_page":record["source_page"],"direct_url":url,"observation_id":oid,"photo_id":pid,
            "study_use":"yes","public_reuse":public,"modifications":"resized and converted to JPG; EXIF/location stripped"})
        with (path.parent/"SOURCES.txt").open("a",encoding="utf-8") as f:
            f.write("\nEXTERNAL FIRST-PHOTO SOURCE "+report["generated_at_utc"]+"\n"+creator+"; "+lic+"; "+urllic+"\n"+record["source_page"]+" | "+record["observation_url"]+"\nImage saved provisionally from exact-taxon Research Grade observation; photographic diagnostic ID unreviewed. EXIF removed.\n")
        path.write_text(json.dumps(sp,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        report["installed"].append({"id":sid,"name":sp["scientific_name"],"photo_id":pid,
                                    "observation_id":oid,"file":str(dest),"bytes":len(binary),
                                    "sha256":hashlib.sha256(binary).hexdigest(),
                                    "creator":creator,"license":lic,"dimensions":dimensions})
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    if report["installed"]:
        from scripts.curation_pipeline import rebuild_photo_fast_fill_queue
        rebuild_photo_fast_fill_queue()
    print(json.dumps({"attempts":report["attempts"],"installed":report["installed"],
                      "skipped":report["skipped"]},indent=2),flush=True)
if __name__=="__main__":main()
