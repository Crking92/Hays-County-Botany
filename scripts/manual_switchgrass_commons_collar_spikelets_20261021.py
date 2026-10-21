#!/usr/bin/env python3
"""Install two explicitly labeled CC BY-SA 4.0 wild-type Panicum virgatum photos,
verify actual author/right/media, and publish honest visible-point annotations.

Only touches canonical switchgrass + Panicum genus comparison. Never infer a cultivar,
change range/nativity, or publish unknown-rights image. Excludes source EXIF/GPS.
"""
import csv
import datetime
import io
import json
import pathlib
import re
import requests
from PIL import Image, ImageOps

ROOT = pathlib.Path(".")
F = ROOT/"content/taxa/Poaceae/Panicum/panicum-virgatum"
SPEC = F/"species.json"
GENUS = F.parent/"genus.json"
LIC = "https://creativecommons.org/licenses/by-sa/4.0/"
BASE = "content/taxa/Poaceae/Panicum/panicum-virgatum/images/"
TARGETS = [
    {
        "title": "File:Panicum virgatum sl37.jpg",
        "filename": "stefan-lefnaer-cc-by-sa-4-switchgrass-ligule.jpg",
        "label": "1 · Switchgrass — ACTUAL ligule and white silky collar hairs",
        "role": "True switchgrass blade/sheath collar: white hairs around the short ligule, plus a 5-mm reference ruler",
        "caption": "Stefan.lefnaer photographed a real P. virgatum blade–sheath junction with a 5-mm scale. The white fringe is the hairy collar/ligule region; do NOT call the hairs Indiangrass's stiff pointed rifle-sight membrane. The thin inner membrane is partly obscured, so no definitive membrane-tip arrow is claimed.",
        "why": "Allows the crew to recognize and physically locate the main vegetative clue before flowering.",
        "markers": [
            {"label":"White collar hair tuft", "label_x":1,"label_y":22,"target_x":34,"target_y":46},
            {"label":"Opposite hair tuft", "label_x":66,"label_y":22,"target_x":70,"target_y":45},
            {"label":"5 mm scale bar", "label_x":5,"label_y":97,"target_x":50,"target_y":91}
        ],
        "image_role":"Real source-labeled ligule/collar close-up, SILKY fringe and physical 5 mm scale (membrane edge not individually scored)"
    },
    {
        "title": "File:Panicum virgatum sl40.jpg",
        "filename": "stefan-lefnaer-cc-by-sa-4-switchgrass-flowering-spikelets.jpg",
        "label": "2 · Switchgrass — ACTUAL panicle spikelets, feathery stigmas, no awns",
        "role": "Panicle side-branch with multiple awnless flowering spikelets and purple feathery exserted stigmas",
        "caption": "True source-labeled Panicum virgatum side branch at the 5-mm scale: individual green ovoid spikelets attach to thin pedicels; dark purple FEATHERY flowering structures are visible (stigmas, not bent awns). We don't claim that tiny glume edges or a mature seed anatomy are separately resolved.",
        "why": "These are singly borne, awnless spikelets rather than the long twisted-awns and naked sterile pedicels of Indiangrass.",
        "markers": [
            {"label":"Awnless flowering spikelet", "label_x":1,"label_y":30,"target_x":44,"target_y":19},
            {"label":"Feathery purple stigma", "label_x":61,"label_y":2,"target_x":59,"target_y":9},
            {"label":"Slender panicle branch", "label_x":4,"label_y":70,"target_x":47,"target_y":62}
        ],
        "image_role":"Actual Panicum panicle branch, awnless spikelets and visible plumose flowering stigmas, with 5 mm scale"
    }
]
def parse_date(value):
    if not value: return None
    try: return datetime.datetime.fromisoformat(str(value).replace("Z","+00:00"))
    except Exception: return None
def verify_not_claimed():
    claims=json.loads((ROOT/"workflow/work-claims.json").read_text(encoding="utf-8"))
    now=datetime.datetime.now(datetime.timezone.utc)
    active=[]
    for q in claims.get("claims",[]):
        if "panicum-virgatum" not in q.get("taxa",[]): continue
        if q.get("status") not in ("active","claimed","in_progress"): continue
        end=parse_date(q.get("expires_at"))
        if end is None or end.astimezone(datetime.timezone.utc)>now: active.append(q.get("claim_id"))
    if active: raise RuntimeError("Active switchgrass work claim: "+repr(active))
def get_media():
    session=requests.Session()
    session.headers.update({"User-Agent":"HaysBotanyManualPhotoInstall/1.0 (photo provenance verification; Wikimedia Commons user content)"})
    response=session.get("https://commons.wikimedia.org/w/api.php",params={
       "action":"query","format":"json","prop":"imageinfo","iiprop":"url|extmetadata",
       "titles":"|".join(x["title"] for x in TARGETS)},timeout=45)
    response.raise_for_status()
    info={}
    for page in response.json().get("query",{}).get("pages",{}).values():
        if page.get("imageinfo"):info[page["title"]]=page["imageinfo"][0]
    verified=[]
    for x in TARGETS:
        title=x["title"]
        if title not in info:raise RuntimeError("Missing exact Commons source "+title)
        metadata=info[title].get("extmetadata",{})
        short=re.sub("<[^>]*>","",metadata.get("LicenseShortName",{}).get("value","")).strip().upper()
        terms=re.sub("<[^>]*>","",metadata.get("UsageTerms",{}).get("value","")).strip().upper()
        creator=re.sub("<[^>]*>","",metadata.get("Artist",{}).get("value","")).lower()
        if "BY-SA" not in short+" "+terms or "4.0" not in short+" "+terms:
            raise RuntimeError("License mismatch "+title+": "+short+" / "+terms)
        if "stefan.lefnaer" not in creator:
            raise RuntimeError("Original creator mismatch "+title+": "+creator[:120])
        url=str(info[title].get("url",""))
        if not url.startswith("https://upload.wikimedia.org/wikipedia/commons/"):
            raise RuntimeError("Unexpected media host: "+url)
        r=session.get(url,timeout=65)
        r.raise_for_status()
        if len(r.content)>10_000_000:raise RuntimeError("Photo too large "+title)
        with Image.open(io.BytesIO(r.content)) as im:
            im.load()
            fixed=ImageOps.exif_transpose(im).convert("RGB")
        if min(fixed.size)<750 or max(fixed.size)<1600:
            raise RuntimeError("Invalid macro dimensions "+title+" "+repr(fixed.size))
        fixed.thumbnail((2000,2000),Image.Resampling.LANCZOS)
        jpg=io.BytesIO();fixed.save(jpg,format="JPEG",quality=92,optimize=True)
        if len(jpg.getvalue())<55000:raise RuntimeError("Downloaded file unexpectedly tiny "+title)
        verified.append((x,url,list(fixed.size),jpg.getvalue()))
    return verified
def main():
    sp=json.loads(SPEC.read_text(encoding="utf-8"))
    g=json.loads(GENUS.read_text(encoding="utf-8"))
    if sp["id"]!="panicum-virgatum" or g["name"]!="Panicum":raise RuntimeError("Unexpected canonical file")
    if sp["project_inclusion"]["target_zone_status"]!="PASS":raise RuntimeError("Unexpected science status")
    verify_not_claimed()
    count=sum(any(t["filename"] in str(im.get("file","")) for t in TARGETS) for im in sp["images"])
    if count:
        if count!=2:raise RuntimeError("Partially installed media: manual review required")
        print("Two switchgrass macros already installed; no-op")
        return
    fetched=get_media()
    for t,_,_,_ in fetched:
        if (F/"images"/t["filename"]).exists():raise RuntimeError("Refusing file overwrite")
    csvpath=F/"image-sources.csv"
    with csvpath.open(newline="",encoding="utf-8-sig") as fh:
        reader=csv.DictReader(fh);fields=list(reader.fieldnames or []);rows=list(reader)
    for t,url,dimensions,blob in fetched:
        dest=F/"images"/t["filename"]
        dest.write_bytes(blob)
        with Image.open(dest) as im:im.verify()
        source="https://commons.wikimedia.org/wiki/"+t["title"].replace(" ","_")
        imdata={"file":"images/"+t["filename"],"role":t["role"],"creator":"Stefan.lefnaer",
           "license":"CC BY-SA 4.0","license_url":LIC,"source_page":source,
           "source_platform":"Wikimedia Commons","downloaded_from":url,
           "image_dimensions":dimensions,"study_use":"yes","public_reuse":"yes",
           "modifications":"Downscaled and JPEG re-encoded with GPS/EXIF metadata removed; derivative site pointer arrows shown separately under CC BY-SA 4.0.",
           "photo_review":"Wikimedia individually verified author, license, species file label and original pixels; macro organs visible. Marker positions chosen on uncropped source view, final mobile overlay alignment pending."}
        sp["images"].append(imdata)
        picture={"label":t["label"],"scientific_name":sp["scientific_name"],
           "image_url":BASE+t["filename"],"image_fit":"contain",
           "creator":"Stefan.lefnaer","license":"CC BY-SA 4.0",
           "license_url":LIC,"source_page":source,"image_role":t["image_role"],
           "caption":t["caption"],"why_it_matters":t["why"],"markers":t["markers"],
           "annotation_status":"Original source visually reviewed; arrow endpoints target actual hairs, scale, individual spikelet/stigma and visible rachis; no invisible membrane tip claimed. Owner mobile QA pending."}
        sp["visual_comparison"]["items"].append(picture)
        g["visual_comparison"]["items"].append({**picture,"species_id":"panicum-virgatum"})
        row={"file_name":t["filename"],"role":t["role"],"platform":"Wikimedia Commons",
             "creator":"Stefan.lefnaer","license":"CC BY-SA 4.0","source_page":source,
             "direct_image_url":url,"study_use":"yes","public_reuse":"yes","license_url":LIC,
             "source_context":"Individual CC BY-SA 4.0 and source taxon verified 2026-10-21; real photo JPEG decoded and EXIF removed."}
        for key in row:
            if key not in fields:fields.append(key)
        rows.append(row)
    with csvpath.open("w",newline="",encoding="utf-8") as fh:
        writer=csv.DictWriter(fh,fieldnames=fields,lineterminator="\n")
        writer.writeheader();writer.writerows(rows)
    sp["curation_status"]["photo_metadata_count"]=len(sp["images"])
    sp["curation_status"]["photo_files_present"]=len([x for x in sp["images"] if str(x["file"]).startswith("images/")])
    sp["curation_status"]["last_visual_reviewed"]="2026-10-21"
    sp["curation_status"]["version"]="1.2-switchgrass-two-CC-SA-macros-six-structural-arrows-20261021"
    sp["curation_status"]["visual_status"]="FIELD_READY_PHOTO_GAPS: 5 real installed public-clear photos, two new exact macro views with six visible-point arrows; true concealed ligule membrane contour and rhizome photo still missing."
    sp["learner_visual_status"]["image_count"]=len(sp["images"])
    sp["learner_visual_status"]["status"]="field_ready_photo_gaps"
    sp["learner_visual_status"]["note"]="Two actual source-licensed blade collar and spikelet/anther-stage detail views installed with 6 verified visible-point markers. Membrane contour, rhizomes, side-by-side Indiangrass remain photo gaps."
    sp["visual_comparison"]["subtitle"]="Five public-safe physically installed photographs including TWO precise licensed CC BY-SA 4.0 botanical macro views; SIX arrows on actually visible hair patches, scale, spikelet, purple feathery stigma and panicle axis. No invented thin ligule membrane-tip arrow.";
    sp["visual_comparison"]["annotation_status"]="Two Wikimedia Stefan.lefnaer photos physically saved and original pixels reviewed, with six photo coordinates. Owner mobile arrow-overlap QA still pending; do not infer local native occurrence from Austrian photo locality.";
    sp["diagnostic_photo_targets"]=[{**item,"status":"PHOTO_INSTALLED_ANNOTATED_MOBILE_QA_PENDING" if item.get("status")=="LICENSED_COMMONS_CANDIDATE_PENDING_INSTALL" else item.get("status")} for item in sp.get("diagnostic_photo_targets",[])]
    g["visual_comparison"]["subtitle"]="Six true photo panels (4 prior genus references + 2 newly verified exact switchgrass macro photos), six actual structural arrows. All licenses and photo-specific sources retained; one final mobile alignment check pending."
    g["visual_comparison"]["annotation_status"]="Six arrow coordinates attached only to 2026-10-21 actual verified switchgrass collar/spikelet photos. No arrows on unrelated genus habit photos."
    g["photo_handoffs"]=[x for x in g.get("photo_handoffs",[]) if "are candidates; physically install" not in x]
    g["photo_handoffs"].append("Real source-verified 5-mm ruler switchgrass hair-collar and flowering awnless spikelet/stigma photos installed and arrowed. Still obtain unobscured inner ligule membrane side view, actual rhizome crown, and local same-scale Indiangrass photo.")
    g["curation_status"].update({"version":"1.3-switchgrass-two-verified-macros-six-arrows-20261021","last_reviewed":"2026-10-21","switchgrass_photo_upgrade":"2 real CC BY-SA 4.0 macros; 6 visible-point arrows; no taxonomy or nativity edits"})
    sp["photo_note"]=(sp.get("photo_note") or "")+" Real Stefan.lefnaer CC BY-SA 4.0 2026 switchgrass collar and flowering spikelet photos installed and source-checked 2026-10-21; annotations track actually visible structures, share-alike and author preserved."
    with (F/"SOURCES.txt").open("a",encoding="utf-8") as fh:
        fh.write("\n2026-10-21 SOURCE-VERIFIED SWITCHGRASS LEAF COLLAR AND FLOWERING SPIKELETS\n")
        for t,_,_,_ in fetched:fh.write(t["title"]+" / Stefan.lefnaer / CC BY-SA 4.0 "+LIC+"\n")
        fh.write("2026-10-03 field specimen photographed in Austria; no inference for native Texas range or cultivars. 5-mm scale visible in each original. Resized/re-encoded JPEG and stripped EXIF/GPS. Six annotation endpoints placed on visible structures; user/mobile QA still needed.\n")
    SPEC.write_text(json.dumps(sp,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    GENUS.write_text(json.dumps(g,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"species":"panicum-virgatum","new_real_macros":len(fetched),
       "total_images":len(sp["images"]),"species_photo_panels":len(sp["visual_comparison"]["items"]),
       "genus_photo_panels":len(g["visual_comparison"]["items"]),
       "arrows_on_new_macros":sum(len(t["markers"]) for t,_,_,_ in fetched),
       "native_target_zone_status_preserved":sp["project_inclusion"]["target_zone_status"]},indent=2))
if __name__=="__main__":
    main()
