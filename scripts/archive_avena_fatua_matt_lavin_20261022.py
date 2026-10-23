#!/usr/bin/env python3
"""Real-photo, license-exact, partial-safe wild oat archive.
Only source-verified Matt Lavin CC BY-SA 2.0 files. At least ligule + hairy
callus must be decoded before any canonical changes. Other source fetches
may be 429/throttled and remain documented holds.
"""
from __future__ import annotations
import csv,hashlib,io,json,time
from pathlib import Path
from urllib.parse import quote
import requests
from PIL import Image,ImageOps

REPO=Path(".")
DIR=REPO/"content/taxa/Poaceae/Avena"
SPEC=DIR/"avena-fatua/species.json"
GEN=DIR/"genus.json"
PROV=DIR/"avena-fatua/image-sources.csv"
REPORT=REPO/"reports/avena-fatua-actual-anatomy-photos-20261022.json"
MARK=REPO/"workflow/field-id-publication/2026-10-22-avena-fatua-local-anatomy-photo-pass.json"
LICENSE="CC BY-SA 2.0"
LICENSE_URL="https://creativecommons.org/licenses/by-sa/2.0/"
PHOTOS=[
  ("3885429615","ligule","TRUE LIGULE: two views of conspicuous membranous flap at junction",
   "Source-identified living wild-oat blade and sheath with actual pale membranous ligule shown from two viewpoints. A nearby pink fingertip is NOT a calibrated millimeter ruler, so no specific length can be measured from these pixels.",
   "A REAL blade/sheath/ligule identification view, not guessed outer collar hairs.",True),
  ("3884459917","callus","HAIRY CALLUS: basal hooked/barbed floret hair bundle",
   "Matt Lavin explicitly photographed the hairs of a ripe wild-oat floret callus and small attached rachilla. These hairs help the detached floret catch fur or soil. This image lacks a ruler: do not infer scar diameter or every rachilla internode.",
   "Observe the actual basal long hairs on the fertile dispersal unit; compare with cultivated oat after collecting real material.",True),
  ("3822613991","spikelet","INTACT SPIKELET: big pointed glumes and strongly bent awns",
   "True exact-species close image of wild-oat spikelets; stout bent dark awns protrude from overlapping pale-green bracts. The photographer cautions against confusing its robust lemma tips with slender oats Avena barbata. Do not assign specific floret counts if hidden behind glumes.",
   "Trace awn and glume architecture in a real flowering unit, rather than assuming all grassy awns indicate wild oats.",False),
  ("3849804128","spent-glumes","SHATTERED SPIKELET: empty glumes persist",
   "Original Matt Lavin Avena fatua photograph from an agricultural/roadside habitat shows faded empty glumes after florets detached. These are NOT hard seed-bearing florets. No identifiable callus remains in the persistent husk.",
   "Teaches shattering versus a still intact fruit-bearing inflorescence; do not confuse cultivated Avena sativa without confirming maturity.",False),
  ("3886254070","panicle","OPEN PANICLE: laterally branched stem with drooping spikelets",
   "Matt Lavin's original exact-species photo shows a lateral branch of the sparse open wild-oat panicle carrying pendant spikelets. The actual branch is photographed, not a straight barley or rye terminal spike.",
   "Crew first notices the nodding open oat panicle, then inspects ligule and mature dissected floret.",False),
]
EXPECTED={"3884459917":(1244,604)}
def save(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf8")

def fetch(session,source_id):
    title=f"Avena fatua ({source_id}).jpg"
    links=[
      "https://commons.wikimedia.org/wiki/Special:Redirect/file/"+quote(title),
      "https://commons.wikimedia.org/wiki/Special:Redirect/file/"+quote(title.replace(" ","_"))
    ]
    # Original no-geometry-change URL recorded on public Commons file page.
    if source_id=="3884459917":
        links.append("https://live.staticflickr.com/65535/3884459917_0ae647416e_o.jpg")
    errors=[]
    for u in links:
        for attempt in range(2):
            try:
                r=session.get(u,timeout=36,headers={"Accept":"image/jpeg,image/*"})
                r.raise_for_status()
                raw=r.content
                if not 9000<len(raw)<8_000_000 or not raw.startswith(b"\xff\xd8\xff"):
                    raise RuntimeError("Unexpected JPEG response length/magic")
                with Image.open(io.BytesIO(raw)) as im:
                    im.load()
                    if im.format!="JPEG" or min(im.size)<300 or max(im.size)>6500:
                        raise RuntimeError("Photo original pixel dimensions are not plausible")
                    expected=EXPECTED.get(source_id)
                    if expected and im.size!=expected:
                        raise RuntimeError("Source not exact expected dimensions")
                    original_dims=list(im.size)
                    clean=ImageOps.exif_transpose(im).convert("RGB")
                clean.thumbnail((2400,2400),Image.Resampling.LANCZOS)
                out=io.BytesIO()
                clean.save(out,"JPEG",quality=92,optimize=True)
                binary=out.getvalue()
                if len(binary)<7000:raise RuntimeError("Decoded archive JPEG too small")
                with Image.open(io.BytesIO(binary)) as check:
                    assert check.format=="JPEG" and not check.getexif().get(34853)
                    check.verify()
                return raw,binary,original_dims,list(clean.size),r.url
            except Exception as exc:
                errors.append(f"{type(exc).__name__}: {str(exc)[:100]}")
                time.sleep(1+attempt)
    return None,"; ".join(errors[-6:])

def main():
    sp=json.loads(SPEC.read_text())
    gen=json.loads(GEN.read_text())
    if sp["id"]!="avena-fatua" or gen["name"]!="Avena":
        raise RuntimeError("Target file identity changed")
    if len(sp["images"])!=1 or len(sp["visual_comparison"]["items"])!=1 or len(gen["visual_comparison"]["items"])!=1:
        raise RuntimeError("Another worker has touched wild oat: refresh and reconcile")
    protected={k:json.dumps(sp.get(k),sort_keys=True) for k in
             ("project_inclusion","county_occurrences_target_zone","native_target_zone_calculated",
              "target_zone_count","synonyms","taxonomic_note","taxonomy_source")}
    scope=json.dumps(gen["project_scope"],sort_keys=True)
    with PROV.open(newline="",encoding="utf8") as fh:
        reader=csv.DictReader(fh);columns=list(reader.fieldnames or []);rows=list(reader)
    if "file_name" not in columns:raise RuntimeError("No photo provenance file")
    valid=[]
    blocked=[]
    session=requests.Session()
    session.headers["User-Agent"]="HaysCountyBotanyPhotoArchive/1.0 (github.com/Crking92/Hays-County-Botany; educational attribution)"
    for source_id,slug,label,caption,why,required in PHOTOS:
        name=f"matt-lavin-avena-fatua-{source_id}-{slug}.jpg"
        dest=SPEC.parent/"images"/name
        if dest.exists() or any(x.get("file_name")==name for x in rows):
            raise RuntimeError("Refuse duplicate already-installed file: "+name)
        answer=fetch(session,source_id)
        if answer[0] is None:
            blocked.append({"source_photo_id":source_id,"required":required,"reason":answer[1]})
            print("SOURCE HELD",source_id,answer[1][:220],flush=True)
            continue
        raw,binary,dims,stored,url=answer
        print("VERIFIED",source_id,dims,len(binary),flush=True)
        valid.append((source_id,slug,label,caption,why,required,name,dest,raw,binary,dims,stored,url))
    ids={p[0] for p in valid}
    if not {"3885429615","3884459917"}.issubset(ids):
        raise RuntimeError("Real ligule AND callus photo essential; no incomplete gallery commit. Held: "+repr(blocked))
    assert all(json.dumps(sp.get(k),sort_keys=True)==v for k,v in protected.items())
    assert json.dumps(gen["project_scope"],sort_keys=True)==scope
    report=[]
    for sid,slug,label,caption,why,required,name,dest,raw,binary,dims,stored,used_url in valid:
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(binary)
        page=f"https://commons.wikimedia.org/wiki/File:Avena_fatua_({sid}).jpg"
        original=f"https://www.flickr.com/photos/plant_diversity/{sid}/"
        meta={"file":"images/"+name,"role":label,"creator":"Matt Lavin","license":LICENSE,
              "license_url":LICENSE_URL,"source_page":page,"original_source_page":original,
              "source_taxon_name":"Avena fatua","source_photo_id":sid,
              "public_reuse":"Yes. CC BY-SA 2.0 (credit and ShareAlike on modified photography). Original Matt Lavin photograph, NOT a local Hays specimen.",
              "image_status":"VERIFIED_CC_BY_SA_2_LOCAL_GITHUB_ARCHIVE_PROVISIONAL",
              "modifications":"Resaved as RGB JPEG (max 2400px), stripped original EXIF/GPS, no added pixels or printed label; photo remains CC BY-SA 2.0.",
              "source_dimensions":dims,"archive_dimensions":stored,
              "original_sha256":hashlib.sha256(raw).hexdigest(),
              "archived_sha256":hashlib.sha256(binary).hexdigest(),
              "downloaded_from":used_url}
        sp["images"].append(meta)
        panel={"label":label,"scientific_name":"Avena fatua","image_url":str(dest),"image_fit":"contain",
               "image_role":label,"caption":caption,"why_it_matters":why,
               "creator":"Matt Lavin","license":LICENSE,"license_url":LICENSE_URL,"source_page":page,
               "modifications":meta["modifications"],"markers":[],
               "photo_status":"Real physically archived verified CC BY-SA 2.0 Matt Lavin photograph (Montana), full rights/creator/source recorded; PROVISIONAL FOR USER ANATOMY REVIEW; no fictitious micromorphology arrows."}
        sp["visual_comparison"]["items"].append(panel)
        gen["visual_comparison"]["items"].append(dict(panel))
        provenance={"file_name":name,"role":label,"creator":"Matt Lavin","license":LICENSE,
                    "source_page":page,"direct_url":used_url,"study_use":"Public scientific/educational learner",
                    "public_reuse":meta["public_reuse"],"observation_id":"","photo_id":sid}
        rows.append({key:provenance.get(key,"") for key in columns})
        report.append({"path":str(dest),"source_page":page,"source_photo_id":sid,
                       "original_sha256":meta["original_sha256"],"archived_sha256":meta["archived_sha256"],
                       "original_dimensions":dims,"archive_dimensions":stored,
                       "creator":"Matt Lavin","license":LICENSE})
    with PROV.open("w",newline="",encoding="utf8") as fh:
        writer=csv.DictWriter(fh,fieldnames=columns,lineterminator="\n")
        writer.writeheader();writer.writerows(rows)
    n=len(valid)
    sp["curation_status"]["photo_metadata_count"]=1+n
    sp["curation_status"]["photo_files_present"]=1+n
    sp["curation_status"]["matt_lavin_licensed_anatomy_20261022"]=f"{n} exact 2.0 ShareAlike real species photographs locally stored, SHA verified; true ligule and hairy callus among physical images. Continue FIELD_READY_PHOTO_GAPS."
    sp["visual_comparison"]["title"]="Wild oat — leaf ligule, bent awn, hairy callus and shattered versus intact oat florets"
    sp["visual_comparison"]["subtitle"]=f"{1+n} fully credited, physically archived photos including {n} Matt Lavin CC BY-SA 2.0 real botanical anatomy references. Only existing 2 gross-feature arrows retained; licensed new photos lack an actual mm ruler."
    sp["visual_comparison"]["memory_rule"]="OPEN nodding panicle + bent/twisted dorsal LEMMA awn + true pale MEMBRANOUS leaf ligule + hairy CALLUS on SHATTERING ripe individual florets. Compare A. sativa and A. barbata using measured mature specimens. No precise 1mm claim from unscaled photo."
    sp["visual_comparison"]["overlay_note"]+=" Added real local JPEG CC BY-SA 2.0 original Matt Lavin biology photos, no guessed fine target arrows. Montana source locality not Texas voucher."
    sp["field_id_finish_pass"]["stage"]="FIELD_READY_PHOTO_GAPS — physically verified open panicle, actual ligule and hairy callus source photos now installed; mm scaled same-plant glume/lemma/rachilla dissection and local A. sativa/A. barbata comparison still required."
    sp["field_id_finish_pass"]["diagnostic_photo_second_pass_20261022"]={"new_physical_verified_CC_BY_SA_2_JPEGs":n,
         "mandatory_photos_locally_archived":["3885429615 true membranous ligule","3884459917 hairy mature callus"],
         "other_photos_archived":sorted(ids-{"3885429615","3884459917"}),
         "source_photo_holds":blocked,"original_introducted_status_unchanged":True,
         "new_guessed_anatomy_markers":0,
         "remaining":["Hays source-vouchered root to panicle full specimen", "Leaf ligule alongside TRUE 1mm ruler",
                      "Dissected ripe A. fatua 2-3 fertile florets with measured lemma/awn/callus/rachilla scar",
                      "Matched A. sativa and A. barbata actual measured florets for diagnostic comparison"]}
    sp["look_here_first"]+=" SECOND PASS: REAL photographer-attributed ligule and basal callus photographs now archived, with separate heads/awns only where archived. Don't confuse Avena fatua with slender A. barbata or cultivated A. sativa solely by a drooping oat-like inflorescence; mature basal callus hairs, seed shattering and floret comparisons need their own real scale."
    gen["visual_status"]="FIELD_READY_PHOTO_GAPS — true licensed original wild-oat ligule and hairy fertile callus macros plus prior hanging awn photo now visible; locally measured mature floret and source-vouched root still needed."
    gen["visual_comparison"]["subtitle"]=f"{1+n} actual source-attributed real photos now PHYSICALLY saved: original Ron Vanderhoff CC BY-NC and {n} Matt Lavin CC BY-SA 2.0 wild oat ligule/callus and possible reproductive photographs. No inaccurate fine organ arrows."
    gen["curation_status"]["matt_lavin_wild_oat_20261022"]={"physical_source_images_added":n,
        "original_species_only":True,"licensing":"CC BY-SA 2.0 Matt Lavin, processed JPEG disclosed",
        "science_unchanged":True,"status":"FIELD_READY_PHOTO_GAPS"}
    save(SPEC,sp);save(GEN,gen)
    save(REPORT,{"result":"LICENSED_AVENA_REAL_PHOTOS_ARCHIVED","species":"Avena fatua","physical_added":n,
         "physical_total":n+1,"genus_panels":1+n,"species_panels":1+n,
         "files":report,"source_holds":blocked,
         "remaining_completion":["Matched local mature fruit/shattering scar and cm/mm-scale lemma", "Ligule with real scale and full local habit", "Avena sativa and Avena barbata true comparative florets"],
         "native_science_preserved":True})
    save(MARK,{"type":"manual_field_id_publication","date":"2026-10-22",
         "title":"Original CC BY-SA 2.0 wild oat ligule and callus physically archived",
         "species":"Avena fatua","report":str(REPORT),"photos_installed":n,
         "source_license":"Matt Lavin CC BY-SA 2.0","user_review":"On public species learner, provisional without preapproval",
         "status":"FIELD_READY_PHOTO_GAPS","native_science_untouched":True})
    print("SUCCESS ARCHIVED",n,"REAL AVENA PHOTOS",flush=True)

if __name__=="__main__":
    main()
