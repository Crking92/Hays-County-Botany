#!/usr/bin/env python3
"""Archive exact CC BY 2.0 source-labelled Cenchrus spinifex photos, preserving county and morphology holds."""
import base64, hashlib, json, os, pathlib, time, urllib.parse
import requests
repo=os.environ["GITHUB_REPOSITORY"]
token=os.environ["GITHUB_TOKEN"]
branch=os.environ.get("GITHUB_REF_NAME","main")
title=os.environ["TITLE"]
base="content/taxa/Poaceae/Cenchrus/cenchrus-spinifex/"
species=base+"species.json"
approved={
 "File:Cenchrus spinifex burr2 (6923261230).jpg":(
  "harry-rose-spinifex-bur-side-cc-by2.jpg",
  "MATURE BUR SIDE — clustered rigid spines and overall cupule shape"),
 "File:Cenchrus spinifex burrs.jpg":(
  "harry-rose-spinifex-burs-close-cc-by2.jpg",
  "MATURE BURS MACRO — distinct spiny cups and their shapes")
}
if title not in approved:raise SystemExit("Exact photo not on source allowlist")
name,role=approved[title]
e=json.loads(pathlib.Path("review_photo/evidence.json").read_text())
data=pathlib.Path("review_photo/candidate.jpg").read_bytes()
if e.get("commons_file")!=title or e.get("taxon_proposed")!="Cenchrus spinifex":
 raise SystemExit("Mismatch between Commons title and proposed species")
if e.get("license_short","").strip().upper()!="CC BY 2.0":
 raise SystemExit("License is not expected CC BY 2.0")
lic=urllib.parse.urlparse(e.get("license_url",""))
if lic.scheme not in ("http","https") or lic.hostname!="creativecommons.org" or lic.path.rstrip("/")!="/licenses/by/2.0":
 raise SystemExit("License URL does not match actual CC BY 2.0")
if not e.get("gps_exif_removed") or len(data)>15_000_000 or not data.startswith(bytes.fromhex("ffd8")):
 raise SystemExit("Sanitized candidate missing or oversized")
if hashlib.sha256(data).hexdigest()!=e.get("image_sha256"):
 raise SystemExit("Candidate hash mismatched rights record")
s=requests.Session()
s.headers.update({"Authorization":"Bearer "+token,"Accept":"application/vnd.github+json",
 "X-GitHub-Api-Version":"2022-11-28","User-Agent":"Hays-Botany-Lane1-Sandbur"})
endpoint=f"https://api.github.com/repos/{repo}/contents/"
def get(path):
 r=s.get(endpoint+urllib.parse.quote(path,safe="/"),params={"ref":branch},timeout=45)
 if r.status_code==404:return None
 r.raise_for_status()
 return r.json()
def put(path,data,sha,msg):
 b={"message":msg,"content":base64.b64encode(data).decode(),"branch":branch}
 if sha:b["sha"]=sha
 r=s.put(endpoint+urllib.parse.quote(path,safe="/"),json=b,timeout=90)
 if r.status_code in (409,422):return False
 r.raise_for_status()
 return True
filepath=base+"images/"+name
existing=get(filepath)
if existing and existing.get("size")!=len(data):
 raise SystemExit("Different prior JPEG exists: do not overwrite")
if not existing and not put(filepath,data,None,"Archive vetted CC BY coastal sandbur mature bur macro"):
 existing=get(filepath)
 if not existing or existing.get("size")!=len(data):
  raise SystemExit("Concurrent image write differs")
source_page="https://commons.wikimedia.org/wiki/"+urllib.parse.quote(title,safe=":/()")
metadata={
 "file":"images/"+name,
 "role":role+" (not dissected; fused base and enclosed spikelets not independently exposed)",
 "creator":"Harry Rose / Macleay Grass Man",
 "license":"CC BY 2.0","license_url":"https://creativecommons.org/licenses/by/2.0/",
 "source_page":source_page,"source_taxon_name":"Cenchrus spinifex",
 "source_determination":"Source photographer-labelled, provisional for regional ID",
 "source_locality":"New South Wales, Australia; NOT a Hays or Texas voucher",
 "study_use":"Public species recognition with photo-specific attribution",
 "public_reuse":"CC BY 2.0; preserve author, source page, license and adaptation notice",
 "modifications":"Converted to RGB JPEG with metadata/GPS removed; author retains photo credit",
 "photo_review":"Mature bur gross morphology only; bristle fusion and enclosed spikelets not certified by this image",
 "anatomy_arrows":"none; no new microstructure annotations"
}
panel={
 "label":"MATURE BUR · Harry Rose (Australian exact-source, NOT Texas voucher)",
 "scientific_name":"Cenchrus spinifex","image_url":filepath,"image_fit":"contain",
 "creator":metadata["creator"],"license":"CC BY 2.0","license_url":metadata["license_url"],
 "source_page":source_page,"image_role":metadata["role"],
 "caption":role+". Original photographer labels this Cenchrus spinifex. Inspect the mature spiny body and whorls; neither actual cupule fusion nor enclosed spikelets is separately dissected, and no scale here establishes exact measurements.",
 "why_it_matters":"Real mature source-determined burs complement existing green burs; bristle-base and dissected-spikelet holds remain.",
 "markers":[],"photo_status":"Public-safe CC BY 2.0 JPEG physically archived; source-determined Australian bur anatomy provisional."
}
for attempt in range(6):
 current=get(species)
 if not current:raise SystemExit("Canonical sandbur species record missing")
 d=json.loads(base64.b64decode(current["content"]))
 photos=d.setdefault("images",[])
 gallery=d.setdefault("visual_comparison",{}).setdefault("items",[])
 prior=[x for x in photos if x.get("file")=="images/"+name]
 priorpanel=[x for x in gallery if x.get("image_url")==filepath]
 if len(prior)==1 and len(priorpanel)==1:
  print("ALREADY_ARCHIVED",filepath)
  break
 if len(prior)>1 or len(priorpanel)>1 or bool(prior)!=bool(priorpanel):
  raise SystemExit("Conflicting partial image install; preserve and review")
 photos.append(metadata)
 # Insert new same-species mature image before the first C. longispinus look-alike.
 idx=next((i for i,x in enumerate(gallery) if x.get("scientific_name")!="Cenchrus spinifex"),len(gallery))
 gallery.insert(idx,panel)
 d.setdefault("curation_status",{})["photo_metadata_count"]=len(photos)
 d["curation_status"]["photo_files_present"]=sum(x.get("file","").startswith("images/") for x in photos)
 d["curation_status"]["lane1_mature_bur_photos_20261024"]="SOURCE_CC_BY2_MATURE_BURS_INSTALLED_NOT_DISSECTED"
 payload=(json.dumps(d,ensure_ascii=False,indent=2)+"\n").encode()
 if put(species,payload,current["sha"],"Lane 1 coastal sandbur: show licensed mature source-specific bur anatomy"):
  print("INSTALLED",filepath)
  break
 time.sleep(attempt+1)
else:raise SystemExit("Concurrent species JSON updates exhausted; image staged and must be reconciled")
