#!/usr/bin/env python3
"""Promote TWO *already inspected and individually licensed* Zizaniopsis images.

Photo #264449018: whole wetland plant/leaf architecture.
Photo #264449037: true culm node & visible leaf–sheath junction, NOT an exposed ligule.
Source: Alex Abair, 2023 Florida iNaturalist obs 153134793, CC BY 4.0.
Wikimedia file-source SHA1 and EXIF-free JPEG SHA256 in prior report.
No other taxa, county flags, holds, automation or photo rights change.
"""
import csv,json,hashlib,shutil
from pathlib import Path
from PIL import Image
P=Path("content/taxa/Poaceae/Zizaniopsis")
SP=P/"zizaniopsis-miliacea/species.json"
GP=P/"genus.json"
CSV=P/"zizaniopsis-miliacea/image-sources.csv"
SOURCE=Path("reports/zizaniopsis-cc-by-photo-review-20261021.json")
REPORT=Path("reports/zizaniopsis-giant-cutgrass-gallery-20261021.json")
MARKER=Path("workflow/field-id-publication/manual-zizaniopsis-singleton-20261021.json")
REQUIRED=[
 (264449018,"giant-cutgrass-alex-abair-habit-264449018.jpg","2 · Wild wetland growth, broad arching blades",
  "The source-photo identified giant cutgrass clump shows long arching green blades rising from dense vegetation in open marsh. Underground rhizomes and a complete flowering stalk are NOT exposed.",
  "A wild-source growth-form view, not a proof of county nativity, exposed rhizomes or species-diagnostic flowering structures.",
  [{"label":"Broad arching blades","label_x":4,"label_y":73,"target_x":30,"target_y":69},
   {"label":"Coarse leafy clump","label_x":63,"label_y":80,"target_x":48,"target_y":67}]),
 (264449037,"giant-cutgrass-alex-abair-sheath-264449037.jpg","3 · Stem node and real leaf–sheath junction",
  "The archived photo shows a swollen culm node higher on the stem and a grass blade leaving its lower enclosing sheath. The 6–20-mm membranous ligule is INSIDE this junction and not independently exposed or measured in this photograph. Minute margin teeth cannot be measured.",
  "Real photographic stem and collar location to guide where the crew should open a sheath and measure the long paperlike ligule, without pretending to show it.",
  [{"label":"Visible culm node","label_x":5,"label_y":13,"target_x":47,"target_y":18},
   {"label":"Blade–sheath junction","label_x":69,"label_y":69,"target_x":50,"target_y":61}])
]
def dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n")
def main():
    src=json.loads(SOURCE.read_text())
    assert src["taxon"]=="Zizaniopsis miliacea" and src["physically_staged"]>=3
    verified={p["photo_id"]:p for p in src["candidates"] if p["status"]=="PHYSICALLY_STAGED_FOR_PIXEL_REVIEW_ONLY"}
    s=json.loads(SP.read_text());g=json.loads(GP.read_text())
    assert s["scientific_name"]=="Zizaniopsis miliacea" and g["project_scope"]["species_ids"]==["zizaniopsis-miliacea"]
    originalids={int(i.get("photo_id",0)) for i in s["images"]}
    ids={x[0] for x in REQUIRED}
    if ids.issubset(originalids):
        for ident in ids:
            rec=next(x for x in s["images"] if x.get("photo_id")==ident)
            assert rec["creator"]=="Alex Abair" and rec["license"]=="CC BY 4.0"
            assert (SP.parent/rec["file"]).is_file()
        print("Already installed and rights-validated; NOOP");return
    assert not originalids.intersection(ids),"Another worker installed one; stop, do not duplicate"
    assert len(s["images"])==1 and len(s["visual_comparison"]["items"])==1 and len(g["visual_comparison"]["items"])==1
    old_species={k:json.dumps(s.get(k),sort_keys=True) for k in ["taxonomy_source","identification_caution","native_target_zone_calculated","project_inclusion","county_occurrences_target_zone"]}
    old_scope=json.dumps(g["project_scope"],sort_keys=True)
    newimages=[]; panels=[]; recorded=[]
    for pid,filename,label,caption,why,arrows in REQUIRED:
        x=verified[pid]
        assert x["creator"]=="Alex Abair" and x["license"]=="CC BY 4.0"
        f=Path(x["path"])
        assert f.is_file() and f.stat().st_size>20000
        assert hashlib.sha256(f.read_bytes()).hexdigest()==x["sanitized_sha256"]
        with Image.open(f) as img:
            assert img.format=="JPEG" and min(img.size)>=800
            assert not img.getexif().get(34853)
            img.verify()
        target=SP.parent/"images"/filename
        assert not target.exists()
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(f,target)
        img={
           "file":"images/"+filename,"role":label,
           "creator":"Alex Abair","license":"CC BY 4.0",
           "license_url":"https://creativecommons.org/licenses/by/4.0/",
           "source_page":x["file_page"],"media_source_url":x["source_original_url"],
           "source_observation":"https://www.inaturalist.org/observations/153134793",
           "photo_id":pid,"source_original_sha1":x["source_sha1"],
           "archive_image_sha256":x["sanitized_sha256"],
           "source_locality":"Florida, NOT Hays County",
           "photo_review":"Individual CC grant & source SHA1 verified in Wikimedia API; original JPEG visually examined manually 2026-10-21. Gross features only, no measured ligule or reproductive sex.",
           "study_use":"Public educational grass field identification",
           "public_reuse":"CC BY 4.0 Alex Abair; credit source and note sanitized/EXIF removal.",
           "modifications":"Saved JPEG without EXIF/GPS, resized to 1400 maximum dimension; overlays rendered in browser."
        }
        newimages.append(img)
        for a in arrows:
            assert all(isinstance(a[k],(int,float)) and 0<=a[k]<=100 for k in ["label_x","label_y","target_x","target_y"])
        panels.append({
           "label":label,"scientific_name":"Zizaniopsis miliacea",
           "image_url":"content/taxa/Poaceae/Zizaniopsis/zizaniopsis-miliacea/images/"+filename,
           "image_fit":"contain",
           "image_role":"Actual individual-photo verified 2023 Florida wild-source giant cutgrass; habitat or stem/collar macro, no reproductive sex or true membrane ligule visibility",
           "caption":caption,"why_it_matters":why,"creator":"Alex Abair",
           "license":"CC BY 4.0","license_url":"https://creativecommons.org/licenses/by/4.0/",
           "source_page":x["file_page"],
           "photo_status":"PHYSICALLY INSTALLED exact-source CC BY 4.0, original original source SHA1 checked, visible gross feature arrows manually inspected; still source-determined and Florida only.",
           "markers":arrows
        })
        recorded.append({"file":str(target),"photo_id":pid,"source_sha1":x["source_sha1"],"sha256":x["sanitized_sha256"]})
    s["images"].extend(newimages)
    s["visual_comparison"]["items"].extend(panels)
    g["visual_comparison"]["items"].extend(panels)
    subtitle="Three physically archived, individually CC BY 4.0 Alex Abair photographs: open flowering panicle, broad-leafed marsh habit, and actual stem node/leaf-sheath junction. Six visible-only arrows. No image yet shows the 6–20-mm papery ligule, actual male/female spikelet sex or leaf-edge serrations at true macro."
    for obj in (s,g):
        obj["visual_comparison"]["title"]="Giant cutgrass — open panicle, coarse marsh habit and culm collar"
        obj["visual_comparison"]["subtitle"]=subtitle
        obj["visual_comparison"]["overlay_note"]="Three independently CC BY 4.0 source-matched Alex Abair Florida JPEGs physically installed and verified; two new distinct original images from per-photo Wikimedia SHA1 proof plus older original. Six visible-only gross arrows. Blade–sheath junction DOES NOT expose true inner long 6–20mm ligule; no unsupported male/female or tiny serration annotations. No county native or taxonomy change."
    s["learner_visual_status"]["image_count"]=3
    s["learner_visual_status"]["note"]="Three physically present credited Alex Abair CC BY 4.0 photographs; actual wetland clump, open panicle and culm/sheath. No measured ligule or male/female micro macro."
    s["field_id_finish_pass"]["stage"]="FIELD_READY_PHOTO_GAPS — 3 physically verified source photos, six gross arrows; real long 6–20mm ligule and matched male-below-female spikelet macro STILL missing"
    s["field_id_finish_pass"]["arrow_count"]=6
    s["field_id_finish_pass"]["original_photo_actually_inspected"]=True
    s["photo_note"]="Two new independently licensed, true source-pixel-reviewed images added alongside existing Florida panicle photo: wetland stand and close stem/sheath. Source licenses CC BY 4.0 retained, Florida not Hays. Six visible gross arrows. Critical 6–20mm long membranous ligule and male/female spikelet identity remain photography gaps."
    s["curation_status"]["photo_files_present"]=3
    s["curation_status"]["photo_metadata_count"]=3
    s["curation_status"]["giant_cutgrass_three_photo_manual_20261021"]="Three physical source CC BY 4.0 original images; two new meaningful views of broad-leaved stand and actual collar, four new real arrow anchors; still long ligule, leaf teeth and separated sexes macro missing"
    g["visual_status"]=s["field_id_finish_pass"]["stage"]
    g["curation_status"]["giant_cutgrass_three_photo_manual_20261021"]="Singleton improved from one to three locally stored CC BY 4.0 source-matched photos, six visible-only arrows; science and native-range holds maintained"
    assert all(json.dumps(s.get(k),sort_keys=True)==v for k,v in old_species.items())
    assert json.dumps(g["project_scope"],sort_keys=True)==old_scope
    assert len(s["images"])==3 and len(s["visual_comparison"]["items"])==3 and len(g["visual_comparison"]["items"])==3
    with CSV.open(newline="",encoding="utf8") as f:
        rr=csv.DictReader(f);cols=rr.fieldnames;rows=list(rr)
    for i in newimages:
        v={"file_name":Path(i["file"]).name,"role":i["role"],"creator":i["creator"],
           "license":i["license"],"source_page":i["source_page"],"direct_url":i["media_source_url"],
           "study_use":i["study_use"],"public_reuse":i["public_reuse"],
           "observation_id":"153134793","photo_id":str(i["photo_id"])}
        rows.append({k:v.get(k,"") for k in cols})
    with CSV.open("w",newline="",encoding="utf8") as f:
        ww=csv.DictWriter(f,fieldnames=cols,lineterminator="\n");ww.writeheader();ww.writerows(rows)
    dump(SP,s);dump(GP,g)
    dump(REPORT,{"taxon":"Zizaniopsis miliacea","species":1,"photos":3,"arrows":6,
      "new_photos":recorded,"licenses":"All 3 Alex Abair CC BY 4.0",
      "science_native_county_preserved":True,"remaining":["6–20mm long membrane ligule macro","separate male below female spikelet reproductive macro","leaf edge serrations measured","non-FL source voucher"]})
    dump(MARKER,{"type":"manual_field_id_publication","requested_at":"2026-10-21",
      "title":"Zizaniopsis singleton 3-photo field learner upgrade",
      "species":"Zizaniopsis miliacea","genus":"Zizaniopsis","new_photos":2,"total_photos":3,"arrows":6,
      "license":"CC BY 4.0 Alex Abair","reproduction":"source verified actual two different photos and EXIF-free bytes",
      "county_nativity_unchanged":True,"science_holds_maintained":True,
      "deployment":"Rights-filtered GitHub Pages publish event requested, not verified"})
    print("PASS 2 photos installed, 3 species & genus panels, 6 gross arrows")
if __name__=="__main__":main()
