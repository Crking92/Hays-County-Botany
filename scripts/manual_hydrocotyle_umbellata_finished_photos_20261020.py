#!/usr/bin/env python3
"""One-species approved-license Hydrocotyle umbellata photo installation.
Selections screened from real Texas iNaturalist research-grade images in prior
contact sheet. Retains original gallery; no county nativeness status updates.
"""
from pathlib import Path
import csv,io,json,hashlib,time,math
import requests
from PIL import Image,ImageOps,ImageDraw,ImageFont
BASE=Path("content/taxa/Araliaceae/Hydrocotyle/hydrocotyle-umbellata")
CARD=BASE/"species.json"
INDEX=Path("workflow/photo-library/reviews/hydrocotyle-umbellata-20261020/candidate-screen.json")
AUDIT=Path("workflow/photo-library/reviews/hydrocotyle-umbellata-20261020/archived-sam-gbif-license.json")
REPORT=Path("reports/hydrocotyle-umbellata-finished-photo-20261020.json")
PICKS=[
 ("653715689","annikaml-653715689-wet-mat.jpg",
 "Recognize it · peltate rounded leaves rising individually from low wet mud; petioles and wet-ground field context, NOT root nodes proven.",[]),
 ("633285519","sam-633285519-leaf-and-head-arrows.jpg",
 "Look closer · scalloped peltate leaf plus separate peduncle with dense flowering cluster; yellow arrows indicate visible scalloped leaf margin and white flower cluster only.",
 [("Scalloped leaf margin",(.70,.14),(.05,.05)),("Flower cluster",(.26,.72),(.54,.86))]),
 ("511737621","annikaml-511737621-young-fruit-umbel.jpg",
 "Confirm clue · stalked cluster of developing green reproductive bodies beside thumb for scale; these are not mature measured mericarps.",[]),
 ("678611366","saltyhiker-678611366-flower-head.jpg",
 "Look closer · crowd of small separate white five-petaled flowers carried on fine stalklets; do not infer entire axis/other tier count from this tight view.",[])
]
USER_AGENT="HaysCountyBotanyPhotoReview/1.0 (github.com/Crking92/Hays-County-Botany)"
session=requests.Session();session.headers.update({"User-Agent":USER_AGENT})
def font(sz):
 for name in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf","/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"):
  try:return ImageFont.truetype(name,sz)
  except OSError:pass
 return ImageFont.load_default()
def annotate(im,points):
 if not points:return im
 w,h=im.size
 d=ImageDraw.Draw(im)
 f=font(max(17,round(w*.022)))
 for name,target,label in points:
  tx,ty=round(w*target[0]),round(h*target[1])
  x,y=round(w*label[0]),round(h*label[1])
  bb=d.textbbox((x,y),name,font=f)
  box=(x-7,y-7,bb[2]+7,bb[3]+7)
  d.rounded_rectangle(box,radius=7,fill="#14352e",outline="#fffeed",width=2)
  d.text((x,y),name,font=f,fill="#ffffff")
  origin=(min(box[2],max(box[0],tx)),box[3] if ty>box[3] else box[1])
  d.line((origin,(tx,ty)),fill="#121a17",width=7)
  d.line((origin,(tx,ty)),fill="#ffdd44",width=3)
  a=math.atan2(ty-origin[1],tx-origin[0]);L=max(12,round(w*.016))
  d.polygon([(tx,ty),(tx-L*math.cos(a-.42),ty-L*math.sin(a-.42)),(tx-L*math.cos(a+.42),ty-L*math.sin(a+.42))],fill="#ffdd44")
 return im
def obtain(x,points):
 photo_id=str(x["photo_id"]);url=x["url"]
 attempts=[url.replace("/large.","/original."),url,
           "https://inaturalist-open-data.s3.amazonaws.com/photos/"+photo_id+"/original.jpg",
           "https://inaturalist-open-data.s3.amazonaws.com/photos/"+photo_id+"/large.jpg"]
 for url in dict.fromkeys(attempts):
  try:
   r=session.get(url,timeout=40)
   r.raise_for_status()
   if not 35000<len(r.content)<18000000:continue
   with Image.open(io.BytesIO(r.content)) as src:
    src.load();raw_dims=src.size
    img=ImageOps.exif_transpose(src).convert("RGB")
   if min(img.size)<450:continue
   sha=hashlib.sha256(r.content).hexdigest()
   img.thumbnail((1400,1400),Image.Resampling.LANCZOS)
   annotated=annotate(img,points)
   buf=io.BytesIO();annotated.save(buf,"JPEG",quality=89,optimize=True,progressive=True)
   payload=buf.getvalue()
   with Image.open(io.BytesIO(payload)) as test:test.verify()
   return payload,sha,list(img.size),url
  except Exception as e:print("DOWNLOAD ATTEMPT",photo_id,url,str(e)[:200])
 raise RuntimeError("No intact full image fetched for "+photo_id)
def main():
 man=json.loads(Path("data/manifest.json").read_text())
 assert {x["id"]:x["path"] for x in man["species"]}.get("hydrocotyle-umbellata")==str(CARD)
 claims=json.loads(Path("workflow/work-claims.json").read_text())
 for c in claims.get("claims",[]):
  if "hydrocotyle-umbellata" in (c.get("taxa") or []) and c.get("status") in ("active","claimed","in_progress"):
   raise RuntimeError("Active competing claim")
 card=json.loads(CARD.read_text())
 assert card["id"]=="hydrocotyle-umbellata" and card["scientific_name"]=="Hydrocotyle umbellata"
 images=card["images"]
 if all(any(i["file"]=="images/"+name for i in images) for _,name,_,_ in PICKS):
  print("Already installed, no-op");return
 assert len(images)==2,"Refuse if concurrent gallery upgrade"
 assert card["curation_status"].get("finished_field_id_pass")=="PASS_IN_PROGRESS"
 source=json.loads(INDEX.read_text());audit=json.loads(AUDIT.read_text())
 rights=[m for m in audit["media"] if m["identifier"]=="https://inaturalist-open-data.s3.amazonaws.com/photos/638686449/original.jpg"]
 assert len(rights)==1 and rights[0]["license"].rstrip("/").endswith("/by/4.0")
 assert audit["rights_holder"]=="Sam Kieschnick"
 old=next(x for x in images if x.get("media_source_url","").endswith("/photos/638686449/original.jpg"))
 assert old["creator"]=="Sam Kieschnick"
 old.update({"license":"CC BY 4.0","license_url":"https://creativecommons.org/licenses/by/4.0/",
 "license_version_note":"Verified exact image GBIF 6234372459 individual media license 2026-10-20; rightsHolder Sam Kieschnick.",
 "public_reuse":"CC BY 4.0: attribution and modification notice required, public web use allowed"})
 candidates={str(x["photo_id"]):x for x in source["candidates"]}
 prepared=[]
 for pid,name,role,arrows in PICKS:
  x=candidates.get(pid)
  assert x and x["exact_taxon"]=="Hydrocotyle umbellata" and x["quality_grade"]=="research"
  assert x["photo_license_code"] in ("cc-by","cc-by-sa","cc0")
  assert x.get("preview_sha256")
  assert not (BASE/"images"/name).exists()
  prepared.append((pid,name,role,arrows,x,*obtain(x,arrows)))
 for pid,name,role,arrows,x,payload,sha,dims,url in prepared:
  out=BASE/"images"/name;out.parent.mkdir(parents=True,exist_ok=True)
  out.write_bytes(payload)
  lic={"cc-by":"CC BY","cc-by-sa":"CC BY-SA","cc0":"CC0"}[x["photo_license_code"]]
  images.append({
   "file":"images/"+name,"role":role,"creator":x["photo_attribution"] or x["photographer_account"],
   "license":lic,
   "license_version_note":"Individually licensed photo license_code="+x["photo_license_code"]+" from exact species iNaturalist observation. Do not assert license version until media page checked.",
   "source_platform":"iNaturalist exact-species research-grade observation",
   "source_page":x["source_page"],"source_observation_page":x["observation_source"],
   "source_photo_id":pid,"image_dimensions":dims,"downloaded_from":url,"original_image_sha256":sha,
   "study_use":"Credited educational reuse under photo-specific "+lic,
   "public_reuse":"Licensable for public site with original author attribution and applicable CC license conditions",
   "modifications":"Resized/reencoded, EXIF removed; "+("manual anatomical yellow arrows" if arrows else "no anatomical arrows"),
   "anatomy_arrows":"Provisional visible flower/leaf labels from inspected source preview; check installed full-size arrow locations after run." if arrows else "none",
   "photo_review":"Source photo inspected in real 32-photo Texas contact sheet. Source species determination research-grade, anatomical fruit maturity and backside petiole insertion not independently proven."
  })
 card["images"]=images
 card["curation_status"].update({
  "photo_metadata_count":len(images),"photo_files_present":len(images),
  "photo_source_checked":True,"visual_reviewed":False,
  "finished_field_id_pass":"PASS_IN_PROGRESS",
  "archived_sam_image_license_verified":"2026-10-20, GBIF occurrence 6234372459 individual media CC BY 4.0",
  "photo_install_checked":"2026-10-20",
  "required_to_finish":[
   "Manual pixel readback of annotated leaf / flower positions before final publish",
   "True underside of leaf with petiole insertion inside blade edge still missing",
   "Matched whole inflorescence axes H. umbellata vs H. verticillata still needed for tricky specimens",
   "Mature flattened two-part mericarp with mm reference and exposed creeping runner root nodes still not clearly photographed",
   "Exact license version of archived Michelle W CC BY photo still requires source-specific check"
  ]
 })
 card["learner_visual_status"].update({"image_count":len(images),
  "mode":"complete_text_six_photo_gallery_partial_anatomy_verified",
  "note":"Six exact-name credited physical photos (2 prior + 4 new), peltate leaf top and many-flowered clusters visible; no underside attachment or mature fruit macro proven."})
 card["photo_note"]="2026-10-20: Two existing original photos inspected; 4 distinct iNaturalist research-grade Texas photo-specific CC-licensed candidates installed after actual pixel contact-sheet screening. Existing Sam Kieschnick original license CC BY 4.0 verified in GBIF media record. Remaining underside-petiole and mature schizocarp structures are explicitly unverified."
 CARD.write_text(json.dumps(card,indent=2,ensure_ascii=False)+"\n")
 ledger=BASE/"image-sources.csv"
 with ledger.open(newline="") as f:
  read=csv.DictReader(f);headers=read.fieldnames;rows=list(read)
 for row in rows:
  if row["file_name"]=="library-review047-4d65eaa1eccd134.jpg":
   row["license"]="CC BY 4.0"
   row["license_url"]="https://creativecommons.org/licenses/by/4.0/"
   row["public_reuse"]="Verified photo-specific GBIF media CC BY 4.0, with attribution/modifications notice"
 for pid,name,role,arrows,x,payload,sha,dims,url in prepared:
  row={key:"" for key in headers}
  entry={"file_name":name,"role":role,"creator":x["photo_attribution"] or x["photographer_account"],
         "license":{"cc-by":"CC BY","cc-by-sa":"CC BY-SA","cc0":"CC0"}[x["photo_license_code"]],
         "source_page":x["source_page"],"direct_url":url,"study_use":"Public attributed botanical education",
         "public_reuse":"Individual photo CC license with credit and modification notice",
         "observation_id":x["observation_id"],"photo_id":pid,
         "modifications":"Resized JPEG, EXIF removed, labeled arrows" if arrows else "Resized JPEG, EXIF removed"}
  for key,val in entry.items():
   if key in row:row[key]=val
  rows.append(row)
 with ledger.open("w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=headers,lineterminator="\n");w.writeheader();w.writerows(rows)
 REPORT.write_text(json.dumps({"species":"hydrocotyle-umbellata",
  "prior_photo_count":2,"new_photo_count":len(prepared),"total_photo_count":len(images),
  "verified_archived_sam_license":"CC BY 4.0 via GBIF media",
  "original_images_preserved":True,"new_files":[name for pid,name,*_ in prepared],
  "scientific_nativity_decisions_unchanged":True,
  "remaining":"Underside peltate stalk and mature schizocarp close-up; full axis pair against H. verticillata",},indent=2)+"\n")
 print("FINISHED photo install:",len(images),"physical photos; originals retained")
if __name__=="__main__":main()
