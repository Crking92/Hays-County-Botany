#!/usr/bin/env python3
"""One-time user-approved introduced purple deadnettle first card.
Fetch exact licensed Wikimedia Commons photo bytes, verify image-level rights,
install canonical card, update henbit and genus, and preserve science/claims.
No other plants, automations, or county native statuses are changed.
"""
import csv, hashlib, io, json, time
from datetime import datetime, timezone
from pathlib import Path
import requests
from PIL import Image, ImageOps

ROOT=Path(".")
BASE=ROOT/"content/taxa/Lamiaceae/Lamium"
NEW=BASE/"lamium-purpureum"
CARD=NEW/"species.json"
HEN=BASE/"lamium-amplexicaule/species.json"
GEN=BASE/"genus.json"
MAN=ROOT/"data/manifest.json"
PROJ=ROOT/"data/project.json"
REPORT=ROOT/"reports/manual-lamium-purpureum-firstcard-20261021.json"
ID="lamium-purpureum"
N="Lamium purpureum"
WIKI="https://commons.wikimedia.org/wiki/File:"
SOURCES=[
 {"title":"Lamium_purpureum_plant.jpg",
  "file":"images/purple-deadnettle-arthur-badel.jpg",
  "creator":"Arthur Badel","license":"CC BY-SA 4.0",
  "license_url":"https://creativecommons.org/licenses/by-sa/4.0/",
  "role":"Flowering purple deadnettle: pointed purplish crowded top leaves, greener lower foliage and lilac flowers; source in France; petiole close-up not resolved."},
 {"title":"Lamium_purpureum_-_March_2025_-_Sarah_Stierch.jpg",
  "file":"images/purple-deadnettle-sarah-stierch.jpg",
  "creator":"Sarah Stierch","license":"CC0 1.0",
  "license_url":"https://creativecommons.org/publicdomain/zero/1.0/",
  "role":"Independently sourced exact purple deadnettle plant from Sonoma, California; supplemental field habit, no Texas provenance."}
]
S=requests.Session()
S.headers.update({"User-Agent":"HaysCountyBotanyLamiumFirstCard/1.0 (educational plant imagery)"})

def js(path):
    return json.loads(path.read_text(encoding="utf-8"))
def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
def source_page(title):
    from urllib.parse import quote
    return WIKI+quote(title,safe="_().-")
def get_source(src):
    params={"action":"query","format":"json","formatversion":"2","titles":"File:"+src["title"],"prop":"imageinfo","iiprop":"url|size|extmetadata","iiurlwidth":"960"}
    result=S.get("https://commons.wikimedia.org/w/api.php",params=params,timeout=38)
    result.raise_for_status()
    pages=result.json()["query"]["pages"]
    assert len(pages)==1 and pages[0].get("imageinfo"),"Commons file missing: "+src["title"]
    info=pages[0]["imageinfo"][0]
    lic=info.get("extmetadata",{}).get("LicenseShortName",{}).get("value","").upper()
    expect=src["license"].upper()
    if expect=="CC0 1.0":
        assert "CC0" in lic or "CC-ZERO" in lic,("Unexpected license",src["title"],lic)
    else:
        assert lic==expect,("Unexpected license",src["title"],lic,expect)
    url=info.get("thumburl")
    assert url and url.startswith("https://") and "wikimedia.org" in url
    res=S.get(url,timeout=60)
    res.raise_for_status()
    assert 18000<len(res.content)<11_000_000,("Unexpected photo size",src["title"],len(res.content))
    with Image.open(io.BytesIO(res.content)) as im:
        im.load()
        im=ImageOps.exif_transpose(im).convert("RGB")
        assert min(im.size)>=320,("Image too small",src["title"],im.size)
        im.thumbnail((1500,1500),Image.Resampling.LANCZOS)
        output=io.BytesIO()
        im.save(output,format="JPEG",quality=90,optimize=True,progressive=True)
        dims=im.size
    data=output.getvalue()
    with Image.open(io.BytesIO(data)) as check:check.verify()
    return data,dims,url,hashlib.sha256(data).hexdigest()

def main():
    manifest=js(MAN)
    ids={entry["id"] for entry in manifest["species"]}
    if ID in ids or CARD.exists():
        if ID in ids and CARD.exists():
            existing=js(CARD)
            pics=existing.get("images",[])
            assert len(pics)>=1 and all((NEW/item["file"]).exists() for item in pics)
            enrich_flower_macros()
            return
        raise RuntimeError("Partial install: manifest/card mismatch; manual reconciliation required")
    claims=js(ROOT/"workflow/work-claims.json").get("claims",[])
    assert not any(c.get("status") in ("claimed","active") and
                   (ID in (c.get("taxa") or []) or ID in json.dumps(c.get("scope_key",""))) for c in claims), "Active first-card work claim"
    hen=js(HEN);genus=js(GEN)
    assert hen["id"]=="lamium-amplexicaule"
    assert genis(genus),"Genus state has changed, please rebase manually"
    assert gen_scope(genus)==["lamium-amplexicaule"]
    assert any(z.get("scientific_name")=="Lamium purpureum" for z in hen["visual_comparison"]["items"]), "Expected credited comparison absent"
    fetched=[]
    for src in SOURCES:
        data,dims,url,digest=get_source(src)
        fetched.append((src,data,dims,url,digest))
        time.sleep(.6)
    # Every photo verified before writing anything to canonical content.
    NEW.mkdir(parents=True,exist_ok=False)
    (NEW/"images").mkdir()
    items=[]
    for src,data,dims,url,digest in fetched:
        target=NEW/src["file"]
        target.write_bytes(data)
        with Image.open(target) as f:f.verify()
        row=dict(src)
        row.update(source_page=source_page(src["title"]),source_platform="Wikimedia Commons",
                   downloaded_from=url,sha256=digest,image_dimensions=list(dims),
                   study_use="Public educational botanical field guide",
                   public_reuse="Cleared under verified exact-image Commons license with source and creator credit.",
                   modifications="Resized public Commons JPEG thumbnail; converted to RGB; stripped EXIF/GPS; web marker overlays are separate.")
        items.append(row)
    original_panel=next(z for z in hen["visual_comparison"]["items"] if z.get("source_page")==items[0]["source_page"] or z.get("image_url","").endswith("Lamium_purpureum_plant.jpg"))
    assert len(original_panel.get("markers",[]))==3
    main_panel=dict(original_panel)
    main_panel.update(label="PURPLE DEADNETTLE — pointed upper leaf cap",scientific_name=N,
        image_url=str(NEW/items[0]["file"]),
        caption="True L. purpureum (Arthur Badel, CC BY-SA 4.0), not henbit. Crowded small POINTED purplish upper leaves above green lower leaves and lilac flowers. This photo does NOT reveal a complete upper petiole junction: inspect a living upper leaf underneath the crown.",
        why_it_matters="The upper triangular purple leaf cap suggests purple deadnettle; trace a SHORT PETIOLE to distinguish it confidently from henbit's sessile green collar.",
        photo_status="PHYSICAL SOURCE PHOTO, licensed and source verified; 3 inherited previously inspected visible-structure arrows; mobile arrow verification pending.")
    secondary={
       "label":"PURPLE DEADNETTLE — second independently sourced whole plant",
       "scientific_name":N,"image_url":str(NEW/items[1]["file"]),"image_fit":"contain",
       "creator":items[1]["creator"],"license":items[1]["license"],"license_url":items[1]["license_url"],
       "source_page":items[1]["source_page"],
       "caption":"A different purple deadnettle plant photographed in California by Sarah Stierch, CC0. Use this supplemental view for overall growth habit and compare with henbit. No microscopic petiole, fruit, or cross-section measurements inferred.",
       "why_it_matters":"Independent exact-species recognition photo, not an unlabeled generic mint-family stand-in.",
       "markers":[],"photo_status":"PHYSICAL JPEG VERIFIED, no anatomy arrows until direct target pixel review."
    }
    henpanel=dict(hen["visual_comparison"]["items"][0])
    henpanel.update(label="DIFFERENT SPECIES — HENBIT HAS UPPER CLASPING LEAVES",scientific_name="Lamium amplexicaule",
        caption="COMPARE-ONLY: this is HENBIT, NOT PURPLE DEADNETTLE. Green round scalloped upper leaves form stalkless collar at nodes; lower leaves have petioles. Contrast deadnettle's typically short-stalked pointed purple leaf cap.",
        markers=[henpanel["markers"][0],henpanel["markers"][2]],
        why_it_matters="Look at leaf attachment, not purple petals or four-sided stems.",
        photo_status="Already installed CC BY 2.0 Harry Rose source image, reused as correctly labeled other-species comparison.")
    card={
      "id":ID,"entry_type":"species","family":"Lamiaceae","genus":"Lamium","species":"purpureum",
      "scientific_name":N,"authority":"L.","common_name":"Purple deadnettle",
      "alternate_common_names":["Red deadnettle","Red henbit"],
      "look_here_first":"LOOK HERE FIRST: a cool-season winter ANNUAL with opposite heart/triangular SCALLOPED leaves, the upper ones CROWDED into a reddish-purple pointed top. Follow an UPPER leaf all the way to the stem: it retains a SHORT PETIOLE and DOES NOT form a stalkless collar. Henbit L. amplexicaule instead has rounded/lobed SESSILE upper leaves encircling the stem; both make pink-purple two-lipped flowers on square stems. Purple color varies with light/stage and is NOT diagnostic by itself.",
      "taxonomy_source":"https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:448939-1",
      "taxonomy_notes":"POWO accepted Lamium purpureum L., not a henbit synonym; may include different infraspecific concepts but this learner card does not identify varieties.",
      "project_inclusion":{
        "learner_admission_status":"USER_EXPLICIT_APPROVAL_20261021_FIRST_CARD",
        "source_pool":"User approved adding the henbit look-alike as its own card",
        "target_zone_status":"INTRODUCED_NON_NATIVE",
        "native_metrics_excluded":True,
        "notes":"POWO confirms species introduced in Texas and native to Europe/western Asia/Med. Not a native restoration recommendation; no official Texas invasive designation asserted.",
        "native_county_audit":"NOT_PERFORMED_AND_NOT_REQUIRED_FOR_UNAMBIGUOUS_EXOTIC"
      },
      "morphology_keys":{
        "life_cycle":"Cool-season herbaceous winter annual with shallow roots and square stems often rooting at low nodes.",
        "leaf_arrangement":"Opposite at stem nodes, prominently crenate/scalloped; lower foliage broadly ovate/heart shaped and petiolate.",
        "upper_leaf":"Upper leaves short-stalked (PETIOLATE), crowded, more triangular/pointed, often distinctly purplish. Unlike henbit the bases don't form complete green stem-clasping collars; examine from below when top leaves overlap.",
        "flowers":"Clusters (verticillasters) at upper nodes; pink-purple tubular two-lipped flowers, upper hood and patterned lower lip with pollen-bearing stamens.",
        "stem":"Four-angled, often purplish near nodes; hairs can be sparse; cross-section is a mint FAMILY clue, not species-only proof.",
        "fruits":"Four little nutlets develop within persistent calyx; mature nutlet/fruit macro not yet available.",
        "habitat":"Disturbed winter-spring open ground, turf margins, beds, fields and paths; it is introduced and can provide nectar without constituting native host-plant support."
      },
      "comparisons":{
        "confused_with":["Lamium amplexicaule (henbit)","Glechoma hederacea (ground ivy, different genus)"],
        "key_distinctions":"PURPUREUM: pointed purple-tinged upper leaves with short PETIOLES; AMPLEXICAULE: green round/lobed upper leaves SESSILE/clasping. Both may have purplish blooms and square stems. Glechoma creeps as perennial and retains petioles to flowers.",
        "field_matrix":[
         {"taxon":"Lamium purpureum","quick_rule":"Upper leaves retain short stalks and cluster into pointed often-purple cap","upper_leaf_base":"PETIOLATE (especially look underneath upper canopy)","habit":"Winter annual","flower_position":"Pink bilabiate flowers partly tucked among compact purple upper leaves"},
         {"taxon":"Lamium amplexicaule","quick_rule":"Upper leaves are sessile rounded/lobed collars on stem","upper_leaf_base":"Clasping/stalkless at mature upper nodes","habit":"Winter annual","flower_position":"Long projecting purple tubes rising above green upper collars"},
         {"taxon":"Glechoma hederacea","quick_rule":"Creeping perennial, stolons and stalked rounded leaves near flower","upper_leaf_base":"Petiolate at flowering nodes","habit":"Perennial creeper","flower_position":"Broader purple flowers in leaf axils"}
        ],
        "not_reliable_alone":["A purple top is common but may be faint or missing.","Square stems/opposite leaves establish mint-family resemblance, not exact species.","Young rosettes lack fully developed upper flowering nodes.","Close petioles may be hidden beneath dense purple top foliage."]
      },
      "images":items,
      "visual_comparison":{
        "title":"Purple deadnettle — top leaves, petioles and the henbit split",
        "subtitle":"Two physically stored exact purple deadnettle licensed photographs (Arthur Badel CC BY-SA 4.0 and Sarah Stierch CC0), plus one different-species henbit photograph. Three source-verified anatomy arrows on Badel's photo; more close-up petiole, corolla and nutlet images are still needed.",
        "memory_rule":"PURPLE POINTED UPPER CAP + SHORT PETIOLES = PURPLE DEADNETTLE. ROUND SESSILE GREEN COLLARS = HENBIT.",
        "items":[main_panel,secondary,henpanel],
        "part_examples":[
         {"title":"Pointed purple upper leaf cap","role":"upper leaves","anchor_species_id":ID,"image_file":items[0]["file"],"look_for":"Pointed/triangular top leaves, often maroon, above greener scalloped lower leaves.","why_it_matters":"Memorable visual cue; leaf color alone is not decisive."},
         {"title":"Compare henbit's collar","role":"look-alike only","anchor_species_id":"lamium-amplexicaule","image_file":"images/lamium-amplexicaule-habit-commons.jpg","look_for":"Round, stalkless upper collar leaves","why_it_matters":"Leaves, not flower color, settle this pair."},
         {"title":"NEED MACRO: actual upper petiole base","role":"petiole vs clasping","status":"needs_photo","look_for":"Short stalk and attachment under the top purple leaves, with mm ruler.","why_it_matters":"Decisive split from henbit."},
         {"title":"NEED MACRO: flower and nutlets","role":"reproductive details","status":"needs_photo","look_for":"Open upper hood/lower lip front and side, plus ripe calyx holding four nutlets with scale.","why_it_matters":"Fruit and detailed corolla remain photo gaps."}
        ]
      },
      "field_photo_quickcheck":{
        "heading":"Purple deadnettle — look at the upper leaves",
        "featured_photo_indices":[0],
        "steps":["Locate crowded pointed purplish upper leaves and greener rounded stalked lower leaves.","Carefully lift an upper leaf and check for a very SHORT STALK, not a clasping leaf collar.","Confirm opposite leaves and pink-purple two-lipped flower whorls; then compare a henbit upper node."],
        "field_rule":"Purple pointed upper cap + short upper petiole = L. purpureum. Henbit = green rounded upper sessile collar.",
        "warning":"Current main photo shows the purple pointed canopy clearly but DOES NOT prove its hidden upper leaf petiole. Do not invent a petiole arrow.",
        "owner_phone_review":"PENDING"
      },
      "curation_status":{
        "taxonomy_identity_checked":True,"photo_source_checked":True,"visual_reviewed":False,
        "lookalikes_reviewed":True,"photo_metadata_count":len(items),"photo_files_present":len(items),
        "version":"1.0-user-approved-purple-deadnettle-firstcard-20261021","last_reviewed":"2026-10-21",
        "visual_status":"FIELD_READY_PHOTO_GAPS: two exact licensed physical images and correct look-alike lesson, three inspected main visual arrows; upper leaf petiole insertion, flowering macro, seed nutlets missing."
      },
      "learner_visual_status":{"status":"field_ready_photo_gaps","mode":"user_approved_first_card_with_enrichment","image_count":len(items)},
      "diagnostic_photo_targets":[
        "MM-SCALE underside upper leaf petiole insertion (don't assume photo proves this under crowded leaf cap)",
        "Fresh open flower front/side showing hood, lower spotted corolla, stamens",
        "Square stem in cross-section and mature four-nutlet calyx, each with mm ruler",
        "Paired henbit stalkless green collar versus deadnettle short stalk on same photo scale"
      ],
      "management_notes":{"local_status":"Introduced encounter winter annual; no claim of official Texas invasive listing.","low_chemical":"Identify before pulling; hand remove small plants before seeds if control desired, reduce bare disturbed soil and favor competitive desired native plantings."}
    }
    assert card["id"]==ID and len(card["images"])==2
    # Site reads manifest; a card is not installed until images AND manifest exist.
    write(CARD,card)
    with (NEW/"image-sources.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=["file_name","creator","license","source_page","direct_url","role","public_reuse"])
        w.writeheader()
        for item in items:
            w.writerow({"file_name":Path(item["file"]).name,"creator":item["creator"],
            "license":item["license"],"source_page":item["source_page"],"direct_url":item["downloaded_from"],
            "role":item["role"],"public_reuse":item["public_reuse"]})
    (NEW/"SOURCES.txt").write_text("User explicitly approved adding Lamium purpureum as henbit look-alike on 2026-10-21.\n"+
      "Accepted name and introduced-Texas status: https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:448939-1\n"+
      "Distinctions: https://cals.cornell.edu/weed-science/weed-profiles/deadnettles\n"+
      "\n".join(i["source_page"]+" | "+i["creator"]+" | "+i["license"] for i in items)+"\n",encoding="utf-8")
    manifest["species"].append({"id":ID,"path":str(CARD)})
    manifest["species"]=sorted(manifest["species"],key=lambda e:e["id"])
    write(MAN,manifest)
    project=js(PROJ);project["species_count"]=len(manifest["species"])
    project["last_automated_manifest_update"]=datetime.now(timezone.utc).isoformat()
    write(PROJ,project)
    existing_ids=genus["project_scope"]["canonical_species_ids"]
    assert existing_ids==["lamium-amplexicaule"]
    genus["project_scope"]["canonical_species_ids"]=["lamium-amplexicaule",ID]
    genus["project_scope"]["pending_canonical_installer"]=[]
    genus["project_scope"]["lesson_scope"]="Two canonical Lamium encounter species now installed with physical exact-taxon licensed images: henbit L. amplexicaule and purple deadnettle L. purpureum. Glechoma is a DIFFERENT genus and comparison-only. Both Lamium treated as introduced Texas species, excluded from native plant counts."
    genus["project_scope"]["science_status"]="Both Lamium species introduced (L. purpureum POWO confirmed introduced Texas); no target-county native claims or official invasive status asserted."
    genus["look_here_first"]="TWO-WAY CREW KEY: UPPER LEAVES first. HENBIT L. amplexicaule has round, deeply scalloped sessile green COLLARS surrounding square stem; PURPLE DEADNETTLE L. purpureum has more pointed often-purple crowded top leaves with small PETIOLES (lift a top leaf to see the hidden stalk). Both have opposite leaves and purple two-lipped flowers. Ground ivy Glechoma is a perennial creeper with stalked leaves."
    for panel in genus["visual_comparison"]["items"]:
        if panel.get("source_page")==items[0]["source_page"]:
            panel["image_url"]=str(NEW/items[0]["file"])
            panel["photo_status"]="Physically installed exact L. purpureum photograph in new canonical species, maintained author/license and preverified arrows."
    genus["visual_comparison"]["items"].append(secondary)
    genus["visual_comparison"]["title"]="Henbit versus purple deadnettle — the upper leaf tells you"
    genus["visual_comparison"]["subtitle"]="TWO installed Lamium encounter species with actual licensed physical source photos. Henbit 2 photos, purple deadnettle 2 photos; comparison includes photographed rounded sessile henbit collars vs pointed purplish upper deadnettle leaf cap. Petiole macro still missing, so do not overclaim invisible attachment."
    genus["visual_comparison"]["memory_rule"]="HENBIT: ROUND SESSILE GREEN COLLAR. DEADNETTLE: PURPLE POINTED UPPER LEAVES WITH SHORT STALK. GROUND IVY: CREEPING PERENNIAL."
    for c in genus.get("comparison_cards",[]):
        if "Henbit vs purple deadnettle" in c.get("title",""):
            c["species_ids"]=["lamium-amplexicaule",ID]
            c["caution"]="BOTH species are now installed with real physical photo files. Badel source shows purple pointed upper cap, but the short upper stalk is hidden: still requires separate diagnostic node macro. Both are introduced Texas encounters."
            c["status"]="TWO_CANONICAL_SPECIES_FIELD_READY_STALK_MACRO_PENDING"
    genus["lookalike_warnings"]=[q.replace("not installed in current project scope","now installed as an introduced exact-species learner card").replace("comparison-only. Upper leaves","now installed. Upper leaves") for q in genus.get("lookalike_warnings",[])]
    genus["photo_diagnostic_targets"]=[q.replace("Purple deadnettle upper petiole insertion matched","Purple deadnettle now physically installed; upper petiole insertion matched") for q in genus.get("photo_diagnostic_targets",[])]
    genus["curation_status"].update({"version":"1.1-henbit-and-purple-deadnettle-installed-20261021","last_reviewed":"2026-10-21",
        "canonical_species_count":2,"actual_source_species_image_files":4,"lookalike_status":"Two canonical Lamium introduced encounter cards with licensed photos; Glechoma other-genus comparison only.","visual_status":"TWO-SPECIES CREW KEY FIELD_READY_PHOTO_GAPS: upper leaf collar vs short upper petiole. Main deadnettle cap pictured, petiole itself still needs macro; four-nutlet seeds need photos."})
    write(GEN,genus)
    for panel in hen["visual_comparison"]["items"]:
        if panel.get("source_page")==items[0]["source_page"]:
            panel["image_url"]=str(NEW/items[0]["file"])
            panel["photo_status"]="Physical exact-species L. purpureum license-verified image in canonical new sibling species; arrows inherited, correctly labeled not henbit."
    hen["comparisons"]["lookalike_install_status"]="Purple deadnettle L. purpureum now exists as separate canonical species (2 physically stored images); upper stalk contrast remains field-key logic and should be verified in hand lens."
    hen["curation_status"]["version"]="1.2-henbit-purple-deadnettle-paired-20261021"
    hen["curation_status"]["last_reviewed"]="2026-10-21"
    write(HEN,hen)
    report={"species":N,"installed":True,"canonical_photo_files":[str(NEW/i["file"]) for i in items],
        "images":len(items),"source_licenses":[i["license"] for i in items],
        "manifest_count":len(manifest["species"]),"henbit_genus_comparison_updated":True,
        "photo_audit":"Images physically downloaded, rights-checked through Commons API, reencoded with EXIF/GPS stripped and PIL decoded.",
        "pending":"Exact short upper petiole macro, flower macro and mature four nutlets, mobile arrow review.",
        "site_publication":"Not confirmed by this installation workflow; trigger rights-filtered Pages marker afterward."}
    write(REPORT,report)
    print(json.dumps({"installed":ID,"photo_files":2,"manifest_count":len(manifest["species"]),"genus_two_species":True}))

def gen_scope(x):
    return x.get("project_scope",{}).get("canonical_species_ids",[])
def genis(x):
    return x.get("name")=="Lamium" and x.get("family")=="Lamiaceae"

def enrich_flower_macros():
    """Add two separately licensed physical flowering detail views to existing canonical card.
    Never modify fields of any other genus/taxon or change the admitted identity."""
    target=NEW
    card=js(CARD)
    genus=js(GEN)
    if card["id"]!=ID or ID not in gen_scope(genus):raise RuntimeError("Must already be installed")
    flowers=[
       {"title":"Lamium_purpureum_377747368.jpg",
        "file":"images/commons-alex-abair-flower.jpg","creator":"Alexander Abair",
        "license":"CC BY 4.0","license_url":"https://creativecommons.org/licenses/by/4.0/",
        "role":"Flowering L. purpureum original France source; image depicts purple corolla with calyx, site-verified taxon source."},
       {"title":"Lamium_purpureum_flowers.jpg",
        "file":"images/commons-muriel-bendel-flower.jpg","creator":"MurielBendel",
        "license":"CC BY-SA 4.0","license_url":"https://creativecommons.org/licenses/by-sa/4.0/",
        "role":"Additional flower/branch macro of L. purpureum from Switzerland, distinct source; flower parts pending arrow review."}
    ]
    current={x["file"] for x in card.get("images",[])}
    if all(item["file"] in current for item in flowers):
        assert all((target/item["file"]).exists() for item in flowers)
        print("Flower enhancement already installed")
        return
    assert not any(item["file"] in current or (target/item["file"]).exists() for item in flowers), "Partial flower photo install; review required"
    package=[]
    for item in flowers:
        data,dims,url,digest=get_source(item)
        package.append((item,data,dims,url,digest))
        time.sleep(.6)
    for item,data,dims,url,digest in package:
        f=target/item["file"]
        f.parent.mkdir(parents=True,exist_ok=True)
        f.write_bytes(data)
        with Image.open(f) as test:test.verify()
        meta=dict(item)
        meta.update(source_page=source_page(item["title"]),
            source_platform="Wikimedia Commons",downloaded_from=url,
            sha256=digest,image_dimensions=list(dims),
            study_use="Public educational botanical field guide",
            public_reuse="Wikimedia per-photo creator and CC license validated; attribution and ShareAlike apply.",
            modifications="Downloaded verified Commons thumbnail; JPEG normalized and EXIF/GPS stripped; website arrows remain separate.")
        card["images"].append(meta)
        panel={
          "label":"PURPLE DEADNETTLE — new licensed real flower anatomy source",
          "scientific_name":N,
          "image_url":str(target/item["file"]),
          "image_fit":"contain",
          "creator":item["creator"],"license":item["license"],"license_url":item["license_url"],
          "source_page":meta["source_page"],"image_role":item["role"],
          "caption":"True flowering purple deadnettle. Flower/anatomy source from an individually licensed Wikimedia Commons file; no claim of Texas locality. Detailed arrow placements pending direct image pixel review.",
          "why_it_matters":"Independent close flower view will allow hood, lower lip, and calyx cues to be highlighted after image-specific arrow review.",
          "markers":[],
          "photo_status":"Physically installed with creator and exact CC license, source-pixel anatomical arrow QA not yet completed."
        }
        card["visual_comparison"]["items"].append(panel)
        genus["visual_comparison"]["items"].append(dict(panel))
    card["curation_status"].update(photo_metadata_count=len(card["images"]),
        photo_files_present=len(card["images"]),last_reviewed="2026-10-21",
        version="1.1-purpureum-four-physical-photo-20261021",
        visual_status="FIELD READY PHOTO GAPS: four distinct individually licensed physical exact species photos (2 whole plant and 2 flower details). Existing visible arrow targets preserved; new flower photos pending anatomical arrow review and mature nutlets/upper petiole macros remain needed.")
    card["learner_visual_status"]["image_count"]=len(card["images"])
    card["visual_comparison"]["subtitle"]="Four physically installed licensed exact purple deadnettle photos (two whole plant, two flowering details) plus correctly labeled henbit comparison. Existing visible arrows retained; newly installed flower views need arrow verification. The short upper petiole and nutlets remain genuine high-value missing macros."
    genus["curation_status"].update(actual_source_species_image_files=2+len(card["images"]),
        version="1.2-lamium-extra-flower-macros-20261021",
        last_reviewed="2026-10-21",
        photo_panels=len(genus["visual_comparison"]["items"]))
    genus["visual_comparison"]["subtitle"]="Two installed Lamium species: henbit has 2 physical photos; purple deadnettle has 4 physical photos (2 plant, 2 new flower views). All linked creator/license metadata preserved. The lower versus upper leaf attachment remains the main ID distinction; detailed petiole/nutlet macros still needed."
    write(CARD,card)
    write(GEN,genus)
    csvfile=target/"image-sources.csv"
    with csvfile.open(newline="",encoding="utf-8") as f:
        rows=list(csv.DictReader(f));fields=list(rows[0])
    for item,data,dims,url,digest in package:
        row={"file_name":Path(item["file"]).name,"creator":item["creator"],"license":item["license"],
             "source_page":source_page(item["title"]),"direct_url":url,"role":item["role"],
             "public_reuse":"Exact Commons CC BY/SA source rights verified"}
        rows.append(row)
    with csvfile.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    rep=js(REPORT);rep["images"]=len(card["images"])
    rep["additional_flower_images"]=[item["file"] for item in flowers]
    rep["source_licenses"]=list(dict.fromkeys(rep["source_licenses"]+[item["license"] for item in flowers]))
    rep["note"]="Flower image pixels installed and verified; arrows deliberately withheld on new images until visual inspection."
    write(REPORT,rep)
    print(json.dumps({"enriched":ID,"physical_total":len(card["images"])}))

if __name__=="__main__":
    main()
