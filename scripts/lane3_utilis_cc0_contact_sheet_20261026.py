#!/usr/bin/env python3
"""CC0 exact-taxon Muhlenbergia utilis contact sheet for disciplined photo screening.
NO canonical species/photo image count changes. Preview files are review-only.
"""
import hashlib,io,json,pathlib,urllib.request,time,math
from PIL import Image,ImageOps,ImageDraw,ImageFont
manifest=json.loads(pathlib.Path("reports/lane3-utilis-inat-open-license-scout-20261026.json").read_text())
assert manifest["taxon"]=="Muhlenbergia utilis"
ids=[410577667,410577679,410577686,410577695,260420250,260420284,260420450,
274634631,274634697,479388364,479388365,479388367,479388378,479389544,
536646034,536646051,647018774,647019382,653911574,192457484,192457572,
192457669,192457746,242540349]
by_id={int(p["photo_id"]):p for p in manifest["sources"]}
assert all(n in by_id and by_id[n]["license_code"]=="cc0" and by_id[n]["taxon"]=="Muhlenbergia utilis" for n in ids)
root=pathlib.Path("reports")
report={"taxon":"Muhlenbergia utilis","status":"PREVIEW_ONLY_NOT_INSTALLED","image_rights":"Each exact iNat source has photo-specific CC0 code per live source scout","review_photo_ids":ids,"downloaded":[],"holds":[],"source_scout":"reports/lane3-utilis-inat-open-license-scout-20261026.json"}
w,h=508,430
cols=4;rows=math.ceil(len(ids)/cols)
sheet=Image.new("RGB",(cols*w,rows*h),(247,247,247))
draw=ImageDraw.Draw(sheet)
try:
 font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",16)
except:font=ImageFont.load_default()
def fetch(url):
 req=urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotanyPublicPhotoReview/1.0 (github.com/Crking92/Hays-County-Botany)","Accept":"image/jpeg,image/*"})
 with urllib.request.urlopen(req,timeout=30) as h:
  body=h.read(5000001)
 assert 1000<len(body)<5000001
 with Image.open(io.BytesIO(body)) as im:
  assert im.format=="JPEG"
  im.verify()
 with Image.open(io.BytesIO(body)) as im:
  im=ImageOps.exif_transpose(im).convert("RGB")
  return im
for k,id in enumerate(ids):
 row=by_id[id]
 x=(k%cols)*w;y=(k//cols)*h
 draw.rectangle((x,y,x+w-1,y+h-1),outline=(120,120,120),width=1)
 try:
  url=row["photo_url"].replace("/square.","/large.")
  img=fetch(url)
  img.thumbnail((w-16,h-78),Image.Resampling.LANCZOS)
  sheet.paste(img,(x+(w-img.width)//2,y+12+(h-78-img.height)//2))
  label=f"#{id}  CC0  {str(row['place_guess'])[:38]}"
  draw.text((x+10,y+h-56),label,font=font,fill=(10,10,10))
  draw.text((x+10,y+h-33),f"iNat observation #{row['observation_id']}",font=font,fill=(50,50,50))
  report["downloaded"].append({"photo_id":id,"photo_page":row["source_page"],"observation":row["observation"],
     "license":"CC0","place_guess":row["place_guess"],"original_source_width":img.width,"original_source_height":img.height,
     "large_url":url,"role":"UNASSESSED - preview only"})
 except Exception as exc:
  draw.text((x+10,y+100),f"PHOTO #{id} NOT LOADED",font=font,fill=(80,80,80))
  report["holds"].append({"photo_id":id,"error":str(exc)[:190]})
out=root/"lane3-utilis-cc0-contact-sheet-20261026.jpg"
buf=io.BytesIO()
sheet.save(buf,"JPEG",quality=86,optimize=True)
out.write_bytes(buf.getvalue())
report["contact_sheet"]=str(out)
report["sheet_sha256"]=hashlib.sha256(buf.getvalue()).hexdigest()
report["downloaded_count"]=len(report["downloaded"])
report["status"]="CONTACT_SHEET_READY_PIXEL_REVIEW_REQUIRED" if len(report["downloaded"])>=6 else "INSUFFICIENT_CONTACT_DOWNLOADS"
(root/"lane3-utilis-cc0-contact-sheet-20261026.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({"status":report["status"],"photos":len(report["downloaded"]),"holds":report["holds"],"contact_sheet":str(out)}))
