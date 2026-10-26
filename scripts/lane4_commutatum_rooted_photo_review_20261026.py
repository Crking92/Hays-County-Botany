#!/usr/bin/env python3
"""Stage exact-source, reuse-cleared Dichanthelium commutatum images for review.
No species card, gallery, license field or arrows are modified by this source screen.
"""
import io,json,pathlib,urllib.parse,urllib.request,hashlib,html,re,time
from PIL import Image,ImageOps
dest=pathlib.Path("workflow/photo-reviews/lane4-commutatum-rooted-20261026")
dest.mkdir(parents=True,exist_ok=True)
ids=["363938833","363938835","363938836","363938848","259295899","259295925"]
titles=["File:Dichanthelium commutatum "+n+".jpg" for n in ids]
headers={"User-Agent":"HaysCountyBotanyVisualLearner/1.0 (contact via github Crking92/Hays-County-Botany)"}
def get(url,maxbytes=11000000):
    for attempt in range(3):
        try:
            request=urllib.request.Request(url,headers=headers)
            with urllib.request.urlopen(request,timeout=45) as r: b=r.read(maxbytes+1)
            if len(b)>maxbytes: raise ValueError("Oversize response")
            return b
        except Exception:
            if attempt==2: raise
            time.sleep((attempt+1)*4)
    raise RuntimeError("No response")
report={"species":"Dichanthelium commutatum","scope":"Rights-gated candidates only; nothing shown in public gallery until pixels verified","added":[],"held":[]}
try:
  query=urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo","iiprop":"url|sha1|extmetadata","titles":"|".join(titles)})
  res=json.loads(get("https://commons.wikimedia.org/w/api.php?"+query))
  pages={v["title"]:v for v in res["query"]["pages"].values()}
except Exception as exc:
  report["held"].append({"stage":"api","reason":str(exc)})
  pages={}
for id,title in zip(ids,titles):
    page="https://commons.wikimedia.org/wiki/"+urllib.parse.quote(title.replace(" ","_"),safe=":/()")
    dst=dest/("commutatum-"+id+".jpg")
    try:
       record=pages.get(title)
       if not record or not record.get("imageinfo"):raise ValueError("Commons metadata unavailable")
       info=record["imageinfo"][0]
       meta=info.get("extmetadata") or {}
       license=html.unescape(re.sub("<[^>]+>"," ",meta.get("LicenseShortName",{}).get("value",""))).strip()
       license_url=meta.get("LicenseUrl",{}).get("value","")
       creator=html.unescape(re.sub("<[^>]+>"," ",meta.get("Artist",{}).get("value",""))).strip()
       if not (license.upper() in ["CC0","CC0 1.0","CC BY 4.0","CC BY 3.0","CC BY-SA 4.0","CC BY-SA 3.0"]):
           raise ValueError("License not publicly cleared for new candidate: "+license)
       if not creator:raise ValueError("No photographer")
       src=info.get("url","")
       if not src.startswith("https://upload.wikimedia.org/wikipedia/commons/"):raise ValueError("Untrusted image host")
       original=get(src)
       if hashlib.sha1(original).hexdigest()!=info.get("sha1"):raise ValueError("Original sha1 differs")
       Image.open(io.BytesIO(original)).verify()
       im=ImageOps.exif_transpose(Image.open(io.BytesIO(original))).convert("RGB")
       if min(im.size)<850:raise ValueError("Photo below target teaching resolution")
       if not dst.exists():im.save(dst,format="JPEG",quality=91,optimize=True)
       sha256=hashlib.sha256(dst.read_bytes()).hexdigest()
       report["added"].append({"id":id,"path":str(dst),"source_page":page,"creator":creator,"license":license,"license_url":license_url,"source_original_sha1":info["sha1"],"archived_sha256":sha256,"size":list(im.size),"photo_role":"UNREVIEWED — inspect whether actual rooted crown, basal leaves, true ligule or attached flowering architecture"})
    except Exception as exc:
       report["held"].append({"id":id,"source":page,"reason":str(exc)})
(dest/"manifest.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({"added":len(report["added"]),"held":report["held"]}))
