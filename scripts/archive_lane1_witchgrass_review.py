#!/usr/bin/env python3
"""Guarded archival of two existing licensed witchgrass external anatomy gallery photos."""
import base64, hashlib, json, os, pathlib, time, urllib.parse
import requests

REPO=os.environ["GITHUB_REPOSITORY"]
TOKEN=os.environ["GITHUB_TOKEN"]
BRANCH=os.environ.get("GITHUB_REF_NAME","main")
TITLE=os.environ["TITLE"]
SPECIES="content/taxa/Poaceae/Panicum/panicum-capillare/species.json"
BASE="content/taxa/Poaceae/Panicum/panicum-capillare/images/"
ALLOWED={
 "File:Panicum capillare sl24.jpg": {
  "original":"Panicum capillare sl24.jpg",
  "name":"stefan-lefnaer-witchgrass-labelled-spikelet-parts-cc-by-sa4.jpg",
  "license":"CC BY-SA 4.0",
  "license_url":"https://creativecommons.org/licenses/by-sa/4.0",
 },
 "File:Panicum capillare (3812306805).jpg": {
  "original":"Panicum capillare (3812306805).jpg",
  "name":"matt-lavin-witchgrass-hairy-sheath-collar-cc-by-sa2.jpg",
  "license":"CC BY-SA 2.0",
  "license_url":"https://creativecommons.org/licenses/by-sa/2.0",
 }
}
if TITLE not in ALLOWED:raise SystemExit("Photo not explicitly approved for this taxon")
config=ALLOWED[TITLE]
evidence=json.loads(pathlib.Path("review_photo/evidence.json").read_text())
data=pathlib.Path("review_photo/candidate.jpg").read_bytes()
if evidence["taxon_proposed"]!="Panicum capillare" or evidence["commons_file"]!=TITLE:
 raise SystemExit("Unexpected taxon/Commons exact image identity")
if evidence["license_short"].strip().lower()!=config["license"].lower():
 raise SystemExit("The image's current source license no longer matches approved rights")
if evidence.get("license_url","").rstrip("/").lower()!=config["license_url"].lower():
 raise SystemExit("Current Commons URL does not match approved rights")
if not evidence.get("gps_exif_removed") or not data.startswith(bytes.fromhex("ffd8")):
 raise SystemExit("Source has not been sanitized to valid JPEG")
if len(data)>15_000_000 or hashlib.sha256(data).hexdigest()!=evidence["image_sha256"]:
 raise SystemExit("File size/checksum invalid")
session=requests.Session()
session.headers.update({"Authorization":f"Bearer {TOKEN}","Accept":"application/vnd.github+json",
 "X-GitHub-Api-Version":"2022-11-28","User-Agent":"Hays-Botany-Lane1-Witchgrass"})
endpoint=f"https://api.github.com/repos/{REPO}/contents/"
def get(path):
 r=session.get(endpoint+urllib.parse.quote(path,safe="/"),params={"ref":BRANCH},timeout=45)
 if r.status_code==404:return None
 r.raise_for_status()
 return r.json()
def put(path,data,sha,message):
 req={"content":base64.b64encode(data).decode(),"message":message,"branch":BRANCH}
 if sha:req["sha"]=sha
 r=session.put(endpoint+urllib.parse.quote(path,safe="/"),json=req,timeout=80)
 if r.status_code in (409,422):return False
 r.raise_for_status()
 return True
path=BASE+config["name"]
existing=get(path)
if existing:
 if existing.get("size")!=len(data):
  raise SystemExit("Existing archive image differs: preserve and stop")
else:
 if not put(path,data,None,f"Archive licensed witchgrass source anatomy: {TITLE}"):
  existing=get(path)
  if not existing or existing.get("size")!=len(data):
   raise SystemExit("Unexpected conflicting file")
for attempt in range(6):
 current=get(SPECIES)
 if not current:raise SystemExit("Missing canonical witchgrass")
 d=json.loads(base64.b64decode(current["content"]))
 def match(ref):
  return config["original"].lower() in urllib.parse.unquote(ref or "").lower().replace("_"," ")
 panels=[x for x in d.get("visual_comparison",{}).get("items",[]) if match(x.get("image_url"))]
 photos=[x for x in d.get("images",[]) if match(x.get("file"))]
 if not panels and not photos:
  if len([x for x in d.get("visual_comparison",{}).get("items",[]) if x.get("image_url")==path])==1 and any(x.get("file")=="images/"+config["name"] for x in d.get("images",[])):
   print("ALREADY_ARCHIVED_AND_LINKED",path)
   break
  raise SystemExit("Source panel/record absent; no creative gallery replacement")
 if len(panels)!=1 or len(photos)!=1:raise SystemExit("Ambiguous gallery/source; do not modify")
 panels[0]["image_url"]=path
 panels[0]["photo_status"]=str(panels[0].get("photo_status",""))+" | Physically archived source CC photo; original labels, author and credit retained."
 photos[0]["file"]="images/"+config["name"]
 photos[0]["archive_review_note"]="Source-authenticated original, JPEG resized and stripped EXIF/GPS; source anatomy not independently microscope verified"
 photos[0]["modifications"]="Resized/converted JPEG; EXIF and GPS removed. Original photo copyright and CC BY-SA license retained."
 d.setdefault("curation_status",{})["photo_files_present"]=sum(x.get("file","").startswith("images/") for x in d.get("images",[]))
 d["curation_status"]["lane1_witchgrass_archive_20261024"]="GUARDED_PHOTO_RELINK_IN_PROGRESS"
 payload=(json.dumps(d,ensure_ascii=False,indent=2)+"\n").encode()
 if put(SPECIES,payload,current["sha"],"Lane 1 witchgrass: use physically archived licensed anatomy photograph"):
  print("ARCHIVED",path,"bytes",len(data))
  break
 time.sleep(attempt+1)
else:raise SystemExit("Excessive concurrent edits; image is stored but gallery needs manual review")
