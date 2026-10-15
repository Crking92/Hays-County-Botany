#!/usr/bin/env python3
"""Install a small repeatable batch of Joey Santore photos.
Modes: zero (empty galleries), thin (1-2 photos), targeted (listed species).
One image per taxon by default; images are provisional, NOT diagnostic verified.
"""
import argparse, collections, copy, csv, datetime, hashlib, io, json, pathlib, re, sys, time, urllib.parse, urllib.request
from PIL import Image,ImageOps,UnidentifiedImageError

ROOT=pathlib.Path(".")
sys.path.insert(0,str(ROOT.resolve()))
CATALOG=ROOT/"workflow/joey-inat-photo-inventory/photo-candidates.csv"
MANIFEST=ROOT/"data/manifest.json"
CLAIMS=ROOT/"workflow/work-claims.json"
REPORT=ROOT/"reports/joey-photo-batch-latest.json"
UA={"User-Agent":"HaysBotany-JoeyPhotoInstaller/1.0","Accept":"application/json,image/*"}
TRUSTED={"static.inaturalist.org","inaturalist-open-data.s3.amazonaws.com","inaturalist-open-data.s3.us-east-1.amazonaws.com"}
RIGHTS="https://creativecommons.org/licenses/by-nc/4.0/"
def get(url,maxbytes=14000000):
    last=None
    for n in range(3):
        try:
            req=urllib.request.Request(url,headers=UA)
            with urllib.request.urlopen(req,timeout=40) as f:
                binary=f.read(maxbytes+1)
            if len(binary)>maxbytes:raise ValueError("Oversize download")
            return binary
        except Exception as exc:
            last=exc
            if n<2:time.sleep(2*(n+1))
    raise last
def science(obj):
    x=copy.deepcopy(obj)
    for k in ("images","photo_note","learner_visual_status"):x.pop(k,None)
    if isinstance(x.get("curation_status"),dict):
        for k in ("photo_metadata_count","photo_files_present","joey_inat_photo_install"):x["curation_status"].pop(k,None)
    return x
def add_csv(path,new):
    original=path.read_text(encoding="utf-8-sig") if path.exists() else ""
    reader=csv.DictReader(io.StringIO(original)); cols=list(reader.fieldnames or []); old=list(reader)
    for k in new:
        if k not in cols:cols.append(k)
    if not any(str(x.get("photo_id"))==str(new["photo_id"]) for x in old):old.append(new)
    buf=io.StringIO();w=csv.DictWriter(buf,fieldnames=cols,lineterminator="\n")
    w.writeheader();w.writerows(old);path.write_text(buf.getvalue(),encoding="utf-8")
def existing_photo_ids(obj):
    found=set()
    for im in obj.get("images",[]):
        if im.get("photo_id"):found.add(str(im["photo_id"]))
        for k in ("source_page","photo_page","source_url"):
            match=re.search(r"/photos/(\d+)",str(im.get(k) or ""))
            if match:found.add(match.group(1))
    return found
def live_photo(row,sciname):
    oid=str(row["observation_id"]);pid=str(row["photo_id"])
    obj=json.loads(get("https://api.inaturalist.org/v1/observations/"+oid))
    a=obj.get("results") or []
    if len(a)!=1:raise ValueError("observation missing")
    obs=a[0]
    if (obs.get("user") or {}).get("login","").lower()!="joeysantore":raise ValueError("observer mismatch")
    if (obs.get("taxon") or {}).get("name")!=sciname:raise ValueError("taxon changed or wrong concept")
    if obs.get("quality_grade")!="research":raise ValueError("observation not Research Grade")
    pictures=[p for p in obs.get("photos",[]) if str(p.get("id"))==pid]
    if len(pictures)!=1:raise ValueError("photo no longer belongs to observation")
    p=pictures[0];credit=p.get("attribution") or ""
    if not any(c in credit.lower() for c in ("joey santore","joeysantore","joseph santore")):raise ValueError("photographer not Joey")
    if p.get("license_code")!="cc-by-nc":raise ValueError("rights changed: require CC BY-NC")
    url=p.get("url") or ""
    parsed=urllib.parse.urlparse(url)
    if parsed.scheme!="https" or parsed.hostname not in TRUSTED:raise ValueError("unexpected image host")
    if not re.search(r"/(?:square|thumb|small|medium|large|original)\.(jpg|jpeg|png|webp)$",url,re.I):
        raise ValueError("unexpected image URL")
    url=re.sub(r"/(?:square|thumb|small|medium|large|original)\.(jpg|jpeg|png|webp)$",
               lambda m:"/large."+m.group(1).lower(),url,flags=re.I)
    raw=get(url)
    with Image.open(io.BytesIO(raw)) as im:
        im.load()
        rgb=ImageOps.exif_transpose(im).convert("RGB")
    if min(rgb.size)<430 or max(rgb.size)<740:raise ValueError("image too small")
    rgb.thumbnail((1600,1600),Image.Resampling.LANCZOS)
    result=io.BytesIO();rgb.save(result,format="JPEG",quality=88,optimize=True,progressive=True)
    if len(result.getvalue())<16000:raise ValueError("implausibly small JPEG")
    return result.getvalue(),url,credit,list(rgb.size)
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=("zero","thin","targeted"),default="zero")
    p.add_argument("--batch-size",type=int,default=10)
    p.add_argument("--species",default="",help="Comma-separated IDs, required for targeted")
    p.add_argument("--photo-ids",default="",help="Optional comma-separated exact iNaturalist photo IDs")
    p.add_argument("--per-species",type=int,default=1)
    a=p.parse_args()
    if not 1<=a.batch_size<=12 or not 1<=a.per_species<=3:raise ValueError("Batch size cap 12; per-species cap 3")
    selected={x.strip() for x in a.species.split(",") if x.strip()}
    photo_filter={x.strip() for x in a.photo_ids.split(",") if x.strip()}
    if a.mode=="targeted" and not selected:raise ValueError("Targeted mode needs species IDs")
    manifest=json.loads(MANIFEST.read_text())
    refs={x["id"]:x["path"] for x in manifest["species"]}
    claims=json.loads(CLAIMS.read_text())
    busy=set()
    for cl in claims.get("claims",[]):
        if cl.get("status") in ("active","queued","blocked"):
            busy.update(cl.get("taxa") or [])
    inbox_ids=set()
    for ready in (ROOT/"curation-inbox").rglob("species.json"):
        try:inbox_ids.add(json.loads(ready.read_text())["id"])
        except (KeyError,ValueError,OSError):pass
    groups=collections.defaultdict(list)
    with CATALOG.open(newline="",encoding="utf-8-sig") as f:
        for x in csv.DictReader(f):
            if not x.get("canonical_id") or x.get("photographer_gate")!="joey_credited_candidate":continue
            if x.get("source_license")!="cc-by-nc" or x.get("taxon_rank")!="species":continue
            if x.get("quality_grade")!="research":continue
            if x["canonical_id"] not in refs:continue
            if selected and x["canonical_id"] not in selected:continue
            if photo_filter and x["photo_id"] not in photo_filter:continue
            groups[x["canonical_id"]].append(x)
    queue_path=ROOT/"reports/photo-fast-fill-zero-queue.json"
    if a.mode=="zero" and queue_path.is_file():
        queue=json.loads(queue_path.read_text())
        priority={x["id"]:i for i,x in enumerate(queue.get("items",[]))}
    else:priority={}
    targets=[];skips=[]
    for sid,candidates in groups.items():
        if sid in busy or sid in inbox_ids:
            skips.append({"id":sid,"reason":"busy claim or curation inbox"});continue
        path=ROOT/refs[sid]
        if not path.is_file():continue
        obj=json.loads(path.read_text(encoding="utf-8"))
        if obj.get("id")!=sid:continue
        gallery=obj.get("images") or []
        if a.mode=="zero" and gallery:continue
        if a.mode=="thin" and (len(gallery)<1 or len(gallery)>2):continue
        already=existing_photo_ids(obj)
        options=[v for v in candidates if v["photo_id"] not in already and v["scientific_name"]==obj.get("scientific_name")]
        # Prefer Research Grade exact-species photos from different observation IDs.
        options.sort(key=lambda v:(v.get("already_installed_photo_id")=="yes",v["observation_id"],v["photo_id"]))
        if not options:continue
        if a.mode=="zero" and path.parent.joinpath("images").exists():
            if list(path.parent.joinpath("images").glob("*")):
                skips.append({"id":sid,"reason":"physical images already exist"});continue
        if not (path.parent/"SOURCES.txt").exists():
            skips.append({"id":sid,"reason":"no source audit file"});continue
        targets.append((sid,path,obj,options))
    targets.sort(key=lambda t:(priority.get(t[0],99999),len(t[2].get("images") or []),-len(t[3]),t[0]))
    report={"run_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),"mode":a.mode,"requested_batch":a.batch_size,
            "eligible_matching_species":len(targets),"installed":[],"skipped":skips,"science_preserved":True,
            "note":"Noncommercial educational CC BY-NC images; source identification and image pixels machine-checked, anatomy not visually reviewed."}
    edits=[]
    for sid,path,obj,options in targets:
        if len(edits)>=a.batch_size:break
        if sid in busy or sid in inbox_ids:continue
        seen_obs={str(im.get("observation_id")) for im in (obj.get("images") or []) if im.get("observation_id")}
        candidates=sorted(options,key=lambda v:(str(v["observation_id"]) in seen_obs,v["observation_id"],v["photo_id"]))
        new=[]
        for row in candidates:
            if len(new)>=a.per_species:break
            if str(row["observation_id"]) in seen_obs and any(str(r["observation_id"])!=str(row["observation_id"]) for r in candidates):
                continue
            try:
                data,url,credit,dims=live_photo(row,obj["scientific_name"])
            except Exception as e:
                report["skipped"].append({"id":sid,"photo_id":row["photo_id"],"reason":str(e)[:150]})
                continue
            new.append((row,data,url,credit,dims))
            seen_obs.add(str(row["observation_id"]))
        if new:edits.append((sid,path,obj,new))
    # All source images downloaded and validated before any files change on disk.
    for sid,path,obj,new in edits:
        before=science(obj);gallery=copy.deepcopy(obj.get("images") or [])
        for row,data,url,credit,dims in new:
            filename="joey-inat-"+row["photo_id"]+".jpg"
            dest=path.parent/"images"/filename
            if dest.exists():raise ValueError("Unexpected existing image: "+str(dest))
            dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
            photo_url="https://www.inaturalist.org/photos/"+row["photo_id"]
            record={"file":"images/"+filename,
              "role":"First-pass whole-plant/recognition candidate; exact diagnostic structures not checked" if not gallery else "Additional exact-taxon view; anatomical role pending visual inspection",
              "creator":"Joey Santore","license":"CC BY-NC 4.0","license_url":RIGHTS,
              "source_platform":"iNaturalist","source_page":photo_url,
              "observation_url":row["observation_url"],"observation_id":row["observation_id"],
              "photo_id":row["photo_id"],"source_recorded_photo_license_at_download":"cc-by-nc",
              "source_recorded_photo_attribution_at_download":credit,"downloaded_from":url,
              "image_dimensions":dims,"study_use":"yes; noncommercial educational",
              "public_reuse":"review — only noncommercial use with credit; verify site context",
              "photo_review":"Research Grade exact-taxon source and readable pixels machine-checked; diagnostic view and ID require manual visual review",
              "anatomy_arrows":"none; not anatomically verified"}
            obj.setdefault("images",[]).append(record)
            add_csv(path.parent/"image-sources.csv",{"file_name":filename,"role":record["role"],"creator":"Joey Santore",
              "license":"CC BY-NC 4.0","license_url":RIGHTS,"source_page":photo_url,"direct_url":url,
              "observation_id":row["observation_id"],"photo_id":row["photo_id"],"study_use":"yes (noncommercial educational)",
              "public_reuse":record["public_reuse"],"review":"automated provisional","modifications":"resized JPG; metadata removed"})
            src=path.parent/"SOURCES.txt"
            with src.open("a",encoding="utf-8") as f:
                f.write("\nJOEY SANTORE PROVISIONAL FIRST-PASS PHOTO "+report["run_at"]+"\nPhoto: Joey Santore; CC BY-NC 4.0 ("+RIGHTS+")\n"+photo_url+"\n"+row["observation_url"]+"\nNoncommercial educational use with credit; actual diagnostic structure not yet verified. EXIF/GPS stripped.\n")
            report["installed"].append({"id":sid,"photo_id":row["photo_id"],"observation_id":row["observation_id"],
                                        "path":str(dest),"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest(),
                                        "dimensions":dims,"license":"CC BY-NC 4.0"})
        status=obj.setdefault("curation_status",{})
        status["photo_metadata_count"]=len(obj["images"])
        status["photo_files_present"]=sum(1 for im in obj["images"] if im.get("file") and (path.parent/im["file"]).is_file())
        status["joey_inat_photo_install"]=report["run_at"][:10]
        if not gallery:
            lv=obj.setdefault("learner_visual_status",{})
            lv["status"]="provisional_learner_ready"
            lv["mode"]="learner_fast_fill"
            lv["image_count"]=len(obj["images"])
            lv["note"]="At least one Joey Santore photograph installed; fine diagnostic verification pending."
            lv["missing_diagnostic_views"]=["Review close-ups of the diagnostic plant parts"]
        obj["photo_note"]=((obj.get("photo_note") or "")+" Joey Santore CC BY-NC 4.0 photo(s) provisionally installed; more diagnostic close-ups pending.").strip()
        if science(obj)!=before:raise AssertionError("Scientific fields altered: "+sid)
        path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    if report["installed"]:
        from scripts.curation_pipeline import rebuild_photo_fast_fill_queue
        rebuild_photo_fast_fill_queue()
    print(json.dumps({"mode":a.mode,"eligible":len(targets),"installed":report["installed"],"skipped":report["skipped"][:20]},indent=2),flush=True)
if __name__=="__main__":main()
