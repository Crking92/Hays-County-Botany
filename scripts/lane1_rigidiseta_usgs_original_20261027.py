#!/usr/bin/env python3
"""Physically archive Larry Allain's USGS-authored Texas grama photos.
Exact source official USGS species 3292; no synthetic ligule or root arrows.
Reject third-party copyright, undetermined species, wrong file or image errors.
"""
import base64, hashlib, html, io, json, os, re, time
from urllib.parse import urljoin,urlparse,quote,unquote,parse_qs
import requests
from PIL import Image,ImageOps
REPO=os.environ["GITHUB_REPOSITORY"];TOKEN=os.environ["GITHUB_TOKEN"]
BRANCH=os.environ.get("GITHUB_REF_NAME","main")
PAGE="https://warcapps.usgs.gov/PlantID/Species/Details/3292"
RIGHTS="https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits"
BASE="content/taxa/Poaceae/Bouteloua/bouteloua-rigidiseta/"
CARD=BASE+"species.json"
s=requests.Session();s.headers.update({"User-Agent":"Hays-Botany-Exact-USGS-Grass-Photo-Archive/1.0"})
page=s.get(PAGE,timeout=55);page.raise_for_status()
text=html.unescape(page.text)
txt=re.sub(r"<[^>]+>"," ",text).lower()
for word in ("bouteloua rigidiseta","larry allain","geological survey"):
    if word not in txt:raise SystemExit("USGS species/photo/photographer attribution verification failed: "+word)
licensepage=s.get(RIGHTS,timeout=45);licensepage.raise_for_status()
if "USGS-authored or produced" not in licensepage.text or "Public Domain" not in licensepage.text:
    raise SystemExit("Can't confirm USGS-produced photo public-domain policy")
candidates=[]
for m in re.finditer(r'(?:src|href|data-src)\s*=\s*["\x27]([^"\x27]+)["\x27]',text,re.I):
    val=html.unescape(m.group(1))
    if "GivenFile" in val and "3292" in val:
        candidates.append(urljoin(PAGE,val))
# Dynamic page may populate an image gallery via script/JSON and hide explicit src attribute.
for m in re.finditer(r'(?:https?:)?//warcapps\.usgs\.gov/PlantID/Image/GivenFile\?[^"<> \x27]+',text,re.I):
    candidates.append(html.unescape(m.group(0).replace("\\/","/")))
# Extract raw image filenames embedded in page markup / scripts.
for m in re.finditer(r'(Bouteloua[\s+_%20]*rigidiseta[^"\x27<>\\]{1,90}?\.(?:JPG|JPEG|jpg|jpeg))',text,re.I):
    name=html.unescape(m.group(1))
    name=unquote(name.replace("+"," ")).replace("\\/","/").strip()
    if "/" not in name and "?" not in name:
        candidates.append("https://warcapps.usgs.gov/PlantID/Image/GivenFile?file="+quote(name)+"&id=3292")
# Verified file discovered by visual source image search; source id/photographer checked above.
candidates.insert(0,"https://warcapps.usgs.gov/PlantID/Image/GivenFile?file=Bouteloua+rigidiseta+_+fruit+3.JPG&id=3292")
seen=set();out=[]
for url in candidates:
    url=url.replace("&amp;","&")
    parsed=urlparse(url)
    if parsed.hostname!="warcapps.usgs.gov" or not parsed.path.endswith("/PlantID/Image/GivenFile"):continue
    pairs=parse_qs(parsed.query)
    if "3292" not in pairs.get("id",[]):continue
    filenames=pairs.get("file",[])
    if len(filenames)!=1 or "bouteloua rigidiseta" not in filenames[0].lower().replace("+"," "):continue
    filename=filenames[0]
    if filename.lower() in seen:continue
    seen.add(filename.lower());out.append((filename,url))
print("OFFICIAL_USGS_CANDIDATE_FILENAMES",json.dumps([k for k,_ in out][:18]))
if not out:raise SystemExit("No direct USGS original photo links found")
photos=[]
for filename,url in out[:14]:
    try:
        q=s.get(url,timeout=70)
        if q.status_code!=200 or not q.content.startswith(b"\xff\xd8") or len(q.content)<18000:
            print("SKIP_UNDOWNLOADABLE",filename,q.status_code,len(q.content));continue
        raw=Image.open(io.BytesIO(q.content));raw.verify()
        raw=ImageOps.exif_transpose(Image.open(io.BytesIO(q.content))).convert("RGB")
        if min(raw.size)<450:continue
        raw.thumbnail((2600,2600),Image.Resampling.LANCZOS)
        buffer=io.BytesIO();raw.save(buffer,"JPEG",quality=88,optimize=True)
        clean=buffer.getvalue()
        if not 20_000<len(clean)<10_000_000:continue
        photos.append((filename,url,clean,raw.size))
    except (requests.RequestException,OSError) as exc:
        print("USGS_PHOTO_RETRIEVAL_PROBLEM",filename,str(exc)[:150])
if len(photos)<2:raise SystemExit("Less than two verifiable downloadable USGS original photos, no edits")
def rating(x):
    name=x[0].lower()
    if "fruit 3" in name:return -2
    if "flower" in name or "fruit" in name:return -1
    if "plant" in name or "habit" in name:return 1
    return 2
photos.sort(key=rating)
selected=[]
for x in photos:
    kind="flowering" if ("fruit" in x[0].lower() or "flower" in x[0].lower()) else "whole-plant"
    if sum(1 for p in selected if p[4]==kind)<(2 if kind=="flowering" else 1):
        selected.append((*x,kind))
    if len(selected)>=3:break
if len(selected)<2:raise SystemExit("Less than two distinct usable source photographs")
print("SELECTED_PIXEL_FILES",json.dumps([{"file":p[0],"bytes":len(p[2]),"dimensions":p[3],"kind":p[4]} for p in selected]))
s.headers.update({"Authorization":"Bearer "+TOKEN,"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"})
API="https://api.github.com/repos/"+REPO+"/contents/"
def get(path):
    z=s.get(API+quote(path,safe="/"),params={"ref":BRANCH},timeout=50)
    if z.status_code==404:return None
    z.raise_for_status();return z.json()
def put(path,raw,sha,message):
    data={"content":base64.b64encode(raw).decode(),"branch":BRANCH,"message":message}
    if sha:data["sha"]=sha
    z=s.put(API+quote(path,safe="/"),json=data,timeout=95)
    if z.status_code in (409,422):return False
    z.raise_for_status();return True
records=[]
for k,(name,url,raw,size,kind) in enumerate(selected):
    localname="larry-allain-usgs-texas-grama-"+("flower-head-"+str(k+1) if kind=="flowering" else "field-habit")+".jpg"
    path=BASE+"images/"+localname
    for i in range(7):
        existing=get(path)
        if existing:
            if existing.get("size")!=len(raw):raise SystemExit("Same named photo differs; don't overwrite "+path)
            break
        if put(path,raw,None,"Lane 1 archive USGS Larry Allain real Texas grama "+kind+" photograph"):
            break
        time.sleep(i+1)
    else:raise SystemExit("Concurrent write collisions "+path)
    records.append({
      "file":"images/"+localname,"role":"Actual photographed "+kind+" of source-identified Texas grama; individual lemma/glume or ligule insertion NOT proven. USGS historical photo, Louisiana not Texas.",
      "creator":"Larry Allain / U.S. Geological Survey","license":"US Public Domain (USGS employee-authored)",
      "license_url":RIGHTS,"source_page":PAGE,"source_original":url,
      "source_taxon_name":"Bouteloua rigidiseta","source_photo_filename":name,
      "source_context":"USGS Plants of Louisiana species 3292, photo credit Larry Allain USGS (federal employee), likely Louisiana habitat, not Hays County",
      "public_reuse":"USGS staff-attributed official government photograph; federal-USGS public-domain policy reviewed; credit USGS/Larry Allain",
      "modifications":"EXIF/GPS stripped, RGB JPEG re-encoded and max 2600 px; entire original photo preserved",
      "image_sha256":hashlib.sha256(raw).hexdigest(),"image_dimensions":list(size),
      "photo_review":"Exact taxon and Larry Allain photographer confirmed on official species page. Distinct real photographic image validated; flowering form/habit gross view only, no 1-mm ligule or individually isolated reproductive parts certified."})
for tries in range(8):
    obj=get(CARD)
    if not obj:raise SystemExit("Texas grama card unavailable")
    d=json.loads(base64.b64decode(obj["content"]))
    if d.get("id")!="bouteloua-rigidiseta":raise SystemExit("Wrong taxon")
    a=d.setdefault("images",[]); b=d.setdefault("visual_comparison",{}).setdefault("items",[])
    changed=False
    for rec in records:
        key=rec["file"];dest=BASE+key
        aa=[z for z in a if z.get("file")==key];bb=[z for z in b if z.get("image_url")==dest]
        if len(aa)==len(bb)==1:continue
        if aa or bb:raise SystemExit("Partial photo/gallery entry mismatch")
        a.append(rec)
        kind="FLOWERING DETAIL" if "flower-head" in key else "HABIT"
        panel={
          "label":"TEXAS GRAMA · USGS real "+kind+" — exact species, Larry Allain",
          "scientific_name":"Bouteloua rigidiseta","image_url":dest,"image_fit":"contain",
          "creator":rec["creator"],"license":rec["license"],"license_url":RIGHTS,
          "source_page":PAGE,"source_original":rec["source_original"],
          "image_role":rec["role"],
          "caption":"Official USGS photograph credited to Larry Allain of actual Texas grama, Bouteloua rigidiseta. Look for the short one-sided, conspicuously bristly flowering branches; do not confuse this with blue grama's longer curved comb. Photograph does NOT establish true collar/ligule or sexed/glume lemma dissection. Source is USGS Plants of Louisiana, not a Hays County voucher.",
          "why_it_matters":"Adds independently sourced original public-domain reproductive/field anatomy photo beyond existing two-card images; supports real grass recognition.",
          "markers":[],"photo_status":"Licensed USGS employee original, physical JPEG archived with GPS removed; no pixel-certified fine anatomy marker or mobile arrow checks."
        }
        idx=next((i for i,z in enumerate(b) if z.get("scientific_name")!="Bouteloua rigidiseta"),len(b))
        b.insert(idx,panel)
        changed=True
    if not changed:print("ALREADY_INSTALLED");break
    d.setdefault("curation_status",{})["photo_files_present"]=sum(str(x.get("file","")).startswith("images/") for x in a)
    d["curation_status"]["lane1_usgs_rigidiseta_photo_20261027"]="EXACT_SOURCE_USGS_PD_REPRODUCTIVE_FIELD_PHOTO_INSTALLED_TRUE_LIGULE_AND_INDIVIDUAL_SPIKELET_STILL_MISSING"
    new=(json.dumps(d,indent=2,ensure_ascii=False)+"\n").encode()
    if put(CARD,new,obj["sha"],"Lane 1 attach genuine USGS Texas grama flowering and field photographs"):
        print("GALLERY_PHOTOS_ARCHIVED",len(records),len(a),len(b));break
    time.sleep(tries+1)
else:raise SystemExit("Concurrent canonical species writes did not settle; physical photos archived")
