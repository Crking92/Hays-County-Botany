#!/usr/bin/env python3
"""Lane 2: physically install exact Setaria scheelei Bob Harms scaled inner collar."""
from pathlib import Path
from urllib.request import Request, urlopen
from PIL import Image, ImageOps
import hashlib, io, json, datetime

R=Path(__file__).resolve().parents[1]
B=R/"content/taxa/Poaceae/Setaria/setaria-scheelei"
CARD=B/"species.json"
SCORE=R/"reports/lane2-six-role-photo-score-20261027.json"
REPORT=R/"reports/lane2-scheelei-harms-scaled-ligule-20261027.json"
MARK=R/"workflow/field-id-publication/lane2-scheelei-scaled-ligule-20261027.json"
HOME="https://w3.biosci.utexas.edu/prc/Monocots/"
PAGE=HOME+"GrassHTML/data/pages/SESC2-L.html"
SOURCE=HOME+"GrassHTML/data/images/SESC2-L.jpg"
FN="bob-harms-scheelei-sesc2-l-scaled-inner-ligule.jpg"
REL="content/taxa/Poaceae/Setaria/setaria-scheelei/images/"+FN
DEST=R/REL

def get(url):
    q=Request(url,headers={"User-Agent":"Mozilla/5.0 HaysCountyBotanyEducationalLearner/1.0"})
    with urlopen(q,timeout=45) as f:return f.read(8_000_001)
def writejson(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

def main():
    j=json.loads(CARD.read_text())
    assert j["scientific_name"]=="Setaria scheelei"
    im=j["images"]
    panels=j["visual_comparison"]["items"]
    if any(x.get("file")=="images/"+FN for x in im):
        assert DEST.exists() and any(x.get("image_url")==REL for x in panels)
        print("ALREADY_ARCHIVED, no score inflation")
        return

    rights=get(HOME).decode("utf-8",errors="replace").lower()
    if "free for scientific and educational uses" not in rights or "bob harms" not in rights:
        raise RuntimeError("Rights landing page no longer states credited educational-use permission")
    landing=get(PAGE).decode("utf-8",errors="replace").lower()
    if "setaria scheelei" not in landing or "bob harms" not in landing:
        raise RuntimeError("Source is no longer attributed to the exact taxon and creator")
    raw=get(SOURCE)
    assert len(raw)>15000 and len(raw)<8_000_000
    with Image.open(io.BytesIO(raw)) as x:
        assert x.format=="JPEG"
        y=ImageOps.exif_transpose(x).convert("RGB")
        w,h=y.size
        assert w>=680 and h>=350,(w,h)
        out=io.BytesIO()
        y.save(out,format="JPEG",quality=95,optimize=True,subsampling=0)
    data=out.getvalue()
    DEST.parent.mkdir(parents=True,exist_ok=True)
    if DEST.exists():raise RuntimeError("Filename exists but card is missing: stop, reconcile manually")
    DEST.write_bytes(data)
    dig=hashlib.sha256(data).hexdigest()
    rights_meta={
        "creator":"Bob Harms",
        "license":"© Bob Harms — scientific/educational use with attribution (NOT Creative Commons)",
        "source_page":PAGE,
        "source_image":SOURCE,
        "license_url":HOME,
        "site_specific_public_permission":"BOB_HARMS_SELECTED_MONOCOTS_EDU_WITH_CREDIT_20261022",
        "public_reuse":"Credited scientific/educational use permitted by the photographer's Selected Central Texas Monocots collection; standalone learner remains noncommercial",
        "source_taxon_name":"Setaria scheelei",
        "modifications":"EXIF/GPS removed and re-encoded JPEG; non-destructive learner browser overlay arrows",
        "image_sha256":dig,
        "source_pixel_dimensions":[w,h]
    }
    im.append({"file":"images/"+FN,"role":"Verified true inner blade/sheath junction with ciliate/hairy ligule exposed, shown beside original millimeter scale",**rights_meta})
    item={
       "label":"TRUE LIGULE · actual Scheele's bristlegrass inner collar and ruler",
       "scientific_name":"Setaria scheelei",
       "image_url":REL,
       "image_fit":"contain",
       "image_role":"True inner collar/ligule exposed by peeling sheath, compared with intact outer sheath; real millimeter scale",
       "caption":"Bob Harms photographed three orientations of Scheele's bristlegrass blade-to-sheath junction: intact exterior on the left, partly opened at center, and peeled inner ciliate/hairy ligule at right. The vertical physical scale is in millimeters. Identify the short inner fringe, not the longer hairs on the outside of the sheath. This is not a root/rhizome or spikelet dissection.",
       "why_it_matters":"Closes the previously missing true INNER ligule photographic role; makes visible the actual anatomical distinction from outer sheath hairs. Do not infer underground growth from this picture.",
       "markers":[
           {"label":"Inner ciliate ligule — opened sheath","label_x":5,"label_y":12,"target_x":79,"target_y":47},
           {"label":"Original millimeter scale","label_x":59,"label_y":87,"target_x":67,"target_y":47}
       ],
       "photo_status":"Original photographed exact species; botanical structure and scale visually inspected before annotation. Attribution and credited educational reuse verified at source collection homepage.",
       **rights_meta
    }
    insert=next((i for i,p in enumerate(panels) if p.get("scientific_name")!="Setaria scheelei"),len(panels))
    panels.insert(insert,item)
    j.setdefault("curation_status",{})["lane2_harms_true_ligule_20261027"]={
       "state":"FIELD_READY_PHOTO_GAPS",
       "source":"Selected Central Texas Monocots, Bob Harms SESC2-L.jpg",
       "public_educational_rights_checked":True,
       "new_species_jpeg":1,"new_visible_annotations":2,
       "local_exact_species_photos":len(im),
       "six_role_score":"4.5/6, 75% provisional photographic completeness",
       "newly_confirmed_role":"true_collar_ligule_sheath: 0.5 -> 1",
       "still_missing":["exposed connected roots/rhizomes","measured dissection of glumes, lemmas, and attached bristle base"],
       "github_pages":"Not verified until guarded release"
    }
    j["photo_note"]=j.get("photo_note","")+"\n2026-10-27 Lane2: added original Bob Harms Selected Monocots exact Setaria scheelei scaled INNER ciliate ligule photograph SESC2-L; 2 gross anatomical overlays, attribution and noncommercial educational-use conditions. True collar photo upgraded half to full role, no roots or bristle dissection claimed."
    writejson(CARD,j)

    s=json.loads(SCORE.read_text())
    r=next(x for x in s["records"] if x["canonical_id"]=="setaria-scheelei")
    assert r["roles"]["true_collar_ligule_sheath"]==0.5
    assert r["after_total"]==4
    r["roles"]["true_collar_ligule_sheath"]=1
    r["after_total"]=4.5
    r["after_percentage"]=75
    r["change_percentage_points"]=r["after_percentage"]-r["before_percentage"]
    r["below_70"]=False
    r["new_source_report"]="reports/lane2-scheelei-harms-scaled-ligule-20261027.json"
    r["gaps_warning"]="True ligule now photographed with real scale by Bob Harms; attached rooted crown/rhizomes NOT photographed, and spikelet/bristle attachment at mm scale still partial."
    allr=s["records"]
    s["summary"]["mean_after_percent"]=round(sum(x["after_total"] for x in allr)/len(allr)/6*100,1)
    s["summary"]["at_or_above_70_count"]=sum(x["after_percentage"]>=70 for x in allr)
    s["summary"]["below_70_count"]=sum(x["after_percentage"]<70 for x in allr)
    s["summary"]["below_70_species"]=[x["canonical_id"] for x in allr if x["after_percentage"]<70]
    dist={}
    for v in allr:
        k=f'{v["after_total"]:.1f}/6'
        dist[k]=dist.get(k,0)+1
    s["summary"]["distribution"]=dist
    s["summary"]["latest_scheele_true_ligule_20261027"]={"photo_added":1,"arrows_added":2,"rights":"Bob Harms credited educational use (not CC)","role_gain":0.5,"pages":"pending controlled QA"}
    writejson(SCORE,s)
    report={
        "species":"Setaria scheelei","date":"2026-10-27","status":"FIELD_READY_PHOTO_GAPS",
        "new_actual_photo":REL,"source_page":PAGE,"source_image":SOURCE,"rights_evidence":HOME,
        "rights":"Photographer's Selected Central Texas Monocots collection says freely usable for properly credited scientific and educational use. NOT Creative Commons.",
        "creator":"Bob Harms","source_original_sha256":hashlib.sha256(raw).hexdigest(),
        "local_sha256":dig,"dimensions":[w,h],"bytes":len(data),
        "new_annotation_arrows":2,"visual_claim":"inner ciliate/hairy ligule and actual mm scale, NOT connected roots",
        "previous_roles":4.0,"new_roles":4.5,"percent":75,
        "photo_files_stored":len(im),"remaining":["connected rooted base","calibrated separated fertile glume/lemma and exact bristle insertion"],
        "pages":"release pending, do not claim deployed"}
    writejson(REPORT,report)
    writejson(MARK,{"type":"manual_field_id_publication","date":"2026-10-27",
        "species":"Setaria scheelei","title":"Lane 2 exact Scheele Bob Harms scale-verified inner collar photo",
        "source_report":str(REPORT.relative_to(R)),"photo":REL,
        "public_use":"Bob Harms science/education with credit per Selected Central Texas Monocots, not CC",
        "status":"FIELD_READY_PHOTO_GAPS","pages":"verify controlled rights-filtered release success"})
    print("SUCCESS",json.dumps({"species":"Setaria scheelei","photos":len(im),"score":s["summary"]["mean_after_percent"],"scheele_percent":75,"sha256":dig,"dimension":[w,h]}))
if __name__=="__main__":main()
