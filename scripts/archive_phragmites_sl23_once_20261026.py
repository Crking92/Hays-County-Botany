#!/usr/bin/env python3
"""One-shot rights-gated Phragmites reproductive photograph installation.
No automatic retries, no taxonomy/lineage inference, no synthetic arrows.
Triggered by the user-approved, non-scheduled photo-finishing push workflow.
"""
import hashlib, html, io, json, os, re, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image, ImageOps

ROOT=Path("content/taxa/Poaceae/Phragmites/phragmites-australis")
SPEC=ROOT/"species.json"
PHOTO=ROOT/"images/species-europe-stefan-lefnaer-sl23-spikelet.jpg"
REPORT=Path("reports/phragmites-sl23-reproductive-photo-retry-20261026.json")
PAGE="https://commons.wikimedia.org/wiki/File:Phragmites_australis_sl23.jpg"
TITLE="File:Phragmites australis sl23.jpg"
HEADERS={"User-Agent":"HaysBotanyPublicLearner/1.0 (educational photo license verification; github.com/Crking92/Hays-County-Botany)"}
def get(url,accept="application/json"):
    request=urllib.request.Request(url,headers=dict(HEADERS,Accept=accept))
    with urllib.request.urlopen(request, timeout=35) as response:
        return response.read(14000000)
def plain(s):
    return html.unescape(re.sub(r"<[^>]+>"," ",s)).strip()
def save_report(obj):
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
def run():
    result={"source":PAGE,"status":"HELD","date":"2026-10-26",
        "intent":"licensed source-confirmed species-level glume/lemma morphology, not lineage"},
    try:
        q=urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo",
              "iiprop":"url|extmetadata|size","titles":TITLE})
        js=json.loads(get("https://commons.wikimedia.org/w/api.php?"+q))
        info=next(iter(js["query"]["pages"].values()))["imageinfo"][0]
        md=info.get("extmetadata",{})
        creator=plain(md.get("Artist",{}).get("value",""))
        license=md.get("LicenseShortName",{}).get("value","")
        desc=plain(md.get("ImageDescription",{}).get("value",""))
        if "Stefan.lefnaer" not in creator or re.sub(r"[^a-z0-9]","",license.lower())!="ccbysa40":
            raise ValueError("individual author/CC BY-SA 4.0 verification failed")
        if "Phragmites" not in desc or not any(s in desc.lower() for s in ("spikelet","glum","lemma","ährchen","spelz")):
            raise ValueError("species and reproductive organ description not established")
        raw=get(info["url"],"image/jpeg")
        if not raw.startswith(b"\xff\xd8") or len(raw)<25000:
            raise ValueError("wrong image signature or unexpected bytes")
        with Image.open(io.BytesIO(raw)) as im: im.verify()
        with Image.open(io.BytesIO(raw)) as im:
            original=im.size
            if min(original)<600 or max(original)<1600:
                raise ValueError("image does not support diagnostic macro")
            img=ImageOps.exif_transpose(im).convert("RGB")
            img.thumbnail((3600,3600))
            dest=io.BytesIO();img.save(dest,format="JPEG",quality=91,optimize=True)
            processed=dest.getvalue()
            size=list(img.size)
        if PHOTO.exists():
            result.update(status="ALREADY_ARCHIVED",sha256=hashlib.sha256(PHOTO.read_bytes()).hexdigest())
            save_report(result);return
        d=json.loads(SPEC.read_text(encoding="utf-8"))
        images=d.setdefault("images",[])
        if any(x.get("file")==("images/"+PHOTO.name) for x in images):
            raise ValueError("canonical image metadata already installed but archive absent")
        # Source-level identity only. Existing authored photo labels are preserved; no guessed arrows.
        source={"file":"images/"+PHOTO.name,
          "role":"Phragmites australis actual photographed spikelet, author-labelled glume/lemma comparison; Austria species-level only, not a certified Texas/native/Gulf/introduced lineage",
          "creator":"Stefan.lefnaer","license":"CC BY-SA 4.0",
          "license_url":"https://creativecommons.org/licenses/by-sa/4.0/",
          "source_page":PAGE,"source_taxon_name":"Phragmites australis sensu Fischer et al. 2008",
          "source_dimensions":list(original),"archived_dimensions":size,
          "archived_sha256":hashlib.sha256(processed).hexdigest(),
          "modifications":"EXIF/GPS removed, converted RGB and resized to 3600 px max; photographer's labels retained",
          "photo_status":"ORIGINAL IMAGE BYTES VERIFIED; source-annotated structures; owner visual-arrow review pending",
          "lineage_caution":"This Austria species-level image cannot determine americanus vs introduced australis vs Gulf berlandieri in Texas"}
        base="content/taxa/Poaceae/Phragmites/phragmites-australis/images/"+PHOTO.name
        items=d["visual_comparison"]["items"]
        panel={"label":"SPIKELET GLUMES AND LEMMA — labelled source anatomy, lineage unknown",
          "scientific_name":"Phragmites australis","image_url":base,"image_fit":"contain",
          "image_role":"Source-labelled reproductive anatomy: distinguish persistent glumes from basal sterile-floret lemma without determining lineage",
          "caption":"Stefan.lefnaer's actual Phragmites spikelet anatomy from Austria, showing photographer-labelled glume and lemma positions. Use this to prevent accidentally measuring a long sterile-floret lemma as an upper glume. No genotype/Texas lineage inference.",
          "why_it_matters":"Pinpoints the botanical measurement trap before comparing mature upper and lower glumes across native, introduced and Gulf lineages.",
          "creator":"Stefan.lefnaer","license":"CC BY-SA 4.0",
          "license_url":"https://creativecommons.org/licenses/by-sa/4.0/",
          "source_page":PAGE,"markers":[],
          "photo_status":"PHYSICAL JPEG ARCHIVED, SOURCE LABELS; NO NEW ARROWS OR SUBSPECIES CLAIM"}
        if any(p.get("image_url")==base for p in items):
            raise ValueError("panel duplicate; no write")
        PHOTO.parent.mkdir(parents=True,exist_ok=True)
        PHOTO.write_bytes(processed)
        images.append(source); items.append(panel)
        idx=len(items)-1
        c=d["curation_status"]
        c["photo_metadata_count"]=len(images);c["photo_files_present"]=len(images)
        c["genus_photo_panels"]=len(items)
        d["photo_note"]="16 physically archived photographs, 20 teaching/comparison panels and 20 existing anatomy arrows. Added source-licensed Stefan.lefnaer Austrian spikelet glume/lemma montage (species-only). NO lineage-vouchered Gulf glume/collar or true ligule measurements yet."
        for tile in d.get("field_id_short_tiles",[]):
            if tile["heading"].startswith(("06 ·","09 ·","12 ·")):
                tile.setdefault("photo_panel_indices",[]).append(idx)
                tile["photo_panel_indices"]=list(dict.fromkeys(tile["photo_panel_indices"]))
        d.setdefault("field_photo_quickcheck",{}).setdefault("featured_photo_indices",[]).append(idx)
        d["phragmites_sl23_glume_photo_20261026"]={
          "panel_index":idx,"file":source["file"],"status":"ARCHIVED SOURCE-LEVEL ANATOMY; OWNER VISUAL ARROW REVIEW PENDING",
          "photographer":"Stefan.lefnaer","license":"CC BY-SA 4.0",
          "notes":"Never call this Texas-native/introduced/Gulf lineage evidence"}
        SPEC.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        result.update(status="ARCHIVED_AND_INSTALLED_PENDING_OWNER_VISUAL_REVIEW",
          "sha256":source["archived_sha256"],"original_dimensions":original,
          "archived_dimensions":size,"panel_index":idx,
          "photo_count":len(images),"teaching_panels":len(items),"arrows_unchanged":20)
    except Exception as exc:
        # No remote workaround/retry against provider rate limits. Preserve all existing photos.
        result["reason"]=type(exc).__name__+": "+str(exc)[:400]
    save_report(result)
if __name__=="__main__":run()
