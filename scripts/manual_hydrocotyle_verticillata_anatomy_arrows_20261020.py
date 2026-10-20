#!/usr/bin/env python3
"""Rebuild one published-size, CC BY Hydrocotyle photo from its exact SHA-matched
original and annotate two visually verified whorl tiers. Does not label species
identity or modern triradiata taxonomy as resolved."""
import io,csv,json,math,hashlib,requests
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
P=Path("content/taxa/Araliaceae/Hydrocotyle/hydrocotyle-verticillata")
C=P/"species.json"
j=json.loads(C.read_text())
assert j["id"]=="hydrocotyle-verticillata" and len(j["images"])==6
fn="images/sam-694125616-full-whorled-axis.jpg"
r=next(v for v in j["images"] if v["file"]==fn)
if r.get("manual_arrow_review")=="2026-10-20-two-verified-whorls":
 print("already corrected");raise SystemExit(0)
pid="694125616"
screen=json.loads(Path("workflow/photo-library/reviews/hydrocotyle-verticillata-20261020/candidate-screen.json").read_text())
source=next(x for x in screen["candidates"] if str(x["photo_id"])==pid)
s=requests.Session();s.headers.update({"User-Agent":"HaysCountyBotanyAnatomyReview/1.0 (github.com/Crking92/Hays-County-Botany)"})
urls=[source["photo_url"].replace("/large.","/original."),source["photo_url"],
"https://inaturalist-open-data.s3.amazonaws.com/photos/"+pid+"/original.jpg"]
image=None
for url in dict.fromkeys(urls):
 try:
  resp=s.get(url,timeout=35);resp.raise_for_status()
  sha=hashlib.sha256(resp.content).hexdigest()
  if sha!=r["original_image_sha256"]:
   print("source not original SHA, skip",url);continue
  with Image.open(io.BytesIO(resp.content)) as im:
   im.load();image=ImageOps.exif_transpose(im).convert("RGB")
  break
 except Exception as e:print("attempt",url,str(e)[:120])
assert image is not None,"Exact SHA-matched original unavailable; no arrows allowed"
image.thumbnail((1450,1450),Image.Resampling.LANCZOS)
w,h=image.size
draw=ImageDraw.Draw(image)
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",max(17,round(w*.024)))
points=[
 ("Upper whorl",(.748,.445),(.51,.23)),
 ("Lower whorl",(.718,.640),(.45,.80))
]
for label,target,pos in points:
 tx,ty=round(target[0]*w),round(target[1]*h)
 x,y=round(pos[0]*w),round(pos[1]*h)
 bbox=draw.textbbox((x,y),label,font=font)
 box=(x-7,y-7,bbox[2]+7,bbox[3]+7)
 draw.rounded_rectangle(box,radius=7,fill="#13372b",outline="#ffffe9",width=2)
 draw.text((x,y),label,font=font,fill="#ffffff")
 ox=min(max(tx,box[0]),box[2]); oy=box[3] if ty>box[3] else box[1]
 draw.line(((ox,oy),(tx,ty)),fill="#172019",width=7)
 draw.line(((ox,oy),(tx,ty)),fill="#ffdb47",width=3)
 a=math.atan2(ty-oy,tx-ox);L=max(14,round(w*.018))
 draw.polygon([(tx,ty),(tx-L*math.cos(a-.42),ty-L*math.sin(a-.42)),
 (tx-L*math.cos(a+.42),ty-L*math.sin(a+.42))],fill="#ffdb47")
data=io.BytesIO();image.save(data,format="JPEG",quality=89,optimize=True,progressive=True)
target=P/fn;assert target.exists() and target.stat().st_size>25000
target.write_bytes(data.getvalue())
with Image.open(target) as check:check.verify()
r["role"]="Look closer · entire slender fertile axis with two visible separate flower/young-fruit WHORLS. Two yellow arrowheads indicate upper and lower tiers; green peltate-like leaf top and palmate veins also visible. This is source-identified H. verticillata; accepted species vs H. bonariensis/var. triradiata requires a taxonomic voucher.";
r["anatomy_arrows"]="Two separately visible tiers annotated from a SHA-matched upstream photograph: upper whorl at normalized (.748,.445); lower whorl at (.718,.640). No claims about unseen blade underside, ripe mericarps or accepted-name voucher proof.";
r["manual_arrow_review"]="2026-10-20-two-verified-whorls";
r["photo_review"]+=" SHA matched original, two whorl tiers manually selected after full-size image readback. Source taxon attribution still provisional due modern taxonomy.";
r["modifications"]="JPG resized/reencoded, EXIF removed; added 2 named whorl arrows as attributed adaptation.";
j["curation_status"]["anatomy_whorl_photo_annotated"]="2026-10-20: two visible flower/young-fruit whorl tiers labeled on 694125616 original, SHA-match verified; final published-size reinspection still required";
j["curation_status"]["required_to_finish"]=[
 "Open installed two-whorl annotated JPEG at its full size and validate tip coordinates before public publication",
 "Scientific voucher verification of accepted H. verticillata versus Kew-treated H. bonariensis / historical var. triradiata",
 "Find properly licensed leaf underside showing peltate insertion and mature ribbed schizocarp mericarps with millimeter scale",
 "Keep BONAP target-zone metrics excluded and document outstanding taxonomic uncertainty"
]
j["learner_visual_status"]["note"]="Six real credited JPEGs: one historical Wikicommons source plus five modern research-grade Texas photos. Whorled-axis photo now with two visible anatomical tier labels; accepted species vs bonariensis remains TAXON HOLD.";
j["photo_note"]+=" Anatomy: 2 arrows on image 694125616 label upper and lower visible tiers (original SHA verified), not an independently voucher-verified H. verticillata diagnostic species determination.";
C.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n")
ledger=P/"image-sources.csv"
with ledger.open(newline="") as f:
 reader=csv.DictReader(f);headers=reader.fieldnames;rows=list(reader)
for row in rows:
 if row.get("file_name")==Path(fn).name:row["role"]=r["role"]
with ledger.open("w",newline="") as f:
 writer=csv.DictWriter(f,fieldnames=headers,lineterminator="\n");writer.writeheader();writer.writerows(rows)
print(json.dumps({"changed":fn,"original_sha_verified":True,"arrow_count":2,"taxonomic_hold_kept":True},indent=2))
