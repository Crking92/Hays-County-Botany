#!/usr/bin/env python3
"""Search actual photo-level open-use iNaturalist images of fall witchgrass.

Stage ONLY, no gallery publication or anatomy inferred.
"""
import urllib.request,urllib.parse,json,pathlib,hashlib,time,io
from PIL import Image,ImageOps
out=pathlib.Path("workflow/photo-reviews/lane4-cognata-basal-20261026")
out.mkdir(parents=True,exist_ok=True)
hdr={"User-Agent":"Hays-County-Botany/1.0 (noncommercial botanical photo screen)"}
def download(url,maxsize=8000000):
    for i in range(3):
        try:
            req=urllib.request.Request(url,headers=hdr)
            with urllib.request.urlopen(req,timeout=30) as r: blob=r.read(maxsize+1)
            if len(blob)>maxsize: raise ValueError("Max bytes exceeded")
            return blob
        except Exception:
            if i==2:raise
            time.sleep(4*(i+1))
records=[]
errors=[]
for params in [
  {"taxon_id":161901,"photos":"true","photo_license":"cc0,cc-by,cc-by-sa","per_page":50,"order":"desc","order_by":"created_at","lat":29.9,"lng":-98.1,"radius":500},
  {"taxon_id":161901,"photos":"true","photo_license":"cc0,cc-by,cc-by-sa","per_page":60,"order":"desc","order_by":"created_at"}
]:
    try:
        api="https://api.inaturalist.org/v1/observations?"+urllib.parse.urlencode(params)
        data=json.loads(download(api))
        for obs in data.get("results",[]):
            if obs.get("taxon",{}).get("name")!="Digitaria cognata":
                continue
            for ph in obs.get("photos",[]):
                if ph.get("license_code") not in ["cc0","cc-by","cc-by-sa"]: continue
                ident=str(ph.get("id",""))
                if ident and all(x["photo_id"]!=ident for x in records):
                    records.append({
                       "photo_id":ident,"observation":obs.get("id"),
                       "source":"https://www.inaturalist.org/photos/"+ident,
                       "observation_page":"https://www.inaturalist.org/observations/"+str(obs.get("id")),
                       "license":ph["license_code"],
                       "attribution":ph.get("attribution",""),
                       "observed_on":obs.get("observed_on"),
                       "place_guess":obs.get("place_guess"),
                       "image_url":ph.get("url","")
                    })
    except Exception as e:
        errors.append(str(e))
# Use smaller candidate count to keep this a review not a photo dump
kept=[]
for record in records[:18]:
    try:
        url=record["image_url"]
        if not url.startswith("https://"):raise ValueError("No HTTPS source")
        # iNat photo size URLs: thumb/small/medium/large/original
        url=url.replace("/square.","/large.").replace("/thumb.","/large.").replace("/small.","/large.").replace("/medium.","/large.")
        blob=download(url,3500000)
        Image.open(io.BytesIO(blob)).verify()
        im=ImageOps.exif_transpose(Image.open(io.BytesIO(blob))).convert("RGB")
        if min(im.size)<400:raise ValueError("Photo too small for study")
        fname=out/("inat-"+record["photo_id"]+".jpg")
        if not fname.exists():im.save(fname,"JPEG",quality=88,optimize=True)
        record["local"]=str(fname)
        record["sha256"]=hashlib.sha256(fname.read_bytes()).hexdigest()
        record["resolution"]=list(im.size)
        record["image_role"]="UNREVIEWED: determine whether crown/rootstock, collar, blade margin or flowering axis actually visible"
        kept.append(record)
    except Exception as e:errors.append({"photo_id":record["photo_id"],"reason":str(e)})
(out/"manifest.json").write_text(json.dumps({"species":"Digitaria cognata","policy":"Photo-level CC0/CC-BY/CC-BY-SA candidates ONLY, not displayed in website","added":kept,"errors":errors,"total_exact_photo_hits":len(records)},indent=2,ensure_ascii=False)+"\n")
print(json.dumps({"found":len(records),"staged":len(kept),"errors":errors[:3]}))
