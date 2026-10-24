#!/usr/bin/env python3
"""Guarded import of three exact CC BY 2.0 P. coloratum var. makarikariense anatomy photographs.
They are variety-labelled Australian sources, NOT Texas vouchers. Preserve all current card work.
"""
import base64,hashlib,json,os,pathlib,time,urllib.parse
import requests
repo=os.environ["GITHUB_REPOSITORY"];token=os.environ["GITHUB_TOKEN"];branch=os.getenv("GITHUB_REF_NAME","main");title=os.environ["TITLE"]
base="content/taxa/Poaceae/Panicum/panicum-coloratum/"
species=base+"species.json"
approved={
 "File:Panicum coloratum var makarikariense collar1 NWP - Flickr - Macleay Grass Man.jpg":("harry-rose-coloratum-var-makarikariense-collar-cc-by2.jpg","COLLAR REGION","Visible blade–sheath junction of source-identified Australian var. makarikariense; true ligule edge must be independently verified."),
 "File:Panicum coloratum var makarikariense ligule2 NWP - Flickr - Macleay Grass Man.jpg":("harry-rose-coloratum-var-makarikariense-ligule-cc-by2.jpg","LIGULE REGION","Author-titled real ligule macro of var. makarikariense; do not claim a measured membrane without scale/pixel verification."),
 "File:Panicum coloratum var makarikariense spikelets1 NWP - Flickr - Macleay Grass Man.jpg":("harry-rose-coloratum-var-makarikariense-spikelets-cc-by2.jpg","SPIKELETS","Author-identified actual mature flowering units; var. makarikariense and Australian locality, not locally vouchered.")
}
if title not in approved:raise SystemExit("Title not explicitly approved")
filename,organ,meaning=approved[title]
e=json.loads(pathlib.Path("review_photo/evidence.json").read_text())
data=pathlib.Path("review_photo/candidate.jpg").read_bytes()
if e.get("commons_file")!=title or e.get("taxon_proposed")!="Panicum coloratum":
 raise SystemExit("Unexpected Commons title or species")
if e.get("license_short","").strip().upper()!="CC BY 2.0":raise SystemExit("License is not CC BY 2.0")
lic=urllib.parse.urlparse(e.get("license_url",""))
if lic.scheme not in ("http","https") or lic.hostname!="creativecommons.org" or lic.path.rstrip("/")!="/licenses/by/2.0":
 raise SystemExit("CC BY version/source validation failed")
if not e.get("gps_exif_removed") or len(data)>15000000 or not data.startswith(bytes.fromhex("ffd8")) or hashlib.sha256(data).hexdigest()!=e.get("image_sha256"):
 raise SystemExit("Sanitized JPEG evidence mismatch")
session=requests.Session()
session.headers.update({"Authorization":"Bearer "+token,"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28","User-Agent":"Hays-Lane1-Kleingrass-Anatomy"})
root=f"https://api.github.com/repos/{repo}/contents/"
def get(path):
 r=session.get(root+urllib.parse.quote(path,safe="/"),params={"ref":branch},timeout=40)
 if r.status_code==404:return None
 r.raise_for_status()
 return r.json()
def put(path,body,sha,msg):
 fields={"message":msg,"content":base64.b64encode(body).decode(),"branch":branch}
 if sha:fields["sha"]=sha
 r=session.put(root+urllib.parse.quote(path,safe="/"),json=fields,timeout=90)
 if r.status_code in (409,422):return False
 r.raise_for_status()
 return True
path=base+"images/"+filename
old=get(path)
if old and old.get("size")!=len(data):raise SystemExit("Archive file exists but bytes differ; preserve")
if not old and not put(path,data,None,"Archive source-verified CC BY 2.0 Kleingrass anatomy "+organ):
 old=get(path)
 if not old or old.get("size")!=len(data):raise SystemExit("Concurrent conflicting upload")
source="https://commons.wikimedia.org/wiki/"+urllib.parse.quote(title.replace("File:","File:"),safe=":/()")
rel="images/"+filename
metadata={
 "file":rel,"role":"VARIETY-SPECIFIC "+organ+" — "+meaning,
 "source_taxon_name":"Panicum coloratum var. makarikariense",
 "source_determination":"From original photographer; independent local determination NOT made",
 "source_locality":"Australia — NOT a Central Texas voucher",
 "creator":"Harry Rose / Macleay Grass Man",
 "license":"CC BY 2.0","license_url":"https://creativecommons.org/licenses/by/2.0/",
 "source_page":source,"public_reuse":"CC BY 2.0 with credit, source and adaptation note",
 "modifications":"Source JPEG resized, converted to RGB and GPS/EXIF removed; photographic content retained",
 "photo_review":"Source-labelled morphology only; no microscopic structure pixel-certified and no arrows added."
}
panel={
 "label":"REFERENCE var. makarikariense — "+organ+" (NOT Hays voucher)",
 "scientific_name":"Panicum coloratum var. makarikariense","image_url":path,"image_fit":"contain",
 "creator":metadata["creator"],"license":"CC BY 2.0","license_url":metadata["license_url"],
 "source_page":source,
 "image_role":metadata["role"],
 "caption":meaning+" Credited photograph of the Australian variety; do not apply subtle characters to unidentified Texas specimens without confirming variety.",
 "why_it_matters":"Adds true anatomical reference for a missing kleingrass feature, avoiding another non-diagnostic distant grass clump.",
 "markers":[],"photo_status":"Source CC BY 2.0 JPEG locally archived; PHOTO_GAPS remain for confirmed local plants and microscope measurements."
}
for attempt in range(6):
 current=get(species)
 if not current:raise SystemExit("Missing canonical Kleingrass card")
 d=json.loads(base64.b64decode(current["content"]))
 photos=d.setdefault("images",[]);items=d.setdefault("visual_comparison",{}).setdefault("items",[])
 already=[x for x in photos if x.get("file")==rel]
 gal=[x for x in items if x.get("image_url")==path]
 if len(already)==1 and len(gal)==1:
  print("ALREADY_INSTALLED",path)
  break
 if len(already)>1 or len(gal)>1 or bool(already)!=bool(gal):
  raise SystemExit("Partial/duplicate candidate detected; preserve for manual review")
 photos.append(metadata)
 # Existing external ligule panel was published by another chat; preserve it and relink
 # rather than adding a duplicate tile. A distinct spikelets1 image stays distinct from spikelets2.
 remote_same=[x for x in items if organ=="LIGULE REGION" and "Panicum_coloratum_var_makarikariense_ligule2_NWP" in x.get("image_url","")]
 if len(remote_same)>1:raise SystemExit("Duplicate external ligule panels; need human review")
 if len(remote_same)==1:
  existing_panel=remote_same[0]
  existing_panel["image_url"]=path
  existing_panel["label"]=existing_panel.get("label","Kleingrass ligule").replace("(external photo)","(archived CC BY 2.0)")
  existing_panel["photo_status"]=str(existing_panel.get("photo_status",""))+" | Actual source image archived locally with original attribution; variety ID is provisional"
  existing_panel["source_page"]=source
 else:
  # Put anatomy before look-alikes; preserve all preexisting panels and markers.
  insert=next((i for i,x in enumerate(items) if "Panicum hallii" in x.get("scientific_name","")),len(items))
  items.insert(insert,panel)
 d.setdefault("curation_status",{})["photo_files_present"]=sum(str(x.get("file","")).startswith("images/") for x in photos)
 d["curation_status"]["lane1_coloratum_variant_photo_gap_20261024"]="CC_BY_2_EXACT_VARIETY_ANNOTATION_PROVISIONAL"
 d["curation_status"]["photos_not_local_vouchers"]=True
 encoded=(json.dumps(d,ensure_ascii=False,indent=2)+"\n").encode()
 if put(species,encoded,current["sha"],"Add actual CC BY 2.0 variety-identified Kleingrass "+organ+" photo panel"):
  print("ARCHIVED_AND_PUBLISHED",path,"bytes",len(data))
  break
 time.sleep(attempt+1)
else:raise SystemExit("Six concurrent edits; JPEG already archived, gallery held")
