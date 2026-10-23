#!/usr/bin/env python3
"""Source-scoped physical archiver: five copyrighted Bob Harms Carolina canarygrass
photographs with his express scientific/educational-with-credit permission.
NOT CC. All five must download and validate before anything is written.
"""
import csv,hashlib,io,json,time
from pathlib import Path
import requests
from PIL import Image,ImageOps

ROOT=Path(".")
BASE=ROOT/"content/taxa/Poaceae/Phalaris"
SP=BASE/"phalaris-caroliniana/species.json"
GN=BASE/"genus.json"
CSV=BASE/"phalaris-caroliniana/image-sources.csv"
REPORT=ROOT/"reports/phalaris-caroliniana-harms-five-real-photos-20261022.json"
MARK=ROOT/"workflow/field-id-publication/2026-10-22-phalaris-caroliniana-five-physical-photos.json"
SOURCE="https://w3.biosci.utexas.edu/prc/Monocots/GrassHTML/data/"
RIGHTS="https://w3.biosci.utexas.edu/prc/Monocots/"
LIC="© Bob Harms — scientific/educational use with attribution (NOT Creative Commons)"
PERMIT="BOB_HARMS_SELECTED_MONOCOTS_EDU_WITH_CREDIT_20261022"
PHOTOS=[
 ("PHCA6-b","whole-annual","1 · COMPLETE GRASS — flowering plant",
  "Whole Carolina canarygrass plant with leafy stems, typical tight spike-like heads and basal growth",
  "Whole grass habit before zooming: leaf arrangement, flowering culms and basal shoot form. Root attachment, life cycle and exact source county are not independently verifiable from this single frame.",
  "Study the actual habit, then inspect the narrow dense seedhead and leaf collar rather than guessing identity from green color."),
 ("PHCA6-i","inflorescence","2 · HEAD — one entire dense panicle",
  "Full inflorescence of Phalaris caroliniana showing compressed compact flowering panicle",
  "The real canarygrass head is dense, short-branched and layered with overlapping glumes. Outer glumes alone do not reveal the inner reduced sterile-floret count.",
  "Teach the field silhouette; the two-sterile-floret diagnostic still needs isolation and dissection."),
 ("PHCA6-j","head-detail","3 · HEAD MACRO — overlapping awnless spikelets",
  "Detailed actual source photograph of spikelet arrangement within the packed head",
  "Magnified crowded spikelets show narrow green/pale strongly keeled bracts making the compact head. These are spikelets, not a single exposed female fruit. No microscopic markers are placed without independently validated pixels.",
  "Trace individual spikelets and note scale/axis before attempting one mature dissected unit."),
 ("PHCA6-S","individual-spikelet","4 · SPIKELET MACRO — glumes and inner floret regions",
  "Source-authenticated tight spikelet anatomy photograph",
  "The photographer identifies this frame as a spikelet detail. Two glumes and the floret-bearing center are the structures to inspect. Do not declare BOTH reduced sterile florets separately visible or label their tips until a measured opened specimen resolves them.",
  "Most important late-stage photo; guide crew to dissect one spikelet and count TWO reduced sterile florets rather than inferring from a whole head."),
 ("PHCA6-L","leaf-ligule","5 · COLLAR — blade/sheath and membrane detail",
  "Source-authenticated leaf sheath, blade and ligule/collar photograph",
  "Actual specimen at the blade/sheath junction, useful for locating the membranous ligule. An individual inner membrane length cannot be claimed from a photograph without an unambiguous actual 1 mm reference in that frame.",
  "Teach crew WHERE to inspect and photograph the true inner ligule, not hairs or outer sheath edges.")
]
def save(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
def photo_bytes(sess,url):
    errors=[]
    for trial in range(2):
        try:
            r=sess.get(url,timeout=36,headers={"Accept":"image/jpeg,image/*"})
            r.raise_for_status()
            raw=r.content
            if not (8000<len(raw)<8_000_000 and raw[:3]==b"\xff\xd8\xff"):
                raise RuntimeError("Source response is not original JPEG")
            with Image.open(io.BytesIO(raw)) as img:
                img.load()
                if img.format!="JPEG" or min(img.size)<180 or max(img.size)>8500:
                    raise RuntimeError("Unexpected source JPEG dimensions")
                original_size=img.size
                clean=ImageOps.exif_transpose(img).convert("RGB")
            clean.thumbnail((2400,2400),Image.Resampling.LANCZOS)
            buff=io.BytesIO()
            clean.save(buff,format="JPEG",quality=92,optimize=True)
            contents=buff.getvalue()
            with Image.open(io.BytesIO(contents)) as verify:
                assert verify.format=="JPEG" and not verify.getexif().get(34853)
                verify.verify()
            assert len(contents)>7000
            return raw,contents,original_size,list(clean.size),r.url
        except Exception as ex:
            errors.append(str(type(ex).__name__)+": "+str(ex)[:170])
            time.sleep(2+trial*3)
    raise RuntimeError("Cannot retrieve/authenticate exact source "+url+" errors "+repr(errors))
def main():
    s=json.loads(SP.read_text(encoding="utf8"))
    g=json.loads(GN.read_text(encoding="utf8"))
    assert s["id"]=="phalaris-caroliniana" and s["scientific_name"]=="Phalaris caroliniana"
    assert g["name"]=="Phalaris" and g["project_scope"]["species_ids"]==["phalaris-caroliniana"]
    if not(len(s["images"])==1 and len(s["visual_comparison"]["items"])==3 and len(g["visual_comparison"]["items"])==3):
        raise RuntimeError("Another chat modified canonical Phalaris; reconcile before re-running")
    prior={k:json.dumps(s.get(k),sort_keys=True) for k in
           ("project_inclusion","county_occurrences_target_zone","native_target_zone_calculated",
            "target_zone_count","synonyms","taxonomic_note")}
    genus_scope=json.dumps(g["project_scope"],sort_keys=True)
    with CSV.open(newline="",encoding="utf8") as csvfile:
        reader=csv.DictReader(csvfile)
        cols=list(reader.fieldnames or [])
        rows=list(reader)
    if not cols or "file_name" not in cols:
        raise RuntimeError("Source CSV missing provenance columns")
    plans=[]
    for code,slug,label,role,caption,why in PHOTOS:
        dest=SP.parent/"images"/("bob-harms-"+code.lower()+"-"+slug+".jpg")
        if dest.exists() or any(x.get("file_name")==dest.name for x in rows):
            raise RuntimeError("Previously archived file/CSV already exists; do not duplicate")
        page=SOURCE+"pages/"+code+".html"
        photo=SOURCE+"images/"+code+".jpg"
        if any(x.get("source_page")==page for x in s["images"]):
            raise RuntimeError("Image already linked; needs another reconciliation")
        plans.append({"code":code,"file":dest,"source_page":page,"image_url":photo,
                      "label":label,"role":role,"caption":caption,"why":why})
    session=requests.Session()
    session.headers["User-Agent"]="HaysCountyBotanyScientificEducationalImageAttribution/1.0 (github.com/Crking92/Hays-County-Botany)"
    prepared=[]
    for p in plans:
        raw,data,size,stored,actual=photo_bytes(session,p["image_url"])
        prepared.append((p,raw,data,size,stored,actual))
        print("PHCA JPEG verified",p["code"],size,len(data),flush=True)
    assert len(prepared)==5
    report=[]
    for p,raw,data,size,stored,actual in prepared:
        p["file"].parent.mkdir(parents=True,exist_ok=True)
        p["file"].write_bytes(data)
        file_rel="images/"+p["file"].name
        uri=str(p["file"])
        desc={ "file":file_rel,"role":p["role"],"creator":"Bob Harms",
          "license":LIC,"license_url":RIGHTS,"source_page":p["source_page"],
          "source_image":p["image_url"],"source_taxon_name":"Phalaris caroliniana",
          "site_specific_public_permission":PERMIT,
          "source_provenance":"Bob Harms Selected Central Texas Monocots; precise source image voucher locality not established",
          "public_reuse":"Scientific/educational credited use on noncommercial Hays public learner only; not CC or transferable blanket license",
          "original_sha256":hashlib.sha256(raw).hexdigest(),
          "archived_sha256":hashlib.sha256(data).hexdigest(),
          "original_dimensions":list(size),"archived_dimensions":stored,
          "downloaded_from":actual,"image_status":"LOCAL_ARCHIVE_CREDITED_EDUCATIONAL_NON_CC",
          "modifications":"JPEG RGB re-encode to max 2400px; EXIF/GPS removed, no image feature changed or burn-in annotation.",
          "photo_review":"Original author/species-specific public Monocots page, real source JPEG and physical dimensions checked. Internal spikelet sterile florets not independently labeled."}
        s["images"].append(desc)
        panel={"label":p["label"],"scientific_name":"Phalaris caroliniana",
          "image_url":uri,"image_fit":"contain","image_role":p["role"],
          "caption":p["caption"],"why_it_matters":p["why"],"creator":"Bob Harms",
          "license":LIC,"license_url":RIGHTS,"source_page":p["source_page"],
          "source_image":p["image_url"],"source_taxon_name":"Phalaris caroliniana",
          "site_specific_public_permission":PERMIT,
          "public_reuse":desc["public_reuse"],"markers":[],
          "photo_status":"Physically archived and hashed real Bob Harms copyrighted original with scientific/educational attribution use only (NOT CC). Anatomy details need final user/pixel review; no fictitious microscopic arrows."}
        s["visual_comparison"]["items"].append(panel)
        g["visual_comparison"]["items"].append(dict(panel))
        values={"file_name":p["file"].name,"role":p["role"],"creator":"Bob Harms","license":LIC,
                "source_page":p["source_page"],"direct_url":actual,
                "study_use":"Noncommercial scientific educational field learner",
                "public_reuse":desc["public_reuse"],"observation_id":"","photo_id":p["code"]}
        rows.append({h:values.get(h,"") for h in cols})
        report.append({"path":uri,"source_page":p["source_page"],"source_image":p["image_url"],
                       "original_sha256":desc["original_sha256"],"archived_sha256":desc["archived_sha256"],
                       "source_size":list(size),"archived_size":stored,"creator":"Bob Harms",
                       "license":LIC})
    assert all(json.dumps(s.get(k),sort_keys=True)==v for k,v in prior.items())
    assert json.dumps(g["project_scope"],sort_keys=True)==genus_scope
    assert len(s["visual_comparison"]["items"])==8 and len(g["visual_comparison"]["items"])==8
    assert sum(len(x.get("markers",[])) for x in s["visual_comparison"]["items"])==7
    for dest in [SP,GN]:
        assert dest.exists()
    s["curation_status"]["photo_metadata_count"]=6
    s["curation_status"]["photo_files_present"]=6
    s["curation_status"]["harms_maygrass_5_photo_archive_20261022"]="Five original credited Bob Harms physical species photo JPEGs hashed and decoded (whole plant, panicle, detail, spikelet, ligule/sheath), existing CC BY-NC photo preserved. Same-plant measured sterile floret count/collar still open."
    s["curation_status"]["visual_photo_panels"]=8
    s["curation_status"]["external_photo_panels"]=2
    s["visual_comparison"]["subtitle"]="8 credited visual panels: original archived CC BY-NC head; five newly archived true Bob Harms Central Texas original photographs of whole plant, head, detail, spikelet and collar; one external Kate Morgan Carolina image; one DIFFERENT SPECIES P. minor comparison. Five Bob Harms images carry site-specific scientific/educational credit permission, NOT CC.";
    s["visual_comparison"]["overlay_note"]+=" Five true source species JPEGs by Bob Harms physically archived, no fine arrows added. The unique two-reduced-sterile-florets distinction is from original botanical treatments and needs specimen-level photo proof, not guessed pixels.";
    s["look_here_first"]+=" FIVE source-labelled physically archived Harms photos now show whole annual habit, entire flowering head, compact inflorescence details, individual spikelet, and photographed collar/sheath. They do NOT yet independently prove individual TWO inner sterile lemmas; count those in a dissected mature spikelet with true 1mm ruler. Original attribution copyrighted science/education, not CC.";
    s["field_id_finish_pass"]["stage"]="FIELD_READY_PHOTO_GAPS — five physical Bob Harms whole/head/spikelet/collar photos plus one original photo and two separate external comparison references; precise opened 2-vs-1 sterile-floret photo pair and measured same-local rooted specimen remain missing";
    s["field_id_finish_pass"]["new_physical_diagnostic_files_20261022"]=5
    s["field_id_finish_pass"]["photo_panels_20261022"]=8
    s["field_id_finish_pass"]["unresolved_diagnostic_photo_truth"]=[
       "A single dissected true Phalaris caroliniana 4–6mm spikelet showing TWO reduced sterile florets and ONE fertile, with separate accurate arrow tip and actual ruler",
       "Matched 1mm dissected P. minor comparison showing ONE reduced sterile floret and toothed wing (introduced, not canonical Phalaris install)",
       "Same vouchered local Hays annual with TRUE fibrous roots, leaf blade, short 1.5–7mm ligule measured in place, flowering head, one open spikelet"
    ];
    s["field_id_finish_pass"]["visible_structure_arrows"]=7
    g["visual_status"]="FIELD_READY_PHOTO_GAPS — 8 genus panels with five real photographed Bob Harms whole/head/spikelet/collar originals physically stored. Micro-validation of two sterile lemmas vs P. minor one still needed.";
    g["visual_comparison"]["subtitle"]="8 true credited genus panels: five Bob Harms exact-species physical JPEG originals via permitted scientific/educational attribution use, plus three older views including separate P. minor comparison. Actual two-inner-sterile-lemmas dissection still missing.";
    g["look_here_first"]+=" Five new physical Bob Harms photographs now lead from whole plant to compact panicle, overlapping spikelets and sheath/collar. No true drawn diagram or source image resolves individually labeled two sterile florets; crew needs a real dissected source-vouchered measured floret.";
    g["curation_status"]["harms_maygrass_photo_upgrade_20261022"]={"physical_new_files":5,"genus_panels":8,"rights":"Exact Bob Harms scientific/educational site use with credit, NOT CC","science_unchanged":True,"unresolved":"same-scale opened native P. caroliniana versus introduced P. minor two-vs-one sterile floret and measured local annual collar/root"};
    with CSV.open("w",newline="",encoding="utf8") as f:
        writer=csv.DictWriter(f,fieldnames=cols,lineterminator="\n");writer.writeheader();writer.writerows(rows)
    save(SP,s);save(GN,g)
    save(REPORT,{"result":"FIVE_HARMS_CAROLINA_CANARYGRASS_JPEGS_ARCHIVED",
      "scientific_name":"Phalaris caroliniana","files":report,"new_physical_files":5,
      "all_physical_species_files":6,"species_panels":8,"genus_panels":8,
      "source_rights":"Bob Harms Selected Central Texas Monocots education/science with attribution, NOT CC",
      "native_zone_and_taxonomy_unchanged":True,"anatomical_arrows_added":0,
      "last_mile":s["field_id_finish_pass"]["unresolved_diagnostic_photo_truth"]})
    save(MARK,{"type":"manual_field_id_publication","date":"2026-10-22",
      "title":"Five author-cleared real Carolina canarygrass photographs physically archived",
      "taxon":"Phalaris caroliniana","report":str(REPORT),
      "new_real_JPEGs":5,"species_panels":8,"genus_panels":8,
      "photo_rights":"Bob Harms own original work scientific/educational use WITH visible attribution, not Creative Commons",
      "scientific_status":"FIELD_READY_PHOTO_GAPS","county_nativity_unchanged":True,
      "user_review":"normal public species page, no preapproval, microscopy arrows held",
      "release":"Standard rights-filtered noncommercial public Pages build"})
    print("SUCCESS: FIVE CAROLINA CANARYGRASS REAL JPEGs; 8 genus + 8 species teaching panels",flush=True)
if __name__=="__main__":main()
