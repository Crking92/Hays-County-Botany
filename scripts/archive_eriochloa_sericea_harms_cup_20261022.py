#!/usr/bin/env python3
"""Archive ONE Bob Harms source-labelled E. sericea basal callus/cup macro.
Exactly the Selected Monocots ERSE5-9 original, which the author permits
for scientific/educational use WITH CREDIT. NOT Creative Commons.
The visible pale knobs beneath detached spikelets can teach the basal cup;
the complete attachment to a live pedicel and true hair ligule remain gaps.
"""
from pathlib import Path
from io import BytesIO
import csv,hashlib,json
import requests
from PIL import Image,ImageOps

BASE=Path("content/taxa/Poaceae/Eriochloa")
SP=BASE/"eriochloa-sericea/species.json"
GN=BASE/"genus.json"
CSV=SP.parent/"image-sources.csv"
DST=SP.parent/"images/bob-harms-texas-cupgrass-erse5-9-basal-cup.jpg"
REPORT=Path("reports/eriochloa-sericea-harms-basal-cup-one-20261022.json")
MARK=Path("workflow/field-id-publication/2026-10-22-eriochloa-sericea-real-basal-cup-photo.json")
PAGE="https://w3.biosci.utexas.edu/prc/Monocots/GrassHTML/data/pages/ERSE5-9.html"
SRC="https://w3.biosci.utexas.edu/prc/Monocots/GrassHTML/data/images/ERSE5-9.jpg"
PERMISSION="https://w3.biosci.utexas.edu/prc/Monocots/"
LICENSE="© Bob Harms — scientific/educational use with attribution (NOT Creative Commons)"
ATTEST="BOB_HARMS_SELECTED_MONOCOTS_EDU_WITH_CREDIT_20261022"

def saved(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf8")

def main():
    s=json.loads(SP.read_text(encoding="utf8"))
    g=json.loads(GN.read_text(encoding="utf8"))
    if s.get("id")!="eriochloa-sericea" or g.get("name")!="Eriochloa":
        raise RuntimeError("Wrong canonical target")
    if (len(s["images"]),len(s["visual_comparison"]["items"]),len(g["visual_comparison"]["items"]),
        s["curation_status"]["photo_files_present"])!=(7,3,3,7):
        raise RuntimeError("Concurrent species/genus photo edit: abort and refresh")
    if DST.exists() or REPORT.exists() or MARK.exists() or any(x.get("source_page")==PAGE for x in s["images"]):
        raise RuntimeError("Already installed; prevent duplicate")
    keep={k:json.dumps(s.get(k),sort_keys=True) for k in
         ("id","family","genus","species","scientific_name","common_name",
          "taxonomy_source","common_name_alternates","comparisons")}
    genus_scope=json.dumps(g.get("project_scope"),sort_keys=True)
    with CSV.open(newline="",encoding="utf8") as f:
        rd=csv.DictReader(f);fields=rd.fieldnames or [];rows=list(rd)
    if "file_name" not in fields or any(x.get("file_name")==DST.name for x in rows):
        raise RuntimeError("Source CSV has changed or photo already listed")
    res=requests.get(SRC,timeout=38,headers={
       "User-Agent":"Hays-Botany-Educational-Learner/1.0 (source-credited scientific image)"})
    res.raise_for_status()
    raw=res.content
    if not(raw.startswith(b"\xff\xd8\xff") and 15000<len(raw)<8000000):
        raise RuntimeError("Image source not a genuine JPEG; no installation")
    with Image.open(BytesIO(raw)) as f:
        f.load()
        if f.format!="JPEG" or min(f.size)<310 or max(f.size)>3000:
            raise RuntimeError("Wrong original photographed source")
        dims=list(f.size)
        if dims[0]/dims[1] < 1.45 or dims[0]/dims[1]>2.1:
            raise RuntimeError("Unexpected image aspect ratio: stop before placing arrows")
        clean=ImageOps.exif_transpose(f).convert("RGB")
    out=BytesIO();clean.save(out,format="JPEG",quality=95,optimize=True)
    encoded=out.getvalue()
    with Image.open(BytesIO(encoded)) as im:
        assert im.format=="JPEG" and list(im.size)==dims and not im.getexif().get(34853)
        im.verify()
    if len(encoded)<13000: raise RuntimeError("JPEG too small")
    # Original 626 x 365 photograph: two detached spikelets at lower right
    # have conspicuous pale goblet-shaped knobs beneath their bodies.
    # The first marker targets the knob beneath x≈477 y≈337, NOT an invented
    # cup under a branch in a broad head shot.
    markers=[
      {"label":"Pale cup/callus beneath spikelet","label_x":40,"label_y":78,
       "target_x":76.5,"target_y":92.5},
      {"label":"Spikelet body above the cup","label_x":50,"label_y":42,
       "target_x":76.5,"target_y":67}
    ]
    if not all(0<=m[z]<=100 for m in markers for z in ("label_x","label_y","target_x","target_y")):
        raise RuntimeError("Arrow coordinates invalid")
    role="ACTUAL E. sericea detached spikelets with visibly pale globular basal cup/callus and original photographed scale reference"
    record={
      "file":"images/"+DST.name,"role":role,"creator":"Bob Harms","license":LICENSE,
      "license_url":PERMISSION,"site_specific_public_permission":ATTEST,
      "source_taxon_name":"Eriochloa sericea",
      "source_page":PAGE,"source_image":SRC,
      "source_scope":"Selected Central Texas Monocots original, Texas cupgrass, not a DigFlora page",
      "photo_review":"Original ERSE5-9 photograph inspected. Lower-right separated spikelets display pale rounded basal knobs. The left white knob near 76% x,93% y is directly visible; its measured width and attached live pedicel cannot be inferred. Original top scale strip retained.",
      "public_reuse":"YES, credited scientific/educational purpose only; NOT CC and not a general license to redistribute",
      "study_use":"Credited scientific/educational crew learner",
      "original_sha256":hashlib.sha256(raw).hexdigest(),
      "archived_sha256":hashlib.sha256(encoded).hexdigest(),
      "source_dimensions":dims,"archived_dimensions":dims,
      "modifications":"Real photo re-encoded RGB JPEG, EXIF/GPS removed. Two non-destructive caption/arrow overlays in JSON point only to visible spikelet and basal knob.",
      "archived_locally":True,
    }
    panel={
      "label":"REAL CUPGRASS CUP — pale globular base beneath detached spikelet; Bob Harms, Texas",
      "scientific_name":"Eriochloa sericea","image_url":str(DST),
      "image_fit":"contain","image_role":role,"creator":"Bob Harms","license":LICENSE,
      "license_url":PERMISSION,"site_specific_public_permission":ATTEST,
      "source_page":PAGE,"source_image":SRC,"source_taxon_name":"Eriochloa sericea",
      "caption":"Original Selected Central Texas Monocots ERSE5-9 photo by Bob Harms. In the LOWER RIGHT, a pale rounded CUP-LIKE CALLUS is visible below one detached spikelet; the arrow marks the actual pale basal knob, and a second arrow marks the spikelet body ABOVE it. The upper source scale strip is photographed, not generated. Do NOT call this an in-situ attached hairy pedicel, an actual ligule, or calibrated cup diameter. Copyright Bob Harms; specifically permitted for credited science/education, not CC.",
      "why_it_matters":"Finally shows why Texas cupgrass is called a cupgrass: a tiny rounded/globular base belongs BELOW a single spikelet, NOT to the flowering head. Other grasses with narrow racemes can look similar until actual spikelet bases are checked.",
      "markers":markers,
      "photo_status":"FIRST REAL visible source-authenticated E. sericea basal cup/callus photo; detached units, no attached pedicel or precision mm measurement. Existing true ligule and rooted whole-plant photo gaps preserved."
    }
    s["images"].append(record)
    s["visual_comparison"]["items"].append(panel)
    g["visual_comparison"]["items"].append(dict(panel))
    s["curation_status"]["photo_metadata_count"]=len(s["images"])
    s["curation_status"]["photo_files_present"]=8
    s["curation_status"]["eriochloa_one_real_cup_macro_20261022"]={
      "real_macro_photos_added":1,"original_sha256":record["original_sha256"],
      "visible_basal_cup_arrow_count":1,"total_new_photo_arrows":2,
      "source_page":PAGE,"rights":"CREDITED_AUTHOR_EDUCATIONAL_NON_CC",
      "true_ligule_still_missing":True,"attached_pedicel_still_missing":True,
      "status":"FIELD_READY_PHOTO_GAPS"
    }
    s["visual_comparison"]["subtitle"] += " NOW ADD: genuine Bob Harms source-identified basal rounded cup/callus beneath separated Texas cupgrass spikelet, with two true-pixel arrows. Original photo shows DETACHED units; still requires attached pedicel and hair-ligule macro."
    g["visual_comparison"]["subtitle"] += " Fourth panel: genuine original photographed E. sericea basal cup/callus on detached spikelets, two overlays. True attached pedicel and hair-fringe ligule still gaps."
    g["curation_status"]["eriochloa_real_cup_macro_20261022"]={
      "original_photos_archived":1,"visible_cup_photo":True,
      "genus_panels":4,"new_cup_arrows":1,"new_structure_arrows_total":2,
      "source":PAGE,"site_public_reuse":"credited educational Harms original, NOT CC",
      "precise_mm_measurement":False,"attached_hairy_pedicel_verified":False,
      "true_ligule_still_missing":True,"status":"FIELD_READY_PHOTO_GAPS"
    }
    g["visual_status"]="FIELD_READY_PHOTO_GAPS — 4 genuine source-credited photos including first visible actual pale basal cup/callus below DETACHED E. sericea spikelet, 7 broad/structure annotations. True collar hair ligule and attached pedicel with verified cup + 1-mm ruler still missing."
    if not g.get("quick_field_id_tiles") or len(g["quick_field_id_tiles"])!=4:
        raise RuntimeError("Unexpected genus crew tile schema")
    g["quick_field_id_tiles"][3]["photo_status"]="ACTUAL DETACHED BASAL CUP PHOTOGRAPH NOW PRESENT; ATTACHED PEDICEL + MEASURED 1-MM REFERENCE STILL MISSING"
    g["quick_field_id_tiles"][3]["expand"]+=" Now see source-credited original ERSE5-9 photo: pale rounded callus UNDER a detached spikelet. The visible white knob has an accurate arrow; NOT the same as showing an intact attached plant pedicel."
    s["field_id_finish_pass"]["stage"]="FIELD_READY_PHOTO_GAPS — actual source-verified pale basal cup/callus photographed beneath detached E. sericea spikelet, but complete attached pedicel, true hairy inner ligule with 1-mm scale, and rooted whole plant still absent."
    s["field_id_finish_pass"]["real_cup_photo_20261022"]={
      "source":PAGE,"photo_installed":True,"cup_on_detached_spikelet":True,
      "arrow_to_real_basal_cup":markers[0],"exact_cup_diameter_proven":False,
      "attached_pedicel_proven":False,"status":"FIELD_READY_PHOTO_GAPS"
    }
    if s.get("field_photo_quickcheck"):
      q=s["field_photo_quickcheck"]
      q["featured_photo_indices"]=list(dict.fromkeys((q.get("featured_photo_indices") or [])+[3]))
      q["steps"].append("7. NEW PHOTO 4 ACTUAL CUP: Bob Harms original ERSE5-9 depicts the small PALE GLOBULAR CUP/CALLUS beneath a detached Texas cupgrass spikelet; photo arrows target the pale base and spikelet above it. This is not a fully attached pedicel, nor a 1-mm measure, nor true hair ligule.")
      q["actual_photos"]=4
      q["already_locally_archived_photo_bytes"]=8
      q["gross_photo_arrows_on_four_panels"]=7
    for k,v in keep.items():
      if json.dumps(s.get(k),sort_keys=True)!=v:
        raise RuntimeError("Protected taxon or comparison field was changed: "+k)
    if json.dumps(g.get("project_scope"),sort_keys=True)!=genus_scope:
      raise RuntimeError("Protected genus scope changed")
    row={"file_name":DST.name,"role":role,"creator":"Bob Harms",
      "license":LICENSE,"license_url":PERMISSION,"source_page":PAGE,
      "direct_url":SRC,"study_use":"Credited science/education public learner",
      "public_reuse":"Original author permits science/education with credit, NOT CC",
      "modifications":record["modifications"]}
    rows.append({k:row.get(k,"") for k in fields})
    DST.parent.mkdir(parents=True,exist_ok=True)
    DST.write_bytes(encoded)
    with CSV.open("w",newline="",encoding="utf8") as f:
      w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n")
      w.writeheader();w.writerows(rows)
    saved(SP,s);saved(GN,g)
    saved(REPORT,{"result":"ONE_REAL_ERIOCHLOA_SERICEA_BASAL_CUP_PHOTO_ARCHIVED",
      "creator":"Bob Harms","source":PAGE,"original_image":SRC,
      "source_author_permission":PERMISSION,"license":LICENSE,
      "photo":str(DST),"dimensions":dims,
      "original_sha256":record["original_sha256"],"archived_sha256":record["archived_sha256"],
      "added_real_photos":1,"new_visible_basal_cup_arrows":1,"new_photo_arrows":2,
      "species_panels":4,"genus_panels":4,"locally_stored_species_photo_count":8,
      "scientific_gaps":["Cup demonstrated only on detached spikelet, not connected to pedicel",
                         "True hair-fringe ligule with millimeter reference not imaged",
                         "Connected rooted whole E. sericea not imaged"],
      "status":"FIELD_READY_PHOTO_GAPS"})
    saved(MARK,{"type":"manual_field_id_publication","date":"2026-10-22",
      "target":"Poaceae Eriochloa sericea","photo_count":1,
      "source":PAGE,"rights":"Bob Harms credited science/education ONLY, NOT CC",
      "status":"FIELD_READY_PHOTO_GAPS","report":str(REPORT),
      "show_in_public_learner":True})
    print("PASS ONE real basal cup photo archived with original author credit and TWO anatomically bounded arrows",flush=True)

if __name__=="__main__":main()
