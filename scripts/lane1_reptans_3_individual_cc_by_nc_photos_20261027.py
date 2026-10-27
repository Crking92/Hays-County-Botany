#!/usr/bin/env python3
"""Lane1 Urochloa reptans: 3 distinct original real species photos, SOURCE + INDIVIDUAL license verified.
Exact iNaturalist observation 107116761, photographed by Francois Rousseu on Reunion.
Includes 2 different reproductive macros and a plant/stems-leaves-flowering view.
No actual inner blade/sheath ligule, roots or dissected glumes => no invented arrows.
"""
import os,re,io,time,base64,hashlib,json
from urllib.parse import quote
import requests
from bs4 import BeautifulSoup
from PIL import Image,ImageOps
REPO=os.environ["GITHUB_REPOSITORY"]
TOKEN=os.environ["GITHUB_TOKEN"]
BRANCH=os.environ.get("GITHUB_REF_NAME","main")
RUN="https://rungrass.org/"
OBS_ID=107116761
OBS="https://www.inaturalist.org/observations/"+str(OBS_ID)
BASE="content/taxa/Poaceae/Urochloa/urochloa-reptans/"
CARD=BASE+"species.json"
LIC="https://creativecommons.org/licenses/by-nc/4.0/"
TARGET=[
 dict(id=181982648,file="francois-rousseau-reptans-mature-ovoid-spikelets-by-nc.jpg",kind="MATURE SPIKELETS",
 role="Genuine high-magnification photograph of clustered mature large green ovoid Urochloa reptans spikelets with characteristic overlapping glume-like surfaces on an attached raceme. Not dissected: lower/upper glume insertion and lemma remain unverified.",
 label="REAL MATURE OVOID SPIKELETS — close arranged flowering units (François Rousseu)",
 caption="Actual mature plump, elliptic Urochloa reptans spikelets against a dark background in a close original photograph. See the overlapping green exterior bracts and side-by-side units; the individual glume and lemma attachment points are not revealed in this intact view. Photograph from Réunion, not a Texas voucher."),
 dict(id=181982682,file="francois-rousseau-reptans-single-raceme-attached-spikelets-by-nc.jpg",kind="ATTACHED SPIKELETS",
 role="Close actual narrow reproductive raceme bearing numerous green paired-looking crowded spikelets, stems and aligned florets genuinely visible. Cannot prove sexed members, dissected glumes or a millimeter count from this photo.",
 label="ATTACHED REPRODUCTIVE RACEME — rows of actual U. reptans spikelets (François Rousseu)",
 caption="True Urochloa reptans reproductive raceme photographed close to show rows of attached oval spikelets along a slender flowering branch. Use it alongside the larger individual-spikelet view. No dissected glume, lemma or palea is claimed."),
 dict(id=180095076,file="francois-rousseau-reptans-field-flowering-with-hand-by-nc.jpg",kind="WHOLE FLOWERING HABIT",
 role="Actual field-growing Urochloa reptans narrow stems and full branching seedhead/leafy patch held against hand for scale in Réunion. Exact rooted crown and ligule are NOT visible.",
 label="LIVING GROWTH FORM — U. reptans leaves, flowering culms and hand for scale (François Rousseu)",
 caption="Living Urochloa reptans stems and branching flowering axes in a grassy field with a hand for rough scale. This is a field habit photo from Réunion rather than a complete uprooted crown, a measured ligule, or a Central Texas field voucher.")
]
S=requests.Session();S.headers.update({"User-Agent":"HaysCountyBotany-RealUrochloaReptans-IndividualPhotoRightsVerifier/1.0"})
p=S.get(RUN,timeout=55);p.raise_for_status()
soup=BeautifulSoup(p.content,"html.parser")
section=soup.find(id="Urochloa_reptans")
if section is None:raise SystemExit("No verified source taxon section")
expected={}
for el in section.find_all_next():
    if el.name=="div" and el is not section and "headersp" in el.get("class",[]):break
    if el.name=="img" and "imgsp" in el.get("class",[]):
        src=el.get("data-src","")
        m=re.fullmatch(r"https://inaturalist-open-data\.s3\.amazonaws\.com/photos/(\d+)/original\.jpeg",src)
        if not m:continue
        if el.get("alt","")!=OBS:raise SystemExit("Other observation in exact source taxon photo series")
        if "François Rousseu" not in el.get("title","") or "CC BY-NC" not in el.get("title",""):
            raise SystemExit("Rungrass individual photo license/author missing: "+str(m.group(1)))
        expected[int(m.group(1))]=src
if len(expected)!=7:raise SystemExit("Rungrass exact taxon photo count changed; no assumptions")
obsresp=S.get("https://api.inaturalist.org/v1/observations/"+str(OBS_ID),timeout=55)
obsresp.raise_for_status()
r=obsresp.json()["results"][0]
if r.get("id")!=OBS_ID or (r.get("taxon") or {}).get("name")!="Urochloa reptans":
    raise SystemExit("Original source observation not a verified Urochloa reptans")
pairs={x["id"]:x for x in r.get("photos",[])}
for t in TARGET:
    id=t["id"]
    if id not in expected or id not in pairs:raise SystemExit("Original photo missing from observation: "+str(id))
    if pairs[id].get("license_code")!="cc-by-nc":raise SystemExit("Photo-level CC BY-NC not verified: "+str(id))
    src=expected[id]
    resp=S.get(src,timeout=75,allow_redirects=True)
    if resp.status_code!=200 or not 50_000<len(resp.content)<14_000_000 or not resp.content.startswith(b"\xff\xd8"):
        raise SystemExit("Original photo binary inaccessible "+str(id))
    check=Image.open(io.BytesIO(resp.content));check.verify()
    im=ImageOps.exif_transpose(Image.open(io.BytesIO(resp.content))).convert("RGB")
    if min(im.size)<900:raise SystemExit("Photo too small for verified species reproductive anatomy "+str(id))
    im.thumbnail((2500,2500),Image.Resampling.LANCZOS)
    buffer=io.BytesIO();im.save(buffer,"JPEG",quality=91,optimize=True)
    t["content"]=buffer.getvalue()
    t["sha256"]=hashlib.sha256(t["content"]).hexdigest()
    t["size"]=list(im.size)
    t["path"]=BASE+"images/"+t["file"]
    t["photo_page"]="https://www.inaturalist.org/photos/"+str(id)
    t["original"]=src
    print("INDIVIDUALLY_CONFIRMED_CC_NC_EXACT_SPECIES_PHOTO",id,len(t["content"]),t["size"],t["sha256"])
S.headers.update({"Authorization":"Bearer "+TOKEN,"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"})
API="https://api.github.com/repos/"+REPO+"/contents/"
def get(path):
    z=S.get(API+quote(path,safe="/"),params={"ref":BRANCH},timeout=45)
    if z.status_code==404:return None
    z.raise_for_status();return z.json()
def put(path,content,sha,message):
    body={"content":base64.b64encode(content).decode(),"branch":BRANCH,"message":message}
    if sha:body["sha"]=sha
    z=S.put(API+quote(path,safe="/"),json=body,timeout=100)
    if z.status_code in (409,422):return False
    z.raise_for_status();return True
for t in TARGET:
    for i in range(9):
        cur=get(t["path"])
        if cur:
            if cur.get("size")!=len(t["content"]):raise SystemExit("Existing different photo; preserve")
            break
        if put(t["path"],t["content"],None,"Lane 1 permanently archive exact U. reptans CC BY-NC "+t["kind"]):
            break
        time.sleep(i+1)
    else:raise SystemExit("Repeated safe upload collisions; no replacement")
for k in range(9):
    obj=get(CARD)
    if obj is None:raise SystemExit("Canonical Urochloa reptans card missing")
    d=json.loads(base64.b64decode(obj["content"]))
    if d.get("id")!="urochloa-reptans":raise SystemExit("Wrong species target")
    imgs=d.setdefault("images",[])
    panels=d.setdefault("visual_comparison",{}).setdefault("items",[])
    changed=False
    for t in TARGET:
        f="images/"+t["file"]
        a=[x for x in imgs if x.get("file")==f]
        b=[x for x in panels if x.get("image_url")==t["path"]]
        if len(a)==len(b)==1:continue
        if a or b:raise SystemExit("Canonical photo conflict detected; do not duplicate")
        imgs.append({
          "file":f,"role":t["role"],"creator":"François Rousseu",
          "license":"CC BY-NC 4.0","license_url":LIC,
          "source_page":t["photo_page"],"source_gallery_page":RUN,"source_observation":OBS,
          "source_original":t["original"],"source_taxon_name":"Urochloa reptans",
          "source_region":"Réunion, Indian Ocean. Not a Texas voucher.",
          "public_reuse":"YES only on strictly noncommercial public learner, with individual CC BY-NC 4.0 photo source credit and no false site entitlement",
          "photo_level_license_verified":"cc-by-nc per original iNaturalist observations API AND individual Rungrass photo label",
          "modifications":"EXIF/GPS removed; recompressed and resized JPEG; photograph composition intact",
          "image_dimensions":t["size"],"image_sha256":t["sha256"],
          "photo_review":"Actual independent source contact-sheet pixel review: "+t["kind"]+" clear. Ligule, dissected floral bracts, and rooted soil contacts NOT visibly proven."
        })
        x={
          "label":t["label"],"scientific_name":"Urochloa reptans","image_url":t["path"],
          "image_fit":"contain","image_role":t["role"],"creator":"François Rousseu",
          "license":"CC BY-NC 4.0","license_url":LIC,"source_page":t["photo_page"],
          "source_observation":OBS,"source_original":t["original"],
          "caption":t["caption"],"why_it_matters":"Source-verified, pixel-reviewed, same-species actual anatomical view, avoids guessing from another signalgrass.",
          "markers":[],"photo_status":"Original ID and photo-level license independently verified. Real species pixels inspected in seven-photo contact sheet; mobile arrow approval and Pages release independent."
        }
        n=next((idx for idx,it in enumerate(panels) if it.get("scientific_name")!="Urochloa reptans"),len(panels))
        panels.insert(n,x);changed=True
    if not changed:print("ALREADY_INSTALLED");break
    d.setdefault("curation_status",{})["photo_files_present"]=sum(str(x.get("file","")).startswith("images/") for x in imgs)
    d["curation_status"]["photo_metadata_count"]=len(imgs)
    d["curation_status"]["lane1_rungrass_verified_u_reptans_20261027"]="THREE_REAL_REPRODUCTIVE_MACROS_AND_HABIT_IMAGES_PHYSICALLY_ARCHIVED_FROM_EXACT_CC_BY_NC_OBSERVATION_NO_LIGULE_OR_GLUML_CLAIM"
    new=(json.dumps(d,indent=2,ensure_ascii=False)+"\n").encode()
    if put(CARD,new,obj["sha"],"Lane 1 Urochloa reptans three verified real anatomy and habit photos"):
        print("INSTALLED_REPTANS_REAL_REPRODUCTIVE_GALLERY",len(imgs),len(panels));break
    time.sleep(k+1)
else:raise SystemExit("Canonical updates exhausted, archived photos need gallery readback")
