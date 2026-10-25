#!/usr/bin/env python3
"""Full resolution licensed candidate original verification and human-viewable detail contact sheet."""
import io,json,pathlib,base64,hashlib,urllib.request,time
from PIL import Image,ImageOps,ImageDraw,ImageFont
root=pathlib.Path("reports");source=json.loads((root/"lane3-pine-muhly-inat-sources-20261025.json").read_text())
ids=[665790824,325197730,325197748,321497834,321497847,321497899]
byid={p["photo"]["id"]:p for p in source["eligible"]}
CW,CH=500,580;C=3;R=2
canvas=Image.new("RGB",(CW*C,CH*R),"#ffffff");dr=ImageDraw.Draw(canvas);font=ImageFont.load_default()
report={"photos":[],"holds":[],"image_role_review":"Candidate previews only; no unverified anatomy arrows"}
for ix,pid in enumerate(ids):
 x=(ix%C)*CW;y=(ix//C)*CH
 try:
  row=byid[pid];photo=row["photo"]
  if photo["license_code"] not in ["cc0","cc-by","cc-by-sa"]:raise ValueError("photo license not approved")
  req=urllib.request.Request(photo["original_url"],headers={"User-Agent":"HaysBotanyVisualLearner/1.0 (botany CC-license source verification; github.com/Crking92/Hays-County-Botany)"})
  with urllib.request.urlopen(req,timeout=40) as res:blob=res.read(9000000)
  with Image.open(io.BytesIO(blob)) as im:im.verify()
  with Image.open(io.BytesIO(blob)) as im:
   im=ImageOps.exif_transpose(im).convert("RGB")
   natural=im.size
   im.thumbnail((CW-24,CH-57))
   canvas.paste(im,(x+(CW-im.width)//2,y+5+(CH-57-im.height)//2))
  dr.text((x+9,y+CH-43),f"{ix+1} — iNat photo {pid}",fill="#111111",font=font)
  dr.text((x+9,y+CH-27),f"obs {row['observation']}   {photo['license_code']}",fill="#111111",font=font)
  dr.text((x+9,y+CH-13),photo["attribution"][:60],fill="#111111",font=font)
  report["photos"].append({"photo_id":pid,"observation":row["observation"],"license":photo["license_code"],"original_pixels":natural,"sha256":hashlib.sha256(blob).hexdigest(),"bytes":len(blob)})
 except Exception as e:report["holds"].append({"photo":pid,"reason":str(e)[:240]})
 time.sleep(0.25)
buf=io.BytesIO();canvas.save(buf,"JPEG",quality=70,optimize=True)
out=root/"lane3-pine-muhly-zoom-audit-20261025.b64.txt"
out.write_text(base64.b64encode(buf.getvalue()).decode("ascii")+"\n")
(root/"lane3-pine-muhly-zoom-audit-20261025.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({"verified_originals":len(report["photos"]),"holds":report["holds"],"text_size":out.stat().st_size,"pixel_dimensions":canvas.size}))
