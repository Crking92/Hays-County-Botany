#!/usr/bin/env python3
"""Publish TWO manually pixel-reviewed ophthalmica images and safe anatomy pointers."""
from pathlib import Path
import json,csv,hashlib,shutil
from PIL import Image

ROOT=Path("content/taxa/Euphorbiaceae/Euphorbia/euphorbia-ophthalmica")
LAB=Path("photo-lab/2026-10-21-euphorbia-ophthalmica-scout")
SPECIES=ROOT/"species.json"
MANIFEST=ROOT/"image-sources.csv"
GENUS=Path("content/taxa/Euphorbiaceae/Euphorbia/genus.json")
REPORT=Path("reports/euphorbia-ophthalmica-source-and-pixel-review-20261021.json")
wanted={
 103176610:{
  "new_file":"images/06-lucy-cash-terminal-head-and-hairy-stem.jpg",
  "role":"Flowering tip with tiny condensed terminal cyathia and visible hairs on the slender stem",
  "arrows":[
   {"label":"Dense terminal reproductive head","target_fraction":[.364,.244]},
   {"label":"Short hairs on slender stem below head","target_fraction":[.422,.482]},
   {"label":"Paired small leaves below tip","target_fraction":[.387,.698]}
  ],
  "caption":"Lucy Cash's exact-species flowering shoot shows a small densely packed terminal cyathium head, slender pale-hairy stem, and opposite leaf pairs. Rounded green reproductive structures within the head are NOT claimed to be individually mature capsules or to prove fine capsule hairs.",
  "inspection":"2026-10-21 manually inspected 1400px-or-smaller saved candidate pixels: endpoints are on the terminal head, hairy flowering stalk and opposite leaves. No structure labeled as mature fruit, seed or stipule."
 },
 125643782:{
  "new_file":"images/07-karlabalrey-terminal-head-and-leaf-hairs.jpg",
  "role":"Compact reddish head on short leafy branch with conspicuous leaf hairs",
  "arrows":[
   {"label":"Compact group of reddish cyathia","target_fraction":[.555,.391]},
   {"label":"Numerous fine hairs on leaf","target_fraction":[.514,.706]}
  ],
  "caption":"karlabalrey's close-up shows tightly clustered pinkish reproductive parts with short hairs visible on an adjacent broad leaf. Individual fruits and their exact mature capsule hair distribution cannot be distinguished securely in this view. Treat as leaf-hair and head-architecture evidence, not a seed or stipule image.",
  "inspection":"2026-10-21 saved photograph visually inspected: the condensed upper head and long lower leaf's hair-covered surface are identifiable. No three-lobed ripe fruit or seed arrow inferred."
 }
}
assert SPECIES.exists() and GENUS.exists()
s=json.loads(SPECIES.read_text())
g=json.loads(GENUS.read_text())
scout=json.loads((LAB/"manifest.json").read_text())
assert s["scientific_name"]=="Euphorbia ophthalmica"
byphoto={r["photo_id"]:r for r in scout["candidate_photos"] if r.get("file")}
rows=[]
with MANIFEST.open(newline="",encoding="utf-8") as fh:
 reader=csv.DictReader(fh);fields=reader.fieldnames; rows=list(reader)
images=s["images"]
existing={x["file"] for x in images}
records=[]
for pid,config in wanted.items():
 item=byphoto.get(pid)
 assert item, f"Missing vetted source {pid}"
 assert item["taxon_from_api"]=="Euphorbia ophthalmica"
 assert item["photo_license_code"]=="cc-by-nc"
 assert item["photo_attribution"] and item["observation_id"]
 inpath=Path(item["file"]);assert inpath.exists()
 assert hashlib.sha256(inpath.read_bytes()).hexdigest()==item["saved_sha256"]
 with Image.open(inpath) as im:im.verify()
 outpath=ROOT/config["new_file"]
 outpath.parent.mkdir(exist_ok=True,parents=True)
 if not outpath.exists():shutil.copyfile(inpath,outpath)
 assert hashlib.sha256(outpath.read_bytes()).hexdigest()==item["saved_sha256"]
 license_url="https://creativecommons.org/licenses/by-nc/4.0/"
 record={
  "file":config["new_file"],"role":config["role"],"caption":config["caption"],
  "creator":item["photo_attribution"],
  "license":"CC BY-NC 4.0","license_url":license_url,
  "source_page":item["photo_src_page"],"observation_url":item["observation_url"],
  "observation_id":item["observation_id"],"photo_id":pid,
  "public_reuse":"yes, ONLY for genuinely noncommercial educational GitHub Pages with license link and attribution",
  "public_site_use_scope":"noncommercial only; author attribution and source license required",
  "source_photo_sha256":item["saved_sha256"],
  "photo_review":config["inspection"],
  "manual_arrow_review":config["inspection"],
  "anatomy_arrows":config["arrows"]
 }
 if config["new_file"] not in existing:
  images.append(record);existing.add(config["new_file"])
 else:
  i=next(i for i in images if i["file"]==config["new_file"])
  i.update(record)
 rows=[x for x in rows if x["file_name"]!=outpath.name]
 rows.append({"file_name":outpath.name,"role":record["role"],"creator":record["creator"],
              "license":record["license"],"source_page":record["source_page"],
              "direct_url":item["source_url"],"study_use":"educational image per photo license",
              "public_reuse":"noncommercial-only with attribution and CC BY-NC license",
              "observation_id":str(item["observation_id"]),"photo_id":str(pid)})
 records.append({"photo_id":pid,"file":str(outpath),"creator":record["creator"],"license":record["license"],"reviewed_arrows":len(record["anatomy_arrows"]),"sha256":item["saved_sha256"]})
with MANIFEST.open("w",newline="",encoding="utf-8") as fh:
 writer=csv.DictWriter(fh,fieldnames=fields);writer.writeheader();writer.writerows(rows)

count=sum(len(i.get("anatomy_arrows",[])) for i in images)
assert count==17,f"Expected 17 arrows after 12 prior plus 5 reviewed, got {count}"
s["photo_note"]="SEVEN real source photographs installed, including five photographed panels with 17 actual pixel-reviewed arrows; two new macro photographs by Lucy Cash and karlabalrey show terminal head placement, thin hairs on STEM and LEAF, but NOT diagnostic tiny capsule hairs, true stipules or mature seeds. All image sources credited per image, two CC BY-NC sources used only on noncommercial educational site. No county-native-range promotion."
s["curation_status"].update({"last_reviewed":"2026-10-21","photo_metadata_count":7,"photo_files_present":7,"annotated_real_photo_count":6,"verified_arrow_count":17,"field_status":"FIELD_READY_HEADS_AND_HAIRS_WITH_CAPSULE_STIPULE_SEED_MACRO_HOLDS"})
s["learner_visual_status"].update({"image_count":7,"annotated_source_count":6,"verified_arrow_count":17,"status":"field_ready_photo_gaps","mode":"six_annotated_source_photos_seventeen_real_arrow_endpoints","note":"Four previously source-reviewed macro/habit panels plus two new saved-source-pixel-reviewed CC BY-NC terminal head/stem/leaf panels. Mature separate capsule, stipules and detached seed remain unverified."})
s["field_id_finalization"].update({"stage":"FIELD_READY_HEADS_AND_HAIRS_WITH_THREE_CRITICAL_MICRO_GAPS","canonical_photo_count":7,"public_eligible_gallery_photos":7,"real_source_photos_annotated":6,"verified_anatomy_arrows":17,
"photo_review":"All 14 candidate photographs were reviewed; ONLY two additional meaningful and physically verified exact-species images promoted (one hairy stem/terminal flowering head, one reddish head with hairy leaf). Neither justifies a mature capsule hair or seed arrow."})
s["field_photo_quickcheck"]["featured_photo_indices"]=[5,6,3,2,4,1,0]
s["visual_comparison"]["subtitle"]="Six separately source-reviewed annotated photos (17 pointers total) across seven credited files: terminal heads, hairy stem and leaves, opposite teeth, low mat. Fine capsule, stipules and seed are photo gaps."
s["visual_comparison"]["items"]=[it for it in s["visual_comparison"]["items"] if not any(it.get("image_url","").endswith(config["new_file"]) for config in wanted.values())]
for pid,config in wanted.items():
 rec=next(x for x in images if x.get("photo_id")==pid)
 view={"label":"Hairy stem and tight flowering head" if pid==103176610 else "Reddish head and hairy leaves",
 "scientific_name":"Euphorbia ophthalmica","image_url":f"content/taxa/Euphorbiaceae/Euphorbia/euphorbia-ophthalmica/{rec['file']}",
 "image_role":rec["role"],"creator":rec["creator"],"license":rec["license"],"license_url":rec["license_url"],
 "source_page":rec["source_page"],"image_fit":"contain","caption":rec["caption"],
 "markers":[{"label":v["label"],"target_x":round(v["target_fraction"][0]*100),"target_y":round(v["target_fraction"][1]*100),
 "label_x":5 if k%2==0 else 69,"label_y":12+23*k} for k,v in enumerate(rec["anatomy_arrows"])],
 "image_pixel_audit":rec["manual_arrow_review"]}
 s["visual_comparison"]["items"].append(view)

c=next(c for c in g["comparison_cards"] if c["id"]=="euphorbia-ophthalmica-hirta-terminal-glomerules")
c["look_here_first"]="TRACE EACH HEAD TO ITS STEM: OPHTHALMICA has dense heads at main and SHORT LEAFY side-branch tips, plus hairy (usually low) stems and small toothed opposite leaves. HIRTA ALSO has terminal heads but commonly additionally bears AXILLARY heads, sometimes on LONG LEAFLESS stalks; observing one terminal head never rules out hirta. HYPERICIFOLIA makes similarly tight heads but tends to have hairless stems and smooth fruit; NUTANS usually has leafier, less crowded cyathia and larger leaves. True ophthalmica capsule hairs, divided stipules and low-ridged tiny seeds still need microscopic photo documentation. No county-level native status inferred."
c["reviewed_at"]="2026-10-21"
c["status"]="OPHTHALMICA_FIELD_READY_EXTERIOR_FEATURES_17_ARROWS_WITH_THREE_MICRO_PHOTO_HOLDS"
c["photo_pair_targets"]=[{**x,"status":("NEWLY CHECKED: 7 licensed source files, six anatomy-arrowed with 17 pointers; two reviewed added terminal head and hairy stem/leaf photos. Mature separate capsule, seed and stipule remain unphotographed at needed magnification.")} if x["role"]=="Ophthalmica terminal-only cluster field context" else x for x in c["photo_pair_targets"]]
c["photo_review_2026_10_21"]={"new_licensed_source_photos":2,"total_canonical_photos":7,"verified_anatomical_arrow_targets":17,
"limitations":["Two new macros don't independently resolve mature capsule pubescence","No real detached seed macro","No measured divided stipule photograph","E. hirta is text reference not pictured; no source swap"]}
for pid,config in wanted.items():
 rec=next(x for x in images if x.get("photo_id")==pid)
 g["visual_comparison"]["items"]=[x for x in g["visual_comparison"]["items"] if x.get("image_url")!=f"content/taxa/Euphorbiaceae/Euphorbia/euphorbia-ophthalmica/{rec['file']}"]
 item=next(x for x in s["visual_comparison"]["items"] if x.get("image_url","").endswith(rec["file"]))
 g["visual_comparison"]["items"].append({**item,"comparison_role":"Actual source-verified ophthalmica condensed heads and STEM/LEAF hairs; contrast with E. hypericifolia smooth stems; E. hirta has additional axillary heads."})
g["curation_status"]["last_reviewed"]="2026-10-21"
g["curation_status"]["ophthalmica_hirta_pair"]="OPHTHALMICA_EXTERNAL_FIELD_READY_7_PHOTOS_17_ARROWS; FRUIT_STIPULE_SEED_MACROS_REQUIRED"

SPECIES.write_text(json.dumps(s,indent=2,ensure_ascii=False)+"\n")
GENUS.write_text(json.dumps(g,indent=2,ensure_ascii=False)+"\n")
REPORT.parent.mkdir(parents=True,exist_ok=True)
REPORT.write_text(json.dumps({"date":"2026-10-21","taxon":"Euphorbia ophthalmica","status":"FIELD_READY_DIAGNOSTIC_HEADS_WITH_CRITICAL_MICRO_PHOTO_HOLDS","source_records":records,
"canonical_real_photos":len(images),"total_checked_arrows":count,
"missing":["True individually pubescent capsule macro","Separate subulate/divided stipules with scale","Detached mature seed with actual 3–6 shallow crosswise ridges and millimeter ruler"],
"rights":"Two added photos individually CC BY-NC, genuinely noncommercial educational use with attribution; source links and original observation/photo IDs retained",
"range":"FNA does not include Texas in its U.S. distribution list; Texas iNat observation or guide not sufficient to assert native-to-Hays; county native HOLD unchanged."},indent=2)+"\n")
print(json.dumps({"photos":len(images),"arrows":count,"new":records},indent=2))
