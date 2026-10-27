#!/usr/bin/env python3
"""Lane 1 Secale cereale true ligule/sheath + auricle originals from individual Commons CC BY-SA 4.0 pages.
Two genuine author-documented images with built-in physical 3mm/10mm scale bars, EXIF removed.
"""
import base64, hashlib, html, io, json, os, re, time
from urllib.parse import quote,urlparse
import requests
from PIL import Image,ImageOps
R=os.environ["GITHUB_REPOSITORY"];TOK=os.environ["GITHUB_TOKEN"];BR=os.environ.get("GITHUB_REF_NAME","main")
BASE="content/taxa/Poaceae/Secale/secale-cereale/"
CARD=BASE+"species.json"
LIC="https://creativecommons.org/licenses/by-sa/4.0/"
photos=[
{"id":"sl13","file":"stefan-lefnaer-rye-true-membranous-ligule-3mm-scale-by-sa4.jpg","role":"Actual rye inner ligule at blade/sheath junction, closely enlarged and accompanied by photographed 3mm scale. Short membranous free ligule margin visible, with rolled leaf collar; not a hair-fringe ligule.","label":"TRUE RYE LIGULE — tiny membranous blade–sheath flap with 3-mm scale (Stefan.lefnaer)","caption":"Real Secale cereale inner collar viewed at macro scale. The whitish/torn-looking membrane clasping the culm is the short TRUE ligule. Do not confuse it with the curved sheath margin. The photographer includes a 3 mm scale bar."},
{"id":"sl11","file":"stefan-lefnaer-rye-four-collar-views-10mm-scale-by-sa4.jpg","role":"Four original side-on photographs of the same species' rye leaf blade/sheath junction with actual comparative 10mm scale bar, showing sheath edge, collar/auricles at several angles.","label":"RYE COLLAR SERIES — four actual sheath/blade junction angles, 10-mm scale (Stefan.lefnaer)","caption":"Four independent original views within the photographer's comparative rye collar image. Actual membrane and folded blade/sheath are visible from different side-on angles. Physical 10 mm bar at bottom; 2022 Vienna crop field source, not Texas."}
]
s=requests.Session();s.headers.update({"User-Agent":"Hays-Botany-Exact-Rye-Ligule-License-Verifier/1.0"})
for p in photos:
    name="Secale_cereale_"+p["id"]+".jpg"
    page="https://commons.wikimedia.org/wiki/File:"+name
    src=s.get(page,timeout=50);src.raise_for_status()
    text=" ".join(html.unescape(re.sub(r"<[^>]+>"," ",src.text)).lower().split())
    for needed in ("secale cereale","stefan.lefnaer","leaf sheath and ligule","attribution-share alike 4.0 international","own work"):
        if needed not in text:
            if needed=="leaf sheath and ligule" and "stängel mit blattscheide und ligula" in text:continue
            raise SystemExit("Photo-by-photo source/license/subject mismatch "+p["id"]+" "+needed)
    choices=[
        ("https://commons.wikimedia.org/wiki/Special:Redirect/file/"+quote(name),("upload.wikimedia.org","thumb.wikimedia.org")),
        ("https://thumb.wikimedia.org/wikipedia/commons/thumb/"+("a/a9" if p["id"]=="sl13" else "3/39")+"/"+name+"/"+("1280px-" if p["id"]=="sl13" else "960px-")+name,("thumb.wikimedia.org",))
    ]
    im=None;used=""
    for url,allowed in choices:
        try:
            z=s.get(url,timeout=100,allow_redirects=True)
            if z.status_code in (403,404,429,502,503,504):
                print("CDN_IMAGE_UNAVAILABLE",p["id"],z.status_code);continue
            z.raise_for_status()
            dom=urlparse(z.url)
            if dom.scheme!="https" or dom.hostname not in ("upload.wikimedia.org","thumb.wikimedia.org"):continue
            if not z.content.startswith(b"\xff\xd8") or len(z.content)<100000:continue
            test=Image.open(io.BytesIO(z.content));test.verify()
            temp=ImageOps.exif_transpose(Image.open(io.BytesIO(z.content))).convert("RGB")
            if min(temp.size)<750:continue
            im=temp;used=z.url;break
        except (requests.RequestException,OSError) as ex:
            print("IMAGE_FETCH_ERROR",p["id"],str(ex)[:180])
    if im is None:raise SystemExit("Exact openly licensed rye ligule original not downloaded "+p["id"])
    im.thumbnail((2800,2800),Image.Resampling.LANCZOS)
    buff=io.BytesIO();im.save(buff,"JPEG",quality=91,optimize=True)
    p["data"]=buff.getvalue();p["dims"]=list(im.size);p["source"]=page;p["original"]=used
    p["sha256"]=hashlib.sha256(p["data"]).hexdigest();p["relative"]="images/"+p["file"];p["path"]=BASE+p["relative"]
    print("EXACT_RYE_LIGULE_LICENSE_AND_PIXELS_OK",p["id"],p["dims"],len(p["data"]))
s.headers.update({"Authorization":"Bearer "+TOK,"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"})
ROOT="https://api.github.com/repos/"+R+"/contents/"
def get(path):
    q=s.get(ROOT+quote(path,safe="/"),params={"ref":BR},timeout=45)
    if q.status_code==404:return None
    q.raise_for_status();return q.json()
def put(path,data,sha,msg):
    d={"message":msg,"branch":BR,"content":base64.b64encode(data).decode()}
    if sha:d["sha"]=sha
    q=s.put(ROOT+quote(path,safe="/"),json=d,timeout=90)
    if q.status_code in (409,422):return False
    q.raise_for_status();return True
for p in photos:
    for i in range(8):
        cur=get(p["path"])
        if cur:
            if cur.get("size")!=len(p["data"]):raise SystemExit("Previously archived photo differed, never overwrite")
            break
        if put(p["path"],p["data"],None,"Lane 1 archive genuine scaled true rye ligule "+p["id"]+" CC BY-SA 4.0"):break
        time.sleep(i+1)
    else:raise SystemExit("Concurrent file upload conflict, preserve originals")
for i in range(9):
    old=get(CARD)
    if not old:raise SystemExit("Rye canonical card missing")
    d=json.loads(base64.b64decode(old["content"]))
    if d.get("id")!="secale-cereale":raise SystemExit("Wrong canonical rye")
    im=d.setdefault("images",[])
    gal=d.setdefault("visual_comparison",{}).setdefault("items",[])
    changed=False
    for p in photos:
        a=[z for z in im if z.get("file")==p["relative"]]
        b=[z for z in gal if z.get("image_url")==p["path"]]
        if len(a)==len(b)==1:continue
        if a or b:raise SystemExit("Inconsistent existing record, stop safely")
        im.append({
          "file":p["relative"],"role":p["role"],"creator":"Stefan.lefnaer",
          "license":"CC BY-SA 4.0","license_url":LIC,"source_page":p["source"],
          "source_original":p["original"],"source_taxon_name":"Secale cereale",
          "source_locality":"Grellgasse rye field, Vienna, Austria; not Texas",
          "public_reuse":"YES; photographer uploaded personally under CC BY-SA 4.0, changes and attribution required",
          "modifications":"Original image RGB JPEG recompression, scale bar preserved, EXIF/GPS removed, resized longest side 2800 pixels, no false anatomical parts",
          "image_dimensions":p["dims"],"image_sha256":p["sha256"],
          "photo_review":"Real macro source-pixel verification: free membranous ligule at proper collar and physical metric bar pictured; own-work CC license checked individually."})
        gal.insert(0,{
          "label":p["label"],"scientific_name":"Secale cereale","image_url":p["path"],"image_fit":"contain",
          "creator":"Stefan.lefnaer","license":"CC BY-SA 4.0","license_url":LIC,
          "source_page":p["source"],"source_original":p["original"],
          "image_role":p["role"],"caption":p["caption"],
          "why_it_matters":"Actual species-specific photograph of the inner sheath–blade junction with metric scale, resolves a genuine six-role identification gap.",
          "markers":[],"photo_status":"Image-pixel true ligule and metric scale independently observed in source preview; no new arrows until full photo/mobile pixel QA."
        })
        changed=True
    if not changed:print("ALREADY_INSTALLED");break
    d.setdefault("curation_status",{})["photo_metadata_count"]=len(im)
    d["curation_status"]["photo_files_present"]=sum(str(z.get("file","")).startswith("images/") for z in im)
    d["curation_status"]["lane1_scaled_true_rye_ligule_20261027"]="TWO_LICENSED_SCALED_LIGULE_SHEATH_ANATOMY_ORIGINALS_ARCHIVED_NO_UNVERIFIED_ARROWS"
    if put(CARD,(json.dumps(d,indent=2,ensure_ascii=False)+"\n").encode(),old["sha"],"Lane 1 add true scaled rye ligule and blade/sheath CC BY-SA photo anatomy"):
        print("RYE_TWO_TRUE_LIGULE_PANELS_COMMITTED",len(im),len(gal));break
    time.sleep(i+1)
else:raise SystemExit("Canonical edits concurrent; source photos archived but link verification needed")
