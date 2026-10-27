#!/usr/bin/env python3
"""Lane 2: install real Bob Harms plains lovegrass anatomy images, not stock habit photos.
Exact artist/collection, original page and JPEG bytes validated before archival.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageOps
import io,json,hashlib

# The photographed hairy collar counts ONLY as 0.5 until the 0.3–0.5 mm inner ligule fringe is individually resolved.
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"content/taxa/Poaceae/Eragrostis/eragrostis-intermedia"
CARD=BASE/"species.json"
SCORE=ROOT/"reports/lane2-six-role-photo-score-20261027.json"
REPORT=ROOT/"reports/lane2-eragrostis-intermedia-harms-anatomy-20261027.json"
MARK=ROOT/"workflow/field-id-publication/lane2-eragrostis-intermedia-harms-anatomy-20261027.json"
SITE="https://w3.biosci.utexas.edu/prc/Monocots/"
URLBASE=SITE+"GrassHTML/data/"
SPEC=[
  dict(code="L",fn="bob-harms-erin-l-collar-hairy-sheath.jpg",title="REAL COLLAR · hairy sheath and scaled blade junction",
    role="True blade/sheath region and external ciliate collar photographed at multiple angles; the 0.3–0.5-mm INNER ligule fringe cannot be isolated confidently",
    caption="Bob Harms photographed plains lovegrass blade/sheath junctions and hairy collars next to an original millimeter scale. This illustrates where to find the ligule. The tiny innermost fringe is not unequivocally isolated from adjacent longer collar hairs; do NOT teach this as measured full ligule detail.",
    arrows=[dict(label="Visible hairy collar at sheath opening",label_x=35,label_y=75,target_x=19,target_y=66),dict(label="Original millimeter scale",label_x=29,label_y=12,target_x=26,target_y=24)]),
  dict(code="z",fn="bob-harms-erin-z-connected-crown-fibrous-roots.jpg",title="REAL ROOTS · connected basal crown and roots",
    role="True collected plant base showing multiple connected culm bases and fibrous roots, but no confirmed elongated underground rhizome",
    caption="The original collected plant base of Eragrostis intermedia shows many tillers attached to the compact crown and long fine roots. Roots are genuine, but the image does not settle whether short knotty rhizomes sometimes occur: FNA/2015 Hill Country treatment says absent, Williamson County flora describes rhizomes.",
    arrows=[dict(label="Connected basal tiller crown",label_x=6,label_y=52,target_x=54,target_y=67),dict(label="Visible fibrous roots",label_x=6,label_y=88,target_x=40,target_y=82)]),
  dict(code="9",fn="bob-harms-erin-9-actual-scaled-mature-spikelets.jpg",title="REAL MACRO · mature spikelets with source scale",
    role="Actual mature spikelets and broken units at more than one scale, source image includes millimeter ruler",
    caption="Source-identified, physically scaled plains lovegrass spikelets with multiple overlapping florets and separate small bracts. Not a generic lovegrass image. Use the pictured original scale; the tiny glume veins are not necessarily resolved in every unit.",
    arrows=[dict(label="Mature overlapping-floret spikelet",label_x=61,label_y=9,target_x=70,target_y=19),dict(label="Actual millimeter scale",label_x=46,label_y=84,target_x=67,target_y=60)]),
  dict(code="d",fn="bob-harms-erin-d-real-lemma-palea-disarticulation.jpg",title="REAL DISSECTION · lemma, palea, grain and separation",
    role="Real dissected floret and mature caryopsis with author-identified lemma and palea, photographed with millimeter marks",
    caption="Bob Harms' same-species dissection labels true lemma, palea and caryopsis, with a photographed scale. The source's existing anatomical labels are left unobscured; the mature parts separate along the pictured rachilla. Do not confuse the caryopsis with an unbroken entire spikelet.",
    arrows=[])
]
def download(url):
    req=Request(url,headers={"User-Agent":"HaysCountyBotanyEducationalLearner/1.0"})
    with urlopen(req,timeout=40) as f:return f.read(10_000_001)
def save(path,obj):
    path.parent.mkdir(exist_ok=True,parents=True)
    path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
def main():
    s=json.loads(CARD.read_text())
    assert s["scientific_name"]=="Eragrostis intermedia" and s["id"]=="eragrostis-intermedia"
    old={x["file"] for x in s["images"] if x.get("file")}
    if all("images/"+v["fn"] in old for v in SPEC):
        for v in SPEC:assert (BASE/"images"/v["fn"]).stat().st_size>10000
        print("ALREADY_ARCHIVED");return
    if any("images/"+v["fn"] in old or (BASE/"images"/v["fn"]).exists() for v in SPEC):
        raise RuntimeError("Partial previous install needs reconciliation, not duplicated")
    rights=download(SITE).decode("utf-8",errors="replace").lower()
    assert "free for scientific and educational uses" in rights and "bob harms" in rights
    new_images=[];panels=[];files=[]
    for obj in SPEC:
        code=obj["code"]
        page=URLBASE+f"pages/ERIN-{code}.html"
        source=URLBASE+f"images/ERIN-{code}.jpg"
        page_text=download(page).decode("utf-8",errors="replace").lower()
        if not ("eragrostis intermedia" in page_text and "bob harms" in page_text):
            raise RuntimeError("Taxon/author source mismatch: "+page)
        raw=download(source)
        if not 9000<len(raw)<10_000_000:raise RuntimeError("Bad JPEG size: "+source)
        with Image.open(io.BytesIO(raw)) as original:
            if original.format!="JPEG":raise RuntimeError("Not photo JPEG")
            img=ImageOps.exif_transpose(original).convert("RGB")
            w,h=img.size
            if min(w,h)<350:raise RuntimeError("Diagnostic original too small: "+source)
            out=io.BytesIO()
            img.save(out,"JPEG",quality=94,subsampling=0,optimize=True)
            data=out.getvalue()
        hashval=hashlib.sha256(data).hexdigest()
        path=BASE/"images"/obj["fn"];path.parent.mkdir(exist_ok=True,parents=True);path.write_bytes(data)
        rel="content/taxa/Poaceae/Eragrostis/eragrostis-intermedia/images/"+obj["fn"]
        attrib={
          "creator":"Bob Harms",
          "license":"© Bob Harms — scientific/educational use with attribution (NOT Creative Commons)",
          "license_url":SITE,
          "source_page":page,
          "source_image":source,
          "source_taxon_name":"Eragrostis intermedia",
          "site_specific_public_permission":"BOB_HARMS_SELECTED_MONOCOTS_EDU_WITH_CREDIT_20261022",
          "public_reuse":"yes — credited scientific/educational use per photographer's Selected Central Texas Monocots terms; noncommercial educational learner",
          "modifications":"Re-encoded as EXIF/GPS-free JPEG; original anatomical labels retained, separate overlay annotations",
          "image_sha256":hashval,"source_dimensions_px":[w,h]
        }
        new_images.append({"file":"images/"+obj["fn"],"role":obj["role"],**attrib})
        panels.append({
            "label":obj["title"],"scientific_name":"Eragrostis intermedia",
            "image_url":rel,"image_fit":"contain","image_role":obj["role"],
            "caption":obj["caption"],"why_it_matters":"Shows real species-specific grass anatomy instead of another distant panicle.",
            "markers":obj["arrows"],
            "photo_status":"Author/individual source verified; visually reviewed organ locations, no fabricated inner micro-ligule or rhizomes.",
            **attrib
        })
        files.append({"code":code,"file":rel,"source":page,"source_sha256":hashlib.sha256(raw).hexdigest(),
                      "local_sha256":hashval,"bytes":len(data),"pixels":[w,h],"arrows":len(obj["arrows"])})
    items=s["visual_comparison"]["items"]
    ix=next((i for i,p in enumerate(items) if p.get("scientific_name") not in (None,"Eragrostis intermedia")),len(items))
    items[ix:ix]=panels
    s["images"].extend(new_images)
    s.setdefault("curation_status",{})["lane2_harms_real_anatomy_20261027"]={
        "status":"FIELD_READY_PHOTO_GAPS","physically_archived_new_species_photos":len(files),
        "real_collar":"PARTIAL — collar hairs photographed; microscopic true ligule tip still ambiguous",
        "real_root":"Full photograph of connected crown/fibrous roots, no rhizome inference",
        "real_floret_dissection":"Measured photographic role upgraded from 0.5 to 1",
        "new_arrows":sum(len(o["arrows"]) for o in SPEC),
        "six_role_photo_score":"5.5/6 (92%) provisional",
        "public_pages":"pending controlled rights-filtered release"
    }
    s["photo_note"]=s.get("photo_note","")+"\n2026-10-27 Lane 2: four genuine Bob Harms original Selected Central Texas Monocots ERIN-L,-z,-9,-d photographed collar, rooted crown, scaled spikelets and actual lemma/palea disarticulation installed with original educational reuse terms. Inner 0.3–0.5mm ligule still partial (exterior hairs are not ligule proof); root photo does not prove rhizomes."
    save(CARD,s)
    report=json.loads(SCORE.read_text())
    record=next(x for x in report["records"] if x["canonical_id"]=="eragrostis-intermedia")
    assert record["roles"]["true_collar_ligule_sheath"]==0 and record["roles"]["reproductive_closeup"]==0.5
    assert record["after_total"]==4.5
    record["roles"]["true_collar_ligule_sheath"]=0.5
    record["roles"]["reproductive_closeup"]=1
    record["after_total"]=5.5
    record["after_percentage"]=92
    record["change_percentage_points"]=92-record["before_percentage"]
    record["new_source_report"]="reports/lane2-eragrostis-intermedia-harms-anatomy-20261027.json"
    record["gaps_warning"]="Source photograph shows outer collar/sheath and hairs, not isolated 0.3–0.5mm true ligule. Attached roots pictured, rhizome contradictory in regional sources; no extra score."
    report["summary"]["mean_after_percent"]=round(sum(a["after_total"] for a in report["records"])/len(report["records"])/6*100,1)
    dist={}
    for a in report["records"]:
        k=f'{a["after_total"]:.1f}/6';dist[k]=dist.get(k,0)+1
    report["summary"]["distribution"]=dist
    report["summary"]["latest_plains_lovegrass_harms_20261027"]={
        "actual_photos_added":len(files),
        "anatomy_arrows":sum(len(o["arrows"]) for o in SPEC),
        "provisional_score":"5.5/6 (92%)",
        "credits":"Bob Harms, Selected Central Texas Monocots, educational with credit (not CC)",
        "public_pages":"not verified"}
    save(SCORE,report)
    save(REPORT,{"species":"Eragrostis intermedia","status":"FIELD_READY_PHOTO_GAPS",
         "date":"2026-10-27","new_original_species_photos":4,"photo_details":files,
         "license":"Bob Harms credited educational scientific use, not Creative Commons",
         "rights_homepage":SITE,"new_arrows":sum(len(o["arrows"]) for o in SPEC),
         "before_photo_roles":4.5,"after_photo_roles":5.5,"after_percent":92,
         "honest_remaining":"0.3–0.5mm truly isolated inner ligule, rhizome conflict unresolved; no invented completeness",
         "pages":"Release unverified"})
    save(MARK,{"type":"manual_field_id_publication","date":"2026-10-27",
       "species":"Eragrostis intermedia","title":"Plains lovegrass real Bob Harms collar root and spikelet anatomy",
       "source_report":str(REPORT.relative_to(ROOT)), "status":"FIELD_READY_PHOTO_GAPS",
       "public_license":"Bob Harms individually credited education/science use; non-CC",
       "pages":"must verify rights-filtered deployment"})
    print("INSTALLED",json.dumps({"photos":len(files),"arrows":sum(len(o["arrows"]) for o in SPEC),"mean":report["summary"]["mean_after_percent"],"species":92,"sources":files}))
if __name__=="__main__":main()
