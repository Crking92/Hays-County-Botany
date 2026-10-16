#!/usr/bin/env python3
"""Contact-sheet-only mirror screening for currently external-only canonical galleries.

No species changes. Each image must have its own explicit compatible license and
creator; source-name metadata is not independent botanical ID.
"""
import datetime as dt, hashlib, io, json, pathlib, urllib.request, urllib.parse, time
from PIL import Image, ImageOps, ImageDraw, ImageFont
R=pathlib.Path(".")
OUT=R/"reports/manual-external-mirror-review-016"
IDS=["symphyotrichum-drummondii","symphyotrichum-sericeum",
     "tradescantia-occidentalis","amorpha-canescens","quercus-virginiana",
     "scutellaria-wrightii","aristida-oligantha","tripsacum-dactyloides"]
UA={"User-Agent":"Mozilla/5.0 (compatible; HaysCountyBotanyPhotoAudit/1.0; educational research)","Accept":"image/avif,image/webp,image/*;q=0.9,*/*;q=0.8"}
def allowed(license):
    s=str(license or "").lower()
    return ("cc0" in s or "cc by" in s or "public domain" in s) and not any(
        bad in s for bad in ("unverified","source-site","all rights","private-study","private study"))
def clean(raw):
    with Image.open(io.BytesIO(raw)) as im:
        im.load()
        rgb=ImageOps.exif_transpose(im).convert("RGB")
        w,h=rgb.size
        if min(w,h)<220 or max(w,h)<550:raise ValueError("image too small")
        rgb.thumbnail((1350,1350),Image.Resampling.LANCZOS)
        stream=io.BytesIO();rgb.save(stream,format="JPEG",quality=89,optimize=True)
        return stream.getvalue(),(w,h),rgb
def read_url(url):
    urls=[url]
    if "commons.wikimedia.org/wiki/Special:Redirect/file/" in url:
        # Wikimedia original may be rate limited, but avoid changing image identity.
        urls.append(url.replace("https://commons.wikimedia.org/wiki/Special:Redirect/file/",
                                "https://commons.wikimedia.org/wiki/Special:FilePath/"))
    last=""
    for candidate in urls:
        try:
            with urllib.request.urlopen(urllib.request.Request(candidate,headers=UA),timeout=22) as resp:
                raw=resp.read(15000001)
                if len(raw)>15000000:raise ValueError("oversize")
            return clean(raw)
        except Exception as e:last=type(e).__name__+":"+str(e)[:100]
    raise ValueError(last)
def font(sz):
    for name in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",):
        try:return ImageFont.truetype(name,sz)
        except OSError:pass
    return ImageFont.load_default()
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((R/"data/manifest.json").read_text(encoding="utf-8"))
    refs={r["id"]:r["path"] for r in manifest["species"]}
    report={"id":"manual-external-mirror-review-016-20261016",
       "generated_at_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
       "species":[],"download_successes":0,"errors":[],
       "caution":"External gallery source metadata is provisional; contact-sheet viewing cannot independently establish exact species identity.",
       "installed":0}
    tiles=[]
    for sid in IDS:
        if sid not in refs:
            report["errors"].append({"id":sid,"error":"not canonical"});continue
        file=R/refs[sid];sp=json.loads(file.read_text(encoding="utf-8"))
        gallery=sp.get("images") or []
        if len(gallery)!=3 or any(not str(x.get("file","")).startswith("https://") for x in gallery):
            report["errors"].append({"id":sid,"error":"not exactly three external-only image records"});continue
        entry={"id":sid,"species_path":str(file),"scientific_name":sp["scientific_name"],
               "gallery_count":len(gallery),"candidates":[]}
        for index,record in enumerate(gallery,1):
            url=record.get("file") or ""
            if not allowed(record.get("license")) or not record.get("creator") or not record.get("source_page"):
                entry["candidates"].append({"index":index,"status":"license_or_creator_missing"});continue
            try:
                img,dim,preview=read_url(url)
                checksum=hashlib.sha256(img).hexdigest()
                entry["candidates"].append({
                    "index":index,"status":"downloaded_for_visual_review",
                    "sha256_of_normalized_jpeg":checksum,"normalized_bytes":len(img),
                    "original_dimensions":dim,"original_url":url,
                    "source_page":record["source_page"],"creator":record["creator"],
                    "license":record["license"],"role":record.get("role",""),
                    "source_record_index":index-1})
                tiles.append((sid,index,preview,record))
                report["download_successes"]+=1
            except Exception as err:
                entry["candidates"].append({"index":index,"status":"unavailable",
                    "error":str(err)[:140]})
        report["species"].append(entry)
    (OUT/"preview-manifest.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    tw,th=340,250
    for page in range((len(report["species"])+3)//4):
        sheet=Image.new("RGB",(tw*4,th*4),(247,246,241));d=ImageDraw.Draw(sheet)
        for row,e in enumerate(report["species"][page*4:page*4+4]):
            for col in range(4):
                x=col*tw;y=row*th
                d.rectangle((x+2,y+2,x+tw-3,y+th-3),outline=(150,155,145),width=2)
                d.text((x+8,y+7),e["scientific_name"][:40],font=font(13),fill=(29,49,44))
                if col==0:
                    d.text((x+8,y+29),"CURRENT EXTERNAL-ONLY RECORDS",font=font(11),fill=(45,90,68))
                    d.text((x+15,y+111),"NO LOCAL PHOTO FILE",font=font(14),fill=(91,95,92))
                    continue
                option=next((c for c in e["candidates"] if c["index"]==col),None)
                candidate=next((t for t in tiles if t[0]==e["id"] and t[1]==col),None)
                if not candidate:
                    d.text((x+8,y+45),(option or {}).get("error",(option or {}).get("status","unavailable"))[:42],font=font(11),fill=(144,61,54))
                    continue
                record=candidate[3]
                d.text((x+8,y+28),"CHOICE "+str(col)+" | "+str(record["creator"])[:28],font=font(11),fill=(37,69,106))
                d.text((x+8,y+44),str(record["license"])[:37],font=font(10),fill=(94,88,84))
                pic=ImageOps.contain(candidate[2],(tw-18,th-72))
                sheet.paste(pic,(x+(tw-pic.width)//2,y+67+(th-72-pic.height)//2))
        p=OUT/("contact-%02d.jpg"%(page+1))
        sheet.save(p,"JPEG",quality=84,optimize=True)
        print("CONTACT",p,flush=True)
    print(json.dumps({"species":len(report["species"]),"successes":report["download_successes"],
                      "errors":report["errors"],"candidate_failures":sum(c["status"]!="downloaded_for_visual_review"
                           for s in report["species"] for c in s["candidates"])},indent=2),flush=True)
if __name__=="__main__":main()
