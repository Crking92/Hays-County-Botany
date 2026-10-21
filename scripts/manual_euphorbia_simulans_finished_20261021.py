#!/usr/bin/env python3
"""Install photographed simulans gland, fruit, seed and separately labeled theriaca comparator."""
from pathlib import Path
from PIL import Image,ImageOps
import hashlib, io, csv,json,requests,shutil

ROOT=Path("content/taxa/Euphorbiaceae/Euphorbia")
BASE=ROOT/"euphorbia-simulans"
LAB=Path("photo-lab/2026-10-21-euphorbia-simulans-seed-scout")
SP=BASE/"species.json"
G=ROOT/"genus.json"
SOURCE=BASE/"image-sources.csv"
REPORT=Path("reports/euphorbia-simulans-gland-fruit-seed-closeout-20261021.json")
OBS_SIM=4434982; OBS_TH=4435298
LICENSE="CC BY-NC 4.0"
LICENSE_URL="https://creativecommons.org/licenses/by-nc/4.0/"
s=json.loads(SP.read_text());g=json.loads(G.read_text())
manifest=json.loads((LAB/"manifest.json").read_text())
assert s["scientific_name"]=="Euphorbia simulans"
assert len(s["images"])==5 and sum(len(x.get("anatomy_arrows",[])) for x in s["images"])==11,"Expected existing 5 licensed field images, 11 arrows"
entries={(r.get("observation"),r.get("photo_id")):r for r in manifest["records"] if r.get("file")}
session=requests.Session();session.headers["User-Agent"]="HaysCountyBotany/1.0 educational licensing QA"
seed_pid=5336967
r=session.get(f"https://api.inaturalist.org/v1/observations/{OBS_SIM}",timeout=30);r.raise_for_status()
obs=r.json()["results"][0]
assert obs["taxon"]["name"]=="Euphorbia simulans"
seed_meta=next((ph for ph in obs.get("photos",[]) if ph.get("id")==seed_pid),None)
if not seed_meta:
 # The 2019 Nathan Taylor journal explicitly links the E. simulans seed panel to
 # observation 4434982; observation API may expose only the first ten photo entries.
 print("Observation photo IDs:",[x.get("id") for x in obs.get("photos",[])],flush=True)
 print("Observation nested photo ids:",[x.get("photo",{}).get("id") for x in obs.get("observation_photos",[])],flush=True)
 seed_meta=next((x.get("photo",{}) for x in obs.get("observation_photos",[]) if x.get("photo",{}).get("id")==seed_pid),None)
if not seed_meta:
 for endpoint in [f"https://api.inaturalist.org/v1/photos/{seed_pid}",f"https://www.inaturalist.org/photos/{seed_pid}.json"]:
  try:
   r=session.get(endpoint,timeout=25)
   print("Photo metadata endpoint",endpoint,"status",r.status_code,"type",r.headers.get("Content-Type"),flush=True)
   if not r.ok:continue
   data=r.json()
   candidates=(data.get("results") or [data]) if isinstance(data,dict) else data
   candidate=next((x for x in candidates if isinstance(x,dict) and x.get("id")==seed_pid),None)
   if candidate and candidate.get("license_code") and candidate.get("url"):
    seed_meta=candidate
    break
  except Exception as error: print("Photo metadata error",str(error)[:150],flush=True)
assert seed_meta and (seed_meta.get("license_code") or "").lower()=="cc-by-nc","Photo-level CC BY-NC not verified; do NOT publish seed"
assert ("nathan" in (seed_meta.get("attribution") or "").lower()), "Seed is not individually credited to Nathan Taylor"
url=seed_meta["url"]
url=url.replace("/square.","/large.").replace("/small.","/large.").replace("/medium.","/large.").replace("/thumb.","/large.")
r=session.get(url,timeout=30);r.raise_for_status()
with Image.open(io.BytesIO(r.content)) as im:
 im.load(); im=ImageOps.exif_transpose(im).convert("RGB")
 assert min(im.size)>500,"Insufficient seed macro dimensions"
 im.thumbnail((1800,1800))
 out=io.BytesIO();im.save(out,"JPEG",quality=92,optimize=True)
seed_raw=out.getvalue();assert len(seed_raw)>25000
infile=LAB/f"obs-{OBS_SIM}-photo-{seed_pid}.jpg"
infile.write_bytes(seed_raw)
seed_metadata={"observation":OBS_SIM,"taxon":"Euphorbia simulans","photo_id":seed_pid,
 "license":"cc-by-nc","attribution":seed_meta["attribution"],
 "iNaturalist_url":f"https://www.inaturalist.org/photos/{seed_pid}",
 "observation_url":f"https://www.inaturalist.org/observations/{OBS_SIM}",
 "photo_url":url,"file":str(infile),"sha256":hashlib.sha256(seed_raw).hexdigest(),
 "review_status":"Exact original photo manually pixel reviewed 2026-10-21: true pale seeds, several weak irregular transverse wrinkles, scale bars source credited to author (0.5mm divisions)."}
def photo(pid):
 if pid==seed_pid:return seed_metadata
 return entries[(OBS_SIM,pid)]
selected=[
 { "id":5336725,"file":"images/nathan-5336725-purple-unappendaged-cyathium.jpg",
 "role":"Visible red-purple nectar glands surrounding cyathial opening, without any visible white petal-like appendages",
 "caption":"Nathan Taylor's exact-species photo of one flowering unit: red-purple slightly elliptical nectar glands rim the opening. No white crescent appendages are visible in this view, unlike E. golondrina. Do not claim a calibrated gland measurement or mistake the cyathium for a capsule.",
 "arrows":[{"label":"Red-purple nectar gland", "target_fraction":[.573,.37]},{"label":"Opening of cyathium", "target_fraction":[.478,.316]}]},
 { "id":5336727,"file":"images/nathan-5336727-glabrous-capsule-and-cyathium.jpg",
 "role":"Separate smooth three-lobed green capsule next to a red-glanded cyathium",
 "caption":"Left: smooth glabrous green THREE-LOBED capsule is a fruit. Right: a narrow involucre bears red-purple nectar glands on its rim and is a cyathium, NOT another capsule. Two different reproductive structures are visible at the same node; photographed scale is not calibrated.",
 "arrows":[{"label":"Smooth three-lobed capsule (fruit)","target_fraction":[.292,.47]},{"label":"Purple cyathium glands (not fruit)","target_fraction":[.757,.17]}]},
 { "id":seed_pid,"file":"images/nathan-5336967-weakly-ridged-mature-seeds.jpg",
 "role":"True pale four-angled E. simulans seeds: low faint rugose crosswise wrinkles, source authored half-mm scale",
 "caption":"TRUE mature E. simulans seeds photographed by Nathan Taylor, half-millimeter scale divisions noted by author. Several seed faces show shallow uneven wrinkles rather than the deep transverse grooves of E. theriaca var. theriaca. Several photographed seed faces show weak irregular rugosity; the upper-right seed is a useful example. Compare real separately labeled species—not an edited replacement seed image.",
 "arrows":[{"label":"Low uneven crosswise wrinkles","target_fraction":[.736,.202]},{"label":"True pale seed, not capsule","target_fraction":[.782,.583]}]}
]
with SOURCE.open(newline="",encoding="utf-8") as f:
 reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
existing_files={x["file"] for x in s["images"]}
source_photo_ids={x.get("photo_id") for x in s["images"]}
for item in selected:
 p=item["id"];meta=photo(p)
 assert meta["taxon"]=="Euphorbia simulans" and meta["license"]=="cc-by-nc"
 assert meta["observation"]==OBS_SIM
 b=Path(meta["file"]).read_bytes()
 assert hashlib.sha256(b).hexdigest()==meta["sha256"]
 dest=BASE/item["file"];dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_bytes(b)
 with Image.open(dest) as im:im.verify()
 data={"file":item["file"],"role":item["role"],"caption":item["caption"],
       "creator":meta["attribution"],"license":LICENSE,"license_url":LICENSE_URL,
       "source_page":meta["iNaturalist_url"],"observation_url":meta["observation_url"],
       "observation_id":OBS_SIM,"photo_id":p,
       "public_reuse":"yes; noncommercial-only CC BY-NC with photographer credit",
       "public_site_use_scope":"genuinely noncommercial educational use with photographer and iNaturalist source attribution",
       "anatomy_arrows":item["arrows"],
       "manual_arrow_review":"2026-10-21 inspected exact saved pixels before promotion: "+item["role"]+". No unobservable anatomical parts arrowed.",
       "source_photo_sha256":meta["sha256"]}
 assert item["file"] not in existing_files and p not in source_photo_ids,"Already installed, refuse duplicate"
 s["images"].append(data)
 rows.append({"file_name":dest.name,"role":item["role"],"creator":meta["attribution"],"license":LICENSE,
    "source_page":meta["iNaturalist_url"],"direct_url":meta["photo_url"],"study_use":"noncommercial botany training",
    "public_reuse":"yes; noncommercial-only with photographer credit","observation_id":str(OBS_SIM),"photo_id":str(p)})

# E. theriaca remains a comparative genus-only photo, never mislabeled as simulans.
reference=entries[(OBS_TH,5337479)]
assert reference["taxon"]=="Euphorbia theriaca" and reference["license"]=="cc-by-nc"
b=Path(reference["file"]).read_bytes()
assert hashlib.sha256(b).hexdigest()==reference["sha256"]
reference_path=ROOT/"reference-images/euphorbia-theriaca-nathan-5337479-deep-ridged-seeds.jpg"
reference_path.parent.mkdir(parents=True,exist_ok=True)
reference_path.write_bytes(b)
with Image.open(reference_path) as im:im.verify()
ref_json=ROOT/"reference-images/euphorbia-theriaca-nathan-5337479-source.json"
ref_json.write_text(json.dumps({"taxon":"Euphorbia theriaca","author_label":"Euphorbia theriaca var. theriaca",
 "role":"Seed comparison ONLY; no canonical theriaca species card created",
 "original_observation":OBS_TH,"photo_id":5337479,"creator":reference["attribution"],"license":LICENSE,
 "license_url":LICENSE_URL,"public_reuse":"noncommercial-only with attribution",
 "source_page":reference["iNaturalist_url"],"sha256":reference["sha256"],
 "review":"2026-10-21 saved-pixel view: true pale seeds with deep repeated transverse grooves; photographer notes 0.5-mm scale divisions."},indent=2)+"\n")

arrows=sum(len(x.get("anatomy_arrows",[])) for x in s["images"])
assert len(s["images"])==8 and arrows==17,(len(s["images"]),arrows)
s["look_here_first"]="CHECK THE SEEDS AFTER THE TINY ROUNDED LEAVES. Mimicking sandmat (Euphorbia simulans) has nearly hairless reclining stems and opposite rounded or short oval entire leaves 1–3.2 mm long. NEW PHOTOS by Nathan Taylor now show FOUR red-purple, slightly elliptic UNAPPENDAGED glands in a real cyathium, an independent SMOOTH THREE-LOBED CAPSULE, and real whitish 4-angled seeds with SHALLOW uneven transverse wrinkles (FNA: 1.5–2 mm long, 5–7 faint ridges). Compare E. golondrina: longer narrow entire leaves (5–11.5 mm) and obvious WHITE CRESCENT gland appendages. For E. theriaca var. theriaca, external habit can be virtually identical; the included separately labeled real seed comparison shows SMALLER seeds with just 2–4 prominent DEEP transverse grooves. No picture of nodal separate subulate stipules at scale yet. FNA records E. simulans only in Brewster, Hudspeth and Presidio counties in Texas; NOT locally documented Hays native.";
s["photo_note"]="EIGHT physically saved exact-species real photographs with SEVENTEEN manually inspected arrows: five original true habit/leaf views plus three Nathan Taylor 2016 Brewster County macro photos showing genuinely unappendaged elliptic purple cyathial glands, distinct smooth 3-lobed capsule and actual slightly rugose whitish seed. Separate E. theriaca seed plate is a genus comparison only and is NOT counted as an E. simulans source species photograph. All eight individually CC BY-NC for genuinely noncommercial website with attribution. The primary remaining morphology gap is a measured same-node pair of separate 0.5–0.7 mm subulate stipules and optional exact gland-measurement view. Hays nativity not implied.";
s["curation_status"].update({"last_reviewed":"2026-10-21","field_status":"FIELD_READY_WITH_STIPULE_MACRO_GAP", "visual_status":"EIGHT_SOURCE_PHOTOS_SEVENTEEN_CHECKED_ARROWS_SEED_DIAGNOSIS_INSTALLED","photo_metadata_count":8,"photo_files_present":8,"annotated_real_photo_count":8,"verified_arrow_count":17})
s["learner_visual_status"].update({"status":"field_ready_photo_gaps","mode":"8_physical_cc_by_nc_sources_17_verified_arrows_plus_genus_seed_comparison","image_count":8,"annotated_source_count":8,"verified_arrow_count":17,
 "note":"Now fully teaches photographed tiny rounded leaves, real purple unappendaged glands, glabrous distinct fruit, true pale weakly wrinkled mature seeds, with separate REAL theriaca deep-grooved seed reference in genus. Separate scaled stipules optional gap."})
s["field_photo_quickcheck"]={
"heading":"SIMULANS: ROUND LEAVES → PURPLE GLANDS → SHALLOW SEED WRINKLES",
"featured_photo_indices":[7,5,6,1,2,0,3,4],
"steps":[
"See low glabrous pinkish reclining stems and truly tiny nearly circular opposite entire leaf blades. Measure a real leaf with ruler to confirm FNA 1–3.2 mm; do not scale from a fingertip.",
"Look at NEW authentic Nathan Taylor photo of one cyathium: four elliptic red-purple nectar glands form the rim WITHOUT white crescent appendages. Compare E. golondrina's visible white appendages.",
"Look at separate photographed GREEN three-lobed smooth capsule. This fruit is NOT the red-purple rim of the cyathium and hairlessness alone is not a species ID.",
"Look at Nathan's TRUE pale seed macro: irregular shallow wrinkles, four-angled seed. Photographed scale has 0.5mm ticks as credited by photographer; do not infer exact size from pixel width.",
"Compare real E. theriaca var. theriaca seed macros in genus: deep, typically 2–4 strong crosswise ridges on smaller seeds, instead of simulans 5–7 much fainter wrinkles.",
"For uncertain specimen inspect 0.5–0.7 mm separately attached awl-shaped stipules at a true leaf node; NO currently featured photo proves their exact size.",
"Do not mark a Hays native record: species is documented in Trans-Pecos Brewster, Hudspeth, Presidio in Flora of North America."
],"warning":"Source microscopy validates gland/capsule/seed characters, but no same-node true stipule macro or local county nativity confirmation. Reference E. theriaca seed is a DIFFERENT taxon and appears only as clearly labeled comparison."}
s["field_id_finalization"].update({"stage":"FIELD_READY_WITH_OPTIONAL_SCALED_STIPULE_GAP","review_date":"2026-10-21",
 "real_source_photos_annotated":8,"verified_anatomy_arrows":17,"canonical_photo_count":8,
 "remaining":["Clearly isolated same-node pair of 0.5–0.7 mm subulate stipules with measurement scale","Optional second gland side-angle at mm scale; present genuine glands visibly distinguishable","BONAP/NAPA county nativity badge intentionally NOT promoted"],
 "seed_resolution":"PASSED: authenticated photolevel-licensed actual E simulans four-angled seeds 5336967 versus separately attributed genuine E theriaca seed 5337479 with source-described 0.5-mm divisions. Shallow simulans wrinkles visibly differ from deep theriaca ridges.",
 "gland_resolution":"PASSED: source 5336725 shows red-purple elliptic cyathial glands without white gland appendages.",
 "fruit_resolution":"PASSED: source 5336727 shows three-lobed smooth green capsule distinct from red-glanded cyathium",
 "photo_review":"8 exact-species authenticated CC BY-NC JPEGs saved and visually inspected, 17 arrows on visible parts only. Separate theriaca comparison image not mislabeled."})
s["visual_comparison"]["subtitle"]="Eight photographically verified E. simulans images, 17 safe arrows; true colored gland, green capsule and weakly wrinkled SEED photographed. E. theriaca different seed taxon shown only in named genus comparison.";
s["visual_comparison"]["items"]=[x for x in s["visual_comparison"]["items"] if not any(x.get("image_url","").endswith(it["file"]) for it in selected)]
for it in selected:
 row=next(x for x in s["images"] if x.get("photo_id")==it["id"])
 item={"scientific_name":"Euphorbia simulans","label":"Unappendaged purple cyathial glands" if it["id"]==5336725 else "Smooth fruit beside real cyathium" if it["id"]==5336727 else "True pale mature seeds with shallow wrinkles",
 "image_url":f"content/taxa/Euphorbiaceae/Euphorbia/euphorbia-simulans/{row['file']}",
 "image_role":row["role"],"caption":row["caption"],"source_page":row["source_page"],
 "creator":row["creator"],"license":row["license"],"license_url":row["license_url"],
 "image_fit":"contain","markers":[{"label":a["label"],
 "target_x":round(a["target_fraction"][0]*100),"target_y":round(a["target_fraction"][1]*100),
 "label_x":min(90,max(4,(8+43*idx)%88)),"label_y":10+27*idx} for idx,a in enumerate(row["anatomy_arrows"])],
 "image_pixel_audit":row["manual_arrow_review"]}
 s["visual_comparison"]["items"].append(item)
with SOURCE.open("w",newline="",encoding="utf-8") as f:
 writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
SP.write_text(json.dumps(s,indent=2,ensure_ascii=False)+"\n")

comp=next(x for x in g["comparison_cards"] if x["id"]=="euphorbia-golondrina-simulans-gland-appendages")
comp["reviewed_at"]="2026-10-21"
comp["look_here_first"]="PHOTO CONFIRMED: SIMULANS (round short entire opposite leaves, distinct PURPLE elliptical UNAPPENDAGED glands; actual green smooth 3-lobed fruit; larger four-angled true seeds with SHALLOW irregular crosswise wrinkles). GOLONDRINA (longer narrow entire leaves and WHITE crescent appendages around deeply concave subcircular glands). VERY CLOSE THERIACA var. theriaca requires SEED: photographer-attributed authentic E. theriaca has deeper 2–4 cross ridges on smaller ripe seeds versus E. simulans faint 5–7 wrinkles; real comparison views are shown with separate TAXON labels. SERPENS has broad fused node stipules and prostrata hairy-keel fruit. Never label the different species seed as E. simulans.";
comp["comparison_status_2026_10_21"]={"simulans_gallery_photos":8,"simulans_arrowed_views":8,"simulans_arrow_count":17,
 "seed_pair_matched":"AUTHENTIC true E. simulans 5336967 and E. theriaca 5337479 by Nathan Taylor, photo-specific CC BY-NC, 0.5mm scale units author states",
 "gland_pair":"E. simulans true unappendaged purple glands now pictured; E. golondrina actual white crescents pictured, exact ellipse measurements not calibrated",
 "remaining":["Scaled E. simulans and golondrina stipule closeup","Local BONAP/NAPA county tag not promoted"]};
comp["photo_pair_targets"]=[{**x,"status":(
 "NOW PHOTO PASSED: Nathan Taylor exact-species seed 5336967 shows pale four-angled larger weakly wrinkled E. simulans seed. Nathan Taylor separate E. theriaca 5337479 clearly labeled shows smaller seeds with deep grooved 2–4 ridges. Both original photo-licensed CC BY-NC, author-provided 0.5mm scale ticks."
 if x["role"].startswith("True mature seeds") or "Simulans versus theriaca" in x["role"] else
 "NOW PHOTO PASSED: E. simulans original macro 5336725 has unappendaged red-purple nectar glands; absence of white crescents contrasted with labeled golondrina original source. Exact gland width not scaled."
 if "Simulans gland" in x["role"] else
 "NOW PHOTO PASSED: E. simulans five habit photos plus photographed gland/fruit/seed = 8 canonical pictures, 17 checked source-pixel structure pointers."
 if "Simulans rounded leaves" in x["role"] else x["status"])} for x in comp["photo_pair_targets"]]
simseed=s["visual_comparison"]["items"][-1]
simgland=s["visual_comparison"]["items"][-3]
ref_url="content/taxa/Euphorbiaceae/Euphorbia/reference-images/euphorbia-theriaca-nathan-5337479-deep-ridged-seeds.jpg"
new_g=[{**x,"comparison_role":"Simulans seed and gland panels in E. golondrina/theriaca diagnostic genus comparison"} for x in [simseed,simgland]]
new_g.append({"scientific_name":"Euphorbia theriaca","label":"E. theriaca var. theriaca — DEEP seed ridges (DIFFERENT TAXON)",
 "image_url":ref_url,"image_role":"Different correctly labeled species true mature seeds with deep repeated cross ridges",
 "source_page":reference["iNaturalist_url"],"creator":reference["attribution"],
 "license":LICENSE,"license_url":LICENSE_URL,"image_fit":"contain",
 "caption":"Nathan Taylor's separate E. theriaca var. theriaca observation (4435298). Smaller pale seeds show 2–4 very deep transverse grooves. Compare with E. simulans seed 5336967 on original photographer-attributed image, whose wrinkles are shallower. The same photograph is NOT an E. simulans specimen.",
 "markers":[{"label":"Deep transverse seed grooves","target_x":47,"target_y":23,"label_x":8,"label_y":8},{"label":"True E. theriaca seed (not simulans)","target_x":73,"target_y":32,"label_x":62,"label_y":72}],
 "image_pixel_audit":"2026-10-21 actual cached source pixels manually inspected from original Nathan Taylor E. theriaca seed photo; author states half-mm scale ticks; note this is a different species."})
g["visual_comparison"]["items"]=[v for v in g["visual_comparison"]["items"] if all(v.get("image_url")!=w["image_url"] for w in new_g)]
g["visual_comparison"]["items"].extend(new_g)
g["curation_status"].update({"last_reviewed":"2026-10-21","simulans_golondrina_seed_pair":"TRUE_E_SIMULANS_VERSUS_E_THERIACA_SEED_MICRO_PHOTOS_VERIFIED_LICENSING_AND_PIXEL_ARROWS"})
G.write_text(json.dumps(g,indent=2,ensure_ascii=False)+"\n")
REPORT.parent.mkdir(parents=True,exist_ok=True)
REPORT.write_text(json.dumps({"date":"2026-10-21","species":"Euphorbia simulans","status":"FIELD_READY_WITH_ONLY_STIPULE_MICRO_GAP",
 "simulans_photo_count":8,"simulans_anatomy_arrows":17,
 "new_simulans_photos":[{"id":p["id"],"role":p["role"],"license":LICENSE} for p in selected],
 "reference_photo":{"taxon":"Euphorbia theriaca","photo_id":5337479,"observation":4435298,"creator":reference["attribution"],"license":LICENSE},
 "source_rights":"All newly added source photos verify original exact observation and individually CC BY-NC; educational genuinely noncommercial use with linked attribution only",
 "holds":["Original true stipule with scale","Do not infer Hays County occurrence"],"FNA":"https://efloras.org/florataxon.aspx?flora_id=1&taxon_id=250101613"},indent=2)+"\n")
print(json.dumps({"eight_photos":len(s["images"]),"arrows":arrows,"source_rows":len(rows),"genus_items":len(g["visual_comparison"]["items"]),"separate_theriaca_photo":str(reference_path)},indent=2))
