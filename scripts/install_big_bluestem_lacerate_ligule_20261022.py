#!/usr/bin/env python3
"""Fail-closed archive of one real Matt Lavin CC BY-SA 2.0 big bluestem ligule macro.
Source and CC verified: https://commons.wikimedia.org/wiki/File:Andropogon_gerardii_-_4055509299.jpg
No new guessed pixel arrows, accepted-name or Hays native-range changes.
"""
import csv, hashlib, io, json, urllib.request
from pathlib import Path
from PIL import Image, ImageOps
ROOT=Path(".")
BASE=ROOT/"content/taxa/Poaceae/Andropogon/andropogon-gerardi"
CARD=BASE/"species.json"
CSV=BASE/"image-sources.csv"
DEST=BASE/"images/matt-lavin-2009-lacerated-ligule.jpg"
REPORT=ROOT/"reports/big-bluestem-lacerated-ligule-licensed-photo-20261022.json"
MARKER=ROOT/"workflow/field-id-publication/2026-10-22-big-bluestem-ligule-real-archived.json"
PAGE="https://commons.wikimedia.org/wiki/File:Andropogon_gerardii_-_4055509299.jpg"
FLICKR="https://live.staticflickr.com/2763/4055509299_a245b51b05_o.jpg"
COMMONS="https://commons.wikimedia.org/wiki/Special:Redirect/file/Andropogon%20gerardii%20-%204055509299.jpg"
EXPECTED_SHA1="8618950eaffb82bce6c70f058948db2970519471"
LICENSE="https://creativecommons.org/licenses/by-sa/2.0/"

def save(p,record):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(record,indent=2,ensure_ascii=False)+"\n",encoding="utf8")

def main():
    s=json.loads(CARD.read_text(encoding="utf8"))
    assert s["id"]=="andropogon-gerardi"
    prior={k:json.dumps(s.get(k),sort_keys=True) for k in
           ("project_inclusion","county_occurrences_target_zone","native_target_zone_calculated",
            "target_zone_count","synonyms","taxonomic_note")}
    matching=[x for x in s["visual_comparison"]["items"] if x.get("source_page")==PAGE]
    if len(matching)!=1 or matching[0].get("creator")!="Matt Lavin" or matching[0].get("license")!="CC BY-SA 2.0" or matching[0].get("markers"):
        raise RuntimeError("Canonical image identity/source/annotation state changed: HOLD")
    panel=matching[0]
    relative="images/"+DEST.name
    if DEST.exists():
        if any(i.get("file")==relative for i in s["images"]) and panel["image_url"]==str(DEST):
            with Image.open(DEST) as image: image.verify()
            print("ALREADY_INSTALLED_NOOP");return
        raise RuntimeError("Partial previously archived state; HOLD")
    if any(x.get("file")==relative for x in s["images"]):
        raise RuntimeError("Existing image metadata without file; HOLD")
    if not panel["image_url"].startswith("https://"):
        raise RuntimeError("Externally prepared panel no longer external; HOLD")
    with CSV.open(newline="",encoding="utf8") as f:
        reader=csv.DictReader(f);columns=reader.fieldnames;rows=list(reader)
    if not columns or "file_name" not in columns or any(row.get("file_name")==DEST.name for row in rows):
        raise RuntimeError("Photo source CSV changed/duplicate; HOLD")
    raw=None;source=None;errors=[]
    for url in (FLICKR,COMMONS):
        try:
            req=urllib.request.Request(url,headers={
                "User-Agent":"Mozilla/5.0 (Hays County Botany public CC attribution validation)",
                "Accept":"image/jpeg,image/*"})
            with urllib.request.urlopen(req,timeout=32) as rsp:
                sample=rsp.read(2_500_000)
            if not (12000<len(sample)<2_500_000):
                raise ValueError("bad image byte size")
            if hashlib.sha1(sample).hexdigest()!=EXPECTED_SHA1:
                raise ValueError("source byte SHA1 differs from Commons published checksum")
            raw=sample;source=url;break
        except Exception as exc:
            errors.append(type(exc).__name__+": "+str(exc)[:160])
    if raw is None:
        raise RuntimeError("Cannot verify the exact photographer image; no files installed. "+repr(errors))
    with Image.open(io.BytesIO(raw)) as source_im:
        source_im.load()
        if source_im.format!="JPEG" or source_im.size!=(1320,772):
            raise RuntimeError("File dimensions / JPEG authenticity differ from Commons: HOLD")
        rgb=ImageOps.exif_transpose(source_im).convert("RGB")
    buf=io.BytesIO()
    rgb.save(buf,format="JPEG",quality=92,optimize=True)
    data=buf.getvalue()
    with Image.open(io.BytesIO(data)) as review:
        assert review.format=="JPEG" and min(review.size)>700
        assert not review.getexif().get(34853)
        review.verify()
    DEST.parent.mkdir(parents=True,exist_ok=True)
    DEST.write_bytes(data)
    archived_hash=hashlib.sha256(data).hexdigest()
    original_hash=hashlib.sha256(raw).hexdigest()
    s["images"].append({
        "file":relative,"role":"Real lacerated membranous ligule macro, original author's exact Andropogon gerardii photograph (new accepted Andropogon gerardi)",
        "creator":"Matt Lavin","license":"CC BY-SA 2.0","license_url":LICENSE,
        "source_page":PAGE,"original_source_page":"https://www.flickr.com/photos/plant_diversity/4055509299/",
        "direct_image_url":source,"photo_credit":"Matt Lavin, original CC BY-SA 2.0; original photographer's tissue image unretouched",
        "source_date":"2009-10-29","source_identity":"Andropogon gerardii source synonym, accepted Andropogon gerardi",
        "source_original_sha1":EXPECTED_SHA1,"source_original_sha256":original_hash,
        "archived_sha256":archived_hash,"image_dimensions":[rgb.width,rgb.height],
        "source_locality_note":"Photographer record does not establish Hays County site or voucher",
        "photo_review":"True species-labelled ligule macro and lacerated membranous edge; NO actual millimeter ruler or independent specimen voucher; no new arrows guessed",
        "public_reuse":"CC BY-SA 2.0 with author credit, license link and indication of JPEG metadata-stripping re-encode",
        "modifications":"RGB JPEG re-encode strips EXIF/GPS; no image part painted and no anatomical arrows added"
    })
    panel["image_url"]=str(DEST)
    panel["photo_status"]="PHYSICALLY ARCHIVED VERIFIED CC BY-SA 2.0 Matt Lavin 2009 source JPEG. Matched published Commons original SHA1, decoded / metadata cleaned, archived SHA256 recorded. Lacerated membranous ligule present but NO 1mm scale, NO new pixel annotations, NOT Hays voucher.";
    if "diagnostic_photo_second_pass_20261022" in s:
        s["diagnostic_photo_second_pass_20261022"]["photo_source_addendum_20261022"]["physical_photo_archived"]=True
        s["diagnostic_photo_second_pass_20261022"]["photo_source_addendum_20261022"]["archived_filename"]=relative
        s["diagnostic_photo_second_pass_20261022"]["source_photo_status"]["new_physical_image_files"]=1
    s["curation_status"]["second_ligule_photo_20261022"]["external_original"]=False
    s["curation_status"]["second_ligule_photo_20261022"]["physical_real_photo_archived"]=True
    for k,v in prior.items():
        if json.dumps(s.get(k),sort_keys=True)!=v:raise RuntimeError("Protected science status changed")
    values={"file_name":DEST.name,"role":"Second authentic big bluestem ligule with lacerated membranous upper edge",
            "platform":"Wikimedia Commons / Flickr verified source","observation_id":"", "photo_id":"4055509299",
            "creator":"Matt Lavin","license":"CC BY-SA 2.0","license_url":LICENSE,"source_page":PAGE,
            "direct_image_url":source,"study_use":"yes","public_reuse":"yes - CC BY-SA terms",
            "source_context":"Photographer source matched exact original SHA1 on Commons. EXIF/GPS stripped on archive. No Texas specimen voucher/1mm size."}
    rows.append({k:values.get(k,"") for k in columns})
    with CSV.open("w",newline="",encoding="utf8") as f:
        writer=csv.DictWriter(f,fieldnames=columns,lineterminator="\n")
        writer.writeheader();writer.writerows(rows)
    save(CARD,s)
    save(REPORT,{"status":"ACTUAL_LIGULE_JPEG_ARCHIVED","path":str(DEST),"source":PAGE,
       "creator":"Matt Lavin","license":"CC BY-SA 2.0","original_sha1":EXPECTED_SHA1,
       "original_sha256":original_hash,"stored_sha256":archived_hash,
       "dimensions":[rgb.width,rgb.height],"new_actual_photos":1,"species_panels":len(s["visual_comparison"]["items"]),
       "taxon_nativity_holds_unchanged":True,"last_mile": [
        "Same local plant true collar and inner sheath with 1 mm rule versus Paspalum floridanum",
        "Hays exact fully attached sessile+pedicellate spikelet pair / awn origin measured"]})
    save(MARKER,{"type":"manual_field_id_publication","requested_at":"2026-10-22",
       "title":"Big bluestem real source-verified lacerate ligule JPEG",
       "taxon":"Andropogon gerardi","photo_count_added":1,"source":PAGE,
       "creator":"Matt Lavin","license":"CC BY-SA 2.0",
       "current_status":"FIELD_READY_PHOTO_GAPS",
       "native_science_holds_unchanged":True,"publish_via":"existing rights-filtered GitHub Pages workflow"})
    print("PASS: photo physical, source exact SHA1, JPEG validated, per-photo CC attribution, no anatomy guessing")

if __name__=="__main__":
    main()
