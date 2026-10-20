#!/usr/bin/env python3
"""Install two visually checked, Wikimedia CC BY-SA Sorghum halepense structure photos.
Source pages were reviewed on 2026-10-20; do not invent an anatomical arrow.
All files and metadata are installed as an all-or-nothing action.
"""
import csv, hashlib, io, json, time
from pathlib import Path
import requests
from PIL import Image, ImageOps

ROOT=Path(".")
P=ROOT/"content/taxa/Poaceae/Sorghum/sorghum-halepense"
CARD=P/"species.json"
REPORT=ROOT/"reports/sorghum-halepense-commons-anatomy-20261020.json"
PICKS=[
 dict(
  name="commons-moadeeb-johnsongrass-rhizome.jpg",
  url="https://upload.wikimedia.org/wikipedia/commons/4/42/Sorghum_Halepense_Rhizome.jpg",
  source="https://commons.wikimedia.org/wiki/File:Sorghum_Halepense_Rhizome.jpg",
  creator="Moadeeb", license="CC BY-SA",
  license_url="https://creativecommons.org/licenses/by-sa/4.0/",
  description="Austin Texas source-labeled Johnsongrass underground horizontal stem with conspicuous pale segmented nodes and attached roots. Photograph does not provide a ruler or resolve every axillary bud.",
  role="Confirm underground structure — pale, jointed creeping rhizome, photographed as one continuous belowground stem with nodes. Some buds are not resolved; compare the joints with nearby true fine roots."
 ),
 dict(
  name="commons-matt-lavin-johnsongrass-ligule.jpg",
  url="https://upload.wikimedia.org/wikipedia/commons/2/27/Sorghum_halepense_%286134701986%29.jpg",
  source="https://commons.wikimedia.org/wiki/File:Sorghum_halepense_(6134701986).jpg",
  creator="Matt Lavin", license="CC BY-SA",
  license_url="https://creativecommons.org/licenses/by-sa/2.0/",
  description="Source-labeled Johnsongrass collar macro showing dense ligule fringe. The exact thin membrane base and 2–6 mm length cannot be independently measured here.",
  role="Look closer — hairy/fringed ligule region where blade meets sheath. Do not label an unmeasured 2–6 mm membrane from this angle; inspect a second collar with blade gently pulled back."
 )
]
def get_photo(url):
 session=requests.Session()
 session.headers["User-Agent"]="HaysCountyBotanyPhotoEducation/1.0 (https://github.com/Crking92/Hays-County-Botany; attributed Wikimedia Commons use)"
 last=""
 for attempt in range(3):
  try:
   response=session.get(url,timeout=55,headers={"Accept":"image/jpeg,image/*"})
   response.raise_for_status()
   original=response.content
   assert 18000<len(original)<12000000, "unexpected source file byte length"
   with Image.open(io.BytesIO(original)) as src:
    src.load()
    assert src.format in ("JPEG","PNG")
    img=ImageOps.exif_transpose(src).convert("RGB")
   assert min(img.size)>=700, "source not detailed enough"
   source_dimensions=list(img.size)
   digest=hashlib.sha256(original).hexdigest()
   img.thumbnail((1700,1700),Image.Resampling.LANCZOS)
   b=io.BytesIO();img.save(b,format="JPEG",quality=92,optimize=True,progressive=True)
   data=b.getvalue()
   assert len(data)>19000
   with Image.open(io.BytesIO(data)) as check: check.verify()
   return data,digest,source_dimensions,list(img.size)
  except Exception as exc:
   last=repr(exc)
   print("Retry",attempt+1,url,last[:160])
   time.sleep(3)
 raise RuntimeError("Download/verification failed: "+url+" "+last)
def main():
 card=json.loads(CARD.read_text(encoding="utf-8"))
 assert card["id"]=="sorghum-halepense"
 assert card["project_inclusion"]["target_zone_status"]=="INTRODUCED_NOT_NATIVE"
 assert len(card.get("unresolved_photo_references",[]))>0
 names={"images/"+p["name"] for p in PICKS}
 present={x["file"] for x in card["images"]}
 if names.issubset(present):
  assert len(card["images"])>=10
  print("Already installed: no changes")
  return
 assert len(card["images"])==8,"unexpected simultaneous changes: do not overwrite"
 assert not (names & present),"partial duplicate — manual inspection required"
 assert all("inat-154485533" not in f for f in present)
 assert all(not (P/"images"/p["name"]).exists() for p in PICKS)
 prepared=[(p,*get_photo(p["url"])) for p in PICKS]
 for p,bytes_,sha,source_dimensions,dimensions in prepared:
  (P/"images"/p["name"]).write_bytes(bytes_)
  card["images"].append(dict(
   file="images/"+p["name"],role=p["role"],creator=p["creator"],
   license=p["license"],license_url=p["license_url"],
   license_version_note="Wikimedia Commons file page documents exact CC BY-SA version: "+p["license_url"],
   source_platform="Wikimedia Commons, uploader/photographer exact-name Sorghum halepense",
   source_page=p["source"],downloaded_from=p["url"],
   original_image_sha256=sha,original_image_dimensions=source_dimensions,
   image_dimensions=dimensions,
   study_use="Public credited botanical field identification education",
   public_reuse="Attribution required; modifications to this image shared under CC BY-SA compatible terms.",
   modifications="Downscaled/resaved JPEG, EXIF removed; no illustrative arrows added.",
   anatomy_arrows="none, actual resized pixels need separate verified arrow audit",
   photo_review=p["description"]+" Source is attributed but identification not independently re-vouchered."
  ))
 if len(card["images"])!=10: raise RuntimeError("Expected 10 photos")
 status=card["curation_status"]
 status["photo_metadata_count"]=10;status["photo_files_present"]=10
 status["photo_source_checked"]=True;status["finished_field_id_pass"]="PASS_IN_PROGRESS"
 status["required_to_finish"]=[
  "Visually audit actual installed Commons JPEG pixels before placing any anatomy arrows",
  "Rhizome now photographed with visible scaly joints, but not every bud; seek a ruler and closer node/bud macro",
  "New ligule photo shows hairy collar but NOT a fully measurable 2–6 mm ciliate membrane; second angle required",
  "Complete sessile+pedicelled spikelet pair with intact bases and scale remains missing",
  "Audit older Dan Johnson and Sam Kieschnick exact photo license versions",
  "Preserve historical rejected non-plant hand-only photo outside gallery"
 ]
 card["diagnostic_image_needs"]=[
  {"role":"Ligule and auricle-free collar macro","status":"PARTIAL_PHOTO_FRINGE_VISIBLE_MEMBRANE_UNMEASURED"},
  {"role":"Exposed intact rhizome with scale-covered nodes","status":"PHOTO_ADDED_NODES_VISIBLE_BUD_MACRO_STILL_NEEDED"},
  {"role":"Paired fertile and pedicelled spikelets with scale","status":"NEEDS_DIAGNOSTIC_PHOTO"}
 ]
 card["learner_visual_status"].update(
  image_count=10,
  mode="species_photo_enriched_ten_real_images_rhizome_and_ligule_partial",
  note="10 publicly reusable attributed real photographs, including CC BY-SA Austin rhizome and photographed hairy collar. Three earlier arrows remain manually pixel-verified. No new unverified arrows. Full exposed ligule membrane with measurement, rhizome buds macro, and complete spikelet pair still pending."
 )
 card["field_id_finalization"]["stage"]="PROVISIONAL"
 card["field_id_finalization"]["flags"]=["NEEDS_DIAGNOSTIC_PHOTO"]
 card["field_id_finalization"]["photo_review"] = (
  "2026-10-20: 10 real credited CC BY / CC BY-SA files. Two Commons photos added: clear pale segmented rhizome and hairy collar/ligule fringe. No new arrows or false measurable membrane claims. Three earlier annotated source-verified arrows remain. Complete paired spikelet macro, measurable ligule membrane and node/bud closeup are pending; two old photograph license versions to reconfirm."
 )
 card["photo_note"] += " 2026-10-20: Commons rhizome and collar partial-anatomy photos added under verified CC BY-SA 4.0 and CC BY-SA 2.0 source licensing; no new unverified arrow. Total ten."
 CARD.write_text(json.dumps(card,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 ledger=P/"image-sources.csv"
 with ledger.open(newline="",encoding="utf-8") as f:
  reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
 for p,bytes_,sha,original_dimensions,dimensions in prepared:
  row={f:"" for f in fields}
  vals={
   "file_name":p["name"],"role":p["role"],"creator":p["creator"],
   "license":p["license"],"source_page":p["source"],"direct_url":p["url"],
   "study_use":"Credited public education CC BY-SA",
   "public_reuse":"CC BY-SA attribution and share alike, link to exact license",
   "modifications":"Downscaled JPEG, EXIF removed; no arrows",
  }
  for k,v in vals.items():
   if k in row:row[k]=v
  rows.append(row)
 with ledger.open("w",newline="",encoding="utf-8") as f:
  writer=csv.DictWriter(f,fieldnames=fields,lineterminator="\n")
  writer.writeheader();writer.writerows(rows)
 REPORT.write_text(json.dumps({
  "species":"Sorghum halepense","total":10,"new_count":2,
  "public_licenses":["CC BY-SA 4.0","CC BY-SA 2.0"],
  "photos":[dict(file=p["name"],source=p["source"],license_url=p["license_url"],original_sha256=sha) for p,b,sha,*_ in prepared],
  "not_yet_claimed":["measurable complete ligule membrane","rhizome axillary bud macro","complete spikelet pair"],
  "historical_nonplant_image_excluded":True,
  "annotation_status":"Existing three remain; new arrows pending visual QA"
 },indent=2)+"\n",encoding="utf-8")
 print("Installed 2 public-safe photos; total 10; Johnsongrass remains provisional")
if __name__=="__main__": main()
