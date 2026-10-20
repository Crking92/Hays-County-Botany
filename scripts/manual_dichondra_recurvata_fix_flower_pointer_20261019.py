#!/usr/bin/env python3
"""Post-install pixel-reviewed one-photo corolla arrow correction. Preserve source image and rights."""
from pathlib import Path
import json,runpy,csv
P=Path("content/taxa/Convolvulaceae/Dichondra/dichondra-recurvata")
C=P/"species.json"
j=json.loads(C.read_text())
assert j["id"]=="dichondra-recurvata" and len(j["images"])==7
target=next(x for x in j["images"] if x["file"].endswith("research-five-lobed-flower.jpg"))
if target.get("arrow_corrected_20261019"):
 print("Arrow already fixed");raise SystemExit(0)
m=runpy.run_path("scripts/manual_dichondra_recurvata_final_photo_install_20261019.py")
screen=json.loads(Path("workflow/photo-library/reviews/dichondra-recurvata-20261019/screen.json").read_text())
source=next(x for x in screen["candidates"] if str(x["photo_id"])=="32243425")
# We only alter the target of the 'flower' arrow.
def corrected_annotate(im,role):
 if role!="flower":return m["annotate"](im,role)
 # Use the original procedure with the physically observed upper cream corolla lobe at x=.55,y=.45.
 # Source code defines normalized arrow target; the run's in-memory function gets an edited constant in globals.
 m["annotate"].__globals__["MANUAL_FLOWER_POINT"]=(.55,.45)
 return m["annotate"](im,role)
# Change dynamically only inside module's annotation routine, via source reading and exec into isolated helper.
from PIL import ImageDraw, ImageFont
import math
def draw_verified(im):
 w,h=im.size
 d=ImageDraw.Draw(im);f=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",max(17,int(w*.023)))
 text="Pale corolla lobe"
 tx,ty=int(w*.55),int(h*.45)
 x,y=int(w*.05),int(h*.065)
 bb=d.textbbox((x,y),text,font=f)
 box=(x-6,y-6,bb[2]+6,bb[3]+6)
 d.rounded_rectangle(box,8,fill="#152e22",outline="#fffcef",width=2)
 d.text((x,y),text,font=f,fill="white")
 sx=min(max(tx,box[0]),box[2]);sy=box[3] if ty>box[3] else box[1]
 d.line(((sx,sy),(tx,ty)),fill="#182018",width=7)
 d.line(((sx,sy),(tx,ty)),fill="#ffe45b",width=3)
 a=math.atan2(ty-sy,tx-sx);sz=max(12,int(w*.02))
 d.polygon([(tx,ty),(tx-sz*math.cos(a-.42),ty-sz*math.sin(a-.42)),
 (tx-sz*math.cos(a+.42),ty-sz*math.sin(a+.42))],fill="#ffe45b")
 return im
# replace only function global reference used by 'retrieve', all other photo selectors unaffected.
m["retrieve"].__globals__["annotate"]=lambda im,role:draw_verified(im) if role=="flower" else im
new,sha,dims,url=m["retrieve"](source,"flower")
assert sha==target["original_sha256"],"Upstream original photo changed; do not silently redraw"
p=P/target["file"]
assert p.is_file()
p.write_bytes(new)
target["role"]="Look closer · tiny pale five-lobed cup flower with verified arrow ending on a cream corolla lobe, not on surrounding dry stems. Flower is visible; microscopic pedicel not resolved."
target["anatomy_arrows"]="Corrected yellow anatomical arrow on pale upper corolla lobe at (.55,.45) after full image inspection; no fruit stalk arrow claimed."
target["photo_review"]+=" Corrected original source recreation 2026-10-19 after visually observing arrow landed on dry twig; source SHA256 unchanged."
target["arrow_corrected_20261019"]=True
other=next(x for x in j["images"] if x["file"].endswith("research-flower-under-canopy.jpg"))
other["role"]="Look closer · very short downward-hooked green structure is visible near the flowering/fruiting region among leaf litter. Potential recurved pedicel, but the full continuous attachment and true calyx/fruit identity are not independently certain; do not use as standalone diagnostic proof."
other["photo_review"]+=" Full-size review flagged conspicuous strongly curved organ as possible diagnostic hooked pedicel, pending exact organ tracing."
j["curation_status"]["annotated_gallery_anatomy_review"]="2026-10-19 the two arrow-annotated images opened and corrected flower arrow to real cream corolla lobe. Curved organ candidate viewed but not certified as entire hooked pedicel."
j["curation_status"]["required_to_finish"]=[
 "Independent macro verifying complete stalk attachment and mature downward-hooking pedicel (existing photo candidate shows hooked organ but entire origin hidden)",
 "Caliper or millimeter-scale mature sepals vs capsule side view, matched with D. carolinensis",
 "Optional verified underside tawny sericeous hair macro",
 "Old original Chuck Sexton CC BY-NC photo remains restricted for public display when rights filter excludes NC"
]
j["learner_visual_status"]["note"]="Seven physical photos: six photo-specific CC BY exact-name iNat research-grade and original CC BY-NC. Cropped leaf and flower anatomy arrows manually inspected and corrected. One photo suggests sharply bent pedicel but complete organ attachment is not proven; 1 mm-scale mature fruit comparison pending."
j["photo_note"]+=" The arrow on flower reference 32243425 was corrected after full installed-file visual readback. Photograph 32243417 may show a hooked green pedicel but its attachment remains hidden; pedagogical caution preserved."
C.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n")
ledger=P/"image-sources.csv"
with ledger.open(newline="") as f:r=csv.DictReader(f);cols=r.fieldnames;rows=list(r)
for row in rows:
 if row["file_name"]=="research-five-lobed-flower.jpg":row["role"]=target["role"]
 if row["file_name"]=="research-flower-under-canopy.jpg":row["role"]=other["role"]
with ledger.open("w",newline="") as f:
 w=csv.DictWriter(f,fieldnames=cols,lineterminator="\n");w.writeheader();w.writerows(rows)
print(json.dumps({"corrected":"research-five-lobed-flower.jpg","original_SHA_same":True,"total_images":len(j["images"]),"other_species_untouched":True}))
