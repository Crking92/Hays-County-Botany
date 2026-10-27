#!/usr/bin/env python3
"""Exact Matt Lavin Bouteloua gracilis lower leaf collar photo.
CC BY-SA 2.0 and Grand Canyon determination verified from individual Commons file.
Conservative anatomy: hairy lower collar/sheath region visible, true free ligule edge not certified.
"""
import base64, hashlib, html, io, json, os, re, time, urllib.parse
import requests
from PIL import Image, ImageOps
REPO=os.environ["GITHUB_REPOSITORY"];TOKEN=os.environ["GITHUB_TOKEN"]
BRANCH=os.environ.get("GITHUB_REF_NAME","main")
BASE="content/taxa/Poaceae/Bouteloua/bouteloua-gracilis/"
CARD=BASE+"species.json"
NAME="matt-lavin-blue-grama-hairy-collar-sheath-by-sa2.jpg"
REL="images/"+NAME
FILE=BASE+REL
PAGE="https://commons.wikimedia.org/wiki/File:Bouteloua_gracilis_(6243884823).jpg"
ORIGINAL="https://upload.wikimedia.org/wikipedia/commons/b/b3/Bouteloua_gracilis_%286243884823%29.jpg"
LIC="https://creativecommons.org/licenses/by-sa/2.0/"
s=requests.Session()
s.headers.update({"User-Agent":"HaysCountyBotany-ExactLicensedBlueGramaAnatomyArchive/1.0"})
p=s.get(PAGE,timeout=40);p.raise_for_status()
t=" ".join(html.unescape(re.sub("<[^>]*>"," ",p.text)).lower().split())
for phrase in ("bouteloua gracilis","matt lavin","6243884823","ligule and collar regions","attribution-share alike 2.0 generic"):
    if phrase not in t:raise SystemExit("Exact taxon creator/license/structure page check failed: "+phrase)
if "flickrreviewr" not in t and "file upload bot" not in t:raise SystemExit("Individual photo license review absent")
im=None
original_used=""
urls=[ORIGINAL]
flickr=s.get("https://www.flickr.com/photos/plant_diversity/6243884823",timeout=40)
if flickr.status_code==200:
    for pat in (r'<meta[^>]+property=["\x27]og:image["\x27][^>]+content=["\x27]([^"\x27]+)',r'https://live\.staticflickr\.com/[^"\x27\s<\\]+\.jpg'):
        m=re.search(pat,flickr.text,re.I)
        if m:
            url=html.unescape(m.group(1) if m.lastindex else m.group(0)).replace("\\/","/")
            if urllib.parse.urlparse(url).hostname=="live.staticflickr.com":urls.append(url);break
for url in urls:
    try:
        x=s.get(url,timeout=100,allow_redirects=True)
        if x.status_code in (403,429,502,503,504):
            print("EXTERNAL_IMAGE_CDN_BLOCKED",x.status_code)
            continue
        x.raise_for_status()
        u=urllib.parse.urlparse(x.url)
        if u.scheme!="https" or u.hostname not in ("upload.wikimedia.org","live.staticflickr.com"):
            raise SystemExit("Unexpected source image redirect")
        if not x.content.startswith(b"\xff\xd8") or not 100000<len(x.content)<15000000:
            continue
        raw=Image.open(io.BytesIO(x.content));raw.verify()
        im=ImageOps.exif_transpose(Image.open(io.BytesIO(x.content))).convert("RGB")
        if min(im.size)<1000:continue
        original_used=x.url
        break
    except (requests.RequestException,OSError) as e:
        print("SOURCE_ORIGINAL_NOT_AVAILABLE",str(e)[:110])
if im is None:raise SystemExit("No exact licensed original available; archive not changed")
im.thumbnail((2800,2800),Image.Resampling.LANCZOS)
out=io.BytesIO();im.save(out,"JPEG",quality=89,optimize=True)
raw=out.getvalue()
digest=hashlib.sha256(raw).hexdigest()
print("REAL_IMAGE_SANITIZED",len(raw),im.size,digest)
s.headers.update({"Authorization":"Bearer "+TOKEN,"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"})
ROOT="https://api.github.com/repos/"+REPO+"/contents/"
def get(path):
    q=s.get(ROOT+urllib.parse.quote(path,safe="/"),params={"ref":BRANCH},timeout=45)
    if q.status_code==404:return None
    q.raise_for_status();return q.json()
def put(path,b,sha,msg):
    payload={"content":base64.b64encode(b).decode(),"message":msg,"branch":BRANCH}
    if sha:payload["sha"]=sha
    q=s.put(ROOT+urllib.parse.quote(path,safe="/"),json=payload,timeout=95)
    if q.status_code in (409,422):return False
    q.raise_for_status();return True
for attempt in range(7):
    prev=get(FILE)
    if prev:
        if prev.get("size")!=len(raw):raise SystemExit("Previously archived file different, don't overwrite")
        break
    if put(FILE,raw,None,"Lane 1 archive CC BY-SA blue grama exact collar/sheath photo"):
        break
    time.sleep(attempt+1)
else:raise SystemExit("Seven branch conflicts, no file overwritten")
record={
  "file":REL,"role":"Actual hairy sheath, leafy culms and lower collar region of source-identified Bouteloua gracilis (Grand Canyon). The true free inner ligule edge and millimeter measurement are NOT clearly resolved.",
  "creator":"Matt Lavin","license":"CC BY-SA 2.0","license_url":LIC,
  "source_page":PAGE,"source_original":original_used,
  "source_taxon_name":"Bouteloua gracilis","source_photo_id":"6243884823",
  "source_locality":"Grand Canyon National Park, Arizona; NOT Hays County",
  "public_reuse":"Individual Commons Flickr-reviewed CC BY-SA 2.0 with full credit and ShareAlike/changes",
  "modifications":"Original photo GPS/EXIF removed; JPEG RGB re-encoded, resized longest side 2800 pixels; no subject crop",
  "image_dimensions":list(im.size),"image_sha256":digest,
  "photo_review":"Image visually reviewed as lower leaf/sheath/collar area, slender hairs visible at multiple growth points. True free 0.5-mm ligule edge is unresolved; no arrow placed."}
panel={
  "label":"BLUE GRAMA — real hairy collar and sheath region (true ligule edge still unresolved)",
  "scientific_name":"Bouteloua gracilis","image_url":FILE,"image_fit":"contain",
  "creator":"Matt Lavin","license":"CC BY-SA 2.0","license_url":LIC,"source_page":PAGE,"source_original":original_used,
  "image_role":record["role"],
  "caption":"Blue grama at Grand Canyon National Park, photographed by Matt Lavin. Actual narrow blades and hairy sheath/collar area are visible; the INNER free edge of the ligule is not isolated or measured in this field image. Do not draw an arrow directly to an assumed ligule; photograph the blade–sheath junction straight on for confirmation.",
  "why_it_matters":"First distinct licensed collar/sheath field close-up on blue grama's card, rather than an additional eyebrow seedhead.",
  "markers":[],"photo_status":"Source species and CC BY-SA 2.0 individually checked, EXIF-clean local JPEG; true ligule still an open photo gap, mobile review pending."}
for attempt in range(7):
    existing=get(CARD)
    if existing is None:raise SystemExit("Missing blue grama card")
    d=json.loads(base64.b64decode(existing["content"]))
    if d.get("id")!="bouteloua-gracilis":raise SystemExit("Wrong taxon")
    a=d.setdefault("images",[]);b=d.setdefault("visual_comparison",{}).setdefault("items",[])
    aa=[x for x in a if x.get("file")==REL];bb=[x for x in b if x.get("image_url")==FILE]
    if len(aa)==len(bb)==1:print("ALREADY_INSTALLED");break
    if aa or bb:raise SystemExit("Partial/duplicate record, preserve")
    a.append(record)
    i=next((i for i,x in enumerate(b) if x.get("scientific_name")!="Bouteloua gracilis"),len(b))
    b.insert(i,panel)
    d.setdefault("curation_status",{})["photo_files_present"]=sum(str(z.get("file","")).startswith("images/") for z in a)
    d["curation_status"]["lane1_blue_grama_hairy_collar_20261027"]="REAL_LOCAL_CC_BY_SA_COLLAR_AREA_PHOTO_LIGULE_EDGE_UNVERIFIED"
    rawcard=(json.dumps(d,ensure_ascii=False,indent=2)+"\n").encode()
    if put(CARD,rawcard,existing["sha"],"Lane 1 publish real licensed blue grama collar and sheath photograph"):
        print("BLUE_GRAMA_LOCAL_COLLAR_GALLERY_UPDATED",len(a),len(b))
        break
    time.sleep(attempt+1)
else:raise SystemExit("Concurrent edits exhausted; JPEG archived, gallery needs review")
