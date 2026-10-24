#!/usr/bin/env python3
"""Guarded publication of two already-reviewed barnyardgrass Commons anatomy photos.
Runs only in GitHub Actions with contents:write. Never guesses image rights or anatomy.
"""
import base64, json, os, pathlib, time, urllib.parse
import requests

OWNER_REPO = os.environ["GITHUB_REPOSITORY"]
TOKEN = os.environ["GITHUB_TOKEN"]
TITLE = os.environ["TITLE"]
SPECIES_PATH = "content/taxa/Poaceae/Echinochloa/echinochloa-crus-galli/species.json"
BASE = "content/taxa/Poaceae/Echinochloa/echinochloa-crus-galli/images/"
APPROVED = {
    "File:Echinochloa crusgalli ligule1 (7120566875).jpg": {
        "filename": "harry-rose-barnyardgrass-absent-ligule-cc-by2.jpg",
        "match": "ligule1_(7120566875).jpg",
        "label": "CC BY 2.0 real collar — ligule absent",
    },
    "File:Echinochloa crusgalli spikelet annotated (7120556227).jpg": {
        "filename": "harry-rose-barnyardgrass-annotated-spikelet-cc-by2.jpg",
        "match": "spikelet_annotated_(7120556227).jpg",
        "label": "CC BY 2.0 source-labelled spikelet anatomy",
    },
}
if TITLE not in APPROVED:
    raise SystemExit("Not an expressly approved barnyardgrass file")
info = APPROVED[TITLE]
evidence = json.loads(pathlib.Path("review_photo/evidence.json").read_text())
data = pathlib.Path("review_photo/candidate.jpg").read_bytes()
license_text = evidence["license_short"].lower()
license_url = evidence["license_url"].lower()
if not ("cc by 2.0" in license_text or "creativecommons.org/licenses/by/2.0" in license_url):
    raise SystemExit("Expected CC BY 2.0 not independently confirmed")
if evidence["taxon_proposed"] != "Echinochloa crus-galli" or evidence["commons_file"] != TITLE:
    raise SystemExit("Taxon/title mismatch")
if not evidence["gps_exif_removed"] or not data.startswith(bytes.fromhex("ffd8")):
    raise SystemExit("Unsafe or invalid JPEG output")
s = requests.Session()
s.headers.update({"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json",
                  "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "HaysCountyBotany-Lane1-PhotoArchive"})
root = f"https://api.github.com/repos/{OWNER_REPO}/contents/"
branch = os.getenv("GITHUB_REF_NAME", "main")
def get(path):
    r=s.get(root+urllib.parse.quote(path,safe="/"),params={"ref":branch},timeout=30)
    if r.status_code==404:return None
    r.raise_for_status()
    return r.json()
def put(path, content, sha, message):
    body={"message":message,"content":base64.b64encode(content).decode(),"branch":branch}
    if sha:body["sha"]=sha
    r=s.put(root+urllib.parse.quote(path,safe="/"),json=body,timeout=40)
    if r.status_code in (409,422):return False
    r.raise_for_status()
    return True
imagepath=BASE+info["filename"]
existing=get(imagepath)
if existing:
    if existing.get("size") != len(data):
        raise SystemExit("Filename exists with different image; never overwrite")
else:
    if not put(imagepath,data,None,"Archive licensed barnyardgrass anatomical photo: "+TITLE):
        existing=get(imagepath)
        if not existing:raise SystemExit("Concurrent image update; verify manually")
# Preserve every concurrently edited JSON field; replace ONLY matching remote gallery URL.
for attempt in range(5):
    current=get(SPECIES_PATH)
    if not current:raise SystemExit("Canonical species card missing")
    doc=json.loads(base64.b64decode(current["content"]))
    matching=[p for p in doc.get("visual_comparison",{}).get("items",[])
              if info["match"] in urllib.parse.unquote(p.get("image_url",""))]
    if len(matching)!=1:raise SystemExit("Gallery remote panel absent/ambiguous; stop, do not guess")
    panel=matching[0]
    panel["image_url"]=imagepath
    panel["photo_status"]=str(panel.get("photo_status",""))+" | Sanitized CC BY 2.0 JPEG physically archived; source-provided organ labels still provisional."
    for source in doc.get("images",[]):
        if info["match"] in urllib.parse.unquote(source.get("file","")):
            source["file"]="images/"+info["filename"]
            source["archival_note"]="Physically archived source photo with EXIF/GPS stripped; anatomy remains subject to review"
    status=doc.setdefault("curation_status",{})
    status["photo_files_present"]=sum(str(x.get("file","")).startswith("images/") for x in doc.get("images",[]))
    payload=(json.dumps(doc,ensure_ascii=False,indent=2)+"\n").encode()
    if put(SPECIES_PATH,payload,current["sha"],"Lane 1: display physically archived barnyardgrass licensed anatomy in species gallery"):
        print("ARCHIVED_AND_RELINKED",imagepath)
        break
    time.sleep(attempt+1)
else:
    raise SystemExit("Species JSON had multiple concurrent edits; image preserved, gallery change held")
