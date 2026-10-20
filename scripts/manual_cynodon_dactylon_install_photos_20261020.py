#!/usr/bin/env python3
"""One-time Bermudagrass field lesson six photo-source vetted upgrades.
Keep original Zinogre CC BY-SA and Dan Johnson CC BY, preserve taxon nonnative
designation. Do not claim belowground rhizome from a surface runner photo.
"""
import csv,hashlib,io,json
from pathlib import Path
import requests
from PIL import Image,ImageOps
BASE=Path("content/taxa/Poaceae/Cynodon/cynodon-dactylon")
CARD=BASE/"species.json"
SCREEN=Path("workflow/photo-library/reviews/cynodon-dactylon-20261020/screen.json")
REPORT=Path("reports/cynodon-dactylon-six-diagnostic-photo-20261020.json")
PICKS=[
("1414422","sam-1414422-dense-mat.jpg","Recognize it: spreading mown living Bermudagrass green mat in lawn; roots are not exposed."),
("410585094","jimmex-410585094-stolon-leafy-node.jpg","Look closer: aboveground running wiry stem with shoot at a node and leaves. Roots not independently exposed and this picture does NOT prove an underground rhizome."),
("410585092","jimmex-410585092-collar-hair-fringe.jpg","Look closer: grass collar area with pale hair tufts at inner blade-sheath junction; do not interpret unscaled hairs as measured 0.5-mm ligule."),
("410585069","jimmex-410585069-spikelet-macro.jpg","Look closer: spikelets and extruded dark pinkish anthers alongside a narrow spike branch; useful one-sided spikelet architecture macro."),
("410585068","jimmex-410585068-finger-seedhead.jpg","Recognize head: several slim finger-like rays radiate from terminal culm tip, each carrying tiny spikelets, seedhead silhouette."),
("752837036","texas-nature-752837036-curb-turf-edge.jpg","Field context: growing edge of dense Bermuda turf beside sidewalk/curb; do not infer that every roadside lawn contains only this species.")
]
S=requests.Session();S.headers.update({"User-Agent":"HaysBotanyCrewCynodonPhotoInstaller/1.0 (github.com/Crking92/Hays-County-Botany)"})
def download(row):
 pid=str(row["photo_id"])
 url=row["photo_url"]
 choices=[url.replace("/large.","/original."),url,
  "https://inaturalist-open-data.s3.amazonaws.com/photos/"+pid+"/original.jpg",
  "https://inaturalist-open-data.s3.amazonaws.com/photos/"+pid+"/large.jpg"]
 for source in dict.fromkeys(choices):
  try:
   response=S.get(source,timeout=37);response.raise_for_status()
   if not 26000<len(response.content)<16500000:continue
   with Image.open(io.BytesIO(response.content)) as old:
    old.load();image=ImageOps.exif_transpose(old).convert("RGB")
   if min(image.size)<420:continue
   image.thumbnail((1450,1450),Image.Resampling.LANCZOS)
   buf=io.BytesIO();image.save(buf,format="JPEG",quality=90,optimize=True,progressive=True)
   data=buf.getvalue()
   with Image.open(io.BytesIO(data)) as check:check.verify()
   if len(data)<22000:continue
   return data,hashlib.sha256(response.content).hexdigest(),list(image.size),source
  except Exception as e:print("Retry image",pid,str(e)[:110])
 raise RuntimeError("No valid identical-species media for "+pid)
def main():
 m=json.loads(Path("data/manifest.json").read_text())
 assert sum(x["id"]=="cynodon-dactylon" for x in m["species"])==1
 claims=json.loads(Path("workflow/work-claims.json").read_text()).get("claims",[])
 assert not any("cynodon-dactylon" in (c.get("taxa") or []) and c.get("status") in ("active","claimed","in_progress") for c in claims)
 card=json.loads(CARD.read_text())
 assert card["id"]=="cynodon-dactylon" and card["project_inclusion"]["target_zone_status"]=="INTRODUCED_NOT_NATIVE"
 imgs=card["images"]
 if all(any(x["file"]=="images/"+name for x in imgs) for _,name,_ in PICKS):
  print("Already installed all candidate images");return
 assert len(imgs)==2 and imgs[0]["file"]=="images/inat-136428732.jpg"
 assert imgs[1]["file"]=="images/library-review052-b8e271bb0d86343.jpg"
 screen=json.loads(SCREEN.read_text())
 assert screen["species"]=="Cynodon dactylon"
 source={str(x["photo_id"]):x for x in screen["candidates"]}
 ready=[]
 for pid,name,role in PICKS:
  x=source[pid]
  assert x.get("preview_sha256") and x["grade"]=="research" and x["source_taxon"]=="Cynodon dactylon"
  assert x["license_code"] in ("cc0","cc-by","cc-by-sa")
  assert not (BASE/"images"/name).exists()
  ready.append((pid,name,role,x,*download(x)))
 for pid,name,role,x,data,sha,dims,url in ready:
  dest=BASE/"images"/name
  dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
  lic={"cc0":"CC0","cc-by":"CC BY","cc-by-sa":"CC BY-SA"}[x["license_code"]]
  imgs.append({
    "file":"images/"+name,"role":role,"creator":x["credit"] or x["photographer"],"license":lic,
    "license_version_note":"Photo-specific iNaturalist license_code="+x["license_code"]+" verified; subversion not separately confirmed.",
    "source_page":x["source_page"],"source_observation_page":x["observation_page"],
    "source_platform":"iNaturalist Texas research-grade exact-name observation",
    "source_photo_id":pid,"downloaded_from":url,"original_image_sha256":sha,
    "image_dimensions":dims,"study_use":"Credited public educational crew field ID under photo-specific CC license",
    "public_reuse":"CC0 or CC BY/CC BY-SA, credit original creator and note alterations/ShareAlike as applicable",
    "modifications":"Resized from original, reencoded JPEG and EXIF stripped; original unchanged; no arrows on this first gallery install",
    "anatomy_arrows":"none pending manual full JPEG exact anatomy pass",
    "photo_review":"Photo individually licensed and visually reviewed in Texas source contact sheet. Photo species source determined research-grade; exact grass hybrid/turf determination not independently verified. Never infer rhizome/collar micro if not visible."
  })
 card["images"]=imgs
 card["curation_status"].update({
  "photo_metadata_count":len(imgs),"photo_files_present":len(imgs),"photo_source_checked":True,
  "visual_reviewed":False,"manual_six_photo_install":"2026-10-20",
  "finished_field_id_pass":"PASS_IN_PROGRESS",
  "required_to_finish":[
   "Inspect installed original-resolution candidate photos, specifically collar macro and unilateral spikelet macro, then annotate only physically visible organs",
   "True underground scaly RHIZOME + roots at stolon node field macro remains missing; don't label a surface runner rhizome",
   "Old Dan Johnson GBIF individual image exact license version and Zinogre CC BY-SA version remain unverified",
   "Retain introduced/non-native Kew decision, regardless of plant utility in turf."
  ]
 })
 card["learner_visual_status"].update({
  "image_count":len(imgs),"mode":"finished_text_eight_physical_images_pending_arrows_and_rhizome_macro",
  "note":"8 real photos total: old 2 plus 6 individually photo-licensed exact-name Texas references. Field context, collar tuft, flowers, one-sided spikelets and surface runner views. Underground rhizome not yet shown."
 })
 card["photo_note"]+=" 2026-10-20 six separately licensed Texas-source field photos installed after visual screening; 8 total, no true underground rhizome or measured hair-ligule macro claimed."
 CARD.write_text(json.dumps(card,indent=2,ensure_ascii=False)+"\n")
 ledger=BASE/"image-sources.csv"
 with ledger.open(newline="") as f:
  rd=csv.DictReader(f);headers=rd.fieldnames;rows=list(rd)
 for pid,name,role,x,content,sha,dims,url in ready:
  line={h:"" for h in headers}
  values={"file_name":name,"role":role,"creator":x["credit"] or x["photographer"],
  "license":{"cc0":"CC0","cc-by":"CC BY","cc-by-sa":"CC BY-SA"}[x["license_code"]],
  "source_page":x["source_page"],"direct_url":url,"study_use":"Public botanically labeled education",
  "public_reuse":"Valid individual photo CC license, photographer credited and changes noted",
  "observation_id":x["observation_id"],"photo_id":pid,"modifications":"JPEG resized/reencoded, EXIF removed"}
  for key,val in values.items():
   if key in line:line[key]=val
  rows.append(line)
 with ledger.open("w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=headers,lineterminator="\n");w.writeheader();w.writerows(rows)
 REPORT.write_text(json.dumps({
  "taxon":"Cynodon dactylon","previous":2,"new_installed":len(ready),"total":len(imgs),
  "actual_files":[x[1] for x in ready],
  "native_zone_decision":"introduced, not native in Texas per Kew",
  "existing_2_preserved":True,
  "pending":"verified underground rhizome/root node anatomy and arrow readback"
 },indent=2)+"\n")
 print("Completed six additional individual-source photos; gallery",len(imgs),"original photos preserved.")
if __name__=="__main__":main()
