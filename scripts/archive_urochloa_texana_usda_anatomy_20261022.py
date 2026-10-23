#!/usr/bin/env python3
"""Archive two genuinely photographed Urochloa texana microscopy-style
USDA APHIS FNWD images; default-author Julia Scher (USDA), US govt public domain.
Source status: the FNWD individual U.texana photographs appear without alternate
third-party credit and are not among its excluded third-party specimens.
Do NOT confuse these with other species U.panicoides on the same page.
Fail closed: both real JPEG originals must decode before writing a single file.
"""
import csv,hashlib,io,json,time
from pathlib import Path
import requests
from PIL import Image,ImageOps

BASE=Path("content/taxa/Poaceae/Urochloa")
SPEC=BASE/"urochloa-texana/species.json"
GEN=BASE/"genus.json"
CSV=SPEC.parent/"image-sources.csv"
REPORT=Path("reports/urochloa-texana-usda-real-spikelet-floret-20261022.json")
MARK=Path("workflow/field-id-publication/2026-10-22-urochloa-texana-usda-true-spikelets.json")
PAGE="https://idtools.org/fnwd/index.cfm?entityID=2703&packageID=1097"
RIGHTS="https://idtools.org/fnwd/index.cfm?pageID=1328"
AUTHOR="Julia L. Scher, USDA APHIS ITP (default credit for FNWD photographs without named alternate author)"
LICENSE="Public Domain (U.S. federal government work)"
PHOTOS=[
  ("02","Urochloa_texana_02_fl.jpg",(322,332),"usda-urochloa-texana-ventral-dorsal-spikelets.jpg",
   "6 · TRUE SPIKELETS: ventral lower glume vs dorsal upper glume, 1 mm scale",
   "An ORIGINAL USDA image of two real Urochloa TEXANA spikelets, ventral face on LEFT with lower glume and lower sterile lemma, dorsal face on RIGHT with upper glume; actual millimeter ticks shown at far left. Do not confuse the second half-visible bract with a whole second floret. No Hays County collection provenance claimed.",
   "Two faces of SAME SPECIES provide crucial glume arrangement absent from unscaled head photos. Use 1-mm ticks to study approximate size; detailed lower-glume vein counts still require a higher-res separate original.",
   [{"label":"Ventral side: lower glume","label_x":1,"label_y":9,"target_x":32,"target_y":51},
    {"label":"Dorsal side: upper glume","label_x":66,"label_y":9,"target_x":74,"target_y":49}]),
  ("01","Urochloa_texana_01_fl.jpg",(500,302),"usda-urochloa-texana-fertile-florets-caryopses.jpg",
   "7 · ACTUAL FLORETS and CARYOPSES — A/B florets, C/D grains, mm ruler",
   "USDA original Urochloa TEXANA A/B true mature florets dorsal and ventral side; C/D detached caryopses ventral and dorsal. A correctly oriented real millimeter scale runs beneath these units. The reddish/hardened floret is not a second species; pale grain C/D is the caryopsis after removing its envelopes. There is no demonstrated true leaf ligule in this image.",
   "Separates hard fertile lemma/palea from caryopsis and outer glumes. Do NOT teach that the two grains are multiple florets in the same intact spikelet.",
   [{"label":"A: floret dorsal","label_x":1,"label_y":9,"target_x":16,"target_y":48},
    {"label":"B: floret ventral","label_x":34,"label_y":8,"target_x":42,"target_y":48},
    {"label":"C: grain ventral","label_x":51,"label_y":88,"target_x":65,"target_y":48},
    {"label":"D: grain dorsal","label_x":78,"label_y":89,"target_x":86,"target_y":48}])
]

def save(p,val):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(val,indent=2,ensure_ascii=False)+"\n",encoding="utf8")

def retrieve(session,url,expected):
    errors=[]
    for trial in range(2):
        try:
            r=session.get(url,timeout=28,headers={"Accept":"image/jpeg,image/*"})
            r.raise_for_status()
            raw=r.content
            if not 9000<len(raw)<3000000 or not raw[:3]==b"\xff\xd8\xff":
                raise ValueError("Source URL not real expected JPEG bytes")
            with Image.open(io.BytesIO(raw)) as im:
                im.load()
                if im.format!="JPEG" or im.size!=expected:
                    raise ValueError("Unexpected source named specimen dimensions: "+str(im.size))
                source_dims=list(im.size)
                converted=ImageOps.exif_transpose(im).convert("RGB")
            temp=io.BytesIO()
            converted.save(temp,format="JPEG",quality=94,optimize=True)
            dst=temp.getvalue()
            with Image.open(io.BytesIO(dst)) as verify:
                assert verify.format=="JPEG" and list(verify.size)==source_dims and not verify.getexif().get(34853)
                verify.verify()
            return raw,dst,r.url,source_dims
        except Exception as e:
            errors.append(type(e).__name__+": "+str(e)[:125])
            if getattr(getattr(e,"response",None),"status_code",None)==429:
                break # respect source throttle
            time.sleep(2)
    raise RuntimeError("Unable to verify actual USDA Urochloa texana source "+url+": "+str(errors))

def main():
    s=json.loads(SPEC.read_text(encoding="utf8"))
    g=json.loads(GEN.read_text(encoding="utf8"))
    assert s["id"]=="urochloa-texana" and g["name"]=="Urochloa"
    assert len(s["images"])==2 and len(s["visual_comparison"]["items"])==5 and len(g["visual_comparison"]["items"])==5
    assert g["project_scope"]["species_count"]==3
    source_sci={k:json.dumps(s.get(k),sort_keys=True) for k in
                ("project_inclusion","county_occurrences_target_zone","native_target_zone_calculated",
                 "target_zone_count","synonyms","taxonomic_note","taxonomy_source")}
    genus_scope=json.dumps(g["project_scope"],sort_keys=True)
    with CSV.open(newline="",encoding="utf8") as f:
        reader=csv.DictReader(f);cols=list(reader.fieldnames or []);rows=list(reader)
    assert "file_name" in cols and "source_page" in cols
    for _,fn,_,dest,_,_,_,_ in PHOTOS:
        if (SPEC.parent/"images"/dest).exists() or any(x.get("file_name")==dest for x in rows):
            raise RuntimeError("Previously installed or partially installed. Reconcile, don't overwrite "+dest)
    session=requests.Session()
    session.headers["User-Agent"]="HaysCountyBotanyScientificPhotoArchive/1.0 (github.com/Crking92/Hays-County-Botany)"
    staged=[]
    for ident,fn,expected,dest,label,caption,why,markers in PHOTOS:
        url="https://idtools.org/tools/1031/images/"+fn
        raw,new,actual,actual_dims=retrieve(session,url,expected)
        staged.append((ident,fn,dest,label,caption,why,markers,raw,new,url,actual,actual_dims))
        print("Verified USDA real "+fn+" "+str(actual_dims)+" "+str(len(raw)),flush=True)
    assert len(staged)==2
    found=[]
    for ident,fn,dest,label,caption,why,markers,raw,new,url,actual,expected in staged:
        file=SPEC.parent/"images"/dest
        file.parent.mkdir(parents=True,exist_ok=True)
        file.write_bytes(new)
        entry={
          "file":"images/"+dest,"role":label,"creator":AUTHOR,
          "license":LICENSE,"license_url":RIGHTS,"source_page":PAGE,
          "source_image":url,
          "source_taxon_name":"Urochloa texana",
          "rights_classification":"Individual USDA-produced default-author photo; FNWD says most U.S. government content is PD and exceptions individually credited. These two comparisons have no named third-party photo author.",
          "source_attribution":"Scher, Walters & Redford. 2015. Federal Noxious Weed Disseminules of the U.S., Edition 2.2. USDA APHIS PPQ ITP and CDFA; photo by Julia Scher, credit courtesy USDA.",
          "public_reuse":"Public domain U.S. federal work; keep source citation and individual default photographer credit.",
          "original_image_sha256":hashlib.sha256(raw).hexdigest(),
          "archived_image_sha256":hashlib.sha256(new).hexdigest(),
          "source_pixel_dimensions":list(expected),
          "archive_pixel_dimensions":list(expected),
          "downloaded_from":actual,
          "image_status":"PHYSICAL_REAL_FEDERAL_PD_DIAGNOSTIC_SOURCE_VERIFY_USER_REVIEW",
          "photo_review":"Authentic microscopic/seed-lab U. texana structure and real printed mm ticks. NOT a local Hays voucher. Existing photographed glumes and mature florets distinguished. Author/source rights checked 2026-10-22.",
          "modifications":"Converted source to RGB JPEG, stripped EXIF/GPS; source anatomical content and original photographed scale retained. Added only HTML arrows."}
        s["images"].append(entry)
        panel={
          "label":label,"scientific_name":"Urochloa texana",
          "image_url":str(file),"image_fit":"contain","image_role":label,
          "caption":caption,"why_it_matters":why,"creator":AUTHOR,"license":LICENSE,
          "license_url":RIGHTS,"source_page":PAGE,
          "source_image":url,
          "source_attribution":entry["source_attribution"],
          "markers":markers,
          "photo_status":"Actual U. texana USDA APHIS seed-lab photographic anatomy with real millimeter scale and source image credit; archived as public-domain default-US-government-author image. Visible group arrows only, no invented ligule or specimen provenance. PROVISIONAL USER PHOTO REVIEW."}
        s["visual_comparison"]["items"].append(panel)
        g["visual_comparison"]["items"].append(dict(panel))
        vals={"file_name":dest,"role":label,"creator":AUTHOR,"license":LICENSE,
              "source_page":PAGE,"direct_url":url,"study_use":"Public educational visual learner",
              "public_reuse":"U.S. Government-produced photo — public domain with requested citation",
              "observation_id":"","photo_id":fn}
        rows.append({key:vals.get(key,"") for key in cols})
        found.append({"file":str(file),"source_image":url,"source_page":PAGE,
                      "original_sha256":entry["original_image_sha256"],
                      "archive_sha256":entry["archived_image_sha256"],
                      "dimensions":list(expected),"author":AUTHOR,"license":LICENSE})
    assert all(json.dumps(s.get(k),sort_keys=True)==v for k,v in source_sci.items())
    assert json.dumps(g["project_scope"],sort_keys=True)==genus_scope
    assert len(s["visual_comparison"]["items"])==7 and len(g["visual_comparison"]["items"])==7
    s["curation_status"]["photo_files_present"]=4
    s["curation_status"]["photo_metadata_count"]=4
    s["curation_status"]["usda_texas_seed_lab_anatomy_20261022"]="Two real USDA APHIS PD exact-species spikelet/glume and floret/caryopsis JPEGs physically archived with mm scale and Julia Scher credit; isolated true 1mm ligule and same local rooted specimen remain PHOTO GAPS."
    s["visual_comparison"]["subtitle"]+=" Two additional physical USDA public-domain U. texana photographs teach REAL lower/upper glume orientation and separate floret/fruit unit structure with printed millimeter scales."
    s["visual_comparison"]["overlay_note"]+=" USDA original anatomical panels with 2+4 coarse visible source-supported arrows, new real JPEG files. No fabricated vein counts or same-plant Hays voucher photo. Additions are author-credited public-domain US federal photographs."
    s["field_id_finish_pass"]["usda_microscopy_progress_20261022"]={
      "archived_real_source_jpegs":2,"new_spikelet_panels":1,"new_floret_caryopsis_panels":1,
      "verified_scale_present":True,"missing_ligule_from_same_species_source":True,
      "whole_rooted_reference_rights":"USF 192277 specimen shows actual true roots/seedhead but reuse rights NOT cleared; research link only",
      "clemson_ligule_source_rights":"Clemson Texas Panicum page includes actual described ligule with hair fringe; copyright © Clemson, no user-public-reuse grant found; source page research link only",
      "strict_remaining_final_roles":["Same Hays-vouchered rooted mature whole plant from same ID/photo series",
             "Real ciliate membranous leaf ligule under mm-scale macro, cilia/membrane distinguished",
             "Higher-res same-specimen detached lower glume/lemma separated if crew needs vein count"],
      "photo_status":"FIELD_READY_PHOTO_GAPS",
      "taxonomy_and_range_protected":True
    }
    s["field_photo_quickcheck"]["heading"]="Texas signalgrass: adult branch → dorsal and ventral spikelet glumes → fertile floret/grain; true ligule remains";
    s["field_photo_quickcheck"]["steps"].append("10. Open USDA real PHOTO 6: TWO faces of the SAME U. texana spikelet. Left ventral lower glume/sterile lemma; right dorsal upper glume; actual original millimeter ticks visible. Remember these are alternate orientations, not two different grasses.")
    s["field_photo_quickcheck"]["steps"].append("11. Open USDA real PHOTO 7: panels A/B are hard fertile FLORETS from dorsal/ventral side, C/D are actual removed GRAINS (caryopses). Scale is printed. None shows a true leaf ligule.")
    s["field_photo_quickcheck"]["steps"].append("12. LIGULE source research-only: Clemson University U. texana page describes a genuine short membranous ciliate fringe, but its copyrighted image is NOT stored or reproduced. Collect a 1-mm lens photo from a Hays-vouchered plant before FINISHED.")
    s["field_photo_quickcheck"]["steps"].append("13. WHOLE ROOT research-only: University of South Florida herbarium USF 192277 shows a real identified pressed flowering plant and fibrous roots; photo reproduction permission not verified, so only a link is provided. Need same-voucher local rooted plant.")
    s["field_photo_quickcheck"]["evidence_sources"]=(s["field_photo_quickcheck"].get("evidence_sources") or [])+[PAGE,RIGHTS,
        "https://www.clemson.edu/cafls/research/weeds/weed-id-bio/grasses-parent/grasses-pages-annuals/texas-panicum.html",
        "https://florida.plantatlas.usf.edu/plant.aspx?id=1700"]
    s["field_id_references"]=list(dict.fromkeys((s.get("field_id_references") or [])+[PAGE,RIGHTS,
        "https://www.clemson.edu/cafls/research/weeds/weed-id-bio/grasses-parent/grasses-pages-annuals/texas-panicum.html",
        "https://florida.plantatlas.usf.edu/plant.aspx?id=1700"]))
    g["visual_comparison"]["subtitle"]+=" Two real U. texana USDA seed-lab images now SHOW comparative glume faces and separated fertile lemma/true grain with millimeter ticks; they are NOT pictures of U. fusca or U. reptans."
    g["curation_status"]["urochloa_texana_usda_anatomy_20261022"]={"new_original_USDA_PD_real_photos":2,"genus_photo_panels":7,
      "source_provenance":"USDA APHIS FNWD comparisons of U. texana, default Julia Scher photo, source attribution maintained",
      "remaining":"real ciliate ligule macro and same-vouchered local rooted adult plant, actual glume dissection evidence",
      "taxonomy_scope_preserved":True}
    with CSV.open("w",newline="",encoding="utf8") as fh:
        writer=csv.DictWriter(fh,fieldnames=cols,lineterminator="\n");writer.writeheader();writer.writerows(rows)
    save(SPEC,s);save(GEN,g)
    save(REPORT,{"result":"TWO_REAL_USDA_TEXAS_SIGNALGRASS_ANATOMY_JPEGS_ARCHIVED",
       "photo_count_added":2,"total_locally_stored":4,"species_gallery_panels":7,"genus_gallery_panels":7,
       "licensed_original":LICENSE,"photographer":AUTHOR,
       "federal_copyright_statement":RIGHTS,"images":found,
       "still_missing":["true photographed 1–1.8mm ciliate membranous leaf ligule from taxon-verified sample","local Hays voucher connected rooted adult with seedhead","if necessary higher-res detached measured lower glume / venation"],
       "research_only_sources_not_copied":["Clemson University true ligule photo, copyright unclear","USF Herbarium 192277 entire rooted plant, photo reproduction rights unclear"],
       "science_native_range_preserved":True})
    save(MARK,{"type":"manual_field_id_publication","date":"2026-10-22",
       "title":"Physical Urochloa texana USDA public domain measured spikelet and true floret/caryopsis photographs",
       "taxon":"Urochloa texana","report":str(REPORT),"new_real_JPEGs":2,
       "source_license":LICENSE,"credits":"Julia Scher USDA APHIS ITP; FNWD tool as requested",
       "stage":"FIELD_READY_PHOTO_GAPS","public_review":"provisional on species/genus public site, no preapproval",
       "unlicensed_ligule_or_herbarium_media":False,
       "native_and_taxonomic_records_unchanged":True})
    print("TWO REAL USDA UROCHLOA TEXANA PHOTOS VERIFIED AND ARCHIVED",flush=True)

if __name__=="__main__":
    main()
