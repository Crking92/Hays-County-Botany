#!/usr/bin/env python3
"""Lane 1 real upper-organ photo finish for Urochloa fusca.
Jim Conrad's OWN explicitly public-domain field photographs in Uvalde, Texas:
true hair-fringed blade–sheath ligule, attached spikelets, whole flowering plant.
Only source-verified 2014 Uvalde photos. 2019 Mexico photo taxon is uncertain
in original text and intentionally excluded. Reject if individual ownership unclear.
"""
import base64,hashlib,html,io,json,os,re,time
from urllib.parse import quote,urljoin,urlparse
import requests
from PIL import Image,ImageOps
REPO=os.environ["GITHUB_REPOSITORY"]
TOKEN=os.environ["GITHUB_TOKEN"]
BRANCH=os.environ.get("GITHUB_REF_NAME","main")
ARTICLE="https://www.backyardnature.net/n/h/urochloa.htm"
RIGHTS="https://www.backyardnature.net/j/copyrite.htm"
BASE="content/taxa/Poaceae/Urochloa/urochloa-fusca/"
CARD=BASE+"species.json"
PHOTO=[
 {"id":"140928ut.jpg","file":"jim-conrad-urochloa-fusca-actual-ligule-public-domain.jpg",
  "label":"ACTUAL TRUE LIGULE — white hair fringe on inside of Uvalde brownseed signalgrass collar (Jim Conrad, public domain)",
  "role":"True inner hair-fringed ligule across the blade–sheath junction, clearly separable from hairs on sheath exterior and surrounding leaf. Photo is visibly species-specific. No physical millimeter ruler photographed.",
  "caption":"Actual inner ligule of brownseed signalgrass at the leaf blade/sheath junction, photographed by Jim Conrad at Cook's Slough Nature Park near Uvalde, Texas. The white fringe forming a low wall across the inside of the leaf junction is the LIGULE, not the longer outside sheath hairs. No millimeter scale is in this photograph.",
  "markers":[{"label":"TRUE white-hairy inner ligule","label_x":8,"label_y":13,"target_x":52,"target_y":76}],
  "photo_role":"collar_ligule"},
 {"id":"140928us.jpg","file":"jim-conrad-urochloa-fusca-attached-spikelet-macro-public-domain.jpg",
  "label":"REAL ATTACHED SPIKELETS — one-sided green ribbed spikelets along Uvalde raceme (Jim Conrad, public domain)",
  "role":"Source-verified actual U. fusca close-up with intact attached green ribbed and purple-tipped spikelets arranged on one side of narrow rachis, plus fine rachis hairs. Glume/lemma dissection NOT present.",
  "caption":"Brownseed signalgrass's ribbed green oval spikelets all face one side of their thin flowering branch (secund arrangement). The thin hair-like stalk structures are rachis hairs, not another spikelet row; individual glumes and fertile lemma remain undissected.",
  "markers":[{"label":"Attached ribbed spikelet","label_x":4,"label_y":18,"target_x":40,"target_y":64},{"label":"Same-side arrangement along rachis","label_x":59,"label_y":13,"target_x":62,"target_y":39}],
  "photo_role":"attached_spikelet_macro"},
 {"id":"140928ur.jpg","file":"jim-conrad-urochloa-fusca-attached-flowering-plant-texas-public-domain.jpg",
  "label":"ACTUAL FIELD FLOWERING HABIT — attached racemes and long arching leaves in Uvalde (Jim Conrad, public domain)",
  "role":"Real field-growing Texas plant, leaves and stems attached to multiple entire branching flowering heads; buried root crown not visible. Uvalde locality.",
  "caption":"Actual flowering brownseed signalgrass growing at Cook's Slough, Uvalde County area, Texas. Observe a whole branched terminal panicle on its culm with long arching leaves attached; the true ligule is shown separately in the close-up, not here.",
  "markers":[{"label":"Whole branched flowering head","label_x":9,"label_y":12,"target_x":60,"target_y":14},{"label":"Long leaf on flowering culm","label_x":5,"label_y":54,"target_x":39,"target_y":43}],
  "photo_role":"whole_flowering_habit"}
]
s=requests.Session();s.headers.update({"User-Agent":"Hays-Botany-Public-Domain-Original-Photo-Archiver/1.0"})
page=s.get(ARTICLE,timeout=55);page.raise_for_status()
site=s.get(RIGHTS,timeout=50);site.raise_for_status()
text=" ".join(html.unescape(re.sub(r"<[^>]+>"," ",page.text)).split())
rights=" ".join(html.unescape(re.sub(r"<[^>]+>"," ",site.text)).split())
if "Jim Conrad" not in text or "UROCHLOA FUSCA" not in text.upper() or "Cook's Slough" not in text or "September 28, 2014" not in text:
    raise SystemExit("Original Texas author, taxon and Uvalde locality not all supported")
if not (re.search(r"Jim Conrad.{0,130}PUBLIC DOMAIN",rights,re.I) and re.search(r"all images produced by myself",rights,re.I)):
    raise SystemExit("Actual photographer's explicit public domain release unavailable")
if not re.search(r"Excerpts from Jim Conrad",text,re.I):
    raise SystemExit("Article not unambiguously identified as author's own newsletter excerpt")
# Prevent 2019 Yucatan photographs, which the author himself labels uncertain.
cut=page.text.lower().find("march 1, 2019")
if cut<0:raise SystemExit("Cannot establish 2014-only original source section")
early=page.text[:cut]
for p in PHOTO:
    if p["id"].lower() not in early.lower():raise SystemExit("Photo not part of original 2014 Uvalde article "+p["id"])
    # Page 2014 images have no third-party photographer credit at image tag.
    for m in re.finditer(r"<img\b[^>]*>",early,re.I|re.S):
        tag=html.unescape(m.group(0))
        if p["id"].lower() in tag.lower():
            if any(q in tag.lower() for q in ("photo by another","courtesy of","copyright of","©","all rights reserved")):
                raise SystemExit("Third party ownership around image "+p["id"])
            break
    else:
        raise SystemExit("Individual 2014 photo not inside original source img tag "+p["id"])
    url="https://www.backyardnature.net/n/14/"+p["id"]
    q=s.get(url,timeout=85,allow_redirects=True);q.raise_for_status()
    u=urlparse(q.url)
    if u.scheme!="https" or u.hostname not in ("www.backyardnature.net","backyardnature.net"):
        raise SystemExit("Image redirected to unverified ownership site "+p["id"])
    if not q.content.startswith(b"\xff\xd8") or not 25_000<len(q.content)<15_000_000:
        raise SystemExit("Exact source JPEG unavailable or unexpected bytes "+p["id"])
    t=Image.open(io.BytesIO(q.content));t.verify()
    im=ImageOps.exif_transpose(Image.open(io.BytesIO(q.content))).convert("RGB")
    if min(im.size)<350:raise SystemExit("Image too small for tissue "+p["id"])
    out=io.BytesIO();im.save(out,"JPEG",quality=93,optimize=True)
    p["data"]=out.getvalue();p["dims"]=list(im.size)
    p["sha256"]=hashlib.sha256(p["data"]).hexdigest()
    p["url"]=url;p["relative"]="images/"+p["file"];p["local"]=BASE+p["relative"]
    print("LICENSED_REAL_EXIF_CLEAN_TAXON_PHOTO",p["id"],p["dims"],len(p["data"]),p["sha256"])
s.headers.update({"Authorization":"Bearer "+TOKEN,"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"})
API="https://api.github.com/repos/"+REPO+"/contents/"
def get(path):
    q=s.get(API+quote(path,safe="/"),params={"ref":BRANCH},timeout=50)
    if q.status_code==404:return None
    q.raise_for_status();return q.json()
def put(path,raw,sha,msg):
    v={"branch":BRANCH,"message":msg,"content":base64.b64encode(raw).decode()}
    if sha:v["sha"]=sha
    q=s.put(API+quote(path,safe="/"),json=v,timeout=90)
    if q.status_code in (409,422):
        print("SAFE_CONCURRENT_RETRY",path,q.status_code,str(q.text)[:170])
        return False
    q.raise_for_status()
    return True
for p in PHOTO:
    for i in range(9):
        old=get(p["local"])
        if old:
            if old.get("size")!=len(p["data"]):
                raise SystemExit("Existing same-name image different bytes; don't replace original")
            break
        if put(p["local"],p["data"],None,"Lane 1 archive exact public-domain Jim Conrad 2014 Texas brownseed "+p["photo_role"]):
            break
        time.sleep(i+1)
    else:raise SystemExit("Concurrent GitHub write collision on image "+p["local"])
for k in range(9):
    obj=get(CARD)
    if not obj:raise SystemExit("Canonical Urochloa fusca card missing")
    d=json.loads(base64.b64decode(obj["content"]))
    if d.get("id")!="urochloa-fusca":raise SystemExit("Wrong taxon card")
    records=d.setdefault("images",[])
    panel=d.setdefault("visual_comparison",{}).setdefault("items",[])
    changed=False
    for p in PHOTO:
        r=[x for x in records if x.get("file")==p["relative"]]
        q=[x for x in panel if x.get("image_url")==p["local"]]
        if len(r)==len(q)==1:continue
        if r or q:raise SystemExit("Partly installed photo, manual conflict protection")
        records.append({
            "file":p["relative"],"role":p["role"],"creator":"Jim Conrad",
            "license":"Public domain — photographer's explicit dedication",
            "license_url":RIGHTS,"source_permission_page":RIGHTS,
            "source_page":ARTICLE,"source_original":p["url"],
            "source_photo_original_name":p["id"],"source_taxon_name":"Urochloa fusca",
            "source_locality":"Cook's Slough Nature Park, Uvalde, Texas — author's 2014 field observation",
            "public_reuse":"YES — Jim Conrad placed his own photographs on Backyard Nature in the public domain; original newsletter identifies author; no other photographer credited for these exact images",
            "modifications":"GPS/EXIF scrubbed; original rectangular composition retained, RGB JPEG recompressed; labeled arrows are web overlays, not embedded image adaptations",
            "photo_review":"Original individual photo visually inspected: "+p["role"],
            "image_dimensions":p["dims"],"image_sha256":p["sha256"]})
        insert=next((j for j,item in enumerate(panel) if item.get("scientific_name")!="Urochloa fusca"),len(panel))
        panel.insert(insert,{
            "label":p["label"],"scientific_name":"Urochloa fusca",
            "image_url":p["local"],"image_fit":"contain",
            "creator":"Jim Conrad","license":"Public domain — photographer's explicit dedication",
            "license_url":RIGHTS,"source_permission_page":RIGHTS,
            "source_page":ARTICLE,"source_original":p["url"],
            "image_role":p["role"],"caption":p["caption"],
            "why_it_matters":"Authentic Hays-region Texas field photograph of actual "+p["photo_role"].replace("_"," ")+" with diagnosable organ pixels, not generic lesson text.",
            "markers":p["markers"],
            "photo_status":"Original photographer PD rights and taxon/location verified, true visible source pixels reviewed, local EXIF-stripped JPEG; final mobile arrow placement and deployed Pages QA separate."
        })
        changed=True
    if not changed:print("ALREADY_INSTALLED");break
    d.setdefault("curation_status",{})["photo_files_present"]=sum(str(v.get("file","")).startswith("images/") for v in records)
    d["curation_status"]["photo_metadata_count"]=len(records)
    d["curation_status"]["lane1_jim_conrad_uvalde_20261027"]="THREE_PUBLIC_DOMAIN_TEXAS_REAL_PHOTOS_TRUE_LIGULE_ATTACHED_REPRODUCTIVE_SPIKELETS_WHOLE_FLOWERING_HABIT_ARCHIVED"
    new=(json.dumps(d,indent=2,ensure_ascii=False)+"\n").encode()
    if put(CARD,new,obj["sha"],"Lane 1 brownseed signalgrass actual true ligule, attached spikelets and whole Texas flowering plant"):
        print("CANONICAL_LIGULE_PLUS_SPIKELET_PLUS_HABIT_UPDATED",len(records),len(panel))
        break
    time.sleep(k+1)
else:raise SystemExit("Canonical species changed repeatedly: photos stored but gallery linkage still needs review")
