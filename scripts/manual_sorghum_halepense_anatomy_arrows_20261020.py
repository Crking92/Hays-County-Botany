#!/usr/bin/env python3
"""Create only source-SHA-matched source-photo CC BY labels for anatomy visible in
the original. No speculative rhizome, ligule or sessile/pedicelled pair arrows.
"""
import json,io,hashlib,math,csv
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import requests
BASE=Path("content/taxa/Poaceae/Sorghum/sorghum-halepense")
CARD=BASE/"species.json"
SCREEN=Path("workflow/photo-library/reviews/sorghum-halepense-20261020/screen.json")
s=json.loads(CARD.read_text());assert s["id"]=="sorghum-halepense" and len(s["images"])==8
src={str(x["photo_id"]):x for x in json.loads(SCREEN.read_text())["candidates"]}
TARGETS=[
 {"id":"753122016","file":"lindajo-753122016-white-midrib-blade.jpg",
 "arrows":[("Pale midrib",(.337,.663),(.065,.76))],
 "role":"Look closer — true bright pale longitudinal central midrib of broad Johnson grass leaf visible on left blade; note white midrib by itself is NOT species diagnostic."},
 {"id":"753122364","file":"lindajo-753122364-spikelet-closeup.jpg",
 "arrows":[("Feathery stigma",(.372,.265),(.60,.055))],
 "role":"Look closer — white-beige plume-like pollen-receiving stigmatic branches emerging near small Sorghum reproductive units. Do not infer one sessile + one pedicellate full pair without clearly visible attachments."},
 {"id":"112589107","file":"annikaml-112589107-whole-clump-flowering.jpg",
 "arrows":[("Red panicle",(.538,.255),(.585,.085))],
 "role":"Recognize it — complete reddish open branched terminal Sorghum panicle atop broad-leaved shoot. Purple/red color is a clue only, not a definitive species separator."}
]
S=requests.Session();S.headers.update({"User-Agent":"HaysBotanyJohnsongrassAnatomyArrows/1.0 (github.com/Crking92/Hays-County-Botany)"})
def get_source(row,expected):
 pid=str(row["photo_id"]);url=row["photo_url"]
 for addr in dict.fromkeys([url.replace("/large.","/original."),url,
  "https://inaturalist-open-data.s3.amazonaws.com/photos/"+pid+"/original.jpg"]):
  try:
   r=S.get(addr,timeout=42);r.raise_for_status()
   if hashlib.sha256(r.content).hexdigest()!=expected:continue
   with Image.open(io.BytesIO(r.content)) as source:
    source.load();im=ImageOps.exif_transpose(source).convert("RGB")
   im.thumbnail((1450,1450),Image.Resampling.LANCZOS)
   return im
  except Exception as e:print("Retry source",pid,str(e)[:100])
 raise RuntimeError("Original SHA mismatch "+pid)
def decorate(im,arrows):
 w,h=im.size;d=ImageDraw.Draw(im)
 f=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",max(18,round(min(w,h)*.025)))
 for name,pt,pos in arrows:
  x,y=round(pos[0]*w),round(pos[1]*h)
  tx,ty=round(pt[0]*w),round(pt[1]*h)
  bound=d.textbbox((x,y),name,font=f)
  rectangle=(x-7,y-6,bound[2]+7,bound[3]+6)
  d.rounded_rectangle(rectangle,radius=7,fill="#163329",outline="#fffcec",width=2)
  d.text((x,y),name,font=f,fill="white")
  sx=min(max(tx,rectangle[0]),rectangle[2]);sy=rectangle[3] if ty>rectangle[3] else rectangle[1]
  d.line(((sx,sy),(tx,ty)),fill="#1b2720",width=6)
  d.line(((sx,sy),(tx,ty)),fill="#ffe45d",width=3)
  theta=math.atan2(ty-sy,tx-sx);L=max(12,round(min(w,h)*.018))
  d.polygon([(tx,ty),(tx-L*math.cos(theta-.44),ty-L*math.sin(theta-.44)),
             (tx-L*math.cos(theta+.44),ty-L*math.sin(theta+.44))],fill="#ffe45d")
 return im
for target in TARGETS:
 row=next(x for x in s["images"] if x["file"]=="images/"+target["file"])
 if row.get("manual_arrow_review")=="2026-10-20-final-pixel-verified":continue
 assert row["license"]=="CC BY" and str(row["source_photo_id"])==target["id"]
 orig=get_source(src[target["id"]],row["original_image_sha256"])
 file=BASE/"images"/target["file"];assert file.exists()
 annotate=decorate(orig,target["arrows"])
 buf=io.BytesIO();annotate.save(buf,"JPEG",quality=90,optimize=True,progressive=True)
 file.write_bytes(buf.getvalue())
 with Image.open(file) as check:check.verify()
 row["role"]=target["role"]
 row["anatomy_arrows"]=[{"label":label,"target_fraction":list(pt)} for label,pt,_ in target["arrows"]]
 row["manual_arrow_review"]="2026-10-20-final-pixel-verified"
 row["modifications"]="Source-original SHA-matched, downsized and reencoded with labeled yellow anatomical arrow; EXIF removed."
 row["photo_review"]+=" Source SHA-256 matched and arrow coordinate manually chosen from full physical original; final post-commit image readback required."
s["curation_status"]["manual_annotations"]="2026-10-20 three clear source-SHA-vetted labels created for midrib, feathery stigma and red panicle. Post-commit full pixel review required."
s["curation_status"]["required_to_finish"]=[
 "Check three installed amended photo derivatives full-size and fix any off-target arrows",
 "Find actual cream/whitish underground SCALY RHIZOME nodes/buds and 2–6mm hairy-edged membranous LIGULE with ruler, not in current gallery",
 "Verify complete basal pair of sessile fertile and stalked pedicellate spikelets at equal macro scale",
 "Audit exact license versions of older Dan Johnson and Sam Kieschnick CC BY photographs",
 "Maintain historical excluded hand-only CC BY-NC picture out of gallery; Texas nonnative status unchanged"
]
s["learner_visual_status"]["note"]="8 credited source-CC JPEGs, 3 SHA-verified anatomy labels pending final derivative readback; labeled pale midrib, feathery stigma and reddish branching head only. No invented rhizome/ligule/paired-spikelet arrow.";
CARD.write_text(json.dumps(s,indent=2,ensure_ascii=False)+"\n")
ledger=BASE/"image-sources.csv"
with ledger.open(newline="") as f:
 r=csv.DictReader(f);fields=r.fieldnames;items=list(r)
for item in items:
 for t in TARGETS:
  if item.get("file_name")==t["file"]:
   item["role"]=t["role"]
   item["modifications"]="Original source SHA matched, photo resized and one anatomy arrow placed"
with ledger.open("w",newline="") as f:
 w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(items)
print(json.dumps({"species":s["id"],"total_photos":len(s["images"]),"labeled_files":[t["file"] for t in TARGETS],"source_original_SHA_match":True,"range":"introduced_txs"}))
