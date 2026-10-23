#!/usr/bin/env python3
"""Archive 4 actual regional Panicum obtusum (= Hopia obtusa) Bob Harms photos.
No assumed individual voucher or guessed 1mm anatomical arrow positions.
"""
import hashlib, io, json, time
from pathlib import Path
import requests
from PIL import Image, ImageOps

FOLDER=Path("content/taxa/Poaceae/Hopia")
SP=FOLDER/"hopia-obtusa/species.json"
GP=FOLDER/"genus.json"
REPORT=Path("reports/hopia-obtusa-four-harms-original-anatomy-20261022.json")
RELEASE=Path("workflow/field-id-publication/2026-10-22-hopia-obtusa-harms-four-physical.json")
BASE="https://w3.biosci.utexas.edu/prc/Monocots/GrassHTML/data/"
RIGHTS="https://w3.biosci.utexas.edu/prc/Monocots/"
PERMIT="BOB_HARMS_SELECTED_MONOCOTS_EDU_WITH_CREDIT_20261022"
LIC="© Bob Harms — scientific/educational use with attribution (NOT Creative Commons)"
ROWS=[
 ("PAOB-I","Actual flowering panicle branches and reproductive outline","FLOWERING — actual vine mesquite panicle","Full flowering branch with closely held flower-bearing units; do not presume basal rooting nodes are visible."),
 ("PAOB-J","Actual close-up flowering units and reproductive organs","FLOWERING CLOSE — real purpletop-like stigma structures in vine mesquite","This is the author's closer view of a source-determined vine mesquite reproductive head. Do not label single fertile/sterile structures until individual pixels are audited."),
 ("PAOB-C","Actual culm and sheath detail from accepted Hopia obtusa","CULM DETAIL — original vine mesquite stem and sheath","This photo documents a real culm/stem area under the older name Panicum obtusum. Do not call the photographed node an ACTUALLY ROOTED stolon node without seeing the roots."),
 ("PAOB-L","Actual blade–sheath ligule region, original source photo","COLLAR/LIGULE ZONE — original author ligule/sheath photo","The blade/sheath junction and ligule zone are presented under the source's label. Its 1–2mm true membrane cannot be pixel-measured unless physically calibrated in a fresh source-verified specimen.")
]
s=json.loads(SP.read_text(encoding="utf-8"));g=json.loads(GP.read_text(encoding="utf-8"))
assert s["id"]=="hopia-obtusa" and s["scientific_name"]=="Hopia obtusa"
assert s["project_inclusion"]["target_zone_status"]=="PASS"
assert len(s["images"])==5 and len(s["visual_comparison"]["items"])==4
assert len(g["visual_comparison"]["items"])==4
assert "FIELD_READY_PHOTO_GAPS" in s["field_id_finish_pass"]["stage"]
old_range=s.get("county_occurrences_target_zone")
SAVED=SP.parent/"images"; SAVED.mkdir(parents=True,exist_ok=True)
session=requests.Session();session.headers.update({"User-Agent":"HaysBotany-CreditedCentralTexasPhotoArchive/1.0","Accept":"image/jpeg,image/*;q=0.9"})
report={"species":"Hopia obtusa","source_name":"Panicum obtusum","source_collection":RIGHTS,
 "rights":"Only Bob Harms's Selected Central Texas Monocots exact four originals under educational/scientific use with original credit; NOT Creative Commons or blanket DigFlora license",
 "true_new_files":0,"photos":[],"original_native_range_unchanged":True,"no_specimen_level_match_claim":True}
for code, role, title, caption in ROWS:
    source=BASE+"images/"+code+".jpg"
    page=BASE+"pages/"+code+".html"
    out=SAVED/("bob-harms-vine-mesquite-"+code.lower()+".jpg")
    if not out.is_file():
        last=None
        for retry in range(3):
            try:
                response=session.get(source,timeout=35)
                response.raise_for_status()
                b=response.content
                if len(b)<5500 or not b.startswith(bytes.fromhex("ffd8ff")):
                    raise ValueError("not credible source original JPEG")
                with Image.open(io.BytesIO(b)) as image:
                    image.load()
                    if image.format!="JPEG" or min(image.size)<140: raise ValueError("small/wrong source")
                    if image.getexif().get(274,1)!=1: raise ValueError("requires orientation review")
                    pixels=ImageOps.exif_transpose(image).convert("RGB")
                pixels.save(out,format="JPEG",quality=93,optimize=True)
                original_hash=hashlib.sha256(b).hexdigest()
                report["true_new_files"]+=1
                break
            except (requests.RequestException,ValueError,OSError) as ex:
                last=str(ex)
                if retry<2:time.sleep(3+2*retry)
        else: raise RuntimeError(f"Source {code} not independently recovered: {last}")
    else:
        original_hash=None
    data=out.read_bytes()
    with Image.open(out) as decoded:
        if decoded.format!="JPEG" or decoded.mode!="RGB" or min(decoded.size)<140: raise ValueError("invalid cached source")
        if decoded.getexif().get(34853): raise ValueError("GPS metadata must be removed")
        dims=list(decoded.size);decoded.verify()
    sha=hashlib.sha256(data).hexdigest()
    record={"file":"images/"+out.name,"role":role,"creator":"Bob Harms",
       "license":LIC,"license_url":RIGHTS,"site_specific_public_permission":PERMIT,
       "source_page":page,"source_image":source,"source_taxon_name":"Panicum obtusum",
       "accepted_taxon_name":"Hopia obtusa",
       "public_reuse":"YES for these exact copyrighted scientific/educational Bob Harms originals with credit; NOT Creative Commons/general redistribution",
       "image_status":"PHYSICAL_SOURCE_SPECIFIC_HARMS_ORIGINAL_PROVISIONAL_ANNOTATION",
       "image_dimensions":dims,"archive_sha256":sha,"photo_review":"SOURCE ID VERIFIED as Panicum obtusum (= Hopia obtusa). Human original-pixel organ arrows not yet verified. User provisional public photo review.",
       "modifications":"Original decoded/re-encoded as RGB JPEG, GPS and EXIF stripped, no crop or source-relabeling"}
    s["images"].append(record)
    panel={
       "label":title+" · REAL CENTRAL TEXAS PHOTO",
       "scientific_name":"Hopia obtusa","image_url":str(out),"image_fit":"contain",
       "image_role":role,"caption":caption,
       "why_it_matters":"Regional source-specific photo; compare actual organ location to the crew ID key, without inventing microscopic structures or falsely connecting separate individual specimens.",
       "creator":"Bob Harms","license":LIC,"license_url":RIGHTS,"source_page":page,
       "photo_status":"Physically archived attributed copyrighted educational use. Source name Panicum obtusum accepted as Hopia obtusa. PROVISIONAL — USER PHOTO REVIEW PENDING.",
       "markers":[]
    }
    s["visual_comparison"]["items"].append(panel)
    g["visual_comparison"]["items"].append(dict(panel))
    report["photos"].append({"source_code":code,"source":source,"source_page":page,"local":str(out),"sha256":sha,
             "source_original_sha256":original_hash,"dimensions":dims,"bytes":len(data),"role":role})
assert len(report["photos"])==4 and len(s["images"])==9
assert len(s["visual_comparison"]["items"])==8 and len(g["visual_comparison"]["items"])==8
assert s.get("county_occurrences_target_zone")==old_range
s["curation_status"]["photo_metadata_count"]=9
s["curation_status"]["photo_files_present"]=6
s["curation_status"]["harms_4_central_texas_20261022"]={
 "physically_archived_originals":4,"species_panels":8,"genus_panels":8,
 "all_pub_reuse":"credited Bob Harms educational use, source- and identity-specific",
 "macro_pixel_annotation":"PENDING_PIXEL_REVIEW","status":"FIELD_READY_PHOTO_GAPS"}
s["field_id_finish_pass"]["four_real_central_texas_photos_20261022"]={
 "source":"Bob Harms Selected Central Texas Monocots (original source name Panicum obtusum)",
 "archived_originals":["PAOB-I","PAOB-J","PAOB-C","PAOB-L"],
 "report":str(REPORT),"total_local_photos":6,
 "existing_sources_unchanged":True,
 "important_safety":"The culm photo cannot prove a particular node roots; need actual source-vouchered attached roots before adding that arrow.",
 "true_final_photo_holds":[
   "Same locally source-vouchered individual: long vine-like stolon attached to leafy shoots, real swollen pubescent node and visible adventitious roots",
   "TRUE inner ligule free margin from leaf collar with 1-mm ruler, not mislabeled sheath hair",
   "Mature blunt oval attached spikelet, separate first/second glumes and sterile/fertile parts measured at 1mm",
   "Same-scale native Hopia versus invasive Cynodon: runners and real flowering heads",
 ],
 "stage":"FIELD_READY_PHOTO_GAPS"
}
s["look_here_first"]="FIRST trace the long aboveground vine-like stolon to a SWOLLEN, hairy node with actual roots and young shoot (if visible) on the same live plant. THEN verify the contracted narrow seedhead of rounded, blunt spikelets. The four new Harms source photographs show reproductive branches, stem and collar but NOT one verified connected root-to-seed voucher. Compare Cynodon terminal fingers; do not call a node 'rooted' from a merely hairy stem macro."
g["look_here_first"]="VINE MESQUITE Hopia obtusa: seek an actually connected stolon to hairy SWOLLEN ROOTING node; next its slender inflorescence of BLUNT oval spikelets. Older source name Panicum obtusum is the same accepted species, NOT generic Panicum."
SP.write_text(json.dumps(s,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
GP.write_text(json.dumps(g,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
REPORT.parent.mkdir(parents=True,exist_ok=True)
REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
RELEASE.parent.mkdir(parents=True,exist_ok=True)
RELEASE.write_text(json.dumps({"type":"manual_field_id_publication","date":"2026-10-22",
 "species":"Hopia obtusa","original_source_name":"Panicum obtusum",
 "archive":str(REPORT),"new_local_originals":4,"total_local_images":6,
 "total_species_panels":8,"total_genus_panels":8,
 "rights":"Bob Harms exact four Selected Monocots copyrighted original images educational reuse with credit, NOT CC",
 "stage":"FIELD_READY_PHOTO_GAPS","release_status":"NOT PROVEN LIVE UNTIL GITHUB PAGES RUN SUCCESSFUL"
},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("ARCHIVED FOUR real licensed and authenticated Central Texas vine mesquite source originals",flush=True)
