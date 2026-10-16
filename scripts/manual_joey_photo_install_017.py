#!/usr/bin/env python3
"""Install precisely visually selected Joey Santore CC BY-NC iNat photos for private study.

Adds no scientific/taxonomy changes; noncommercial rights explicitly preserved.
"""
import copy,hashlib,io,json,pathlib,urllib.request,datetime as dt,subprocess,sys
from PIL import Image,ImageOps
R=pathlib.Path(".")
CFG=R/"workflow/manual-photo-enrichment/joey-selection-017-20261016.json"
REPORT=R/"reports/manual-joey-install-017-20261016.json"
def load(p):return json.loads(p.read_text(encoding="utf-8"))
def main():
    cfg=load(CFG);preview=load(R/cfg["preview_manifest"])
    options={s["id"]:s for s in preview["species"]}
    species={s["id"]:s["path"] for s in load(R/"data/manifest.json")["species"]}
    sys.path.insert(0,str(R.resolve()))
    from scripts.manual_library_photo_install_010 import signature,blocked_claims
    from scripts.gbif_exact_zero_photo_recovery import csvappend
    claims=blocked_claims()
    report={"id":cfg["id"],"time":dt.datetime.now(dt.timezone.utc).isoformat(),
            "installed":[],"skipped":[],"science_unchanged":True,"species_affected":0,
            "rights":"Individual Joey Santore CC BY-NC images; private noncommercial education only; no commercial/public reuse approval"}
    for selection in cfg["selections"]:
        sid=selection["id"]
        if sid not in species or sid not in options:
            report["skipped"].append({"id":sid,"reason":"Missing canonical/visual preview"});continue
        if sid in claims:
            report["skipped"].append({"id":sid,"reason":"Unexpired claim or curation inbox"});continue
        path=R/species[sid];obj=load(path)
        previous=signature(obj)
        if any((s.get("file") or "").startswith("images/") for s in obj.get("images",[])):
            report["skipped"].append({"id":sid,"reason":"Local files now present; avoid duplicate installation conflict"});continue
        if obj["scientific_name"] not in options[sid]["taxon_names"]:
            report["skipped"].append({"id":sid,"reason":"Exact source name no longer matches"});continue
        new=[]
        for choice in selection["choices"]:
            c=next((x for x in options[sid]["candidates"] if x["index"]==choice and x["status"]=="visual_preview"),None)
            if not c or c["creator"]!="Joey Santore" or c["license"]!="CC BY-NC":
                report["skipped"].append({"id":sid,"choice":choice,"reason":"No approved CC BY-NC preview"});continue
            if not c["image_url"].startswith("https://inaturalist-open-data.s3.amazonaws.com/photos/"):
                report["skipped"].append({"id":sid,"choice":choice,"reason":"Unsafe unrecognized source"});continue
            try:
                req=urllib.request.Request(c["image_url"],headers={"User-Agent":"HaysBotanyStudy/1.0","Accept":"image/*"})
                with urllib.request.urlopen(req,timeout=28) as resp:raw=resp.read(10000001)
                if len(raw)>10000000:raise ValueError("Image exceeds size cap")
                with Image.open(io.BytesIO(raw)) as im:
                    im.load();pic=ImageOps.exif_transpose(im).convert("RGB")
                if min(pic.size)<240:raise ValueError("Insufficient resolution")
                pic.thumbnail((1280,1280),Image.Resampling.LANCZOS)
                buf=io.BytesIO();pic.save(buf,"JPEG",quality=89,optimize=True)
                data=buf.getvalue()
                if hashlib.sha256(data).hexdigest()!=c["sha256"]:
                    raise ValueError("Source photo changed since visual review")
                name="joey-review017-"+hashlib.sha256(data).hexdigest()[:16]+".jpg"
                dest=path.parent/"images"/name
                if dest.exists():raise ValueError("Local filename collision")
                new.append((c,data,name,dest))
            except Exception as e:
                report["skipped"].append({"id":sid,"choice":choice,"reason":str(e)[:160]})
        if not new:continue
        for c,data,name,dest in new:
            dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
            record={"file":"images/"+name,
                "role":selection["reason"]+" (source determination provisional; no verified anatomy arrows)",
                "creator":"Joey Santore","license":"CC BY-NC",
                "license_url":"https://creativecommons.org/licenses/by-nc/4.0/",
                "license_version_note":"License shorthand per image inventory, check original iNaturalist photo for exact version",
                "source_platform":"Joey Santore iNaturalist Texas observation",
                "source_page":c["source_page"],"source_observation":c["observation"],
                "media_source_url":c["image_url"],"source_determination":c["source_scientific_name"],
                "photo_id":c["photo_id"],"observation_id":c["observation"].rsplit("/",1)[-1],
                "photo_review":"Actual photograph visually screened via JPEG contact sheet; independent botanical identity pending",
                "anatomy_arrows":"none; exact structures not expert-confirmed",
                "study_use":"Private noncommercial educational botany project only, with Joey Santore attribution",
                "public_reuse":"Noncommercial CC BY-NC conditions; commercial reuse not cleared",
                "modifications":"Re-encoded JPEG and removed EXIF metadata; creator and original CC BY-NC retained"}
            obj.setdefault("images",[]).append(record)
            csvappend(path.parent/"image-sources.csv",{"file_name":name,"role":record["role"],
                "creator":record["creator"],"license":record["license"],"license_url":record["license_url"],
                "source_page":record["source_page"],"direct_url":record["media_source_url"],
                "study_use":record["study_use"],"public_reuse":record["public_reuse"],"modifications":record["modifications"]})
            with (path.parent/"SOURCES.txt").open("a",encoding="utf-8") as f:
                f.write("\nJOEY LIBRARY PHOTO REVIEW 017 "+report["time"]+"\n"+obj["scientific_name"]+"\nJoey Santore / iNaturalist; CC BY-NC (exact version consult photo source)\n"+c["source_page"]+"\nIndependent botanical determination not completed; no anatomy arrows.\n")
            report["installed"].append({"id":sid,"path":str(dest),"sha256":hashlib.sha256(data).hexdigest(),
                "creator":"Joey Santore","license":"CC BY-NC","source_page":c["source_page"],
                "photo_id":c["photo_id"],"independent_botanical_identity_verified":False})
        st=obj.setdefault("curation_status",{})
        st["photo_metadata_count"]=len(obj["images"])
        st["photo_files_present"]=sum(1 for p in obj["images"] if p.get("file") and (path.parent/p["file"]).is_file())
        obj["photo_note"]=((obj.get("photo_note") or "")+" Joey Santore photo additions are rights-limited CC BY-NC and botanical ID provisional.").strip()
        if signature(obj)!=previous:raise AssertionError("Unexpected scientific content change: "+sid)
        path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        report["species_affected"]+=1
    REPORT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    subprocess.run([sys.executable,"scripts/refresh_photo_coverage_snapshot.py"],check=True)
    print(json.dumps({"installed":len(report["installed"]),"species":report["species_affected"],"skipped":report["skipped"]},indent=2))
if __name__=="__main__":main()
