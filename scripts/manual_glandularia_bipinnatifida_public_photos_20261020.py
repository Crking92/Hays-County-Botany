#!/usr/bin/env python3
"""Add locally stored, publicly licensed exact species teaching photos to prairie verbena.
Replaces two existing remote-only photos with their exact local copies and adds three
new photographs. Attribution, original source and modifications are retained.
NO anatomy arrows are invented before real downloaded pixel inspection.
"""
import csv, hashlib, io, json, time
from pathlib import Path
from urllib.parse import quote
import requests
from PIL import Image, ImageOps

ROOT=Path(".")
P=ROOT/"content/taxa/Verbenaceae/Glandularia/glandularia-bipinnatifida"
CARD=P/"species.json"
REPORT=ROOT/"reports/glandularia-bipinnatifida-public-photos-20261020.json"
PHOTOS=[
 dict(
  title="Glandularia bipinnatifida.jpg",name="commons-masonbrock-texas-prairie-verbena.jpg",
  creator="Mason Brock",license="Public Domain",license_url="https://commons.wikimedia.org/wiki/File:Glandularia_bipinnatifida.jpg",
  role="Recognize it — Texas wild plant photographed in dry rocky Ellis County prairie; show general clustered purple flowers and coarse habitat context. Only label structures actually visible.",
  replace_existing=0),
 dict(
  title="Glandularia bipinnatifida 000000000527.jpg",name="commons-fonseca-prairie-verbena-527.jpg",
  creator="Juan Carlos Fonseca Mata",license="CC BY-SA",license_url="https://creativecommons.org/licenses/by-sa/4.0/",
  role="Look closer — source-verified Glandularia flower cluster and cut foliage. Distinguish individual five-lobed corolla, calyx and pinnate leaves only if clear in downloaded pixels.",
  replace_existing=2),
 dict(
  title="Glandularia bipinnatifida 554081866.jpg",name="commons-annika-554081866-texas.jpg",
  creator="Annika Lindqvist",license="CC BY",license_url="https://creativecommons.org/licenses/by/4.0/",
  role="Recognize it — source-ID prairie verbena in Central Texas. Photograph useful for species context; leaf and flower anatomy remain visually unmarked pending full-frame inspection.",
  replace_existing=None),
 dict(
  title="Glandularia bipinnatifida 586522824.jpg",name="commons-michelle-586522824-comal.jpg",
  creator="Michelle W. （鍾偉瑋）",license="CC BY",license_url="https://creativecommons.org/licenses/by/4.0/",
  role="Recognize it — public-reusable Comal County Texas exact-name Glandularia field photo, useful for regional comparison; no unverified anatomy labels.",
  replace_existing=None),
 dict(
  title="Glandularia bipinnatifida (Verbenaceae) 171222.jpg",name="commons-fonseca-171222-flowering.jpg",
  creator="Juan Carlos Fonseca Mata",license="CC BY-SA",license_url="https://creativecommons.org/licenses/by-sa/4.0/",
  role="Flower and stem detail — independently credited specimen of Glandularia bipinnatifida. Compare head and foliage from a second camera angle; confirm anatomical substructures before adding arrows.",
  replace_existing=None)
]
session=requests.Session()
session.headers.update({"User-Agent":"HaysCountyBotanyPublicPhotoInstaller/1.0 (https://github.com/Crking92/Hays-County-Botany)"})
def commons_source(title):
 filename=title.replace(" ","_")
 md5=hashlib.md5(filename.encode("utf-8")).hexdigest()
 return "https://upload.wikimedia.org/wikipedia/commons/"+md5[0]+"/"+md5[:2]+"/"+quote(filename,safe="()_")
def download(photo):
 path=commons_source(photo["title"])
 last_error=""
 for candidate in [path,"https://commons.wikimedia.org/wiki/Special:Redirect/file/"+quote(photo["title"].replace(" ","_"))]:
  for attempt in range(3):
   try:
    response=session.get(candidate,timeout=55)
    response.raise_for_status()
    raw=response.content
    assert 18000<len(raw)<20000000 and response.headers.get("Content-Type","").startswith("image/"),"not a JPG"
    with Image.open(io.BytesIO(raw)) as src:
     src.load()
     assert src.format=="JPEG","unexpected image format"
     image=ImageOps.exif_transpose(src).convert("RGB")
    assert min(image.size)>600,"image too small"
    original_dimensions=list(image.size)
    sha=hashlib.sha256(raw).hexdigest()
    image.thumbnail((1600,1600),Image.Resampling.LANCZOS)
    buf=io.BytesIO();image.save(buf,"JPEG",quality=91,optimize=True,progressive=True)
    data=buf.getvalue()
    assert len(data)>19000
    with Image.open(io.BytesIO(data)) as check:check.verify()
    return data,sha,original_dimensions,list(image.size),response.url
   except Exception as exc:
    last_error=repr(exc)
    print("Retry",photo["name"],attempt+1,last_error[:150])
    time.sleep(2)
 raise RuntimeError("Failed to retrieve / verify: "+photo["title"]+" "+last_error)
def main():
 manifest=json.loads((ROOT/"data/manifest.json").read_text())
 assert sum(x["id"]=="glandularia-bipinnatifida" for x in manifest["species"])==1
 card=json.loads(CARD.read_text(encoding="utf-8"))
 assert card["scientific_name"]=="Glandularia bipinnatifida"
 assert card["project_inclusion"]["target_zone_status"]=="PASS"
 assert card["curation_status"]["finished_field_id_pass"]=="PASS_IN_PROGRESS"
 images=card["images"]
 expected={"images/"+p["name"] for p in PHOTOS}
 if len(images)==10 and expected.issubset({x["file"] for x in images}):
  print("Already installed, not modifying")
  return
 assert len(images)==7,"unexpected gallery state; review any concurrent edits"
 assert images[0]["creator"]=="Mason Brock" and images[2]["creator"]=="Juan Carlos Fonseca Mata"
 assert all(not (P/"images"/x["name"]).exists() for x in PHOTOS)
 # All downloads finish and decode before ANY photo or metadata changes.
 prepared=[(p,*download(p)) for p in PHOTOS]
 for p,bytes_,sha,origdim,dim,url in prepared:
  dest=P/"images"/p["name"]
  dest.parent.mkdir(parents=True,exist_ok=True)
  dest.write_bytes(bytes_)
  title=p["title"]
  source="https://commons.wikimedia.org/wiki/File:"+quote(title.replace(" ","_"),safe="()_")
  old=images[p["replace_existing"]] if p["replace_existing"] is not None else {}
  row=dict(old)
  if old:row["previous_remote_file"]=old["file"]
  row.update(
   file="images/"+p["name"],role=p["role"],creator=p["creator"],license=p["license"],
   license_url=p["license_url"],source_platform="Wikimedia Commons, licensed original photo",
   source_page=source,downloaded_from=url,original_image_sha256=sha,
   original_image_dimensions=origdim,image_dimensions=dim,
   source_taxon="Glandularia bipinnatifida",study_use="Credited public botanical education",
   public_reuse="Yes; obey linked individual Public Domain/CC BY/CC BY-SA source rights.",
   modifications="EXIF removed and image downscaled to 1600 pixels; no arrows added.",
   anatomy_arrows="none, no pixel-validated annotation added by this installer",
   photo_review="Exact species and individual photographer/source license independently researched; source image pixel-level anatomy arrow review still pending."
  )
  if p["replace_existing"] is not None:images[p["replace_existing"]]=row
  else:images.append(row)
 assert len(images)==10
 card["curation_status"]["photo_metadata_count"]=len(images)
 card["curation_status"]["photo_files_present"]=sum(x["file"].startswith("images/") for x in images)
 card["curation_status"]["public_licensed_gallery_update"]="2026-10-20"
 card["curation_status"]["finished_field_id_pass"]="PASS_IN_PROGRESS"
 card["learner_visual_status"]=dict(card.get("learner_visual_status") or {},
  status="provisional_learner_ready",image_count=10,
  mode="ten_photo_mix_more_local_public_sources_annotated_macro_pending",
  note="Five original public-safe Commons photos locally archived, two previous remote sources replaced not duplicated; existing mixed-license private-study photographs retained with unaltered restrictive credit. NEW sources contain NO anatomy arrows pending actual JPEG pixel QA. Need true bract/calyx and old fruiting axis macros.")
 card["photo_note"]=str(card.get("photo_note") or "")+" 2026-10-20: 5 public-safe Wikimedia photos physically archived (2 replace remote only, 3 new), 10 gallery records total. No new arrows invented."
 card["field_id_finalization"]["photo_review"]="2026-10-20 five public-domain/CC BY/CC BY-SA Commons photo originals downloaded and saved with creator/license and SHA-256. Existing private-study photos remain marked restricted. Need view final JPEGs before ANY newly promised leaf/flower/bract arrows."
 CARD.write_text(json.dumps(card,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 ledger=P/"image-sources.csv"
 with ledger.open(newline="",encoding="utf-8") as f:
  reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
 for p,data,sha,origdim,dim,url in prepared:
  source="https://commons.wikimedia.org/wiki/File:"+quote(p["title"].replace(" ","_"),safe="()_")
  entry={field:"" for field in fields}
  e=dict(file_name=p["name"],role=p["role"],platform="Wikimedia Commons",creator=p["creator"],
         license=p["license"],source_page=source,direct_image_url=url,
         study_use="public credited educational",public_reuse="yes individual CC/PD",
         license_url=p["license_url"],source_context="Individually licensed source; exact source and photographer checked; no new arrows.",
         modifications="Downscaled JPEG, stripped EXIF")
  for k,v in e.items():
   if k in entry:entry[k]=v
  rows.append(entry)
 with ledger.open("w",newline="",encoding="utf-8") as f:
  writer=csv.DictWriter(f,fieldnames=fields,lineterminator="\n")
  writer.writeheader();writer.writerows(rows)
 REPORT.parent.mkdir(parents=True,exist_ok=True)
 REPORT.write_text(json.dumps({
  "species":"Glandularia bipinnatifida",
  "photos_physically_installed":5,
  "old_remote_replaced":2,"new_gallery_records":3,"total_gallery_records":10,
  "rights_check":"One public-domain; two CC BY 4.0; two CC BY-SA 4.0",
  "photo_records":[{"file":p["name"],"source_title":p["title"],"sha256":sha,"source_url":url,"license":p["license"]} for p,data,sha,origdim,dim,url in prepared],
  "no_false_arrows":True,
  "photo_macro_holds":["mature leaf-pair arrow","individual bract vs hairy calyx macro","old elongated fruiting spike"],
  "public_photo_caveat":"3 Joey CC BY-NC and 1 owner-private image in pre-existing gallery remain unchanged; separate policy gate required for any reuse restriction."
 },indent=2)+"\n",encoding="utf-8")
 print("PASS Prairie verbena: five source-licensed physical pictures, ten records, three additions; missing anatomy still tracked")
if __name__=="__main__":main()
