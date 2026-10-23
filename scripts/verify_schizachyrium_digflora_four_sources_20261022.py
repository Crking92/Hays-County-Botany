#!/usr/bin/env python3
"""Verify Bob Harms DigFlora/KR Schizachyrium original JPEGs, and write
only factual reproducibility/source/rights JSON. This intentionally DOES NOT
write/rehost copyrighted DigFlora photographs in the public repository.
The author's separate Selected Monocots educational-use policy is NOT a
verified blanket license for DigFlora/KR originals.
"""
import hashlib,io,json,time
from datetime import date
from pathlib import Path
import requests
from PIL import Image

ROOT=Path(".")
DEST=ROOT/"reports/schizachyrium-digflora-four-source-verification-20261022.json"
SOURCE_PAGE="https://w3.biosci.utexas.edu/prc/DigFlora/KR/SCSC.html"
DIRECT_BASE="https://w3.biosci.utexas.edu/prc/DigFlora/KR/0-BOISS4Web/"
TERMS_SPECIFIC="https://w3.biosci.utexas.edu/prc/Monocots/"
FNA="https://openherbarium.org/portal/taxa/index.php?clid=26&taxauthid=1&tid=239979"
KEW="https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:420956-1/general-information"
SOURCES=[
("SCSC-L-Shth-Nod.JPG","true_ligule_and_keel",
 "Four side-by-side photographic features A/B/C with author-designated L at true blade/sheath ligule, plus a real black/white metric scale",
 "Source author L marks membrane in situ, but composite is NOT a demonstrated completely unfolded free membranous rim or calibrated 0.5-mm free-tip closeup"),
("SCSC-disart-w-red.JPG","attached_A_F_P_spikelet_pairs",
 "An intact source-authored raceme axis, disarticulation positions (red arrows), A axis-segment, F awned fertile sessile spikelet, P pedicellate companion, plus metric scale",
 "Image confirms the intact paired anatomy of the illustrated source material; it does NOT prove that separately depicted dissected pieces and rooted tuft are this same physical individual"),
("SCSC-spkcut.JPG","sessile_spikelet_dissection",
 "Different separated original sessile spikelet bracts g1/g2 (glumes), lf fertile lemma, ls sterile lemma, ps sterile palea with photographed millimeter ticks",
 "Correctly identifies source-authored detached organs, NOT one completely assembled spikelet, nor documented same exact spikelet from SCSC-disart photo"),
("SCSC-04-P-bX.JPG","actual_rooted_tuft",
 "The actual author-labelled northern-Hays little-bluestem turf bunch with narrow culms, enclosing lower sheath bases and roots at bottom of image",
 "Real attached root hairs/root strands and basal shoots ARE visible; no simultaneously attached mature flowering head or provenance tying it to the dissected photographed pair"),
]
def download(sess,url):
    errs=[]
    for attempt in range(2):
        try:
            resp=sess.get(url,timeout=40,headers={"Accept":"image/jpeg,image/*"})
            resp.raise_for_status()
            binary=resp.content
            if not 9000<len(binary)<8_000_000 or not binary.startswith(b"\xff\xd8\xff"):
                raise ValueError("Not a real usable source JPEG response")
            with Image.open(io.BytesIO(binary)) as im:
                im.load()
                if im.format!="JPEG" or min(im.size)<200 or max(im.size)>7000 or im.size[0]*im.size[1]<60000:
                    raise ValueError("Unexpected original taxon-photo size: "+repr(im.size))
                w,h=im.size
            return {"sha256":hashlib.sha256(binary).hexdigest(),"width_px":w,"height_px":h,
                    "jpeg_bytes":len(binary),"retrieved_from":resp.url,
                    "file_signature":"Original JPEG decoded by Pillow, SHA256 computed, no file saved"}
        except Exception as exc:
            errs.append(str(type(exc).__name__)+": "+str(exc)[:200])
            if getattr(getattr(exc,"response",None),"status_code",None)==429: break
            time.sleep(attempt+2)
    raise RuntimeError("Original image unable to be verified; no source inventory published: "+url+" "+repr(errs))
def main():
    spath=ROOT/"content/taxa/Poaceae/Schizachyrium/schizachyrium-scoparium/species.json"
    s=json.loads(spath.read_text(encoding="utf8"))
    if s["id"]!="schizachyrium-scoparium":
        raise RuntimeError("Canonical identity changed, stop")
    old=s.get("field_id_finish_pass",{}).get("last_mile_external_evidence_search_20261022",{})
    have=[x.get("exact_photo") for x in old.get("identified_source_material",[])]
    sess=requests.Session()
    sess.headers["User-Agent"]="HaysCountyBotanyEducationalSourceVerification/1.0 github.com/Crking92/Hays-County-Botany"
    verified=[]
    for name,role,facts,limits in SOURCES:
        url=DIRECT_BASE+name
        if url not in have:raise RuntimeError("Exact original not already claimed by source researcher: "+url)
        result=download(sess,url)
        verified.append({"file_name":name,"source_role":role,"source_page":SOURCE_PAGE,
            "original_photo_url":url,"photographer":"Bob Harms",
            "source_botanical_concept":"Schizachyrium scoparium (Michx.) Nash, local northern Hays form according to author",
            "anatomy_from_author_caption":facts,"evidential_limits":limits,
            "image_permission_status":"COPYRIGHTED RESEARCH REFERENCE — exact DigFlora/KR website has no confirmed public republication license; LINK ONLY",
            "publication_decision":"Do not commit the JPEG to repository, embed full image in web page, or transfer the educational-use notice from separate Selected Monocots",
            **result})
        print("EXACT SOURCE PHOTO PROVEN",name,result["width_px"],result["height_px"],result["sha256"][:16],flush=True)
    assert len(verified)==4
    out={
       "result":"FOUR_REAL_NORTH_HAYS_DIGFLORA_SCHIZACHYRIUM_JPEGS_ORIGINALLY_VERIFIED_METADATA_ONLY",
       "source_date":"2026-10-22",
       "scientific_name":"Schizachyrium scoparium (Michx.) Nash",
       "author_and_site":"Bob Harms / University of Texas Plant Resources Center, DigFlora KR Schizachyrium (north Hays populations)",
       "source_landing_page":SOURCE_PAGE,
       "rights_specific":"Copyright of four distinct original DigFlora/KR photos not affirmatively cleared for public redistribution; author photo and taxon credit verified.",
       "rights_nuance":"https://w3.biosci.utexas.edu/prc/Monocots/ expressly permits scientific and educational reuse of Selected Monocots images, but is limited by wording to that separately curated subset. It is NOT a blanket rights grant for these DigFlora/KR original files.",
       "scientific_comparison":{
          "accepted_name":KEW,
          "FNA_review":FNA,
          "ligule_variation":"FNA 0.5–2 mm; Kew GrassBase 1–3 mm eciliate membrane; another SDSU educational source describes fringed membrane less than 2.5 mm. Do not demand hair-fringed membrane in every same-species plant or state 0.5–2.5mm absolute.",
          "spikelet_pairs":"Author A/F/P and FNA agree that pairs consist of fertile sessile + usually reduced but variably developed sterile or staminate pedicellate spikelets. Upper spikelet/floret structures must not be incorrectly conflated.",
          "reproductive_caution":"The sessile spikelet contains upper bisexual fertile floret and lower sterile floret, enclosed by two glumes; detached glumes/lemmas/palea on author image are separately placed parts, not visually joined from one voucher.",
          "hays_plant_scope":"North Hays local source identity strongly documented; no single collection number demonstrates that photographs from root, ligule, attached pair, dissection all come from same plant.",
          "invasive_split":"Little bluestem has mostly separate short leaf-branch racemes; Texas KR bluestem has several longer narrow fingers from terminal cluster. Not a single-node-hair or color-only split."
       },
       "original_photograph_records":verified,
       "physical_photo_jpegs_added_to_public_git":0,
       "media_location":"Original links and SHA/dimensions saved in this report, original JPEG bytes verified ephemerally in runner and discarded",
       "remaining_final_photo_hold":["Unfurled membrane free ligule tip photo with actual calibrated millimeter ruler","Matched one-plant intact A/F/P spikelet + dissection photo to comparable scale","Traceable rooted crown-to-flowering branch-to-mature-pair Hays specimen/source accession"],
       "current_status":"FIELD_READY_PHOTO_GAPS; fully legitimate botanical source links FOUND, COPYRIGHT/one-voucher link HELD"
    }
    DEST.parent.mkdir(parents=True,exist_ok=True)
    DEST.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    print("PASS: four exact originals decoded and hashed, zero third-party JPEG files rehosted",flush=True)
if __name__=="__main__":main()
