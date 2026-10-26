#!/usr/bin/env python3
"""Archive exact USDA ARS NA0068870 Texas fluffgrass herbarium voucher, CC0.
Trust no unknown source/license, preserve concurrent canonical edits, no invented organ arrows.
"""
import base64, hashlib, io, json, os, pathlib, re, time, urllib.parse
import requests
from PIL import Image, ImageOps

REPO=os.environ["GITHUB_REPOSITORY"]
TOKEN=os.environ["GITHUB_TOKEN"]
BRANCH=os.environ.get("GITHUB_REF_NAME","main")
PAGE="https://biocollections.ars.usda.gov/collections/individual/index.php?occid=10517"
PHOTO="https://biocollections.ars.usda.gov/imglib/NA/NA0068/NA0068870.jpg"
FILE="usda-ars-na0068870-brewster-texas-herbarium-cc0.jpg"
BASE="content/taxa/Poaceae/Munroa/munroa-pulchella/"
PHOTO_PATH=BASE+"images/"+FILE
CARD=BASE+"species.json"
LICENSE="https://creativecommons.org/publicdomain/zero/1.0/"

source=requests.Session()
source.headers.update({"User-Agent":"HaysCountyBotany-ScienceImageReview/1.0 (educational original-photo-rights check)"})
r=source.get(PAGE,timeout=40);r.raise_for_status()
html=r.text.lower()
clean=" ".join(re.sub(r"<[^>]*>"," ",html).split())
for phrase in ("na0068870","munroa pulchella","brewster county","agricultural research service"):
    if phrase not in clean:raise SystemExit("USDA voucher field missing: "+phrase)
if "creativecommons.org/publicdomain/zero/1.0" not in html:
    raise SystemExit("Exact herbarium record does not carry CC0")
if "1991-08-20" not in clean and "1991" not in clean:
    raise SystemExit("Expected collection date missing")
if "imglib/na/na0068/na0068870.jpg" not in html:
    raise SystemExit("Exact specimen image URL missing from the record")
photo=source.get(PHOTO,timeout=75,allow_redirects=True)
photo.raise_for_status()
pu=urllib.parse.urlparse(photo.url)
if pu.scheme!="https" or pu.hostname!="biocollections.ars.usda.gov":
    raise SystemExit("Unexpected USDA photo redirect")
if not photo.content.startswith(bytes.fromhex("ffd8")) or not 25000<len(photo.content)<16000000:
    raise SystemExit("USDA original did not return plausible JPEG")
im=Image.open(io.BytesIO(photo.content))
im.verify()
im=Image.open(io.BytesIO(photo.content))
im=ImageOps.exif_transpose(im).convert("RGB")
if min(im.size)<500:raise SystemExit("Voucher lacks useful resolution")
im.thumbnail((3600,3600),Image.Resampling.LANCZOS)
buf=io.BytesIO()
im.save(buf,"JPEG",quality=91,optimize=True)
raw=buf.getvalue()
digest=hashlib.sha256(raw).hexdigest()
print("SOURCE_IMAGE_VALID",im.size,"sha256",digest)
api=requests.Session()
api.headers.update({"User-Agent":"HaysCountyBotany-SpeciesPhotoArchive/1.0","Authorization":"Bearer "+TOKEN,
                    "Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"})
root="https://api.github.com/repos/"+REPO+"/contents/"
def get(path):
    u=root+urllib.parse.quote(path,safe="/")
    response=api.get(u,params={"ref":BRANCH},timeout=40)
    if response.status_code==404:return None
    response.raise_for_status()
    return response.json()
def put(path,content,sha,msg):
    payload={"message":msg,"content":base64.b64encode(content).decode(),"branch":BRANCH}
    if sha:payload["sha"]=sha
    response=api.put(root+urllib.parse.quote(path,safe="/"),json=payload,timeout=100)
    if response.status_code in (409,422):return False
    response.raise_for_status()
    return True
prior=get(PHOTO_PATH)
if prior:
    if prior.get("size")!=len(raw):
        raise SystemExit("Existing voucher photo name has different size. Preserve, request review.")
else:
    if not put(PHOTO_PATH,raw,None,"Lane 1 archive genuine USDA ARS CC0 Brewster County Munroa voucher"):
        prior=get(PHOTO_PATH)
        if not prior or prior.get("size")!=len(raw):
            raise SystemExit("Concurrent photo conflict; no overwrite")
record={
 "file":"images/"+FILE,
 "role":"REAL physically archived USDA ARS U.S. National Arboretum herbarium Texas accession NA0068870, whole pressed specimen with original roots, branching stems, clustered flowering tip and ruler/label; no live crown, ligule or dissections proved.",
 "creator":"USDA Agricultural Research Service — U.S. National Arboretum Herbarium",
 "license":"CC0 1.0","license_url":LICENSE,"source_page":PAGE,"source_original":PHOTO,
 "specimen":"NA0068870","taxon":"Munroa pulchella (labelled Dasyochloa pulchella)",
 "collector":"Amos, B.; Emerson, T.","collection_date":"1991-08-20",
 "locality":"Brewster County, Texas, Big Brushy Canyon (not Hays County)",
 "public_reuse":"yes — specimen page explicitly assigns CC0 1.0; USDA ARS rights holder",
 "modifications":"Original JPEG re-encoded after EXIF orientation, resized if >3600px, GPS/EXIF removed; source composition unchanged",
 "image_sha256":digest,"image_dimensions":list(im.size),
 "photo_review":"Physical archive and exact-source license/taxon verified. Pixel-based arrow review remains PENDING; paper voucher root/flower shape not equal to a live rooted photo."}
panel={
 "label":"TEXAS HERBARIUM VOUCHER — NA0068870 rooted pressed Munroa, CC0",
 "scientific_name":"Munroa pulchella","image_url":PHOTO_PATH,"image_fit":"contain",
 "image_role":"USDA ARS Brewster County vouchered whole pressed specimen with root, scale, mature branching leaf/flower clusters; actual photo, not an illustrative drawing or Hays County live sample.",
 "caption":"Texas Brewster County voucher NA0068870, collected by B. Amos and T. Emerson on August 20, 1991; labelled Dasyochloa pulchella (same accepted species). Inspect the complete pressed growth architecture and retained specimen label. A herbarium sheet cannot demonstrate a live rooting node or 0.3–0.5 versus 3–5 mm true ligule; nor does it isolate lemma/awn organs.",
 "why_it_matters":"Genuine voucher-backed Texas source for whole-plant architecture, rather than relying entirely on social-media species identification.",
 "creator":record["creator"],"license":"CC0 1.0","license_url":LICENSE,
 "source_page":PAGE,"source_original":PHOTO,
 "markers":[],
 "photo_status":"Physical USDA CC0 JPEG source right/taxon/ID verified, saved in canonical species gallery. Original pressed specimen image awaiting pixel-specific anatomy/arrows and mobile QA."}
for attempt in range(6):
    c=get(CARD)
    if not c:raise SystemExit("Species card absent")
    data=json.loads(base64.b64decode(c["content"]))
    if data.get("id")!="munroa-pulchella":raise SystemExit("Wrong canonical taxon card")
    images=data.setdefault("images",[])
    gallery=data.setdefault("visual_comparison",{}).setdefault("items",[])
    old_im=[x for x in images if x.get("file")==record["file"]]
    old_panel=[x for x in gallery if x.get("image_url")==PHOTO_PATH]
    if len(old_im)==len(old_panel)==1:
        print("ALREADY_ARCHIVED_IN_GALLERY");break
    if old_im or old_panel:raise SystemExit("Partial or duplicated canonical entry; manual reconciliation")
    images.append(record)
    # Insert immediately following the true introductory Munroa field photo.
    gallery.insert(1,panel)
    data.setdefault("curation_status",{})["lane1_munroa_voucher_archive_20261026"]={
        "status":"PHYSICALLY_ARCHIVED","catalog":"NA0068870","license":"CC0 1.0",
        "rights_page":PAGE,"source":PHOTO,
        "photo_roles":"ROOTED PRESSED VOUCHER + WHOLE FORM; TRUE COLLAR/FINE DISSECTION STILL MISSING",
        "live_site_qa":"NOT CHECKED"}
    bytes_out=(json.dumps(data,ensure_ascii=False,indent=2)+"\n").encode("utf-8")
    if put(CARD,bytes_out,c["sha"],"Lane 1 display real USDA CC0 Brewster County Munroa voucher in learner"):
        print("ARCHIVED_AND_LINKED",PHOTO_PATH,len(raw),im.size);break
    time.sleep(attempt+1)
else:raise SystemExit("Six concurrent JSON write conflicts; archived JPG remains for reconciliation")
