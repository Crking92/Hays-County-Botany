#!/usr/bin/env python3
"""Lane 1 source-and-rights-gated P. capillare external mirror plus genuine collar detail.
Never infer a TRUE visible ligule or add arrows from page text; accurate image-level
review required. Preserve other lane and automation edits; archive GPS-free JPEG.
"""
import base64, hashlib, html, io, json, os, re, time, urllib.parse
import requests
from PIL import Image,ImageOps
REPO=os.environ["GITHUB_REPOSITORY"]; TOKEN=os.environ["GITHUB_TOKEN"]
BRANCH=os.environ.get("GITHUB_REF_NAME","main")
BASE="content/taxa/Poaceae/Panicum/panicum-capillare/"
CARD=BASE+"species.json"
SOURCES=[
 dict(id="3813114550",filename="matt-lavin-witchgrass-complete-diffuse-panicle-by-sa2.jpg",
 creator="Matt Lavin",license="CC BY-SA 2.0",lic="https://creativecommons.org/licenses/by-sa/2.0/",
 host="plant_diversity",kind="mirror",
 role="Original same-species complete diffuse witchgrass panicle on flowering plant; NOT microscope florets"),
 dict(id="7185668229",filename="harry-rose-witchgrass-foliage-sheath-reference-by2.jpg",
 creator="Harry Rose",license="CC BY 2.0",lic="https://creativecommons.org/licenses/by/2.0/",
 host="macleaygrassman",kind="mirror",
 role="Real P. capillare field leaf/sheath/culm view, Australian photograph; collar itself NOT certified"),
 dict(id="3812305589",filename="matt-lavin-witchgrass-sheath-collar-ligule-region-by-sa2.jpg",
 creator="Matt Lavin",license="CC BY-SA 2.0",lic="https://creativecommons.org/licenses/by-sa/2.0/",
 host="plant_diversity",kind="new",
 role="Source-labelled true P. capillare sheath, collar, node and often bulbous-based hairs; photographer describes fringe ligule but FREE LIGULE EDGE MUST BE PIXEL CONFIRMED"),
]
s=requests.Session()
s.headers.update({"User-Agent":"HaysCountyBotany-ExactGrassLicensedImageMirror/1.0"})
def getsource(x):
    title=f"Panicum capillare ({x['id']}).jpg"
    page="https://commons.wikimedia.org/wiki/File:"+urllib.parse.quote(title,safe="()")
    q=s.get(page,timeout=45);q.raise_for_status()
    visible=" ".join(html.unescape(re.sub(r"<[^>]*>"," ",q.text)).lower().split())
    for word in ("panicum capillare",x["creator"].lower(),x["id"],x["lic"].split("creativecommons.org/",1)[-1].rstrip("/"),"flickreviewr"):
        if word not in visible and word not in q.text.lower():
            raise SystemExit("Exact individual Commons CC source mismatch "+x["id"]+" "+word)
    if x["creator"]=="Harry Rose" and "cc-by-2.0" not in visible:
        raise SystemExit("Harry Rose original review not CC BY 2.0")
    if x["creator"]=="Matt Lavin" and "cc-by-sa-2.0" not in visible:
        raise SystemExit("Matt Lavin original review not CC BY-SA 2.0")
    x["page"]=page
    imageurl="https://commons.wikimedia.org/wiki/Special:Redirect/file/"+urllib.parse.quote(title)
    attempt_urls=[imageurl]
    original=None
    im=None
    source_page=s.get("https://www.flickr.com/photos/"+x["host"]+"/"+x["id"]+"/",timeout=35)
    if source_page.status_code==200 and x["id"] in source_page.text:
        patterns=[
          r'<meta[^>]+property=["\x27]og:image["\x27][^>]+content=["\x27]([^"\x27]+)',
          r'<meta[^>]+content=["\x27]([^"\x27]+)["\x27][^>]+property=["\x27]og:image',
          r'https://live\.staticflickr\.com/[^"\x27<\s\\]+\.jpg'
        ]
        for pat in patterns:
            m=re.search(pat,source_page.text,re.I)
            if m:
                candidate=html.unescape(m.group(1) if m.lastindex else m.group(0)).replace("\\/","/")
                if urllib.parse.urlparse(candidate).hostname=="live.staticflickr.com":
                    attempt_urls.append(candidate);break
    for url in attempt_urls:
        try:
            response=s.get(url,timeout=80,allow_redirects=True)
            if response.status_code in (403,429,500,502,503,504):
                print("SOURCE_CDN_RATE_LIMIT",x["id"],response.status_code)
                continue
            response.raise_for_status()
            parsed=urllib.parse.urlparse(response.url)
            if parsed.scheme!="https" or parsed.hostname not in ("upload.wikimedia.org","live.staticflickr.com"):
                raise SystemExit("Unapproved photo redirect host")
            if not response.content.startswith(b"\xff\xd8") or not 20000<len(response.content)<18000000:
                continue
            test=Image.open(io.BytesIO(response.content));test.verify()
            im=ImageOps.exif_transpose(Image.open(io.BytesIO(response.content))).convert("RGB")
            if min(im.size)<650:continue
            original=response.url;break
        except (requests.RequestException,OSError) as exc:
            print("PHOTO_DOWNLOAD_RETRY_OTHER_HOST",x["id"],str(exc)[:120])
    if im is None:
        raise SystemExit("Verified licensed photo unavailable on both Commons and source Flickr CDN "+x["id"])
    im.thumbnail((2600,2600),Image.Resampling.LANCZOS)
    out=io.BytesIO()
    im.save(out,"JPEG",quality=89,optimize=True)
    x["raw"]=out.getvalue()
    x["bytes_hash"]=hashlib.sha256(x["raw"]).hexdigest()
    x["size"]=list(im.size)
    x["original"]=original
    x["path"]=BASE+"images/"+x["filename"]
    print("VERIFIED_ORIGINAL_AND_LICENSE",x["id"],x["size"],len(x["raw"]))
for x in SOURCES:
    getsource(x)
s.headers.update({"Authorization":"Bearer "+TOKEN,"Accept":"application/vnd.github+json",
                  "X-GitHub-Api-Version":"2022-11-28"})
ROOT="https://api.github.com/repos/"+REPO+"/contents/"
def get(path):
    q=s.get(ROOT+urllib.parse.quote(path,safe="/"),params={"ref":BRANCH},timeout=45)
    if q.status_code==404:return None
    q.raise_for_status();return q.json()
def put(path,blob,sha,message):
    data={"message":message,"branch":BRANCH,"content":base64.b64encode(blob).decode()}
    if sha:data["sha"]=sha
    q=s.put(ROOT+urllib.parse.quote(path,safe="/"),json=data,timeout=100)
    if q.status_code in (409,422):return False
    q.raise_for_status();return True
for x in SOURCES:
    for write_attempt in range(7):
        prior=get(x["path"])
        if prior:
            if prior.get("size") != len(x["raw"]):
                raise SystemExit("Existing same-name photo differs; stop to preserve existing files")
            print("PHOTO_ALREADY_ARCHIVED",x["id"])
            break
        if put(x["path"],x["raw"],None,"Lane 1 permanently archive "+x["id"]+" witchgrass CC anatomical reference"):
            print("PHOTO_ARCHIVED",x["id"])
            break
        # Other lanes/automations commit to main during this run. GitHub's
        # contents API can reject a perfectly valid photo upload when the
        # branch changes. Never force or overwrite; refetch/retry safely.
        time.sleep(1+write_attempt)
    else:
        raise SystemExit("Concurrent image path conflict after seven safe retries "+x["id"])
def photo(x):
    return {
      "file":"images/"+x["filename"],"role":x["role"],
      "creator":x["creator"],"license":x["license"],"license_url":x["lic"],
      "source_page":x["page"],"source_original":x["original"],
      "source_photo_id":x["id"],"source_taxon_name":"Panicum capillare",
      "source_region":"Montana, USA" if x["creator"]=="Matt Lavin" else "Australia (same species; NOT local Texas voucher)",
      "public_reuse":"yes, individual photo CC and photographer confirmed by Commons and Flickr photo review",
      "modifications":"Re-encoded JPEG, EXIF/GPS removed, scaled to <=2600 px longest side; ShareAlike applies to transformations where applicable",
      "image_sha256":x["bytes_hash"],"image_dimensions":x["size"],
      "photo_review":"Exact species and photo license/source confirmed. No new ligule arrow: actual free hair-fringe edge is NOT yet independently pixel-certified."
    }
def panel(x):
    return {
      "label":"SOURCE-VERIFIED WITCHGRASS — sheath, collar and node hair region (ligule still needs visual confirmation)",
      "scientific_name":"Panicum capillare","image_url":x["path"],"image_fit":"contain",
      "image_role":x["role"],
      "caption":"Matt Lavin's actual Panicum capillare photograph documents hairy leaf-sheath, nodes, and the collar region. The photographer states that the ligule is a fringe of hairs; do not confuse the surface sheath hairs with the true inner blade–sheath ligule, and do not claim a measured ligule from this photograph without verified pixels. Montana, not Texas.",
      "why_it_matters":"A distinct licensed real-species close-up helps the crew assess where the ligule and swollen hair bases should be examined. Exact free ligule fringe still requires close pixel review.",
      "creator":x["creator"],"license":x["license"],"license_url":x["lic"],
      "source_page":x["page"],"source_original":x["original"],
      "markers":[],"photo_status":"Physical source-and-license-verified JPEG; true free ligule edge and any arrow still PENDING real-pixel inspection."
    }
for attempt in range(7):
    obj=get(CARD)
    if obj is None:raise SystemExit("Canonical witchgrass card absent")
    d=json.loads(base64.b64decode(obj["content"]))
    if d.get("id")!="panicum-capillare":raise SystemExit("Wrong species")
    images=d.setdefault("images",[])
    gallery=d.setdefault("visual_comparison",{}).setdefault("items",[])
    changed=False
    for x in SOURCES:
        if x["kind"]=="mirror":
            oldrecords=[z for z in images if z.get("source_page")==x["page"]]
            oldpanels=[z for z in gallery if z.get("source_page")==x["page"]]
            if len(oldrecords)!=1 or len(oldpanels)!=1:raise SystemExit("Expected exactly one old source-and-panel, preserve for review "+x["id"])
            expected=oldrecords[0].get("file","")
            if expected.startswith("images/"):
                if expected=="images/"+x["filename"] and oldpanels[0].get("image_url")==x["path"]:continue
                raise SystemExit("Old reference independently archived, don't overwrite "+x["id"])
            oldrecords[0].update(photo(x))
            oldpanels[0]["image_url"]=x["path"]
            oldpanels[0]["source_original"]=x["original"]
            oldpanels[0]["license_url"]=x["lic"]
            oldpanels[0]["photo_status"]="Mirrored original source photo physically under images/, no new anatomy arrows; pixel anatomy QA pending"
            changed=True
        else:
            a=[z for z in images if z.get("source_page")==x["page"]]
            b=[z for z in gallery if z.get("source_page")==x["page"]]
            if len(a)==len(b)==1:continue
            if a or b:raise SystemExit("Half-installed different photo")
            images.append(photo(x))
            idx=next((i for i,z in enumerate(gallery) if z.get("scientific_name")!="Panicum capillare"),len(gallery))
            gallery.insert(idx,panel(x))
            changed=True
    if not changed:
        print("ALREADY_MIRRORED_AND_ADDED")
        break
    d.setdefault("curation_status",{})["photo_files_present"]=sum(str(x.get("file","")).startswith("images/") for x in images)
    d["curation_status"]["lane1_20261027_source_verified_witchgrass_3"]="3_LICENSED_LOCAL_MACROS_TWO_PREVIOUS_REMOTE_GALLERY_PANELS_LOCAL_PLUS_ONE_NEW_SHEATH_COLLAR_PENDING_TRUE_LIGULE"
    body=(json.dumps(d,indent=2,ensure_ascii=False)+"\n").encode()
    if put(CARD,body,obj["sha"],"Lane 1 permanently mirror two witchgrass panels and add genuine licensed collar photo"):
        print("ARCHIVED_3_WITCHGRASS_PHOTOS_AND_RELINKED_2_EXISTING_PANELS",len(images),len(gallery))
        break
    time.sleep(attempt+1)
else:raise SystemExit("Seven concurrent edits, photos safely archived; gallery review needed")
