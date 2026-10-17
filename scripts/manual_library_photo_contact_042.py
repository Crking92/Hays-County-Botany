#!/usr/bin/env python3
"""Build private, image-backed manual review contact sheets from permanent GitHub Release photo library.
No photo installs and no edits to canonical species.json.
"""
import collections,datetime,hashlib,io,json,os,pathlib,subprocess,zipfile
from PIL import Image,ImageDraw,ImageFont,ImageOps
ROOT=pathlib.Path(".")
SPEC=ROOT/"workflow/manual-photo-enrichment/library-review-042-20261016.json"
QUEUE=ROOT/"reports/diagnostic-photo-selection-queue-latest.json"
OUT=ROOT/"reports/manual-library-review-042-20261016"
ARCH=pathlib.Path("/tmp/hays-photo-library-review-042")
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def font(size):
    try:return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",size)
    except OSError:return ImageFont.load_default()
def clip(t,n=43):return str(t or "")[:n]
def main():
    config=read(SPEC); queue=read(QUEUE)
    available={x["id"]:x for x in queue["review_shortlist"]+queue["more_review_candidates"]}
    refs={x["id"]:x["path"] for x in read(ROOT/"data/manifest.json")["species"]}
    requested=config["species"]
    needed={}
    selected={}
    for x in requested:
        sid=x["id"]
        assert sid in available,("Not in current unclaimed review list",sid)
        info=available[sid]
        sp=read(ROOT/refs[sid])
        assert info["local_files"]==1 and len(sp.get("images") or [])==info["gallery_records"],(sid,len(sp.get("images") or []),info["local_files"])
        assert info["gallery_records"]>=1,(sid,info["gallery_records"])
        # One candidate from each independent observation first; exact displayed scientific name already gated by queue.
        candidates=info["candidate_images"]
        ranked=sorted(candidates,key=lambda c:(c.get("source")!="GBIF",c.get("license","").startswith("CC BY-NC")))
        uniq=[]; seenobs=set(); seenurl=set()
        for c in ranked:
            obs=c.get("observation_id") or c.get("image_url")
            if obs in seenobs or c["image_url"] in seenurl:continue
            uniq.append(c);seenobs.add(obs);seenurl.add(c["image_url"])
        for c in ranked:
            if len(uniq)>=3:break
            if c["image_url"] in seenurl:continue
            uniq.append(c);seenurl.add(c["image_url"])
        selected[sid]=uniq[:3]
        for c in selected[sid]:needed[c["archive_tag"]]=c["asset_name"]
    archives={a["tag"]:a for a in queue["archive_batches"]}
    ARCH.mkdir(parents=True,exist_ok=True)
    zips={}
    for tag,asset in sorted(needed.items()):
        assert tag in archives,tag
        target=ARCH/asset
        if not target.exists():
            subprocess.run(["gh","release","download",tag,"--repo",os.environ["GITHUB_REPOSITORY"],"--pattern",asset,"--dir",str(ARCH)],check=True)
        checksum=hashlib.sha256(target.read_bytes()).hexdigest()
        assert checksum==archives[tag]["checksum"],(tag,"Archive checksum mismatch")
        zips[tag]=zipfile.ZipFile(target)
    manifest={"batch_id":config["id"],"generated_at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
      "source_queue_at":queue["generated_at_utc"],"species":[],"photos_installed":0,
      "warning":"Review-only. Thumbnails have not been botanically verified. Source metadata is not plant identity proof."}
    cells=[]
    for row in requested:
        sid=row["id"]; p=ROOT/refs[sid];sp=read(p)
        existing=None
        for im in sp.get("images") or []:
            file=im.get("file") or ""
            if file and not file.startswith(("http://","https://")) and (p.parent/file).is_file():
                try:
                    with Image.open(p.parent/file) as src:existing=src.convert("RGB").copy()
                    break
                except OSError:pass
        candidates=[]
        for i,c in enumerate(selected[sid],start=1):
            zi=zips[c["archive_tag"]]
            assert c["archive_file"] in zi.namelist(),(sid,c["archive_file"])
            raw=zi.read(c["archive_file"])
            assert len(raw)>18000,(sid,"small archived image")
            with Image.open(io.BytesIO(raw)) as src:
                src.verify()
            with Image.open(io.BytesIO(raw)) as src:
                photo=ImageOps.exif_transpose(src).convert("RGB")
            candidates.append({**c,"index":i,"sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw),"dimensions":[photo.width,photo.height]})
            cells.append((sid,i,photo,c))
        cells.append((sid,0,existing,{"creator":"EXISTING","license":"existing"}))
        manifest["species"].append({"id":sid,"scientific_name":sp["scientific_name"],
            "requested_view":row["desired_view"],"current_gallery_records":len(sp.get("images") or []),
            "current_local_files":int(existing is not None),"candidate_images":candidates})
    OUT.mkdir(parents=True,exist_ok=True)
    tilew,tileh,header=325,266,68
    for page in range((len(requested)+3)//4):
        img=Image.new("RGB",(4*tilew,4*tileh),(247,246,241))
        dr=ImageDraw.Draw(img)
        for rowind,item in enumerate(requested[page*4:page*4+4]):
            sid=item["id"];sp=next(x for x in manifest["species"] if x["id"]==sid)
            cand={}
            for cx in cells:
                if cx[0]==sid:cand[cx[1]]=cx
            for col in range(4):
                x=col*tilew;y=rowind*tileh
                dr.rectangle((x+2,y+2,x+tilew-3,y+tileh-3),outline=(150,150,148),width=2)
                dr.text((x+9,y+8),clip(sp["scientific_name"],34),font=font(14),fill=(25,34,32))
                if col==0:
                    dr.text((x+9,y+29),"EXISTING GALLERY",font=font(12),fill=(25,95,75))
                elif col in cand:
                    c=cand[col][3]
                    dr.text((x+9,y+29),f"CHOICE {col} | {clip(c['creator'],21)}",font=font(12),fill=(30,55,120))
                    dr.text((x+9,y+45),f"{clip(c['license'],12)} | {c['source']}",font=font(11),fill=(65,70,69))
                else:dr.text((x+9,y+29),"NO ARCHIVED OPTION",font=font(11),fill=(100,100,100))
                if col in cand and cand[col][2] is not None:
                    photo=cand[col][2]
                    copy=ImageOps.contain(photo,(tilew-20,tileh-header-12))
                    xp=x+(tilew-copy.width)//2;yp=y+header+(tileh-header-copy.height)//2
                    img.paste(copy,(xp,yp))
                else:
                    dr.text((x+35,y+135),"NOT LOCALLY SAVED",font=font(15),fill=(105,105,105))
        file=OUT/f"contact-{page+1:02d}.jpg"
        img.save(file,"JPEG",quality=75,optimize=True)
        print("REVIEW SHEET",file,file.stat().st_size,flush=True)
    (OUT/"preview-manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"archive_count":len(zips),"species":len(manifest["species"]),
      "options":sum(len(s["candidate_images"]) for s in manifest["species"]),"installed":0},indent=2),flush=True)
if __name__=="__main__":main()
