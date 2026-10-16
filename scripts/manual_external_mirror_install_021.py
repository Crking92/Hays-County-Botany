#!/usr/bin/env python3
"""Install one visually reviewed image of Amphiachyris amoena for private noncommercial botany study."""
import datetime,hashlib,json,pathlib,sys,subprocess
R=pathlib.Path(".");sys.path.insert(0,str(R.resolve()))
from scripts.manual_external_mirror_review_021 import read_url
from scripts.manual_library_photo_install_010 import signature,blocked_claims
from scripts.gbif_exact_zero_photo_recovery import csvappend
SID="amphiachyris-amoena"
OUT=R/"reports/manual-external-mirror-install-021-20261016.json"
def read(path):return json.loads(path.read_text(encoding="utf-8"))
def main():
    preview=read(R/"reports/manual-external-mirror-review-021/preview-manifest.json")
    refs={x["id"]:x["path"] for x in read(R/"data/manifest.json")["species"]}
    rep={"batch":"external-mirror-install-021","installed":[],"skipped":[],"science_unchanged":True,
         "notes":"Individual photo creator and CC BY-NC inherited from pre-reviewed canonical image metadata; original precise license version not independently confirmed."}
    if SID in blocked_claims():rep["skipped"].append({"id":SID,"reason":"Unexpired active claim"});OUT.write_text(json.dumps(rep,indent=2)+"\n");return
    path=R/refs[SID];sp=read(path);before=signature(sp)
    source=sp["images"]
    if len(source)!=1 or any(str(x.get("file","")).startswith("images/") for x in source):
        raise ValueError("Gallery changed or local already saved")
    original=source[0];cand=preview["species"][0]["candidates"][0]
    assert preview["species"][0]["id"]==SID and sp["scientific_name"]=="Amphiachyris amoena"
    assert original["file"]==cand["original_url"] and original["license"]=="CC BY-NC"
    assert original["creator"]=="Ellen Hildebrandt" and cand["creator"]=="Ellen Hildebrandt"
    data,dimensions,unused=read_url(cand["original_url"])
    checksum=hashlib.sha256(data).hexdigest()
    assert checksum==cand["sha256_of_normalized_jpeg"],"Visual review and newly fetched source differ"
    name="inat-165635431-reviewed-"+checksum[:12]+".jpg"
    local=path.parent/"images"/name
    if local.exists():raise ValueError("already installed; no overwrite")
    local.parent.mkdir(parents=True,exist_ok=True);local.write_bytes(data)
    record={"file":"images/"+name,
       "role":"Yellow flower head, narrow linear leaves and finely branched stem; source determined, diagnostic identity provisional",
       "creator":"Ellen Hildebrandt","license":"CC BY-NC",
       "license_version_note":"Exact CC BY-NC version not confirmed; check image-specific iNaturalist source",
       "source_page":"https://www.inaturalist.org/photos/165635431",
       "original_species_source_page":original["source_page"],
       "direct_url":cand["original_url"],"photo_id":"165635431",
       "photo_review":"Actual source pixels visually inspected; expert species verification pending",
       "public_reuse":"CC BY-NC permits attribution-based noncommercial uses; commercial use not authorized",
       "modifications":"Resized and JPEG re-encoded; original EXIF removed; source and creator retained",
       "anatomy_arrows":"none"}
    sp["images"].append(record)
    st=sp.setdefault("curation_status",{})
    st["photo_metadata_count"]=len(sp["images"])
    st["photo_files_present"]=1
    sp["photo_note"]=((sp.get("photo_note") or "")+" Original CC BY-NC external image mirrored locally after visual review; exact source species determination still provisional.").strip()
    assert signature(sp)==before,"Unintended botanical science edit"
    path.write_text(json.dumps(sp,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    csvappend(path.parent/"image-sources.csv",{"file_name":name,"role":record["role"],
      "creator":record["creator"],"license":record["license"],"source_page":record["source_page"],
      "direct_url":record["direct_url"],"public_reuse":record["public_reuse"],
      "modifications":record["modifications"]})
    with (path.parent/"SOURCES.txt").open("a",encoding="utf-8") as f:
        f.write("\nLOCAL MIRROR REVIEW 021 (2026-10-16)\n"+record["source_page"]+
             "\nPhoto creator Ellen Hildebrandt; individual CC BY-NC, version pending verification; noncommercial private study.\n")
    rep["installed"].append({"id":SID,"photo_file":str(local),"sha256":checksum,"license":record["license"],"creator":record["creator"],"source_page":record["source_page"]})
    OUT.write_text(json.dumps(rep,indent=2)+"\n",encoding="utf-8")
    subprocess.run([sys.executable,"scripts/refresh_photo_coverage_snapshot.py"],check=True)
    print(json.dumps({"installed":len(rep["installed"]),"notes":rep["notes"]},indent=2))
if __name__=="__main__":main()
