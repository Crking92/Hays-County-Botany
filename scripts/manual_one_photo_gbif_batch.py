#!/usr/bin/env python3
"""Manual targeted one-photo enrichment using individually licensed exact-ID GBIF media.
No taxonomy or native-range changes, no claimed taxa, no duplicate photo install.
New image roles remain unverified until inspected by a botanist.
"""
import collections,copy,csv,datetime,hashlib,io,json,pathlib,re,subprocess,sys
from concurrent.futures import ThreadPoolExecutor,as_completed
from PIL import Image
ROOT=pathlib.Path(".");sys.path.insert(0,str(ROOT.resolve()))
from scripts.gbif_exact_zero_photo_recovery import scan_one,encode,csvappend
BATCH=ROOT/"workflow/manual-photo-enrichment/batch-001-20261015.json"
REPORT=ROOT/"reports/manual-diagnostic-photo-batch-001.json"
def pixels_hash(img):
    with Image.open(img) as im:
        gray=im.convert("L").resize((9,8),Image.Resampling.LANCZOS)
        px=list(gray.getdata())
    h=0
    for y in range(8):
        for x in range(8):
            h=(h<<1)|int(px[y*9+x]>px[y*9+x+1])
    return h
def too_similar(data,path):
    h=pixels_hash(io.BytesIO(data))
    images=path.parent/"images"
    if not images.exists():return False
    for f in images.iterdir():
        if not f.is_file() or f.suffix.lower() not in (".png",".jpg",".jpeg",".webp"):continue
        try:
            other=pixels_hash(f)
            if (h^other).bit_count()<=6:return True
        except (OSError,ValueError):continue
    return False
def science(obj):
    o=copy.deepcopy(obj)
    for k in ("images","photo_note","learner_visual_status"):o.pop(k,None)
    cs=o.get("curation_status")
    if isinstance(cs,dict):
        for k in ("photo_metadata_count","photo_files_present","gbif_manual_photo_enrichment"):cs.pop(k,None)
        if not cs:o.pop("curation_status",None)
    return o
def claim_exclusion():
    claims=json.loads((ROOT/"workflow/work-claims.json").read_text(encoding="utf-8"))
    busy=set()
    for c in claims.get("claims",[]):
        if c.get("status") in ("active","queued","blocked"):
            busy.update(c.get("taxa") or [])
    inbox=set()
    for f in (ROOT/"curation-inbox").rglob("species.json"):
        try:inbox.add(json.loads(f.read_text(encoding="utf-8"))["id"])
        except (OSError,ValueError,KeyError):pass
    return busy|inbox
def main():
    batch=json.loads(BATCH.read_text(encoding="utf-8"))
    manifest=json.loads((ROOT/"data/manifest.json").read_text(encoding="utf-8"))
    refs={x["id"]:x["path"] for x in manifest["species"]}
    busy=claim_exclusion()
    now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    output={"batch_id":batch["id"],"date_utc":now,"installed":[],"skipped":[],
        "searched":[],"source_policy":"Original occurrence scientific determination exactly equals accepted species. Individually licensed CC photo and downloaded pixels. Photo view provisional; not visually diagnosed.",
        "science_preserved":True}
    tasks=[]
    for row in batch["candidates"]:
        sid=row["id"];ref=refs.get(sid)
        if not ref:
            output["skipped"].append({"id":sid,"why":"No longer canonical"});continue
        if sid in busy:
            output["skipped"].append({"id":sid,"why":"Active claim or curation inbox"});continue
        path=ROOT/ref
        sp=json.loads(path.read_text(encoding="utf-8"))
        if len(sp.get("images") or [])!=1:
            output["skipped"].append({"id":sid,"why":"Gallery changed; no longer exactly one photo"});continue
        if (sp.get("scientific_name") or "").count(" ")!=1:
            output["skipped"].append({"id":sid,"why":"Infraspecific name; requires rank-concept-specific review"});continue
        tasks.append((sid,path,sp,row))
    found={}
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures={pool.submit(scan_one,sid,[sp["scientific_name"]]):sid for sid,path,sp,task in tasks}
        for f in as_completed(futures):
            sid=futures[f]
            try:
                _,stats,rows=f.result()
                found[sid]=(stats,rows)
            except Exception as ex:
                found[sid]=([{"error":str(ex)[:140]}],[])
    prepared=[]
    for sid,path,sp,request in tasks:
        stats,options=found[sid]
        output["searched"].append({"id":sid,"queries":stats,"license_pass_candidates":len(options)})
        current=sp["images"][0]
        used_sources={str(current.get(k) or "") for k in ("source_page","downloaded_from","media_source_url")}
        used_ids={str(current.get("photo_id") or ""),str(current.get("observation_id") or "")}
        old_role=(current.get("role") or "").lower()
        # Prefer a different observation/media and, when the first was a herbarium voucher,
        # prefer field photos. This is a source-diversity heuristic, NOT visual diagnosis.
        voucher_first=any(w in old_role for w in ("voucher","herbarium","specimen"))
        options.sort(key=lambda x:(
            (x.get("basis")!="HUMAN_OBSERVATION") if voucher_first else (x.get("basis")!="PRESERVED_SPECIMEN"),
            x.get("license") not in ("CC0 1.0","CC BY"),
            str(x.get("gbif_id") or "") in used_ids,
            x.get("gbif_id") or 0))
        chosen=None
        for opt in options[:14]:
            if opt["uri"] in used_sources or opt["occurrence_url"] in used_sources:continue
            if str(opt["gbif_id"]) in used_ids:continue
            try:
                image=encode(opt["uri"])
                if not image:continue
                blob,dims=image
                if too_similar(blob,path):continue
                chosen=(opt,blob,dims);break
            except Exception:continue
        if not chosen:
            output["skipped"].append({"id":sid,"why":"No source-safe retrievable photo clearly distinct from current image; do not duplicate or invent anatomy.","candidate_count":len(options)})
            continue
        prepared.append((sid,path,sp,request,chosen))
    for sid,path,sp,req,(source,blob,dim) in prepared:
        original=science(sp)
        name="gbif-manual-"+str(source["gbif_id"])+"-"+hashlib.sha1(source["uri"].encode()).hexdigest()[:9]+".jpg"
        f=path.parent/"images"/name
        if f.exists():raise ValueError("Refuse image collision "+str(f))
        f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(blob)
        photo={
            "file":"images/"+name,
            "role":"Additional distinct image candidate; target structures not yet visually verified",
            "requested_diagnostic_view":req["desired_view"],
            "creator":source["creator"] or "CC0 creator not specified",
            "license":source["license"],
            "license_url":source["license_url"],
            "source_platform":"GBIF occurrence image, original creator retained",
            "source_page":source["occurrence_url"],
            "gbif_occurrence_id":str(source["gbif_id"]),
            "source_determination":source["source_determination"],
            "accepted_target":sp["scientific_name"],
            "media_source_url":source["uri"],
            "image_dimensions":dim,
            "photo_review":"Exact source determination, individually licensed media, downloaded pixels, and basic near-duplicate filter checked. Anatomy NOT visually confirmed.",
            "anatomy_arrows":"not added; image anatomy not verified",
            "study_use":"follow individual license conditions; noncommercial only for CC BY-NC",
            "public_reuse":"Respect recorded photo-specific license",
            "modifications":"Resized JPEG and EXIF removed"
        }
        sp["images"].append(photo)
        state=sp.setdefault("curation_status",{})
        state["photo_metadata_count"]=len(sp["images"])
        state["photo_files_present"]=sum(1 for x in sp["images"] if x.get("file") and (path.parent/x["file"]).is_file())
        state["gbif_manual_photo_enrichment"]=now[:10]
        sp["photo_note"]=((sp.get("photo_note") or "")+" Manual diagnostic-photo enrichment candidate installed from individually licensed source; verify anatomy against target before labeling.").strip()
        if science(sp)!=original:raise AssertionError("Science modified: "+sid)
        csvappend(path.parent/"image-sources.csv",{
          "file_name":name,"role":photo["role"],"creator":photo["creator"],"license":photo["license"],
          "license_url":photo["license_url"],"source_page":photo["source_page"],
          "direct_url":photo["media_source_url"],"study_use":"yes, with actual license restrictions",
          "public_reuse":photo["public_reuse"],"modifications":photo["modifications"]})
        with (path.parent/"SOURCES.txt").open("a",encoding="utf-8") as g:
            g.write("\nMANUAL ONE-PHOTO ENRICHMENT "+now+"\n"+source["source_determination"]+"\n"+source["occurrence_url"]+"\n"+
            photo["creator"]+" | "+photo["license"]+" "+photo["license_url"]+"\n"+
            "Target visual view (NOT YET verified): "+req["desired_view"]+"\nNo anatomy arrows; no scientific or native-range changes.\n")
        path.write_text(json.dumps(sp,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        output["installed"].append({
         "id":sid,"file":str(f),"source":source["occurrence_url"],"photo_license":source["license"],
         "creator":photo["creator"],"bytes":len(blob),"sha256":hashlib.sha256(blob).hexdigest(),
         "diagnostic_view_verified":False})
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text(json.dumps(output,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    subprocess.run([sys.executable,"scripts/refresh_photo_coverage_snapshot.py"],check=True)
    print(json.dumps({"installed":len(output["installed"]),"skipped":output["skipped"],
                      "ids":[x["id"] for x in output["installed"]]},indent=2),flush=True)
if __name__=="__main__":main()
