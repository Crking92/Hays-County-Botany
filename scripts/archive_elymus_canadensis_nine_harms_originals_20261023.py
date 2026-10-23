#!/usr/bin/env python3
"""Physically archive nine genuine, separately source-determined, copyrighted
but author-permitted educational Elymus canadensis original photos.

Preserves old 2 Matt Lavin source files and all taxon/county/arrow data.
The source gallery already contains 9 external-only Harms records/panels;
replace EXTERNAL ONLY with local real JPEG file references only after hashes,
sanitization and EXACT species/rights verification.
"""
import hashlib,io,json,time
from pathlib import Path
import requests
from PIL import Image,ImageOps

BASE=Path("content/taxa/Poaceae/Elymus")
SP=BASE/"elymus-canadensis/species.json"
GP=BASE/"genus.json"
REPORT=Path("reports/elymus-canadensis-nine-harms-real-anatomy-20261023.json")
RELEASE=Path("workflow/field-id-publication/2026-10-23-elymus-canadensis-nine-real-harms-photos.json")
URL="https://w3.biosci.utexas.edu/prc/Monocots/GrassHTML/data/"
AUTHOR_HOME="https://w3.biosci.utexas.edu/prc/Monocots/"
PERMIT="BOB_HARMS_SELECTED_MONOCOTS_EDU_WITH_CREDIT_20261022"
LICE="© Bob Harms — scientific/educational use with attribution (NOT Creative Commons)"
CODES=[
"ELCA4-b","ELCA4-I","ELCA4-i1","ELCA4-J1","ELCA4-J",
"ELCA4-J3","ELCA4-S","ELCA4-d","ELCA4-L"
]
sp=json.loads(SP.read_text(encoding="utf-8"))
gen=json.loads(GP.read_text(encoding="utf-8"))
assert sp["id"]=="elymus-canadensis" and sp["scientific_name"]=="Elymus canadensis"
assert len(sp["images"])==11 and len(sp["visual_comparison"]["items"])==13
assert len(gen["visual_comparison"]["items"])==19
assert sp["curation_status"]["photo_files_present"]==2
assert "FIELD_READY_PHOTO_GAPS" in sp["field_id_finish_pass"]["stage"]
old_science={k:sp.get(k) for k in ["project_inclusion","county_occurrences_target_zone","target_zone_count","native_target_zone_calculated","morphology_keys","comparisons"]}
sess=requests.Session()
sess.headers.update({"User-Agent":"HaysBotany-Credited-Elymus-Canada-Source-Photo-Archive/1.0",
                     "Accept":"image/jpeg,image/*;q=0.9"})
save_dir=SP.parent/"images"; save_dir.mkdir(parents=True,exist_ok=True)
report={"species":"Elymus canadensis","original_collection":AUTHOR_HOME,
 "copyright":"Nine individually exact-source Bob Harms Selected Central Texas Monocots ORIGINAL photographic frames; author grants scientific/educational use with attribution, NOT Creative Commons",
 "preexisting_local_photos":2,"archived_new_photo_files":0,"photos":[],"unresolved":"Mature same-voucher Hays glume comparison to Virginia, opening of exact membrane at collar, 1mm full dissection, rooted entire local voucher"}
for ident in CODES:
    source=URL+"images/"+ident+".jpg"
    page=URL+"pages/"+ident+".html"
    fn="bob-harms-canada-wildrye-"+ident.lower()+".jpg"
    local=save_dir/fn
    if local.exists():raise RuntimeError("Refuse overwrite: "+str(local))
    ms=[m for m in sp["images"] if m.get("source_page")==page and m.get("file")==source]
    assert len(ms)==1,("existing external original metadata",ident,len(ms))
    orig=ms[0]
    assert orig["creator"]=="Bob Harms" and orig["source_photo_id"]==ident
    existing_rights=orig["license"]
    for collection in [sp["visual_comparison"]["items"],gen["visual_comparison"]["items"]]:
        panels=[p for p in collection if p.get("source_page")==page and p.get("image_url")==source and p.get("scientific_name")=="Elymus canadensis"]
        assert len(panels)==1,("existing panel",ident,len(panels))
        assert not panels[0].get("markers"),("Cannot replace earlier unreviewed micro arrows",ident)
    last=None
    for attempt in range(3):
        try:
            response=sess.get(source,timeout=38)
            response.raise_for_status()
            original_bytes=response.content
            if not original_bytes.startswith(bytes.fromhex("ffd8ff")) or len(original_bytes)<5000:
                raise ValueError("Original source JPEG not confirmed")
            with Image.open(io.BytesIO(original_bytes)) as x:
                x.load()
                if x.format!="JPEG" or min(x.size)<35:raise ValueError("Wrong anatomical image")
                clean=ImageOps.exif_transpose(x).convert("RGB")
                dims=list(clean.size)
            clean.save(local,"JPEG",quality=93,optimize=True)
            source_hash=hashlib.sha256(original_bytes).hexdigest()
            break
        except (requests.RequestException,OSError,ValueError) as err:
            last=str(err)
            if attempt<2: time.sleep((attempt+1)*4)
    else:raise RuntimeError("Original "+ident+" unavailable; no partial commits: "+last)
    data=local.read_bytes()
    with Image.open(local) as x:
        assert x.format=="JPEG" and x.mode=="RGB" and not x.getexif().get(34853) and list(x.size)==dims
        x.verify()
    digest=hashlib.sha256(data).hexdigest()
    orig["file"]="images/"+fn
    orig["creator"]="Bob Harms"
    orig["license"]=LICE
    orig["license_url"]=AUTHOR_HOME
    orig["site_specific_public_permission"]=PERMIT
    orig["source_image"]=source
    orig["source_taxon_name"]="Elymus canadensis"
    orig["original_source_license_statement"]=existing_rights
    orig["image_dimensions"]=dims
    orig["original_source_sha256"]=source_hash
    orig["archive_sha256"]=digest
    orig["public_reuse"]="YES, Bob Harms's original copyrighted Selected Central Texas Monocots educational scientific use with credit ONLY; NOT CC"
    orig["modifications"]="Original photographic pixels retained without crop at source dimensions; clean RGB JPEG re-encode removes all EXIF and GPS."
    orig["asset_status"]="PHYSICALLY_STORED_EXACT_SOURCE_JPEG; original-pixel arrow audit pending; user public review provisional"
    for collection in [sp["visual_comparison"]["items"],gen["visual_comparison"]["items"]]:
        panel=next(p for p in collection if p.get("source_page")==page and p.get("image_url")==source and p.get("scientific_name")=="Elymus canadensis")
        panel["image_url"]=str(local)
        panel["creator"]="Bob Harms"
        panel["license"]=LICE
        panel["license_url"]=AUTHOR_HOME
        panel["photo_status"]="Source-verified EXACT Canada wildrye Bob Harms original physically archived with credited educational permission, GPS/EXIF removed; user provisional review, no unproved submillimeter arrow claims."
    report["photos"].append({"ident":ident,"original_url":source,"source_page":page,"local_file":str(local),
       "dimensions":dims,"bytes":len(data),"source_sha256":source_hash,"archive_sha256":digest})
    report["archived_new_photo_files"]+=1

assert report["archived_new_photo_files"]==9 and len(sp["images"])==11
assert len(sp["visual_comparison"]["items"])==13 and len(gen["visual_comparison"]["items"])==19
assert all(sp.get(k)==v for k,v in old_science.items()),"County/taxonomy/compare data changed unexpectedly"
sp["curation_status"]["photo_metadata_count"]=11
sp["curation_status"]["photo_files_present"]=11
sp["curation_status"]["elymus_canada_harms_nine_physical_20261023"]={
 "real_source_jpegs_new":9,"physically_stored_species_jpegs":11,
 "species_comparison_panels":13,"genus_comparison_panels":19,
 "source_licensed":"Author's copyrighted source-specific credited educational/scientific use, NOT CC",
 "identification_hold":"1mm attached mature paired-node, glume-base and true ligule from a vouchered Hays plant",
 "stage":"FIELD_READY_PHOTO_GAPS"
}
sp["field_id_finish_pass"]["harms_nine_physically_archived_20261023"]={
 "photo_ids":CODES,"source_report":str(REPORT),
 "confirmed_roles":["upper flowering culm","flowering spike","mature spike with original metric marks",
 "attached spikelet pairs","pollen-bearing anthers","whole detached spikelet","disarticulated floret parts","true collar and auricles"],
 "exact_completion_holds":[
  "Locally verified rooted whole mature plant-to-spike sequence from one Hays voucher",
  "Two same-voucher attached rachis nodes with measured Canada narrow straighter glume bases alongside Virginia U-bowed glumes",
  "One opened free membranous ligule margin distinct from surrounding auricles with original mm scale",
  "Single locally authenticated mature paired multi-flowered spikelet detached and dissected at 1-mm scale"
 ],
 "note":"Nine author-determined real originals represent regional photo references, not one accession. Sources retain original metric markings without unverified 1mm organ lengths. Field-ready does not mean specimen-level 100%.",
 "status":"FIELD_READY_PHOTO_GAPS"
}
sp["visual_comparison"]["subtitle"]="11 real source-specific locally stored Canada wildrye JPEGs, including 9 credited copyrighted Bob Harms Central Texas macro originals + 2 Matt Lavin Commons images. 13 species teaching panels, including actual paired nodes/anthers/collar and Virginia glume-base comparison. Exact same-voucher mm anatomy still needed."
gen["visual_comparison"]["subtitle"]="Canada 9 Bob Harms source-original closeups now physically archived alongside five Virginia wildrye source originals and Canada vs Virginia structural comparison. Incomplete mm-level glume bases and local taxon vouchers remain flagged."
SP.write_text(json.dumps(sp,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
GP.write_text(json.dumps(gen,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
REPORT.parent.mkdir(parents=True,exist_ok=True)
REPORT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
RELEASE.parent.mkdir(parents=True,exist_ok=True)
RELEASE.write_text(json.dumps({
 "type":"manual_field_id_publication","date":"2026-10-23","species":"Elymus canadensis",
 "report":str(REPORT),"new_real_source_jpegs":9,"total_local_species_jpegs":11,
 "species_teaching_panels":13,"genus_teaching_panels":19,
 "rights":"Bob Harms exact copyrighted educational and scientific reuse with original creator credit (NOT CC)",
 "stage":"FIELD_READY_PHOTO_GAPS","release":"Check rights-filtered site build+deploy SUCCESS separately"
},indent=2)+"\n",encoding="utf-8")
print("PASS 9 real Bob Harms source-matched Canada wildrye photographs; 11 local originals; 13 species panels; 19 genus panels",flush=True)
