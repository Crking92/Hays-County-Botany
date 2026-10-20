#!/usr/bin/env python3
"""Annotate 3 exact-sha grass macro photos with conservative anatomical targets.
Only botanical structures visible at full original pixels may receive arrows.
Avoid inventing an underground rhizome or measured ligule from a turf photo.
"""
import json,io,math,csv,hashlib
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import requests
BASE=Path("content/taxa/Poaceae/Cynodon/cynodon-dactylon")
FILE=BASE/"species.json"
SCREEN=Path("workflow/photo-library/reviews/cynodon-dactylon-20261020/screen.json")
j=json.loads(FILE.read_text());assert j["id"]=="cynodon-dactylon" and len(j["images"])==8
c={str(x["photo_id"]):x for x in json.loads(SCREEN.read_text())["candidates"]}
SETS=[
 {"id":"410585092","file":"jimmex-410585092-collar-hair-fringe.jpg",
  "arrows":[("Collar hair tuft",(.74,.28),(.03,.06))],
  "role":"Look closer: genuine white tuft of hairs at leaf collar/sheath junction; the microscopic INNER short ligule (approx. 0.5 mm) is NOT separately measured or certified."},
 {"id":"410585069","file":"jimmex-410585069-spikelet-macro.jpg",
  "arrows":[("Spikelets",(.55,.56),(.30,.06)),("Exserted anther",(.692,.667),(.58,.86))],
  "role":"Confirm clue: small one-sided spikelets on slender finger and dangling brownish anther exposed from an individual grass flower. Pink feathery stigmas also visible but not separately labeled."},
 {"id":"410585068","file":"jimmex-410585068-finger-seedhead.jpg",
  "arrows":[("Fingerlike ray",(.719,.36),(.62,.09)),("Shared tip",(.48,.867),(.06,.72))],
  "role":"Recognize it: terminal DIGITATE seedhead; several slender unilateral spikelet-bearing fingers and the nearly common point from which they radiate."}
]
S=requests.Session();S.headers.update({"User-Agent":"HaysCountyBotanyMacroLabels/1.0 (github.com/Crking92/Hays-County-Botany)"})
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def draw_photo(im,arrows):
 w,h=im.size;D=ImageDraw.Draw(im);ft=ImageFont.truetype(FONT,max(17,round(min(w,h)*.041)))
 for title,point,place in arrows:
  tx,ty=round(w*point[0]),round(h*point[1])
  lx,ly=round(w*place[0]),round(h*place[1])
  bb=D.textbbox((lx,ly),title,font=ft)
  rect=(lx-6,ly-5,bb[2]+6,bb[3]+5)
  D.rounded_rectangle(rect,5,fill="#152e29",outline="#fffdf0",width=2)
  D.text((lx,ly),title,fill="white",font=ft)
  sx=max(rect[0],min(tx,rect[2]));sy=rect[3] if ty>rect[3] else rect[1]
  D.line(((sx,sy),(tx,ty)),fill="#17231b",width=6)
  D.line(((sx,sy),(tx,ty)),fill="#ffdb46",width=3)
  a=math.atan2(ty-sy,tx-sx);L=max(11,round(min(w,h)*.029))
  D.polygon([(tx,ty),(tx-L*math.cos(a-.46),ty-L*math.sin(a-.46)),(tx-L*math.cos(a+.46),ty-L*math.sin(a+.46))],fill="#ffdb46")
 return im
def fetch(src,expected):
 pid=str(src["photo_id"]);url=src["photo_url"]
 choices=[url.replace("/large.","/original."),url,"https://inaturalist-open-data.s3.amazonaws.com/photos/"+pid+"/original.jpg"]
 for u in dict.fromkeys(choices):
  try:
   r=S.get(u,timeout=38);r.raise_for_status()
   if hashlib.sha256(r.content).hexdigest()!=expected:continue
   with Image.open(io.BytesIO(r.content)) as origin:
    origin.load();im=ImageOps.exif_transpose(origin).convert("RGB")
   im.thumbnail((1450,1450),Image.Resampling.LANCZOS)
   return im
  except Exception as e:print("retry",pid,str(e)[:110])
 raise RuntimeError("Identical SHA original unavailable for "+pid)
for t in SETS:
 x=next(z for z in j["images"] if z["file"]=="images/"+t["file"])
 if x.get("manual_arrow_review")=="2026-10-20-source-original-labeled":continue
 assert x["license"]=="CC0" and str(x["source_photo_id"])==t["id"]
 src=c[t["id"]]
 im=draw_photo(fetch(src,x["original_image_sha256"]),t["arrows"])
 out=BASE/"images"/t["file"];assert out.exists();im.save(out,"JPEG",quality=91,optimize=True,progressive=True)
 with Image.open(out) as check:check.verify()
 x["role"]=t["role"]
 x["modifications"]="From SHA-verified original, resized JPEG, EXIF removed; original-safe anatomy arrow adaptation added."
 x["anatomy_arrows"]=[{"label":label,"target_fraction":list(point)} for label,point,_ in t["arrows"]]
 x["manual_arrow_review"]="2026-10-20-source-original-labeled"
 x["photo_review"]+=" Exact source original SHA-256 matched. Arrowpoints manually selected against prior inspected full-size photo, awaiting committed derivative QA."
j["curation_status"]["photo_annotation_install"]="2026-10-20 three exact-original CC0 anatomy overlays prepared. Must re-open actual committed JPEGs for arrow-tip certification."
j["curation_status"]["required_to_finish"]=[
 "Open all three committed photo overlays at rendered full size and verify arrows terminate on visible correct grass anatomy",
 "Underground scaly rhizome with nodes AND actually rooted living stolon node still missing from this learner gallery",
 "Older Zinogre CC BY-SA and Dan Johnson GBIF individual photo license subversions not independently verified; source credit unchanged",
 "Public photo rights and site deployment verification pending"
]
j["learner_visual_status"]["note"]="8 real verified gallery photos, including 3 CC0 grass anatomy derivatives with labeled collar hairs, spikelets/anthers and digitate head; arrows must pass installed-pixel readback. Rooted rhizome macro missing.";
FILE.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n")
ledger=BASE/"image-sources.csv"
with ledger.open(newline="") as f:
 reader=csv.DictReader(f);header=reader.fieldnames;rows=list(reader)
for row in rows:
 for t in SETS:
  if row.get("file_name")==t["file"]:
   row["role"]=t["role"]
   if "modifications" in header:row["modifications"]="Resized CC0 original; yellow anatomy arrows verified against original SHA, final readback pending"
with ledger.open("w",newline="") as f:
 writer=csv.DictWriter(f,fieldnames=header,lineterminator="\n");writer.writeheader();writer.writerows(rows)
print(json.dumps({"count":len(j["images"]),"annotated":[x["file"] for x in j["images"] if x.get("manual_arrow_review")],"nonnative":j["project_inclusion"]["target_zone_status"]}))
