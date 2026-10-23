#!/usr/bin/env python3
"""Physical original-image archive: four licensed-for-credited-education
Bob Harms Paspalum pubiflorum images. Not CC. No fabricated microscopic arrows.
"""
import csv,hashlib,io,json,time
from pathlib import Path
import requests
from PIL import Image,ImageOps
ROOT=Path(".")
BASE=ROOT/"content/taxa/Poaceae/Paspalum"
SPEC=BASE/"paspalum-pubiflorum/species.json"
GEN=BASE/"genus.json"
CSV=BASE/"paspalum-pubiflorum/image-sources.csv"
REPORT=ROOT/"reports/paspalum-pubiflorum-harms-original-four-20261022.json"
MARK=ROOT/"workflow/field-id-publication/2026-10-22-paspalum-pubiflorum-four-real-jpegs.json"
SRC="https://w3.biosci.utexas.edu/prc/Monocots/GrassHTML/data/"
LICENSE="© Bob Harms — scientific/educational use with attribution (NOT Creative Commons)"
LICENSE_URL="https://w3.biosci.utexas.edu/prc/Monocots/"
PERMISSION="BOB_HARMS_SELECTED_MONOCOTS_EDU_WITH_CREDIT_20261022"
PHOTOS=[
 ("PAPU5-I","full-inflorescence","3 · WHOLE HEAD — several actual one-sided spikelet racemes",
  "Author-identified inflorescence photograph of hairyseed paspalum. Examine the COMPLETE flowering head and count racemes attached to this same central stem; don't infer branch count from a crop of a single side branch.",
  "First confirm the whole reproductive architecture. Compare to Florida paspalum and Dallisgrass using independently labelled photographs."),
 ("PAPU5-J","flowering-detail","4 · FLOWERING — actual open pollen-bearing parts",
  "Actual Bob Harms photographed flowering material of Paspalum pubiflorum. Flowers are visible in the source image; do not label isolated green scales as fertile fruit nor assume a glume-hair count without a 1 mm scale.",
  "Shows the crew that floral tissue and glumes are distinct from each other and from mature spikelets."),
 ("PAPU5-J1","flowering-anatomy","5 · SPIKELET DETAIL — small ovoid units on a one-sided branch",
  "Real source-determined reproductive close-up. Identify rows of compressed oval spikelets and look for fine hairs on the upper glume; their length and precise position require a more magnified side-lit view with a ruler.",
  "The close comparison with Paspalum floridanum depends on a real mature 2.7–3.2 mm unit, not image-based guesswork."),
 ("PAPU5-L","true-ligule-sheath","6 · COLLAR — real blade/sheath junction and ligule area",
  "Real Bob Harms leaf collar/sheath photograph. The true ligule is found inside the blade/sheath joint, not in longer unrelated basal hairs. Actual length must be established with a 1 mm ruler from a same-vouchered local specimen.",
  "Replaces the previous absence of an exact-species collar view, without calling an unmeasured membrane 2 mm.")
]
def save(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def verify_download(sess,url):
    errors=[]
    for attempt in range(3):
        try:
            r=sess.get(url,timeout=40,headers={"Accept":"image/jpeg,image/*"})
            r.raise_for_status()
            b=r.content
            if not 7000<len(b)<8_000_000 or not b.startswith(b"\xff\xd8\xff"):raise ValueError("Not an original JPEG")
            with Image.open(io.BytesIO(b)) as im:
                im.load()
                if im.format!="JPEG" or min(im.size)<65 or im.size[0]*im.size[1]<12000 or max(im.size)>12000:
                    raise ValueError("Image dimensions invalid: "+str(im.size))
                dimensions=list(im.size)
                clean=ImageOps.exif_transpose(im).convert("RGB")
            clean.thumbnail((2400,2400),Image.Resampling.LANCZOS)
            output=io.BytesIO()
            clean.save(output,format="JPEG",quality=92,optimize=True)
            blob=output.getvalue()
            with Image.open(io.BytesIO(blob)) as im:
                assert im.format=="JPEG" and not im.getexif().get(34853)
                im.verify()
            assert len(blob)>6000
            return b,blob,dimensions,list(clean.size),r.url
        except Exception as exc:
            errors.append(f"{type(exc).__name__}: {str(exc)[:120]}")
            time.sleep(1+attempt*2)
    raise RuntimeError("Exact original unavailable: "+url+" "+repr(errors))
def main():
    s=json.loads(SPEC.read_text(encoding="utf8"))
    g=json.loads(GEN.read_text(encoding="utf8"))
    assert s["id"]=="paspalum-pubiflorum" and g["name"]=="Paspalum"
    if len(s["images"])!=1 or len(s["visual_comparison"]["items"])!=2 or len(g["visual_comparison"]["items"])!=10:
        raise RuntimeError("Canonical files changed in another chat; abort and reconcile first")
    protected={k:json.dumps(s.get(k),sort_keys=True) for k in
          ("project_inclusion","county_occurrences_target_zone","native_target_zone_calculated","target_zone_count",
           "synonyms","taxonomic_note","taxonomy_source")}
    genus_scope=json.dumps(g["project_scope"],sort_keys=True)
    with CSV.open(newline="",encoding="utf8") as handle:
        reader=csv.DictReader(handle)
        cols=list(reader.fieldnames or [])
        rows=list(reader)
    if "file_name" not in cols:raise RuntimeError("CSV missing filename")
    session=requests.Session()
    session.headers["User-Agent"]="HaysCountyBotanyPublicEducationalPhotoArchive/1.0 (github.com/Crking92/Hays-County-Botany)"
    loaded=[]
    for code,slug,label,caption,why in PHOTOS:
        src=SRC+"images/"+code+".jpg"
        page=SRC+"pages/"+code+".html"
        dest=SPEC.parent/"images"/("bob-harms-"+code.lower()+"-"+slug+".jpg")
        if dest.exists() or any(r.get("file_name")==dest.name for r in rows):
            raise RuntimeError("Photo already exists; no overwrites or duplicate inclusion")
        raw,clean,dims,store_dims,actual=verify_download(session,src)
        loaded.append((code,label,caption,why,src,page,dest,raw,clean,dims,store_dims,actual))
        print("VERIFIED ORIGINAL",code,dims,len(clean),flush=True)
    if len(loaded)!=4:raise RuntimeError("Four originals were not all verified, commit none")
    report=[]
    for code,label,caption,why,src,page,dest,raw,clean,dims,store_dims,actual in loaded:
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(clean)
        meta={"file":"images/"+dest.name,"role":label,"creator":"Bob Harms","license":LICENSE,
              "license_url":LICENSE_URL,"source_page":page,"source_image":src,
              "source_taxon_name":"Paspalum pubiflorum",
              "site_specific_public_permission":PERMISSION,
              "source_locality":"Selected Central Texas Monocots collection; exact photo location not proven Hays",
              "public_reuse":"Credited scientific/educational public learner only under author permission, not CC or transferable photo license",
              "archived_sha256":hashlib.sha256(clean).hexdigest(),
              "original_sha256":hashlib.sha256(raw).hexdigest(),
              "original_dimensions":dims,"archived_dimensions":store_dims,
              "downloaded_from":actual,
              "modifications":"RGB JPEG recompression, max 2400px, EXIF/GPS stripped; no retouch or burned-in anatomy arrows",
              "image_status":"PHYSICAL_AUTHOR_EDUCATIONAL_CREDIT_ONLY_PROVISIONAL"}
        s["images"].append(meta)
        panel={"label":label,"scientific_name":"Paspalum pubiflorum","image_url":str(dest),
               "image_fit":"contain","image_role":label,"caption":caption,"why_it_matters":why,
               "creator":"Bob Harms","license":LICENSE,"license_url":LICENSE_URL,
               "source_page":page,"source_image":src,"source_taxon_name":"Paspalum pubiflorum",
               "site_specific_public_permission":PERMISSION,
               "public_reuse":meta["public_reuse"],
               "photo_status":"Real, physically stored Bob Harms source-original photo; © photographer, allowed credited science/education use only, not CC. Provisional public ID review; not a local voucher; 0 speculative microscopic arrows.","markers":[]}
        s["visual_comparison"]["items"].append(panel)
        g["visual_comparison"]["items"].append(dict(panel))
        csvrow={"file_name":dest.name,"role":label,"creator":"Bob Harms","license":LICENSE,
                "source_page":page,"direct_url":actual,
                "study_use":"Public noncommercial plant ID learner","public_reuse":meta["public_reuse"],
                "observation_id":"","photo_id":code}
        rows.append({k:csvrow.get(k,"") for k in cols})
        report.append({"path":str(dest),"source_page":page,"original_sha256":meta["original_sha256"],
             "archived_sha256":meta["archived_sha256"],"dims_original":dims,
             "dims_archived":store_dims,"creator":"Bob Harms","license":LICENSE})
    assert all(json.dumps(s.get(k),sort_keys=True)==v for k,v in protected.items())
    assert json.dumps(g["project_scope"],sort_keys=True)==genus_scope
    s["curation_status"]["photo_metadata_count"]=5
    s["curation_status"]["photo_files_present"]=5
    s["curation_status"]["real_harms_photos_20261022"]="Four original Bob Harms whole/head, bloom, spikelet and collar photos physically archived and hashes verified with credited scientific/educational permission; not Creative Commons."
    s["visual_comparison"]["title"]="Hairyseed paspalum — complete racemes, flowering units, true collar and close local look-alikes"
    s["visual_comparison"]["subtitle"]="Six visible teaching panels: one original archived CC BY-NC row of spikelets, four new real, physically archived, credited Harms Central Texas photos, and one distinct P. setaceum comparison. The real photos are not automatically a same-voucher local confirmed ID."
    s["visual_comparison"]["overlay_note"]=(s["visual_comparison"].get("overlay_note","")+" Four Bob Harms originals safely archived, zero guessed micro arrows, previous visible 3 gross arrow markers retained.").strip()
    s["look_here_first"]=(s.get("look_here_first") or "")+" NEW REAL DIAGNOSTIC PHOTO SERIES: four archived Central Texas original Harms images now show the FULL set of unilateral racemes, reproductive tissue, a close-up spikelet row and real blade/sheath junction. Source labels and rights are explicit. Compare ripe, calibrated spikelet glumes with Florida paspalum and Dallisgrass; do not claim 2.7–3.2mm from an unscaled image or identify species from one branch."
    s["field_photo_quickcheck"]["heading"]="Hairyseed paspalum: full flowering culm → one-sided racemes → glumes → true leaf collar"
    s["field_photo_quickcheck"]["featured_photo_indices"]=[0,2,3,4,5,1]
    s["field_photo_quickcheck"]["steps"].extend([
      "PHOTO 3: inspect a real complete flowering head and count all one-sided racemes on the SAME stem, not a crop of one row.",
      "PHOTO 4: study actual flowering organs within the panicle; purple or yellow tissue is not a ripe caryopsis.",
      "PHOTO 5: get a separately detached mature 2.7–3.2 mm spikelet and shine angled light on true glume hairs; picture has no reliable measured 1mm proof.",
      "PHOTO 6: lift the blade and photograph the real membranous inner ligule with millimeter reference, avoiding hairs on nearby external sheath.",
      "Compare to P. floridanum with larger published spikelet sizes and dallisgrass with long silky hairs; do NOT key on site moisture or gross head similarity alone."
    ])
    s["field_photo_quickcheck"]["warning"]+=" Four Harms original images are copyrighted, permitted for scientific/educational use only WITH visible Bob Harms credit. No Creative Commons grant and no confirmed Hays voucher for each photo."
    s["field_id_finish_pass"]["stage"]="FIELD_READY_PHOTO_GAPS — four real credited source photos archive head/bloom/spikelets/collar plus prior exact species row photo; same local measured spikelet hair, true ligule mm macro, root and Florida-paspalum lookalike comparisons remain."
    s["field_id_finish_pass"]["diagnostic_photo_20261022"]={
      "new_physically_archived_real_photos":4,"total_real_species_photos":5,
      "current_species_visual_panels":6,"source":"Bob Harms copyrighted scientific/educational credit",
      "missing":["same-voucher local Hays root-to-flowering-head and physical 1mm scale",
                 "opened mature upper glume with decisive hairs/veins under 10–20× with mm ruler",
                 "true visible ligule measured from junction in local source",
                 "same-view locally verified mature pubiflorum vs floridanum vs dilatatum"],
      "national_ranging_or_taxonomy_unchanged":True}
    g["visual_comparison"]["subtitle"]+=" Four additional genuinely original Bob Harms P. pubiflorum photos now physically stored, shared by species and genus, original creator and copyright preserved, not CC."
    g["curation_status"]["pubiflorum_real_photo_archiving_20261022"]={"new_archived_exact_species_originals":4,
         "all_genus_panels":14,"license":"Bob Harms original science/educational permission with credit, NOT CC",
         "science_and_county_nativity_untouched":True}
    g["visual_status"]="FIELD_READY_PHOTO_GAPS — genus now includes actual P. pubiflorum flowering head, bloom, spikelets, and collar; calibrated microhair and same-voucher Hays plant need finishing."
    with CSV.open("w",encoding="utf8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=cols,lineterminator="\n")
        writer.writeheader();writer.writerows(rows)
    save(SPEC,s);save(GEN,g)
    save(REPORT,{"result":"FOUR_PHYSICAL_HARMS_PASPALUM_PUBIFLORUM_JPEGS_ARCHIVED",
         "files":report,"added":4,"all_physically_stored_species_photos":5,
         "species_panels":6,"genus_panels":14,"original_science_untouched":True,
         "photo_rights":"Bob Harms science/education with attribution; copyrighted NOT CC",
         "last_mile":s["field_id_finish_pass"]["diagnostic_photo_20261022"]["missing"]})
    save(MARK,{"type":"manual_field_id_publication","date":"2026-10-22",
         "title":"Archive four real credited hairyseed paspalum anatomical photos",
         "species":"Paspalum pubiflorum","report":str(REPORT),
         "physical_new_files":4,"species_panels":6,"genus_panels":14,
         "status":"FIELD_READY_PHOTO_GAPS","copyright":"Bob Harms, credited educational-use-only, NOT CC",
         "review":"normal public learner, provisional; no user preapproval",
         "range_taxonomy_unchanged":True})
    print("SUCCESS FOUR_REAL_PASPALUM_PUBIFLORUM_PHOTOS",flush=True)
if __name__=="__main__":main()
