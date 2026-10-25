#!/usr/bin/env python3
"""Build compact labelled candidate photo contact sheet from source-licensed pine muhly originals.
Private research report, does not add anything to the public species gallery.
"""
import json,pathlib,urllib.request,io,time,urllib.error
from PIL import Image,ImageOps,ImageDraw,ImageFont
src=pathlib.Path("reports/lane3-pine-muhly-inat-sources-20261025.json")
data=json.loads(src.read_text())
eligible=data["eligible"]
sheet_entries=[]
for entry in eligible[:52]:
 p=entry["photo"];url=p.get("original_url","")
 if not url or p.get("license_code") not in ("cc0","cc-by","cc-by-sa"):continue
 sheet_entries.append((entry["observation"],p["id"],url.replace("/original.","/medium."),p["license_code"],p.get("attribution","")))
W,H=240,198;C=5
R=(len(sheet_entries)+C-1)//C
canvas=Image.new("RGB",(C*W,R*H),"#eff1ec")
dr=ImageDraw.Draw(canvas)
font=ImageFont.load_default()
report={"total_eligible":len(eligible),"review_slots":[],"holds":[]}
for index,(ob,pid,url,lic,author) in enumerate(sheet_entries):
 x=(index%C)*W;y=(index//C)*H
 try:
  req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyVisualLearner/1.0 (original CC licensed photo review, github.com/Crking92/Hays-County-Botany)"})
  with urllib.request.urlopen(req,timeout=35) as r:blob=r.read(3500000)
  with Image.open(io.BytesIO(blob)) as im:
   im=ImageOps.exif_transpose(im).convert("RGB");im.thumbnail((W-10,H-39))
   ox=x+(W-im.width)//2;oy=y+5+(H-39-im.height)//2
   canvas.paste(im,(ox,oy))
  dr.text((x+5,y+H-32),f"{index+1}: p{pid}",font=font,fill="#111111")
  dr.text((x+5,y+H-17),f"obs {ob} / {lic}",font=font,fill="#111111")
  report["review_slots"].append({"slot":index+1,"observation":ob,"photo_id":pid,"license":lic,"attribution":author,"image":url,"result":"RENDERED"})
 except Exception as e:
  dr.text((x+6,y+12),"Image unavailable",font=font,fill="#aa2222")
  report["holds"].append({"slot":index+1,"photo_id":pid,"reason":str(e)[:220]})
 time.sleep(0.08)
destination=pathlib.Path("reports/lane3-pine-muhly-license-source-contact-20261025.jpg")
canvas.save(destination,"JPEG",quality=64,optimize=True)
pathlib.Path("reports/lane3-pine-muhly-license-source-contact-20261025.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"total_eligible":report["total_eligible"],"contact_sheet":str(destination),"bytes":destination.stat().st_size,"rendered":len(report["review_slots"]),"holds":report["holds"][:8]}))
