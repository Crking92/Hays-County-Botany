#!/usr/bin/env python3
"""Archive one exact-species Tobosa close flowering photo with CC BY 4.0 provenance.

Gross flared and veined papery bracts only; do not infer visible ligule,
dissected glumes, individual bisexual/staminate spikelets or rooted rhizome.
"""
import hashlib, io, json, pathlib, time, urllib.request
from PIL import Image

base=pathlib.Path("content/taxa/Poaceae/Hilaria/hilaria-mutica")
card=base/"species.json"
name="alex-abair-tobosa-strong-veined-papery-fans-ccby4.jpg"
dest=base/"images"/name
page="https://commons.wikimedia.org/wiki/File:Hilaria_mutica_24533040.jpg"
original="https://upload.wikimedia.org/wikipedia/commons/3/37/Hilaria_mutica_24533040.jpg"
photo_source="https://www.inaturalist.org/photos/24533040"
obs="https://www.inaturalist.org/observations/16328080"
d=json.loads(card.read_text(encoding="utf-8"))
assert d["id"]=="hilaria-mutica"
if dest.exists() and any(i.get("file")=="images/"+name for i in d.get("images",[])):
    print("Photo already installed; no duplicate")
    raise SystemExit(0)
assert not dest.exists(), "Unexpected existing binary at target path"
assert not any(i.get("source_page")==page or i.get("source_original")==original for i in d.get("images",[])), "Source already used"

raw=None
for attempt in range(4):
    try:
        req=urllib.request.Request(original,headers={"User-Agent":"HaysCountyBotanyFieldLearner/1.0 (source-credited Wikimedia image archival)"})
        with urllib.request.urlopen(req,timeout=60) as response:
            raw=response.read()
        break
    except Exception as e:
        print("Download attempt failed",attempt+1,str(e),flush=True)
        if attempt==3: raise
        time.sleep(8*(attempt+1))
assert raw and 100000<len(raw)<6000000,"Unexpected image payload"
im=Image.open(io.BytesIO(raw));im.load()
assert im.format=="JPEG" and im.size==(1536,2048), "Unexpected source version; inspect before publication"
im=im.convert("RGB")
dest.parent.mkdir(parents=True,exist_ok=True)
im.save(dest,"JPEG",quality=93,optimize=True)
newfile={
  "file":"images/"+name,
  "role":"REAL exact-species maturing Tobosa flowering-head close-up. Shows broad fan-shaped, visibly longitudinally veined papery bracts flaring from successive attached groups; no individually separated sexed triad and no ligule.",
  "creator":"Alex Abair",
  "license":"CC BY 4.0",
  "license_url":"https://creativecommons.org/licenses/by/4.0/",
  "source_page":page,
  "source_original":original,
  "source_photo_page":photo_source,
  "source_observation":obs,
  "source_region":"Near southern New Mexico desert, original observation 2018-09-08. Not Hays County.",
  "license_evidence":"Individual Wikimedia Commons original file page verified 2026-10-27: author Alex Abair, CC BY 4.0, iNaturalistReviewBot photo-level check.",
  "photo_review":"Original 1536x2048 pixels visually checked: multiple actually flared fan-shaped papery pieces with conspicuous parallel veins along the attached head, blue sky behind. Individual glume vs lemma insertion, central vs lateral sexed spikelets, true ligule, rhizome, and measurement scale NOT proven.",
  "public_reuse":"CC BY 4.0 permitted with photographer attribution, source link, license link, and modification notice.",
  "image_sha256":hashlib.sha256(dest.read_bytes()).hexdigest(),
  "image_dimensions":[1536,2048],
  "modifications":"JPEG re-encoded without EXIF/GPS, no crop or annotations burned into source image"
}
d.setdefault("images",[]).append(newfile)
panel={
 "label":"NEW CLEAR PAPERY FANS — Tobosa attached veined flowering structures (Alex Abair)",
 "scientific_name":"Hilaria mutica",
 "image_url":"content/taxa/Poaceae/Hilaria/hilaria-mutica/images/"+name,
 "image_fit":"contain",
 "creator":"Alex Abair",
 "license":"CC BY 4.0",
 "license_url":"https://creativecommons.org/licenses/by/4.0/",
 "source_page":page,
 "image_role":"Real 1536×2048 source-verified macro showing multiple attached spread-out fanlike, strongly veined pale reproductive bracts (not dissected parts).",
 "caption":"Tobosa head photographed by Alex Abair in New Mexico. Follow the successive large, flared, paperlike and visibly parallel-veined pieces against blue sky. Do NOT label a particular visible part as central fertile glume, lateral male spikelet, lemma, or individual measured triad without a real dissection.",
 "why_it_matters":"Clearer species-specific reproductive structural photo than typical distant seedheads. The fans distinguish Tobosa's flowering architecture and show exactly where an expert needs to separate an individual cluster under a hand lens.",
 "markers":[
  {"label":"Flared veined papery flower bracts", "label_x":2,"label_y":13,"target_x":38,"target_y":29},
  {"label":"Another attached papery fan", "label_x":72,"label_y":83,"target_x":44,"target_y":62}
 ],
 "photo_status":"Source and CC BY 4.0 verified. Original photo visibly reviewed, arrow labels refer only to gross attached papery fans; individual anatomical boundaries and mobile arrow-render alignment UNCONFIRMED."
}
items=d.setdefault("visual_comparison",{}).setdefault("items",[])
assert not any(p.get("image_url")==panel["image_url"] for p in items)
cmp_idx=next((i for i,p in enumerate(items) if p.get("scientific_name")!="Hilaria mutica"),len(items))
items.insert(cmp_idx,panel)
d.setdefault("curation_status",{})["photo_files_present"]=len(d["images"])
d["curation_status"]["lane1_abair_tobosa_papery_fans_20261027"]="REAL_CC_BY4_HIGH_RES_ATTACHED_FANS_ARCHIVED_TRUE_LIGULE_TRIAD_STILL_OPEN"
d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
d["learner_visual_status"]["note"]="Ten local Tobosa image records, nine public-eligible and one NC research hold; new Alex Abair 1536×2048 veined papery fans photo among real flowering close-ups. True free ligule 0.5–2 mm, sexed central/lateral triad, and rhizome macro still missing."
d["photo_note"]=d.get("photo_note","")+" 2026-10-27: high-res genuine Alex Abair CC BY 4.0 veined Tobosa flowering fans added as real anatomical context with two gross labels; exact individual glume/lemma, inner ligule, and triad sex arrangement unresolved."
d.setdefault("last_mile_diagnostic_photo_hold_20261023",{})["source_photos_currently_verified"]=len(d["images"])
q=d.get("field_photo_quickcheck",{})
q["warning"]="Ten Tobosa photo records physically archived, nine public eligible and one CC BY-NC research hold; nine same-species visual teaching panels plus one different-species curlymesquite look-alike public eligible. Real gross arrows only; no true inner 0.5–2 mm lacerate ligule, dissected sexed three-spikelet fascicle, excavated rootstock or independently verified mobile Pages overlay."
card.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"archived":str(dest),"sha256":newfile["image_sha256"],"images":len(d["images"]),"panels":len(items),"public_species_photos":sum(i.get("public_gallery_eligibility")!="HOLD_CC_BY_NC" for i in d["images"])}))
