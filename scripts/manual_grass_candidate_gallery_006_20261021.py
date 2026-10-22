#!/usr/bin/env python3
"""Install archive-backed, attributed GRASS photo candidates as user-review gallery photos.

Explicit user request: see the actual images on the public species pages and inspect
there. They are visibly PROVISIONAL and have zero approved diagnostic arrows.
No botanical/taxonomic/region claims or non-photo lesson text are changed.
"""
from __future__ import annotations
import copy, csv, datetime, hashlib, io, json, os, pathlib, subprocess, zipfile
from collections import Counter
from PIL import Image, ImageOps

ROOT = pathlib.Path(".")
BATCH = "diagnostic-39704168823"
ARCHIVE = ROOT / "workflow/photo-library/batches" / BATCH
REPORT = ROOT / "reports/manual-grass-gallery-preview-006-20261021.json"
EXPECTED = {
    "eriochloa-sericea": "Eriochloa sericea",
    "hilaria-belangeri": "Hilaria belangeri",
    "hilaria-mutica": "Hilaria mutica",
}
LICENSES = {
    "CC0": "https://creativecommons.org/publicdomain/zero/1.0/",
    "CC BY": "https://creativecommons.org/licenses/by/",
}
def load(path):
    return json.loads(path.read_text(encoding="utf-8"))
def dhash(data):
    with Image.open(io.BytesIO(data)) as src:
        im = ImageOps.exif_transpose(src).convert("L").resize((9,8))
        pixels=list(im.getdata())
    out=0
    for y in range(8):
        for x in range(8):
            out=(out<<1) | int(pixels[y*9+x] > pixels[y*9+x+1])
    return out
def active_claims():
    path=ROOT/"workflow/work-claims.json"
    now=datetime.datetime.now(datetime.timezone.utc)
    active=set()
    if not path.is_file(): return active
    for claim in load(path).get("claims",[]):
        if claim.get("status") not in ("active","queued","blocked"): continue
        exp=claim.get("expires_at")
        if exp:
            try:
                expiry=datetime.datetime.fromisoformat(exp.replace("Z","+00:00"))
                if expiry.tzinfo is None: expiry=expiry.replace(tzinfo=datetime.timezone.utc)
                if expiry<=now:continue
            except (TypeError,ValueError):continue
        for sid in claim.get("taxa") or []:active.add(sid)
    return active
def science(sp):
    clone=copy.deepcopy(sp)
    clone.pop("images",None)
    clone.pop("photo_note",None)
    cs=clone.get("curation_status")
    if isinstance(cs,dict):
        for k in ("photo_metadata_count","photo_files_present","manual_gallery_preview_006"):
            cs.pop(k,None)
    return clone

def main():
    archive=load(ARCHIVE/"archive.json")
    assert archive["batch_id"]==BATCH and archive["persistent_release"] is True
    assert archive["photo_file_count"]==18 and archive["candidate_rows"]==18
    rows=list(csv.DictReader((ARCHIVE/"candidates.csv").open(encoding="utf-8",newline="")))
    assert len(rows)==18 and Counter(r["canonical_id"] for r in rows)==Counter({k:6 for k in EXPECTED})
    manifest={row["id"]:row["path"] for row in load(ROOT/"data/manifest.json")["species"]}
    active=active_claims()
    for sid in EXPECTED:
        if sid in active: raise RuntimeError("Unexpired work claim on "+sid+"; do not conflict")
        if sid not in manifest:raise RuntimeError("Missing canonical "+sid)
        if not manifest[sid].startswith("content/taxa/Poaceae/"):raise RuntimeError("Not grass "+sid)
    folder=pathlib.Path("/tmp/hays-grass-gallery-006")
    folder.mkdir(parents=True,exist_ok=True)
    asset=folder/archive["asset_name"]
    if not asset.exists():
        subprocess.run(["gh","release","download",archive["private_release_tag"],
            "--repo",os.environ["GITHUB_REPOSITORY"],"--pattern",archive["asset_name"],
            "--dir",str(folder)],check=True)
    assert hashlib.sha256(asset.read_bytes()).hexdigest()==archive["asset_sha256"],"Release archive checksum mismatch"
    output={"batch":BATCH,"mode":"user-review-on-public-species-pages",
        "archive_sha256_verified":True,"installed":[],"skipped":[],
        "taxonomy_science_unchanged":True,"diagnostic_arrows_added":0}
    prepared=[]
    with zipfile.ZipFile(asset) as z:
        for sid in EXPECTED:
            path=ROOT/manifest[sid]
            sp=load(path);original=science(sp)
            assert sp.get("id")==sid and sp.get("scientific_name")==EXPECTED[sid]
            existing=sp.get("images",[])
            existing_urls={str(v) for x in existing for k in ("media_source_url","direct_url","downloaded_from") if (v:=x.get(k))}
            oldhashes=[]
            for other in (path.parent/"images").glob("*"):
                if other.suffix.lower() not in (".jpg",".jpeg",".png",".webp"):continue
                try:oldhashes.append(dhash(other.read_bytes()))
                except (ValueError,OSError):pass
            kept=[]
            for row in [r for r in rows if r["canonical_id"]==sid]:
                if row["scientific_name"]!=EXPECTED[sid]:raise RuntimeError("Wrong source name: "+sid)
                if row["license"] not in LICENSES or not row["creator"] or not row["source_page"] or not row["image_url"]:
                    raise RuntimeError("Missing supported photo rights/creator/source: "+sid)
                if row["license_basis"]!="media" or row["photo_license_status"]!="supported":
                    raise RuntimeError("Photo-specific license not supported: "+sid)
                if not row["source_page"].startswith("https://www.gbif.org/occurrence/"):
                    raise RuntimeError("Missing original occurrence: "+sid)
                src=row["staged_file"]
                if not src.startswith("staged_images/"+sid+"/") or ".." in pathlib.PurePosixPath(src).parts:
                    raise RuntimeError("Unsafe archive member")
                if row["image_url"] in existing_urls:
                    output["skipped"].append({"id":sid,"image_url":row["image_url"],"reason":"Already in gallery"})
                    continue
                if src not in z.namelist():raise RuntimeError("Missing archived photo "+src)
                raw=z.read(src)
                if len(raw)<12000:raise RuntimeError("Undersized image "+src)
                with Image.open(io.BytesIO(raw)) as im:
                    im.verify()
                with Image.open(io.BytesIO(raw)) as im:
                    cleaned_im=ImageOps.exif_transpose(im).convert("RGB")
                    width,height=cleaned_im.size
                    if min(width,height)<190:raise RuntimeError("Too-small photo "+src)
                    buff=io.BytesIO()
                    cleaned_im.save(buff,"JPEG",quality=88,optimize=True)
                    data=buff.getvalue()
                h=dhash(data)
                if any((h^old).bit_count()<=5 for old in oldhashes):
                    output["skipped"].append({"id":sid,"image_url":row["image_url"],"reason":"Near-duplicate already present"})
                    continue
                oldhashes.append(h)
                digest=hashlib.sha256(data).hexdigest()
                name="public-review006-"+hashlib.sha1(src.encode()).hexdigest()[:14]+".jpg"
                dest=path.parent/"images"/name
                if dest.exists():raise RuntimeError("Image filename collision "+str(dest))
                record={
                    "file":"images/"+name,
                    "role":"Provisional photo — review actual plant identity and visible field features before using for diagnostic ID",
                    "creator":row["creator"],
                    "license":row["license"],
                    "license_url":LICENSES[row["license"]],
                    "license_version_note":"Photo-level CC code from GBIF media; confirm original full license version during user review",
                    "source_page":row["source_page"],
                    "media_source_url":row["image_url"],
                    "source_platform":"GBIF individual occurrence and archived photo library",
                    "source_observation_id":str(row["observation_id"]),
                    "source_determination":row["scientific_name"],
                    "library_release_tag":archive["private_release_tag"],
                    "library_archive_file":src,
                    "image_sha256":digest,
                    "image_dimensions":[width,height],
                    "photo_review":"PROVISIONAL: source taxon label only; user to verify on public species webpage",
                    "anatomy_arrows":"none; no structure has been visually confirmed",
                    "public_reuse":"yes, subject to recorded CC source license and creator credit",
                    "modifications":"EXIF/GPS removed, normalized JPEG; no labels or arrows applied",
                }
                kept.append((dest,data,record))
                existing_urls.add(row["image_url"])
            if not kept:
                output["skipped"].append({"id":sid,"reason":"No new distinct archive images"})
                continue
            sp["images"].extend(x[2] for x in kept)
            sp["photo_note"]=((sp.get("photo_note") or "").strip()
                +" Supplemental attributed photo references published for user's visual review; exact ID and anatomical organs NOT confirmed; no arrows.").strip()
            c=sp.setdefault("curation_status",{})
            c["photo_metadata_count"]=len(sp["images"])
            c["photo_files_present"]=sum(1 for x in sp["images"]
                if x.get("file","").startswith("images/") and
                ((path.parent/x["file"]).is_file() or any(str(d)==str(path.parent/x["file"]) for d,_,_ in kept)))
            c["manual_gallery_preview_006"]="2026-10-21"
            if science(sp)!=original:raise RuntimeError("Non-photo scientific content changed: "+sid)
            prepared.append((path,sp,kept))
        if not prepared:raise RuntimeError("No new images eligible; do not commit an empty release")
        for path,sp,items in prepared:
            for dest,data,record in items:
                dest.parent.mkdir(parents=True,exist_ok=True)
                dest.write_bytes(data)
                output["installed"].append({"id":sp["id"],"file":str(dest),
                  "sha256":record["image_sha256"],"source":record["source_page"],
                  "creator":record["creator"],"license":record["license"],
                  "identity_verified":False})
            path.write_text(json.dumps(sp,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"installed":len(output["installed"]),
      "species":Counter(x["id"] for x in output["installed"]),
      "skipped":output["skipped"],
      "public_user_review_pending":True},indent=2,default=dict),flush=True)
if __name__=="__main__":main()
