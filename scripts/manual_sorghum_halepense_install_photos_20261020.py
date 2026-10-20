#!/usr/bin/env python3
"""One-time Johnsongrass exact-species individual-CC-licensed photo installation.
Only original real photos screened at pixel level. Preserve the previous
rejected hand-only nonplant image outside images[], do not alter taxonomy holds.
"""
import csv,hashlib,io,json
from pathlib import Path
from PIL import Image,ImageOps
import requests
ROOT=Path(".")
P=ROOT/"content/taxa/Poaceae/Sorghum/sorghum-halepense"
CARD=P/"species.json"
SCREEN=ROOT/"workflow/photo-library/reviews/sorghum-halepense-20261020/screen.json"
REPORT=ROOT/"reports/sorghum-halepense-photo-upgrade-20261020.json"
PICKS=[
 ("112589107","annikaml-112589107-whole-clump-flowering.jpg",
 "Recognize it — leafy field clump with purple panicles, visible broad leaves and neighboring graminoids. Plant identity from research-grade observation, full rhizome not in frame."),
 ("753122016","lindajo-753122016-white-midrib-blade.jpg",
 "Look closer — wide grass leaf blade with a clearly pale central midrib against fingers/soil. Blade sheath/ligule insertion is not clearly resolved."),
 ("753122364","lindajo-753122364-spikelet-closeup.jpg",
 "Look closer — small spikelet units with pollen-producing anthers and delicate plumelike stigmas. A full sessile-pedicelled PAIR cannot be certified from this angle alone."),
 ("753122718","lindajo-753122718-panicle-flower-details.jpg",
 "Look closer — fine branch with close reproductive units and visible flower parts, hand scale. Sessile/pedicel attachment still requires fully exposed base."),
 ("1115145","lauramorganclark-1115145-ruler-panicle.jpg",
 "Confirm context — flowering panicle next to real field ruler; plant head is relatively open with many radiating fine branches; no ligule/rhizome illustrated."),
 ("1822861","sambiology-1822861-tall-roadside-stand.jpg",
 "Recognize it — tall robust vegetative grass colony at disturbed trail/road edge, broad curved blades; exact stem junction and rhizomes not visible.")
]
S=requests.Session();S.headers.update({"User-Agent":"HaysBotanySorghumPhotoInstall/1.0 (github.com/Crking92/Hays-County-Botany)"})
def download(row):
 pid=str(row["photo_id"]);url=row["photo_url"]
 for src in dict.fromkeys([url.replace("/large.","/original."),url,
  "https://inaturalist-open-data.s3.amazonaws.com/photos/"+pid+"/original.jpg",
  "https://inaturalist-open-data.s3.amazonaws.com/photos/"+pid+"/large.jpg"]):
  try:
   r=S.get(src,timeout=40);r.raise_for_status()
   if not 19000<len(r.content)<16000000:continue
   with Image.open(io.BytesIO(r.content)) as original:
    original.load();im=ImageOps.exif_transpose(original).convert("RGB")
   if min(im.size)<320:continue
   sha=hashlib.sha256(r.content).hexdigest()
   im.thumbnail((1450,1450),Image.Resampling.LANCZOS)
   buf=io.BytesIO();im.save(buf,format="JPEG",quality=90,optimize=True,progressive=True)
   data=buf.getvalue()
   if len(data)<19000:continue
   with Image.open(io.BytesIO(data)) as test:test.verify()
   return data,sha,list(im.size),src
  except Exception as e:print("Candidate retry",pid,str(e)[:150])
 raise RuntimeError("Failed photo "+pid+" — no partial installation")
def main():
 man=json.loads((ROOT/"data/manifest.json").read_text())
 assert sum(x["id"]=="sorghum-halepense" for x in man["species"])==1
 claims=json.loads((ROOT/"workflow/work-claims.json").read_text()).get("claims",[])
 assert not any("sorghum-halepense" in (c.get("taxa") or []) and c.get("status") in ("active","claimed","in_progress") for c in claims)
 card=json.loads(CARD.read_text())
 assert card["scientific_name"]=="Sorghum halepense" and card["id"]=="sorghum-halepense"
 assert card["project_inclusion"]["target_zone_status"]=="INTRODUCED_NOT_NATIVE"
 assert len(card["unresolved_photo_references"])>=1
 images=card["images"]
 if len(images)==8 and all(any(z["file"]=="images/"+name for z in images) for _,name,_ in PICKS):
  print("Already installed, no-op");return
 assert len(images)==2 and images[0]["file"]=="images/library-review045-be8202c19cd1029.jpg"
 assert images[1]["file"]=="images/library-review045-30a192f0096dd1d.jpg"
 screen=json.loads(SCREEN.read_text());assert screen["species"]=="Sorghum halepense"
 byid={str(x["photo_id"]):x for x in screen["candidates"]}
 prepared=[]
 for pid,name,role in PICKS:
  x=byid[pid]
  assert x["source_taxon"]=="Sorghum halepense" and x["grade"]=="research" and x.get("preview_sha256")
  assert x["license_code"] in ("cc-by","cc0","cc-by-sa")
  assert not (P/"images"/name).exists()
  prepared.append((pid,name,role,x,*download(x)))
 for pid,name,role,x,data,sha,dims,url in prepared:
  destination=P/"images"/name;destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(data)
  lic={"cc-by":"CC BY","cc0":"CC0","cc-by-sa":"CC BY-SA"}[x["license_code"]]
  images.append({
   "file":"images/"+name,"role":role,"creator":x["credit"] or x["photographer"],
   "license":lic,
   "license_version_note":"iNaturalist individually provided photo license_code="+x["license_code"]+"; exact version not separately checked.",
   "source_platform":"iNaturalist, Texas research-grade exact taxon name",
   "source_page":x["source_page"],"source_observation_page":x["observation_page"],
   "source_photo_id":pid,"downloaded_from":url,
   "original_image_sha256":sha,"image_dimensions":dims,
   "study_use":"Public credited crew botanical education, photo-specific CC terms",
   "public_reuse":"CC BY/CC0/CC BY-SA applies to individual photo: original photographer attribution and ShareAlike if required.",
   "modifications":"Downscaled, JPEG resaved, EXIF removed; no arrows until final physical JPEG inspection.",
   "anatomy_arrows":"none, awaiting pixel-level verified arrows",
   "photo_review":"Source research-grade iNaturalist determination and visually checked original preview. This is not an independent expert botanical voucher; organs not actually in frame must not be claimed."
  })
 card["curation_status"].update({
  "photo_metadata_count":len(images),"photo_files_present":len(images),
  "photo_source_checked":True,"visual_reviewed":False,"finished_field_id_pass":"PASS_IN_PROGRESS",
  "diagnostic_gallery_addition":"2026-10-20",
  "required_to_finish":[
   "Review newly installed actual JPEGs full-size and label only visible midrib/panicle or other real anatomy",
   "A true underground SCALY RHIZOME with intact buds/nodes and 2–6 mm hairy-edged MEMBRANOUS LIGULE photo still needed",
   "Complete paired sessile and pedicelled spikelet macro with basal attachments still needed",
   "Review older Dan Johnson and Sam Kieschnick individual source-photo license versions",
   "Historical excluded hand-only CC BY-NC photo must stay OUT of images[]"
  ]
 })
 card["learner_visual_status"].update({
  "image_count":len(images),"mode":"species_photo_enriched_eight_real_images_missing_rhizome_ligule_macro",
  "note":"8 original photo files, old 2 plus new 6 individually public-licensed. Tall vegetative stand, pale midrib, open heads, flowering organs; serious diagnostic rhizome+membranous ligule+complete spikelet pair still need distinct photo evidence."
 })
 card["photo_note"]+=" 2026-10-20: six source-licensed Texas source photos added after 48-image visual screen; historical hand-only CC BY-NC remains outside displayed gallery. 8 actual photos, provisional identification confidence.";
 CARD.write_text(json.dumps(card,indent=2,ensure_ascii=False)+"\n")
 ledger=P/"image-sources.csv"
 with ledger.open(newline="") as f:
  reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
 for pid,name,role,x,data,sha,dims,url in prepared:
  row={f:"" for f in fields}
  vals={"file_name":name,"role":role,"creator":x["credit"] or x["photographer"],
   "license":{"cc-by":"CC BY","cc0":"CC0","cc-by-sa":"CC BY-SA"}[x["license_code"]],
   "source_page":x["source_page"],"direct_url":url,"study_use":"CC attributed public crew field ID",
   "public_reuse":"CC terms individual-photo with attribution and indicated alterations",
   "observation_id":x["observation_id"],"photo_id":pid,"modifications":"Resized JPEG, EXIF removed"}
  for key,val in vals.items():
   if key in row:row[key]=val
  rows.append(row)
 with ledger.open("w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(rows)
 REPORT.write_text(json.dumps({"species":"Sorghum halepense","previous":2,"added":len(prepared),"total":len(images),
  "new_files":[name for pid,name,*_ in prepared],"previous_excluded_photo_preserved_not_visible":True,
  "introduced_in_Texas":True,"pending":"Rhizome/ligule/full paired spikelet macro", "published":False},indent=2)+"\n")
 print("Installed",len(prepared),"source-licensed real photos; total",len(images))
if __name__=="__main__":main()
