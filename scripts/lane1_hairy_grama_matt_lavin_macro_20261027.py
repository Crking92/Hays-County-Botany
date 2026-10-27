#!/usr/bin/env python3
"""Lane1 one new species-specific anatomical macro of Bouteloua hirsuta.
Exact Matt Lavin individual file license CC BY-SA 2.0 verified by FlickrReviewR,
distinct original 49158063571 from existing Lavin photo 4087876904.
Original second-glume gland/hair claim from original photographer; no unproven arrows.
"""
import requests,io,base64,json,html,re,time,hashlib
from PIL import Image,ImageOps
from urllib.parse import quote,urlparse
import os
R=os.environ["GITHUB_REPOSITORY"];TOK=os.environ["GITHUB_TOKEN"];BR=os.environ.get("GITHUB_REF_NAME","main")
BASE="content/taxa/Poaceae/Bouteloua/bouteloua-hirsuta/"
CARD=BASE+"species.json"
NAME="matt-lavin-hairy-grama-glume-gland-hairs-49158063571-by-sa2.jpg"
REL="images/"+NAME; FILE=BASE+REL
ORIGINAL="https://live.staticflickr.com/65535/49158063571_19e3ca346b_o.jpg"
PAGE="https://commons.wikimedia.org/wiki/File:Bouteloua_hirsuta_-_hairy_grama_-_Flickr_-_Matt_Lavin.jpg"
LIC="https://creativecommons.org/licenses/by-sa/2.0/"
s=requests.Session();s.headers.update({"User-Agent":"HaysCountyBotany-Lane1SpeciesPhoto-OriginalLicenseAudit/1.0"})
p=s.get(PAGE,timeout=45);p.raise_for_status()
page=" ".join(html.unescape(re.sub(r"<[^>]+>"," ",p.text)).lower().split())
for t in ("bouteloua hirsuta","matt lavin","49158063571","second glumes","dark sessile glands","attribution-share alike 2.0 generic","flickreviewr"):
    if t not in p.text.lower() and t not in page:raise SystemExit("Original author/rights/taxon/morphology not verified: "+t)
choices=[
 "https://commons.wikimedia.org/wiki/Special:Redirect/file/"+quote("Bouteloua hirsuta - hairy grama - Flickr - Matt Lavin.jpg"),
 ORIGINAL
]
photo=None;used=""
for url in choices:
    try:
        q=s.get(url,timeout=95,allow_redirects=True)
        if q.status_code in (403,404,429,500,502,503,504):
            print("PUBLIC_ORIGINAL_HOST_BLOCKED",q.status_code);continue
        q.raise_for_status()
        host=urlparse(q.url)
        if host.hostname not in ("upload.wikimedia.org","live.staticflickr.com"):raise SystemExit("Image redirect to unapproved host")
        if not q.content.startswith(b"\xff\xd8") or not 65_000<len(q.content)<18_000_000:continue
        check=Image.open(io.BytesIO(q.content));check.verify()
        im=ImageOps.exif_transpose(Image.open(io.BytesIO(q.content))).convert("RGB")
        if min(im.size)<1000:continue
        photo=im;used=q.url;break
    except (requests.RequestException,OSError) as exc:print("SOURCE_DOWNLOAD_RETRY",str(exc)[:120])
if photo is None:raise SystemExit("Original species photo not reachable; no data changed")
photo.thumbnail((3000,3000),Image.Resampling.LANCZOS)
buf=io.BytesIO();photo.save(buf,"JPEG",quality=90,optimize=True)
data=buf.getvalue();digest=hashlib.sha256(data).hexdigest()
print("LICENSE_AND_ORIGINAL_PIXELS_CONFIRMED",len(data),photo.size,digest)
s.headers.update({"Authorization":"Bearer "+TOK,"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"})
api="https://api.github.com/repos/"+R+"/contents/"
def get(path):
    x=s.get(api+quote(path,safe="/"),params={"ref":BR},timeout=50)
    if x.status_code==404:return None
    x.raise_for_status();return x.json()
def put(path,blob,sha,msg):
    d={"branch":BR,"message":msg,"content":base64.b64encode(blob).decode()}
    if sha:d["sha"]=sha
    q=s.put(api+quote(path,safe="/"),json=d,timeout=100)
    if q.status_code in (409,422):return False
    q.raise_for_status();return True
for i in range(8):
    old=get(FILE)
    if old:
        if old.get("size")!=len(data):raise SystemExit("Different existing photo; preserve")
        break
    if put(FILE,data,None,"Lane 1 real licensed hairy grama second-glume gland/hair photo"):break
    time.sleep(i+1)
else:raise SystemExit("Concurrent photos not committed; no overwrite attempted")
record={
 "file":REL,"role":"Actual second-glume region, outward-spreading hairs and naked projected terminal branch tip on true Bouteloua hirsuta. Photographer documents dark hair-base glands; macro pixel identification still needs final zoom review. Not a collar or rooted plant.",
 "creator":"Matt Lavin","license":"CC BY-SA 2.0","license_url":LIC,
 "source_page":PAGE,"source_original":used,"source_flickr_id":"49158063571",
 "source_taxon_name":"Bouteloua hirsuta","source_locality":"Bozeman, Montana USA; not a Central Texas voucher",
 "public_reuse":"CC BY-SA 2.0 attribution/license/change notice with ShareAlike; FlickreviewR confirmed original individual source rights",
 "modifications":"RGB JPEG reencoded, EXIF/GPS removed and scaled down; full composition retained",
 "image_dimensions":list(photo.size),"image_sha256":digest,
 "photo_review":"Real extra photo from a distinct Matt Lavin source, selected for true hair-bearing reproductive bracts. No glume vein/actual gland microscopic arrow unless individually identifiable on image pixels."
}
panel={
 "label":"HAIRY GRAMA — second-glume spreading hairs and bare branch extension (real macro)",
 "scientific_name":"Bouteloua hirsuta","image_url":FILE,"image_fit":"contain",
 "creator":"Matt Lavin","license":"CC BY-SA 2.0","license_url":LIC,
 "source_page":PAGE,"source_original":used,"image_role":record["role"],
 "caption":"Original hairy grama reproduction photograph by Matt Lavin. Prominent second glumes carry long spreading hairs, described by the photographer as arising from dark sessile glands. Unlike blue grama, the flower-bearing branch ends in a longer naked extension. This is NOT the ligule or leaf collar; glume hair gland points remain to be verified in full-resolution pixels.",
 "why_it_matters":"A new distinct view of the reproductive glume/rachis anatomy, emphasizing an important look-alike difference rather than another generic seedhead.",
 "markers":[],"photo_status":"Original individual CC image and exact species verified; new GPS-free local JPEG. Final micro arrows and mobile placement held for expert image review."
}
for attempt in range(9):
    obj=get(CARD)
    if not obj:raise SystemExit("Hairy grama canonical species missing")
    d=json.loads(base64.b64decode(obj["content"]))
    if d.get("id")!="bouteloua-hirsuta":raise SystemExit("Wrong species")
    ar=d.setdefault("images",[]);gal=d.setdefault("visual_comparison",{}).setdefault("items",[])
    a=[z for z in ar if z.get("file")==REL];b=[z for z in gal if z.get("image_url")==FILE]
    if len(a)==len(b)==1:print("ALREADY_INSTALLED");break
    if a or b:raise SystemExit("Half-install; preserve and stop")
    ar.append(record)
    ix=next((i for i,z in enumerate(gal) if z.get("scientific_name")!="Bouteloua hirsuta"),len(gal))
    gal.insert(ix,panel)
    d.setdefault("curation_status",{})["photo_files_present"]=sum(str(z.get("file","")).startswith("images/") for z in ar)
    d["curation_status"]["lane1_hairy_grama_second_glume_macro_20261027"]="ADDITIONAL_GENUINE_CC_BY_SA_REPRODUCTIVE_MACRO_ARCHIVED_AND_GALLERY_ADDED_LIGULE_STILL_MISSING"
    textblob=(json.dumps(d,indent=2,ensure_ascii=False)+"\n").encode()
    if put(CARD,textblob,obj["sha"],"Lane1 add original licensed hairy grama reproductive hair-bearing glume macro"):
        print("HAIRY_GRAMA_PHOTO_INSTALLED",len(ar),len(gal));break
    time.sleep(attempt+1)
else:raise SystemExit("Concurrent edit; photo archived but canonical gallery not updated")
