#!/usr/bin/env python3
"""Install a full-resolution historical grass botanical plate as provisional offline study media.

The page depicts MULTIPLE Muhlenbergia taxa; NOT a diagnostic, exclusive plant photo.
Do not edit taxonomy/range, or infer all figures show M. x involuta.
"""
import datetime,hashlib,json,pathlib,sys,subprocess,urllib.request,io
from PIL import Image
R=pathlib.Path(".");sys.path.insert(0,str(R.resolve()))
from scripts.manual_external_mirror_review_024 import clean
from scripts.manual_library_photo_install_010 import signature,blocked_claims
from scripts.gbif_exact_zero_photo_recovery import csvappend
SID="muhlenbergia-x-involuta"
OUT=R/"reports/manual-external-mirror-install-024-20261016.json"
BHL="https://www.biodiversitylibrary.org/pageimage/42021050"
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def main():
    preview=read(R/"reports/manual-external-mirror-review-024/preview-manifest.json")
    refs={r["id"]:r["path"] for r in read(R/"data/manifest.json")["species"]}
    report={"batch":"external-mirror-install-024","installed":[],"skipped":[],
      "science_unchanged":True,"living_plant_photo_installed":False,
      "warning":"Historic page contains multiple Muhlenbergia species. Only labeled M. x involuta figure applies; a real field photo remains needed."}
    if SID in blocked_claims():
        report["skipped"].append({"id":SID,"reason":"Unexpired active claim"});OUT.write_text(json.dumps(report,indent=2)+"\n");return
    path=R/refs[SID];sp=read(path);before=signature(sp)
    assert sp["scientific_name"]=="Muhlenbergia ×involuta"
    gallery=sp.get("images") or []
    if len(gallery)!=1 or not gallery[0]["file"].startswith("https://"):
        raise ValueError("Gallery changed or already locally installed; manual reconciliation required")
    original=gallery[0];cand=preview["species"][0]["candidates"][0]
    assert preview["species"][0]["id"]==SID and cand["status"]=="downloaded_for_visual_review"
    assert cand["original_url"]==original["file"]
    assert cand["license"]=="Public Domain Mark 1.0"
    req=urllib.request.Request(BHL,headers={"User-Agent":"HaysBotanyStudy/1.0","Accept":"image/jpeg,image/*"})
    with urllib.request.urlopen(req,timeout=32) as resp:raw=resp.read(14000001)
    if len(raw)>14000000:raise ValueError("Large image; refusing to install")
    with Image.open(io.BytesIO(raw)) as im:
        im.load()
        width,height=im.size
        fmt=im.format
    if [width,height]!=cand["original_dimensions"]:
        raise ValueError("Original plate dimensions no longer match visual review")
    normalized,dim,photo=clean(raw)
    assert hashlib.sha256(normalized).hexdigest()==cand["sha256_of_normalized_jpeg"],"Photo pixels differ from visual review"
    # BHL can serve the public-domain page as PNG despite the Commons JPEG alias.
    # Save the source pixels to a full-resolution JPEG for stable offline gallery use.
    with Image.open(io.BytesIO(raw)) as original_image:
        original_image.load()
        rgb=original_image.convert("RGB")
    output_buffer=io.BytesIO()
    rgb.save(output_buffer,format="JPEG",quality=91,optimize=True,progressive=True)
    saved=output_buffer.getvalue()
    sha=hashlib.sha256(saved).hexdigest()
    name="bhl42021050-multi-taxon-plate-"+sha[:12]+".jpg"
    output=path.parent/"images"/name
    if output.exists():raise ValueError("No overwrite permitted")
    output.parent.mkdir(parents=True,exist_ok=True);output.write_bytes(saved)
    entry={"file":"images/"+name,
      "role":"HISTORICAL MULTI-TAXON BOTANICAL PLATE. Locate only the labeled Muhlenbergia involuta illustration; other labeled figures represent different grasses. NOT a field photograph.",
      "creator":"A. S. Hitchcock and Agnes Chase / Biodiversity Heritage Library",
      "license":"Public Domain Mark 1.0",
      "source_page":original["source_page"],"original_image_page":BHL,
      "source_type":"Historical public-domain botanical illustration",
      "photo_review":"Visual page reviewed; figure labels must be consulted, botanical identity not expert verified",
      "learner_visual_status":"PROVISIONAL_ILLUSTRATION_ONLY_NEEDS_REAL_PHOTOS",
      "public_reuse":"Public Domain Mark 1.0; attribution encouraged",
      "anatomy_arrows":"none — multi-taxon page, no automated annotation"}
    sp["images"].append(entry)
    st=sp.setdefault("curation_status",{})
    st["photo_metadata_count"]=len(sp["images"]);st["photo_files_present"]=1
    sp["photo_note"]=((sp.get("photo_note") or "")+" Full-resolution BHL plate mirrored locally for offline reference. This multi-taxon plate is NOT a verified live M. ×involuta photograph; exact living-plant views remain missing.").strip()
    assert signature(sp)==before,"Unexpected change in scientific data"
    path.write_text(json.dumps(sp,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    csvappend(path.parent/"image-sources.csv",{"file_name":name,"role":entry["role"],
      "creator":entry["creator"],"license":entry["license"],"source_page":entry["source_page"],
      "direct_url":BHL,"public_reuse":entry["public_reuse"],"visual_caution":entry["learner_visual_status"]})
    with (path.parent/"SOURCES.txt").open("a",encoding="utf-8") as f:
        f.write("\nBHL MULTI-TAXON PLATE REVIEW 024 (2026-10-16)\n"+BHL+"\n"+
        "Full-resolution page is historical public-domain source (Hitchcock/Chase); multiple Muhlenbergia figures shown. Confirm the label for M. involuta; field photo still needed.\n")
    report["installed"].append({"id":SID,"photo_file":str(output),"sha256":sha,
        "source":BHL,"license":entry["license"],"type":"multi-taxon historical illustration"})
    OUT.write_text(json.dumps(report,indent=2)+"\n")
    subprocess.run([sys.executable,"scripts/refresh_photo_coverage_snapshot.py"],check=True)
    print(json.dumps({"local_plate_installed":1,"living_plant_photo_installed":False},indent=2))
if __name__=="__main__":main()
