#!/usr/bin/env python3
"""Make private-in-repo small source-specific visual contact sheets for one-off
Limnodea photo diagnostics. NO canonical species media is changed here.
Only preview data, read-only iNat source photo and individual licenses.
"""
from pathlib import Path
import json,io,hashlib,requests
from PIL import Image,ImageOps,ImageDraw,ImageFont
root=Path("reports/limnodea-photo-shortlist-20261023")
src=json.loads(Path("reports/limnodea-inat-potential-fine-macro-scout-20261023.json").read_text())
ids=[
359373339,283435855,354995431,276792689,207472916,207479270,
350866665,380163833,364891216,364789042,350132852,350715408,
279591415,350060377
]
photos=src["candidate_photos"]
selected=[]
for ident in ids:
 vv=sorted([x for x in photos if x["observation_id"]==ident],key=lambda x:x["position"])
 for p in vv[:8]: selected.append(p)
# 63-ish images, 4 montage boards
selected=selected[:64]
session=requests.Session()
session.headers["User-Agent"]="HaysBotanyOzarkgrassLicensedPhotoPixelReview/1.0"
session.headers["Accept"]="image/jpeg,image/*;q=0.9"
valid=[]
for i,ph in enumerate(selected):
 url=ph["url"].replace("/square.","/medium.")
 try:
  r=session.get(url,timeout=20);r.raise_for_status()
  with Image.open(io.BytesIO(r.content)) as img:
   img.load()
   if img.format not in ("JPEG","PNG","WEBP"): raise ValueError("Not image")
   im=ImageOps.exif_transpose(img).convert("RGB")
  im.thumbnail((320,282))
  ph={**ph,"contact_index":i+1,"raw_size":len(r.content),"preview_dimensions":list(im.size),"preview_sha256":hashlib.sha256(r.content).hexdigest()}
  valid.append((ph,im))
 except Exception as ex: print("image retrieval failed",i+1,ph["photo_id"],str(ex)[:100])
root.mkdir(parents=True,exist_ok=True)
report={"scope":"Limnodea arkansana exact iNaturalist source-determined candidate previews for fine specimen anatomy",
"license_policy":"Each source per-image license; no confirmation or gallery install from preview alone",
"photos":[],"montages":[],"total_selected":len(selected),"downloaded_for_review":len(valid)}
for block in range(0,len(valid),16):
 subset=valid[block:block+16]
 w,h=1360,1460
 panel=Image.new("RGB",(w,h),(250,249,245))
 d=ImageDraw.Draw(panel)
 for j,(metadata,im) in enumerate(subset):
  x=(j%4)*340
  y=(j//4)*365
  panel.paste(im,(x+(340-im.width)//2,y+18))
  caption=f"#{metadata['contact_index']} o{metadata['observation_id']} p{metadata['photo_id']}"
  lic=f"{metadata['license']}  frame {metadata['position']+1}"
  d.text((x+9,y+307),caption,fill=(0,0,0))
  d.text((x+9,y+329),lic,fill=(0,0,0))
  report["photos"].append({k:metadata[k] for k in [
     "contact_index","observation_id","photo_id","license","attribution",
     "url","original_url","observation_url","position","preview_dimensions"]})
 fn=f"sheet-{block//16+1:02d}.jpg"
 target=root/fn
 panel.save(target,"JPEG",quality=84,optimize=True)
 report["montages"].append({"file":str(target),"indices":[m["contact_index"] for m,_ in subset]})
(root/"contact-index.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
print("Saved",len(valid),"small previews to",len(report["montages"]),"license-tagged contact sheets")
