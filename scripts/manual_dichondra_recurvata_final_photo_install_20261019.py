#!/usr/bin/env python3
"""Install an independently pixel-screened selection of photo-CC-BY D. recurvata views.
Never claim a hooked mature fruiting pedicel without a visible complete stalk.
No native county audits and no edits to other species/automation queues.
"""
import hashlib, io, json, csv, math, requests
from pathlib import Path
from PIL import Image,ImageDraw,ImageOps,ImageFont

ROOT=Path(".")
P=ROOT/"content/taxa/Convolvulaceae/Dichondra/dichondra-recurvata"
CARD=P/"species.json"
SCREEN=ROOT/"workflow/photo-library/reviews/dichondra-recurvata-20261019/screen.json"
OUTPUT=ROOT/"reports/dichondra-recurvata-photo-install-20261019.json"
SID="dichondra-recurvata"
# Exact photo ids from independently examined 24-image contact sheet, restricted to research-grade observations.
PICKS=[
 ("503385966","research-mat-habit.jpg",
  "Recognize it · rooted low patch of Dichondra in thin grassy / disturbed soil with leafy runners; source research-grade observation.",""),
 ("39569588","research-leaf-notched.jpg",
  "Look closer · broad kidney-shaped green leaf with basal notch and entire margin, beside a hand for scale; full petiole attachment not established.","leaf"),
 ("32243425","research-five-lobed-flower.jpg",
  "Look closer · small pale five-lobed Dichondra flower nestled among leaves; flower is visible, microscopic pistil not resolved.","flower"),
 ("32243440","research-low-flower-and-petiole.jpg",
  "Look closer · tiny whitish flower and nearby leaf petiole/runner; flower stalk curvature not resolved.",""),
 ("32243422","research-hairy-calyx-and-bud.jpg",
  "Confirm clue · fuzzy small green floral / young fruit structures against fingertip; not proof of mature capsule size or fully recurved stalk.",""),
 ("32243417","research-flower-under-canopy.jpg",
  "Look closer · tiny flower borne below the kidney-shaped leaf canopy in leaf litter; stalk bend not independently visible.","")
]
FONT_NAME="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
session=requests.Session()
session.headers.update({"User-Agent":"HaysCountyBotanyEducationalSpeciesPhoto/1.0 (https://github.com/Crking92/Hays-County-Botany)"})
def annotate(im,role):
 if not role:return im
 w,h=im.size
 d=ImageDraw.Draw(im)
 font=ImageFont.truetype(FONT_NAME,max(17,int(w*.023)))
 if role=="leaf":
  point=(.51,.35);place=(.05,.08);label="Kidney-shaped leaf"
 elif role=="flower":
  point=(.68,.37);place=(.06,.08);label="Pale five-lobed flower"
 else:return im
 tx,ty=int(w*point[0]),int(h*point[1])
 x,y=int(w*place[0]),int(h*place[1])
 bb=d.textbbox((x,y),label,font=font)
 box=(x-6,y-6,bb[2]+6,bb[3]+6)
 d.rounded_rectangle(box,8,fill="#152e22",outline="#fffcef",width=2)
 d.text((x,y),label,font=font,fill="white")
 sx=min(max(tx,box[0]),box[2]);sy=box[3] if ty>box[3] else box[1]
 d.line(((sx,sy),(tx,ty)),fill="#182018",width=7)
 d.line(((sx,sy),(tx,ty)),fill="#ffe45b",width=3)
 a=math.atan2(ty-sy,tx-sx);sz=max(12,int(w*.02))
 d.polygon([(tx,ty),(tx-sz*math.cos(a-.42),ty-sz*math.sin(a-.42)),
 (tx-sz*math.cos(a+.42),ty-sz*math.sin(a+.42))],fill="#ffe45b")
 return im
def retrieve(row,role):
 pid=str(row["photo_id"])
 for kind in ("original","large"):
  url="https://inaturalist-open-data.s3.amazonaws.com/photos/"+pid+"/"+kind+".jpg"
  try:
   r=session.get(url,timeout=35);r.raise_for_status()
   if not 40000<len(r.content)<16000000:continue
   with Image.open(io.BytesIO(r.content)) as base:
    if base.format!="JPEG":continue
    rgb=ImageOps.exif_transpose(base).convert("RGB")
   if min(rgb.size)<420:continue
   sha=hashlib.sha256(r.content).hexdigest()
   rgb.thumbnail((1450,1450),Image.Resampling.LANCZOS)
   annotated=annotate(rgb,role)
   out=io.BytesIO()
   annotated.save(out,format="JPEG",quality=89,optimize=True,progressive=True)
   if len(out.getvalue())<25000:continue
   with Image.open(io.BytesIO(out.getvalue())) as check:check.verify()
   return out.getvalue(),sha,list(annotated.size),url
  except Exception as e:print("Candidate fetch",pid,kind,str(e)[:100])
 raise RuntimeError("Could not retrieve original or large for "+pid)
def main():
 man=json.loads((ROOT/"data/manifest.json").read_text())
 assert {z["id"]:z["path"] for z in man["species"]}.get(SID)==str(CARD)
 claims=json.loads((ROOT/"workflow/work-claims.json").read_text())
 for claim in claims.get("claims",[]):
  if SID in (claim.get("taxa") or []) and claim.get("status") in ("active","claimed","in_progress"):
   raise RuntimeError("Existing project claim for D. recurvata; do not collide")
 card=json.loads(CARD.read_text())
 assert card["id"]==SID and card["scientific_name"]=="Dichondra recurvata"
 if len(card["images"])==len(PICKS)+1 and all(any(x["file"].endswith(name) for x in card["images"]) for _,name,_,_ in PICKS):
  print("Already installed all selected photos; no-op");return
 assert len(card["images"])==1 and card["images"][0]["file"]=="images/inat-7297738.jpg", "Concurrent gallery changed; refuse overwrite"
 screen=json.loads(SCREEN.read_text())
 assert screen["taxon"]=="Dichondra recurvata"
 candidates={str(x["photo_id"]):x for x in screen["candidates"]}
 for pid,name,role,arrow in PICKS:
  x=candidates.get(pid)
  assert x and x["taxon_name"]=="Dichondra recurvata" and x["quality_grade"]=="research" and x["photo_license"]=="cc-by" and x["preview_sha256"]
  assert not (P/"images"/name).exists()
 all_files=[]
 for pid,name,role,arrow in PICKS:
  record=candidates[pid]
  img,sha,dims,url=retrieve(record,arrow)
  all_files.append((pid,name,role,arrow,record,img,sha,dims,url))
 for pid,name,role,arrow,src,img,sha,dims,url in all_files:
  dest=P/"images"/name
  dest.parent.mkdir(parents=True,exist_ok=True)
  dest.write_bytes(img)
  entry={
   "file":"images/"+name,"role":role,
   "creator":src["photo_attribution"] or src["observer"],
   "license":"CC BY",
   "license_url":"https://creativecommons.org/licenses/by/4.0/",
   "license_version_note":"iNaturalist photo-specific API license_code cc-by verified; version not individually rechecked on rendered iNaturalist photo page.",
   "source_platform":"iNaturalist exact-species research-grade observation",
   "source_page":src["photo_source"],"source_observation_page":src["observation_source"],
   "downloaded_from":url,"source_photo_id":pid,"image_dimensions":dims,"original_sha256":sha,
   "study_use":"Attributed educational use with CC BY permission",
   "public_reuse":"Creative Commons Attribution: author and changes notice; check photo-specific license source on reuse",
   "modifications":"Resized/reencoded JPEG, source EXIF removed; "+("one visible anatomical arrow added" if arrow else "no arrows"),
   "anatomy_arrows":"Provisional manually chosen visible "+("leaf" if arrow=="leaf" else "flower")+" arrow; check original committed JPEG for precise pointer" if arrow else "none",
   "photo_review":"Verified photo-level CC BY and research-grade taxon on individual iNaturalist observation; source image visible in contact sheet. Species identity remains iNaturalist research-grade, not independently verified from a complete voucher. DO NOT claim hooked pedicel."
  }
  card["images"].append(entry)
 card["curation_status"].update({
  "photo_metadata_count":len(card["images"]),"photo_files_present":len(card["images"]),
  "photo_source_checked":True,"visual_reviewed":False,
  "curated_new_photo_install":"2026-10-19",
  "finished_field_id_pass":"PASS_IN_PROGRESS",
  "required_to_finish":[
   "Check two newly rendered arrow images at full display size and fix any pointer that misses its anatomy",
   "Find independently validated macro of the mature sharply recurved fruiting pedicel, 5 green sepals and true two-lobed capsule with 1 mm scale",
   "Optional: find underside sericeous-hair macro in verified exact-species source",
   "Original Chuck Sexton photo retains CC BY-NC; should not be promoted publicly if a rights filter blocks NC"
  ]})
 card["learner_visual_status"].update({
  "image_count":len(card["images"]),"mode":"complete_text_seven_gallery_views_pending_hooked_pedicel_macro",
  "note":"Six real CC BY research-grade reference photos selected after contact sheet review plus preserved original CC BY-NC. Flower, leaf and patch documented; curled mature pedicel plus measured calyx/fruit not visualized; do not mark complete."})
 card["photo_note"]="Curated six exact-species iNaturalist research-grade photos whose individual photo license_code is cc-by, 2026-10-19. Existing Chuck Sexton image unchanged. This is a field-photo lesson, not independent species-voucher certification. Critical true hooked pedicel and mature calyx/fruit measurement photograph still missing."
 CARD.write_text(json.dumps(card,indent=2,ensure_ascii=False)+"\n")
 csvfile=P/"image-sources.csv"
 with csvfile.open(newline="") as f:
  reader=csv.DictReader(f);rows=list(reader);headers=reader.fieldnames
 for pid,name,role,arrow,src,img,sha,dims,url in all_files:
  item={h:"" for h in headers}
  values={"file_name":name,"role":role,"creator":src["photo_attribution"] or src["observer"],"license":"CC BY",
   "source_page":src["photo_source"],"direct_url":url,"study_use":"Attributed public education",
   "public_reuse":"CC BY, credit author and identify modifications",
   "observation_id":src["observation_id"],"photo_id":pid}
  for key,value in values.items():
   if key in item:item[key]=value
  rows.append(item)
 with csvfile.open("w",newline="") as f:
  writer=csv.DictWriter(f,fieldnames=headers,lineterminator="\n")
  writer.writeheader();writer.writerows(rows)
 report={"species":SID,"new_photos":len(all_files),"gallery_count":len(card["images"]),
  "new_media":[{"photo_id":x[0],"file":x[1],"rights":"CC BY","original_sha256":x[6]} for x in all_files],
  "original_photo_preserved":True,"county_nativeness_unchanged":True,
  "pending":"full pedicel and calyx/fruit macro, plus arrow review"}
 OUTPUT.write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps(report,indent=2))
if __name__=="__main__":main()
