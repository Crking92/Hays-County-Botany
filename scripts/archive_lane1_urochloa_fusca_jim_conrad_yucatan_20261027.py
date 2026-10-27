#!/usr/bin/env python3
"""Archive 2 licensed actual Urochloa cf. fusca field detail photos,
with honest provisional 2019 Yucatan taxon uncertainty.

Not verified same-species anatomy: author himself describes the identification
as tentative, so we must never use these as certified definitive U. fusca.
"""
import io,json,hashlib,pathlib,time,urllib.request, re, html
from PIL import Image
BASE=pathlib.Path("content/taxa/Poaceae/Urochloa/urochloa-fusca")
CARD=BASE/"species.json"
PAGE="https://www.backyardnature.net/n/h/urochloa.htm"
PERM="https://www.backyardnature.net/j/copyrite.htm"
def get(url):
    for attempt in range(4):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotanyCrewFieldLearner/1.0; species ID and photo rights verification"})
            with urllib.request.urlopen(req,timeout=45) as res:
                return res.read()
        except Exception as e:
            print("Attempt",attempt+1,"failed",str(e),flush=True)
            if attempt==3: raise
            time.sleep(5*(attempt+1))
def decoded(x):
    raw=x.decode("utf-8",errors="replace")
    without_tags=re.sub(r"<[^>]+>"," ",raw)
    return " ".join(html.unescape(without_tags).split())
page_text=decoded(get(PAGE))
permission_text=decoded(get(PERM))
assert "put into the PUBLIC DOMAIN all images produced by myself" in permission_text, "No verified photographer permission"
assert "I've had a hard time convincing myself" in page_text and "I've settled on the ID mostly" in page_text, "Original uncertainty not captured"
assert "These nodes on the stem" in page_text or "adventitious roots" in page_text, "Original node description absent"
assert "spikelets are a little larger" in page_text, "Original scaled-spikelet caption absent"
sp=json.loads(CARD.read_text(encoding="utf-8"))
assert sp["id"]=="urochloa-fusca"
items=[
 {
  "file":"images/jim-conrad-yucatan-urochloa-cf-fusca-measured-whole-spikelets-pd.jpg",
  "original":"https://www.backyardnature.net/n/19/190301uu.jpg",
  "role":"TENTATIVE-TAXON reference: actual author's Urochloa cf. fusca 2019 Yucatan two entire mature spikelets placed beside real mm ruler. Whole spikelet length visually measurable; glume/lemma boundaries not dissected.",
  "panel_label":"PROVISIONAL SPECIES DETERMINATION — two real signalgrass spikelets beside millimeter scale",
  "photo_review":"Original author explains 2019 Yucatan Urochloa fusca identification remained difficult / elimination-based; open reference of measurable WHOLE signalgrass spikelets, NOT proof these are U. fusca or individual glume lengths.",
  "markers":[
   {"label":"Whole spikelet beside real millimeter marks","label_x":1,"label_y":11,"target_x":19,"target_y":41},
   {"label":"Second whole spikelet at same scale","label_x":45,"label_y":83,"target_x":68,"target_y":53}
  ],
  "caption":"Jim Conrad photographed two real signalgrass spikelets with a physical millimeter ruler in Yucatán. Important: the author was uncertain about this plant's U. fusca identification. Use as a demonstration of HOW to measure complete spikelets, not proof of exact U. fusca anatomy or glume identity.",
  "why":"This directly models a necessary field action: comparing actual entire mature spikelets to true 1-mm divisions instead of guessing the length from a fuzzy seedhead."
 },
 {
  "file":"images/jim-conrad-yucatan-urochloa-cf-fusca-protruding-root-initials-pd.jpg",
  "original":"https://www.backyardnature.net/n/19/190301ux.jpg",
  "role":"TENTATIVE-TAXON reference: actual swollen root structures (early adventitious roots or root initials) protruding from a cut-looking lower creeping grass stem node. Identification in author source Urochloa cf. fusca uncertain, and rooting into soil not pictured.",
  "panel_label":"PROVISIONAL SPECIES DETERMINATION — real adventitious root beginnings at a creeping grass node",
  "photo_review":"Actual image inspected: brownish lower stem structure plus at least two fleshy protruding root beginnings. Visible features do not prove roots penetrated ground or species identity; author says ID uncertain.",
  "markers":[
   {"label":"Visible emerging adventitious roots","label_x":1,"label_y":79,"target_x":45,"target_y":76},
   {"label":"Root initials at lower stem/node region","label_x":62,"label_y":12,"target_x":49,"target_y":63}
  ],
  "caption":"Actual lower-stem node with protruding early adventitious roots from a signalgrass Jim Conrad provisionally called Urochloa fusca in Yucatán. The source openly cautions that the taxon ID is uncertain; this is therefore an example of a rooting feature to seek, NOT confirmed species-specific U. fusca evidence or an intact root-to-soil connection.",
  "why":"Shows what a developing root at a decumbent stem node can look like; do not equate an exposed root initial with proof of a fully rooted living U. fusca plant."
 }
]
for q in items:
    local=BASE/q["file"]
    if local.exists() and any(p.get("file")==q["file"] for p in sp.get("images",[])):
        print("Already installed:",q["file"],flush=True)
        continue
    assert not local.exists(),"Unexpected existing target image file"
    assert not any(x.get("source_original")==q["original"] for x in sp.get("images",[])), "Duplicate licensed source"
    raw=get(q["original"])
    assert 8000<len(raw)<4000000,"Unexpected photo byte size"
    im=Image.open(io.BytesIO(raw));im.load()
    assert im.format=="JPEG" and im.width>=450 and im.height>=280, f"Not suitable teaching photo: {im.size}"
    local.parent.mkdir(parents=True,exist_ok=True)
    im.convert("RGB").save(local,"JPEG",quality=95,optimize=True)
    metadata={
     "file":q["file"],"role":q["role"],"creator":"Jim Conrad",
     "license":"Public domain — express dedication by original photographer (source site)",
     "license_url":PERM,"source_permission_page":PERM,
     "source_page":PAGE,"source_original":q["original"],
     "source_taxon_name":"Urochloa cf. fusca — author's determination TENTATIVE",
     "source_region":"Yucatán, Mexico, March 2019 (NOT Texas)",
     "taxon_verification_status":"TENTATIVE_IDENTIFICATION_AUTHOR_ACKNOWLEDGED_UNCERTAINTY",
     "photo_review":q["photo_review"],
     "public_reuse":"Confirmed Jim Conrad original images on author's source page are public domain by personal declaration; scientific identity provisional",
     "modifications":"RGB JPEG recompression for public learning, no physical image crop, GPS/EXIF removed",
     "image_dimensions":[im.width,im.height],
     "image_sha256":hashlib.sha256(local.read_bytes()).hexdigest()
    }
    sp.setdefault("images",[]).append(metadata)
    panel={
     "label":q["panel_label"],
     "scientific_name":"Urochloa cf. fusca (author uncertain)",
     "image_url":"content/taxa/Poaceae/Urochloa/urochloa-fusca/"+q["file"],
     "image_fit":"contain","image_role":q["role"],
     "caption":q["caption"],"why_it_matters":q["why"],
     "creator":"Jim Conrad","license":metadata["license"],"license_url":PERM,
     "source_page":PAGE,"source_original":q["original"],
     "markers":q["markers"],
     "taxon_verification_status":metadata["taxon_verification_status"],
     "photo_status":"PUBLIC RIGHTS VERIFIED but species determination UNCONFIRMED; actual root structures or whole spikelets labelled without species-level certifying claims. Overlay mobile QA pending."
    }
    vc=sp.setdefault("visual_comparison",{}).setdefault("items",[])
    assert not any(x.get("image_url")==panel["image_url"] for x in vc)
    idx=next((i for i,x in enumerate(vc) if x.get("scientific_name")=="Urochloa reptans"),len(vc))
    vc.insert(idx,panel)
    print(json.dumps({"new_photo":q["file"],"size":im.size,"sha256":metadata["image_sha256"]}),flush=True)
sp.setdefault("curation_status",{})["photo_files_present"]=len(sp["images"])
sp["curation_status"]["lane1_jim_conrad_yucatan_cf_fusca_20261027"]="TWO_REAL_PUBLIC_DOMAIN_GROSS_PHOTOS_INSTALLED_AUTHOR_SPECIES_ID_TENTATIVE_NOT_CERTIFIED";
sp.setdefault("learner_visual_status",{})["image_count"]=len(sp["images"])
sp["learner_visual_status"]["note"]="Seven locally hosted subject and cf. subject photo records: 4 definitively labelled public U. fusca, 2 tentative Urochloa cf. fusca from Yucatan, one U. fusca CC BY-NC rights hold. Texas inner ligule and reproductive macro are strongest definitive lessons, foreign tentative images demonstrate root beginnings and real mm ruler without adding a verified species diagnostic role."
sp["photo_note"]=(sp.get("photo_note") or "")+" 2026-10-27: Two genuine rights-clear 2019 Yucatan Jim Conrad physical macro images added as 'cf. fusca' with author species ID explicitly tentative; photographed root initials and mm-scaled entire spikelets, NOT proof of exact U. fusca rooting anatomy, glume identities, or morphometrics."
sp.setdefault("field_photo_quickcheck",{})["steps"].append("OPTIONAL ADVANCED REFERENCE: two 2019 Yucatán Jim Conrad photos show true ruler comparisons and early roots on a creeping node, but the photographer himself was uncertain they were U. fusca. They are marked Urochloa cf. fusca and do not certify a diagnostic role.")
CARD.write_text(json.dumps(sp,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"local_photos":len(sp["images"]),"panels":len(sp["visual_comparison"]["items"]),"held_photos":sum(x.get("public_gallery_eligibility")=="HOLD_CC_BY_NC" for x in sp["images"])}))
