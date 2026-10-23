#!/usr/bin/env python3
"""Archive nine source-verified real Bob Harms LITTLE BLUESTEM photographs.
Photographer grants educational/scientific reuse with clear attribution, not CC.
Full all-or-none authenticated photo download before ANY card mutation.
Existing restricted/unlicensed legacy media never enter public visual gallery.
"""
from pathlib import Path
import csv,io,json,hashlib,time
import requests
from PIL import Image, ImageOps

DIR=Path("content/taxa/Poaceae/Schizachyrium")
SPEC=DIR/"schizachyrium-scoparium/species.json"
GEN=DIR/"genus.json"
CSV=SPEC.parent/"image-sources.csv"
REPORT=Path("reports/schizachyrium-little-bluestem-nine-real-harms-20261022.json")
MARK=Path("workflow/field-id-publication/2026-10-22-little-bluestem-nine-anatomy-harms.json")
BASE="https://w3.biosci.utexas.edu/prc/Monocots/GrassHTML/data/"
GRANT="https://w3.biosci.utexas.edu/prc/Monocots/"
LICENSE="© Bob Harms — scientific/educational use with attribution (NOT Creative Commons)"
PERMIT="BOB_HARMS_SELECTED_MONOCOTS_EDU_WITH_CREDIT_20261022"
# Only the image-specific pages linked by the author's Schizachyrium-text.html.
# Markers use 0-100 image coordinates and label broad visible structures only.
P=[
("SCSC-a","BUNCH BASE: real North Hays grass tuft",
 "Root-zone-level close-up of a dense actual little-bluestem tuft, narrow erect culms and lower dry persistent sheaths. This is a field photograph, not extracted roots, so fibrous roots and short rhizomes remain unknown.",
 "Teach compact tuft and many erect stems. Source grass is Texas; individual voucher coordinates beyond the author's North Hays/Travis collection are not established.",
 [{"label":"Clustered culm bases","label_x":5,"label_y":87,"target_x":46,"target_y":81}]),
("SCSC-a1","HABIT: naturally mixed native Texas grassy prairie",
 "North Hays/Travis author-field overview showing numerous erect dry bluish/russet bluestem clumps amongst other plants. Multiple overlapping stems make any SINGLE basal root position uncertain.",
 "Understand a native prairie population. Do not arrow a single unknown background shoot as a proven separate little bluestem.",
 []),
("SCSC-i","FLOWERING ARCHITECTURE: multiple branches each bearing short raceme",
 "Detached upper flowering culms with MANY short separate narrow racemes distributed along branched leafy stems. The BASE of this specimen is below the frame; it is not a rooted plant photo.",
 "Distinguish from introduced King Ranch bluestem, which has multiple longer fingers clustered at one apex. Follow branching connection instead of color.",
 [{"label":"Short separate racemes","label_x":3,"label_y":12,"target_x":48,"target_y":13},{"label":"Leafy upper branch","label_x":68,"label_y":86,"target_x":53,"target_y":61}]),
("SCSC-J","EARLY FLOWERING: real flowering culm, exposed anthers and hairy axes",
 "True little-bluestem floral close-up with pale feathery raceme axis and tan projecting flower parts during anthesis. Some photographed mature narrow florets are apparent; no paired mature same-plant units are isolated with full ruler here.",
 "Early flowering can lack full white seed fluff. Look for multiple short racemes, projecting flower organs and hairy axis sections.",
 [{"label":"Flowering unit along axis","label_x":2,"label_y":15,"target_x":48,"target_y":38},{"label":"Hairy raceme margins","label_x":66,"label_y":85,"target_x":57,"target_y":69}]),
("SCSC-J1","BLOOM CLOSE-UP: dark anthers, pale stigmas and mm scale",
 "Two original source images juxtaposed of actual purple/brown projecting ANTHERS and nearby pale hairy floral tissue. Millimeter reference printed on left image only; do not treat paired halves as exactly one plant or count florets from image background.",
 "Distinguish anthers during flowering from later airy white pappus-like rachis/pedicel hairs, and compare stages.",
 [{"label":"Protruding anthers","label_x":2,"label_y":30,"target_x":46,"target_y":33},{"label":"Scale strip visible","label_x":76,"label_y":92,"target_x":2,"target_y":66}]),
("SCSC-s","ATTACHED MATURE: actual awned spikelet pair with hairy axis",
 "True attached mature little-bluestem raceme on culm; long twisted/bent awn lines extend from brown fertile units and fine hairs surround the axis/short companion. This frame has no isolated 1-mm scale for a confirmed length.",
 "Real connected flowering architecture and attached hairy segment, before laboratory dissection of the two paired spikelets.",
 [{"label":"Awned fertile unit","label_x":1,"label_y":32,"target_x":44,"target_y":43},{"label":"Hairy raceme axis","label_x":63,"label_y":84,"target_x":45,"target_y":55}]),
("SCSC-9","DISSECTION: genuine isolated awned spikelets and white-haired segments with ruler",
 "An original Bob Harms photograph of several separated dry source-identified little-bluestem spikelet and rachis parts on dark background, with the PHYSICAL original ruler at left. Parts are from the botanical source, but they are separated; do not imply all nine positions belonged to one intact specimen. Advanced dissection of lower/upper glumes, lemma and pedicelled companion still requires adjacent same-spikelet lab macro.",
 "Best real source for isolated parts and scale, showing how awn-bearing fertile body differs from plume-like dispersal structures; no incorrect organ-specific pixels marked.",
 [{"label":"Isolated awned unit","label_x":64,"label_y":7,"target_x":62,"target_y":48},{"label":"Ruler at image edge","label_x":2,"label_y":10,"target_x":1,"target_y":55}]),
("SCSC-C","CULM ANATOMY: actual keeled leaf sheath, flattened stem and node",
 "Harms original photo of little-bluestem longitudinal flattened culm and overlapping green sheath, elongated hairs near the lower sheath opening; a node and original black-and-white metric strip at lower left. This is not a cross-section or proof of an anatomical ligule at this viewing angle.",
 "Observe ACTUAL compressed culm and visible node, compare KR. Do not miscall white sheath-edge hair as the true membrane.",
 [{"label":"Visible stem node","label_x":58,"label_y":2,"target_x":51,"target_y":17},{"label":"Flattened culm surface","label_x":1,"label_y":62,"target_x":46,"target_y":63}]),
("SCSC-L","COLLAR & LIGULE ZONE: actual blade/sheath junction with mm ruler",
 "Source-authenticated photograph of the little-bluestem collar: narrow blade bends upward, overlapping sheath below, hair tufts beside the opening and pale inner junction membrane. Original ruler strip at upper right and inset sheath cross-section at left. A precise free membranous edge 0.5–2.5 mm cannot be definitively measured in this overlapping/cropped photo, so arrow COLLAR ZONE rather than an invented ligule-tip pixel.",
 "Closes the major shortage of REAL leaf-junction imagery from Central Texas. The 0.5–2.5 mm membranous fringed ligule still merits a calibrated, pulled-open same-voucher macro for strict 100%.",
 [{"label":"True collar junction zone","label_x":1,"label_y":8,"target_x":39,"target_y":44},{"label":"Sheath-edge hair tufts","label_x":64,"label_y":89,"target_x":51,"target_y":66}])
]
def save(path,val):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(val,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
def load_source(session,url):
    errors=[]
    for attempt in range(3):
        try:
            res=session.get(url,timeout=40,headers={"Accept":"image/jpeg,image/*"})
            res.raise_for_status()
            raw=res.content
            if not (5000<len(raw)<8_000_000 and raw.startswith(b"\xff\xd8\xff")):
                raise ValueError("Not real JPEG source data")
            with Image.open(io.BytesIO(raw)) as im:
                im.load()
                if im.format!="JPEG" or min(im.size)<160 or max(im.size)>12000 or im.size[0]*im.size[1]<40000:
                    raise ValueError("Unusable original photograph dimensions "+repr(im.size))
                original_dims=list(im.size)
                rgb=ImageOps.exif_transpose(im).convert("RGB")
            rgb.thumbnail((2200,2200),Image.Resampling.LANCZOS)
            out=io.BytesIO()
            rgb.save(out,format="JPEG",quality=93,optimize=True)
            archive=out.getvalue()
            with Image.open(io.BytesIO(archive)) as chk:
                assert chk.format=="JPEG" and not chk.getexif().get(34853)
                chk.verify()
            if len(archive)<5000:raise ValueError("Archive too small")
            return raw,archive,original_dims,list(rgb.size),res.url
        except Exception as exc:
            errors.append(type(exc).__name__+":"+str(exc)[:150])
            if getattr(getattr(exc,"response",None),"status_code",None)==429:break
            time.sleep(2+attempt)
    raise RuntimeError("Missing actual original "+url+" "+repr(errors))
def main():
    s=json.loads(SPEC.read_text(encoding="utf8"))
    g=json.loads(GEN.read_text(encoding="utf8"))
    assert s["id"]=="schizachyrium-scoparium" and g["name"]=="Schizachyrium"
    if len(s["images"])!=5 or len(s["visual_comparison"]["items"])!=7 or len(g["visual_comparison"]["items"])!=8:
        raise RuntimeError("Concurrent species/genus gallery edits: refresh canonical SHA before install")
    pre={k:json.dumps(s.get(k),sort_keys=True) for k in
         ("project_inclusion","county_occurrences_target_zone","native_target_zone_calculated","target_zone_count","synonyms","authority","project_tracker_diagnostic")}
    gscope=json.dumps(g["project_scope"],sort_keys=True)
    with CSV.open(newline="",encoding="utf8") as fh:
        reader=csv.DictReader(fh);cols=list(reader.fieldnames or []);rows=list(reader)
    if "file_name" not in cols or "direct_image_url" not in cols:raise RuntimeError("Original source CSV changed")
    plans=[]
    for code,title,caption,why,markers in P:
        source=BASE+"images/"+code+".jpg"
        page=BASE+"pages/"+code+".html"
        target=SPEC.parent/"images"/("bob-harms-schizachyrium-scoparium-"+code.lower()+".jpg")
        if target.exists() or any(p.get("file_name")==target.name for p in rows):
            raise RuntimeError("Duplicate/partial archive of "+str(target))
        if any(p.get("source_page")==page for p in s["images"]):
            raise RuntimeError("This source photo already in canonical image pool")
        plans.append((code,title,caption,why,markers,source,page,target))
    session=requests.Session()
    session.headers["User-Agent"]="HaysBotanyAttributionPreservingEducationalArchive/1.0 github.com/Crking92/Hays-County-Botany"
    # All-or-nothing download verification before editing any canonical species/genus.
    staged=[]
    for code,title,caption,why,markers,source,page,target in plans:
        raw,data,origsize,storedsize,downloaded=load_source(session,source)
        staged.append((code,title,caption,why,markers,source,page,target,raw,data,origsize,storedsize,downloaded))
        print("VALID original little bluestem",code,origsize,"JPEG",len(data),flush=True)
    if len(staged)!=9:raise RuntimeError("Nine originals mandatory for publication")
    rows_report=[]
    for code,title,caption,why,markers,source,page,target,raw,data,origsize,storedsize,downloaded in staged:
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(data)
        meta={
            "file":"images/"+target.name,"role":title,"creator":"Bob Harms",
            "license":LICENSE,"license_url":GRANT,
            "source_page":page,"source_image":source,
            "source_taxon_name":"Schizachyrium scoparium",
            "site_specific_public_permission":PERMIT,
            "source_locality":"Selected Central Texas Monocots, primarily Travis and north Hays; exact specimen GPS/voucher not established",
            "source_original_sha256":hashlib.sha256(raw).hexdigest(),
            "archived_sha256":hashlib.sha256(data).hexdigest(),
            "source_dimensions":origsize,"archived_dimensions":storedsize,"downloaded_from":downloaded,
            "public_reuse":"YES for credited scientific/educational use of the author's originals only; COPYRIGHTED not CC/general redistribution",
            "modifications":"Original subject preserved as re-encoded JPEG, max2200px; EXIF/GPS stripped, annotations browser-overlays not burned into photographs.",
            "photo_review":"Actual taxon-specific Harms image source-paged, original photo inspected at public reference; exact individual specimen locality not authenticated. User final arrow/photo review provisional.",
            "image_status":"PHYSICAL_LICENSED_EDUCATIONAL_COPYRIGHTED_EXACT_SPECIES_PROVISIONAL"}
        s["images"].append(meta)
        newpanel={
            "label":title,"scientific_name":"Schizachyrium scoparium",
            "image_url":str(target),"image_fit":"contain","image_role":title,
            "caption":caption,"why_it_matters":why,
            "creator":"Bob Harms","license":LICENSE,"license_url":GRANT,
            "source_page":page,"source_image":source,"source_taxon_name":"Schizachyrium scoparium",
            "site_specific_public_permission":PERMIT,"public_reuse":meta["public_reuse"],
            "markers":markers,
            "photo_status":"Source-specific genuine central Texas botanical anatomy, originally photographed and credited to Bob Harms, copyrighted education/science with credit (NOT CC). Archival SHA and image dimensions verified, markers intentionally broad and provisional; not a same-vouchered 0.5mm ligule/sessile-pedicelled pair series."
        }
        s["visual_comparison"]["items"].append(newpanel)
        if code not in ("SCSC-a1","SCSC-J"):g["visual_comparison"]["items"].append(dict(newpanel))
        row={"file_name":target.name,"role":title,"platform":"UT PRC Selected Monocots",
             "creator":"Bob Harms","license":LICENSE,"source_page":page,"direct_image_url":source,
             "study_use":"public scientific education with photographer credit","public_reuse":meta["public_reuse"],
             "photo_id":code,"observation_id":""}
        rows.append({key:row.get(key,"") for key in cols})
        rows_report.append({"file":str(target),"source_page":page,"source_image":source,
                            "source_dimensions":origsize,"archived_dimensions":storedsize,
                            "source_SHA256":meta["source_original_sha256"],"archived_SHA256":meta["archived_sha256"],
                            "license":LICENSE,"creator":"Bob Harms","broad_actual_arrows":len(markers)})
    for k,v in pre.items():
        if json.dumps(s.get(k),sort_keys=True)!=v:raise RuntimeError("Protected taxon, nativity or region changed "+k)
    assert json.dumps(g["project_scope"],sort_keys=True)==gscope
    assert len(s["visual_comparison"]["items"])==16 and len(g["visual_comparison"]["items"])==15 and len(s["images"])==14
    s["curation_status"]["photo_metadata_count"]=14
    s["curation_status"]["photo_files_present"]=14
    s["curation_status"]["littlebluestem_harms_nine_20261022"]={
        "physical_licensed_originals_added":9,
        "total_local_photos_all_rights":14,
        "public_eligible_local_photos":11,
        "source":"Bob Harms exact nine photos SCSC a,a1,i,J,J1,s,9,C,L",
        "rights":"Science/education with credit, not CC",
        "cards_status":"FIELD_READY_PHOTO_GAPS — finish photo evidence stricter than field usefulness",
        "native_county_science_untouched":True}
    s["field_id_finish_pass"]["stage"]="FIELD_READY_PHOTO_GAPS — thorough 16-panel true local diagnostic photo lesson READY FOR CREW, but STRICT same-voucher 1-mm unfurled free ligule tip and complete attached sessile/pedicelled pair DISSECTION are still not independently resolved."
    s["field_id_finish_pass"]["nine_real_texas_harms_photos_20261022"]={
        "new_files":9,"new_gallery_panels":9,
        "originals_source_verified":True,"creator_attribution":"Bob Harms",
        "source_licensing":"Copyrighted, attributed scientific/educational use allowed, not CC",
        "real_source_ruler_ligule_sheath":"SCSC-L exact Central Texas real sheath/ligule zone photograph; original physical mm reference present, but tip obscured/cropped, no inferred 0.5–2.5mm measurement",
        "real_source_ruler_spikelet_dissection":"SCSC-9 photographed separately arranged actual spikelet/bract/dispersal units with original scale; cannot prove matched pairs or named individual lower sterile floret organs",
        "real_intact_raceme":"SCSC-s real attached awned units/hairy axis; physical scale absent",
        "actual_local_specimen_roots":"Source SCSC-a shows basal bunch but not excavated roots; preserve honest field-bunch distinction",
        "visible_safe_anatomy_arrows_added":sum(len(x[4]) for x in P),
        "user_review":"Provisional photos directly to public learner",
        "unresolved_photo_roles":["Open blade/sheath exposing the exact 0.5–2.5mm free true membranous ligule/fringe beside 1mm ruler","ONE SAME mature pair showing both attached sessile fertile and pedicelled sterile companion, axis internode & true disarticulation scar and 1mm ruler; then isolated anatomical dissection on SAME voucher","A single root-to-flower vouchered Hays plant photograph with sheath and flowering upper branches physically connected"],
        "finish_level":"HIGH FIELD READINESS, NOT BOTANICAL 100% FINAL"}
    s["visual_comparison"]["title"]="LITTLE BLUESTEM — genuine Texas field/root zone, flowering, paired spikelet and collar photo course";
    s["visual_comparison"]["subtitle"]="16 real source-credited photographs, including 9 Bob Harms original Central Texas habitat, true blooming spikelet, isolated scale reference, culm and ligule-zone anatomy photos archived in GitHub. Four/other legacy source-rights restrictions preserved. 100% microscopic same-voucher completion not claimed.";
    s["visual_comparison"]["overlay_note"]=(s["visual_comparison"].get("overlay_note","")+" NEW: Nine exactly source-verified Bob Harms original photos and safe broad anatomical pointers. Scientific/educational WITH credit only, NOT Creative Commons. Local Hays collection does not imply one voucher for all nine. Do not confuse sheath-edge long hairs with the tiny true membranous ligule.").strip()
    s["field_photo_quickcheck"]["heading"]="Little bluestem — true Texas bunch to attached flowers, 1-mm source closeups and KR comparison"
    s["field_photo_quickcheck"]["featured_photo_indices"]=[0,9,14,11,12,13,15,4,2,5,6]
    s["field_photo_quickcheck"]["steps"]=[
      "1. See the existing real green bunch and Bob Harms photo 8 (SCSC-a) for a truly densely tufted plant with closely grouped basal culms. Photo 9 is a mixed prairie context; do not identify background grasses by color.",
      "2. Trace photo 10 (SCSC-i): multiple short independent racemes arise from different leafy UPPER branches, unlike several clustered long terminal fingers on KR B. ischaemum.",
      "3. Compare early flowering photo 2 (Judy Gallagher anthers) with Bob Harms photos 11–12 (SCSC-J/J1). Brown-purple dangling structures are anthers; airy white hairs on ripe rachis are separate dispersal adaptations, NOT aster-style pappus.",
      "4. Photo 13 (SCSC-s) shows an ACTUAL attached mature awned raceme with hairy rachis/pedicel area. Find one awned sessile fertile unit and smaller pedicelled companion at a node; its exact mm length is NOT measured from this unscaled view.",
      "5. Photo 14 (SCSC-9) shows physically detached original little-bluestem spikelet/bract parts with an actual ruler. DO NOT join neighboring detached pieces conceptually into one falsely identified attached spikelet pair.",
      "6. Photo 15 (SCSC-C) proves visible flattened culm, a node, green overlapping sheath and long sheath hairs; those are not the ligule.",
      "7. Photo 16 (SCSC-L) shows the TRUE blade/sheath junction + hairs and metric reference. Treat the tiny free membrane as PROVISIONAL / obscured, not photographically measured. To close the 100% gap, gently open SAME true collar under 10–20x with a 1mm ruler, find membranous fringed edge.",
      "8. Compare original archived Matt Lavin source photo 5: awned fertile sessile unit and reduced stalked companion. The photo lacks actual ruler/local voucher, but illustrates true paired structure instead of KR's terminal cluster.",
      "9. Compare KR panels 6 & 7 at equivalent flowering stage: KING RANCH longer multiple terminal racemes from same center; LITTLE more separate SHORT branches from upper leaf axils. Neither stem color nor node hairs alone is conclusive.",
      "10. End with the honest finish test: record cultivar/voucher/locality where available. Do not say microscopic species confirmation FINISHED unless same-voucher attached paired spikelet + free ligule are source photographed to scale."
    ]
    s["field_photo_quickcheck"]["field_rule"]="CREW READY: a distinctive narrow perennial bunch with many upper separate SHORT racemes, fuzzy mature paired spikelets and flattened keeled sheath. For specimen-level positive ID, verify ligule and pair and compare actual KR terminal branching.";
    s["field_photo_quickcheck"]["warning"]="All nine new Texas photographs are genuine copyrighted Bob Harms originals licensed for credited scientific/educational use, NOT CC. Some have a true printed mm reference, but ligule membrane and sessile + pedicellate pair are NOT documented fully opened and measured on one individual source. Original restricted Jean H., Minnesota and Illinois files are excluded from public gallery; preserve their private metadata.";
    g["visual_comparison"]["subtitle"]+=" Seven new original Bob Harms local true Schizachyrium photos now physically backed by canonical species JPEGs: North Hays bunch, branching, flowers, attached and isolated units and true collar/sheath. Microscopy 1mm exact membrane/paired voucher remains.";
    g["visual_status"]="FIELD_READY_PHOTO_GAPS — local true flower, spikelet, separately scaled bract and ligule-zone 9-photo source series substantially closes field training; microscope same-voucher free ligule/pair still required for 100%.";
    g["curation_status"]["little_blues_nine_original_harms_20261022"]={
      "new_sp_panels":9,"new_genus_panels":7,"local_new_image_files":9,
      "source_license":"Copyright Bob Harms, education/science with attribution, NOT CC",
      "original_taxa_scope_unchanged":True,"remaining_unresolved_microscopic_gaps":2}
    with CSV.open("w",newline="",encoding="utf8") as fh:
        writer=csv.DictWriter(fh,fieldnames=cols,lineterminator="\n");writer.writeheader();writer.writerows(rows)
    save(SPEC,s);save(GEN,g)
    save(REPORT,{"result":"NINE_AUTHENTIC_HARMS_LITTLE_BLUESTEM_JPEGS_ARCHIVED","files":rows_report,
                 "new_local_JPEGs":9,"all_species_photo_files":14,"public_species_gallery_panels":16,
                 "genus_photo_panels":15,
                 "photo_rights":"© Bob Harms; explicit scientific and educational reuse with proper attribution, NOT Creative Commons. Original restricted photos not exposed.",
                 "source_area":"Harms primarily northern Hays/Travis; individual photographs are not all same source voucher",
                 "photo_gaps_remaining":s["field_id_finish_pass"]["nine_real_texas_harms_photos_20261022"]["unresolved_photo_roles"],
                 "no_taxonomy_or_nativity_changes":True,"status":"FIELD_READY_PHOTO_GAPS"})
    save(MARK,{"type":"manual_field_id_publication","date":"2026-10-22",
                 "title":"Nine real credited Central Texas little bluestem diagnostic photographs, practical near-finish crew lesson",
                 "taxon":"Schizachyrium scoparium","report":str(REPORT),
                 "new_physical_JPEGs":9,"species_photo_panels":16,"genus_photo_panels":15,
                 "source_permission":"Copyrighted Bob Harms originals, science/education with visible photographer credit, not CC",
                 "user_review":"provisional directly on public learner; no preapproval",
                 "taxon_range_unchanged":True,"status":"FIELD_READY_PHOTO_GAPS",
                 "publication":"NORMAL_RIGHTS_FILTERED_GITHUB_PAGES"})
    print("SUCCESS: nine REAL Bob Harms little bluestem source photos, 16 species lesson panels, 15 genus panels",flush=True)
if __name__=="__main__":
    main()
