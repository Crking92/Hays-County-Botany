#!/usr/bin/env python3
"""Contact sheets of EXISTING canonical learner images; no installs or source modifications."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import json, textwrap, hashlib

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"reports/diagnostic-role-review-061-20261017"
IDS=[
 "bouteloua-curtipendula","asclepias-asperula","coreopsis-basalis","croton-texensis",
 "solidago-altissima","euphorbia-cyathophora","quercus-laceyi","matelea-reticulata"]
manifest=json.loads((ROOT/"data/manifest.json").read_text())
by_id={x["id"]:ROOT/x["path"] for x in manifest["species"]}
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
bold=ImageFont.truetype(FONT,19)
small=ImageFont.truetype(FONT,13)
caption=ImageFont.truetype(FONT,12)
W=1900; H=640; cardW=310; cardH=275; cols=6; margin=15
OUT.mkdir(parents=True,exist_ok=True)
entries=[]
def draw_wrap(draw,x,y,s,font,width,maxlines=3,fill="#222222",lineheight=17):
    words=s.split(); lines=[]; line=""
    for word in words:
        cand=(line+" "+word).strip()
        if draw.textbbox((0,0),cand,font=font)[2]>width and line:
            lines.append(line); line=word
        else: line=cand
    if line: lines.append(line)
    for l in lines[:maxlines]:
        draw.text((x,y),l,font=font,fill=fill);y+=lineheight
    return y

for pi in range(0,len(IDS),2):
    sheet=Image.new("RGB",(W,H),"#f5f5f1")
    draw=ImageDraw.Draw(sheet)
    for ri,id in enumerate(IDS[pi:pi+2]):
        file=by_id[id]; sp=json.loads(file.read_text())
        assert sp["id"]==id
        draw.text((margin,ri*318+4),sp.get("scientific_name",id),fill="#254c32",font=bold)
        images=sp.get("images",[])
        assert len(images)<=6
        values=[]
        for i,im in enumerate(images):
            f=str(im.get("file") or "")
            path=(file.parent/f).resolve()
            assert path.is_relative_to(ROOT) and path.is_file(), (id,f)
            if path.suffix.lower()==".svg":
                values.append({"index":i,"file":f,"role":im.get("role"),"format":"vector","photographer":im.get("creator"),"license":im.get("license")})
                continue
            with Image.open(path) as src:
                src=ImageOps.exif_transpose(src).convert("RGB")
                size=list(src.size)
                src.thumbnail((cardW-14,cardH-95),Image.Resampling.LANCZOS)
                x=margin+i*cardW+5; y=ri*318+36
                sheet.paste(src,(x+(cardW-14-src.width)//2,y+(cardH-95-src.height)//2))
                draw.text((x,y+cardH-90),f"IMAGE {i} | {size[0]}x{size[1]}",font=small,fill="#222")
                y2=draw_wrap(draw,x,y+cardH-70,str(im.get("role") or "Uncaptioned"),caption,cardW-13,2,fill="#333",lineheight=15)
                draw_wrap(draw,x,y2+3,str(im.get("creator") or "")[:42]+" | "+str(im.get("license") or "")[:30],caption,cardW-13,2,fill="#555",lineheight=15)
            values.append({"index":i,"file":f,"role":im.get("role"),"dimensions":size,"creator":im.get("creator"),"license":im.get("license"),"source":im.get("source_page")})
        entries.append({"id":id,"scientific_name":sp.get("scientific_name",id),"path":str(file.relative_to(ROOT)),"photos":values,"look_here_first":sp.get("look_here_first","")})
    out=OUT/f"contact-{pi//2+1:02}.jpg"
    sheet.save(out,"JPEG",quality=86,optimize=True)
    print(out.relative_to(ROOT),out.stat().st_size)
(OUT/"view-manifest.json").write_text(json.dumps({"mode":"existing-canonical-photos-only","species":entries,"note":"Contact sheets screen broad visible content; exact anatomical features and species determination require full-resolution and expert confirmation."},indent=2,ensure_ascii=False)+"\n")
print("species",len(entries),"photos",sum(len(x["photos"]) for x in entries))
