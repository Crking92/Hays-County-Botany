#!/usr/bin/env python3
"""Rights-gated *real* Texas Panicum hallii pressed rooted voucher archival.

Never label a pressed herbarium sheet as a live rooted field plant.
No public file is added unless individual specimen record and license
can be verified, and the original downloadable large image has sufficient resolution.
"""
import urllib.request,urllib.parse,time,re,json,io,hashlib,pathlib,html
from bs4 import BeautifulSoup
from PIL import Image,ImageOps

BASE=pathlib.Path("content/taxa/Poaceae/Panicum/panicum-hallii")
CARD=BASE/"species.json"
FILENAME="usda-ars-na0084210-blanco-county-hallii-rooted-pressed-voucher-cc0.jpg"
OUT=BASE/"images"/FILENAME
LIST="https://biocollections.ars.usda.gov/collections/list.php?country=United+States&county=Blanco&db=1&reset=1&state=Texas"
ROOT="https://biocollections.ars.usda.gov"
ORIGINAL=ROOT+"/imglib/NA/NA0084/NA0084210.jpg"
THUMB=ROOT+"/imglib/NA/NA0084/NA0084210_tn.jpg"
ACC="NA0084210"
def get(url):
    last=None
    for k in range(3):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 HaysCountyBotanyEducationalPhotoAudit/1.0"})
            with urllib.request.urlopen(req,timeout=45) as f:
                data=f.read()
                print("GET",f.status,url,len(data),flush=True)
                return data
        except Exception as e:
            last=e
            print("RETRY",k,str(e)[:160],flush=True)
            time.sleep((k+1)*4)
    raise last
def pure(raw):return " ".join(html.unescape(BeautifulSoup(raw,"html.parser").get_text(" ",strip=True)).split())

page=get(LIST)
soup=BeautifulSoup(page,"html.parser")
focus=soup.find(string=lambda x: x is not None and ACC in str(x))
assert focus, "Accession not present on government Blanco County specimen list"
parent=focus.parent
frag=""
for depth in range(5):
    frag=str(parent)
    print("LISTING HTML AT DEPTH",depth,frag[:1900],flush=True)
    parent=parent.parent if parent.parent else parent
record_candidates=re.findall(r"openIndPU\((\d+),0\)",str(focus.find_parent("tr")),re.I)
if not record_candidates:
    record_candidates=re.findall(r"(?:individual/index\.php\?occid=|openIndv\(|openOccurrence\()\s*['\"]?(\d+)",str(page.decode("utf-8",errors="replace")),re.I)
record_candidates=list(dict.fromkeys(record_candidates))
print("CANDIDATE_IDS",record_candidates,flush=True)
assert record_candidates, "Cannot derive individually verifiable specimen page: abort without copying photo"
recurl=None
for occid in record_candidates[:10]:
    url=ROOT+"/collections/individual/index.php?occid="+occid
    try:
        record=get(url)
        txt=pure(record).lower()
        if ACC.lower() in txt and "panicum hallii" in txt:
            recurl=url
            print("SPECIMEN_RIGHTS_CONTEXT",txt[max(txt.find("creative commons")-90,0):txt.find("creative commons")+400],flush=True)
            print("SPECIMEN_CC0_CONTEXT",txt[max(txt.find("cc0")-100,0):txt.find("cc0")+180],flush=True)
            assert "cc0" in txt or "creative commons zero" in txt, "Individual specimen page does not explicitly confirm CC0 reuse"
            break
    except Exception as e:
        print("CANDIDATE_REJECTED",url,str(e)[:250],flush=True)
assert recurl, "No individually verified CC0 photo rights linked to this exact Blanco County specimen"
assert ACC in pure(page) and "Panicum hallii" in pure(page)
thumbbytes=get(THUMB)
thumb=Image.open(io.BytesIO(thumbbytes));thumb.load()
print("THUMBNAIL_PIXEL_SIZE",thumb.size,flush=True)
assert thumb.width>=170 and thumb.height>=230,"Wrong thumbnail"
raw=get(ORIGINAL)
assert 250000<len(raw)<15000000,"Unexpected original bytes"
img=Image.open(io.BytesIO(raw));img.load()
print("FULL_IMAGE",img.format,img.size,flush=True)
assert img.format=="JPEG" and img.height>=2000 and img.width>=1200,"Full voucher image not adequately resolved"
sp=json.loads(CARD.read_text(encoding="utf-8"))
assert sp["id"]=="panicum-hallii"
if any(x.get("file")=="images/"+FILENAME for x in sp.get("images",[])):
    assert OUT.is_file(), "Existing record without JPEG"
    print("ALREADY_INSTALLED")
    raise SystemExit(0)
assert not OUT.exists(),"Unexpected existing bytes"
im=ImageOps.exif_transpose(img).convert("RGB")
im.thumbnail((3000,3500),Image.Resampling.LANCZOS)
OUT.parent.mkdir(parents=True,exist_ok=True)
im.save(OUT,"JPEG",quality=91,optimize=True)
photo={
 "file":"images/"+FILENAME,
 "role":"REAL vouchered pressed Panicum hallii specimen NA0084210 collected in Blanco County TX, 1986. Intact basal tuft and physical fibrous roots are connected to a flattened flowering plant, preserved against a white herbarium sheet; NOT a living field root crown or separately dissected rhizome.",
 "creator":"USDA Agricultural Research Service — U.S. National Arboretum Herbarium (voucher collected by J.K. Wipff, no. 314)",
 "license":"CC0 1.0 — specimen image-level public-domain dedication verified",
 "license_url":"https://creativecommons.org/publicdomain/zero/1.0/",
 "source_page":recurl,"source_index":LIST,
 "source_original":ORIGINAL,
 "specimen_id":ACC,"collection_date":"1986-06-27","collector":"J.K. Wipff","collector_number":"314",
 "source_locality":"Blanco County, Texas; 5.6 miles E on Ranch Road 1 from Hwy 290 (not Hays County)",
 "public_reuse":"CC0 verified on same individual specimen record; source accession and USDA herbarium explicitly credited.",
 "image_dimensions_original":[img.width,img.height],
 "image_sha256":hashlib.sha256(OUT.read_bytes()).hexdigest(),
 "image_review":"Blanco County listing and exact true-photo thumbnail visibly checked: herbarium sheet with attached dark fibrous root tuft and long branched flowering shoots. Preserved specimen only, not photographed from live soil, not a true collar micro image.",
 "modifications":"Scaled RGB original, no crop, scrubbed GPS/EXIF, preserve paper voucher accession reference and root-to-culm connection."
}
sp.setdefault("images",[]).append(photo)
panel={
 "label":"BLANCO COUNTY VOUCHER — genuine pressed grass with connected fibrous roots (USDA ARS CC0)",
 "scientific_name":"Panicum hallii",
 "image_url":"content/taxa/Poaceae/Panicum/panicum-hallii/images/"+FILENAME,
 "image_fit":"contain",
 "creator":photo["creator"],"license":photo["license"],"license_url":photo["license_url"],
 "source_page":recurl,"specimen_id":ACC,
 "image_role":"True physically connected root system of Texas Panicum hallii NA0084210 on a HERBARIUM SHEET. Not growing in soil. Do not imply field-observed active rooting from its pressed form.",
 "caption":"USDA National Arboretum Herbarium genuine 1986 Blanco County Hall's panicgrass voucher NA0084210. The pressed plant includes its rooted basal tuft and long flowering shoots. The photograph helps explain the fibrous base but is NOT a living field-root image or evidence for a 1-mm ligule.",
 "why_it_matters":"Previously the Learner had low live clumps and a real ligule/flowering macros but no visible attached species-identified roots. This preserved voucher adds true same-species connected fibrous root evidence without inventing a live crown.",
 "markers":[],
 "photo_status":"Exact photo/source/CC0 metadata verified in official record; original visibly intact basal root material in thumbnail; precision root-marker placement and mobile overlay QA intentionally pending."
}
vc=sp.setdefault("visual_comparison",{}).setdefault("items",[])
idx=next((i for i,p in enumerate(vc) if p.get("scientific_name")!="Panicum hallii"),len(vc))
vc.insert(idx,panel)
sp.setdefault("curation_status",{})["photo_files_present"]=len(sp["images"])
sp["curation_status"]["lane1_blanco_na0084210_20261027"]="CC0_ROOTED_PRESSED_BLANC0_VOUCHER_INSTALLED_LIVING_ROOT_PHOTO_STILL_MISSING"
sp.setdefault("learner_visual_status",{})["image_count"]=len(sp["images"])
sp["learner_visual_status"]["note"]="Additional authentic USDA ARS Panicum hallii pressed Blanco County voucher with connected fibrous roots physically archived. This illustrates a preserved root system but doesn't prove a living actively rooted crown; true ligule and attached/detached spikelets already photographed in separate real Uvalde sources."
sp["photo_note"]=(sp.get("photo_note","") or "")+" 2026-10-27: CC0 1986 Blanco County USDA ARS rooted pressed Panicum hallii whole voucher physically stored; true connected fibrous roots visible on herbarium sheet. Live rooted field crown still unphotographed; no fake root arrows."
CARD.write_text(json.dumps(sp,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"result":"PHOTO_ARCHIVED","path":str(OUT),"count":len(sp["images"]),"panels":len(vc),"source_page":recurl,"bytes":OUT.stat().st_size}),flush=True)
