#!/usr/bin/env python3
"""Archive ONLY four explicitly reviewed CC BY-SA 4.0 switchgrass photos from Commons.
The website already includes these same exact source images as external gallery panels.
Preserve all original creator/license/labels and every concurrent species-card change.
"""
import base64, hashlib, json, os, pathlib, time, urllib.parse
import requests

TITLE=os.environ["TITLE"]
REPO=os.environ["GITHUB_REPOSITORY"]
TOKEN=os.environ["GITHUB_TOKEN"]
BRANCH=os.environ.get("GITHUB_REF_NAME","main")
ROOT=f"https://api.github.com/repos/{REPO}/contents/"
SPECIES="content/taxa/Poaceae/Panicum/panicum-virgatum/species.json"
IMAGE_DIR="content/taxa/Poaceae/Panicum/panicum-virgatum/images/"
APPROVED={
 "File:Panicum virgatum sl25.jpg":("Panicum virgatum sl25.jpg","stefan-lefnaer-switchgrass-rooted-rhizome-cc-by-sa4.jpg"),
 "File:Panicum virgatum sl33.jpg":("Panicum virgatum sl33.jpg","stefan-lefnaer-switchgrass-open-panicle-cc-by-sa4.jpg"),
 "File:Panicum virgatum sl53.jpg":("Panicum virgatum sl53.jpg","stefan-lefnaer-switchgrass-glume-lemma-palea-dissection-cc-by-sa4.jpg"),
 "File:Panicum virgatum sl55.jpg":("Panicum virgatum sl55.jpg","stefan-lefnaer-switchgrass-fertile-floret-cc-by-sa4.jpg"),
}
if TITLE not in APPROVED:raise SystemExit("Source title not on per-photo allowlist")
original_name,name=APPROVED[TITLE]
evidence=json.loads(pathlib.Path("review_photo/evidence.json").read_text())
data=pathlib.Path("review_photo/candidate.jpg").read_bytes()
if evidence["commons_file"]!=TITLE or evidence["taxon_proposed"]!="Panicum virgatum":
 raise SystemExit("The taxon or original exact Commons title changed")
if evidence["license_short"].strip().lower()!="cc by-sa 4.0":
 raise SystemExit("Actual Commons file license is not CC BY-SA 4.0")
license_uri=evidence.get("license_url","").lower().rstrip("/")
if license_uri not in ("http://creativecommons.org/licenses/by-sa/4.0","https://creativecommons.org/licenses/by-sa/4.0"):
 raise SystemExit("Expected CC BY-SA 4.0 license URL not confirmed")
if not evidence["gps_exif_removed"] or not data.startswith(bytes.fromhex("ffd8")) or len(data)>15_000_000:
 raise SystemExit("Image invalid, too large, or not sanitized")
if hashlib.sha256(data).hexdigest()!=evidence["image_sha256"]:
 raise SystemExit("Candidate bytes do not match recorded evidence")
session=requests.Session()
session.headers.update({"Authorization":f"Bearer {TOKEN}","Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28","User-Agent":"HaysBotany-Lane1-CuratedSwitchgrass"})
def get(path):
 r=session.get(ROOT+urllib.parse.quote(path,safe="/"),params={"ref":BRANCH},timeout=40)
 if r.status_code==404:return None
 r.raise_for_status()
 return r.json()
def put(path,payload,sha,message):
 b={"message":message,"content":base64.b64encode(payload).decode(),"branch":BRANCH}
 if sha:b["sha"]=sha
 r=session.put(ROOT+urllib.parse.quote(path,safe="/"),json=b,timeout=80)
 if r.status_code in (409,422):return False
 r.raise_for_status()
 return True

image_path=IMAGE_DIR+name
existing=get(image_path)
if existing:
 # Refuse any accidental image overwrite; an already-published image is protected.
 if existing.get("size")!=len(data):
  raise SystemExit("A different JPEG already has this name. Preserve existing binary and stop.")
else:
 if not put(image_path,data,None,f"Lane 1: archive CC BY-SA 4.0 switchgrass anatomical original {TITLE}"):
  existing=get(image_path)
  if not existing or existing.get("size")!=len(data):
   raise SystemExit("Concurrent image insertion differs from candidate; stop")

for attempt in range(6):
 current=get(SPECIES)
 if not current:raise SystemExit("Canonical species.json missing")
 d=json.loads(base64.b64decode(current["content"]))
 def is_match(url):
  return original_name.lower() in urllib.parse.unquote(url or "").lower().replace("_"," ")
 item=[p for p in d.get("visual_comparison",{}).get("items",[]) if is_match(p.get("image_url"))]
 record=[im for im in d.get("images",[]) if is_match(im.get("file"))]
 if not item and not record:
  # Fully completed repeats should not fail the entire photo job.
  already_panel=[p for p in d.get("visual_comparison",{}).get("items",[]) if p.get("image_url")==image_path]
  already_photo=[x for x in d.get("images",[]) if x.get("file")=="images/"+name]
  if len(already_panel)==1 and len(already_photo)==1:
   print("ALREADY_ARCHIVED_AND_LINKED",image_path)
   break
  raise SystemExit("Neither matching source panel nor media record exists; do not invent/replace")
 if len(item)!=1 or len(record)!=1:
  raise SystemExit("Ambiguous source image/panel, stop instead of duplicating")
 item[0]["image_url"]=image_path
 item[0]["photo_status"]=str(item[0].get("photo_status",""))+" | Physically archived CC BY-SA 4.0 author image; original morphology labels retained, overlays unmodified."
 item[0]["source_page"]=record[0].get("source_page",item[0].get("source_page"))
 record[0]["file"]="images/"+name
 record[0]["archival_note"]="Physically archived exact Commons image; JPEG resized, converted to RGB, and EXIF/GPS removed; author retained and CC BY-SA 4.0 applies to modified photo."
 record[0]["modifications"]="Resized JPEG, EXIF and GPS removed; source anatomical content unchanged. CC BY-SA 4.0 applies to adapted image."
 d.setdefault("curation_status",{})["photo_files_present"]=sum(x.get("file","").startswith("images/") for x in d.get("images",[]))
 d["curation_status"]["lane1_switchgrass_archiving_20261024"]="INCREMENTAL_GUARDED_CC_BY_SA_4_GALLERY_RELINK"
 content=(json.dumps(d,ensure_ascii=False,indent=2)+"\n").encode()
 if put(SPECIES,content,current["sha"],f"Lane 1 switchgrass: display archived CC BY-SA anatomical photo {TITLE}"):
  print("ARCHIVED_AND_RELINKED",image_path,"bytes",len(data))
  break
 time.sleep(attempt+1)
else:raise SystemExit("Too many concurrent species record edits. Image retained; gallery link pending")
