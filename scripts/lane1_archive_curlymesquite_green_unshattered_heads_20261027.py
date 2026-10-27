#!/usr/bin/env python3
"""Archive species-specific green unshattered curlymesquite reproductive heads.

Copyright: original Patrick Alexander CC0; keep source and license.
No invented sexed central/lateral spikelet, ligule, glume/lemma or true rooted node.
"""
import io,json,pathlib,hashlib,time,urllib.request
from PIL import Image
ROOT=pathlib.Path("content/taxa/Poaceae/Hilaria/hilaria-belangeri")
CARD=ROOT/"species.json"
FILENAME="patrick-alexander-curlymesquite-three-green-intact-heads-cc0.jpg"
DEST=ROOT/"images"/FILENAME
PAGE="https://commons.wikimedia.org/wiki/File:Hilaria_belangeri_-_Flickr_-_aspidoscelis_(1).jpg"
ORIGINAL="https://upload.wikimedia.org/wikipedia/commons/4/49/Hilaria_belangeri_-_Flickr_-_aspidoscelis_%281%29.jpg"
d=json.loads(CARD.read_text(encoding="utf-8"))
assert d["id"]=="hilaria-belangeri"
if any(p.get("file")=="images/"+FILENAME for p in d["images"]):
    assert DEST.exists(),"Previously cited file absent"
    print("ALREADY_ARCHIVED")
    raise SystemExit(0)
assert not DEST.exists() and not any(p.get("source_page")==PAGE for p in d["images"])
raw=None
for n in range(4):
    try:
        request=urllib.request.Request(ORIGINAL,headers={"User-Agent":"HaysCountyBotanyFieldLearner/1.0 Commons CC0 exact original"})
        with urllib.request.urlopen(request,timeout=55) as resp:
            raw=resp.read()
        break
    except Exception as e:
        print("RETRY",n+1,str(e)[:150],flush=True)
        if n==3: raise
        time.sleep(5*(n+1))
assert raw and 700000<len(raw)<5000000,"Unexpected image source bytes"
im=Image.open(io.BytesIO(raw));im.load()
assert im.format=="JPEG" and im.size==(3600,2400),f"Unexpected original size {im.size}"
im=im.convert("RGB")
im.thumbnail((2500,2000),Image.Resampling.LANCZOS)
DEST.parent.mkdir(parents=True,exist_ok=True)
im.save(DEST,"JPEG",quality=93,optimize=True)
d["images"].append({
 "file":"images/"+FILENAME,
 "role":"Actual close original Hilaria belangeri with THREE intact narrow green/lime-to-purple/brown young maturing spikes showing tiered attached unopened cluster units and residual pale fine flower filaments; not a separated flowering triad.",
 "creator":"Patrick Alexander",
 "license":"CC0 1.0",
 "license_url":"https://creativecommons.org/publicdomain/zero/1.0/",
 "source_page":PAGE,
 "source_original":ORIGINAL,
 "source_flickr_photo":"https://www.flickr.com/photos/aspidoscelis/24126379618/",
 "source_taxon_name":"Hilaria belangeri",
 "source_region":"Grant County, New Mexico, 2017-08-13, not Hays County",
 "public_reuse":"CC0 1.0 confirmed at individual Wikimedia Commons file via FlickrReviewR; voluntary original photographer credit preserved.",
 "photo_review":"Actual 3600×2400 source visually inspected: three sharply resolved erect intact green/purple terminal flowering heads of Hilaria belangeri, tip and successive overlapping reproductive groups visible. No true ligule/inner blade–sheath junction, exact sexed three-spikelet parts, scale or rooting node.",
 "image_dimensions_original":[3600,2400],
 "image_dimensions_stored":[im.width,im.height],
 "image_sha256":hashlib.sha256(DEST.read_bytes()).hexdigest(),
 "modifications":"Downscaled and GPS/EXIF scrubbed; original scene not cropped, two non-destructive gross anatomical arrow overlays."
})
panel={
 "label":"GREEN INTACT CURLYMESQUITE FLOWERING HEADS — three real overlapping unshattered spikes (CC0)",
 "scientific_name":"Hilaria belangeri",
 "image_url":"content/taxa/Poaceae/Hilaria/hilaria-belangeri/images/"+FILENAME,
 "image_fit":"contain",
 "creator":"Patrick Alexander",
 "license":"CC0 1.0",
 "license_url":"https://creativecommons.org/publicdomain/zero/1.0/",
 "source_page":PAGE,
 "image_role":"Three actual intact tight green-to-purple terminal flowering spikes of curlymesquite, each repeated scale-like flowering cluster remains attached to central narrow axis. No detached glume/lemma or separated sexed triad.",
 "caption":"Actual green, partly purple unopened-to-maturing curlymesquite heads from New Mexico. Trace the three upright spikes: repeated green papery flowering clusters remain tight and attached. Compare these with the separately archived mature pale fan-shaped units and detached clusters later in the Learner. The three HEADS shown here are NOT the three spikelets inside one microscopic fascicle.",
 "why_it_matters":"Distinguishes real green head stage from red older and pale opened curlymesquite clusters. Prevents learners mistaking three separate upright inflorescences for a three-spikelet reproductive cluster.",
 "markers":[
  {"label":"Unshattered green flowering units","label_x":2,"label_y":34,"target_x":26,"target_y":46},
  {"label":"Repeated units along intact narrow head","label_x":70,"label_y":12,"target_x":50,"target_y":37}
 ],
 "photo_status":"Exact original viewed: arrows placed only on visible gross attached flowering units, not imaginary central bisexual or lateral staminate spikelet anatomy; mobile arrow QA pending."
}
items=d.setdefault("visual_comparison",{}).setdefault("items",[])
idx=next((i for i,p in enumerate(items) if p.get("scientific_name")!="Hilaria belangeri"),len(items))
items.insert(idx,panel)
d.setdefault("curation_status",{})["photo_files_present"]=len(d["images"])
d["curation_status"]["lane1_green_unshattered_curlymesquite_20261027"]="CC0_REAL_EARLY_GREEN_THREE_HEADS_ARCHIVED_TWO_GROSS_ARROWS_TRUE_LIGULE_DISSECTION_STILL_MISSING"
d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
d["learner_visual_status"]["note"]="Thirteen genuine H. belangeri source-labelled archived photos, including actual unshattered green spikes, purple attached heads, mature pale clusters, detached full units and real aboveground stolons. True inner 0.5–1mm membrane, connected roots at a verified stolon node and individually dissected sexed triad are STILL UNPHOTOGRAPHED."
d["photo_note"]=(d.get("photo_note","") or "")+" 2026-10-27: added Patrick Alexander original green still-attached curlymesquite flowering head close CC0, two gross arrows. Three entire green flowering heads ≠ the species' three-individual-spikelet fascicle; do not confuse them."
q=d.get("field_photo_quickcheck")
if q:
    q["steps"].append("UNSHATTERED GREEN HEAD PHOTO: another real Patrick Alexander original compares three entire green-to-purple immature heads with separate older pale opened clusters. Three heads pictured are NOT an anatomical three-spikelet cluster: that needs a dissected individual unit with mm scale.")
    q["warning"]="13 physically archived real curlymesquite photos, one separately labelled Tobosa comparison. Actual distinct green, purple-red and pale open head stages and connected aboveground stolons documented. True inner 0.5–1mm ligule, verified rooted stolon node and individually separated fertile/staminate spikelets remain OPEN. Live/mobile QA pending."
CARD.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"result":"ARCHIVED_CC0_UNSHATTERED_HILARIA_BELANGERI","photos":len(d["images"]),"panels":len(items),"file":str(DEST),"bytes":DEST.stat().st_size,"new_arrows":len(panel["markers"])}),flush=True)
