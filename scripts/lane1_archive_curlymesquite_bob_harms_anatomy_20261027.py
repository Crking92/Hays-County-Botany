#!/usr/bin/env python3
"""Archive four genuine species-specific Hilaria belangeri Bob Harms photographs.

CC-free explicit scientific/educational reuse only, author credit mandatory.
No generic ligules, no false membrane annotation, no unsourced anatomy arrows.
"""
import io,json,time,pathlib,hashlib,urllib.request,html
from bs4 import BeautifulSoup
from PIL import Image,ImageOps

ROOT="https://w3.biosci.utexas.edu/prc/Monocots/"
IDX=ROOT+"GrassHTML/data/Hilaria-text.html"
FROOT=ROOT+"GrassHTML/data/images/"
PAGE=ROOT+"GrassHTML/data/pages/"
BASE=pathlib.Path("content/taxa/Poaceae/Hilaria/hilaria-belangeri")
CARD=BASE/"species.json"

def get(url):
    for n in range(4):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotanyEducationalFieldLearner/1.0 (photo credit Bob Harms)"})
            with urllib.request.urlopen(req,timeout=50) as r: return r.read()
        except Exception as e:
            print("FETCH_RETRY",url,n,str(e)[:140],flush=True)
            if n==3:raise
            time.sleep(4*(n+1))
def clean(buf):
    return " ".join(html.unescape(BeautifulSoup(buf,"html.parser").get_text(" ",strip=True)).split())
rights=clean(get(ROOT))
assert "All Selected Monocots images and web pages are copyrighted by Bob Harms" in rights, "No author credit statement"
assert "free for scientific and educational uses provided that Bob Harms is properly credited" in rights, "No explicit relevant reuse permission"
catalog=clean(get(IDX))
for term in ["H. belangeri (curlymesquite ) - Spikelet detail","H. belangeri (curlymesquite ) - Stolons","H. belangeri (curlymesquite ) - Ligule/sheath"]:
    assert term in catalog, f"Source catalogue caption not confirmed: {term}"
d=json.loads(CARD.read_text(encoding="utf-8"))
assert d["id"]=="hilaria-belangeri" and len(d["images"])>=13, "Species inventory unexpectedly changed"
TO_INSTALL=[
 {
 "id":"HIBE-S",
 "filename":"bob-harms-curlymesquite-labeled-fertile-floret-lemma-palea-caryopsis-educational.jpg",
 "label":"EXPERT DISSECTION — real curlymesquite fertile floret, palea, caryopsis, sterile lemmas",
 "role":"Real source-identified Hilaria belangeri full photographic dissection with named dorsal/ventral spikelet clusters, extracted fertile floret, lemma, palea/caryopsis, and sterile floret lemmas against millimeter scale. Original Bob Harms labels embedded in source; exact sex placement of all lateral spikelets still cannot be inferred beyond labeled elements.",
 "caption":"Real Hilaria belangeri photographed and anatomically separated by Bob Harms. Read his labels directly on the photo: spikelet cluster (dorsal–ventral), fertile floret, lemma, palea and caryopsis, and sterile-floret lemmas. This is actual dissected reproductive material, not a generic drawing; the precise sex of every photographed lateral member is not separately demonstrated.",
 "why":"Closes the prior absence of real separate and labelled reproductive parts, with a real scale and no need to invent glume or lemma labels in our overlay.",
 "markers":[],
 "min_size":[650,500],
 "evidence":"Original pixels visually inspected: existing yellow arrows and actual reproductive-part names burnt into real scientific photo, black background and mm scale."
 },
 {
 "id":"HIBE-9",
 "filename":"bob-harms-curlymesquite-separated-papery-spikelet-fascicles-scale-educational.jpg",
 "label":"TRUE MATURE FASCICLE — separate whole papery three-member flowering groups",
 "role":"Three physically separated Hilaria belangeri dry whole flowering-unit groups on black background, two opened into broad radiating papery awned lobes, with actual ruler at left; whole fascicles not individually sex-typed.",
 "caption":"Bob Harms' real scale-referenced curlymesquite flowering clusters demonstrate the radiating fan-shaped papery components after separation from the rachis. The complete cluster is shown here; use his other dissection panel to learn the fertile floret and sterile lemmas. Do not call these three clusters the three spikelets of a single fascicle.",
 "why":"True intact and partly spread mature clusters with photographic size reference, bridging whole green head to identified separated floral anatomy.",
 "markers":[],
 "min_size":[600,180],
 "evidence":"Three real physical flowering clusters shown by Bob Harms, scale ticks visible on left; true single central fertile versus lateral staminate assignment requires caution."
 },
 {
 "id":"HIBE-6",
 "filename":"bob-harms-curlymesquite-connected-rooted-stolons-and-sheaths-educational.jpg",
 "label":"REAL ROOTED STOLONS — actual roots attached to curlymesquite runner-bearing tuft",
 "role":"Real Hilaria belangeri isolated living-origin plant arranged on white surface, visible fibrous roots attached to central basal crown and a long horizontal stolon leading to right-hand leafy ramet; other runner extends left, scale shown. Photographed roots at center clearly visible; do not infer roots under the distant right ramet.",
 "caption":"Bob Harms lifted actual curlymesquite: the fibrous roots under the central leafy tuft are visibly ATTACHED to the plant, and thin aboveground stolons connect to other leafy shoots. Follow the stem horizontally to the right-hand shoot, but do not invent roots beneath that distant shoot where none is exposed.",
 "why":"Together with Sue Carnahan's FEIS runner photo, this establishes actual photographed root-to-shoot continuity and surface runner growth, not just descriptive text.",
 "markers":[
  {"label":"Real fibrous roots below central tuft","label_x":3,"label_y":89,"target_x":43,"target_y":85},
  {"label":"Attached horizontal surface stolon","label_x":70,"label_y":8,"target_x":72,"target_y":79}
 ],
 "min_size":[500,550],
 "evidence":"Source image inspected: central roots visible below middle tuft, runner extends to distant right node, ruler at right; endpoints refer to visible roots/stolon only."
 },
 {
 "id":"HIBE-L",
 "filename":"bob-harms-curlymesquite-outer-collar-sheath-real-scale-educational.jpg",
 "label":"REAL LEAF–SHEATH REGION — true curlymesquite collar context, free ligule edge still hidden",
 "role":"Actual Hilaria belangeri green leaf blades and overlapping sheaths with sparse long hairs in frontal exterior, mm reference at edge. Source photo labelled Ligule/sheath, but continuous free inner membrane edge not securely distinguished; collar-region photo only.",
 "caption":"Bob Harms' actual curlymesquite sheath/ligule-region photo is useful for locating WHERE to open the leaf: follow the blade down to its surrounding sheath and inspect hair placement with the scale. The free 0.5–1 mm membranous ligule is NOT clearly exposed from this exterior view, so please don't confuse long sheath hairs with the true ligule.",
 "why":"This exact-species sheath junction view advances aboveground collar-region coverage without falsely labeling an unexposed microscopic membrane.",
 "markers":[],
 "min_size":[210,560],
 "evidence":"Actual 265px-wide source viewed: green blades and long sheath hairs + color ruled strip. True free membranous ligule not clearly exposed; withhold specific ligule arrow."
 }
]
added=[]
for t in TO_INSTALL:
    source=FROOT+t["id"]+".jpg"
    page=PAGE+t["id"]+".html"
    rel="images/"+t["filename"];target=BASE/rel
    if any(x.get("file")==rel for x in d["images"]):
        assert target.exists(),"Existing photo metadata but no bytes"
        print("ALREADY_INSTALLED",rel,flush=True)
        continue
    assert not target.exists() and not any(x.get("source_original")==source for x in d["images"]),"Duplicate or unexpected stored original"
    raw=get(source)
    assert 9000<len(raw)<4500000, "Unexpected source file size"
    im=Image.open(io.BytesIO(raw));im.load()
    print("SOURCE_IMAGE",source,im.size,im.format,len(raw),flush=True)
    assert im.format=="JPEG" and im.width>=t["min_size"][0] and im.height>=t["min_size"][1],f"Source too small for this task {im.size}"
    target.parent.mkdir(parents=True,exist_ok=True)
    ImageOps.exif_transpose(im).convert("RGB").save(target,"JPEG",quality=95,optimize=True)
    meta={
      "file":rel,"role":t["role"],"creator":"Bob Harms",
      "license":"Copyright Bob Harms — express scientific/educational reuse with attribution (NOT CC)",
      "license_url":ROOT,
      "source_permission_page":ROOT,
      "source_page":page,"source_gallery_index":IDX,"source_original":source,
      "source_taxon_name":"Hilaria belangeri",
      "source_region":"Bob Harms central Texas monocot field-photo collection; exact original photo's county NOT individually confirmed",
      "public_reuse":"Free for scientific and educational reuse with Bob Harms properly credited; NOT general CC/public domain/commercial license.",
      "photo_review":t["evidence"],
      "image_dimensions_original":[im.width,im.height],
      "image_sha256":hashlib.sha256(target.read_bytes()).hexdigest(),
      "modifications":"Source JPEG re-encoded EXIF/GPS-free, no crop; original Bob Harms scientific labels preserved."
    }
    d["images"].append(meta)
    panel={
      "label":t["label"],"scientific_name":"Hilaria belangeri",
      "image_url":"content/taxa/Poaceae/Hilaria/hilaria-belangeri/"+rel,
      "image_fit":"contain","creator":"Bob Harms",
      "license":meta["license"],"license_url":ROOT,
      "source_page":page,"image_role":t["role"],"caption":t["caption"],
      "why_it_matters":t["why"],"markers":t["markers"],
      "photo_status":"Real source-labelled species original verified; Bob Harms source labels preserve exact organ IDs where provided. Ligule remains partial, unexposed. Mobile overlay/Pages QA separate."
    }
    p=d.setdefault("visual_comparison",{}).setdefault("items",[])
    idx=next((i for i,x in enumerate(p) if x.get("scientific_name")!="Hilaria belangeri"),len(p))
    p.insert(idx,panel)
    added.append({"file":rel,"bytes":target.stat().st_size,"dims":im.size})
q=d.get("field_photo_quickcheck")
if q:
 q["heading"]="Curlymesquite photo key: rooted runner → actual triad dissection → collar region"
 q["steps"]=[
  "FIRST see Bob Harms' REAL lifted curlymesquite rooted tuft: fibrous roots emerge beneath a central leafy shoot, thin stolons link other shoots. Do NOT label an unseen root at the distant right-hand node.",
  "NEXT inspect the Bob Harms labeled real black-background dissection: fertile floret, lemma, palea and caryopsis, sterile lemmas, and multiple full spikelet clusters. Read the original labels and ruler rather than guessing internal parts from a whole head.",
  "Look at the separate real mature fascicles on black background: three separate whole photographed clusters are shown, each bearing papery expanding bracts. Don't confuse these with the three spikelets INSIDE one reproductive fascicle.",
  "TRACK REPRODUCTIVE MATURITY: compare Patrick Alexander's genuine green tightly closed heads, purple flowering groups and old open pale dry units on real separate plants; colors change as reproductive bracts mature and shed.",
  "LIGULE STILL INCOMPLETE: the Bob Harms original photograph labelled ligule/sheath truly shows the sheath and hair placement with size reference, but the FREE membrane edge is NOT clearly exposed. Gently open a verified specimen's INNER blade–sheath junction with 10–20× lens and millimeter scale before labelling the actual 0.5–1 mm membranous lacerate ligule.",
  "COMPARE TO TOBOSA: use distinct source-labelled Hilaria mutica views. Tobosa is coarser, with stout underground scaly rhizomes; curlymesquite has thin visible ABOVEGROUND runner stolons. Use linked physical structures and measured spikelets, not one seedhead silhouette."
 ]
 q["warning"]="17 exact-species curlymesquite photograph records including Bob Harms's real source-labelled dissection, separate flowering fascicles, actual rooted central tuft with connected runners and outer collar/sheath region. Still missing truly peeled-open free 0.5–1-mm ligule edge and confirmed active rooting into soil at every photographed runner node. Expert/mobile arrow overlay and deployed Pages QA pending."
d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
d["learner_visual_status"]["note"]="Curlymesquite true source-verified Bob Harms reproductive dissections and attached rooted stolons archived, plus exact-species outer sheath/collar region only; true 0.5–1mm free ligule edge remains unphotographed. Bob Harms images have explicit scientific/educational permission, not CC."
d.setdefault("curation_status",{})["photo_files_present"]=len(d["images"])
d["curation_status"]["lane1_hilaria_belangeri_harms_anatomy_20261027"]="FOUR_REAL_ROOT_STOLON_SPIKELET_DISSECTION_AND_COLLAR_PHOTOS_EDUCATIONAL_REUSE_LICENSE_NOT_CC_FREE_LIGULE_OPEN";
d["photo_note"]=(d.get("photo_note","") or "")+" 2026-10-27: archived four actual Bob Harms Hilaria belangeri Central TX photos: HIBE-S keyed reproductive floret/glume/lemma and caryopsis, HIBE-9 mature spread fascicles, HIBE-6 actual rooted central tuft + linked stolons, HIBE-L collar SHEATH context only not isolated membranous ligule. Credit original educational use permission; do not falsely promote to 100%."
CARD.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"added":added,"photos":len(d["images"]),"panels":len(d["visual_comparison"]["items"]),"arrows":sum(len(x.get("markers",[])) for x in d["visual_comparison"]["items"])}),flush=True)
