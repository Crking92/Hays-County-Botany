#!/usr/bin/env python3
"""Visually stage rights-limited Joey Santore photo inventory for 3 exact canonical taxa.

Review only: preserve CC BY-NC, original observer credit, avoid public/commercial reuse.
Do not edit species files or infer botanical identity from iNaturalist labels.
"""
import csv,collections,io,json,pathlib,urllib.request,hashlib,datetime as dt
from PIL import Image,ImageOps,ImageDraw,ImageFont
R=pathlib.Path(".")
OUT=R/"reports/manual-joey-review-019"
TARGET=["verbena-canescens","bothriochloa-barbinodis","opuntia-macrorhiza","eragrostis-intermedia"]
SOURCE=R/"workflow/joey-texas-inat-photo-inventory/photo-candidates.csv"
def font(sz):
    try:return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",sz)
    except OSError:return ImageFont.load_default()
def pick(rows):
    byobs=collections.defaultdict(list)
    for r in rows:byobs[r["observation_id"]].append(r)
    chosen=[]
    for obs in sorted(byobs,key=lambda x:(-len(byobs[x]),x)):
        for r in byobs[obs][:3]:
            chosen.append(r)
            if len(chosen)>=6:return chosen
    return chosen
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    with SOURCE.open(newline="",encoding="utf-8-sig") as f: rows=list(csv.DictReader(f))
    cards=[]
    thumbnails={}
    for sid in TARGET:
        data=[r for r in rows if r.get("canonical_id")==sid
              and r.get("photographer_gate")=="joey_credited_candidate"
              and r.get("source_license","").lower()=="cc-by-nc"
              and r.get("taxon_match","").startswith("exact_slug")
              and str(r.get("image_url","")).startswith("https://inaturalist-open-data.s3.amazonaws.com/")]
        ent={"id":sid,"taxon_names":list(sorted(set(r["scientific_name"] for r in data))),
             "available_inventory":len(data),"candidates":[]}
        for n,row in enumerate(pick(data),1):
            item={"index":n,"photo_id":row["photo_id"],"image_url":row["image_url"],
                  "source_page":row["photo_url"],"observation":row["observation_url"],
                  "source_scientific_name":row["scientific_name"],
                  "creator":"Joey Santore","license":"CC BY-NC",
                  "rights_note":"Private noncommercial botany educational use with explicit attribution; do not redistribute on commercial/public-facing website without permission and rights review"}
            try:
                req=urllib.request.Request(row["image_url"],headers={"User-Agent":"HaysBotanyStudy/1.0","Accept":"image/*"})
                with urllib.request.urlopen(req,timeout=24) as resp:raw=resp.read(10000001)
                if len(raw)>10000000:raise ValueError("oversize")
                with Image.open(io.BytesIO(raw)) as im:
                    im.load();rgb=ImageOps.exif_transpose(im).convert("RGB")
                if min(rgb.size)<240:raise ValueError("small image")
                rgb.thumbnail((1280,1280),Image.Resampling.LANCZOS)
                buf=io.BytesIO();rgb.save(buf,"JPEG",quality=89,optimize=True)
                item.update({"status":"visual_preview","sha256":hashlib.sha256(buf.getvalue()).hexdigest(),
                             "bytes":len(buf.getvalue()),"dimensions":[rgb.width,rgb.height]})
                thumbnails[(sid,n)]=rgb
            except Exception as e:item.update({"status":"unavailable","error":str(e)[:120]})
            ent["candidates"].append(item)
        cards.append(ent)
    report={"generated_at_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
            "id":"manual-joey-review-019","species":cards,"installed":0,"expert_id_verified":False}
    (OUT/"preview-manifest.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    tw,th=225,245
    img=Image.new("RGB",(tw*7,th*len(cards)),(246,245,241));d=ImageDraw.Draw(img)
    for i,card in enumerate(cards):
        for k in range(7):
            x=k*tw;y=i*th
            d.rectangle((x+1,y+1,x+tw-2,y+th-2),outline=(171,169,160),width=2)
            d.text((x+7,y+8),card["id"][:25],font=font(11),fill=(26,58,45))
            if k==0:
                d.text((x+7,y+48),str(card["available_inventory"])+" archived Joey",font=font(13),fill=(27,72,55))
                d.text((x+7,y+72),"candidate photos",font=font(12),fill=(27,72,55))
                continue
            ent=next((c for c in card["candidates"] if c["index"]==k),None)
            if ent:
                d.text((x+7,y+30),"CHOICE "+str(k)+"  CC BY-NC",font=font(10),fill=(40,74,112))
                d.text((x+7,y+46),str(ent["photo_id"]),font=font(11),fill=(70,70,70))
                photo=thumbnails.get((card["id"],k))
                if photo is not None:
                    small=ImageOps.contain(photo,(tw-16,th-75))
                    img.paste(small,(x+(tw-small.width)//2,y+68+(th-75-small.height)//2))
                else:d.text((x+7,y+100),ent.get("error","No photo")[:24],font=font(10),fill=(130,66,57))
    sheet=OUT/"contact-01.jpg";img.save(sheet,"JPEG",quality=85,optimize=True)
    print(json.dumps({"cards":len(cards),"photo_previews":len(thumbnails),"sheet":str(sheet),
        "unavailable":[(c["id"],x["photo_id"]) for c in cards for x in c["candidates"] if x["status"]!="visual_preview"]},indent=2))
if __name__=="__main__":main()
