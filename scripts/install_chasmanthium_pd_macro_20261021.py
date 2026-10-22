#!/usr/bin/env python3
"""One-time, fail-closed exact-author-PD Chasmanthium spikelet import.

Source rights: Jim Conrad publicly released this specific photograph:
https://commons.wikimedia.org/wiki/File:Chasmanthium_latifolium-spikelet.jpg
Source file SHA1: 047d2ea52ecddf4dca060a33031cc22949902b66
Unambiguously NOT a Hays County provenance/photo. Only same bytes accepted.
"""
from __future__ import annotations
import csv, hashlib, io, json, urllib.request
from pathlib import Path
from PIL import Image, ImageOps

R=Path(".")
BASE=R/"content/taxa/Poaceae/Chasmanthium"
SP=BASE/"chasmanthium-latifolium/species.json"
GP=BASE/"genus.json"
CSV=BASE/"chasmanthium-latifolium/image-sources.csv"
DIR=BASE/"chasmanthium-latifolium/images"
DST=DIR/"jim-conrad-pd-chasmanthium-single-spikelet.jpg"
OUT=R/"reports/chasmanthium-pd-macro-import-20261021.json"
MARKER=R/"workflow/field-id-publication/manual-chasmanthium-singleton-pd-20261021.json"
ORIGINAL="https://upload.wikimedia.org/wikipedia/commons/9/9e/Chasmanthium_latifolium-spikelet.jpg"
FILE_PAGE="https://commons.wikimedia.org/wiki/File:Chasmanthium_latifolium-spikelet.jpg"
SOURCE_SHA1="047d2ea52ecddf4dca060a33031cc22949902b66"
LINKED="https://upload.wikimedia.org/wikipedia/commons/9/9e/Chasmanthium_latifolium-spikelet.jpg"
LOCAL="content/taxa/Poaceae/Chasmanthium/chasmanthium-latifolium/images/"+DST.name

def dump(path,obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf8")

def main():
    s=json.loads(SP.read_text(encoding="utf8"))
    g=json.loads(GP.read_text(encoding="utf8"))
    assert s["scientific_name"]=="Chasmanthium latifolium"
    assert g["project_scope"]["species_count"]==1
    assert g["project_scope"]["species_ids"]==["chasmanthium-latifolium"]
    assert len(s["visual_comparison"]["items"])==4 and len(g["visual_comparison"]["items"])==4
    spanel=s["visual_comparison"]["items"][-1]
    gpanel=g["visual_comparison"]["items"][-1]
    if DST.exists():
        if spanel["image_url"]==LOCAL and gpanel["image_url"]==LOCAL:
            assert any(x.get("file")=="images/"+DST.name for x in s["images"])
            print("Previously physically installed. NOOP.");return
        raise RuntimeError("Existing physical file but canonical cards not synchronized: HOLD for manual reconciliation")
    assert spanel["image_url"]==LINKED and gpanel["image_url"]==LINKED
    assert spanel["creator"]=="Jim Conrad" and gpanel["creator"]=="Jim Conrad"
    assert "Public domain" in spanel["license"] and "Public domain" in gpanel["license"]
    protected={k:json.dumps(s.get(k),sort_keys=True) for k in ("taxonomy_source","native_target_zone_calculated","county_occurrences_target_zone","project_inclusion")}
    scope=json.dumps(g["project_scope"],sort_keys=True)
    req=urllib.request.Request(ORIGINAL,headers={"User-Agent":"HaysBotanyCCPublicDomainPhotoVerifier/1.0 (educational Github Pages botany)"})
    with urllib.request.urlopen(req,timeout=35) as f: raw=f.read(1000000)
    assert 15000<len(raw)<100000
    sha=hashlib.sha1(raw).hexdigest()
    assert sha==SOURCE_SHA1, ("Original Wikimedia SHA1 mismatch",sha)
    with Image.open(io.BytesIO(raw)) as obj:
        assert obj.format=="JPEG" and obj.size==(400,678)
        obj.load()
        converted=ImageOps.exif_transpose(obj).convert("RGB")
    buff=io.BytesIO()
    converted.save(buff,format="JPEG",quality=92,optimize=True)
    data=buff.getvalue()
    with Image.open(io.BytesIO(data)) as im:
        assert im.size==(400,678) and not im.getexif().get(34853)
        im.verify()
    DIR.mkdir(parents=True,exist_ok=True)
    DST.write_bytes(data)
    sha256=hashlib.sha256(data).hexdigest()
    s["images"].append({
      "file":"images/"+DST.name,
      "role":"Single correctly source-identified laterally compressed Chasmanthium latifolium spikelet, visible repeated pointed overlapping florets",
      "creator":"Jim Conrad","license":"Public domain (author release)",
      "license_url":FILE_PAGE,"source_page":FILE_PAGE,"media_source_url":ORIGINAL,
      "source_locality":"Mississippi / original Jim Conrad publication, NOT a Hays specimen",
      "source_determination":"Chasmanthium latifolium (original author's image label; independent determination not re-vouchered)",
      "source_original_sha1":sha,"archived_sha256":sha256,
      "image_dimensions":[400,678],"photo_review":"Viewed on Wikimedia 2026-10-21; original exact-source bytes SHA1 and visible overlapping florets verified. No glume or seed macro claims.",
      "public_reuse":"Author released exact image into public domain worldwide; credit Jim Conrad and Commons page retained for transparency.",
      "modifications":"Re-encoded JPEG to remove EXIF and camera GPS; no annotations drawn into original pixels."
    })
    for p in (spanel,gpanel):
        p["image_url"]=LOCAL
        p["photo_status"]="PUBLIC DOMAIN Jim Conrad exact source 400×678 JPEG physically saved and original SHA1 verified 2026-10-21; altered only by EXIF-free JPEG re-encode, source/photo credit retained. Photo points to overlapping florets/flat spikelet, no individual glume/caryopsis dissection. Original Mississippi photo, no Hays provenance."
    s["visual_comparison"]["subtitle"]=s["visual_comparison"]["subtitle"].replace("EXTERNALLY", "PHYSICALLY").replace("not yet installed","now physically installed").replace("binary not yet installed","binary installed")
    g["visual_comparison"]["subtitle"]=g["visual_comparison"]["subtitle"].replace("EXTERNAL", "PHYSICALLY STORED").replace("not physically archived","physically archived")
    s["field_id_finish_pass"]["photo_sources_verified_20261021"]["external_exact_species_public_domain_closeup"]["physical_github_binary_present"]=True
    s["field_id_finish_pass"]["photo_sources_verified_20261021"]["external_exact_species_public_domain_closeup"]["review"]="REAL PHYSICAL IMAGE SHA1 MATCH AND CORRECT AUTHOR PUBLIC DOMAIN; STILL NEEDS USER MOBILE ARROW QA"
    s["curation_status"]["manual_pd_spikelet_photo_physical_20261021"]="Jim Conrad exact source public-domain JPEG physically imported, SHA1 and pixels verified, inventoried, 2 trusted broad annotations, field-ready photo gaps remain"
    g["curation_status"]["manual_pd_spikelet_photo_physical_20261021"]="Fourth panel changed from authorized external preview to verified physical source-exact public domain image, attribution preserved; older panels unaffected."
    assert json.dumps(g["project_scope"],sort_keys=True)==scope
    for k,v in protected.items():assert json.dumps(s.get(k),sort_keys=True)==v
    with CSV.open(newline="",encoding="utf8") as f:
        reader=csv.DictReader(f)
        cols=reader.fieldnames
        rows=list(reader)
    assert not any(x.get("file_name")==DST.name for x in rows)
    values={"file_name":DST.name,"role":"Flat one-spikelet multi-floret macro",
     "creator":"Jim Conrad","license":"Public domain (author release)",
     "source_page":FILE_PAGE,"direct_url":ORIGINAL,
     "study_use":"Public botanical education",
     "public_reuse":"YES, author public-domain release; attribution retained",
     "license_url":FILE_PAGE,"modifications":"Resaved as JPEG with EXIF/GPS removed"}
    rows.append({c:values.get(c,"") for c in cols})
    with CSV.open("w",newline="",encoding="utf8") as f:
        writer=csv.DictWriter(f,fieldnames=cols,lineterminator="\n")
        writer.writeheader();writer.writerows(rows)
    dump(SP,s);dump(GP,g)
    dump(OUT,{"result":"JIM_CONRAD_PD_PHOTO_PHYSICALLY_INSTALLED",
      "original_sha1":sha,"archived_sha256":sha256,"image_file":str(DST),
      "photo_credit":"Jim Conrad","license":"Public domain (author release)",
      "file_page":FILE_PAGE,"dimensions":[400,678],"source_locality":"Mississippi",
      "species_panels":4,"genus_panels":4,"arrows":10,
      "new_photo_bytes":1,"native_review_modified":False,
      "remaining":["true measured fresh ligule","dissected glumes/caryopsis","locally rooted plant","mobile overlay QA"]})
    dump(MARKER,{"type":"manual_field_id_publication","requested_at":"2026-10-21",
      "title":"Chasmanthium 1-species visual key and verified public-domain macro",
      "species":"Chasmanthium latifolium","genus":"Chasmanthium",
      "creator":"Jim Conrad","license":"Public domain by author",
      "new_physical_images":1,"species_panels":4,"genus_panels":4,"arrows":10,
      "source_original_sha1":sha,"physical_image_source_credit_in_repo":True,
      "nativities_preserved":True,"remaining_macro_gaps":"True ligule, roots and mature caryopsis/grain dissection",
      "publication":"Release via existing rights-filtered Pages. A marker is a request, not a verified successful deployment."})
    print("PASS: Jim Conrad PD original SHA1 confirmed and one EXIF-free image staged in canonical species + genus")
if __name__=="__main__":main()
