#!/usr/bin/env python3
"""Generate a contact sheet and pixel QA for existing Chloris images. Never claim anatomy from metadata."""
import json,hashlib,pathlib
from PIL import Image,ImageOps,ImageDraw,ImageFont
root=pathlib.Path("content/taxa/Poaceae/Chloris/chloris-andropogonoides")
card=json.loads((root/"species.json").read_text())
assert card["id"]=="chloris-andropogonoides"
photos=card["images"]
width=1200; tile_w=600; tile_h=540
sheet=Image.new("RGB",(width,((len(photos)+1)//2)*tile_h),"white")
draw=ImageDraw.Draw(sheet)
rows=[]
for i,item in enumerate(photos):
 path=root/item["file"]
 rec={"file":item["file"],"license":item.get("license"),"source_page":item.get("source_page"),"present":path.is_file()}
 if not path.is_file():
  rows.append(rec);continue
 payload=path.read_bytes()
 try:
  with Image.open(path) as original:
   original.verify()
  with Image.open(path) as original:
   original=ImageOps.exif_transpose(original).convert("RGB")
   rec["dimensions"]=list(original.size)
   rec["bytes"]=len(payload)
   rec["sha256"]=hashlib.sha256(payload).hexdigest()
   tile=original.copy()
   tile.thumbnail((tile_w-32,tile_h-115))
  x=(i%2)*tile_w; y=(i//2)*tile_h
  sheet.paste(tile,(x+(tile_w-tile.width)//2,y+8))
  draw.text((x+12,y+tile_h-103),item["file"],fill="black")
  draw.text((x+12,y+tile_h-79),"Rights: "+str(item.get("license","unknown")),fill="black")
  draw.text((x+12,y+tile_h-55),"Original: "+str(rec["dimensions"][0])+" x "+str(rec["dimensions"][1]),fill="black")
  draw.text((x+12,y+tile_h-31),"Anatomy: NOT YET VERIFIED",fill="black")
  rec["decoded"]=True
 except Exception as exc:
  rec["error"]=str(exc)
 rows.append(rec)
report={"species":"Chloris andropogonoides","purpose":"Image QA and visual anatomy review; not proof of taxonomic ID","photos":rows,"image_count":len(photos),"note":"Contact sheet scaled from original local JPEGs. Review source full-resolution photo to place any anatomy arrow; don't annotate microscopic organs from the montage."}
out=pathlib.Path("reports/chloris-anatomy-photo-review-20261023.json")
out.write_text(json.dumps(report,indent=2)+"\n")
target=pathlib.Path("reports/chloris-anatomy-contact-sheet-20261023.jpg")
sheet.save(target,quality=88,optimize=True)
print(json.dumps({"contact_sheet":str(target),"report":str(out),"decoded":sum(1 for r in rows if r.get("decoded"))}))
