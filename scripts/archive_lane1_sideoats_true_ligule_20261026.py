#!/usr/bin/env python3
"""Archive one exact, vetted Matt Lavin CC BY-SA 2.0 sideoats grama ligule.
This is a real photographer-labelled collar source, NOT a measured Texas voucher.
Save bytes + provenance, preserve concurrent canonical changes, add zero arrows until pixel review.
"""
import base64, hashlib, json, os, pathlib, time, urllib.parse
import requests

REPO=os.environ["GITHUB_REPOSITORY"]
TOKEN=os.environ["GITHUB_TOKEN"]
BRANCH=os.environ.get("GITHUB_REF_NAME","main")
TITLE="File:Bouteloua curtipendula (3796749425).jpg"
IMAGE="matt-lavin-curtipendula-hairy-ligule-cc-by-sa2.jpg"
FOLDER="content/taxa/Poaceae/Bouteloua/bouteloua-curtipendula/"
PATH=FOLDER+"images/"+IMAGE
CARD=FOLDER+"species.json"
SOURCE="https://commons.wikimedia.org/wiki/File:Bouteloua_curtipendula_(3796749425).jpg"
LICENSE="https://creativecommons.org/licenses/by-sa/2.0/"
E=json.loads(pathlib.Path("review_photo/evidence.json").read_text())
DATA=pathlib.Path("review_photo/candidate.jpg").read_bytes()

if E.get("commons_file")!=TITLE or E.get("taxon_proposed")!="Bouteloua curtipendula":
    raise SystemExit("Exact Commons source/taxon mismatch")
if E.get("license_short","").strip().upper()!="CC BY-SA 2.0":
    raise SystemExit("CC BY-SA 2.0 not verified; hold")
lic=urllib.parse.urlparse(E.get("license_url",""))
if lic.scheme not in ("https","http") or lic.hostname!="creativecommons.org" or lic.path.rstrip("/")!="/licenses/by-sa/2.0":
    raise SystemExit("License URL version/source mismatch")
if "matt lavin" not in (E.get("creator_unverified_html") or "").lower():
    raise SystemExit("Commons creator does not state Matt Lavin; hold")
if not E.get("gps_exif_removed") or not DATA.startswith(bytes.fromhex("ffd8")):
    raise SystemExit("Not metadata-sanitized JPEG")
if len(DATA)>15000000 or hashlib.sha256(DATA).hexdigest()!=E.get("image_sha256"):
    raise SystemExit("Image checksum/size mismatch")
s=requests.Session()
s.headers.update({"Authorization":"Bearer "+TOKEN,"Accept":"application/vnd.github+json",
                  "X-GitHub-Api-Version":"2022-11-28","User-Agent":"Lane1-Sideoats-PhotoArchive"})
root=f"https://api.github.com/repos/{REPO}/contents/"
def get(path):
    r=s.get(root+urllib.parse.quote(path,safe="/"),params={"ref":BRANCH},timeout=35)
    if r.status_code==404:return None
    r.raise_for_status()
    return r.json()
def put(path,raw,sha,message):
    payload={"message":message,"content":base64.b64encode(raw).decode(),"branch":BRANCH}
    if sha:payload["sha"]=sha
    r=s.put(root+urllib.parse.quote(path,safe="/"),json=payload,timeout=80)
    if r.status_code in (409,422):return False
    r.raise_for_status()
    return True
old=get(PATH)
if old:
    if old.get("size")!=len(DATA):raise SystemExit("Existing photo bytes differ; DO NOT overwrite")
else:
    if not put(PATH,DATA,None,"Lane 1 archive verified Matt Lavin CC BY-SA sideoats ligule JPEG"):
        old=get(PATH)
        if not old or old.get("size")!=len(DATA):raise SystemExit("Conflicting photo archive")
record={
    "file":"images/"+IMAGE,
    "role":"True source-labelled hairy ligule and bulbous-based leaf-margin hairs at actual B. curtipendula collar; exact lengths not measurable, not same specimen as Texas field photos.",
    "creator":"Matt Lavin","license":"CC BY-SA 2.0","license_url":LICENSE,
    "source_page":SOURCE,
    "source_original":"https://www.flickr.com/photos/plant_diversity/3796749425/",
    "source_taxon":"Bouteloua curtipendula",
    "source_locality":"Montana, not a Hays County voucher",
    "public_reuse":"yes — credited CC BY-SA 2.0, ShareAlike derivatives",
    "modifications":"Commons photograph resized to a metadata-free JPEG; no photographic details altered. Original CC BY-SA 2.0 applies to derivative.",
    "photo_review":"Exact photographer caption identifies hairy ligule and bulbous marginal hair bases; requires pixel inspection prior to arrows or measured organ claims.",
}
panel={
    "label":"NEW · TRUE HAIRY LIGULE — Matt Lavin collar (Montana reference)",
    "scientific_name":"Bouteloua curtipendula",
    "image_url":PATH,"image_fit":"contain",
    "creator":"Matt Lavin","license":"CC BY-SA 2.0","license_url":LICENSE,
    "source_page":SOURCE,
    "image_role":"True source-labelled hairy ligule at blade–sheath junction; bulbous bases of adjacent blade margin hairs; scale not supplied.",
    "caption":"Matt Lavin source photograph of the hairy ligule and characteristic bulbous-based marginal hairs. These are TWO nearby structures; do not confuse blade-margin hairs with the true ligule. Montana reference, NOT an authenticated Hays specimen or a measured 0.3–0.5-mm membrane.",
    "why_it_matters":"Adds the missing genuine collar view to a gallery previously showing mostly hanging one-sided racemes.",
    "markers":[],
    "photo_status":"CC BY-SA 2.0, physical JPEG archived with EXIF/GPS stripped. Pixel arrows and scale still pending; Montana reference.",
}
for attempt in range(6):
    c=get(CARD)
    if not c:raise SystemExit("Missing canonical species.json")
    d=json.loads(base64.b64decode(c["content"]))
    images=d.setdefault("images",[])
    gallery=d.setdefault("visual_comparison",{}).setdefault("items",[])
    got_im=[x for x in images if x.get("file")==record["file"]]
    got_panel=[x for x in gallery if x.get("image_url")==PATH]
    if len(got_im)==len(got_panel)==1:
        print("ALREADY_ARCHIVED_AND_VISIBLE",PATH)
        break
    if got_im or got_panel:
        raise SystemExit("Partial/duplicate record; preserve for manual reconciliation")
    images.append(record)
    at=next((i for i,p in enumerate(gallery) if p.get("scientific_name")!="Bouteloua curtipendula"),len(gallery))
    gallery.insert(at,panel)
    d.setdefault("curation_status",{})["photo_files_present"]=sum(
        x.get("file","").startswith("images/") for x in images)
    d["curation_status"]["lane1_sideoats_true_ligule_20261026"]={
        "source_photo":SOURCE,"status":"FIELD_READY_PHOTO_GAPS",
        "confirmed_role":"source-labelled, actual collar/ligule",
        "unconfirmed":["image-level overlay arrows","measured millimeter ligule",
                       "same-plant Texas rooted rhizome","live Pages mobile QA"],
        "copyright":"Matt Lavin CC BY-SA 2.0 — attribution and license retained",
    }
    raw=(json.dumps(d,ensure_ascii=False,indent=2)+"\n").encode()
    if put(CARD,raw,c["sha"],"Lane 1 display physical CC BY-SA Matt Lavin sideoats hairy-ligule photo"):
        print("ARCHIVED_AND_LINKED",PATH,len(DATA))
        break
    time.sleep(1+attempt)
else:
    raise SystemExit("Six conflicting writes; image preserved, gallery needs reconciliation")
