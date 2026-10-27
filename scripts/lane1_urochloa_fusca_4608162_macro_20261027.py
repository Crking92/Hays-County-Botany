#!/usr/bin/env python3
"""Lane 1 actual Urochloa fusca attached oval spikelets from verified iNat photo 4608162.
Fail closed unless exact image-level CC, observation taxon and photo photographer verified.
No fake true ligule/microscopic anatomy, no unsupported arrows. Noncommercial site only.
"""
import base64,hashlib,html,io,json,os,re,time
from urllib.parse import quote,urlparse
import requests
from PIL import Image,ImageOps
REPO=os.environ["GITHUB_REPOSITORY"];TOKEN=os.environ["GITHUB_TOKEN"];BRANCH=os.environ.get("GITHUB_REF_NAME","main")
PHOTONUM=4608162
PAGE="https://www.inaturalist.org/photos/4608162"
GUIDE="https://www.inaturalist.org/guide_taxa/922815"
API="https://api.inaturalist.org/v1/"
BASE="content/taxa/Poaceae/Urochloa/urochloa-fusca/"
CARD=BASE+"species.json"
NAME="inat-4608162-urochloa-fusca-attached-spikelets.jpg"
LOCAL=BASE+"images/"+NAME
s=requests.Session();s.headers.update({"User-Agent":"HaysCountyBotany-LicenseAndTaxonExactPhoto/1.0"})
def fetchjson(url):
    try:
        q=s.get(url,timeout=45)
        if q.status_code!=200:return None
        return q.json()
    except (ValueError,requests.RequestException) as e:
        print("SOURCE_JSON_UNAVAILABLE",url,str(e)[:180]);return None
photos=fetchjson(API+"photos/4608162")
if isinstance(photos,dict) and isinstance(photos.get("results"),list):
    photos=photos["results"][0] if photos["results"] else None
if not isinstance(photos,dict) or photos.get("id")!=PHOTONUM:
    photos=fetchjson(PAGE+".json")
    if isinstance(photos,dict) and "photo" in photos:photos=photos["photo"]
if not isinstance(photos,dict) or photos.get("id")!=PHOTONUM:
    raise SystemExit("Individual iNaturalist photo metadata endpoint did not validate exact 4608162; do not archive")
license_code=str(photos.get("license_code") or "").lower().replace("_","-")
if license_code not in ("cc0","cc-by","cc-by-sa","cc-by-nc","cc-by-nc-sa"):
    raise SystemExit("Photo-level license not allowed: "+license_code)
user=photos.get("user") or {}
creator=photos.get("attribution") or user.get("name") or user.get("login") or ""
if len(creator.strip())<2:raise SystemExit("No attributable photographer")
obsid=photos.get("observation_id") or (photos.get("observation") or {}).get("id")
obs=None
if obsid:
    data=fetchjson(API+"observations/"+str(obsid))
    if data and data.get("results"):obs=data["results"][0]
if not obs:
    data=fetchjson(API+"observations?photo_id=4608162&per_page=8")
    for candidate in (data or {}).get("results",[]):
        if any(x.get("id")==PHOTONUM for x in candidate.get("photos",[])):
            obs=candidate;break
if not obs:raise SystemExit("No original photo-linked observation to validate species")
names=[str((obs.get("taxon") or {}).get("name") or "").lower()]
names += [str(z.get("taxon",{}).get("name") or "").lower() for z in obs.get("identifications",[]) if isinstance(z,dict)]
if "urochloa fusca" not in names and "brachiaria fasciculata" not in names:
    raise SystemExit("Photo observation exact taxon not verified: "+str(names[:7]))
photolink=next((x for x in obs.get("photos",[]) if x.get("id")==PHOTONUM),None)
if not photolink:raise SystemExit("Photo 4608162 not actually present in original observation")
lic2=str(photolink.get("license_code") or license_code).lower().replace("_","-")
if lic2!=license_code:raise SystemExit("Photo-level observation license conflicts")
print("SOURCE_PHOTO_VERIFIED",json.dumps({"license":license_code,"creator":creator,"taxon":names[0],"observation":obs["id"]}))
imageurl=(photos.get("url") or photolink.get("url") or "").replace("square.","original.").replace("thumb.","original.").replace("small.","original.").replace("medium.","original.").replace("large.","original.")
uris=[
 "https://inaturalist-open-data.s3.amazonaws.com/photos/4608162/original.jpeg",
 "https://inaturalist-open-data.s3.amazonaws.com/photos/4608162/original.jpg",
 "https://static.inaturalist.org/photos/4608162/original.jpeg",
 "https://static.inaturalist.org/photos/4608162/original.jpg"
]
if imageurl:uris.insert(0,imageurl)
img=None;used=None
for url in uris:
    try:
        q=s.get(url,timeout=65,allow_redirects=True)
        if q.status_code in (403,404,429,500,502,503,504):continue
        q.raise_for_status()
        parsed=urlparse(q.url)
        if parsed.scheme!="https" or parsed.hostname not in ("static.inaturalist.org","inaturalist-open-data.s3.amazonaws.com","inaturalist.s3.amazonaws.com","inaturalist-production.s3.amazonaws.com"):continue
        if not q.content.startswith(b"\xff\xd8") or not 40000<len(q.content)<16000000:continue
        im=Image.open(io.BytesIO(q.content));im.verify()
        im=ImageOps.exif_transpose(Image.open(io.BytesIO(q.content))).convert("RGB")
        if min(im.size)<650:continue
        img=im;used=q.url;break
    except (requests.RequestException,OSError):continue
if img is None:raise SystemExit("License and species validated but actual source JPEG unavailable")
img.thumbnail((2300,2300),Image.Resampling.LANCZOS)
out=io.BytesIO();img.save(out,"JPEG",quality=89,optimize=True)
binary=out.getvalue();checksum=hashlib.sha256(binary).hexdigest()
print("ARCHIVE_VERIFIED_IMAGE",len(binary),img.size,checksum)
LICENSE_URL={
  "cc0":"https://creativecommons.org/publicdomain/zero/1.0/",
  "cc-by":"https://creativecommons.org/licenses/by/4.0/",
  "cc-by-sa":"https://creativecommons.org/licenses/by-sa/4.0/",
  "cc-by-nc":"https://creativecommons.org/licenses/by-nc/4.0/",
  "cc-by-nc-sa":"https://creativecommons.org/licenses/by-nc-sa/4.0/"
}[license_code]
s.headers.update({"Authorization":"Bearer "+TOKEN,"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"})
REST="https://api.github.com/repos/"+REPO+"/contents/"
def get(path):
    q=s.get(REST+quote(path,safe="/"),params={"ref":BRANCH},timeout=45)
    if q.status_code==404:return None
    q.raise_for_status();return q.json()
def put(path,data,sha,msg):
    q={"message":msg,"branch":BRANCH,"content":base64.b64encode(data).decode()}
    if sha:q["sha"]=sha
    x=s.put(REST+quote(path,safe="/"),json=q,timeout=95)
    if x.status_code in (409,422):return False
    x.raise_for_status();return True
for i in range(7):
    prior=get(LOCAL)
    if prior:
        if prior.get("size")!=len(binary):raise SystemExit("Existing photo differs, don't overwrite")
        break
    if put(LOCAL,binary,None,"Lane 1 archive genuine CC iNat brownseed signalgrass attached spikelets"):
        break
    time.sleep(i+1)
else:raise SystemExit("Photo safe upload conflicts exhausted")
record={
 "file":"images/"+NAME,"role":"Exact species-source Urochloa fusca inflorescence with green mature oval spikelets lined up along multiple slender attached racemes. True inner ligule and dissected glumes/lemmas not pictured.",
 "creator":creator,"license":license_code.upper(),"license_url":LICENSE_URL,
 "source_page":PAGE,"source_original":used,"source_observation":"https://www.inaturalist.org/observations/"+str(obs["id"]),"source_photo_id":PHOTONUM,
 "source_taxon_name":names[0],"public_reuse":"Only if individual "+license_code+" image license remains valid and site's current noncommercial setting is honored where NC applies",
 "modifications":"JPEG re-encoded, EXIF/GPS removed, original composition retained","image_dimensions":list(img.size),"image_sha256":checksum,
 "photo_review":"Original guide photograph pixel-reviewed for individual oval spikelets attached to raceme at fingertip scale. Exact source taxon and image-level Creative Commons license separately verified via observation. No false ligule or glume arrows."}
panel={
 "label":"BROWNSEED SIGNALGRASS — individual attached oval spikelets against fingertips (source-licensed)",
 "scientific_name":"Urochloa fusca","image_url":LOCAL,"image_fit":"contain",
 "creator":creator,"license":license_code.upper(),"license_url":LICENSE_URL,
 "source_page":PAGE,"source_original":used,
 "image_role":record["role"],
 "caption":"Real Urochloa fusca photographed with the thin flowering racemes laid across fingers for scale. Notice ovoid spikelets arranged on the raceme axes. This is gross attachment structure only; exposed glumes, fertile lemma/palea and true ligule are NOT separately documented. Noncommercial public reuse requires original license and creator credit where NC.",
 "why_it_matters":"Species-verified source photo showing individual attached spikelets, unlike existing distant whole-plant and greenhouse vegetative views.",
 "markers":[],"photo_status":"Source photo and license checked; archived, visible macroscopic spikelets; new precise arrows and mobile pixel-review held until verified."}
for k in range(7):
    obj=get(CARD)
    if not obj:raise SystemExit("Brownseed signalgrass canonical card absent")
    d=json.loads(base64.b64decode(obj["content"]))
    if d.get("id")!="urochloa-fusca":raise SystemExit("Wrong taxon")
    a=d.setdefault("images",[]);b=d.setdefault("visual_comparison",{}).setdefault("items",[])
    already=[z for z in a if z.get("file")==record["file"]]
    gallery=[z for z in b if z.get("image_url")==LOCAL]
    if len(already)==len(gallery)==1:print("ALREADY_COMPLETE");break
    if already or gallery:raise SystemExit("Partial prior source photo/gallery install; preserve")
    a.append(record);idx=next((i for i,z in enumerate(b) if z.get("scientific_name")!="Urochloa fusca"),len(b))
    b.insert(idx,panel)
    d.setdefault("curation_status",{})["lane1_fusca_spikelets_20261027"]="SOURCE_VERIFIED_CONNECTED_SPIKELETS_ONLY_TRUE_LIGULE_GLUML_DISCUSSION_STILL_MISSING"
    d["curation_status"]["photo_files_present"]=sum(str(x.get("file","")).startswith("images/") for x in a)
    body=(json.dumps(d,indent=2,ensure_ascii=False)+"\n").encode()
    if put(CARD,body,obj["sha"],"Lane 1 add authentic archived brownseed signalgrass spikelet macro"):
        print("BROWNSEED_GALLERY_UPDATED",len(a),len(b));break
    time.sleep(k+1)
else:raise SystemExit("Card concurrency, photo physically installed but gallery edit needs review")
