#!/usr/bin/env python3
"""Lane 2: archive true rooted/live Eragrostis lugens from photo-level CC BY 2.0 source."""
from pathlib import Path
from urllib.request import Request,urlopen
import io,hashlib,json
from PIL import Image,ImageOps

CARD=Path("content/taxa/Poaceae/Eragrostis/eragrostis-lugens/species.json")
PIC=CARD.parent/"images"/"harry-rose-lugens-live-rooted-tuft-plant10.jpg"
REPORT=Path("reports/lane2-eragrostis-lugens-rooted-habit-20261026.json")
SRC="https://commons.wikimedia.org/wiki/File:Eragrostis_lugens_plant10_(7324851218).jpg"
MEDIA="https://upload.wikimedia.org/wikipedia/commons/a/ac/Eragrostis_lugens_plant10_%287324851218%29.jpg"
LICENSE="https://creativecommons.org/licenses/by/2.0/"
def main():
    j=json.loads(CARD.read_text())
    assert j["id"]=="eragrostis-lugens"
    # Licensing reviewed on the exact Wikimedia Commons file page:
    # Harry Rose, CC BY 2.0, transferred from Flickr and license reviewed 2015-05-20.
    with urlopen(Request(MEDIA,headers={"User-Agent":"Hays-Botany-Learner/1.0 (public botany education; CC BY 2.0 with credit)"}),timeout=45) as f:
        assert f.url.startswith("https://upload.wikimedia.org/"),"Unexpected download origin"
        blob=f.read(8_000_001)
    assert 1_000_000<len(blob)<8_000_001,"Unexpected source photo size; hold"
    with Image.open(io.BytesIO(blob)) as x:
        assert x.format=="JPEG" and x.size==(4000,3000),"Source changed; hold for reinspection"
        y=ImageOps.exif_transpose(x).convert("RGB")
    y.thumbnail((2400,2400))
    buf=io.BytesIO()
    y.save(buf,format="JPEG",quality=88,optimize=True)
    cleaned=buf.getvalue()
    with Image.open(io.BytesIO(cleaned)) as chk:
        assert chk.format=="JPEG" and not chk.getexif(),"EXIF retained"
    PIC.parent.mkdir(parents=True,exist_ok=True)
    if PIC.exists():
        assert hashlib.sha256(PIC.read_bytes()).digest()==hashlib.sha256(cleaned).digest(),"Existing archive differs: do not overwrite"
    else:
        PIC.write_bytes(cleaned)
    expected=j["images"][0]
    assert expected.get("source_page")==SRC,"Expected external source changed; stop"
    old=expected["file"]
    assert old.startswith("https://"),"Already local: stop for review"
    expected["historical_remote_image_url"]=old
    expected["file"]="images/"+PIC.name
    expected["role"]="LIVE SOURCE-LABELLED TUFT: one actual flowering tussock with multiple flowering culms, central emerging leafy crown, AND exposed fibrous roots contiguous beneath the crown; not a ligule close-up"
    expected["creator"]="Harry Rose"
    expected["license"]="CC BY 2.0"
    expected["license_url"]=LICENSE
    expected["public_reuse"]="yes, CC BY 2.0 with creator credit and change notice"
    expected["source_page"]=SRC
    expected["source_identification"]="Photographer/source Eragrostis lugens, collected/photographed in Australia; NO Hays County identification/voucher inferred"
    expected["image_change_note"]="Downscaled original 4000x3000 JPEG to 2400 max edge, RGB, EXIF and GPS stripped, no crop; gallery arrows separate overlay"
    expected["photo_status"]="PHYSICALLY_ARCHIVED_PUBLIC_SAFE_20261026: source verified CC BY 2.0 photo showing flowering clump + clearly connected crown and fibrous roots"
    items=j["visual_comparison"]["items"]
    URL="content/taxa/Poaceae/Eragrostis/eragrostis-lugens/images/"+PIC.name
    if not any(x.get("image_url")==URL for x in items):
        items.insert(0,{
          "label":"LIVE ROOTED CLUMP · crown, fibrous roots and attached flowering stems",
          "scientific_name":"Eragrostis lugens",
          "image_url":URL,"image_fit":"contain",
          "image_role":"Harry Rose source-determined live tuft with attached rooted base, emerging tillers and wispy terminal flowering panicles (Australia)",
          "caption":"The SAME lifted tuft shows fibrous roots directly beneath the central leafy crown, many emerging leafy shoots, and several still-attached fine flowering panicles. All arrows identify structures visible at this scale. Don't infer the true inner ligule or exact rolled-blade cross section. Source photographed in Australia; species name follows original photographer, not a local voucher.",
          "why_it_matters":"First public gallery photograph here clearly showing the rooted BUNCHGRASS crown and flowering stems connected in one real plant; contrasts with the separate pressed Texas vouchers.",
          "creator":"Harry Rose","license":"CC BY 2.0","license_url":LICENSE,
          "source_page":SRC,
          "modifications":"RGB resized from 4000x3000 to 2400px max side; EXIF stripped; non-destructive SVG arrows in UI",
          "markers":[
            {"label":"Attached airy flowering panicles","label_x":4,"label_y":12,"target_x":34,"target_y":25},
            {"label":"Leafy crown and emerging tillers","label_x":73,"label_y":59,"target_x":48,"target_y":71},
            {"label":"Connected fibrous roots (not rhizomes)","label_x":2,"label_y":86,"target_x":47,"target_y":81}
          ],
          "photo_status":"Original Commons page and 4000x3000 pixels reviewed 2026-10-26, CC BY 2.0 verified individually; anatomical arrows gross-organ level only."
        })
    # Pre-existing Harry Rose plant2 photo was inaccurately identified as leaf-sheath macro.
    # Image shows the WHOLE rooted plant and multiple complete attached flowering panicles.
    leaf=next((a for a in items if "harry-rose-lugens-leaf-sheath.jpg" in a.get("image_url","")),None)
    assert leaf is not None,"Existing live whole-plant gallery entry missing; hold"
    leaf.update({
      "label":"SECOND LIVE CLUMP · whole flowering plant and basal crown",
      "image_role":"Actual full flowering tussock with many entire airy panicles, narrow leaf blades and compact leafy crown; NOT a close-up of the true collar or ligule",
      "caption":"Harry Rose's source-labelled CC BY 2.0 photograph shows an actual uprooted and living flowering tuft with complete attached delicate panicles, green narrow leaves and a crowded basal crown. Small dark roots are visible under the hand at the very bottom. The true 0.3–0.5 mm ligule cannot be diagnosed from this whole plant view.",
      "why_it_matters":"Whole attached seedheads are visible from crown to tip. Compare the fine airy branches with broad-leaved purple lovegrass; confirm the tiny true ligule separately.",
      "license_url":LICENSE,
      "photo_status":"Verified source photo and gross structure pixels; original is 3000x3000 2012 Harry Rose, CC BY 2.0. Existing locally archived copy preserved; 2 gross arrows, no microscopic claim.",
      "markers":[
       {"label":"Complete attached flowering panicles","label_x":4,"label_y":12,"target_x":42,"target_y":25},
       {"label":"Compact leafy crown (not ligule)","label_x":73,"label_y":80,"target_x":51,"target_y":85}
      ]
    })
    # Gallery indices after new first panel: 0 rooted, 4 complete flowering whole plant, 1 & 2 pressed.
    j["field_photo_quickcheck"]["featured_photo_indices"]=[0,4,2,1]
    j["field_photo_quickcheck"]["steps"]=[
      "START with the two Harry Rose LIVE tuft photographs: trace fibrous roots upward into ONE leafy crown and emerging tillers, then trace the flowering culms to their complete airy attached panicles. These are source-identified Australian plants, not Texas vouchers.",
      "At the leaf sheath mouth, keep long hairs DISTINCT from the true very short inner ligule (Harry Rose reports 0.3–0.5 mm, membranous below and hairy above). NO current whole-plant image proves the actual ligule; photograph one peeled-open collar with 1-mm bar.",
      "The pressed Texas voucher images show narrow leaf blades and separate reproductive branches, but flatten natural leaf rolling. Confirm an inrolled blade edge with a fresh cross-section before deciding between similar Eragrostis species.",
      "Record connected roots, young tillers, narrow blade, true ligule and complete attached seedhead from a single Hays-area specimen before strict field-ID completion. Retain existing mature spikelet seed evidence without calling it measured."
    ]
    j["field_photo_quickcheck"]["warning"]="New physically archived live flowering/rooted clump photo is CC BY 2.0 Harry Rose from AUSTRALIA, not a Hays voucher. A separate existing Harry Rose photograph also shows whole live flowering clump (it is NOT a ligule macro). Three visible-only roots/crown/panicle arrows on new frame plus two crown/panicle arrows on prior frame; no true ligule or involute-blade cross section proven. Existing two Texas pressed sheets and seed photos remain."
    j["field_id_finish_pass"]["photo_evidence_limits"]+=" 2026-10-26: LIVE crown, tillers, roots, and complete attached seedhead roles are now taught by licensed exact-source Australian photos. Local same-voucher field confirmation, peeled-open membranous/hairy true ligule, and fresh blade cross-section remain open."
    j["curation_status"]["photo_files_present"]=len([z for z in j["images"] if str(z.get("file","")).startswith("images/")])
    j["curation_status"]["photo_metadata_count"]=len(j["images"])
    j["curation_status"]["lane2_live_rooted_role_20261026"]="REAL ROOTED CROWN+TILLERS+ATTACHED PANICLES PHOTO; LICENSE CLEARED; MICROSCOPIC HOLDS"
    if isinstance(j.get("learner_visual_status"),dict):
        j["learner_visual_status"]["image_count"]=len(j["images"])
    j["photo_note"]=j.get("photo_note","")+"\n2026-10-26 Lane 2: physically archived verified CC BY 2.0 live Harry Rose plant10 image (root/crown/tillers/attached panicles); re-described existing plant2 as another complete attached flowering tuft rather than a ligule photo. All prior photo science retained; Hays voucher/collar/rolled blade remain gaps."
    CARD.write_text(json.dumps(j,ensure_ascii=False,indent=2)+"\n")
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps({
      "species":"Eragrostis lugens","source_photo":SRC,"creator":"Harry Rose","license":"CC BY 2.0","source_verified":"Wikimedia Commons source file+FlickreviewR original Flickr copyright 2015-05-20","image_path":str(PIC),"stored_clean_sha256":hashlib.sha256(cleaned).hexdigest(),"stored_clean_bytes":len(cleaned),"size":list(y.size),
      "local_image_files":j["curation_status"]["photo_files_present"],"gallery_species_panels":sum(a.get("scientific_name")=="Eragrostis lugens" for a in items),
      "new_photo":1,"gross_anatomy_arrows_added":5,"region_caution":"Photographed in Australia; must not assert Hays specimen", "site_status":"not yet verified","stage":"FIELD_READY_PHOTO_GAPS",
      "still_missing":["same-Hays-plant crown-to-panicle series", "peeled true membrane-plus-hair ligule with mm scale (not sheath-mouth hairs)", "live involute blade cross-section", "mature scaled spikelet as needed"]
    },indent=2)+"\n")
    print("ARCHIVE_SUCCESS",PIC,len(cleaned),y.size)
if __name__=="__main__": main()
