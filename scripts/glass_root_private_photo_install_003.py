#!/usr/bin/env python3
"""Append owner-authorized private photos; reuse existing exact-ID downloader.
Preserves prior images and science, strips EXIF, records stale source rights honestly.
"""
import copy,csv,hashlib,io,json,pathlib,sys
sys.path.insert(0,str(pathlib.Path(".").resolve()))
from scripts.glass_root_inat_install_approved import validated_photo
from PIL import Image
ROOT=pathlib.Path(".")
BATCH=ROOT/"workflow/glass-root-inat/approved-photo-install-batch-003.json"
REPORT=ROOT/"reports/glass-root-private-photo-batch-003.json"
def science(sp):
    value=copy.deepcopy(sp)
    for k in ("images","photo_note","learner_visual_status"):value.pop(k,None)
    cur=value.get("curation_status",{})
    for k in ("photo_metadata_count","photo_files_present","glass_root_garden_photo_install"):cur.pop(k,None)
    return value
def csv_append(path,records):
    text=path.read_text(encoding="utf-8-sig") if path.exists() else ""
    reader=csv.DictReader(io.StringIO(text)); columns=list(reader.fieldnames or []); old=list(reader)
    for rec in records:
        for k in rec:
            if k not in columns:columns.append(k)
    stream=io.StringIO(); writer=csv.DictWriter(stream,fieldnames=columns,lineterminator="\n")
    writer.writeheader();writer.writerows(old+records);path.write_text(stream.getvalue(),encoding="utf-8")
def main():
    batch=json.loads(BATCH.read_text())
    assert batch["public_reuse"]=="no"
    manifest=json.loads((ROOT/"data/manifest.json").read_text()); canonical={x["id"]:x["path"] for x in manifest["species"]}
    work=[]
    for target in batch["targets"]:
        assert canonical.get(target["id"])==target["path"],target["id"]
        path=ROOT/target["path"];sp=json.loads(path.read_text());assert sp["id"]==target["id"]
        assert (path.parent/"SOURCES.txt").exists()
        prior=copy.deepcopy(sp.get("images",[]))
        rel="images/"+target["filename"]
        existing=[im for im in prior if str(im.get("photo_id"))==str(target["photo_id"])]
        if existing:
            assert len(existing)==1
            file=path.parent/existing[0]["file"]
            with Image.open(file) as image:image.verify()
            work.append((target,path,sp,prior,None,None));continue
        assert not (path.parent/rel).exists(),rel
        assert not any(im.get("file")==rel for im in prior)
        binary,url,api_license,api_credit,dim=validated_photo(
            {"scientific_name":target["scientific_name"]},
            {"observation_id":target["observation_id"],"id":target["photo_id"]})
        record={"file":rel,"role":target["role"],"creator":"Glass Root Garden",
          "license":"Owner-authorized private study","license_basis":target["permission_basis"],
          "license_url":"https://github.com/Crking92/Hays-County-Botany/blob/main/workflow/glass-root-inat/OWNER_PERMISSION_2026-10-14.md",
          "study_use":"yes","public_reuse":"no","source_platform":"iNaturalist",
          "source_page":target["photo_page"],"observation_url":"https://www.inaturalist.org/observations/"+str(target["observation_id"]),
          "observation_id":target["observation_id"],"photo_id":target["photo_id"],
          "source_recorded_photo_license_at_download":api_license,
          "source_recorded_photo_attribution_at_download":api_credit,"downloaded_from":url,
          "image_dimensions":list(dim),"photo_review":"Exact Research Grade observation checked; image visually inspected; first-pass recognition only.",
          "anatomy_arrows":"none; detailed anatomy pending"}
        work.append((target,path,sp,prior,binary,record))
    report={"batch_id":batch["batch_id"],"installed":[],"science_preserved":True,"previous_galleries_preserved":True,"public_reuse":"no","canonical_species_count":len(canonical)}
    for target,path,sp,prior,binary,record in work:
        before_science=science(sp)
        if binary is not None:
            dest=path.parent/record["file"];dest.parent.mkdir(exist_ok=True);dest.write_bytes(binary)
            sp["images"]=prior+[record]
            assert sp["images"][:len(prior)]==prior
            meta=sp.setdefault("curation_status",{})
            meta["photo_metadata_count"]=len(sp["images"])
            meta["photo_files_present"]=sum(1 for im in sp["images"] if im.get("file") and not str(im["file"]).startswith(("https://","http://")) and (path.parent/im["file"]).is_file())
            meta["glass_root_garden_photo_install"]="2026-10-14"
            sp["learner_visual_status"]={"status":"provisional_learner_ready","mode":"learner_fast_fill","image_count":len(sp["images"]),"note":"Private owner-authorized first-photo coverage; fine diagnostic views remain pending."}
            sp["photo_note"]=(sp.get("photo_note") or "")+" Private owner-authorized Glass Root Garden photo physically installed 2026-10-14; source API rights retained separately."
            assert science(sp)==before_science,"Scientific metadata changed"
            path.write_text(json.dumps(sp,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
            csv_append(path.parent/"image-sources.csv",[{"file_name":target["filename"],"role":record["role"],"creator":record["creator"],"license":record["license"],"source_page":record["source_page"],"direct_url":record["downloaded_from"],"observation_id":str(record["observation_id"]),"photo_id":str(record["photo_id"]),"study_use":"yes","public_reuse":"no","rights_basis":record["license_basis"],"source_recorded_license":record["source_recorded_photo_license_at_download"]}])
            src=path.parent/"SOURCES.txt"
            src.write_text(src.read_text(encoding="utf-8")+"\nOWNER-AUTHORIZED PRIVATE PHOTO, 2026-10-14\nGlass Root Garden; "+record["source_page"]+"; observation "+str(record["observation_id"])+".\n"+record["license_basis"]+"\nSource API license: "+record["source_recorded_photo_license_at_download"]+"; public_reuse=no. EXIF/GPS stripped.\n",encoding="utf-8")
        current=json.loads(path.read_text())
        rec=next(im for im in current["images"] if str(im.get("photo_id"))==str(target["photo_id"]))
        file=path.parent/rec["file"]
        with Image.open(file) as image:
            dims=list(image.size);image.verify()
        assert rec["public_reuse"]=="no"
        assert current["images"][:len(prior)]==prior
        report["installed"].append({"id":target["id"],"path":target["path"],"photo_id":target["photo_id"],"observation_id":target["observation_id"],"file":str(file),"bytes":file.stat().st_size,"dimensions":dims,"sha256":hashlib.sha256(file.read_bytes()).hexdigest(),"prior_gallery_count":len(prior),"new_gallery_count":len(current["images"]),"scientific_metadata_unchanged":science(current)==before_science,"source_api_license":rec["source_recorded_photo_license_at_download"],"source_page":rec["source_page"],"permission":"owner-authorized private study"})
    REPORT.parent.mkdir(exist_ok=True);REPORT.write_text(json.dumps(report,indent=2)+"\n")
    from scripts.curation_pipeline import rebuild_photo_fast_fill_queue
    rebuild_photo_fast_fill_queue()
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
