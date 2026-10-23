#!/usr/bin/env python3
"""QA physical grass images and produce a visual contact sheet. No speculative anatomical labels."""
import json, pathlib, hashlib
from PIL import Image, ImageOps, ImageDraw
targets={
"pine-muhly":"content/taxa/Poaceae/Muhlenbergia/muhlenbergia-dubia",
"anatherum-tenuispatheum":"content/taxa/Poaceae/Anatherum/anatherum-tenuispatheum",
}
outdir=pathlib.Path("reports")
report={"species":{},"purpose":"Physical file proof, license inventory and visual inspection handoff"}
for name,root in targets.items():
 root=pathlib.Path(root);record=json.loads((root/"species.json").read_text())
 assert record["images"],name+" has no photos"
 items=[];w=1000;h=500;canvas=Image.new("RGB",(w,h*((len(record["images"])+1)//2)),"white");draw=ImageDraw.Draw(canvas)
 for n,im in enumerate(record["images"]):
  path=root/im["file"];item={"path":str(path),"source":im.get("source_page"),"license":im.get("license"),"exists":path.is_file()}
  if path.is_file():
   raw=path.read_bytes()
   with Image.open(path) as p:p.verify()
   with Image.open(path) as p:
    img=ImageOps.exif_transpose(p).convert("RGB")
    item["dimensions"]=list(img.size);item["sha256"]=hashlib.sha256(raw).hexdigest();item["decoded"]=True
    img.thumbnail((475,400))
    x=n%2*500+(500-img.width)//2;y=n//2*h+10
    canvas.paste(img,(x,y))
    draw.text((n%2*500+10,(n//2+1)*h-85),im["file"],fill="black")
    draw.text((n%2*500+10,(n//2+1)*h-60),"License: "+str(im.get("license")),fill="black")
    draw.text((n%2*500+10,(n//2+1)*h-35),"Anatomy: NOT YET VERIFIED",fill="black")
  items.append(item)
 report["species"][name]={"images":items,"notes":"Use originals, not thumbnails, before anatomy arrows. Do not count CC BY-NC as unrestricted reuse."}
 canvas.save(outdir/(name+"-review-contact-sheet-20261023.jpg"),quality=88,optimize=True)
(outdir/"sparse-grass-photo-file-qa-20261023.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({k:len(v["images"]) for k,v in report["species"].items()}))
