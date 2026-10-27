#!/usr/bin/env python3
"""Guarded archival of Dave Thayer's actual Hilaria mutica fascicle photo.

No artificial anatomical assertions: whole fascicle only; individual sexed
spikelets, true inner ligule, and scale remain UNVERIFIED.
"""
import hashlib
import io
import json
import pathlib
import re
import time
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup
from PIL import Image

ROOT=pathlib.Path("content/taxa/Poaceae/Hilaria/hilaria-mutica")
CARD=ROOT/"species.json"
FILENAME="dave-thayer-azgrasses-tobosa-real-single-fascicle-educational.jpg"
FILE=ROOT/"images"/FILENAME
PAGE="https://www.azgrasses.org/pages-grasses/HH/Hilaria%20mutica.html"
RIGHTS="https://www.azgrasses.org/"
BY="Dave Thayer"
def fetch(url):
    for attempt in range(4):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (Hays County Conservation botanist field education with credit)"})
            with urllib.request.urlopen(req,timeout=50) as response:
                return response.read()
        except Exception as exc:
            print(f"fetch attempt {attempt+1}: {str(exc)[:150]}",flush=True)
            if attempt==3: raise
            time.sleep(8*(attempt+1))
    raise RuntimeError("no response")
home=BeautifulSoup(fetch(RIGHTS),"html.parser").get_text(" ",strip=True)
assert "by Dave Thayer" in home, "Cannot verify site creator"
assert "Mine are free for you to use in any way you choose" in home, "Cannot verify explicit photograph public-reuse permission"
html=BeautifulSoup(fetch(PAGE),"html.parser")
text=html.get_text(" ",strip=True)
assert "Hilaria mutica" in text and "Tobosagrass" in text, "Wrong taxon page"
assert "A Tobosagrass fascicle" in text, "Caption no longer names verified fascicle"
imgs=html.find_all("img")
print("IMAGE CANDIDATES",json.dumps([{"alt":i.get("alt",""),"src":i.get("src","")} for i in imgs],ensure_ascii=False),flush=True)
selected=[i for i in imgs if "tobosa" in (i.get("alt","").lower()) and "fascicle" in (i.get("alt","").lower())]
assert len(selected)==1, f"Ambiguous/no photo alt. Found {len(selected)} exact fascicles; do not archive unverified photo."
img=selected[0]
source_url=urllib.parse.urljoin(PAGE,img.get("src") or "")
assert source_url.startswith("https://www.azgrasses.org/"), "Image from outside expressly-authorized author's domain"
src=fetch(source_url)
assert 10000<len(src)<11000000, "Unexpected source size"
im=Image.open(io.BytesIO(src)); im.load()
print("FASCICLE SOURCE PIXELS",json.dumps({"source_url":source_url,"format":im.format,"size":im.size,"download_bytes":len(src)}),flush=True)
assert im.format in ("JPEG","PNG","WEBP") and im.width>=300 and im.height>=250, "Image not large enough for teaching"
original_size=[im.width,im.height]
d=json.loads(CARD.read_text(encoding="utf-8"))
assert d.get("id")=="hilaria-mutica"
if any(x.get("file")=="images/"+FILENAME for x in d.get("images",[])):
    assert FILE.is_file(), "Record exists but JPEG absent"
    print("Previously installed, unchanged")
    raise SystemExit(0)
assert not FILE.exists(),"Untracked file exists"
FILE.parent.mkdir(parents=True,exist_ok=True)
im.convert("RGB").save(FILE,"JPEG",quality=92,optimize=True) # remove source EXIF/GPS
photo={
 "file":"images/"+FILENAME,
 "role":"Actual detached one-fascicle macro of correctly labelled Hilaria mutica photographed and captioned by Dave Thayer. Whole fanlike papery flowering structure identifiable; three sexed spikelets NOT yet visually dissected or labelled.",
 "creator":BY,
 "license":"Photographer's express public-use permission (not Creative Commons)",
 "license_url":RIGHTS,
 "site_specific_public_permission":"DAVE_THAYER_AZGRASSES_GENERAL_PUBLIC_USE",
 "rights_text":"All photos and drawings are Dave Thayer's except a couple as indicated; author states 'Mine are free for you to use in any way you choose'. Individual H. mutica fascicle photo has no third-party photo credit on the species page.",
 "source_page":PAGE,
 "source_original":source_url,
 "source_taxon_name":"Hilaria mutica",
 "source_photo_caption":"A Tobosagrass fascicle. Note the fanned-out spoon shape of the glumes in front.",
 "public_reuse":"YES, original photographer's express reuse permission on linked homepage; credit Dave Thayer and link original.",
 "image_dimensions_original":original_size,
 "image_sha256":hashlib.sha256(FILE.read_bytes()).hexdigest(),
 "photo_review":"Caption/species and explicit author-rights verified. Whole fanned out fascicle shown per source caption; no individual central vs lateral spikelet sex or true leaf junction, scale or basal rhizome claimed. Arrow overlay withheld until post-install pixel inspection.",
 "modifications":"Original photo converted to EXIF/GPS-free JPEG preserving composition."
}
d.setdefault("images",[]).append(photo)
panel={
 "label":"ONE TRUE TOBOSA FASCICLE — real separated flowering cluster with spoon-shaped fan bracts (Dave Thayer)",
 "scientific_name":"Hilaria mutica",
 "image_url":"content/taxa/Poaceae/Hilaria/hilaria-mutica/images/"+FILENAME,
 "image_fit":"contain",
 "image_role":"Photographer-labelled real Tobosagrass fascicle close-up, distinct from photos of an entire flowering head. Papery, fan-shaped structures visible; no artificially separated sexed spikelets.",
 "caption":"Dave Thayer's close-up of ONE detached Hilaria mutica fascicle: the spoon-shaped, outward-flaring papery glumes are the practical clue. This is a complete fascicle view, not a dissection proving the position or sex of each of its three spikelets. The author also publishes a different-species galleta comparison.",
 "why_it_matters":"A source-labelled macro of one actual reproductive cluster bridges the gap between an entire Tobosa head and the anatomy a learner must study with a hand lens. A further photographed dissection with millimeter scale is still required for individual spikelet and floret assignments.",
 "creator":BY,
 "license":"Photographer's express public-use permission (not Creative Commons)",
 "license_url":RIGHTS,
 "site_specific_public_permission":"DAVE_THAYER_AZGRASSES_GENERAL_PUBLIC_USE",
 "source_page":PAGE,
 "markers":[],
 "photo_status":"Real one-fascicle photo archived after source and photographer-rights check, but precise anatomical arrows and independent mobile overlay QA intentionally pending."
}
items=d.setdefault("visual_comparison",{}).setdefault("items",[])
assert not any(p.get("image_url")==panel["image_url"] for p in items),"Panel already present"
at=next((i for i,p in enumerate(items) if p.get("scientific_name")!="Hilaria mutica"),len(items))
items.insert(at,panel)
d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
d["learner_visual_status"]["note"]="Eleven archived Tobosa photos, ten eligible for public site and one NC research hold, including Dave Thayer's actual individual detached fascicle macro. The true ligule, fully separated central-versus-lateral sexed spikelets and rooted rhizome photo remain absent."
d.setdefault("curation_status",{})["photo_files_present"]=len(d["images"])
d["curation_status"]["lane1_tobosa_real_single_fascicle_dave_thayer_20261027"]="PHOTO_ARCHIVED_WITH_AUTHOR_EXPLICIT_PUBLIC_REUSE_NOT_INDIVIDUAL_SEXED_SPIKELET_DISSECTION"
d["photo_note"]=d.get("photo_note","")+" 2026-10-27: Dave Thayer's personally photographed genuine whole Tobosa fascicle archived using author's explicit general reuse permission. Individual sexed triad dissection and true leaf ligule remain OPEN."
d.setdefault("field_photo_quickcheck",{})["warning"]="Eleven archived Tobosa species photos, one noncommercial-only held. Dave Thayer's detached whole fascicle picture improves true flower-cluster recognition, but the sex of individual spikelets remains unverified. 0.5-2mm true inner ligule and attached scaly rhizome still not photographed; mobile QA outstanding."
CARD.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"result":"PHOTO_ARCHIVED","url":source_url,"file":str(FILE),"size":original_size,"images":len(d["images"]),"panels":len(items),"sha256":photo["image_sha256"]}))
