#!/usr/bin/env python3
"""One-time strict image-license/source-guarded Festuca pair archive, Oct 22, 2026.
Two ORIGINAL Matt Lavin CC BY-SA 2.0 Vulpia octoflora photos and one historic
1906 US National Herbarium PUBLIC DOMAIN Festuca johnsoni illustration.
Names/rights/micro anatomy and native range remain untouched.
"""
import csv, hashlib, io, json, urllib.request
from pathlib import Path
from PIL import Image,ImageOps

BASE=Path("content/taxa/Poaceae/Festuca")
SP={k:BASE/f"festuca-{k}/species.json" for k in ("octoflora","versuta")}
GP=BASE/"genus.json"
REPORT=Path("reports/festuca-two-cards-physical-photo-archive-20261022.json")
MARK=Path("workflow/field-id-publication/2026-10-22-festuca-two-species-photo-archive.json")
JOBS=[
("octoflora","https://commons.wikimedia.org/wiki/File:Vulpia_octoflora_(6243564299).jpg",
 "https://upload.wikimedia.org/wikipedia/commons/0/03/Vulpia_octoflora_%286243564299%29.jpg",
 "matt-lavin-vulpia-whole-plant.jpg","Entire short flowering Vulpia octoflora plant attached to rocky-site base, source Utah","Matt Lavin","CC BY-SA 2.0"),
("octoflora","https://commons.wikimedia.org/wiki/File:Vulpia_octoflora_(6243569951).jpg",
 "https://upload.wikimedia.org/wikipedia/commons/e/ec/Vulpia_octoflora_%286243569951%29.jpg",
 "matt-lavin-vulpia-awns-spikelets.jpg","Close source-labelled crowded one-sided multi-floret awned spikelets, Grand Canyon Arizona","Matt Lavin","CC BY-SA 2.0"),
("versuta","https://commons.wikimedia.org/wiki/File:Contributions_from_the_U.S._National_Herbarium_(1906)_(20660168056).jpg",
 "https://upload.wikimedia.org/wikipedia/commons/6/62/Contributions_from_the_U.S._National_Herbarium_%281906%29_%2820660168056%29.jpg",
 "us-national-herbarium-1906-festuca-johnsoni-plate.jpg","HISTORICAL BOTANICAL ILLUSTRATION, not photograph; 1906 Festuca johnsoni Vasey synonym complex of F. versuta",
 "United States National Herbarium / Smithsonian Institution (1906)","Public domain — United States federal botanical plate (1906)")
]
def put(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
def main():
    s={k:json.loads(v.read_text(encoding="utf-8")) for k,v in SP.items()}
    g=json.loads(GP.read_text(encoding="utf-8"))
    assert s["octoflora"]["id"]=="festuca-octoflora" and s["versuta"]["id"]=="festuca-versuta"
    assert g["project_scope"]["species_count"]==2
    hold={k:{a:json.dumps(j.get(a),sort_keys=True) for a in ("project_inclusion","county_occurrences_target_zone","native_target_zone_calculated","target_zone_count","scientific_name")} for k,j in s.items()}
    genus_scope=json.dumps(g["project_scope"],sort_keys=True)
    planned=[];source_tables={}
    for k in s:
        with (BASE/f"festuca-{k}/image-sources.csv").open(newline="",encoding="utf-8") as f:
            rd=csv.DictReader(f)
            source_tables[k]=[rd.fieldnames,list(rd)]
    if any(not tab[0] or "file_name" not in tab[0] for tab in source_tables.values()):
        raise RuntimeError("Unexpected original CSV fields; HOLD")
    for k,source,remote,filename,role,author,license in JOBS:
        panels=[]
        for obj in (s[k],g):
            matches=[x for x in obj["visual_comparison"]["items"] if x.get("source_page")==source]
            if len(matches)!=1:raise RuntimeError("Expected one source-identified panel in BOTH species/genus for "+source)
            panel=matches[0]
            if panel["creator"]!=author or panel["license"]!=license:
                raise RuntimeError("Rights/name mismatch: "+source)
            if not panel.get("image_url","").startswith("https://"):
                raise RuntimeError("Candidate no longer external or already installed: "+filename)
            panels.append(panel)
        dest=BASE/f"festuca-{k}/images/{filename}"
        if dest.exists():raise RuntimeError("Destination already present: "+str(dest))
        if any(x.get("file")=="images/"+filename for x in s[k]["images"]):
            raise RuntimeError("Image already listed: "+filename)
        if any(row.get("file_name")==filename for row in source_tables[k][1]):
            raise RuntimeError("CSV already lists filename: "+filename)
        planned.append((k,source,remote,filename,role,author,license,dest,panels))
    downloaded=[]
    for k,src,remote,filename,role,author,lic,dest,panels in planned:
        req=urllib.request.Request(remote,headers={"User-Agent":"HaysCountyBotanyLicensedPublicEducationalArchive/1.0","Accept":"image/jpeg,image/*"})
        with urllib.request.urlopen(req,timeout=40) as res:
            original=res.read(7_000_000)
        if not 12000<len(original)<7_000_000:raise RuntimeError("Bad source size "+filename)
        with Image.open(io.BytesIO(original)) as im:
            im.load()
            if im.format!="JPEG" or min(im.size)<550:raise RuntimeError("Wrong image/dimensions "+filename)
            converted=ImageOps.exif_transpose(im).convert("RGB")
        buffer=io.BytesIO()
        converted.save(buffer,format="JPEG",quality=90,optimize=True)
        data=buffer.getvalue()
        with Image.open(io.BytesIO(data)) as check:
            assert check.format=="JPEG" and check.size==converted.size and not check.getexif().get(34853)
            check.verify()
        downloaded.append((k,src,remote,filename,role,author,lic,dest,panels,
                           hashlib.sha256(original).hexdigest(),hashlib.sha256(data).hexdigest(),data,list(converted.size)))
    # Verify all 3 downloaded and photo source guarantees BEFORE modifying canonical files.
    report=[]
    for k,src,remote,filename,role,author,lic,dest,panels,originalsha,newsha,data,dims in downloaded:
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(data)
        relative="images/"+filename
        s[k]["images"].append({"file":relative,"role":role,"creator":author,"license":lic,
           "license_url":"https://creativecommons.org/licenses/by-sa/2.0/" if k=="octoflora" else "https://creativecommons.org/publicdomain/mark/1.0/",
           "source_page":src,"direct_url":remote,"original_sha256":originalsha,"archived_sha256":newsha,
           "image_dimensions":dims,"source_country":"United States",
           "identity_caution":"Photographer determined Vulpia octoflora outside Texas" if k=="octoflora" else "1906 plate labeled Festuca johnsoni Vasey, historical synonym/concept of Festuca versuta; illustration not living field specimen",
           "modifications":"EXIF GPS stripped via pixel decoded/recoded JPEG; visual arrows remain separate overlays.",
           "public_reuse":"Yes, attribution+ShareAlike 2.0 conditions" if k=="octoflora" else "Yes, US historic federal public-domain plate"})
        for panel in panels:
            panel["image_url"]=str(dest)
            panel["photo_status"]="PHYSICALLY ARCHIVED real source file with verified public rights and original/archived SHA256; metadata/GPS removed. Real feature-level annotations only, no verified local voucher or micron-scale glume/ligule measurement. "+("Historical drawing, NOT modern photograph." if k=="versuta" else "Real out-of-state flora photograph. User public review pending.")
        columns,rows=source_tables[k]
        values={"file_name":filename,"role":role,"creator":author,"license":lic,"source_page":src,"direct_url":remote,
                "study_use":"Public noncommercial field education","public_reuse":"YES; attribution+SA conditions" if k=="octoflora" else "YES; US historical public domain",
                "observation_id":"historical-1906" if k=="versuta" else "Commons-Matt-Lavin","photo_id":filename}
        rows.append({field:values.get(field,"") for field in columns})
        report.append({"file":str(dest),"sha256":newsha,"source_sha256":originalsha,"source_page":src,"creator":author,"license":lic,"dims":dims})
    for k in s:
        if any(json.dumps(s[k].get(a),sort_keys=True)!=v for a,v in hold[k].items()):
            raise RuntimeError("Native taxon/science hold changed")
        cols,rows=source_tables[k]
        with (BASE/f"festuca-{k}/image-sources.csv").open("w",newline="",encoding="utf8") as f:
            wr=csv.DictWriter(f,fieldnames=cols,lineterminator="\n");wr.writeheader();wr.writerows(rows)
        s[k]["curation_status"]["source_cc_photo_archive_20261022"]="Canonical photograph(s)/historical drawing physicalized, exact source and artist rights; status still FIELD_READY_PHOTO_GAPS."
        put(SP[k],s[k])
    if genus_scope!=json.dumps(g["project_scope"],sort_keys=True):raise RuntimeError("Genus original admission changed")
    g["curation_status"]["source_cc_photo_archive_20261022"]={"archived_media":3,"canonical_species":2,"photo_panels":5,"microscopic_macro_still_missing":True}
    put(GP,g)
    put(REPORT,{"result":"ARCHIVED_2_SIXWEEKS_ACTUAL_PHOTOS_AND_1_TEXAS_HISTORIC_ILLUSTRATION",
        "files":report,"species_count":2,"genus_panels":5,"native_taxon_range_and_licenses_preserved":True,
        "remaining":["Texan Festuca versuta REAL field plant and intact panicle (historic plate isn't proof)",
                     "Matched 1mm ligule/glume/lemma photos for both grasses","Fresh rooted annual-vs-perennial base comparison"]})
    put(MARK,{"type":"manual_field_id_publication","requested_at":"2026-10-22",
        "title":"Festuca two-species licensing-safe archived photo comparison",
        "species_ids":["festuca-octoflora","festuca-versuta"],"physical_new_media":3,
        "source_photographs":2,"historical_illustrations":1,
        "scope":"existing canonical FINISH_ENRICH","native_range_unchanged":True,
        "stage":"FIELD_READY_PHOTO_GAPS"})
    print("PASS: two actual licensed Vulpia photos and one clearly historical Festuca synonym plate stored safely")
if __name__=="__main__":main()
