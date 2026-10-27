#!/usr/bin/env python3
"""Lane 1 physically mirror exactly licensed existing Commons Munroa pulchella panels.
Original names Dasyochloa pulchella = same accepted taxon. Preserve credits and arrows.
No claims of unphotographed true ligule, glume lemma or root structure.
"""
import base64,hashlib,html,io,json,os,re,time
from urllib.parse import quote,urlparse
import requests
from PIL import Image,ImageOps
REPO=os.environ["GITHUB_REPOSITORY"];TOKEN=os.environ["GITHUB_TOKEN"];BRANCH=os.environ.get("GITHUB_REF_NAME","main")
BASE="content/taxa/Poaceae/Munroa/munroa-pulchella/"
CARD=BASE+"species.json"
S=[
{"id":"14751775","title":"Dasyochloa_pulchella_14751775.jpg","filename":"alex-abair-fluffgrass-woolly-nested-flowering-ccby4.jpg","creator":"Alex Abair","license":"CC BY 4.0","license_url":"https://creativecommons.org/licenses/by/4.0/","role":"True species synonym-labelled leafy flowering woolly cluster in field, not dissected spikelets","backup":["https://inaturalist-open-data.s3.amazonaws.com/photos/14751775/original.jpg","https://inaturalist-open-data.s3.amazonaws.com/photos/14751775/original.jpeg"]},
{"id":"45895144765","title":"Fluffgrass,_Dasyochloa_pulchella_(45895144765).jpg","filename":"jim-morefield-fluffgrass-natural-flowering-habit-ccbysa2.jpg","creator":"Jim Morefield","license":"CC BY-SA 2.0","license_url":"https://creativecommons.org/licenses/by-sa/2.0/","role":"Source-verified California fluffgrass flowering in rocky habitat: real field growth form and fluffy inflorescence, no inner ligule macro","backup":[]}
]
s=requests.Session();s.headers.update({"User-Agent":"HaysBotany-IndividualCommonsOriginalTaxonLicenseArchiver/1.0"})
def fetch(x):
    x["page"]="https://commons.wikimedia.org/wiki/File:"+x["title"]
    p=s.get(x["page"],timeout=50);p.raise_for_status()
    plain=" ".join(html.unescape(re.sub(r"<[^>]*>"," ",p.text)).lower().split())
    for term in ("dasyochloa pulchella",x["creator"].lower(),x["id"],"creativecommons.org/licenses/"+("by-sa/2.0" if "by-sa" in x["license_url"] else "by/4.0")):
        if term not in p.text.lower() and term not in plain:
            raise SystemExit("Source rights/taxon/author check not met "+x["id"]+" "+term)
    if x["id"]=="14751775" and "inaturalistreview" not in p.text.lower():
        raise SystemExit("iNaturalist CC author license not reverified on Commons")
    if x["id"]=="45895144765" and "flickreviewr" not in p.text.lower():
        raise SystemExit("Flickr CC review not in Commons source")
    u="https://commons.wikimedia.org/wiki/Special:Redirect/file/"+quote(x["title"])
    urls=[u,*x["backup"]]
    if "45895144765"==x["id"]:
        flick=s.get("https://www.flickr.com/photos/127605180@N04/45895144765",timeout=35)
        if flick.status_code==200:
            for pat in (r'<meta[^>]+property=["\x27]og:image["\x27][^>]+content=["\x27]([^"\x27]+)',r'https://live\.staticflickr\.com/[^"\x27<\s\\]+\.jpg'):
                m=re.search(pat,flick.text,re.I)
                if m:
                    imageurl=html.unescape(m.group(1) if m.lastindex else m.group(0)).replace("\\/","/")
                    if urlparse(imageurl).hostname=="live.staticflickr.com":urls.append(imageurl);break
    im=None;used=""
    for url in urls:
        try:
            q=s.get(url,timeout=80,allow_redirects=True)
            if q.status_code in (403,404,429,500,502,503,504):
                print("THUMB_OR_ORIGINAL_RATE_LIMIT",x["id"],q.status_code);continue
            q.raise_for_status()
            uri=urlparse(q.url)
            if uri.scheme!="https" or uri.hostname not in ("upload.wikimedia.org","thumb.wikimedia.org","live.staticflickr.com","inaturalist-open-data.s3.amazonaws.com","static.inaturalist.org"):continue
            if not q.content.startswith(b"\xff\xd8") or len(q.content)<30000:continue
            v=Image.open(io.BytesIO(q.content));v.verify()
            v=ImageOps.exif_transpose(Image.open(io.BytesIO(q.content))).convert("RGB")
            if min(v.size)<650:continue
            im=v;used=q.url;break
        except (requests.RequestException,OSError) as ex:print("IMAGE_SOURCE_RETRY",x["id"],str(ex)[:90])
    if im is None:
        print("SOURCE_LICENSE_VERIFIED_BUT_NO_USABLE_ORIGINAL",x["id"])
        return False
    im.thumbnail((2600,2600),Image.Resampling.LANCZOS)
    buf=io.BytesIO();im.save(buf,"JPEG",quality=88,optimize=True)
    x["binary"]=buf.getvalue();x["dim"]=list(im.size);x["original"]=used
    x["hash"]=hashlib.sha256(x["binary"]).hexdigest();x["rel"]="images/"+x["filename"];x["path"]=BASE+x["rel"]
    print("EXACT_SOURCE_PHOTO_READY",x["id"],x["dim"],len(x["binary"]))
    return True
good=[]
for x in S:
    if fetch(x):good.append(x)
if not good:raise SystemExit("No original photo downloaded. Canonical gallery stays unchanged")
s.headers.update({"Authorization":"Bearer "+TOKEN,"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"})
ROOT="https://api.github.com/repos/"+REPO+"/contents/"
def get(path):
    q=s.get(ROOT+quote(path,safe="/"),params={"ref":BRANCH},timeout=45)
    if q.status_code==404:return None
    q.raise_for_status();return q.json()
def put(path,blob,sha,msg):
    p={"content":base64.b64encode(blob).decode(),"branch":BRANCH,"message":msg}
    if sha:p["sha"]=sha
    z=s.put(ROOT+quote(path,safe="/"),json=p,timeout=100)
    if z.status_code in (409,422):return False
    z.raise_for_status();return True
for x in good:
    for k in range(7):
        old=get(x["path"])
        if old:
            if old.get("size")!=len(x["binary"]):raise SystemExit("Already-existing image has different bytes "+x["filename"])
            break
        if put(x["path"],x["binary"],None,"Lane 1 physically archive real licensed fluffgrass flowering photo "+x["id"]):
            break
        time.sleep(k+1)
    else:raise SystemExit("Concurrent conflict uploading protected image")
for k in range(7):
    old=get(CARD)
    if not old:raise SystemExit("Canonical fluffgrass card missing")
    d=json.loads(base64.b64decode(old["content"]))
    if d.get("id")!="munroa-pulchella":raise SystemExit("Not Munroa pulchella")
    records=d.setdefault("images",[]);panels=d.setdefault("visual_comparison",{}).setdefault("items",[])
    changed=False
    for x in good:
        existing=[z for z in panels if z.get("source")==x["page"] or z.get("source_page")==x["page"]]
        if len(existing)!=1:raise SystemExit("Unexpected gallery original URL/synonym not 1 "+x["id"]+" "+str(len(existing)))
        p=existing[0]
        if p.get("image_url")==x["path"] and any(z.get("file")==x["rel"] for z in records):
            continue
        if any(z.get("file")==x["rel"] for z in records):
            raise SystemExit("Partial prior install; don't duplicate")
        records.append({
          "file":x["rel"],"role":x["role"],"creator":x["creator"],
          "license":x["license"],"license_url":x["license_url"],
          "source_page":x["page"],"source_original":x["original"],"source_photo_id":x["id"],
          "source_taxon_name":"Dasyochloa pulchella","canonical_taxon_name":"Munroa pulchella",
          "source_region":"New Mexico, USA" if x["id"]=="14751775" else "Deep Springs Valley, California, USA",
          "public_reuse":"Individual Commons image-level CC license verified; attribution, license, ShareAlike (if applicable), changes notice required",
          "modifications":"Saved RGB JPEG, stripped EXIF/GPS and resized to <=2600px longest side; original composition preserved",
          "image_dimensions":x["dim"],"image_sha256":x["hash"],
          "photo_review":"Exact source taxon synonym and image-level rights verified; source content known as live field leafy flowering-habit; true free ligule/glume dissection still absent."
        })
        p["image_url"]=x["path"];p["source_original"]=x["original"];p["license_url"]=x["license_url"]
        p["photo_status"]="Verified photo bytes physically archived under species images; original pixel role still gross habit/flowering, true anatomy macro unresolved"
        changed=True
    if not changed:print("ALREADY_INSTALLED");break
    d.setdefault("curation_status",{})["photo_files_present"]=sum(str(z.get("file","")).startswith("images/") for z in records)
    d["curation_status"]["lane1_fluffgrass_photos_20261027"]="TWO_EXTERNALLY_LINKED_EXACT_SPECIES_FLOWERING_IMAGES_NOW_PERMANENT_CC_ARCHIVES_LIGULE_SPIKELET_DISSECTION_STILL_MISSING"
    b=(json.dumps(d,indent=2,ensure_ascii=False)+"\n").encode()
    if put(CARD,b,old["sha"],"Lane 1 mirror genuinely licensed fluffgrass flowering/habit references to local GitHub photos"):
        print("MUNROA_GALLERY_LOCAL_ARCHIVE_SUCCESS",len(good),len(records),len(panels));break
    time.sleep(k+1)
else:raise SystemExit("Concurrent canonical edits; image files archived but require gallery recheck")
