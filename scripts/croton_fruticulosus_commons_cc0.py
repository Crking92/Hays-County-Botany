#!/usr/bin/env python3
"""Strictly verify two individual Commons CC0 Croton fruticulosus photos, append public-safe media only.
Does not change taxonomy/range or invent tissue arrows. An exact-source candidate is not an
installed photo until downloaded, decoded, and read back from the canonical repository.
"""
import csv, io, json, pathlib, requests, sys
from PIL import Image, ImageOps
ROOT=pathlib.Path(".")
P=ROOT/"content/taxa/Euphorbiaceae/Croton/croton-fruticulosus"
SPEC=P/"species.json"
SOURCES=[
 ("File:Croton fruticulosus (2).jpg","commons-gaiacoyote-cc0-female-flower.jpg",
  "Female flower and nearby developing flower buds; source photo shows style arms but six final ends need careful macro review",
  "Source-proven female flower and buds; do not label male stamens or count six tips from an unresolved image"),
 ("File:Croton fruticulosus (3).jpg","commons-gaiacoyote-cc0-underside-hairs.jpg",
  "Abaxial leaf surface with stellate hairs; source identified, fine marginal teeth not necessarily pictured",
  "Source-proven leaf underside with stellate hair texture; NOT a verified tooth-by-tooth margin macro")
]
session=requests.Session()
session.headers.update({"User-Agent":"HaysCountyBotanyEducationalLearner/1.0 (photo-rights verification; github.com/Crking92/Hays-County-Botany)"})
def request_info():
    r=session.get("https://commons.wikimedia.org/w/api.php",params={
      "action":"query","format":"json","prop":"imageinfo","iiprop":"url|extmetadata","titles":"|".join(x[0] for x in SOURCES)},timeout=40)
    r.raise_for_status();j=r.json();info={}
    for page in j.get("query",{}).get("pages",{}).values():
        if "missing" in page:raise RuntimeError("Missing Commons page "+str(page))
        ii=page.get("imageinfo") or []
        if not ii:raise RuntimeError("Missing per-image Commons metadata")
        info[page["title"]]=ii[0]
    return info
def save_csv(entries):
    f=P/"image-sources.csv"
    with f.open(newline="",encoding="utf-8-sig") as h:
        rr=csv.DictReader(h); columns=list(rr.fieldnames or []); rows=list(rr)
    for e in entries:
        for k in e:
            if k not in columns:columns.append(k)
        rows.append(e)
    with f.open("w",newline="",encoding="utf-8") as h:
        w=csv.DictWriter(h,fieldnames=columns,lineterminator="\n")
        w.writeheader();w.writerows(rows)
def main():
    current=json.loads(SPEC.read_text())
    assert current["id"]=="croton-fruticulosus"
    assert current.get("project_inclusion",{}).get("target_zone_status")=="PASS"
    prior=json.loads((ROOT/"workflow/work-claims.json").read_text())
    active=[c for c in prior.get("claims",[]) if "croton-fruticulosus" in c.get("taxa",[]) and c.get("status") in ("active","claimed","in_progress")]
    if active:raise RuntimeError("Species claimed by another worker; refuse overwrite")
    if any(str(x.get("file","")).startswith("images/commons-gaiacoyote-cc0-") for x in current["images"]):
        print("Already installed. No-op.");return
    info=request_info();found=[]
    for title,filename,role,caption in SOURCES:
        if title not in info:raise RuntimeError("Unexpected Commons title missing "+title)
        ii=info[title];e=ii.get("extmetadata",{})
        short=str(e.get("LicenseShortName",{}).get("value","")).upper()
        us=str(e.get("UsageTerms",{}).get("value","")).upper()
        artist=str(e.get("Artist",{}).get("value",""))
        if "CC0" not in short+" "+us:
            raise RuntimeError("Photo-specific CC0 proof absent: "+title+" license="+short)
        if "gaiacoyote" not in artist.lower():
            raise RuntimeError("Photo-specific photographer mismatch: "+title+" / "+artist[:100])
        url=str(ii.get("url",""))
        if not url.startswith("https://upload.wikimedia.org/wikipedia/commons/"):
            raise RuntimeError("Unexpected URL")
        resp=session.get(url,timeout=40)
        resp.raise_for_status()
        if len(resp.content)>10_000_000:raise RuntimeError("Oversize media")
        with Image.open(io.BytesIO(resp.content)) as im:
            im.load();out=ImageOps.exif_transpose(im).convert("RGB")
        if min(out.size)<375 or max(out.size)<440:raise RuntimeError("Resolution too small: "+title)
        out.thumbnail((1600,1600))
        buf=io.BytesIO();out.save(buf,format="JPEG",quality=91,optimize=True)
        if len(buf.getvalue())<13000:raise RuntimeError("Tiny image bytes: "+title)
        found.append((title,filename,role,caption,buf.getvalue(),list(out.size),url))
    # All source checks and downloads completed before mutating any files.
    add_csv=[]
    for title,filename,role,caption,data,dimensions,url in found:
        dest=P/"images"/filename
        if dest.exists():raise RuntimeError("Refuse overwrite "+str(dest))
        dest.write_bytes(data)
        with Image.open(dest) as check:check.verify()
        src="https://commons.wikimedia.org/wiki/"+title.replace("File:","File:").replace(" ","_")
        record={"file":"images/"+filename,"role":role,"creator":"Gaiacoyote","license":"CC0 1.0",
         "license_url":"https://creativecommons.org/publicdomain/zero/1.0/","source_platform":"Wikimedia Commons",
         "source_page":src,"downloaded_from":url,"image_dimensions":dimensions,
         "study_use":"yes","public_reuse":"yes","modifications":"JPEG recompression and metadata/EXIF/GPS removal; no synthetic imagery or drawn arrows",
         "photo_review":"Photo-specific Commons page labels this original Gaiacoyote CC0 and identifies exact species; structure caption based on source description; owner mobile arrow/ID check remains."}
        current["images"].append(record)
        add_csv.append({"file_name":filename,"role":role,"creator":"Gaiacoyote","license":"CC0 1.0",
          "license_url":record["license_url"],"source_page":src,"direct_image_url":url,
          "study_use":"yes","public_reuse":"yes","source_context":"Physically installed, verified Wikimedia image metadata and decoded JPEG; EXIF removed"})
        current["visual_comparison"]["items"].append({
          "label":"CC0 photo · "+("female flower" if "(2)" in title else "abaxial star hairs"),
          "scientific_name":"Croton fruticulosus","image_url":"content/taxa/Euphorbiaceae/Croton/croton-fruticulosus/images/"+filename,
          "image_fit":"contain","creator":"Gaiacoyote","license":"CC0 1.0","source_page":src,
          "image_role":role,"caption":caption,"why_it_matters":"Shows a structural detail missing from the two initial owner field views; do not pretend this proves woody crown or leaf-edge teeth.",
          "markers":[]})
    save_csv(add_csv)
    current["curation_status"]["photo_metadata_count"]=len(current["images"])
    current["curation_status"]["photo_files_present"]=len([z for z in current["images"] if str(z.get("file","")).startswith("images/")])
    current["curation_status"]["visual_status"]="FIELD_READY_PHOTO_GAPS: added two verified CC0 Gaiacoyote exact-species reproductive/underside photos; basal woody crown and verified tiny leaf-edge teeth still pending."
    current["learner_visual_status"]["image_count"]=len(current["images"])
    current["photo_note"]+=" Added CC0 Commons female flower and leaf-underside macros (2026-10-21). No unsupported anatomy arrow coordinates were invented."
    targets=current.get("diagnostic_photo_targets",[])
    for target in targets:
        if target.get("status")=="CC0_CANDIDATE_NOT_INSTALLED":target["status"]="PHOTO_INSTALLED_NEEDS_PRECISE_ANATOMY_ARROW_REVIEW"
    current["visual_comparison"]["subtitle"]="Two owner-authorized Glass Root Garden photos and two physically stored Gaiacoyote CC0 structure photos. Two original genus arrows reused; new macroscopic style/hair photo markers await independent arrow coordinate verification."
    current["visual_comparison"]["annotation_status"]="Two inherited genus annotations only; the newly installed CC0 images remain unannotated until actual precise arrows can be verified."
    with (P/"SOURCES.txt").open("a",encoding="utf-8") as h:
        h.write("\n2026-10-21 TWO COMMONS GAIACOYOTE CC0 EXACT-SPECIES PHOTO ENRICHMENT\n")
        for title,_,_,_,_,_,_ in found:h.write(title+" / CC0 1.0 / photographer Gaiacoyote\n")
        h.write("License individually checked against Wikimedia Commons imageinfo before download. No change to target-zone nativity or taxonomy.\n")
    SPEC.write_text(json.dumps(current,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({"status":"installed","species":current["id"],"new_photos":len(found),
      "total_records":len(current["images"]),"new_licensed":True,
      "new_photo_arrows":0,"preserved_native_range":current["project_inclusion"]["target_zone_status"]},indent=2))
if __name__=="__main__":main()
