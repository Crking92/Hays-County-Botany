#!/usr/bin/env python3
"""Archive exactly two Jim Conrad 2012 Uvalde Bouteloua pectinata images (CC0).
Preserve existing creator/license/photo evidence and concurrent species JSON edits.
No guessed microscopic anatomy or annotations.
"""
import base64, hashlib, io, json, os, pathlib, time, urllib.parse
import requests
from PIL import Image, ImageOps

repo=os.environ["GITHUB_REPOSITORY"]
token=os.environ["GITHUB_TOKEN"]
branch=os.environ.get("GITHUB_REF_NAME","main")
page="https://www.backyardnature.net/n/h/tallgram.htm"
base="content/taxa/Poaceae/Bouteloua/bouteloua-pectinata/"
card=base+"species.json"
approved=[
 ("https://www.backyardnature.net/n/12/121014bu.jpg",
  "jim-conrad-uvalde-tallgram-habit-cc0.jpg",
  "Uvalde limestone prairie habit with true rooted-in-soil tuft and very tall culms; actual belowground crown and root anatomy hidden."),
 ("https://www.backyardnature.net/n/12/121014bv.jpg",
  "jim-conrad-uvalde-tallgram-comb-tip-cc0.jpg",
  "Uvalde source-described eyebrow-shaped flowering branch, pointed naked distal rachis projection and visible glume/spikelet hairs; no 1-mm scale or dissected parts.")
]
sess=requests.Session()
sess.headers.update({"User-Agent":"HaysBotany-Lane1-Authorized-Source/1.0"})
res=sess.get(page,timeout=40)
res.raise_for_status()
s=res.text.lower()
if "bouteloua pectinata" not in s or "jim conrad" not in s:
    raise SystemExit("Exact source page and named photographer missing")
if "creativecommons.org/publicdomain/zero/1.0" not in s:
    raise SystemExit("Exact source page CC0 dedication missing")
for url,_,_ in approved:
    if pathlib.PurePosixPath(urllib.parse.urlparse(url).path).name not in s:
        raise SystemExit("Source page is not linking the pinned image "+url)
sess.headers.update({
 "Authorization":"Bearer "+token,"Accept":"application/vnd.github+json",
 "X-GitHub-Api-Version":"2022-11-28"})
api=f"https://api.github.com/repos/{repo}/contents/"
def get(p):
    r=sess.get(api+urllib.parse.quote(p,safe="/"),params={"ref":branch},timeout=35)
    if r.status_code==404:return None
    r.raise_for_status()
    return r.json()
def put(p,raw,sha,msg):
    form={"message":msg,"branch":branch,"content":base64.b64encode(raw).decode()}
    if sha:form["sha"]=sha
    r=sess.put(api+urllib.parse.quote(p,safe="/"),json=form,timeout=90)
    if r.status_code in (409,422):return False
    r.raise_for_status()
    return True
for url,name,description in approved:
    image=sess.get(url,timeout=60)
    image.raise_for_status()
    if urllib.parse.urlparse(image.url).hostname not in ("www.backyardnature.net","backyardnature.net"):
        raise SystemExit("Unexpected redirect")
    if len(image.content)<8000 or len(image.content)>12000000 or not image.content.startswith(bytes.fromhex("ffd8")):
        raise SystemExit("Source is not plausible JPG")
    im=Image.open(io.BytesIO(image.content))
    im.verify()
    im=Image.open(io.BytesIO(image.content))
    im=ImageOps.exif_transpose(im).convert("RGB")
    if min(im.size)<250:
        raise SystemExit("Source quality too small")
    buf=io.BytesIO()
    im.save(buf,"JPEG",quality=90,optimize=True)
    data=buf.getvalue()
    digest=hashlib.sha256(data).hexdigest()
    dest=base+"images/"+name
    exists=get(dest)
    if not exists:
        if not put(dest,data,None,"Lane 1 archive exact Jim Conrad CC0 Uvalde tall grama "+name):
            exists=get(dest)
            if not exists or exists.get("size")!=len(data):
                raise SystemExit("Concurrent conflicting photo upload; manual review needed")
    elif exists.get("size")!=len(data):
        raise SystemExit("Existing image name has different bytes; preserving")
    photo={"file":"images/"+name,"role":description,"creator":"Jim Conrad",
           "license":"CC0 1.0 — author-page linked public-domain dedication",
           "license_url":"https://creativecommons.org/publicdomain/zero/1.0/",
           "source_page":page,"source_original":url,
           "source_locality":"northern Uvalde County, Edwards Plateau, Texas",
           "public_reuse":"yes — original creator CC0 source page",
           "image_sha256":digest,"image_dimensions":list(im.size),
           "modifications":"Re-encoded JPEG RGB after EXIF transpose; all GPS/EXIF stripped; no morphology changed",
           "photo_review":"Source-authenticated macro/habit only. Exact species ID from Jim Conrad, no herbarium voucher; gross pixels require reviewer arrow inspection."}
    panel={"label":"UVALDE CC0 REFERENCE — "+("habitat and elevated culms" if "habit" in name else "long eyebrow and naked distal rachis"),
           "scientific_name":"Bouteloua pectinata","image_url":dest,"image_fit":"contain",
           "creator":"Jim Conrad","license":"CC0 1.0","license_url":photo["license_url"],
           "source_page":page,"source_original":url,"image_role":description,
           "caption":description+" Source-identified Texas photograph; fine hair-fringe ligule and actual roots are not demonstrated here.",
           "why_it_matters":"Texas source view helps the crew distinguish a tall-grana comb/field posture from ordinary blue or hairy grama; verify full flowering stem before species call.",
           "markers":[],"photo_status":"Actual local JPEG archived under CC0 after source-page check. No pixel-specific arrows installed yet; local voucher and mobile display QA pending."}
    for attempt in range(6):
        c=get(card)
        if not c:raise SystemExit("Canonical species missing")
        d=json.loads(base64.b64decode(c["content"]))
        images=d.setdefault("images",[])
        gallery=d.setdefault("visual_comparison",{}).setdefault("items",[])
        matches=[q for q in images if q.get("file")==photo["file"]]
        rows=[q for q in gallery if q.get("image_url")==dest]
        if len(matches)==len(rows)==1:
            print("ALREADY_INSTALLED",dest)
            break
        if matches or rows:
            raise SystemExit("Partial/duplicate photo metadata; preserving")
        images.append(photo)
        pos=next((i for i,q in enumerate(gallery) if q.get("scientific_name")!="Bouteloua pectinata"),len(gallery))
        gallery.insert(pos,panel)
        d.setdefault("curation_status",{})["photo_files_present"]=sum(
          str(x.get("file","")).startswith("images/") for x in images)
        d["curation_status"]["lane1_tallgram_jim_conrad_cc0_20261026"]="PHYSICALLY_ARCHIVED_GROSS_STRUCTURES_PIXEL_ARROWS_PENDING"
        raw=(json.dumps(d,ensure_ascii=False,indent=2)+"\n").encode()
        if put(card,raw,c["sha"],"Lane 1 show Jim Conrad CC0 Uvalde tall grama "+name):
            print("ARCHIVED_AND_GALLERY",dest,"bytes",len(data),"sha256",digest)
            break
        time.sleep(attempt+1)
    else:raise SystemExit("Six concurrent species edits; image retained but gallery needs follow-up")
