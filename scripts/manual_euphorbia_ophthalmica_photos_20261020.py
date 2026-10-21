#!/usr/bin/env python3
"""Add image-level licensed, exact-name Wikimedia E. ophthalmica source photos.

Each original photo is verified via Wikimedia Commons imageinfo metadata and
downloaded as a real, decoded JPEG, before any canonical metadata change.
Diagnostic arrows are not invented: saved images must first be inspected.
"""
from pathlib import Path
from urllib.parse import quote
import csv, hashlib, io, json, re, time, html
import requests
from PIL import Image, ImageOps

BASE=Path("content/taxa/Euphorbiaceae/Euphorbia/euphorbia-ophthalmica")
CARD=BASE/"species.json"
CSV=BASE/"image-sources.csv"
REPORT=Path("reports/euphorbia-ophthalmica-commons-photo-intake-20261020.json")
API="https://commons.wikimedia.org/w/api.php"
SOURCES=[
("Euphorbia ophthalmica.jpg","images/02-roget-flowering-plant.jpg","Original broad plant habit/flowering branch from photographed specimen"),
("Euphorbia ophthalmica (1).jpg","images/03-gaiacoyote-inflorescence-hairs.jpg","Original close-up of round cyathium heads and fine hairs"),
("Euphorbia ophthalmica (2).jpg","images/04-gaiacoyote-leaf-reproductive-view.jpg","Another detailed photographic view of leaves and head placement"),
("Euphorbia ophthalmica (3), mat-forming plant on very hot limestone step.jpg","images/05-gaiacoyote-prostrate-habit.jpg","In-situ low growth habit on limestone in Guatemala; geographic comparison, not a Hays native-range observation"),
]

def text_only(s):
    return html.unescape(re.sub(r"<[^>]+>","",s or "")).strip()

def fetch(session,name):
    resp=session.get(API,params={"action":"query","format":"json","formatversion":"2",
       "prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":"1500",
       "titles":"File:"+name},timeout=65)
    resp.raise_for_status()
    pages=resp.json()["query"]["pages"]
    assert len(pages)==1 and "missing" not in pages[0],name
    record=pages[0]["imageinfo"][0]
    meta=record["extmetadata"]
    license_name=text_only(meta["LicenseShortName"]["value"])
    license_url=html.unescape(meta["LicenseUrl"]["value"])
    artist=text_only(meta["Artist"]["value"])
    assert artist and len(artist)<220,(name,artist)
    assert "creativecommons.org/licenses/by" in license_url,(name,license_url)
    assert "nd" not in license_url.lower().split("/licenses/")[-1].split("/")[0]
    assert re.search(r"/licenses/by(?:-sa)?/[234]\.0/",license_url),(name,license_url)
    assert ("CC BY" in license_name or "CC-BY" in license_name),(name,license_name)
    url=record.get("thumburl") or record["url"]
    assert url.startswith("https://")
    binary=session.get(url,timeout=80)
    binary.raise_for_status()
    raw=binary.content
    assert 10000<len(raw)<15000000,(name,len(raw))
    with Image.open(io.BytesIO(raw)) as original:
        original.load()
        assert original.format in ("JPEG","PNG"),(name,original.format)
        assert min(original.size)>=440,(name,original.size)
        original_dimensions=list(original.size)
        safe=ImageOps.exif_transpose(original).convert("RGB")
    safe.thumbnail((1700,1700),Image.Resampling.LANCZOS)
    out=io.BytesIO()
    safe.save(out,"JPEG",quality=91,optimize=True)
    content=out.getvalue()
    assert len(content)>13000,(name,len(content))
    with Image.open(io.BytesIO(content)) as probe: probe.verify()
    return content,dict(creator=artist,license=license_name,license_url=license_url,
       source_sha256=hashlib.sha256(raw).hexdigest(),
       image_dimensions=list(safe.size),original_image_dimensions=original_dimensions,
       downloaded_from=url)

def run():
    j=json.loads(CARD.read_text(encoding="utf-8"))
    assert j["scientific_name"]=="Euphorbia ophthalmica"
    assert j["field_id_finalization"]["stage"]=="PASS_IN_PROGRESS"
    assert len(j["images"]) in (1,5),len(j["images"])
    expected={rel for _,rel,_ in SOURCES}
    if len(j["images"])==5:
        assert expected.issubset({x["file"] for x in j["images"]})
        assert all((BASE/x["file"]).is_file() for x in j["images"])
        print("EXISTING four checked image records; no re-download needed.")
        return
    assert j["images"][0]["file"]=="images/inat-153476082.jpg"
    assert j["images"][0]["license"]=="CC BY-NC"
    assert (BASE/j["images"][0]["file"]).is_file()
    session=requests.Session()
    session.headers["User-Agent"]="HaysCountyBotanyCrewLearner/1.0 (https://github.com/Crking92/Hays-County-Botany)"
    collected=[]
    for name,rel,role in SOURCES:
        assert not (BASE/rel).exists(),rel
        last=""
        for attempt in range(3):
            try:
                content,rights=fetch(session,name)
                collected.append((name,rel,role,content,rights))
                break
            except Exception as ex:
                last=str(ex)[:500]
                if attempt==2:raise RuntimeError("Photo license/byte check HOLD for "+name+": "+last)
                time.sleep(3)
    for name,rel,role,content,rights in collected:
        dest=BASE/rel
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(content)
        page="https://commons.wikimedia.org/wiki/File:"+quote(name.replace(" ","_"),safe="._-(),")
        j["images"].append({
          "file":rel,"role":role,"source_page":page,"platform":"Wikimedia Commons",
          "study_use":"educational public learner","public_reuse":"yes",
          "photo_review":"Individual Commons File title exact Euphorbia ophthalmica; photographer and verified CC BY-family license from live photo metadata. Actual image bytes downloaded/decoded. Anatomical arrows pending original pixel review; no local Texas provenance asserted.",
          "modifications":"Downscaled JPEG copy, EXIF stripped; actual photo unchanged; pointers displayed as overlay only.",
          "anatomy_arrows":[],**rights
        })
    assert len(j["images"])==5
    j["curation_status"].update({"photo_metadata_count":5,"photo_files_present":5,
       "photo_source_checked":True,"visual_reviewed":False,
       "field_status":"REAL_GALLERY_INSTALLED_BUT_MICRO_ARROWS_PENDING"})
    j["learner_visual_status"].update({"image_count":5,"status":"field_ready_photo_gaps",
      "note":"Five exact-name real saved source photos: the original CC BY-NC plus four individually licensed Wikimedia photographs of habit/reproductive structures; saved pixel target review pending, seed/stipule macros still missing."})
    j["field_id_finalization"]["real_source_photos_annotated"]=0
    j["field_id_finalization"]["verified_anatomy_arrows"]=0
    j["field_id_finalization"]["photo_rights"]="One originally existing CC BY-NC iNat photo conditional on genuinely noncommercial educational site; four Wikimedia CC BY/CC BY-SA author-and-license-verified exact-species original photos; no unverified third-party source."
    j["photo_note"]+=" Four individually licensed Wikimedia Commons source photos of flowering structures and habit physically installed; anatomy arrows to be verified after image readback."
    CARD.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    with CSV.open(newline="",encoding="utf-8") as f:
        reader=csv.DictReader(f);header=reader.fieldnames;rows=list(reader)
    for name,rel,role,content,rights in collected:
        row={k:"" for k in header}
        details={"file_name":Path(rel).name,"role":role,"creator":rights["creator"],
         "license":rights["license"],"source_page":"https://commons.wikimedia.org/wiki/File:"+quote(name.replace(" ","_"),safe="._-(),"),
         "direct_url":rights["downloaded_from"],"study_use":"educational website","public_reuse":"yes"}
        for key,value in details.items():
            if key in row:row[key]=value
        rows.append(row)
    with CSV.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=header,lineterminator="\n");writer.writeheader();writer.writerows(rows)
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps({"species":"Euphorbia ophthalmica","review_date":"2026-10-20",
      "added_photos":[{"name":name,"file":rel,"role":role,**rights} for name,rel,role,content,rights in collected],
      "original_image_preserved":True,"nativity_review":"left unreviewed",
      "unverified_anatomy_arrow_count":0,
      "note":"All image license/source checks and physical file decode passed. Not equivalent to botanical anatomical macro verification."},indent=2)+"\n",encoding="utf-8")
    print("PASS: four real exact-name Commons photos, all source-level CC licenses, existing original preserved; total five.")
if __name__=="__main__":run()
