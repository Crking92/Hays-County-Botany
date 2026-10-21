#!/usr/bin/env python3
"""Promote manually inspected, license-checked photos to E. simulans and its true seed comparison."""
import csv,hashlib,json,shutil
from pathlib import Path
from PIL import Image

ROOT=Path("content/taxa/Euphorbiaceae/Euphorbia")
SPECIES=ROOT/"euphorbia-simulans/species.json"
SOURCES=ROOT/"euphorbia-simulans/image-sources.csv"
GENUS=ROOT/"genus.json"
LAB=Path("photo-lab/2026-10-21-euphorbia-simulans-seed-scout")
REPORT=Path("reports/euphorbia-simulans-anatomy-and-theriaca-seed-closeout-20261021.json")
s=json.loads(SPECIES.read_text())
g=json.loads(GENUS.read_text())
m=json.loads((LAB/"manifest.json").read_text())
assert s["scientific_name"]=="Euphorbia simulans"
assert m["stage"]=="PHOTO_LAB_SEED_MICRO_CANDIDATES_NOT_CANONICAL"
rows={r["photo_id"]:r for r in m["records"] if r.get("file")}
for pid in [5336725,5336727,5336967,5337479]:
    assert pid in rows, f"missing actual image {pid}"
    r=rows[pid]
    assert r["license"]=="cc-by-nc"
    assert r.get("sha256") and r.get("attribution")
    if pid==5337479:assert r["taxon"]=="Euphorbia theriaca"
    else: assert r["taxon"]=="Euphorbia simulans"
    p=Path(r["file"])
    assert p.exists()
    assert hashlib.sha256(p.read_bytes()).hexdigest()==r["sha256"]
    with Image.open(p) as im: im.verify()

def A(label,x,y):return {"label":label,"target_fraction":[x,y]}
PHOTO_SPECS=[
 {
  "id":5336725,"filename":"nathan-5336725-true-elliptic-glands.jpg",
  "role":"Macro of separate red-purple elliptical gland pads around a cyathium; no white crescent appendages visible",
  "caption":"Nathan Taylor's exact-species cyathium has red-purple elliptical to oval gland pads directly surrounding its tiny central reproductive cavity. No white petal-like gland crescents are visible. The little reproductive unit in back is not a seed.",
  "arrows":[A("One of four reddish cyathial gland pads",.683,.377),A("Central cyathial reproductive cavity",.517,.362)],
  "manual":"2026-10-21 saved source 5336725 visually inspected. Red/purple gland at upper right and central cyathial space identified; gland dimension cannot be calibrated from enlarged image."
 },
 {
  "id":5336727,"filename":"nathan-5336727-smooth-three-lobed-fruit.jpg",
  "role":"True smooth green three-lobed capsule beside separate reddish cyathial cup",
  "caption":"Rounded green THREE-LOBED capsule at left is the developing fruit, distinct from the reddish gland-bearing cyathial cup at right. The fruit's photographed surface is smooth, without conspicuous hairs; tiny stipule placement is not marked here.",
  "arrows":[A("Three-lobed smooth green fruit",.307,.449),A("Red-purple gland-bearing cyathium",.743,.174)],
  "manual":"2026-10-21 saved JPEG 5336727 read visually: fruit lobes left and cyathial glands right directly distinguishable. No claim of mature seed or measurable microscopic stipules."
 },
 {
  "id":5336967,"filename":"nathan-5336967-mature-weakly-wrinkled-seeds.jpg",
  "role":"TRUE pale red-brown 4-angled seeds with shallow irregular transverse wrinkles and source-calibrated half-millimeter scale",
  "caption":"Five true Euphorbia simulans seeds photographed by Nathan Taylor. Their pale-coated faces have weak scattered transverse wrinkles/pits; compare with the much deeper three transverse furrows on E. theriaca seeds. Black calibration bar visible at bottom; observation author states divisions are HALF millimeters, not a pixel-based guess.",
  "arrows":[A("Shallow broken wrinkles on upper-right seed",.789,.203),A("Weak low ridges on central seed",.484,.557),A("Author's half-millimeter scale divisions",.488,.943)],
  "manual":"2026-10-21 seed pixel QA: original photographed true seeds and uneven shallow seedcoat depressions visible; black ruler along bottom and observation owner states 'Scale in half millimeters'. No single exact measurement calculated from pixels."
 }
]
old_names={i["file"] for i in s["images"]}
source_map={}
for spec in PHOTO_SPECS:
    pid=spec["id"];r=rows[pid]
    name="images/"+spec["filename"];out=SPECIES.parent/name
    out.parent.mkdir(parents=True,exist_ok=True)
    if not out.exists():shutil.copyfile(r["file"],out)
    assert hashlib.sha256(out.read_bytes()).hexdigest()==r["sha256"]
    view={
     "file":name,"role":spec["role"],"caption":spec["caption"],
     "creator":r["attribution"],"license":"CC BY-NC 4.0","license_url":"https://creativecommons.org/licenses/by-nc/4.0/",
     "source_page":r["iNaturalist_url"],"observation_url":r["observation_url"],
     "observation_id":r["observation"],"photo_id":pid,"source_photo_sha256":r["sha256"],
     "public_reuse":"yes, ONLY if site is genuinely noncommercial; photographer attribution and original photo-level CC BY-NC must be preserved",
     "public_site_use_scope":"noncommercial educational GitHub Pages only",
     "photo_review":spec["manual"],"manual_arrow_review":spec["manual"],"anatomy_arrows":spec["arrows"]
    }
    if name in old_names:
        next(x for x in s["images"] if x["file"]==name).update(view)
    else:
        s["images"].append(view);old_names.add(name)
    source_map[pid]=view

# Store the comparison organism OUTSIDE simulans species image directory and do not masquerade as a simulans gallery card.
r=rows[5337479]
ther_path=ROOT/"comparison-media/nathan-theriaca-5337479-strongly-ridged-seeds.jpg"
ther_path.parent.mkdir(parents=True,exist_ok=True)
if not ther_path.exists():shutil.copyfile(r["file"],ther_path)
assert hashlib.sha256(ther_path.read_bytes()).hexdigest()==r["sha256"]
ther_desc={
 "scientific_name":"Euphorbia theriaca",
 "label":"Comparison only — theriaca seeds have deep transverse grooves",
 "image_url":str(ther_path),
 "image_role":"TRUE theriaca seed photographs from separate observation; three deep transverse grooves; DO NOT put on simulans species card",
 "creator":r["attribution"],"license":"CC BY-NC 4.0","license_url":"https://creativecommons.org/licenses/by-nc/4.0/",
 "source_page":r["iNaturalist_url"],
 "caption":"Nathan Taylor's Euphorbia theriaca observation: pale mature seeds have fewer, MUCH DEEPER crosswise grooves than simulans. This is a distinct comparison species, NOT a photo of simulans. Author's half-millimeter divisions appear along lower margin.",
 "markers":[
  {"label":"Deep transverse seed furrows", "target_x":76,"target_y":27,"label_x":53,"label_y":11},
  {"label":"Author's half-millimeter ruler", "target_x":48,"target_y":93,"label_x":12,"label_y":83}
 ],
 "image_pixel_audit":"2026-10-21 actual 1000px JPEG opened; source obs 4435298 exact E. theriaca with photo 5337479 verified individual CC BY-NC licence. Marked deep transverse furrows and visible ruler; distinct taxon label mandatory.",
 "comparison_role":"E. simulans versus E. theriaca: true contrasting seeds; theriaca is NOT installed as a canonical species"
}
count=sum(len(i.get("anatomy_arrows",[])) for i in s["images"])
assert len(s["images"])==8 and count==18, f"Expected 8 and 18: {len(s['images'])}, {count}"

s["look_here_first"]="LEAVES FIRST, BUT THE SEEDS FINISH THE ID. Euphorbia simulans is a low, largely glabrous desert sandmat with very short opposing ROUND to oval entire leaves (1–3.2 mm long) with near-symmetric bases. The small red-purple cyathial glands are ELLIPTIC and lack the white crescents of E. golondrina; Nathan Taylor's licensed true gland photograph now shows their shape. The smooth green THREE-LOBED capsule is photographed too. The decisive look-alike E. theriaca can look almost identical above ground: true SIMULANS SEEDS are generally 1.5–2 mm with 5–7 WEAK interrupted transverse wrinkles or pits, while THERIACA has smaller seeds with usually 2–4 MUCH DEEPER clear grooves. Both real seed macro photographs and author-stated 0.5mm calibration are now in the genus comparison. Still missing: independently measured same-node 0.5–0.7 mm stipules. FNA records simulans in Brewster, Hudspeth and Presidio; NOT validated as native to Hays or a local crew weed.";
s["photo_note"]="8 actual exact-E. simulans public-eligible CC BY-NC photographs: previous five habit/round leaf images with 11 checked arrows, plus three NEW Nathan Taylor micromorphology images with 7 checked arrows showing elliptical reddish appendage-free cyathial glands, smooth three-lobed fruit, and true weakly ridged pale mature seeds with author's HALF-MILLIMETER calibration. E. theriaca deeply ridged seed image kept in genus COMPARISON-MEDIA ONLY, explicitly labeled different taxon. No fabricated stipule closeup or Hays range promotion.";
s["curation_status"].update({"last_reviewed":"2026-10-21","field_status":"FIELD_READY_SEED_FRUIT_GLAND_PHOTOS_COMPLETE_STIPULE_MACRO_GAP","photo_metadata_count":8,"photo_files_present":8,"annotated_real_photo_count":8,"verified_arrow_count":18})
s["learner_visual_status"].update({"image_count":8,"status":"field_ready_photo_gaps","mode":"8_verified_source_photos_18_anatomical_arrows","annotated_source_count":8,"verified_arrow_count":18,"note":"Two actual source-seed datasets compared, but theriaca images used only on genus look-alike panel. Remaining one high-value gap is exact calibrated true leaf-node stipules."})
s["field_id_finalization"].update({"stage":"FIELD_READY_WITH_MINOR_STIPULE_MACRO_GAP","review_date":"2026-10-21","canonical_photo_count":8,"real_source_photos_annotated":8,"verified_anatomy_arrows":18,
 "remaining":["True same-node independently scaled 0.5–0.7mm separate awl-shaped stipule macro; gland photo not substitute"],
 "photo_review":"All five original image panels plus three Nathan Taylor actual JPEG macro photos manually inspected. Real photographed elliptical purplish glands without obvious white crescents, three-lobed glabrous capsule and mature four-angled weakly wrinkled seeds now documented; true theriaca ridge comparator safely separate and labeled in genus. No pixel-to-mm measurement inferred."})
s["field_photo_quickcheck"]["heading"]="Tiny rounded leaves → elliptical glands without white crescents → true weakly ridged 1.5–2mm seed"
s["field_photo_quickcheck"]["featured_photo_indices"]=[7,5,6,1,2,0,3,4]
s["field_photo_quickcheck"]["steps"]=[
 "Find reddish low MAT habit and extremely small opposite near-round entire leaf blades; avoid confusing with similarly small seedlings.",
 "Study a real cyathium under 10–20x: E. simulans elliptical RED-PURPLE glands lack petal-like WHITE crescents; compare E. golondrina whose gland pads have white crescents.",
 "Check the real SMOOTH THREE-LOBED green fruit, not the gland-bearing cyathial involucre cup.",
 "To rule out E. theriaca, compare detached seed faces with a half-millimeter ruler: SIMULANS about 1.5–2mm and faint irregular 5–7 ridges, versus THERIACA fewer/deeper (usually 3) furrows.",
 "Get a true same-node 0.5–0.7mm separate threadlike stipule pair for optional close confirmation; not clearly resolved in current images."
]
s["field_photo_quickcheck"]["warning"]="The theriaca photograph belongs ONLY to the genus look-alike comparison and is never presented as an E. simulans species photo. Nathan's stated half-millimeter marks are author-calibrated; no independent pixel-derived dimensions claimed. Hays County nativity is not proven."
s["visual_comparison"]["subtitle"]="Eight real exact-species CC BY-NC source photos with 18 manually checked arrow targets now include true cyathial glands, true glabrous capsules and calibrated pale weakly wrinkled SEEDS. Stipules remain a small targeted gap."
s["visual_comparison"]["items"]=[v for v in s["visual_comparison"]["items"] if not any(v.get("image_url","").endswith(sp["filename"]) for sp in PHOTO_SPECS)]
for sp in PHOTO_SPECS:
    v=source_map[sp["id"]]
    item={
     "scientific_name":"Euphorbia simulans","label":("Real gland macro — no white appendage" if sp["id"]==5336725 else "True three-lobed glabrous capsule" if sp["id"]==5336727 else "Mature pale seeds — shallow wrinkles"),
     "image_url":f"content/taxa/Euphorbiaceae/Euphorbia/euphorbia-simulans/{v['file']}",
     "image_role":v["role"],"caption":v["caption"],"source_page":v["source_page"],
     "creator":v["creator"],"license":v["license"],"license_url":v["license_url"],
     "image_fit":"contain","markers":[{"label":a["label"],"target_x":round(a["target_fraction"][0]*100),"target_y":round(a["target_fraction"][1]*100),
     "label_x":8 if ix%2==0 else 61,"label_y":15+24*ix} for ix,a in enumerate(v["anatomy_arrows"])],
     "image_pixel_audit":v["manual_arrow_review"]
    }
    s["visual_comparison"]["items"].append(item)

# Extend source-credit manifest with new exact-species photo records.
with SOURCES.open(newline="",encoding="utf-8") as fh:
 reader=csv.DictReader(fh);fields=reader.fieldnames;credits=list(reader)
existing={row["file_name"] for row in credits}
for sp in PHOTO_SPECS:
 v=source_map[sp["id"]];r=rows[sp["id"]]
 name=sp["filename"]
 if name in existing:continue
 credits.append({"file_name":name,"role":v["role"],"creator":v["creator"],
 "license":v["license"],"source_page":v["source_page"],"direct_url":r["photo_url"],
 "study_use":"verified botanical learner under source photo rights",
 "public_reuse":"yes ONLY for genuinely noncommercial education with photo credit and CC BY-NC",
 "observation_id":str(v["observation_id"]),"photo_id":str(v["photo_id"])})
with SOURCES.open("w",newline="",encoding="utf-8") as fh:
 writer=csv.DictWriter(fh,fieldnames=fields);writer.writeheader();writer.writerows(credits)

pair=next(v for v in g["comparison_cards"] if v["id"]=="euphorbia-golondrina-simulans-gland-appendages")
pair["reviewed_at"]="2026-10-21"
pair["look_here_first"]="GOLONDRINA vs SIMULANS: first compare leaf shape—golondrina longer narrower 5–11.5mm, simulans rounded 1–3.2mm. The decisive cyathial comparison is SHOWABLE NOW: golondrina has cup-shaped ROUND purple glands with WHITE crescent appendages; simulans has ELLIPTIC red-purple glands WITHOUT white appendages. Real photographed simulans SMOOTH three-lobed capsule is available (shared trait, NOT separating the pair). Hardest simulans vs THERIACA require true seeds, now both photographed by Nathan Taylor with half-mm ruler: simulans larger weakly WRINKLED/pitted 5–7 faint transverse ridges; theriaca smaller with about THREE VERY DEEP ridges. Never use leaf photos alone to choose simulans vs theriaca; nor mistake white tips of stamens for gland appendages."
pair["comparison_status_2026_10_21"].update({"simulans_gallery_photos":8,"simulans_arrowed_views":8,"simulans_arrow_count":18,
 "simulans_genus_comparison_photos":5,"status":"GLAND_CAPSULE_AND_SIMULANS_THERIACA_TRUE_SEED_MACROS_VISUALLY_CHECKED",
 "critical_holds":["Simulans 0.5–0.7 mm true nodal stipules in situ macro remains unverified","Golondrina round gland outline and distinct mature seed macros still only partly resolved"]})
pair["photo_pair_targets"]= [{**x,"status":("NOW VERIFIED: source photo 5336725 Nathan Taylor shows real red-purple gland pads; no white appendages visible. E. golondrina's white crescent already documented separately.")} if x["role"]=="Simulans gland comparison" else {**x,"status":("NOW VERIFIED: Nathan Taylor 5336967 SIMULANS seeds with shallow weak wrinkle/pit relief and 5337479 separate THERIACA seeds with three deep crosswise grooves; author notes half-millimeter scale. Golondrina seed macro remains a separate possible enrichment.")} if x["role"]=="True mature seeds (both species)" else {**x,"status":("NOW VERIFIED: two separately licensed photographed seed macros (E. simulans 5336967 versus E. theriaca 5337479), exact species labels, creator credits and scale; no inference from a close habit photo.")} if x["role"]=="Simulans versus theriaca true mature seed microscopy" else x for x in pair["photo_pair_targets"]]

# Genus images reuse real species images and store a separately tagged theriaca comparator.
paths=[f"content/taxa/Euphorbiaceae/Euphorbia/euphorbia-simulans/{source_map[pid]['file']}" for pid in [5336725,5336727,5336967]]
paths.append(str(ther_path))
g["visual_comparison"]["items"]=[i for i in g["visual_comparison"]["items"] if i.get("image_url") not in paths]
for pid in [5336725,5336727,5336967]:
 v=next(i for i in s["visual_comparison"]["items"] if i.get("image_url","").endswith(source_map[pid]["file"]))
 g["visual_comparison"]["items"].append({**v,"comparison_role":"True exact E. simulans seed/gland/fruit source photograph; matched safely against golondrina and theriaca in genus key"})
g["visual_comparison"]["items"].append(ther_desc)
g["curation_status"].update({"last_reviewed":"2026-10-21","simulans_golondrina_theriaca":"SIMULANS_REAL_GLAND_CAPSULE_AND_MATURE_SEED_CONFIRMED; THERIACA_SEED_COMPARATOR_CONFIRMED; STIPULE_MACRO_PENDING"})

SPECIES.write_text(json.dumps(s,ensure_ascii=False,indent=2)+"\n")
GENUS.write_text(json.dumps(g,ensure_ascii=False,indent=2)+"\n")
REPORT.parent.mkdir(parents=True,exist_ok=True)
REPORT.write_text(json.dumps({
 "date":"2026-10-21","status":"SIMULANS_FIELD_READY_WITH_STIPULE_MACRO_GAP",
 "simulans_images":len(s["images"]),"simulans_annotations":count,
 "added_photo_ids":[5336725,5336727,5336967],"comparator":{"taxon":"Euphorbia theriaca","photo_id":5337479,"file":str(ther_path),"creator":r["attribution"],"license":"CC BY-NC 4.0"},
 "source_obs_ids":[4434982,4435298],
 "license_guardrail":"Five existing species files and three source photos all individually CC BY-NC. Site must be genuinely noncommercial and preserve attribution and license; comparator never impersonates a species card.",
 "photo_qa":"Nine new anatomical arrows placed on real visually inspected macro structures: elliptic gland, central cyathium, three-lobed smooth fruit, adjacent reproductive cup, weak seed wrinkles and author half-mm scale; theriaca genus example deep furrows/scale separately.",
 "remaining":["Same-node independently measurable 0.5–0.7mm true subulate separate stipules"],
 "nativity":"FNA E. simulans currently lists Brewster, Hudspeth, Presidio Texas, not Hays. No local nativity assumption."
},indent=2)+"\n")
print(json.dumps({"simulans":len(s["images"]),"simulans_arrows":count,"theriaca_reference":str(ther_path)},indent=2))
