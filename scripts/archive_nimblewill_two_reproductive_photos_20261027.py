#!/usr/bin/env python3
"""Nimblewill: archive TWO genuine source-verified reproduction photos.

Emily Summerbell's exact iNat-92218276 (Wikimedia Commons, CC BY 4.0)
Bob Harms' MUSC-J (original Selected Monocots, credited educational-only).
Do not claim photographs of rooted stolon, exposed true ligule, or oriented
glume/lemma dissection. No photo pixels edited besides GPS/EXIF-stripping.
"""
from __future__ import annotations
import hashlib, io, json, time
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlparse
import requests
from PIL import Image, ImageOps

ROOT=Path(".")
D=ROOT/"content/taxa/Poaceae/Muhlenbergia"
SP=D/"muhlenbergia-schreberi/species.json"
GP=D/"genus.json"
REPORT=ROOT/"reports/lane3-nimblewill-two-real-reproductive-photos-20261027.json"
HOLD=ROOT/"reports/lane3-nimblewill-source-photo-hold-20261027.json"
RELEASE=ROOT/"workflow/field-id-publication/2026-10-27-nimblewill-two-real-reproductive-photos.json"
HARMS="https://w3.biosci.utexas.edu/prc/Monocots/GrassHTML/data/"
CREATOR_RIGHTS="https://w3.biosci.utexas.edu/prc/Monocots/"
LICENSE_HARMS="© Bob Harms — scientific/educational use with attribution (NOT Creative Commons)"
PERM="BOB_HARMS_SELECTED_MONOCOTS_EDU_WITH_CREDIT_20261022"

PHOTOS=[
{
"id":"MUSC-J","filename":"bob-harms-musc-j-spikelet-edu.jpg",
"url":HARMS+"images/MUSC-J.jpg",
"allowed_hosts":{"w3.biosci.utexas.edu","www.biosci.utexas.edu"},
"page":HARMS+"pages/MUSC-J.html",
"creator":"Bob Harms","license":LICENSE_HARMS,"license_url":CREATOR_RIGHTS,
"role":"Genuine narrow nimblewill panicle with attached awned florets and author-provided millimeter scale",
"label":"REAL SPIKELETS — attached reproductive units with scale",
"caption":"Bob Harms' source-labelled M. schreberi flowering branch with overlapping small spikelets and long awns. The black/red millimeter strip is visible at the bottom; the exact tiny glume margins and detached lemma hairs are not independently separable here. This photo does NOT document roots or the true leaf ligule.",
"why":"Directly connects field-recognizable narrow flowering heads to their actual attached spikelet structure and awns.",
"source_taxon_name":"Muhlenbergia schreberi",
"site_specific_public_permission":PERM,
"public_reuse":"Copyright Bob Harms: free for properly credited scientific/educational display of exact Selected Monocots original only, NOT Creative Commons",
},
{
"id":"92218276","filename":"emily-summerbell-inat-92218276-awned-spikelets-ccby4.jpg",
"url":"https://upload.wikimedia.org/wikipedia/commons/0/04/Muhlenbergia_schreberi_iNat-92218276.jpg",
"allowed_hosts":{"upload.wikimedia.org"},
"page":"https://commons.wikimedia.org/wiki/File:Muhlenbergia_schreberi_iNat-92218276.jpg",
"creator":"Emily Summerbell","license":"CC BY 4.0","license_url":"https://creativecommons.org/licenses/by/4.0/",
"role":"Real detached nimblewill spikelets with prominent long thin awns against a hand-neutral background, unmeasured",
"label":"REAL AWNED SPIKELETS — detached open view",
"caption":"Emily Summerbell's CC BY 4.0 individual photograph #92218276 from the same species-identified observation as this card's other photos. Several small narrow spikelets and very fine long awns are photographed against a plain surface. This is a useful shape lesson, but no 1-mm ruler, glume dissection or proved rooted node appears.",
"why":"Shows the awned one-flowered spikelets apart from the complete narrow panicle, without guessing individual glume identity.",
"source_taxon_name":"Muhlenbergia schreberi",
"public_reuse":"CC BY 4.0 with author, URL, version and modifications credited",
"observation_url":"https://www.inaturalist.org/observations/57794694",
"source_photo_id":92218276
}
]
def dump(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def download(sess,p):
    errs=[]
    urls=[p["url"]]
    if p["id"]=="MUSC-J":
        urls.append(p["url"].replace("w3.biosci.utexas.edu","www.biosci.utexas.edu"))
    for url in urls:
        for attempt in range(3):
            try:
                resp=sess.get(url,timeout=32,headers={"Accept":"image/jpeg,image/*"})
                resp.raise_for_status()
                if urlparse(resp.url).hostname not in p["allowed_hosts"]:
                    raise ValueError("untrusted source host")
                blob=resp.content
                if not 3000<len(blob)<5_000_000 or blob[:3]!=b"\xff\xd8\xff":
                    raise ValueError("invalid source image bytes")
                with Image.open(io.BytesIO(blob)) as im:
                    im.load()
                    original_format=im.format
                    raw_dims=list(im.size)
                    if original_format!="JPEG" or min(raw_dims)<110 or max(raw_dims)>5000:
                        raise ValueError("original source not a plausible original JPEG")
                    if p["id"]=="92218276" and im.size!=(1536,2048):
                        raise ValueError("unexpected Wikimedia original resolution")
                    clean=ImageOps.exif_transpose(im).convert("RGB")
                buff=io.BytesIO()
                clean.save(buff,"JPEG",quality=93,optimize=True)
                cleaned=buff.getvalue()
                with Image.open(io.BytesIO(cleaned)) as verify:
                    assert verify.format=="JPEG" and not verify.getexif().get(34853)
                    verify.verify()
                return {"bytes":cleaned,"source_sha256":hashlib.sha256(blob).hexdigest(),
                  "archive_sha256":hashlib.sha256(cleaned).hexdigest(),
                  "source_dimensions":raw_dims,"archived_dimensions":list(clean.size),"download_url":resp.url}
            except Exception as exc:
                errs.append(f"{type(exc).__name__}: {str(exc)[:150]}")
                time.sleep(1+attempt)
    return {"error":" | ".join(errs[-6:])}
def main():
    sp=json.loads(SP.read_text(encoding="utf-8"))
    gen=json.loads(GP.read_text(encoding="utf-8"))
    if sp.get("id")!="muhlenbergia-schreberi" or gen.get("name")!="Muhlenbergia":
        raise ValueError("exact canonical species/genus identity lost")
    photos=sp["images"]
    prior={str(x.get("source_photo_id") or x.get("inaturalist_photo_id")) for x in photos}
    sess=requests.Session()
    sess.headers["User-Agent"]="HaysBotany-Nimblewill-Exact-JPEG-Archive/1.0 (educational open plant learner, Crking92/Hays-County-Botany)"
    installed=[];failures=[]
    for photo in PHOTOS:
        ident=str(photo["id"])
        if ident in prior:
            print("ALREADY_ARCHIVED",ident,flush=True)
            continue
        if any(x.get("source_page")==photo["page"] for x in photos):
            raise ValueError("image page already in metadata without expected source photo id")
        path=SP.parent/"images"/photo["filename"]
        if path.exists():raise ValueError("local path already exists, avoid overwriting unknown photo")
        data=download(sess,photo)
        if "error" in data:
            failures.append({"id":ident,"reason":data["error"]})
            print("SOURCE_HOLD",ident,flush=True)
            continue
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(data["bytes"])
        metadata={
            "file":"images/"+path.name,"role":photo["role"],
            "creator":photo["creator"],"license":photo["license"],
            "license_url":photo["license_url"],"source_page":photo["page"],
            "source_image":photo["url"],"source_taxon_name":"Muhlenbergia schreberi",
            "public_reuse":photo["public_reuse"],
            "source_photo_id":photo["id"],
            "photo_status":"REAL_EXACT_SPECIES_SOURCE_ARCHIVED; true ligule, rooting nodes and oriented lemma veins still unverified",
            "modifications":"Resaved as GPS/EXIF-free JPEG, no crop or over-image anatomical labels",
            **({"site_specific_public_permission":photo["site_specific_public_permission"]} if photo.get("site_specific_public_permission") else {}),
            **({"observation_source":photo["observation_url"]} if photo.get("observation_url") else {}),
            "source_sha256":data["source_sha256"],"archived_sha256":data["archive_sha256"],
            "source_dimensions":data["source_dimensions"],"archived_dimensions":data["archived_dimensions"],
            "downloaded_from":data["download_url"]
        }
        photos.append(metadata)
        panel={
            "label":photo["label"],"scientific_name":"Muhlenbergia schreberi",
            "image_url":str(path),"image_fit":"contain",
            "image_role":photo["role"],"caption":photo["caption"],
            "why_it_matters":photo["why"],"creator":photo["creator"],
            "license":photo["license"],"license_url":photo["license_url"],
            "source_page":photo["page"],"source_image":photo["url"],
            "source_photo_id":photo["id"],"source_taxon_name":"Muhlenbergia schreberi",
            "markers":[],"photo_status":metadata["photo_status"],
            **({"site_specific_public_permission":photo["site_specific_public_permission"]} if photo.get("site_specific_public_permission") else {})
        }
        for doc in (sp,gen):
            panels=doc["visual_comparison"]["items"]
            if any(x.get("source_page")==photo["page"] or str(x.get("source_photo_id"))==ident for x in panels):
                raise ValueError("duplicate source teaching panel detected; abort")
            panels.append(dict(panel))
        installed.append({"id":ident,"local":str(path),"source":photo["page"],
           "creator":photo["creator"],"license":photo["license"],
           "archive_sha256":data["archive_sha256"],"source_sha256":data["source_sha256"],
           "source_dimensions":data["source_dimensions"],"archive_dimensions":data["archived_dimensions"]})
        print("VERIFIED",ident,data["source_dimensions"],flush=True)
    if not installed:
        dump(HOLD,{"checked":datetime.now(timezone.utc).isoformat(),
            "state":"NO_NEW_SOURCE_BYTES_ARCHIVED","source_holds":failures})
        return
    sp["curation_status"]["photo_files_present"]=sum(
       1 for m in photos if str(m.get("file","")).startswith("images/") and (SP.parent/m["file"]).is_file())
    sp["curation_status"]["photo_metadata_count"]=len(photos)
    sp["curation_status"]["lane3_nimblewill_reproductive_archive_20261027"]=(
       f"{len(installed)} physical taxon-specific flowering/anatomy photos added with individual rights; "
       "no connected ROOTED node, truly measured inner membranous ligule, or matched lemma/glume dissection yet.")
    sp["learner_visual_status"]["image_count"]=len(photos)
    sp["learner_visual_status"]["status"]="FIELD_READY_PHOTO_GAPS"
    sp["field_photo_quickcheck"]["warning"] += (
      " 2026-10-27 new licensed real attached and detached flowering units added; "
      "do not interpret as demonstrated root-producing node or calibrated ligule anatomy.")
    dump(SP,sp);dump(GP,gen)
    dump(REPORT,{"date_utc":datetime.now(timezone.utc).isoformat(),
      "result":"NIMBLEWILL_REAL_REPRODUCTIVE_JPEGS_ARCHIVED",
      "species":"Muhlenbergia schreberi","source_count_added":len(installed),
      "source_ids":[r["id"] for r in installed],"photos":installed,"failures":failures,
      "archived_photos_current":sp["curation_status"]["photo_files_present"],
      "teaching_panels_current":len(sp["visual_comparison"]["items"]),
      "reproductive_role":"Additional source-visible awned spikelet evidence (provisional single-floret anatomy); avoid full role credit until six-role rescore.",
      "persistent_holds":["attached stolon visibly ROOTING at node","exposed true inner 0.5-1mm membranous ligule with scale","separately measured lemma/glume and awn labels"],
      "copyright":"Summerbell CC BY 4.0 and Bob Harms source-specific credited scientific/educational use, not CC"})
    dump(RELEASE,{"date":"2026-10-27","species":"muhlenbergia-schreberi",
       "report":str(REPORT),"publication":"rights-filtered noncommercial educational Pages build; require successful deploy/readback before claiming live"})
    print("SUCCESS",len(installed),flush=True)
if __name__=="__main__":
    main()
