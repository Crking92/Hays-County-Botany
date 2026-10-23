#!/usr/bin/env python3
"""Physical archive of Sam Kieschnick exact CC BY 4.0 Texas signalgrass panicle.
Fail closed on Wikimedia source rate limit; no invented pixels or rights.
"""
import csv,hashlib,io,json,time
from pathlib import Path
import requests
from PIL import Image,ImageOps

SPEC=Path("content/taxa/Poaceae/Urochloa/urochloa-texana/species.json")
GENUS=Path("content/taxa/Poaceae/Urochloa/genus.json")
CSV=SPEC.parent/"image-sources.csv"
DEST=SPEC.parent/"images/sam-kieschnick-urochloa-texana-panicle-cc-by4.jpg"
REPORT=Path("reports/urochloa-texana-panicle-physical-20261022.json")
MARK=Path("workflow/field-id-publication/2026-10-22-urochloa-texana-panicle-physical.json")
PAGE="https://commons.wikimedia.org/wiki/File:Urochloa_texana_Panicle.jpg"
ORG="https://upload.wikimedia.org/wikipedia/commons/3/3d/Urochloa_texana_Panicle.jpg"
THUMB="https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Urochloa_texana_Panicle.jpg/960px-Urochloa_texana_Panicle.jpg"
SRC="https://thumb.wikimedia.org/wikipedia/commons/thumb/3/3d/Urochloa_texana_Panicle.jpg/960px-Urochloa_texana_Panicle.jpg"
LICENSE="CC BY 4.0"
LICENSE_URL="https://creativecommons.org/licenses/by/4.0/"

def save(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
def fetch():
    sess=requests.Session()
    sess.headers.update({"User-Agent":"HaysCountyBotanyFieldEducation/1.0 (github.com/Crking92/Hays-County-Botany; source-credited)", "Accept":"image/jpeg,image/*"})
    failures=[]
    for url in (ORG,THUMB,SRC):
        try:
            r=sess.get(url,timeout=27)
            r.raise_for_status()
            b=r.content
            if not (10000<len(b)<7000000 and b[:3]==b"\xff\xd8\xff"):
                raise ValueError("Source response not a JPEG")
            with Image.open(io.BytesIO(b)) as im:
                im.load()
                if im.format!="JPEG" or im.size not in ((1536,2048),(960,1280)):
                    raise ValueError("Source is not one of the two Commons indexed 3:4 original/960px sizes: "+str(im.size))
                original_dims=list(im.size)
                clean=ImageOps.exif_transpose(im).convert("RGB")
            clean.thumbnail((1600,2000),Image.Resampling.LANCZOS)
            tmp=io.BytesIO()
            clean.save(tmp,format="JPEG",quality=92,optimize=True)
            stored=tmp.getvalue()
            with Image.open(io.BytesIO(stored)) as chk:
                assert chk.format=="JPEG" and not chk.getexif().get(34853)
                chk.verify()
            return b,stored,original_dims,list(clean.size),r.url
        except requests.HTTPError as e:
            code=e.response.status_code if e.response is not None else 0
            failures.append({"url":url,"status":code,"issue":"Source site denied"})
            if code==429:
                print("Wikimedia rate limit; no repeated retries to same URL",flush=True)
            continue
        except Exception as e:
            failures.append({"url":url,"reason":type(e).__name__+":"+str(e)[:160]})
            continue
    raise RuntimeError("SOURCE_HOLD_NO_BYTES: exact permitted Commons JPEG unavailable; NO CANONICAL CHANGE: "+repr(failures))
def main():
    sp=json.loads(SPEC.read_text(encoding="utf-8"))
    gen=json.loads(GENUS.read_text(encoding="utf-8"))
    assert sp["id"]=="urochloa-texana" and gen["name"]=="Urochloa"
    if DEST.exists():raise RuntimeError("Physical panicle already archived, no overwrite")
    if not (len(sp["images"])==1 and len(sp["visual_comparison"]["items"])==5 and len(gen["visual_comparison"]["items"])==5):
        raise RuntimeError("Concurrent gallery changes. Refetch canonical.")
    src_panel=next((p for p in sp["visual_comparison"]["items"] if p.get("source_page")==PAGE),None)
    gen_panel=next((p for p in gen["visual_comparison"]["items"] if p.get("source_page")==PAGE),None)
    if not src_panel or not gen_panel or src_panel.get("image_url")!=SRC or gen_panel.get("image_url")!=SRC:
        raise RuntimeError("Panicle source not the exact existing Commons photo")
    if src_panel.get("creator")!="Sam Kieschnick" or src_panel.get("license")!=LICENSE:
        raise RuntimeError("Source owner/license mismatch")
    with CSV.open(newline="",encoding="utf-8") as fh:
        rd=csv.DictReader(fh);cols=list(rd.fieldnames or []);rows=list(rd)
    if "file_name" not in cols:raise RuntimeError("Source provenance table changed")
    if any(x.get("file_name")==DEST.name for x in rows):raise RuntimeError("File already in provenance")
    protected={k:json.dumps(sp.get(k),sort_keys=True) for k in
      ("project_inclusion","county_occurrences_target_zone","native_target_zone_calculated","target_zone_count","synonyms","taxonomic_note")}
    original_scope=json.dumps(gen["project_scope"],sort_keys=True)
    raw,archived,dims,stored,actual=fetch()
    print("VERIFIED ORIGINAL",dims,"ARCHIVED",stored,"JPEG",len(archived),flush=True)
    DEST.parent.mkdir(parents=True,exist_ok=True)
    DEST.write_bytes(archived)
    meta={"file":"images/"+DEST.name,
       "role":"Exact source CC BY 4.0 fertile panicle closeup with large ovoid spikelets and ascending one-sided branches",
       "creator":"Sam Kieschnick","license":LICENSE,"license_url":LICENSE_URL,
       "source_page":PAGE,"source_image":ORG,"downloaded_from":actual,
       "original_dimensions":dims,"archived_dimensions":stored,
       "original_sha256":hashlib.sha256(raw).hexdigest(),"archived_sha256":hashlib.sha256(archived).hexdigest(),
       "source_taxon_name":"Urochloa texana",
       "original_source_locality":"Sam Kieschnick photograph, Washington County TX; not Hays voucher",
       "photo_status":"REAL_CC_BY_4_EXACT_SOURCE_PHYSICALLY_ARCHIVED_PROVISIONAL_USER_ANATOMY_REVIEW",
       "public_reuse":"CC BY 4.0 attributed source, linked author/license and change disclosure",
       "modifications":"JPEG RGB encode/resize, stripped EXIF/GPS; original photograph subject unchanged. HTML arrows are independent overlays."}
    sp["images"].append(meta)
    for p in (src_panel,gen_panel):
        p["image_url"]=str(DEST)
        p["license_url"]=LICENSE_URL
        p["source_image"]=ORG
        p["modification_note"]=meta["modifications"]
        p["photo_status"]="PHYSICALLY ARCHIVED: exact Sam Kieschnick Commons CC BY 4.0 panicle JPEG, decoded and source-hashed. Gross branching/spikelets visible; no ruler, no individual lower glume, no ligule or 2-floret dissection. PROVISIONAL — USER PHOTO REVIEW PENDING."
    sp["curation_status"]["photo_metadata_count"]=2
    sp["curation_status"]["photo_files_present"]=2
    sp["curation_status"]["signalgrass_CC_BY_4_panicle_archived_20261022"]="Second real exact-species source panicle JPEG physically stored on main, full photographer/license/source/changes, source hashes; 5 species photo teaching panels, 5 genus panels; microscopic 1mm structures still FIELD_READY_PHOTO_GAPS."
    sp["field_id_finish_pass"]["diagnostic_panicle_archive_20261022"]={
       "new_physical_real_photo_files":1,"total_stored_files":2,"source_license":LICENSE,
       "same_taxon_author":"Sam Kieschnick",
       "measured_microscopy_unavailable":True,
       "hold_roles":["1mm true ciliate ligule macro on same adult","5 mature 4.5–5.9mm spikelets","2.4–3.2mm lower glume with veins","true cross-veined lower lemma versus hard upper lemma","whole rooted plant matched to mature head"] }
    sp["visual_comparison"]["subtitle"]+=" Sam Kieschnick CC BY 4.0 real attached spikelet panicle now backed by a physical site-local JPEG."
    sp["visual_comparison"]["overlay_note"]+=" Exact panicle source archived in GitHub, gross arrow placements retained from prior photographic review; no new guessed fine glume/ligule arrows.";
    gen["visual_comparison"]["subtitle"]+=" Texas signalgrass reference is now a true local canonical JPEG, not just a Wikimedia hotlink.";
    gen["curation_status"]["texas_signalgrass_physical_panicle_20261022"]={"species_local_files":2,"new":1,"source":PAGE,"license":LICENSE,"field_ready_photo_gaps_preserved":True}
    vals={"file_name":DEST.name,"role":meta["role"],"creator":meta["creator"],"license":LICENSE,
          "source_page":PAGE,"direct_url":actual,"study_use":"Public educational field photo site",
          "public_reuse":meta["public_reuse"],"photo_id":"Sam-Kieschnick-2021-Urochloa-texana-Panicle","observation_id":""}
    rows.append({col:vals.get(col,"") for col in cols})
    with CSV.open("w",encoding="utf-8",newline="") as fh:
        writer=csv.DictWriter(fh,fieldnames=cols,lineterminator="\n");writer.writeheader();writer.writerows(rows)
    for k,earlier in protected.items():
        assert json.dumps(sp.get(k),sort_keys=True)==earlier,"science protected "+k
    assert json.dumps(gen["project_scope"],sort_keys=True)==original_scope
    assert len(sp["images"])==2 and len(sp["visual_comparison"]["items"])==5 and len(gen["visual_comparison"]["items"])==5
    save(SPEC,sp);save(GENUS,gen)
    save(REPORT,{"result":"ONE_REAL_CC_BY4_UROCHLOA_TEXANA_PANICLE_ARCHIVED","file":str(DEST),
      "source_page":PAGE,"creator":"Sam Kieschnick","license":LICENSE,
      "original_sha256":meta["original_sha256"],"archived_sha256":meta["archived_sha256"],
      "source_dimensions":dims,"archive_dimensions":stored,"images_physical_total":2,
      "species_panels":5,"genus_panels":5,"last_mile":sp["field_id_finish_pass"]["diagnostic_panicle_archive_20261022"]["hold_roles"]})
    save(MARK,{"type":"manual_field_id_publication","date":"2026-10-22",
      "title":"Local real licensed Texas signalgrass panicle and accurate 9-step diagnostic lesson",
      "taxon":"Urochloa texana","report":str(REPORT),"new_real_jpegs":1,
      "source_license":"Sam Kieschnick CC BY 4.0","status":"FIELD_READY_PHOTO_GAPS",
      "review":"Normal public learner species page, no preapproval required",
      "range_taxonomy_unchanged":True})
    print("SUCCESS ONE TEXAS SIGNALGRASS REAL PHOTO ARCHIVED",flush=True)
if __name__=="__main__":main()
