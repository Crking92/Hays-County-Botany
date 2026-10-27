#!/usr/bin/env python3
"""Archive real Panicum hallii flowering and loose mature units from
Jim Conrad 2014 Uvalde TX; scientific roles only on actually visible pixels.
"""
import io,json,time,pathlib,urllib.request,hashlib,re,html
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Panicum/panicum-hallii")
card=base/"species.json"
page="https://www.backyardnature.net/n/h/panic-2.htm"
permission="https://www.backyardnature.net/j/copyrite.htm"
d=json.loads(card.read_text(encoding="utf-8"))
assert d["id"]=="panicum-hallii" and len(d.get("images",[]))>=6, "Unexpected scientific card state"
def get(url):
    for k in range(4):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyFieldLearner/1.0 (public-domain Jim Conrad photo reuse, credit retained)"})
            with urllib.request.urlopen(req,timeout=50) as response: return response.read()
        except Exception as e:
            print("retry",k,str(e),flush=True)
            if k==3: raise
            time.sleep(5*(k+1))
txt=lambda b:" ".join(html.unescape(re.sub(r"<[^>]+>"," ",b.decode("utf-8",errors="replace"))).split())
s=txt(get(page));rights=txt(get(permission))
assert "HALL'S PANICUM" in s and "Panicum" in s and "several-ribbed glume" in s, "Author ID/repro caption missing"
assert "PUBLIC DOMAIN" in rights.upper() and "images produced by myself" in rights.lower(),"Photographer PD author rights not established"
items=[
 {
  "filename":"jim-conrad-hallii-uvalde-attached-ribbed-spikelets-pd.jpg",
  "src":"https://www.backyardnature.net/n/14/140831po.jpg",
  "size":[499,579],
  "role":"ACTUAL photographed attached maturing Panicum hallii ribbed pale green spikelets on narrow connected branching flowering stalk and slender pedicels; original source photographer Jim Conrad, Uvalde TX.",
  "label":"UVALDE TRUE SPIKELET CLOSEUP — attached green veined flowering units and narrow pedicels",
  "caption":"Actual Hall's panicgrass (*Panicum hallii*) in northern Uvalde County, Texas. See the narrowly pointed green oval spikelets, conspicuous multiple ribs on an enclosing bract, and small stalks attaching them to a branching panicle. This is not a dissected glume, lemma or 1-mm measurement.",
  "markers":[
    {"label":"Attached ribbed spikelet", "label_x":1,"label_y":28,"target_x":42,"target_y":45},
    {"label":"Slender spikelet-bearing pedicel","label_x":55,"label_y":10,"target_x":59,"target_y":24}
  ],
  "anatomy":"actual spikelets and their attachment (not individually separated glumes or sexed florets)"
 },
 {
  "filename":"jim-conrad-hallii-uvalde-detached-mature-spikelets-hand-pd.jpg",
  "src":"https://www.backyardnature.net/n/14/140831pq.jpg",
  "size":[454,300],
  "role":"ACTUAL naturally detached maturing Panicum hallii spikelet-sized papery reproductive units resting on the source photographer's fingertip, with pale enclosing bracts visibly folded, no physical mm ruler.",
  "label":"UVALDE TRUE DETACHED UNITS — pale mature ribbed spikelet bracts against fingertip",
  "caption":"Three actual separated, dry or drying Hall's panicgrass flowering units on a fingertip from the same Uvalde source treatment. This demonstrates pale papery enclosing structures on a mature spikelet; not a full glume-versus-lemma dissection or calibrated millimeter-size measurement.",
  "markers":[
    {"label":"Detached mature papery unit","label_x":47,"label_y":83,"target_x":41,"target_y":74}
  ],
  "anatomy":"naturally detached pale mature units, not anatomically separated parts of one glume/lemma."
 }
]
added=[]
for x in items:
    target=base/"images"/x["filename"]
    rel="images/"+x["filename"]
    if any(p.get("file")==rel for p in d["images"]):
        assert target.is_file(), "Photo metadata exists but bytes absent"
        print("already installed",rel,flush=True)
        continue
    assert not target.exists() and not any(p.get("source_original")==x["src"] for p in d["images"]), "Existing source duplicate"
    raw=get(x["src"])
    assert 15000<len(raw)<2000000, f"Unexpected image payload {len(raw)}"
    im=Image.open(io.BytesIO(raw));im.load()
    assert im.format=="JPEG" and im.size==tuple(x["size"]),f"Unexpected image version {im.size}"
    target.parent.mkdir(parents=True,exist_ok=True)
    im.convert("RGB").save(target,"JPEG",quality=94,optimize=True)
    photo={
      "file":rel,"role":x["role"],"creator":"Jim Conrad",
      "license":"Public domain — original photographer's express release",
      "license_url":permission,"source_permission_page":permission,
      "source_page":page,"source_original":x["src"],
      "source_taxon_name":"Panicum hallii Vasey",
      "source_locality":"Juniper House, northern Uvalde County, Edwards Plateau, Texas (2014-08-31), NOT Hays County",
      "public_reuse":"YES: original source author Jim Conrad explicitly dedicates his own images to public domain; source, creator and URL credited.",
      "image_dimensions":[im.width,im.height],
      "image_sha256":hashlib.sha256(target.read_bytes()).hexdigest(),
      "photo_review":"The original source pixel image was reviewed: "+x["anatomy"]+" No 1-mm scale or isolated fertile lemma/glume dissection inferred.",
      "modifications":"RGB JPEG re-encoded with GPS/EXIF stripped, no subject crop, arrows are non-destructive gallery overlay."
    }
    d["images"].append(photo)
    p={
      "label":x["label"],
      "scientific_name":"Panicum hallii",
      "image_url":"content/taxa/Poaceae/Panicum/panicum-hallii/"+rel,
      "image_fit":"contain","creator":"Jim Conrad",
      "license":photo["license"],"license_url":permission,
      "source_page":page,
      "image_role":x["role"],"caption":x["caption"],
      "why_it_matters":"Genuine local-region anatomy, not a distant whole-plant repeat. Complements the already archived white hair-fringe inner ligule and Patrick Alexander's shiny fruits.",
      "markers":x["markers"],
      "photo_status":"Original source pixels reviewed for shown gross structures; no individually dissected glume/lemma ID, physical millimeter ruler or rooted crown. Web arrow overlay/mobile page QA separate."
    }
    panels=d.setdefault("visual_comparison",{}).setdefault("items",[])
    assert not any(z.get("image_url")==p["image_url"] for z in panels)
    ins=next((i for i,z in enumerate(panels) if z.get("scientific_name")!="Panicum hallii"),len(panels))
    panels.insert(ins,p)
    added.append({"file":x["filename"],"bytes":target.stat().st_size})
d.setdefault("curation_status",{})["photo_files_present"]=len(d["images"])
d["curation_status"]["lane1_hallii_conrad_attached_detached_macro_20261027"]="TWO_REAL_PUBLIC_DOMAIN_UVALDE_REPRODUCTIVE_MACROS_LOCAL_AND_ANNOTATED_LIGULE_ALREADY_PRESENT"
d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
d["learner_visual_status"]["note"]="Eight actual Hall's panicgrass local photos and one different-species witchgrass look-alike. Uvalde field habit, true inner hair-fringed ligule and now attached veined reproductive units + detached mature spikelets photographed; true mm glume and rooted crown still incomplete."
q=d.get("field_photo_quickcheck")
if q:
    q["steps"].append("NEW ACTUAL UVALDE MACRO: Jim Conrad photographed attached green narrow spikelets with repeated veins and separate detached pale mature units on a fingertip. Neither proves exact glume, fertile lemma or 1-mm spikelet size; do not add invisible arrows.")
    q["warning"]="Eight exact Hall's panicgrass archived photos, one different-species witchgrass comparator. Source-verified Uvalde true hairy ligule, attached ribbed green spikelets and detached mature pale units now locally archived. A rooted basal crown and a 1-mm scale plus individually dissected glumes/lemmas remain absent. Site/mobile arrow QA separate."
d["photo_note"]=(d.get("photo_note") or "")+" 2026-10-27: two authentic public-domain Jim Conrad Panicum hallii Uvalde TX reproductive macro photos archived (attached ribbed spikelets, detached mature units on fingertip). Three conservative arrows on visible structures. No species substitution, no claim of microscopic glume/lemma separation or ruler.";
card.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"added":added,"archived_total":len(d["images"]),"panels_total":len(d["visual_comparison"]["items"])}))
