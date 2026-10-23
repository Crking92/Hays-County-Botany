#!/usr/bin/env python3
"""Physical exact-source archive for the eight already reviewed Harms
Sporobolus vaginiflorus educational/attribution photos, NOT CC.
Also count current canonical grass-card completion statuses without changing science.
Fail closed: verify all eight photos before mutating anything on disk.
"""
import csv,hashlib,io,json,time
from pathlib import Path
import requests
from PIL import Image,ImageOps

ROOT=Path(".")
BASE=ROOT/"content/taxa/Poaceae/Sporobolus"
SP=BASE/"sporobolus-vaginiflorus/species.json"
GN=BASE/"genus.json"
CSV=BASE/"sporobolus-vaginiflorus/image-sources.csv"
REPORT=ROOT/"reports/sporobolus-vaginiflorus-physical-harms-eight-20261022.json"
AUDIT=ROOT/"reports/grass-diagnostic-progress-live-20261022.json"
MARK=ROOT/"workflow/field-id-publication/2026-10-22-sporobolus-vaginiflorus-eight-archived-harms.json"
SOURCE="https://w3.biosci.utexas.edu/prc/Monocots/GrassHTML/data/"
LIC="© Bob Harms — scientific/educational use permitted with photographer credit ONLY (NOT Creative Commons)"
PERMIT="BOB_HARMS_SELECTED_MONOCOTS_EDU_WITH_CREDIT_20261022"
IDS=["SPVA-a3","SPVA-b1","SPVA-c","SPVA-i","SPVA-J1","SPVA-j2","SPVA-d","SPVA-L"]

def save(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

def jpeg(session,url):
    errors=[]
    for attempt in range(3):
        try:
            response=session.get(url,timeout=40,headers={"Accept":"image/jpeg,image/*"})
            response.raise_for_status()
            raw=response.content
            if not (8000 < len(raw) < 9000000) or not raw.startswith(b"\xff\xd8\xff"):
                raise RuntimeError("Not an expected original JPEG")
            with Image.open(io.BytesIO(raw)) as im:
                im.load()
                if im.format!="JPEG" or min(im.size)<75 or max(im.size)>8500 or im.size[0]*im.size[1]<15000:
                    raise RuntimeError("Unusable source JPEG format/dimensions: "+str(im.size))
                print("SOURCE PIXELS",url,im.size,flush=True)
                dimensions=list(im.size)
                clean=ImageOps.exif_transpose(im).convert("RGB")
            clean.thumbnail((2400,2400),Image.Resampling.LANCZOS)
            out=io.BytesIO()
            clean.save(out,"JPEG",quality=91,optimize=True)
            data=out.getvalue()
            if len(data)<7000: raise RuntimeError("Stored jpeg too small")
            with Image.open(io.BytesIO(data)) as chk:
                assert chk.format=="JPEG" and not chk.getexif().get(34853)
                chk.verify()
            return raw,data,dimensions,list(clean.size),response.url
        except Exception as exc:
            errors.append(f"{type(exc).__name__}: {str(exc)[:180]}")
            time.sleep(2+attempt*2)
    raise RuntimeError("No licensed bytes retrieved "+url+" "+repr(errors))

def audit():
    species=sorted((ROOT/"content/taxa/Poaceae").glob("*/*/species.json"))
    report={"species_cards":len(species),"genus_modules":len(list((ROOT/"content/taxa/Poaceae").glob("*/genus.json"))),
        "cards_explicit_photo_gap":0,"cards_explicit_verified_complete":0,
        "cards_without_clear_field_finish_status":0,
        "physical_media_entries_total":0,"cards_with_zero_local_media":0,
        "status_definition":"True final completion only if current canonical finish stage explicitly begins FINISHED or COMPLETE AND does not contain GAPS/HOLD. Otherwise do not infer 100% completion; gap flags and unclassified status shown separately.",
        "examples_unclassified":[]}
    for file in species:
        s=json.loads(file.read_text(encoding="utf8"))
        stage=str((s.get("field_id_finish_pass") or {}).get("stage") or "")
        vis=str((s.get("curation_status") or {}).get("visual_finish") or "")
        alt=str(s.get("visual_status") or "")
        summary=" | ".join((stage,vis,alt)).upper()
        if "FIELD_READY_PHOTO_GAPS" in summary or "NEEDS_REAL_PHOTOS" in summary:
            report["cards_explicit_photo_gap"]+=1
        elif (stage.upper().startswith(("FINISHED","COMPLETE","100_PERCENT")) and not any(t in summary for t in ("GAP","HOLD","PENDING","PROVISIONAL"))):
            report["cards_explicit_verified_complete"]+=1
        else:
            report["cards_without_clear_field_finish_status"]+=1
            if len(report["examples_unclassified"])<15:report["examples_unclassified"].append(s.get("id",file.parent.name))
        n=sum(1 for x in s.get("images",[]) if str(x.get("file","")).startswith("images/"))
        report["physical_media_entries_total"]+=n
        if n==0:report["cards_with_zero_local_media"]+=1
    assert report["species_cards"]==sum(report[k] for k in ("cards_explicit_photo_gap","cards_explicit_verified_complete","cards_without_clear_field_finish_status"))
    return report

def main():
    s=json.loads(SP.read_text(encoding="utf8"))
    g=json.loads(GN.read_text(encoding="utf8"))
    assert s["id"]=="sporobolus-vaginiflorus" and g["name"]=="Sporobolus"
    assert g["project_scope"]["canonical_species_count"]==3
    if len(s["images"])!=11 or len(s["visual_comparison"]["items"])!=12 or len(g["visual_comparison"]["items"])!=14:
        raise RuntimeError("Concurrent edits to target card: need refresh before using installer")
    protected={k:json.dumps(s.get(k),sort_keys=True) for k in ("project_inclusion",
              "county_occurrences_target_zone","native_target_zone_calculated","target_zone_count",
              "synonyms","taxonomic_note")}
    genus_scope=json.dumps(g["project_scope"],sort_keys=True)
    with CSV.open(newline="",encoding="utf8") as fh:
        reader=csv.DictReader(fh);columns=list(reader.fieldnames or []);rows=list(reader)
    if "file_name" not in columns:raise RuntimeError("Image source CSV missing filename column")
    todo=[]
    for ident in IDS:
        url=SOURCE+"images/"+ident+".jpg"
        page=SOURCE+"pages/"+ident+".html"
        recs=[x for x in s["images"] if x.get("file")==url and x.get("source_page")==page]
        panes=[x for x in s["visual_comparison"]["items"] if x.get("image_url")==url]
        gpanes=[x for x in g["visual_comparison"]["items"] if x.get("image_url")==url]
        if len(recs)!=1 or len(panes)!=1 or len(gpanes)!=1:
            raise RuntimeError("Existing exact-source records/gallery must match exactly "+ident)
        x=recs[0]
        if x.get("creator")!="Bob Harms" or x.get("license")!=LIC or x.get("source_taxon")!="Sporobolus vaginiflorus (photographer identification)":
            raise RuntimeError("Existing original rights/taxon mismatch "+ident)
        target=SP.parent/"images"/("bob-harms-"+ident.lower()+"-poverty-dropseed.jpg")
        if target.exists() or any(row.get("file_name")==target.name for row in rows):
            raise RuntimeError("File preexists. No overwrite: "+str(target))
        todo.append((ident,url,page,target,x,panes[0],gpanes[0]))
    audit_before=audit()
    if audit_before["species_cards"]!=112:
        print("NOTICE: canonical grass count changed from 112: ",audit_before["species_cards"],flush=True)
    sess=requests.Session()
    sess.headers.update({"User-Agent":"HaysCountyBotanyEducationalImageArchive/1.0 (github.com/Crking92/Hays-County-Botany)"})
    prepared=[]
    for ident,url,page,target,x,spane,gpane in todo:
        raw,data,dims,stored,actual=jpeg(sess,url)
        prepared.append((ident,url,page,target,x,spane,gpane,raw,data,dims,stored,actual))
        print("VERIFIED SOURCE",ident,dims,len(data),flush=True)
    assert len(prepared)==8
    found=[]
    for ident,url,page,target,x,spane,gpane,raw,data,dims,stored,actual in prepared:
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(data)
        x.update({
            "file":"images/"+target.name,
            "source_image":url,
            "source_taxon_name":"Sporobolus vaginiflorus",
            "site_specific_public_permission":PERMIT,
            "source_original_sha256":hashlib.sha256(raw).hexdigest(),
            "archived_sha256":hashlib.sha256(data).hexdigest(),
            "original_image_size":dims,
            "archived_image_size":stored,
            "downloaded_from":actual,
            "archived_locally":True,
            "image_status":"PHYSICALLY_ARCHIVED_COPYRIGHTED_HARMS_EDUCATIONAL_ATTRIBUTION_ONLY",
            "modifications":"Re-encoded original photo as RGB JPEG, maximum edge 2400px, stripped EXIF/GPS, browser arrows remain separate.",
            "public_reuse":"Bob Harms expressly grants credited scientific/educational use of his own Selected Central Texas Monocots images (site only, NOT CC)."
        })
        for panel in (spane,gpane):
            panel["image_url"]=str(target)
            panel["source_image"]=url
            panel["source_taxon_name"]="Sporobolus vaginiflorus"
            panel["site_specific_public_permission"]=PERMIT
            panel["photo_status"]="PHYSICALLY ARCHIVED exact original Bob Harms copyrighted photograph: credited SCIENTIFIC/EDUCATIONAL site use only, NOT CC. Original creator/source/license preserved, EXIF/GPS scrubbed, needs final user anatomy review; no invented microscopic arrows."
        vals={"file_name":target.name,"role":x["role"],"creator":"Bob Harms","license":LIC,
              "license_url":x["license_url"],"source_page":page,"direct_url":actual,
              "study_use":"Public noncommercial scientific education","public_reuse":x["public_reuse"],
              "modifications":x["modifications"]}
        rows.append({col:vals.get(col,"") for col in columns})
        found.append({"image_path":str(target),"source_page":page,"creator":"Bob Harms","license":LIC,
                     "source_original_sha256":x["source_original_sha256"],
                     "archived_sha256":x["archived_sha256"],"original_dimensions":dims,
                     "archived_dimensions":stored})
    for key, prior in protected.items():
        if json.dumps(s.get(key),sort_keys=True)!=prior:
            raise RuntimeError("Protected native/range taxonomy changed")
    if json.dumps(g["project_scope"],sort_keys=True)!=genus_scope:
        raise RuntimeError("Protected genus scope changed")
    s["curation_status"]["photo_metadata_count"]=11
    s["curation_status"]["photo_files_present"]=10
    s["curation_status"]["harms_sporobolus_eight_physical_archived_20261022"]="Eight exact Bob Harms original photos physically archived and source hashed with educational credit (not CC), all previously existing 2 local CC photos remain. Original Historic PD plate stays external."
    s["field_id_finish_pass"]["stage"]="FIELD_READY_PHOTO_GAPS — eight physically stored real documented Harms Texas botanical anatomy images now cover rooted habit, sheaths, head architecture, blooming, dispersal and collar; missing measured 1mm isolated lemma/callus/ligule and source-vouchered local microscope series."
    s["field_id_finish_pass"]["new_photo_archive_20261022"]={"added_real_JPEGs":8,"added_new_anatomy_arrows":0,"real_photos_total":10,
          "photo_license":"Bob Harms scientific/educational credited use only, NOT CC",
          "needed_microscopy":["1mm dissected lemma/palea with true hairs/prickles under 40–45×","Measured actual ligule margin and scale","Same-site rooted/panicle/spikelet specimen crosslinked with voucher"],
          "original_science_unchanged":True}
    s["visual_comparison"]["subtitle"]+=" EIGHT Harms exact-source photos now stored in GitHub (no external image dependency), with photographer and limited rights retained."
    s["visual_comparison"]["overlay_note"]=(s["visual_comparison"].get("overlay_note","")+" Eight already expert-source-identified Harms photos moved to physical local JPEGs; no fine-point marker additions, previous annotations retained.").strip()
    g["visual_comparison"]["subtitle"]+=" Eight linked S. vaginiflorus diagnostic Harms photographs are now backed by real files in the species folder; no duplicate bytes."
    g["visual_status"]="FIELD_READY_PHOTO_GAPS — eight physical author-credited S. vaginiflorus photographs plus original genus material; still missing microscopic lemma vestiture and measured same-specimen comparisons across complexes."
    g["curation_status"]["sporobolus_vaginiflorus_second_pass_20261022"]["new_stored_binary_photos"]=8
    g["curation_status"]["sporobolus_vaginiflorus_second_pass_20261022"]["photos_locally_archived_and_verified"]=True
    with CSV.open("w",newline="",encoding="utf8") as fh:
        writer=csv.DictWriter(fh,fieldnames=columns,lineterminator="\n");writer.writeheader();writer.writerows(rows)
    save(SP,s);save(GN,g)
    audit_after=audit()
    save(AUDIT,audit_after)
    save(REPORT,{"result":"EIGHT_REAL_HARMS_POVERTY_DROPSEED_IMAGES_PHYSICALLY_ARCHIVED",
             "species":"Sporobolus vaginiflorus","files":found,"photo_files_added":8,
             "total_target_species_local_jpegs":10,"species_panels":12,"genus_panels":14,
             "copyright":"© Bob Harms, scientific and educational use with proper attribution ONLY. Not Creative Commons.",
             "science_range_unchanged":True,"target_stage":s["field_id_finish_pass"]["stage"],
             "grass_inventory":audit_after})
    save(MARK,{"type":"manual_field_id_publication","date":"2026-10-22",
       "title":"Publish eight real locally archived poverty dropseed anatomical originals",
       "species":"Sporobolus vaginiflorus","report":str(REPORT),
       "physical_new_images":8,"total_local_species_photos":10,"species_panels":12,
       "genus_panels":14,"site_use_only":"credited Bob Harms scientific education; copyrighted, not Creative Commons",
       "status":"FIELD_READY_PHOTO_GAPS","native_county_unchanged":True,
       "photo_review":"ordinary public learner, provisional with original creator credit"})
    print("SUCCESS: eight real Harms photos physical, grass coverage "+str(audit_after),flush=True)
if __name__=="__main__":main()
