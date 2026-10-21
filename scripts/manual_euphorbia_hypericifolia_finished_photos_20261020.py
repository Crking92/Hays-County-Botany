#!/usr/bin/env python3
"""Install four photo-specific CC BY 4.0 Wikimedia Commons E. hypericifolia views.

Fail closed on photo rights, exact taxon filenames, actual image bytes and concurrent
canonical changes. Don't invent diagnostic arrows before reviewing stored pixels.
"""
from pathlib import Path
from urllib.parse import quote
import csv, hashlib, io, json, requests, time
from PIL import Image, ImageOps

ROOT=Path("content/taxa/Euphorbiaceae/Euphorbia/euphorbia-hypericifolia")
CARD=ROOT/"species.json"
CSV=ROOT/"image-sources.csv"
REPORT=Path("reports/euphorbia-hypericifolia-m108t-fourphoto-20261020.json")
SOURCES=[
 ("Habit of Euphorbia hypericifolia in Ishigaki, Okinawa.jpg","images/02-m108t-whole-habit.jpg","Overall habit in the field; exact root/crown not necessarily resolved"),
 ("Inflorescece of Euphorbia hypericifolia in Ishigaki, Okinawa 1.jpg","images/03-m108t-dense-cyathia.jpg","Terminal/axillary dense head-like cyathium glomerules; identify flower cluster position"),
 ("Stipule of Euphorbia hypericifolia in Ishigaki, Okinawa 1.jpg","images/04-m108t-stipule-a.jpg","Opposite leaf node with spreading triangular connate stipules; arrow location awaits manual JPEG review"),
 ("Stipule of Euphorbia hypericifolia in Ishigaki, Okinawa 2.jpg","images/05-m108t-stipule-b.jpg","Second angle of true stipules; fusion architecture must be visually confirmed before arrow claims")
]
LIC="https://creativecommons.org/licenses/by/4.0/"
SRC="https://commons.wikimedia.org/wiki/File:"
API="https://commons.wikimedia.org/w/api.php"

def fetch(session, name):
    result=session.get(API,params={"action":"query","format":"json","formatversion":"2","prop":"imageinfo",
        "iiprop":"url|extmetadata","iiurlwidth":"1700","titles":"File:"+name},timeout=60)
    result.raise_for_status()
    pages=result.json()["query"]["pages"]
    assert len(pages)==1 and "missing" not in pages[0],name
    info=pages[0]["imageinfo"][0]
    license=info["extmetadata"]["LicenseShortName"]["value"]
    artist=info["extmetadata"].get("Artist",{}).get("value","")
    assert "CC BY 4.0" in license and "M108t" in artist, (name, license, artist)
    imageurl=info.get("thumburl") or info.get("url")
    assert imageurl.startswith("https://")
    res=session.get(imageurl,timeout=90)
    res.raise_for_status()
    data=res.content
    assert 15000<len(data)<16000000,(name,len(data))
    with Image.open(io.BytesIO(data)) as im:
        im.load()
        assert im.format in ("JPEG","PNG"),(name,im.format)
        original=list(im.size)
        assert min(im.size)>=650,(name,original)
        rendered=ImageOps.exif_transpose(im).convert("RGB")
    rendered.thumbnail((1700,1700),Image.Resampling.LANCZOS)
    buffer=io.BytesIO()
    rendered.save(buffer,format="JPEG",quality=90,optimize=True)
    out=buffer.getvalue()
    with Image.open(io.BytesIO(out)) as check:
        check.verify()
    assert len(out)>18000,(name,len(out))
    return out,{"source_image_sha256":hashlib.sha256(data).hexdigest(),
      "original_image_dimensions":original,"saved_image_dimensions":list(rendered.size),
      "downloaded_from":imageurl,"source_license_on_commons":license}

def main():
    obj=json.loads(CARD.read_text(encoding="utf-8"))
    assert obj["id"]=="euphorbia-hypericifolia"
    assert obj["scientific_name"]=="Euphorbia hypericifolia"
    assert len(obj["images"]) in (1,5)
    target_files={rel for _,rel,_ in SOURCES}
    if len(obj["images"])==5:
        assert target_files.issubset({x["file"] for x in obj["images"]})
        assert all((ROOT/x["file"]).is_file() for x in obj["images"])
        print("Four Commons photos already installed; no-op")
        return
    initial=obj["images"][0]
    assert initial["file"]=="images/inat-338600902.jpg" and initial["license"]=="CC BY"
    assert (ROOT/initial["file"]).is_file()
    session=requests.Session()
    session.headers["User-Agent"]="HaysBotanyCrewVisualLearner/1.0 (https://github.com/Crking92/Hays-County-Botany)"
    fetched=[]
    for name,rel,role in SOURCES:
        assert "Diamond" not in name and "hyssopifolia" not in name.lower()
        assert not (ROOT/rel).exists(),rel
        last=None
        for attempt in range(3):
            try:
                blob,meta=fetch(session,name)
                fetched.append((name,rel,role,blob,meta))
                break
            except Exception as e:
                last=str(e)
                if attempt==2:raise RuntimeError(f"Couldn't verify photo {name}: {last}")
                time.sleep(3)
    for name,rel,role,blob,meta in fetched:
        (ROOT/rel).write_bytes(blob)
        item={"file":rel,"role":role,"creator":"M108t","license":"CC BY 4.0","license_url":LIC,
          "source_page":SRC+quote(name.replace(" ","_"),safe="._-(),"),
          "source_platform":"Wikimedia Commons exact-name wild-type photographic evidence",
          "study_use":"yes","public_reuse":"yes",
          "modifications":"Downscaled max 1700 px and converted to metadata-stripped JPEG for public educational website; original composition unchanged.",
          "photo_review":"Source name, author and image-level CC BY 4.0 license verified by live Wikimedia Commons API. Photograph decoded, size and saved bytes checked; STRUCTURE ARROWS still require manual review of saved JPEG.",
          "anatomy_arrows":[],
          **meta}
        obj["images"].append(item)
    assert len(obj["images"])==5
    obj["authority"]="L."
    obj["entry_type"]="provisional_species"
    obj["synonyms"]=["Chamaesyce hypericifolia (L.) Millsp.","Chamaesyce glomerifera Millsp.","Euphorbia glomerifera (Millsp.) L.C.Wheeler"]
    obj["taxonomic_note"]="Accepted Euphorbia hypericifolia L. in POWO and Flora of North America. Not to be confused with E. hyssopifolia or the historically misapplied E. nutans complex; do not substitute garden cultivar 'Diamond Frost' photographs for wild plants."
    obj["look_here_first"]="FIRST FIND THE DENSE LITTLE CLUSTERS: E. hypericifolia has tight axillary and terminal, headlike glomerules of many tiny cyathia on short condensed axes, usually subtended by drastically reduced bractlike leaves. Its stems and leaves are GLABROUS, opposite oblong/oblanceolate leaves are unequal at the base with finely serrate edges, and the node has CONNATE DELTATE scale-like stipules about 1.5-2.2 mm long. Capsules are smooth/glabrous. Compare nutans: often short-curly stem hairs and usually solitary or small leafy groups of cyathia, rather than dense near-leafless clusters. Compare hyssopifolia: short usually lacerate stipules 0.5-1 mm and cyathia solitary or in small cymes; both can look nearly hairless distally. Verify seeds when available: hypericifolia has shallow irregular depressions and low ridges, hyssopifolia commonly has 2-3 PROMINENT transverse ribs. Current photos have NOT yet been assessed for calibrated stipule length or seed micromorphology.";
    obj["morphology_keys"]={
      "family_pattern":"Euphorbiaceae; Euphorbia sect. Anisophyllum: opposite unequal leaves, milky latex, cyathium (tiny special flower head), dry three-lobed capsule.",
      "habit":"Annual taprooted herb; ascending/erect, 15–50 cm; shoots glabrous. New habit photograph is a potential example, not calibrated proof of height.",
      "leaves":"Opposite, obliquely oblong to oblanceolate, 10–35 × 7–15 mm, asymmetric base, margins serrate/serrulate especially distally, glabrous; petioles 1–3 mm.",
      "stipules":"Paired stipules at nodes fused into deltoid, usually entire scales (occasionally fringed apically), 1.5–2.2 mm, glabrous; often spreading away from stem. Need both-side node photo and scale before arrow labeling exact fusion.",
      "inflorescence":"Cyathia crowded in dense, axillary or terminal headlike clusters (glomerules), with much-reduced bractlike leaves, NOT the leafy loosely spaced small cymes of E. nutans or E. hyssopifolia.",
      "cyathium":"Four yellow-green/brown, often stipitate glands; white-pink petal-like gland appendages may be inconspicuous or absent from smaller glands. These are not true petals.",
      "capsule":"Flattened-globose, smooth glabrous, approximately 1.3–1.4 × 1.1–1.5 mm.",
      "seed":"About 0.9–1.1 × 0.5 mm; pale brown underneath a thin white mucilage coat; low smooth ridges and shallow irregular pits/depressions, not the 2–3 conspicuous transverse bars often seen in E. hyssopifolia.",
      "best_field_traits":["dense terminal and axillary glomerules of many tiny cyathia","small, highly reduced bracts at cyathium heads","hairless stems and leaf surfaces (verify at basal node, not only at tips)","fused triangular nodal stipules about 1.5–2.2 mm","asymmetric opposite oblong leaves with finely serrate margins","smooth three-lobed capsules","seed sculpture if mature, with scale and confirmed exact species"]
    }
    obj["comparisons"]={
      "confused_with":["Euphorbia hyssopifolia","Euphorbia nutans","Euphorbia villifera"],
      "key_distinctions":"Hypericifolia has glabrous stems AND dense head-like cyathia clusters with reduced bracts plus larger fused triangular stipules; hyssopifolia has generally smaller/leafier clusters and 0.5-1 mm lacerate stipules; nutans usually bears crinkled stem hairs and less condensed leafy cymes. Smooth capsules alone do not separate these species.",
      "field_matrix":[
       {"character":"Cyathia arrangement","hypericifolia":"dense globose glomerules on short axes with reduced bracts","nutans":"solitary or small leafy terminal cymes","hyssopifolia":"solitary or small leafy cymes, sometimes congested"},
       {"character":"Stems","hypericifolia":"glabrous throughout","nutans":"some short incurved/crinkled hairs usually present","hyssopifolia":"often pilose below, potentially glabrous at tips"},
       {"character":"Stipules","hypericifolia":"fused deltoid scales, 1.5–2.2 mm","nutans":"irregularly toothed/fringed scales; variable basal fusion","hyssopifolia":"fused, irregularly lacerate scales 0.5–1 mm"},
       {"character":"Seed sculpture","hypericifolia":"shallow irregular depressions/low smooth ridges","nutans":"fine irregular wrinkles, occasionally weak cross-ridges","hyssopifolia":"2–3 usually prominent transverse ridges or coarse pits"},
       {"character":"Capsule","hypericifolia":"glabrous depressed-globose","nutans":"glabrous ovoid","hyssopifolia":"glabrous depressed-ovoid"}
      ]
    }
    obj["field_photo_quickcheck"]={
      "heading":"Where to look first: condensed clusters, then stipules",
      "steps":["1. Photograph the full shoot including ground attachment and a ruler if possible.","2. Look for DENSE head-like clusters of many cyathia, often with reduced bracts rather than ordinary leafy flowering branches.","3. Check an opposite leaf pair for oblique unequal bases and fine marginal teeth.","4. At 10–20×, check BOTH sides of node for fused triangular stipules; don't mistake a tiny leaf bud for a stipule.","5. Inspect basal stem for hairs (nutans/hyssopifolia can be hairy below).","6. Confirm smooth capsule, and if possible mature seed with 1mm scale."],
      "warning":"The original single inaturalist image and newly sourced Wikimedia photos do not yet prove every microscopic claim. Exact stipule fusion, whole-plant measurement and seed sculpture require pixel-level manual arrow/image review. No cultivar example as evidence."
    }
    obj["field_id_finalization"]={
      "stage":"PASS_IN_PROGRESS",
      "field_training_status":"TEXT_DIAGNOSTICS_READY; FOUR_NEW_LICENSED_PHOTOS_INSTALLED_AWAITING_PIXEL_QA",
      "date":"2026-10-20","canonical_photo_count":5,
      "photographic_arrow_status":"Not yet annotated; new photographs need on-screen original-image pixel inspection before arrows.",
      "remaining":["Visually audit saved photos and mark only actual visible morphology","Photograph/verify whole plant and scale if unavailable","Confirm conjoined triangular stipules at true node vs bracts under loupe","True mature seeds with scale, specific shallow ridges/pits","Preserve native-county research as previously unreviewed"]
    }
    obj["curation_status"].update({"taxonomy_reviewed":True,"morphology_reviewed":True,
      "lookalikes_reviewed":True,"visual_reviewed":False,"photo_metadata_count":5,"photo_files_present":5,
      "field_status":"FIELD_READY_TEXT; VISUAL_MACRO_PENDING"})
    obj["learner_visual_status"].update({"image_count":5,"status":"field_ready_photo_gaps",
      "note":"Original CC BY iNat face plus four exact-name personally created CC BY 4.0 Commons photos (habit, inflorescence, two stipule views); physically saved. Anatomical arrows and seed macro still pending saved-pixel verification."})
    obj["photo_note"]="Original CC BY iNaturalist face preserved, plus four individually license-verified CC BY 4.0 Commons actual images; no cultivars. New photo anatomy requires manual inspection before pointer labels; seeds remain a gap."
    obj["science_reference_links"]=[
       "https://efloras.org/florataxon.aspx?flora_id=1&taxon_id=242321438",
       "https://www.efloras.org/florataxon.aspx?flora_id=1&taxon_id=242321439",
       "https://efloras.org/florataxon.aspx?flora_id=1&taxon_id=242427660",
       "https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:101671-2"
    ]
    CARD.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    with CSV.open(newline="",encoding="utf-8") as f:
        reader=csv.DictReader(f);columns=reader.fieldnames;rows=list(reader)
    assert len(rows)==1
    for name,rel,role,blob,meta in fetched:
        cols={k:"" for k in columns}
        cols.update({"file_name":Path(rel).name,"role":role,"creator":"M108t","license":"CC BY 4.0",
          "source_page":SRC+quote(name.replace(" ","_"),safe="._-(),"),
          "direct_url":meta["downloaded_from"],"study_use":"Botanical education","public_reuse":"yes"})
        rows.append(cols)
    with CSV.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=columns,lineterminator="\n");writer.writeheader();writer.writerows(rows)
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps({
       "species":"Euphorbia hypericifolia","date":"2026-10-20",
       "photos_installed":[{"file":rel,"commons_title":name,"creator":"M108t","license":"CC BY 4.0",**meta}
           for name,rel,role,blob,meta in fetched],
       "pixel_checks":"Decoded and checked actual new JPEG bytes; diagnostic arrow positions pending manual visual inspection",
       "previous_licensed_photo_retained":True,"cultivars_excluded":True,
       "range_status":"Not reviewed as county native, unchanged"
    },indent=2)+"\n",encoding="utf-8")
    print("PASS: 4 new physical exact-name images with CC BY 4.0 rights; total 5, no arrow fabrication.")
if __name__=="__main__":main()
