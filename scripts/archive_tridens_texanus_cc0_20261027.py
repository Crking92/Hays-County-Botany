#!/usr/bin/env python3
"""Recover exact licensed Texas tridens original photographs previously remote-only.
Only Commons files (4) true collar region and (5) Uvalde habitat by Gaiacoyote,
each individually confirmed CC0 1.0. Preserve all field-ID and taxonomy fields.
"""
import hashlib,io,json,time
from pathlib import Path
from datetime import datetime,timezone
from urllib.parse import urlparse
import requests
from PIL import Image,ImageOps

DIR=Path("content/taxa/Poaceae/Tridens")
SP=DIR/"tridens-texanus/species.json"
GEN=DIR/"genus.json"
REPORT=Path("reports/tridens-texanus-commons-cc0-physical-20261027.json")
HOLD=Path("reports/tridens-texanus-commons-cc0-hold-20261027.json")
MARK=Path("workflow/field-id-publication/2026-10-27-tridens-texanus-cc0-collar-and-habitat.json")
PHOTOS=[
 ("4","ligule", (488,360),"https://upload.wikimedia.org/wikipedia/commons/2/2a/Tridens_texanus_%284%29.jpg"),
 ("5","habitat",(350,635),"https://upload.wikimedia.org/wikipedia/commons/c/cf/Tridens_texanus_%285%29.jpg"),
]
def write(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def get_orig(session,n,url,expected):
    failures=[]
    urls=[url, "https://commons.wikimedia.org/wiki/Special:Redirect/file/Tridens%20texanus%20%28"+n+"%29.jpg"]
    for u in urls:
        for attempt in range(2):
            try:
                r=session.get(u,timeout=32,headers={"Accept":"image/jpeg,image/*"})
                r.raise_for_status()
                if urlparse(r.url).hostname not in ("upload.wikimedia.org","commons.wikimedia.org"):
                    raise ValueError("Untrusted redirect host: "+str(r.url)[:90])
                raw=r.content
                if not (2500<len(raw)<4_000_000) or raw[:3]!=b"\xff\xd8\xff":
                    raise ValueError("Not original substantial JPEG bytes")
                with Image.open(io.BytesIO(raw)) as im:
                    im.load()
                    if im.format!="JPEG" or im.size!=expected:
                        raise ValueError("File identity/dimensions mismatch: "+repr(im.size)+" expected "+repr(expected))
                    clean=ImageOps.exif_transpose(im).convert("RGB")
                buf=io.BytesIO();clean.save(buf,"JPEG",quality=95,optimize=True)
                blob=buf.getvalue()
                with Image.open(io.BytesIO(blob)) as ck:
                    assert ck.format=="JPEG" and not ck.getexif().get(34853)
                    ck.verify()
                return dict(blob=blob,source_sha256=hashlib.sha256(raw).hexdigest(),
                    local_sha256=hashlib.sha256(blob).hexdigest(),source_url=r.url,
                    original_dimensions=list(expected),archive_dimensions=list(clean.size))
            except Exception as e:
                failures.append(type(e).__name__+": "+str(e)[:140])
                time.sleep(1+attempt)
    return {"error":"; ".join(failures[-4:])}
def main():
    s=json.loads(SP.read_text(encoding="utf8"));g=json.loads(GEN.read_text(encoding="utf8"))
    if s.get("id")!="tridens-texanus" or g.get("name")!="Tridens":
        raise RuntimeError("Target canonical identity mismatch")
    session=requests.Session()
    session.headers["User-Agent"]="HaysBotanyOriginalCC0Photo/1.0 (academic grass learner, Crking92/Hays-County-Botany)"
    successes=[];blocked=[]
    for n,role,dimensions,url in PHOTOS:
        source="https://commons.wikimedia.org/wiki/File:Tridens_texanus_("+n+").jpg"
        matches=[x for x in s.get("images",[]) if x.get("source_page")==source]
        if len(matches)!=1 or matches[0].get("creator")!="Gaiacoyote" or matches[0].get("license")!="CC0 1.0":
            raise RuntimeError("Source copyright/identity card changed; reconcile before reusing "+source)
        item=matches[0]
        local=SP.parent/"images"/("gaiacoyote-tridens-texanus-"+n+"-"+role+"-cc0.jpg")
        if str(item.get("file","")).startswith("images/"):
            print("ALREADY_PHYSICALLY_STORED",n)
            continue
        if local.exists():raise RuntimeError("Would overwrite photo without canonical record: "+str(local))
        found=get_orig(session,n,url,dimensions)
        if "error" in found:
            blocked.append({"photo_number":n,"source_page":source,"failure":found["error"]})
            print("SOURCE_HOLD",n,found["error"],flush=True)
            continue
        existing=[k for k,x in enumerate(s["visual_comparison"]["items"]) if x.get("source_page")==source]
        if len(existing)!=1:
            raise RuntimeError("Species teaching panel missing/duplicated for "+source)
        panel=s["visual_comparison"]["items"][existing[0]]
        if panel.get("creator")!="Gaiacoyote" or panel.get("license")!="CC0 1.0":
            raise RuntimeError("Teaching panel is not same licensed source: "+source)
        local.parent.mkdir(parents=True,exist_ok=True)
        local.write_bytes(found["blob"])
        item["file"]="images/"+local.name
        item["byte_verification"]="VERIFIED exact original Wikimedia JPEG and expected original pixel dimensions; SHA-256 recorded; metadata scrubbed"
        item["image_status"]="PHYSICALLY_ARCHIVED_CC0_1_ORIGINAL_USER_REVIEW_FOR_MICRO_DETAIL"
        item["photo_review"]=("Photographer/source/CC0 individually verified. Original JPEG downloaded and physically saved. "
            "Actual hair-fringe legibility is provisionally visible; tiny free margin NOT calibrated.")
        item["original_sha256"]=found["source_sha256"]
        item["archived_sha256"]=found["local_sha256"]
        item["original_image_dimensions"]=found["original_dimensions"]
        item["archived_dimensions"]=found["archive_dimensions"]
        item["modifications"]="RGB JPEG re-encode, original EXIF/GPS removed; no cropping, digital organ arrows or drawn labels."
        item["annotation_status"]="annotation_pending; only gross actual organs, no invented fine ligule anchors"
        panel["image_url"]=str(local)
        panel["photo_status"]="LOCAL exact source CC0 Gaiacoyote original with source/dimensions/SHA verified; no overlaid anatomy arrows; true hair attachments still unmeasured"
        panel["markers"]=[]
        panel["annotation_status"]="annotation_pending; hand-check actual free ligule fringe before marker"
        genus_panels=[x for x in g.get("visual_comparison",{}).get("items",[]) if x.get("source_page")==source]
        if len(genus_panels)>1:raise RuntimeError("Duplicate genus source panel")
        if genus_panels:
            if genus_panels[0].get("creator")!="Gaiacoyote":raise RuntimeError("Genus source collision")
            genus_panels[0].update(dict(panel))
        else:
            g["visual_comparison"]["items"].append(dict(panel))
        successes.append({"source_photo_number":n,"file":str(local),
            "source_page":source,"creator":"Gaiacoyote","license":"CC0 1.0",
            "source_sha256":found["source_sha256"],"archive_sha256":found["local_sha256"],
            "original_dimensions":found["original_dimensions"],"archive_dimensions":found["archive_dimensions"]})
        print("ARCHIVED_ACTUAL_CC0",n,found["original_dimensions"],flush=True)
    if not successes:
        write(HOLD,{"checked_utc":datetime.now(timezone.utc).isoformat(),
            "result":"NO_NEW_EXACT_CC0_PHOTOS","source_failures":blocked})
        return
    s["curation_status"]["photo_files_present"]=sum(
        1 for x in s["images"] if str(x.get("file","")).startswith("images/") and (SP.parent/x["file"]).is_file())
    s["curation_status"]["photo_metadata_count"]=len(s["images"])
    s["curation_status"]["texas_tridens_exact_cc0_ligule_habitat_20261027"]=(
       f"{len(successes)} photographer-licensed CC0 Texas tridens source photos now locally archived, "
       "including collar-region and habitat if both source IDs succeeded; true collar hair/lemma macro still provisional.")
    s["learner_visual_status"]["status"]="FIELD_READY_PHOTO_GAPS"
    write(SP,s);write(GEN,g)
    write(REPORT,{"created_utc":datetime.now(timezone.utc).isoformat(),
        "result":"EXACT_TRIDENS_TEXANUS_CC0_SOURCE_PHOTOS_ARCHIVED","count":len(successes),
        "photos":successes,"source_failures":blocked,"photos_current":s["curation_status"]["photo_files_present"],
        "panels_current":len(s["visual_comparison"]["items"]),
        "taxon":"Tridens texanus","photo_use":"Original by Gaiacoyote; CC0 1.0, source locality northern Uvalde County, not Hays voucher",
        "remaining":"Calibrated free ligule hairs, rooted crown attached to flowering culm, 1mm numbered spikelet and dorsal 3-nerved lemma hair macro"})
    write(MARK,{"date":"2026-10-27","taxon":"tridens-texanus",
        "report":str(REPORT),"deployment":"rights-filtered noncommercial educational Pages, check build success before live claim"})
    print("SUCCESS_ARCHIVED",len(successes),flush=True)
if __name__=="__main__":main()
