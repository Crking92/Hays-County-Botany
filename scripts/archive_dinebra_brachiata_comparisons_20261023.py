#!/usr/bin/env python3
"""Install four author-permitted exact Selected Monocots original photographs of
DINEBRA PANICEA SUBSP. BRACHIATA solely as comparisons on the
D. panicea SUBSP. MUCRONATA visual-ID card. These are DIFFERENT
subspecies; no source photo has been reidentified as mucronata.
PLUS two existing physically archived and arrowed Disakisperma photos.
Fail closed on mismatch, rights, concurrency or source download errors.
"""
from pathlib import Path
from io import BytesIO
from copy import deepcopy
import csv,hashlib,json,requests
from PIL import Image,ImageOps

BASE=Path("content/taxa/Poaceae")
SPEC=BASE/"Dinebra/dinebra-panicea-subsp-mucronata/species.json"
GENUS=BASE/"Dinebra/genus.json"
DISA=BASE/"Disakisperma/genus.json"
REG=SPEC.parent/"image-sources.csv"
REPORT=Path("reports/dinebra-mucronata-brachiata-four-pictures-and-native-lookalike-20261023.json")
MARK=Path("workflow/field-id-publication/2026-10-23-dinebra-sprangletop-six-reusable-comparisons.json")
PREFIX="https://w3.biosci.utexas.edu/prc/Monocots/GrassHTML/data/"
RIGHTS="https://w3.biosci.utexas.edu/prc/Monocots/"
LICENSE="© Bob Harms — scientific/educational use with attribution (NOT Creative Commons)"
PERM="BOB_HARMS_SELECTED_MONOCOTS_EDU_WITH_CREDIT_20261022"
RECORDS=[
 ("LEPAB-I","Flowering branches — another Dinebra subspecies", "Other subspecies: B. Harms photographed D. panicea subsp. brachiata flowering panicle in Central Texas. Look for many narrow flower-bearing side branches. This is NOT an authenticated subsp. mucronata photo."),
 ("LEPAB-J","Flowering units — other subspecies, never mucronata voucher", "Bob Harms' actual subsp. brachiata flowering close-up. Explore side branch origins and small flowering units. Without measured glumes/caryopsis, DON'T label this another subspecies and DON'T arrow minute mucros."),
 ("LEPAB-J1","Flowering-unit comparison — nearby subspecies", "Actual D. panicea subsp. brachiata, author-verified local reproductive detail. Near-relative botanical example for panicle/spikelet form, NOT target mucronata evidence."),
 ("LEPAB-L","True leaf ligule and sheath — other subspecies ONLY", "Original author-labelled L. panicea subsp. brachiata TRUE ligule/sheath. Use this to teach WHERE a ligule is. Subsp. mucronata needs its own photographed opened inner membrane with 1mm ruler; not automatically identical.")
]

def save(path,val):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(val,indent=2,ensure_ascii=False)+"\n",encoding="utf8")

def main():
    s=json.loads(SPEC.read_text(encoding="utf8"))
    g=json.loads(GENUS.read_text(encoding="utf8"))
    d=json.loads(DISA.read_text(encoding="utf8"))
    if (s.get("id")!="dinebra-panicea-subsp-mucronata" or g.get("name")!="Dinebra"
        or d.get("name")!="Disakisperma"):
        raise RuntimeError("Unexpected target identity, stop")
    if (len(s["images"]),len(s["visual_comparison"]["items"]),len(g["visual_comparison"]["items"]))!=(1,3,3):
        raise RuntimeError("Concurrent genus/species change; abort")
    if len(d["visual_comparison"]["items"])<9: raise RuntimeError("Native comparison changed")
    if REPORT.exists() or MARK.exists(): raise RuntimeError("Already installed")
    protected={k:json.dumps(s.get(k),sort_keys=True) for k in (
       "id","family","genus","species","infraspecific_rank","infraspecific_epithet",
       "scientific_name","common_name","taxonomy_source","synonyms","photo_taxonomy_note")}
    gscope=json.dumps(g.get("project_scope"),sort_keys=True)
    with REG.open(newline="",encoding="utf8") as f:
        rd=csv.DictReader(f);cols=list(rd.fieldnames or []);rows=list(rd)
    if "file_name" not in cols: raise RuntimeError("Bad original-source CSV")
    staged=[]
    for ident,title,description in RECORDS:
        name="bob-harms-dinebra-brachiata-"+ident.lower()+".jpg"
        outpath=SPEC.parent/"images"/name
        url=PREFIX+"images/"+ident+".jpg"
        page=PREFIX+"pages/"+ident+".html"
        if outpath.exists() or any(z.get("source_page")==page for z in s["images"]):
            raise RuntimeError("Already installed one original; do not double add")
        r=requests.get(url,timeout=40,headers={"User-Agent":"Hays-County-Botany-educational-grass-learner/1.0"})
        r.raise_for_status()
        raw=r.content
        if not (raw.startswith(b"\xff\xd8\xff") and 10000<len(raw)<8000000):
            raise RuntimeError(ident+" source is not an authentic source JPEG")
        with Image.open(BytesIO(raw)) as original:
            original.load()
            if original.format!="JPEG" or min(original.size)<300 or max(original.size)>4500:
                raise RuntimeError(ident+" unexpected source image dimensions")
            clean=ImageOps.exif_transpose(original).convert("RGB")
            dims=list(clean.size)
        bio=BytesIO();clean.save(bio,format="JPEG",quality=94,optimize=True)
        encoded=bio.getvalue()
        with Image.open(BytesIO(encoded)) as verified:
            assert verified.format=="JPEG" and verified.size==tuple(dims)
            assert not verified.getexif().get(34853)
            verified.verify()
        role="OTHER SUBSPECIES COMPARISON ONLY — Dinebra panicea subsp. brachiata, not target subsp. mucronata"
        item={
            "file":"images/"+name,"role":role,"creator":"Bob Harms",
            "license":LICENSE,"license_url":RIGHTS,
            "site_specific_public_permission":PERM,
            "source_taxon_name":"Dinebra panicea subsp. brachiata",
            "taxon_comparison_only":True,"source_page":page,"source_image":url,
            "source_original_name":"Leptochloa panicea ssp. brachiata",
            "source_region":"Bob Harms original Selected Central Texas Monocots",
            "public_reuse":"YES with credit for educational/scientific use only; copyrighted, NOT Creative Commons",
            "modifications":"Reencoded RGB JPEG; EXIF/GPS removed; image original not labeled as subsp. mucronata; no speculative new arrow",
            "original_sha256":hashlib.sha256(raw).hexdigest(),
            "archived_sha256":hashlib.sha256(encoded).hexdigest(),
            "image_dimensions":dims,"archived_locally":True,
            "photo_review":"Source-page exact taxon identification checked. Other subspecies scientifically distinct. No microscopic arrow coordinates because precise original-pixel target inspection not documented."
        }
        panel={
            "label":"OTHER SUBSPECIES · "+title,"scientific_name":"Dinebra panicea subsp. brachiata",
            "image_url":str(outpath),"image_fit":"contain","image_role":role,
            "caption":description+" Photographer Bob Harms permits credited scientific/educational use of this Selected Monocots original.",
            "why_it_matters":"The two recognized American subspecies are taxonomically distinct. Learn genus-level floral architecture without treating sibling subspecies as a mucronata voucher.",
            "creator":"Bob Harms","license":LICENSE,"license_url":RIGHTS,
            "site_specific_public_permission":PERM,
            "source_taxon_name":"Dinebra panicea subsp. brachiata",
            "source_page":page,"source_image":url,"taxon_comparison_only":True,
            "markers":[],
            "photo_status":"REAL source-original, author permission for educational use; different subspecies, NOT TARGET mucronata, no claimed glume mucro/caryopsis/ligule dimensions or fabricated arrows."
        }
        staged.append((outpath,encoded,item,panel))
    # Reuse already physically archived original of actual native green sprangletop.
    # The native lesson already verified two structural arrows at the correct
    # positions. Do not duplicate image binaries or label it as Dinebra.
    different=[]
    for index in (5,8):
        entry=deepcopy(d["visual_comparison"]["items"][index])
        if entry.get("scientific_name")!="Disakisperma dubium" or len(entry.get("markers") or [])!=2:
            raise RuntimeError("Green sprangletop verified reference changed")
        if not str(entry.get("image_url","")).startswith("content/taxa/Poaceae/Disakisperma/disakisperma-dubium/images/"):
            raise RuntimeError("Not a physically archived native comparison")
        if not entry.get("creator") or not entry.get("source_page") or not entry.get("license"):
            raise RuntimeError("Missing license provenance")
        entry["label"]="DIFFERENT NATIVE GREEN SPRANGLETOP · "+entry.get("label","")
        entry["caption"]="OTHER SPECIES, Disakisperma dubium, NOT Dinebra. "+entry.get("caption","")+" Source's two preverified arrows are kept on its actual structures. Native perennial typically has larger multi-flowered spikelets, useful contrast against a Dinebra ANNUAL; no absolute one-character ID."
        entry["photo_status"]=(entry.get("photo_status") or "")+" | Cross-taxon reference: existing physical original and existing photo-pixel-reviewed arrows only."
        different.append(entry)
    for p,b,item,panel in staged:
        s["images"].append(item)
        s["visual_comparison"]["items"].append(panel)
        g["visual_comparison"]["items"].append(deepcopy(panel))
        add={"file_name":p.name,"role":item["role"],"creator":item["creator"],
             "license":item["license"],"source_page":item["source_page"],
             "direct_url":item["source_image"],"study_use":"Credited educational site only",
             "public_reuse":"Authorized original educational reuse; NOT CC"}
        rows.append({k:add.get(k,"") for k in cols})
    s["visual_comparison"]["items"].extend(different)
    g["visual_comparison"]["items"].extend(deepcopy(different))
    s["visual_comparison"]["title"]="MUCRONATE SPRANGLETOP — one provisional target, sibling subspecies anatomy, and native green sprangletop"
    s["visual_comparison"]["subtitle"]="Nine total panels: 1 provisional target photo (CC BY-NC: public rights filter may hide), 2 existing lookalikes (CC BY-NC: public filter), 4 genuinely public education-permitted Bob Harms images of DIFFERENT D. panicea subsp. brachiata (not mucronata), plus 2 public-safe, physically archived native Disakisperma images with four existing verified arrows. No authenticated target micro photo."
    g["visual_comparison"]["title"]=s["visual_comparison"]["title"]
    g["visual_comparison"]["subtitle"]=s["visual_comparison"]["subtitle"]
    if len(s["visual_comparison"]["items"])!=9 or len(g["visual_comparison"]["items"])!=9:
        raise RuntimeError("Panel count changed")
    s["curation_status"]["photo_metadata_count"]=len(s["images"])
    s["curation_status"]["photo_files_present"]=len([q for q in s["images"] if q.get("file","").startswith("images/")])
    if s["curation_status"]["photo_files_present"]!=5:raise RuntimeError("Unexpected actual photos")
    g["curation_status"]["brachiata_originals_four_20261023"]={
      "new_original_photos":4,"other_subspecies_only":True,
      "other_native_green_sprangletop_photo_panels":2,
      "new_unverified_anatomy_arrows":0,
      "already_reviewed_native_arrows_reused":4,
      "target_mucronata_lens_micro_still_missing":True,
      "stage":"FIELD_READY_PHOTO_GAPS"
    }
    s["curation_status"]["brachiata_originals_four_20261023"]=deepcopy(g["curation_status"]["brachiata_originals_four_20261023"])
    s["curation_status"]["brachiata_originals_four_20261023"]["species_image_originals_total"]=5
    g["look_here_first"]="MUCRONATE SPRANGLETOP (subsp. mucronata) — annual with many slender ascending branches along a central axis and 2–4(-5)-flowered tiny spikelets. Short truncate/irregular membranous true ligule and raised-base sheath hairs must be inspected on the target itself. Four Central Texas Bob Harms comparison images show DIFFERENT subspecies brachiata, not a confirmed mucronata; the two separately labelled native green sprangletop photographs show larger multi-flowered units. Do not equate species complex or background other subspecies with target."
    s["look_here_first"]=g["look_here_first"]
    s["field_id_finish_pass"]["stage"]="FIELD_READY_PHOTO_GAPS — 4 REAL correctly named sibling subspecies brachiata macro photos newly archived, 2 actually documented native green sprangletop lookalike photos reused with 4 real existing arrows. Authentic mucronata macro, 1–3mm ligule, swollen sheath hair bases and tiny upper glume mucro still need source/voucher and scale."
    s["field_id_finish_pass"]["new_subspecies_comparison_lesson_20261023"]={
      "source_project_taxon":"Dinebra panicea subsp. mucronata",
      "comparison_taxon":"Dinebra panicea subsp. brachiata",
      "separate_currently_accepted_kew_subspecies":True,
      "original_credited_brachiata_photos":4,
      "original_target_mucronata_public_safe_diagnostic_photo_count":0,
      "additional_native_lookalike_reused_panels":2,
      "native_photo_arrows_reused":4,
      "particular_hold":"Individual floret under mm scale showing linear glumes over florets, 0.9–1.2mm lemma, caryopsis groove absent/present (distinguish mucronata and brachiata by regional key)",
      "sources":[
       "https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:60458622-2",
       "https://w3.biosci.utexas.edu/prc/Monocots/GrassHTML/data/Leptochloa-text.html",
       "https://herbarium.arizona.edu/sites/herbarium.arizona.edu/files/documents/Grass%20ID%20Workshop%202024%20W%20Index_1.pdf",
       "https://www.govinfo.gov/content/pkg/GOVPUB-SI-PURL-gpo92220/pdf/GOVPUB-SI-PURL-gpo92220.pdf"
      ]
    }
    g["visual_needs"]=[
      "FIRST: confirmed American/Texas DINEBRA PANICEA SUBSP. MUCRONATA small attached spikelet; distinguish BRAchiata comparison, 10-20x with 1mm scale.",
      "SECOND: actual MUCRONATA 1-3mm truncate-erose true membranous ligule and papilla/bulbous hair base sheath detail with ruler.",
      "THIRD: entire rooted annual mucronata, full many-branched narrow brushy flowering architecture.",
      "FOURTH: matched brachiata photo/voucher at same scale plus caryopsis with or without ventral groove, actual glumes relative to florets.",
      "Compare verified perennial green sprangletop Disakisperma dubium with much larger multiple-floret spikelets (two sourced local macro photos already in genus)."
    ]
    g["visual_status"]=s["field_id_finish_pass"]["stage"]
    if any(json.dumps(s.get(k),sort_keys=True)!=v for k,v in protected.items()):
        raise RuntimeError("Protected canonical taxonomy changed")
    if json.dumps(g.get("project_scope"),sort_keys=True)!=gscope:
        raise RuntimeError("Protected genus scope changed")
    for path,data,item,panel in staged:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(data)
    with REG.open("w",newline="",encoding="utf8") as f:
        wr=csv.DictWriter(f,fieldnames=cols,lineterminator="\n")
        wr.writeheader();wr.writerows(rows)
    save(SPEC,s);save(GENUS,g)
    save(REPORT,{
      "status":"FOUR_ACTUAL_OTHER_SUBSPECIES_LICENSED_HARMS_PHOTOS_ARCHIVED",
      "target":"Dinebra panicea subsp. mucronata",
      "actual_comparison":"Dinebra panicea subsp. brachiata",
      "real_new_source_photos":4,
      "original_photos":[{"file":str(p),"sha256":hashlib.sha256(b).hexdigest(),"source":item["source_page"],"dims":item["image_dimensions"]} for p,b,item,panel in staged],
      "genus_total_panels":9,"species_total_panels":9,
      "native_disakisperma_photo_panels_reused":2,
      "native_reference_original_arrow_count":4,
      "exact_mucronata_macro_added":0,
      "new_unverified_photo_arrows":0,
      "all_source_credits":"Bob Harms, educational/scientific use with credit (NOT CC)",
      "status_remaining":"FIELD_READY_PHOTO_GAPS"
    })
    save(MARK,{"type":"manual_photo_publication","date":"2026-10-23",
      "source":"Bob Harms Selected Monocots (4 of distinct brachiata) and already archived native Disakisperma images",
      "target":"Dinebra panicea subsp. mucronata",
      "actual_new_originals":4,
      "other_subspecies_only":True,
      "lookalike_panels_reused":2,
      "photo_rights":"Source-specific credited scientific and educational Harms permission, NOT CC",
      "annotation":"4 original previously pixel-verified Disakisperma arrows reused; no fabricated new arrows",
      "report":str(REPORT),"publish":"public learner rights filter",
      "finish_status":"FIELD_READY_PHOTO_GAPS"})
    print("SUCCESS four exact Harms OTHER SUBSPECIES photos and two native lookalikes, 0 invented arrows; no mucronata overclaims",flush=True)

if __name__=="__main__":main()
