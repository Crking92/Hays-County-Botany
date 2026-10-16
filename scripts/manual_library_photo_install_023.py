#!/usr/bin/env python3
"""Install visually screened photo-library RELEASE images into existing sparse canonical cards.
Source metadata is not an expert species confirmation. Do not edit scientific content.
"""
import collections,copy,datetime,hashlib,io,json,os,pathlib,subprocess,sys,zipfile
from PIL import Image,ImageOps
R=pathlib.Path(".")
REVIEW=R/"reports/manual-library-review-023-20261016/preview-manifest.json"
SELECTION=R/"workflow/manual-photo-enrichment/library-selection-023-20261016.json"
REPORT=R/"reports/manual-library-install-023-20261016.json"
ARCH=pathlib.Path("/tmp/hays-photo-library-install-023")
RIGHTS={"CC0":"https://creativecommons.org/publicdomain/zero/1.0/",
"CC0 1.0":"https://creativecommons.org/publicdomain/zero/1.0/",
"CC BY":"https://creativecommons.org/licenses/by/",
"CC BY-SA":"https://creativecommons.org/licenses/by-sa/",
"CC BY-NC":"https://creativecommons.org/licenses/by-nc/",
"CC BY-NC-SA":"https://creativecommons.org/licenses/by-nc-sa/"}
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def signature(obj):
    cp=copy.deepcopy(obj)
    for k in ("images","photo_note"):cp.pop(k,None)
    state=cp.get("curation_status")
    if isinstance(state,dict):
        for k in ("photo_metadata_count","photo_files_present","manual_library_install_023"):state.pop(k,None)
        if not state:cp.pop("curation_status",None)
    return cp
def dhash(data):
    with Image.open(io.BytesIO(data)) as pic:
        v=ImageOps.exif_transpose(pic).convert("L").resize((9,8),Image.Resampling.LANCZOS)
        points=list(v.getdata())
    h=0
    for y in range(8):
        for x in range(8):h=(h<<1)|int(points[y*9+x]>points[y*9+x+1])
    return h
def saved_current_hashes(path):
    hits=[]
    for f in (path.parent/"images").glob("*"):
        if f.suffix.lower() not in (".jpg",".jpeg",".png",".webp"):continue
        if not f.is_file():continue
        try:hits.append(dhash(f.read_bytes()))
        except (OSError,ValueError):pass
    return hits
def blocked_claims():
    f=R/"workflow/work-claims.json"
    claims=collections.defaultdict(list)
    now=datetime.datetime.now(datetime.timezone.utc)
    if f.exists():
        for c in read(f).get("claims",[]):
            if c.get("status") not in ("active","queued","blocked"):continue
            expiry=c.get("expires_at")
            if expiry:
                try:
                    t=datetime.datetime.fromisoformat(expiry.replace("Z","+00:00"))
                    if t.tzinfo is None:t=t.replace(tzinfo=datetime.timezone.utc)
                    if t<=now:continue
                except (ValueError,TypeError):pass
            for sid in c.get("taxa") or []:claims[sid].append(c.get("claim_id"))
    for p in (R/"curation-inbox").rglob("species.json"):
        try:claims[read(p)["id"]].append("curation-inbox")
        except (OSError,ValueError,KeyError):pass
    return claims
def main():
    cfg=read(SELECTION);preview=read(REVIEW)
    chosen={x["id"]:x for x in cfg["selections"]}
    prev={x["id"]:x for x in preview["species"]}
    refs={x["id"]:x["path"] for x in read(R/"data/manifest.json")["species"]}
    claims=blocked_claims()
    now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    out={"batch_id":cfg["id"],"completed_at_utc":now,
         "installed":[],"skipped":[],"species_affected":0,"science_unchanged":True,
         "selection_basis":"Selected images viewed in 3 visual contact sheets; exact source labels and rights checked; independent expert identity verification pending.",
         "archive_policy":"Use only exact photo files from checksum-verified PRIVATE GitHub Release archives; no fresh photo search."}
    tasks=[];archives={}
    for entry in cfg["selections"]:
        sid=entry["id"]
        if sid not in refs or sid not in prev:
            out["skipped"].append({"id":sid,"reason":"Canonical ID or inspected preview missing"});continue
        if sid in claims:
            out["skipped"].append({"id":sid,"reason":"Unexpired claim or curation inbox","claim_ids":claims[sid]});continue
        path=R/refs[sid];sp=read(path)
        if len(sp.get("images") or [])!=3 or any((path.parent / img.get("file", "")).is_file() for img in sp.get("images") or [] if img.get("file") and not str(img["file"]).startswith(("http://","https://"))):
            out["skipped"].append({"id":sid,"reason":"Gallery no longer has exactly three external-only records"});continue
        if sp.get("scientific_name")!=prev[sid].get("scientific_name"):
            out["skipped"].append({"id":sid,"reason":"Scientific taxon name changed after review"});continue
        wanted=[]
        for index in entry["choices"]:
            arr=[x for x in prev[sid]["candidate_images"] if x["index"]==index]
            if len(arr)!=1:raise AssertionError(("Missing contact choice",sid,index))
            c=arr[0]
            if c.get("license") not in RIGHTS or not c.get("creator") or not c.get("source_page"):
                raise AssertionError(("Unlicensed photo source",sid,index))
            if c.get("scientific_name")!=sp["scientific_name"] and (sid,c.get("scientific_name")) not in {("anatherum-glomeratum","Andropogon glomeratus"),("opuntia-engelmannii-var-lindheimeri","Opuntia lindheimeri")}:
                raise AssertionError(("Source taxon name not exact",sid,index))
            if c["archive_tag"] not in archives:archives[c["archive_tag"]]=c["asset_name"]
            wanted.append(c)
        tasks.append((sid,path,sp,entry,wanted))
    queue=read(R/"reports/photo-library-selection-queue-latest.json")
    checksum={x["tag"]:x["checksum"] for x in queue["archive_batches"]}
    ARCH.mkdir(parents=True,exist_ok=True)
    zips={}
    for tag,asset in sorted(archives.items()):
        filepath=ARCH/asset
        if not filepath.is_file():
            subprocess.run(["gh","release","download",tag,"--repo",os.environ["GITHUB_REPOSITORY"],"--pattern",asset,"--dir",str(ARCH)],check=True)
        assert hashlib.sha256(filepath.read_bytes()).hexdigest()==checksum[tag],("Archive SHA mismatch",tag)
        zips[tag]=zipfile.ZipFile(filepath)
    prepared=[]
    for sid,path,sp,entry,candidates in tasks:
        existing=sp.get("images") or []
        used={str(v) for img in existing for key in ("source_page","media_source_url","downloaded_from","direct_url")
              if (v:=img.get(key))}
        photos=[];dhashes=saved_current_hashes(path)
        for row in candidates:
            uri=row["archive_file"]
            if not uri.startswith("staged_images/"+sid+"/") or ".." in pathlib.PurePosixPath(uri).parts:
                out["skipped"].append({"id":sid,"index":row["index"],"reason":"Unsafe archive member"});continue
            if row["image_url"] in used or row["source_page"] in used:
                out["skipped"].append({"id":sid,"index":row["index"],"reason":"Already installed source URL"});continue
            if uri not in zips[row["archive_tag"]].namelist():
                out["skipped"].append({"id":sid,"index":row["index"],"reason":"Selected image missing from validated private release"});continue
            raw=zips[row["archive_tag"]].read(uri)
            if hashlib.sha256(raw).hexdigest()!=row["sha256"]:
                raise AssertionError(("Preview image hash differs",sid,row["index"]))
            if len(raw)<19000:continue
            try:
                with Image.open(io.BytesIO(raw)) as photo:
                    photo.verify()
                with Image.open(io.BytesIO(raw)) as photo:
                    photo=ImageOps.exif_transpose(photo).convert("RGB")
                    if min(photo.size)<190:continue
                    target=io.BytesIO()
                    photo.save(target,"JPEG",quality=90,optimize=True)
                    cleaned=target.getvalue()
                hash=dhash(cleaned)
                if any((hash^old).bit_count()<=6 for old in dhashes):
                    out["skipped"].append({"id":sid,"index":row["index"],"reason":"Image perceptually duplicates current gallery or batch"});continue
            except (OSError,ValueError):
                out["skipped"].append({"id":sid,"index":row["index"],"reason":"Unreadable image"});continue
            dhashes.append(hash)
            photos.append((row,cleaned,[photo.width,photo.height]))
        if photos:prepared.append((sid,path,sp,entry,photos))
        else:out["skipped"].append({"id":sid,"reason":"No distinct surviving selected photos"})
    sys.path.insert(0,str(R.resolve()))
    from scripts.gbif_exact_zero_photo_recovery import csvappend
    for sid,path,sp,entry,photos in prepared:
        before=signature(sp)
        for row,cleaned,dim in photos:
            filename="library-review023-"+hashlib.sha1((row["archive_tag"]+row["archive_file"]).encode()).hexdigest()[:15]+".jpg"
            dest=path.parent/"images"/filename
            if dest.exists():raise AssertionError(("Would overwrite existing photo",str(dest)))
            dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_bytes(cleaned)
            record={
              "file":"images/"+filename,
              "role":"Complementary visible view manually screened on review sheet; exact diagnostic features and botanical identity need expert sign-off",
              "requested_diagnostic_view":entry["reason"],
              "creator":row["creator"],"license":row["license"],"license_url":RIGHTS[row["license"]],
              "license_version_note":"Exact license version must be checked at original media source; shorthand preserved from archived media",
              "source_platform":row["source"]+" via durable private Hays photo library",
              "source_page":row["source_page"],"media_source_url":row["image_url"],
              "source_determination":row["scientific_name"],
              "source_observation_id":str(row["observation_id"]),
              "library_release_tag":row["archive_tag"],"library_archive_file":row["archive_file"],
              "archive_image_sha256":row["sha256"],
              "image_dimensions":dim,
              "photo_review":"Actual photographic content visually screened for broad teaching view; taxon determined by source metadata and not independently expert-verified.",
              "anatomy_arrows":"none; diagnostic structures not expert verified",
              "study_use":"Private project; comply with individually stated CC license conditions",
              "public_reuse":"Review individual license version, attribution, commercial restrictions and ShareAlike where applicable before publication",
              "modifications":"Resaved JPEG with metadata removed (original source rights remain attached)"
            }
            sp.setdefault("images",[]).append(record)
            csvappend(path.parent/"image-sources.csv",{
              "file_name":filename,"role":record["role"],"creator":record["creator"],"license":record["license"],
              "license_url":record["license_url"],"source_page":record["source_page"],
              "direct_url":record["media_source_url"],"study_use":record["study_use"],
              "public_reuse":record["public_reuse"],"modifications":record["modifications"]})
            with (path.parent/"SOURCES.txt").open("a",encoding="utf-8") as fh:
                fh.write("\nLIBRARY-FIRST IMAGE SELECTION 023 "+now+"\n"+sp["scientific_name"]+
                  "\nCreator: "+row["creator"]+"; License shorthand: "+row["license"]+
                  "\nOriginal source: "+row["source_page"]+"\nStored archive: "+row["archive_tag"]+
                  " :: "+row["archive_file"]+
                  "\nVisually screened broad view. Independent exact-species botanical ID and close-up anatomy need verification. EXIF stripped; no arrows.\n")
            out["installed"].append({"id":sid,"path":str(dest),"index":row["index"],"creator":row["creator"],"license":row["license"],
              "source_page":row["source_page"],"release":row["archive_tag"],
              "bytes":len(cleaned),"sha256":hashlib.sha256(cleaned).hexdigest(),
              "expert_botanical_identity_verified":False})
        state=sp.setdefault("curation_status",{})
        state["photo_metadata_count"]=len(sp.get("images") or [])
        state["photo_files_present"]=sum(1 for p in sp["images"] if p.get("file") and (path.parent/p["file"]).is_file())
        state["manual_library_install_023"]=now[:10]
        sp["photo_note"]=((sp.get("photo_note") or "")+
            " Manual library-first complementary photo selection installed; independent diagnostic ID review pending.").strip()
        if signature(sp)!=before:raise AssertionError("Science changed on "+sid)
        path.write_text(json.dumps(sp,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    out["species_affected"]=len(prepared)
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    subprocess.run([sys.executable,"scripts/refresh_photo_coverage_snapshot.py"],check=True)
    print(json.dumps({"installed":len(out["installed"]),"species_affected":out["species_affected"],
                      "skipped":out["skipped"]},indent=2),flush=True)
if __name__=="__main__":main()
