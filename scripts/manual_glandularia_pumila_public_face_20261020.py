#!/usr/bin/env python3
"""Install actual individual CC BY-SA Pl@ntNet Glandularia pumila face in canonical gallery.
Source is the species page which identifies Angela's photo/license; do not substitute taxa.
No arrows added until saved file visually reviewed. Guard existing restricted image rights.
"""
import csv,hashlib,io,json,time
from pathlib import Path
import requests
from PIL import Image,ImageOps

ROOT=Path(".")
BASE=ROOT/"content/taxa/Verbenaceae/Glandularia/glandularia-pumila"
CARD=BASE/"species.json"
OUT=BASE/"images/plantnet-angela-pumila-face.jpg"
REPORT=ROOT/"reports/glandularia-pumila-public-face-20261020.json"
URL="https://bs.plantnet.org/image/o/258f239e64608ec94f364a119185b4a4576d9472"
SOURCE="https://identify.plantnet.org/el/namerica/species/Glandularia%20pumila%20(Rydb.)%20Umber/data"
def load_image():
 s=requests.Session();s.headers.update({"User-Agent":"HaysBotanyPublicLicensedStudy/1.0 (https://github.com/Crking92/Hays-County-Botany)"})
 last=None
 for i in range(3):
  try:
   res=s.get(URL,timeout=50)
   res.raise_for_status()
   raw=res.content
   assert 14000<len(raw)<15000000
   assert "image" in res.headers.get("Content-Type","image/jpeg")
   with Image.open(io.BytesIO(raw)) as source:
    source.load(); im=ImageOps.exif_transpose(source).convert("RGB")
   assert min(im.size)>=550
   srcdim=list(im.size)
   im.thumbnail((1500,1500),Image.Resampling.LANCZOS)
   buf=io.BytesIO();im.save(buf,format="JPEG",quality=93,optimize=True,progressive=True)
   processed=buf.getvalue()
   assert len(processed)>15000
   with Image.open(io.BytesIO(processed)) as check:check.verify()
   return processed,hashlib.sha256(raw).hexdigest(),srcdim,list(im.size)
  except Exception as exc:
   last=repr(exc)
   print("Photo retry",i+1,last[:160]);time.sleep(3)
 raise RuntimeError("No verified species photo downloadable; maintain source-only hold: "+str(last))
def main():
 man=json.loads((ROOT/"data/manifest.json").read_text())
 assert sum(x["id"]=="glandularia-pumila" for x in man["species"])==1
 j=json.loads(CARD.read_text(encoding="utf-8"))
 assert j["scientific_name"]=="Glandularia pumila"
 assert j["project_inclusion"]["target_zone_status"]=="PASS"
 assert len(j["images"])==4
 before=j["images"][0]
 if before["file"]=="images/plantnet-angela-pumila-face.jpg":
  assert OUT.exists() and OUT.stat().st_size>15000
  print("Source face previously installed. No-op.");return
 assert before["file"]==URL, "expected exact original remote species image; refusing to overwrite"
 assert before["creator"].startswith("Angela") and before["license"]=="CC BY-SA 3.0"
 assert not OUT.exists()
 assert j["images"][1]["license"]=="Owner-authorized private study"
 assert all(x["license"]=="CC BY" for x in j["images"][2:])
 data,digest,srcdim,dims=load_image()
 OUT.parent.mkdir(parents=True,exist_ok=True)
 OUT.write_bytes(data)
 face={**before,
  "file":"images/plantnet-angela-pumila-face.jpg",
  "previous_remote_file":URL,
  "role":"Recognize Glandularia pumila — photographed broad fan-lobed simple leaf and crowded small pink-lilac flowers on leafy shoot; not ripe fruits.",
  "creator":"Angela (Pl@ntNet contributor)",
  "license":"CC BY-SA 3.0",
  "license_url":"https://creativecommons.org/licenses/by-sa/3.0/",
  "source_page":SOURCE,
  "source_platform":"Pl@ntNet featured exact-species photo with displayed author and CC license",
  "original_image_sha256":digest,
  "original_image_dimensions":srcdim,
  "image_dimensions":dims,
  "downloaded_from":URL,
  "remote_only":False,
  "local_file_present":True,
  "modifications":"Resaved source JPEG at full source resolution up to 1500 pixels, EXIF removed; no image pixels retouched.",
  "photo_review":"Exact species label and photographer/license displayed together on Pl@ntNet page. Anatomy arrows pending readback of saved JPEG pixels.",
  "anatomy_arrows":"none; actual downloaded photograph awaiting real-pixel target confirmation",
  "public_reuse":"CC BY-SA 3.0: attribute Angela and original photo + link exact license, share adaptions alike."
 }
 j["images"][0]=face
 j["curation_status"]["photo_files_present"]=4
 j["curation_status"]["licensed_face_physically_installed"]="2026-10-20"
 j["curation_status"]["photo_metadata_count"]=4
 j["curation_status"]["finished_field_id_pass"]="PASS_IN_PROGRESS"
 j["learner_visual_status"]={**(j.get("learner_visual_status") or {}), "status":"provisional_learner_ready","image_count":4,"mode":"four_photos_including_local_cc_by_sa_species_face","note":"Angela's individual CC BY-SA 3.0 Pl@ntNet source-face now locally saved, along with old owner-private image and two CC BY library review photos. Real anatomy overlay/mature compact FRUIT comparison still outstanding."}
 j["photo_note"]+=" 2026-10-20: Exact original public-safe source-licensed Angela Pl@ntNet species face physically archived; no unreviewed anatomy arrows."
 j["field_id_finalization"]["photo_review"]="Actual original Pl@ntNet CC BY-SA 3.0 featured image physically downloaded, decoded and SHA stored. Existing local Jo and owner images preserved without license changes. Now ready for saved JPEG pixel arrow review."
 CARD.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 csvpath=BASE/"image-sources.csv"
 with csvpath.open(newline="",encoding="utf-8") as f:
  reader=csv.DictReader(f);cols=reader.fieldnames;rows=list(reader)
 row={c:"" for c in cols}
 update={"file_name":OUT.name,"role":face["role"],"platform":"Pl@ntNet","creator":"Angela","license":"CC BY-SA 3.0","license_url":face["license_url"],"source_page":SOURCE,"direct_image_url":URL,"study_use":"Public botanical education","public_reuse":"yes with attribution and ShareAlike","modifications":"EXIF stripped; local JPEG copy"}
 for key,val in update.items():
  if key in row:row[key]=val
 rows.append(row)
 with csvpath.open("w",newline="",encoding="utf-8") as f:
  writer=csv.DictWriter(f,fieldnames=cols,lineterminator="\n")
  writer.writeheader();writer.writerows(rows)
 REPORT.parent.mkdir(parents=True,exist_ok=True)
 REPORT.write_text(json.dumps({"species":"Glandularia pumila","license":"CC BY-SA 3.0","creator":"Angela","file":str(OUT),"source":SOURCE,"source_url":URL,"sha256":digest,"source_dimensions":srcdim,"public_safe_photos_added":1,"total_gallery_records":4,"existing_restricted_photos_unchanged":True,"arrows_added":0,"still_missing":["mature fruit axis macro","individual bract-vs-calyx macro"]},indent=2)+"\n",encoding="utf-8")
 print("PASS Installed CC BY-SA photo; 4 original gallery records unchanged in count")
if __name__=="__main__":main()
