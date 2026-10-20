#!/usr/bin/env python3
"""One-time exact-species licensed-photo installer for the user-approved divine nightshade.
Do not confuse photo staging with final scientific, visual, or county-native approval.
Source photo URLs and licensing verified against individually named Wikimedia Commons pages.
"""
from __future__ import annotations
import csv
import hashlib
import io
import json
import time
from pathlib import Path
import requests
from PIL import Image, ImageOps, UnidentifiedImageError

ROOT=Path("content/taxa/Solanaceae/Solanum/solanum-nigrescens")
IMAGE_DIR=ROOT/"images"
MANIFEST=Path("data/manifest.json")
GENUS=Path("content/taxa/Solanaceae/Solanum/genus.json")
SOURCE_OBSERVATION="https://www.inaturalist.org/observations/103616257"
LICENSE="https://creativecommons.org/licenses/by/4.0/"
PREFIX="https://commons.wikimedia.org/wiki/File:Solanum_nigrescens_"
SOURCES=[
 dict(pid="173461473",stem="01-whole-plant",hash="f/fe",role="Whole plant, unarmed green stems, alternate leaf blades and white flowers", markers=[
 dict(label="Simple green leaf",label_x=2,label_y=15,target_x=33,target_y=24),
 dict(label="Small white flower",label_x=68,label_y=35,target_x=52,target_y=42)
 ]),
 dict(pid="173461476",stem="02-leaves-flowering",hash="3/39",role="Broad ovate leaf and clustered white flowers with yellow anthers", markers=[
 dict(label="Broad ovate leaf",label_x=2,label_y=76,target_x=27,target_y=57),
 dict(label="White corolla",label_x=71,label_y=23,target_x=62,target_y=37),
 dict(label="Yellow anthers",label_x=73,label_y=53,target_x=63,target_y=40)
 ]),
 dict(pid="173461484",stem="03-flower-anthers",hash="2/2c",role="Flower close-up showing longer yellow anthers and white corolla lobes", markers=[
 dict(label="Long yellow anther",label_x=72,label_y=16,target_x=64,target_y=38),
 dict(label="White corolla lobe",label_x=2,label_y=20,target_x=43,target_y=37)
 ]),
 dict(pid="173461482",stem="04-buds-pedicels",hash="1/14",role="Hairy flower stalk and four hanging unopened buds", markers=[
 dict(label="Closed flower bud",label_x=63,label_y=79,target_x=69,target_y=54),
 dict(label="Hairy flower stalk",label_x=4,label_y=16,target_x=46,target_y=38)
 ])
]
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def save(p,j): p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def get_image(entry):
    """Try individually identified primary iNaturalist open-data media, then Commons originals.
    Both URLs must refer to the *same verified iNaturalist photo ID* from the Commons page.
    No substitute photo or species is permitted."""
    pid=entry["pid"]
    commons=f'https://upload.wikimedia.org/wikipedia/commons/{entry["hash"]}/Solanum_nigrescens_{pid}.jpg'
    inat=f'https://inaturalist-open-data.s3.amazonaws.com/photos/{pid}/original.jpg'
    fallback=f'https://inaturalist-open-data.s3.amazonaws.com/photos/{pid}/large.jpg'
    session=requests.Session()
    session.headers.update({"User-Agent":"HaysCountyBotanyLearner/1.0 (verified Creative Commons public photo research)","Accept":"image/jpeg,image/*;q=0.8"})
    errors=[]
    # First try source iNaturalist open data to avoid Wikimedia's rate-limited raw originals.
    for url in (inat,fallback,commons):
        for tries in range(2):
            try:
                response=session.get(url,timeout=20)
                response.raise_for_status()
                if len(response.content)<25000 or len(response.content)>12_000_000:raise ValueError("unexpected byte size")
                raw=Image.open(io.BytesIO(response.content))
                raw.verify()
                picture=Image.open(io.BytesIO(response.content))
                if min(picture.size)<450:raise ValueError("source resolution too small")
                image=ImageOps.exif_transpose(picture).convert("RGB")
                image.thumbnail((1800,1800),Image.Resampling.LANCZOS)
                out=IMAGE_DIR/(entry["stem"]+".jpg")
                IMAGE_DIR.mkdir(parents=True,exist_ok=True)
                image.save(out,format="JPEG",quality=88,optimize=True,exif=b"")
                with Image.open(out) as reread:reread.verify()
                return out,url,hashlib.sha256(out.read_bytes()).hexdigest(),list(image.size)
            except (requests.RequestException,UnidentifiedImageError,OSError,ValueError) as exc:
                errors.append(str(exc)[:130])
                if tries==0:time.sleep(1)
    raise RuntimeError("Photo "+pid+" all same-photo sources failed: "+"; ".join(errors))

def main():
    if (ROOT/"species.json").exists():
        previous=load(ROOT/"species.json")
        if previous.get("id")=="solanum-nigrescens" and previous.get("images"):
            print("SKIP: a species card with media already exists; never overwrite other workers")
            return
        raise SystemExit("Conflict: preexisting species without expected installed state")
    m=load(MANIFEST)
    if any(x.get("id")=="solanum-nigrescens" for x in m["species"]):raise SystemExit("Existing manifest species ID collision")
    g=load(GENUS)
    records=[];panels=[];errors=[]
    for e in SOURCES:
        try:
            out,url,sha,dimensions=get_image(e)
        except Exception as exc:
            errors.append(str(exc));print("HOLD",str(exc));continue
        pid=e["pid"]
        img={"file":"images/"+out.name,"role":e["role"],
             "creator":"Alex Abair","license":"CC BY 4.0","license_url":LICENSE,
             "source_page":PREFIX+pid+".jpg","media_source_url":url,
             "source_photo_id":pid,"source_observation":SOURCE_OBSERVATION,
             "source_determination":"Solanum nigrescens M.Martens & Galeotti",
             "source_geography":"Florida, USA (not a Hays occurrence record)",
             "image_dimensions":dimensions,"sha256":sha,
             "modifications":"Resized JPEG and EXIF/GPS stripped; plant pixels not otherwise edited. Website SVG annotations are separate.",
             "study_use":"yes","public_reuse":"yes","visual_role_reviewed":True}
        records.append(img)
        panels.append({"label":str(len(panels)+1)+" — "+e["role"],"scientific_name":"Solanum nigrescens",
         "image_url":"content/taxa/Solanaceae/Solanum/solanum-nigrescens/"+img["file"],
         "image_fit":"contain","image_role":e["role"],"creator":"Alex Abair",
         "license":"CC BY 4.0","license_url":LICENSE,"source_page":img["source_page"],
         "markers":e["markers"],
         "caption":e["role"]+". All photographs are the same Florida observation by Alex Abair; they document flowers, leaves and buds, NOT ripe fruit. Arrow overlays are learner-created, not part of the original photograph.",
         "why_it_matters":"Use flower shape, anther proportions, growth habit, or flower-stalk anatomy as appropriate; exact S. americanum separation requires additional ripe fruit/calyx evidence."})
    if not records:
        raise SystemExit("NEEDS_FIRST_PUBLIC_PHOTO: none successfully fetched; species/manifest not installed")
    j={
       "id":"solanum-nigrescens","entry_type":"provisional_species",
       "family":"Solanaceae","genus":"Solanum","species":"nigrescens",
       "scientific_name":"Solanum nigrescens",
       "authority":"M.Martens & Galeotti","common_name":"Divine nightshade / slender nightshade",
       "look_here_first":"LOOK HERE FIRST · An UNARMED herb with ALTERNATE simple green ovate leaves and little WHITE five-lobed flowers. Its yellow anthers are distinctly longer than those of American black nightshade (typically 1.8–2.5 mm versus ca. 0.8–1.5 mm). CONFIRM with mature fruit: S. nigrescens usually has DULL green/dark purplish berries, calyx lobes APPRESSED or spreading against the berry base, and fruit pedicels that spread or droop. S. americanum usually has shiny black berries with tiny calyx lobes STRONGLY REFLEXED backward. Do not assign species confidently from white flowers or immature fruit alone.",
       "county_occurrences_target_zone":[],
       "target_zone_count":0,"native_target_zone_calculated":False,"native_metrics_excluded":True,
       "project_inclusion":{"target_zone_status":"PROVISIONAL","range_basis":"User explicitly selected for the black-nightshade comparison lesson; POWO reports species in Texas; exact Hays County proof not adjudicated.","range_guardrail":"Current learner is encounter-based; do not claim verified Hays County nativity or calculate native scores."},
       "learner_role":"PROVISIONAL_LEARNER",
       "morphology_keys":{
          "family_pattern":"Solanaceae/Solanum: mostly alternate foliage, fused five-lobed corolla, five poricidal anthers, and multi-seeded berry; Morelloid black nightshades are unarmed.",
          "best_field_traits":[
              "Green unarmed branching herb/short-lived perennial; simple alternate ovate leaves, margins entire to shallowly toothed",
              "White 5-lobed rotate/star corolla with projecting yellow relatively elongated anthers",
              "Anthers generally 1.8–2.5 mm, elliptic, not almost globose short anthers as in S. americanum",
              "Fruit ultimately commonly dark purplish or green/dull rather than glossy black; fruit clusters often have spreading/deflexed stalks",
              "Calyx lobes below ripe berry APPRESSED to SPREADING, not strongly reflexed backwards",
              "More than five hard sclerotic granules (stone cells) often in berry; specialist character, not a tasting or field-food lesson"
          ],
          "habit":"Annual or short-lived perennial herb, branching, green, unarmed; stems may be sparsely hairy. Habit alone overlaps the Solanum morelloid group.",
          "leaves":"ALTERNATE simple ovate or elliptic green leaves, entire to wavy/toothed edges, pointed tips, petioles evident. Do not call the species from leaves alone.",
          "flowers":"Small white five-part star flowers, clustered; five equal elongated yellow anthers approximately 1.8–2.5 mm long; pale style projects centrally. Flower macros can show relative size, but no quantitative length is proved without a scale.",
          "fruit":"Immature green berries; mature dark purple to black, often dull/glaucous rather than shiny. Fruiting pedicels spreading or deflexed (tend to depart with fallen berries). The short green calyx lobes remain appressed or spreading under the mature fruit, NOT sharply curled away as typical in S. americanum.",
          "habitat":"Fields, open woodland edges, disturbed and moist areas, forest margins. Flora of North America reports Texas but Hays-local nativity verification deferred.",
          "management":"Do not recommend consuming any part based on image ID. Black-nightshade species overlap and their chemistry varies. Field crew: photograph reproductive structures, avoid bare-handed tasting, and make management decisions after firm ID.",
          "field_terms":{"Anther":"Yellow pollen-producing organ; compare LENGTH and shape against S. americanum, ideally with a millimeter scale.",
            "Calyx":"Green SEPALS under flower or berry; appressed = pressed close to berry, reflexed = bent sharply backward.",
            "Pedicel":"Little individual flower/berry stalk; inspect whether it spreads/droops and stays with fruit when it drops.",
            "Sclerotic granules":"Small hard stone cells inside a berry, NOT the seeds; laboratory-level character, not photographed/verified in this card.",
            "Morelloid group":"Close unarmed black-nightshade species; white stars and black berries alone are not exact IDs."},
          "crew_field_sequence":[
            "1 · Whole plant: unarmed green herb with simple alternate leaves. If prickly, compare the other Solanum cards.",
            "2 · Open flower: find 5 white lobes and the yellow ANTHERS; take a macro with a millimeter scale.",
            "3 · Flower comparison: S. nigrescens anthers usually about 1.8–2.5 mm versus S. americanum short plump ~0.8–1.5 mm.",
            "4 · Mature berry: photograph side view showing fruit luster and green CALYX LOBES; nigrescens calyx typically appressed/spreading.",
            "5 · Fruiting cluster: photograph pedicel direction and stalk attachment. Drooping fruit with calyx close to berry supports nigrescens over americanum.",
            "6 · If only white flower or immature green fruit is visible: record Solanum morelloid complex and return with macro/ripe fruit evidence."
          ],
          "comparison_training":"Hard pair: American black nightshade. Longer anthers + appressed/spreading calyx + duller fruit + spreading/deflexed pedicels favor nigrescens."
       },
       "comparisons":{
          "field_matrix":[
           {"taxon":"Solanum nigrescens · DIVINE NIGHTSHADE","flower":"White star, ellipsoid LONGER anthers typically 1.8–2.5 mm","berries":"Usually matte/dull dark purplish or green mature berry","calyx":"Short lobes APPRESSED to SPREADING at berry base","pedicels":"Spreading or bent downward; often drop with berry","quick_rule":"Longer anthers + calyx touching berry + dull fruit together."},
           {"taxon":"Solanum americanum · AMERICAN BLACK NIGHTSHADE","flower":"Tiny white star; plump SHORT anthers ~0.8–1.5 mm","berries":"Ripe SHINY purple-black","calyx":"Tiny lobes STRONGLY REFLEXED away from mature berry","pedicels":"Spreading/erect, often remain on shoot after fruit drops","quick_rule":"Very short anthers + glossy berry + backwards calyx."},
           {"taxon":"Solanum emulans · EASTERN BLACK NIGHTSHADE","flower":"Short yellow anthers overlap S. americanum, filaments usually relatively longer","berries":"Matte dark fruit, typically more stone cells","calyx":"Appressed/spreading","pedicels":"Usually deflexed/drop with berry","quick_rule":"Short anthers + dull fruit and calyx appressed; harder with only photos."},
           {"taxon":"Solanum interius · CENTRAL PLAINS BLACK NIGHTSHADE","flower":"Anthers may overlap nigrescens (1.8–2.5 mm)","berries":"Often larger ripe fruit; internal granules differ","calyx":"Frequently unequal calyx lobes with rounded tips","pedicels":"Check articulation and inflorescence spacing","quick_rule":"Regional look-alike; larger berries, unequal rounded-tipped calyx lobes."},
           {"taxon":"Solanum nigrum · EUROPEAN BLACK NIGHTSHADE","flower":"Medium yellow anthers, inflorescence frequently more elongated","berries":"Often matte black; lacks stone cells","calyx":"Calyx variable","pedicels":"Usually spreading; fruit/seed diagnostics needed","quick_rule":"Introduced comparison; do not identify by black ripe berries alone."},
           {"taxon":"Solanum rostratum · BUFFALOBUR","flower":"Large bright yellow flower with ONE long curved anther","berries":"Hidden inside spiny enlarging calyx","calyx":"Very spiny enclosing calyx","pedicels":"Heavily prickly growth","quick_rule":"Yellow corolla plus spiny fruit enclosure."}
          ],
          "not_reliable_alone":[
            "WHITE flowers alone: shared across morelloids.",
            "One green immature fruit: not diagnostic.",
            "Black berry alone: both species and more have dark berries.",
            "Size of anther without measurement: use scale and compare same angle.",
            "Fruit from photographs taken in different lighting can look glossy or dull differently."
          ]},
       "images":records,
       "visual_comparison":{
          "instance_id":"solanum-nigrescens-20261020-field-id",
          "title":"Divine nightshade: LONGER yellow anthers; mature fruit calyx usually pressed CLOSE",
          "subtitle":"All included main photographs show plant, flowers or buds; ripe fruit calyx photographs remain a HIGH-PRIORITY gap.",
          "memory_rule":"Flower anthers longer than American black nightshade. Verify later with mature berry/calyx: appressed instead of strongly bent back.",
          "items":panels+[
           {"label":"LOOK-ALIKE · AMERICAN BLACK NIGHTSHADE ripe fruit","scientific_name":"Solanum americanum",
            "image_url":"https://upload.wikimedia.org/wikipedia/commons/5/55/Solanum_americanum_fruit6_%2815119198229%29.jpg?utm_campaign=index&utm_content=original&utm_source=commons.wikimedia.org",
            "image_fit":"contain","image_role":"Different species: shiny black berry with reflexed calyx",
            "caption":"THIS IS AMERICAN BLACK NIGHTSHADE — NOT DIVINE NIGHTSHADE. The little green sepals are strongly folded BACK under ripe glossy fruit. Contrast with S. nigrescens, whose calyx generally hugs/spreads at the berry base.",
            "why_it_matters":"Contrast the precise target of a mature-fruit calyx photo; this is a comparison species, never presented as divine nightshade.",
            "creator":"Harry Rose","license":"CC BY 2.0","license_url":"https://creativecommons.org/licenses/by/2.0/",
            "source_page":"https://commons.wikimedia.org/wiki/File:Solanum_americanum_fruit6_(15119198229).jpg",
            "markers":[{"label":"American: calyx curls BACK", "label_x":67,"label_y":87,"target_x":62,"target_y":70}]}
          ],
          "overlay_note":"Arrows are non-destructive original photo overlays. On source images from Florida, photographed anatomy is visually reviewed. They do NOT prove a Texas occurrence or anther measurement. Final mobile arrow validation pending."
       },
       "field_photo_quickcheck":{
          "recognition":"Green unarmed ovate leaves, small white flowers, conspicuous yellow anthers; take mature berry/calyx photos to confirm the look-alike split.",
          "what_to_photograph":["Whole plant with leaves", "Flower macro with millimeter ruler to measure anthers","Fruiting cluster at full ripeness","Single fully ripe fruit side view with calyx lobes visible","Pedicel attachment after berries detach"],
          "missing":["Exact-species visibly ripe fruit and appressed calyx close-up; NO ripe S. nigrescens fruit photographs in current gallery","Measured anther scale; photograph lacks ruler","Hays provenance; existing photos were taken in Florida","Review iPhone arrows before final visual PASS"]
       },
       "curation_status":{
         "version":"1.0-manual-20261020-provisional",
         "taxonomy_reviewed":True,
         "range_reviewed":False,
         "morphology_reviewed":True,
         "lookalikes_reviewed":True,
         "user_approved":True,
         "provisional":True,
         "photo_metadata_count":len(records),
         "photo_files_present":len(records),
         "field_id_finish_status":"PASS_IN_PROGRESS",
         "last_field_id_reviewed":"2026-10-20"
       },
       "learner_visual_status":{
          "status":"provisional_learner_ready",
          "mode":"manual_one_species_field_pass",
          "image_count":len(records),
          "note":"Physically downloaded and verified individually CC-licensed exact-species photographs. Flower/lobes/buds identified; ripe fruit comparison still MISSING; no false fruit photo."
       },
       "photo_note":"Main photos 2021 Florida iNaturalist observation 103616257 by Alex Abair, CC BY 4.0 via Wikimedia Commons. Source JPEGs were compressed and EXIF/GPS stripped; education overlays separate. Mature fruit not photographed.",
       "field_id_reference_sources":[
          "https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:239356-2",
          "https://www.efloras.org/florataxon.aspx?flora_id=1&taxon_id=250044964",
          "https://pmc.ncbi.nlm.nih.gov/articles/PMC6554266/",
          "https://www.mdpi.com/2223-7747/12/8/1645"
       ]
    }
    ROOT.mkdir(parents=True,exist_ok=True)
    save(ROOT/"species.json",j)
    (ROOT/"SOURCES.txt").write_text(
      "Accepted concept: Solanum nigrescens M.Martens & Galeotti (POWO)\n"+
      "Morphology: Flora of North America & Knapp et al 2019 Morelloid revision\n"+
      "Photography (same Florida observation): "+SOURCE_OBSERVATION+"\n"+
      "Rights: CC BY 4.0 Alex Abair, four independent photo pages Wikimedia Commons\n"+
      "No current photo illustrates verified ripe S. nigrescens berries/calyx. Do not infer fruit from these photos.\n"+
      "Additional scientific ripe fruit figures: https://www.mdpi.com/2223-7747/12/8/1645 (Figure 3). Requires separate image-integrity review before installation.\n",encoding="utf-8")
    with (ROOT/"image-sources.csv").open("w",newline="",encoding="utf-8") as fp:
       cols=["file","role","creator","license","license_url","source_page","media_source_url","source_observation","sha256"]
       writer=csv.DictWriter(fp,fieldnames=cols);writer.writeheader()
       for a in records:writer.writerow({k:a.get(k,"") for k in cols})
    m["species"].append({"id":"solanum-nigrescens","path":str(ROOT/"species.json")})
    m["species"].sort(key=lambda x:x.get("id",""))
    save(MANIFEST,m)
    scope=g.setdefault("project_scope",{})
    ids=scope.setdefault("species_ids",[])
    if "solanum-nigrescens" not in ids:ids.append("solanum-nigrescens");ids.sort()
    scope["species_count"]=len(ids)
    scope["admission"]="Existing species preserved; S. nigrescens added 2026-10-20 by explicit owner approval as provisional comparative field learner, county range remains on hold."
    save(GENUS,g)
    audit={"date":"2026-10-20","species_id":"solanum-nigrescens","installed":len(records),"photo_license":"Alex Abair CC BY 4.0","files":[{"file":a["file"],"sha256":a["sha256"],"source":a["source_page"]} for a in records],"missing_image_roles":["Ripe berries","Fully ripe fruit calyx closeup with scale"],"download_holds":errors,"manifest_count":len(m["species"]),"status":"PASS_IN_PROGRESS"}
    save(Path("reports/solanum-nigrescens-firstcard-install-20261020.json"),audit)
    print("VERIFIED",len(records),"physically installed exact licensed photos; manifest",len(m["species"]),"; fruit photos HOLD")

if __name__=="__main__":main()
