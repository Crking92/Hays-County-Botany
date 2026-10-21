#!/usr/bin/env python3
"""Install an individually CC BY 4.0 licensed, source-exact Panicum virgatum collar photo.
This is an existing-card finishing lane, not a new-taxon installer or range audit.
Source and image quality must pass before any canonical file mutation.
"""
import csv, io, json, pathlib, re, requests
from bs4 import BeautifulSoup
from PIL import Image, ImageOps
ROOT=pathlib.Path(".")
GENUS=ROOT/"content/taxa/Poaceae/Panicum/genus.json"
FOLDER=ROOT/"content/taxa/Poaceae/Panicum/panicum-virgatum"
SPEC=FOLDER/"species.json"
PAGE="https://plants.ces.ncsu.edu/plants/panicum-virgatum/"
FILENAME="Panicum-virgatum--Andrey-Zharkikh-2--CC-BY.jpg"
SAVED="images/ncsu-andrey-zharkikh-ccby4-collar-ligule.jpg"
LICENSE="https://creativecommons.org/licenses/by/4.0/"
SOURCE_CREDIT="Andrey Zharkikh"

def source_checked():
    sess=requests.Session()
    sess.headers.update({"User-Agent":"HaysBotanyEducationalPhotoCuration/1.0 (Crking92/Hays-County-Botany)"})
    r=sess.get(PAGE,timeout=40);r.raise_for_status()
    soup=BeautifulSoup(r.text,"html.parser")
    if "Panicum virgatum" not in soup.get_text(" ",strip=True):
        raise ValueError("NC State source species concept mismatch")
    candidates=[a for a in soup.select("a[href]") if FILENAME in a.get("href","")]
    if not candidates:raise ValueError("Exact Andrey collar photo link not found in NC State source")
    verified=False
    for node in candidates:
        a=node
        for level in range(8):
            txt=a.get_text(" ",strip=True)
            if "Andrey Zharkikh" in txt and "CC BY 4.0" in txt:
                verified=True;break
            if a.parent is None:break
            a=a.parent
        if verified:break
    if not verified:
        # A plain-text gallery crop is acceptable only if the photo link is surrounded
        # by the exact author and per-photo license within the same HTML neighborhood.
        raw=soup.get_text(" ",strip=True)
        if "Leaf blade attachment Andrey Zharkikh CC BY 4.0" not in raw:
            raise ValueError("Image-specific CC BY 4.0 / photographer not proved")
    from urllib.parse import urljoin,urlsplit
    image_url=urljoin(PAGE,candidates[0]["href"])
    parts=urlsplit(image_url)
    if parts.scheme!="https" or parts.hostname not in ("eit-planttoolbox-prod.s3.amazonaws.com","s3.amazonaws.com"):
        raise ValueError("Source image outside vetted NC State host")
    if not parts.path.endswith(FILENAME):raise ValueError("Unexpected image object")
    q=sess.get(image_url,timeout=50);q.raise_for_status()
    if not (15000<len(q.content)<12000000):raise ValueError("Unusable image payload")
    with Image.open(io.BytesIO(q.content)) as im:
        im.load();im=ImageOps.exif_transpose(im).convert("RGB")
    if min(im.size)<325:raise ValueError("Insufficient collar image resolution")
    im.thumbnail((1600,1600),Image.Resampling.LANCZOS)
    data=io.BytesIO();im.save(data,format="JPEG",quality=94,optimize=True)
    return data.getvalue(),list(im.size)

def record_caption():
    return "NC State source-identified genuine switchgrass collar: dense white hairs at leaf blade/sheath junction, above a short membrane. Visible tuft and blade are marked; a large rifle-sight membrane would instead indicate Indiangrass. No claim of 1-2 mm sizing without a ruler."

def photo_panel():
    return {
      "label":"1 · SWITCHGRASS — actual hairy collar and short ligule",
      "scientific_name":"Panicum virgatum",
      "image_url":"content/taxa/Poaceae/Panicum/panicum-virgatum/"+SAVED,
      "image_fit":"contain",
      "creator":SOURCE_CREDIT,"license":"CC BY 4.0","license_url":LICENSE,
      "source_page":PAGE,"image_role":"Photo of true switchgrass blade/sheath collar, pale silky hairs and leaf blade",
      "caption":record_caption(),
      "why_it_matters":"Decisive early routing from conspicuous upright Indiangrass membrane; hairy collars alone also occur on witchgrass, so cross-check annual/perennial and panicle.",
      "markers":[
          {"label":"White collar hairs","label_x":70,"label_y":10,"target_x":44,"target_y":51},
          {"label":"Leaf sheath below collar","label_x":73,"label_y":82,"target_x":51,"target_y":77}
      ],
      "annotation_status":"Two targets selected from visually inspected original NC State photograph, without transformations beyond EXIF-free JPEG encoding; owner mobile alignment QA pending."
    }

def main():
    s=json.loads(SPEC.read_text(encoding="utf-8"))
    g=json.loads(GENUS.read_text(encoding="utf-8"))
    if s["id"]!="panicum-virgatum" or s["scientific_name"]!="Panicum virgatum" or g["name"]!="Panicum":
        raise ValueError("Wrong existing canonical target")
    if any(z.get("file")==SAVED for z in s["images"]):
        assert (FOLDER/SAVED).is_file()
        print("Already installed, no-op");return
    if (FOLDER/SAVED).exists():raise ValueError("Image physically exists but is not yet listed: avoid overwrite")
    # no currently live target-claim conflicts
    import datetime
    claims=json.loads((ROOT/"workflow/work-claims.json").read_text(encoding="utf-8"))
    for c in claims.get("claims",[]):
        if "panicum-virgatum" not in c.get("taxa",[]):continue
        if c.get("status") not in ("active","in_progress","claimed"):continue
        expiry=c.get("expires_at")
        if not expiry:raise ValueError("Active target claim needs coordination")
        when=datetime.datetime.fromisoformat(expiry.replace("Z","+00:00"))
        if when.astimezone(datetime.timezone.utc)>datetime.datetime.now(datetime.timezone.utc):
            raise ValueError("Active target claim needs coordination")
    image,dim=source_checked()
    (FOLDER/SAVED).write_bytes(image)
    with Image.open(FOLDER/SAVED) as im:im.verify()
    record={
      "file":SAVED,"role":"Diagnostic true switchgrass blade/sheath collar showing tuft of hairs",
      "creator":SOURCE_CREDIT,"license":"CC BY 4.0","license_url":LICENSE,
      "source_platform":"NC State Extension Plant Toolbox","source_page":PAGE,
      "source_filename":FILENAME,"image_dimensions":dim,
      "study_use":"yes","public_reuse":"yes",
      "modifications":"EXIF/GPS removed, JPEG recompressed; two positional annotation arrows stored in JSON, not baked into JPEG",
      "photo_review":"Source page explicitly pairs 'Leaf blade attachment' with Andrey Zharkikh CC BY 4.0. Exact photo viewed for visible white collar hairs and green leaf blade; arrow position on mobile remains to be checked."
    }
    s["images"].append(record)
    s["look_here_first"]="SWITCHGRASS — LIFT THE BLADE AT THE COLLAR FIRST: a striking triangular cluster/cup of fine WHITE HAIRS projects from behind a SHORT membranous ligule. New CC BY 4.0 photograph demonstrates this directly. Compare Indiangrass's prominent stiff, upright 'rifle sight' membrane, and Witchgrass's likewise hairy collar but ANNUAL habit and typically much more hairy sheaths/nodes. Then trace the BROAD, open airy PYRAMIDAL PANICLE of individually pedicelled, unawned 3–5 mm spikelets. Follow stems down to creeping scaly rhizomes, unlike Hall's panicgrass's smaller bluish basal tuft or Kleingrass's knotty bunchgrass base. Use at least two characters; white hairs alone do not prove switchgrass."
    s["comparisons"]={
      "confused_with":["Sorghastrum nutans","Panicum hallii","Panicum capillare","Panicum coloratum","Sorghum halepense","Hopia obtusa"],
      "key_distinctions":"Real switchgrass hair-tuft collar + wide airy panicle + creeping scaly rhizomes. Indiangrass has a tall stiff rifle-sight membrane and denser golden plume; Hall's panicum short bluish tuft and compact ascending panicle; witchgrass annual with rough hairy sheaths/nodes and very diffuse branched inflorescence; introduced Kleingrass has tight knotty crown; Johnsongrass has large panicle with developed pedicelled companion spikelets and prominent white blade midrib.",
      "field_matrix":[
        {"taxon":"Panicum virgatum","collar":"DENSE white hairs behind a SHORT membrane","growth":"Robust perennial with CREEPING scaly rhizomes","head":"Long loose airy pyramidal panicle; solitary unawned spikelets"},
        {"taxon":"Sorghastrum nutans","collar":"Tall erect NOTCHED membranous ligule ('rifle sight')","growth":"Perennial often tufted/short rhizomes","head":"Single golden elongated more crowded panicle; bent awns"},
        {"taxon":"Panicum hallii","collar":"Hair-fringe; not reliably distinguished by collar alone","growth":"Short bluish, mostly basal-leaved perennial tuft","head":"Small stiff ascending panicle"},
        {"taxon":"Panicum capillare","collar":"Also hairy ligule — overlap","growth":"ANNUAL, conspicuously hairy sheaths and nodes","head":"Chaotic huge, very diffuse panicle with smaller spikelets"},
        {"taxon":"Panicum coloratum","collar":"No switchgrass-only definitive hair cue","growth":"Introduced bunchgrass with KNOTTY crown","head":"Fine fanlike branches"},
        {"taxon":"Sorghum halepense","collar":"Different shorter membranous ligule","growth":"Thick rhizomes and conspicuous white leaf midribs","head":"Branched open panicle with developed pedicelled partners"}
      ],
      "not_reliable_alone":["A white collar hair tuft: witchgrass and other grasses can also have hairs.","A purple tinge on the panicle or blade.","Tall stand: Indiangrass, bluestems and Johnsongrass overlap.","An exposed 'rhizome' from one broken stem; photograph connected underground runners before claiming."]
    }
    s["morphology_keys"]["best_field_traits"]=[
      "Long-lived C4 warm-season perennial with creeping scaly rhizomes and stout stems.",
      "Short (often ~1–2 mm) membranous-ciliate ligule with conspicuous pale-white 3–7 mm hairs from/behind ligular area: usually appears as a triangular tuft or cup.",
      "Wide glabrous to sometimes hairy blades, often blue-green, commonly with prominent light midrib.",
      "Open airy pyramid-shaped panicle, typically 15–50 cm, many ascending/arching branches; individual ovate awnless spikelets ~3.5–5 mm.",
      "Contrast annual Panicum capillare's hairy sheaths/nodes and reduced spikelet size; no species ID from ligule hairs alone."
    ]
    s["photo_diagnostic_lesson"]={
      "title":"Switchgrass — show the hairy collar, then airy panicle and scaly rhizomes",
      "steps":[
        {"stage":"1 — EXPOSE COLLAR","look":"White silky tuft at leaf/sheath junction, behind a SHORT membrane","what":"See the new actual switchgrass close-up with arrows to hairs and blade; compare upright rifle-sight membrane on Indiangrass."},
        {"stage":"2 — TRACE SEEDHEAD","look":"OPEN branched loose triangular/pyramidal panicle","what":"Photograph one intact head, not only its purple color; point out branch spacing and numerous small individual spikelets."},
        {"stage":"3 — CHECK SPIKELET","look":"Unawned solitary ovate spikelets (roughly 3.5–5 mm)","what":"Existing public licensed seed/fruit image is a learning view; an attached spikelet-on-branch macro with ruler is still needed."},
        {"stage":"4 — FOLLOW BASE","look":"Scaly creeping rhizomes joining multiple shoots","what":"An exposed basal crown and adjoining rhizomes distinguish switchgrass from short tufted Hall's panicgrass or knotty introduced Kleingrass."},
        {"stage":"5 — RULE OUT OTHER HAIRY COLLARS","look":"Witchgrass is hairy too, but ANNUAL","what":"Check leaf sheaths/nodes and seedhead spread; never identify from hairs alone."}
      ],
      "memory_rule":"SWITCHGRASS = WHITE COLLAR HAIR TUFT + BIG AIRY PANICLE + CREEPING RHIZOMES."
    }
    panel=photo_panel()
    photos=[
      panel,
      {"label":"2 · SWITCHGRASS — overall wild-type stand","scientific_name":"Panicum virgatum","image_url":"content/taxa/Poaceae/Panicum/panicum-virgatum/images/01-switchgrass-stand.jpg","image_fit":"contain","creator":s["images"][0]["creator"],"license":s["images"][0]["license"],"source_page":s["images"][0]["source_page"],"image_role":"Whole stand for relative grass height and loose open plume","caption":"Real switchgrass stand; tufted growth and seedheads visible from a distance, but no direct rhizome anatomy can be claimed.","why_it_matters":"Whole plant gestalt, weaker than collar/seedhead close-up.","markers":[]},
      {"label":"3 · SWITCHGRASS — actual mature fruit","scientific_name":"Panicum virgatum","image_url":"content/taxa/Poaceae/Panicum/panicum-virgatum/images/02-fruit-seed.jpg","image_fit":"contain","creator":s["images"][1]["creator"],"license":s["images"][1]["license"],"source_page":s["images"][1]["source_page"],"image_role":"Source-correct fruit/seed close-up, NOT attached panicle or ligule","caption":"Real fruit/seed view for scale and seed shape. Spikelet glumes, upper sterile lemma and exact branch attachment are not all visible.","why_it_matters":"Useful seed recognition, but don't confuse detached mature caryopsis with whole spikelet.","markers":[]},
      {"label":"4 · SWITCHGRASS — field stem context","scientific_name":"Panicum virgatum","image_url":"content/taxa/Poaceae/Panicum/panicum-virgatum/images/03-field-stems.jpg","image_fit":"contain","creator":s["images"][2]["creator"],"license":s["images"][2]["license"],"source_page":s["images"][2]["source_page"],"image_role":"Stand/stem density contextual image","caption":"Stems and leaves in a field; collar and true base are not magnified. This is supporting context, not an anatomy macro.","why_it_matters":"Crew recognizes plant in a maintained or natural stand.","markers":[]}
    ]
    s["visual_comparison"]={
       "title":"Switchgrass — the WHITE COLLAR HAIR TUFT is the first real photo clue",
       "subtitle":"FOUR exact-species public-safe local images. Andrey Zharkikh CC BY 4.0 collar photo now adds two true-organ arrow targets. Existing three images are preserved and credited.",
       "items":photos,
       "memory_rule":s["photo_diagnostic_lesson"]["memory_rule"],
       "annotation_status":"Two coordinate arrows placed against NC State original image with white tuft visible; stored JPEG kept same aspect and uncropped. Final mobile alignment QA pending.",
       "part_examples":[
         {"title":"White collar hairs and short membrane","role":"leaf blade/sheath collar","anchor_species_id":"panicum-virgatum","image_file":SAVED,"look_for":"White triangular/cup-shaped tuft where green blade pulls from sheath","why_it_matters":"Practical switchgrass vs Indiangrass discriminator; not unique from every panicgrass."},
         {"title":"Open pyramidal panicle","role":"mature inflorescence","status":"needs_photo","look_for":"Branching and attached spikelets with scale","why_it_matters":"Separates from dense awned panicles, especially Indiangrass."},
         {"title":"True creeping scaly rhizome","role":"basal growth architecture","status":"needs_photo","look_for":"Connected rhizome segments and shoot bases","why_it_matters":"Rules out tufted Hall's panicum and Kleingrass."}
       ]
    }
    s["field_photo_quickcheck"]={
       "heading":"Panicum virgatum — collar, panicle, rhizome",
       "featured_photo_indices":[3,0,1,2],
       "steps":[x["what"] for x in s["photo_diagnostic_lesson"]["steps"]],
       "field_rule":s["photo_diagnostic_lesson"]["memory_rule"],
       "warning":"The newly installed hair tuft is real and diagnostic in combination; existing whole-plant photos still do not document underground rhizome joints or attached multi-spikelet macro.",
       "owner_mobile_review":"PENDING"
    }
    s["diagnostic_photo_targets"]=[
       {"role":"Whole mature 15–50 cm airy panicle with branching and scale","status":"NEEDS_LICENSED_VERIFIED_PHOTO"},
       {"role":"Actual attached ovate unawned spikelet and glumes with 1 mm ruler","status":"NEEDS_LICENSED_MACRO"},
       {"role":"Scaly creeping rhizome connected to plant crown","status":"NEEDS_LICENSED_DIAGNOSTIC_PHOTO"},
       {"role":"Matched source-authenticated Switchgrass vs Indiangrass collar macros with mobile reviewed arrows","status":"PARTIAL_SWITCHGRASS_IMAGE_INSTALLED"}
    ]
    s["curation_status"].update({
      "version":"1.1-switchgrass-real-collar-20261021","last_visual_reviewed":"2026-10-21",
      "photo_metadata_count":len(s["images"]),"photo_files_present":len([z for z in s["images"] if str(z["file"]).startswith("images/")]),
      "visual_status":"FIELD_READY_PHOTO_GAPS: four exact species public photos; real NC State CC BY collar with two targeted arrows; basal rhizome and full spikelet-on-branch macros missing; mobile final arrow QA pending."
    })
    s["learner_visual_status"]={
       **s["learner_visual_status"],"status":"field_ready_photo_gaps","image_count":len(s["images"]),
       "note":"Real Andrey Zharkikh CC BY 4.0 switchgrass collar macro and two annotation arrows added; no other photo right changed."
    }
    s["photo_note"]+=" 2026-10-21: verified NC State Andrey Zharkikh CC BY 4.0 collar macro installed; arrow positions source-checked, user mobile QA remains."
    g["comparison_cards"].append({
       "title":"Switchgrass vs Indiangrass vs Johnsongrass — leaf collar first",
       "species_ids":["panicum-virgatum"],
       "look_here_first":"Switchgrass: SHORT membranous-ciliate ligule hidden beneath conspicuous white triangular HAIR TUFT (new exact CC BY 4.0 photo). Indiangrass: much TALLER upright NOTCHED ligule with two 'rifle-sight' corners. Johnsongrass: membranous ligule without that switchgrass tuft; follow broad white midrib and spikelet pair. Witchgrass also has collar HAIRS but is annual.",
       "field_matrix":[
         {"character":"Ligule","switchgrass":"Short membrane and tuft of WHITE HAIRS","indiangrass":"Tall notched rigid membrane","johnsongrass":"Membranous but no rifle-sight / switchgrass tuft","witchgrass":"Fringe hairs too (not species-specific)"},
         {"character":"Inflorescence","switchgrass":"Huge airy open pyramid","indiangrass":"Dense elongated golden plume; awns","johnsongrass":"Open panicle but developed paired spikelets","witchgrass":"Irregular expansive annual diffuse panicle"},
         {"character":"Growth base","switchgrass":"Creeping scaly RHIZOMES","indiangrass":"Tuft / short rhizomes","johnsongrass":"Thick aggressive rhizomes","witchgrass":"Annual no rhizomes"}
       ],
       "caution":"Do not teach 'hairs equal switchgrass'; get panicle and basal habit. NC State source closeup photo licensing separately checked; mobile arrow precision needs final review."
    })
    if not isinstance(g.get("visual_comparison"),dict):
        g["visual_comparison"]={"title":"Panicum — field photo key","items":[]}
    g["visual_comparison"]["items"]=[x for x in g["visual_comparison"].get("items",[]) if x.get("image_url")!=panel["image_url"]]+[panel]
    g["visual_comparison"]["title"]="Panicum — first inspect the COLLAR, then the panicle and base"
    g["visual_comparison"]["subtitle"]="One new exact-source switchgrass white-hair collar close-up CC BY 4.0 with two organ arrows; genus-level differentiation now teaches hairy-annual witchgrass and tufted Hall's/Kleingrass as well."
    g["quick_key"][0]["if"]="tall rhizomatous perennial + HUGE airy pyramid panicle + patch of WHITE COLLAR HAIRS backed by short membrane"
    g["photo_handoffs"].append("New switchgrass collar photo is physically installed; rhizomes, attached ovate spikelet and matched Hall's / witchgrass collar photos remain priority.")
    g["curation_status"].update({"version":"1.2-switchgrass-collar-plus-genus-20261021","last_reviewed":"2026-10-21","switchgrass_collar":"one NC State Andrey Zharkikh CC BY 4.0 JPEG physically installed; two arrows; mobile QA pending"})
    # Append source metadata and final files only after source+bytes validation.
    csvfile=FOLDER/"image-sources.csv"
    with csvfile.open(newline="",encoding="utf-8-sig") as h:
       reader=csv.DictReader(h);cols=list(reader.fieldnames or []);rows=list(reader)
    row={"file_name":pathlib.Path(SAVED).name,"role":record["role"],"creator":record["creator"],"license":record["license"],"source_page":PAGE,
         "direct_image_url":"https://s3.amazonaws.com/eit-planttoolbox-prod/media/images/"+FILENAME,
         "study_use":"yes","public_reuse":"yes","license_url":LICENSE,
         "source_context":"NC State photo-specific 'Leaf blade attachment' Andrey Zharkikh CC BY 4.0, downloaded photo verified and EXIF removed; JSON carries new two arrows"}
    for k in row:
       if k not in cols:cols.append(k)
    rows.append(row)
    with csvfile.open("w",newline="",encoding="utf-8") as h:
       writer=csv.DictWriter(h,fieldnames=cols,lineterminator="\n");writer.writeheader();writer.writerows(rows)
    with (FOLDER/"SOURCES.txt").open("a",encoding="utf-8") as h:
       h.write("\n2026-10-21 EXACT SWITCHGRASS COLLAR PHOTO\nNC State Extension Plant Toolbox "+PAGE+"\n")
       h.write("Image-specific Leaf blade attachment photograph by Andrey Zharkikh, CC BY 4.0 "+LICENSE+"\n")
       h.write("Photo locally saved: "+SAVED+"; JPEG EXIF removed; two arrow coordinates in visual_comparison, mobile QA pending.\n")
       h.write("Additional scientific morphology: https://www.srs.fs.usda.gov/pubs/rp/rp_so210.pdf and https://rangeplants.tamu.edu/plant/switchgrass/\n")
    SPEC.write_text(json.dumps(s,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    GENUS.write_text(json.dumps(g,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"result":"installed", "species":s["id"],"photos":len(s["images"]),
      "real_new_photos":1,"diagnostic_arrows":2,"genus_photo_panels":len(g["visual_comparison"]["items"]),
      "license":"CC BY 4.0","creator":"Andrey Zharkikh","native_status_unchanged":s["project_inclusion"]["target_zone_status"]},indent=2))

if __name__=="__main__":main()
