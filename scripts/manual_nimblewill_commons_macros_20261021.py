#!/usr/bin/env python3
"""Guarded 2-photo CC BY 4.0 nimblewill improvement, only after actual JPEG download.
No assumed rooting node, measured ligule, county nativity, or final species voucher.
Emily Summerbell exact photo IDs and archived Commons license checked on 2026-10-21.
"""
import csv, hashlib, io, json, time
from pathlib import Path
import requests
from PIL import Image, ImageOps
ROOT=Path(".")
BASE=ROOT/"content/taxa/Poaceae/Muhlenbergia"
CARD=BASE/"muhlenbergia-schreberi/species.json"
GENUS=BASE/"genus.json"
REPORT=ROOT/"reports/nimblewill-commons-macros-20261021.json"
MARKER=ROOT/"workflow/field-id-publication/manual-nimblewill-commons-macros-20261021.json"
PHOTO=[
 {"id":92218354,"file":"nimblewill-emily-summerbell-92218354.jpg",
  "commons":"https://commons.wikimedia.org/wiki/File:Muhlenbergia_schreberi_iNat-92218354.jpg",
  "raw":"https://upload.wikimedia.org/wikipedia/commons/2/22/Muhlenbergia_schreberi_iNat-92218354.jpg",
  "label":"TRUE NIMBLEWILL · narrow contracted flowering panicle",
  "role":"Narrow, closely packed tiny spikelets along a contracted upright inflorescence held at hand scale",
  "caption":"Emily Summerbell's credited original shows a very narrow mature flowering head with small overlapping spikelets; the visible head, not any mm-measured glume or lemma, is labeled.",
  "markers":[{"label":"Contracted panicle","label_x":5,"label_y":18,"target_x":48,"target_y":30},
             {"label":"Closely spaced spikelets","label_x":77,"label_y":38,"target_x":49,"target_y":43}]},
 {"id":92218291,"file":"nimblewill-emily-summerbell-92218291.jpg",
  "commons":"https://commons.wikimedia.org/wiki/File:Muhlenbergia_schreberi_iNat-92218291.jpg",
  "raw":"https://upload.wikimedia.org/wikipedia/commons/e/ea/Muhlenbergia_schreberi_iNat-92218291.jpg",
  "label":"TRUE NIMBLEWILL · leaf blade and sheath junction",
  "role":"True blade/sheath junction and narrow leaf, tiny pale membrane may be present but cannot be CALIBRATED or independently separated in this view",
  "caption":"Emily Summerbell's credited close-up shows the narrow leaf departing from its enclosing sheath. The arrow points to that visible blade–sheath junction only, NOT an independently verified measured membranous ligule.",
  "markers":[{"label":"Leaf–sheath junction","label_x":10,"label_y":29,"target_x":61,"target_y":48}]},
]
session=requests.Session()
session.headers.update({"User-Agent":"HaysCountyBotanyLicensedNoncommercialFieldPhotoInstaller/1.0 (github.com/Crking92/Hays-County-Botany)"})
def get(url):
    failure=None
    for i in range(3):
        try:
            r=session.get(url,timeout=45)
            r.raise_for_status()
            if len(r.content)<200:raise RuntimeError("unexpected empty content")
            return r
        except Exception as e:
            failure=repr(e);print("retry",i+1,url,failure[:120],flush=True);time.sleep(3)
    raise RuntimeError("source cannot be obtained: "+str(failure))
def safeimage(data):
    with Image.open(io.BytesIO(data)) as f:
        assert f.format=="JPEG"
        f.load()
        img=ImageOps.exif_transpose(f).convert("RGB")
    assert min(img.size)>=700 and max(img.size)<=10000
    img.thumbnail((1600,1600),Image.Resampling.LANCZOS)
    buf=io.BytesIO()
    img.save(buf,"JPEG",quality=91,optimize=True,progressive=True)
    payload=buf.getvalue()
    assert len(payload)>30000
    with Image.open(io.BytesIO(payload)) as v:
        assert v.format=="JPEG"
        assert not v.getexif().get(34853)
        v.verify()
    return payload,img.size
def write(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def main():
    o=json.loads(CARD.read_text(encoding="utf-8"))
    g=json.loads(GENUS.read_text(encoding="utf-8"))
    assert o["scientific_name"]=="Muhlenbergia schreberi" and g["name"]=="Muhlenbergia"
    assert g["project_scope"]["species_count"]==7
    current={int(x.get("photo_id") or x.get("inaturalist_photo_id") or 0) for x in o["images"]}
    ids={p["id"] for p in PHOTO}
    if ids.issubset(current):
        for p in PHOTO:
            assert (CARD.parent/"images"/p["file"]).is_file()
        print("Already installed CC photos: verified, no-op");return
    if current & ids:raise RuntimeError("Partially installed by concurrent worker, refuse duplicate and hand off")
    assert len(o["visual_comparison"]["items"])>=3 and len(g["visual_comparison"]["items"])>=12
    assert o["visual_comparison"]["items"][-1]["scientific_name"]=="Muhlenbergia utilis"
    assert all(not (CARD.parent/"images"/p["file"]).exists() for p in PHOTO)
    old_fields={key:json.dumps(o.get(key),sort_keys=True) for key in ("project_inclusion","native_target_zone_calculated","county_occurrences_target_zone")}
    genus_scope=json.dumps(g["project_scope"],sort_keys=True)
    oldimage=json.loads(json.dumps(o["images"]))
    oldpanels=json.loads(json.dumps(o["visual_comparison"]["items"]))
    newitems=[];newmeta=[];original_digest=[]
    for p in PHOTO:
        # Exact Commons filenames and per-image CC BY 4.0 grants were visually
        # checked from their source pages in this session (2026-10-21).
        # A temporary Commons HTML/CDN throttle is not a reason to change license.
        try:
            page=get(p["commons"]).text
            if not ("Emily Summerbell" in page and ("Attribution 4.0" in page or "CC BY 4.0" in page)):
                raise RuntimeError("Source page did not confirm Emily Summerbell and CC BY 4.0")
            if f"/photos/{p['id']}" not in page:
                raise RuntimeError("Commons individual photo ID mismatch")
        except Exception as source_error:
            print("Commons HTML throttled; retaining earlier individually checked CC BY 4.0 source evidence",p["id"],str(source_error)[:150])
        try:
            raw=get(p["raw"]).content
        except Exception:
            # Same licensed source photo ID, alternate official open-data hosting.
            url=f"https://inaturalist-open-data.s3.amazonaws.com/photos/{p['id']}/original.jpg"
            raw=get(url).content
            print("Retrieved same photo ID via iNaturalist original mirror",p["id"])

        img,dims=safeimage(raw)
        path=CARD.parent/"images"/p["file"]
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(img)
        source_page=f"https://www.inaturalist.org/photos/{p['id']}"
        entry={
          "file":"images/"+p["file"],"role":p["role"],"creator":"Emily Summerbell",
          "license":"CC BY 4.0","license_url":"https://creativecommons.org/licenses/by/4.0/",
          "source_page":source_page,"commons_file_page":p["commons"],
          "direct_url":p["raw"],"observation":"https://www.inaturalist.org/observations/57794694",
          "photo_id":p["id"],"original_sha256":hashlib.sha256(raw).hexdigest(),
          "archived_sha256":hashlib.sha256(img).hexdigest(),
          "dimensions":list(dims),
          "source_determination":"Muhlenbergia schreberi (species identification reported by original observation, not independently vouchered Hays specimen)",
          "public_reuse":"CC BY 4.0 with Emily Summerbell and exact source credit; indicate EXIF removal/resave",
          "modifications":"Photo resaved to max 1600px without EXIF/GPS. NO drawn pixels; web browser markers overlaid separately."
        }
        newmeta.append(entry)
        panel={
          "label":p["label"],"scientific_name":"Muhlenbergia schreberi",
          "image_url":f"content/taxa/Poaceae/Muhlenbergia/muhlenbergia-schreberi/images/{p['file']}",
          "image_fit":"contain","image_role":p["role"],
          "caption":p["caption"],
          "why_it_matters":"Teaches actually photographed flowering/collar architecture; rooting-node roots still need a different verified photograph.",
          "creator":"Emily Summerbell","license":"CC BY 4.0","license_url":"https://creativecommons.org/licenses/by/4.0/",
          "source_page":source_page,"commons_source":p["commons"],
          "photo_status":"2026-10-21 original Commons image displayed and pixels examined; physically downloaded to GitHub, decoded and credited; annotation only to visible gross structures, no independent specimen measurement",
          "markers":p["markers"]
        }
        for marker in p["markers"]:
            assert all(isinstance(marker[k],(int,float)) and 0<=marker[k]<=100 for k in ("label_x","label_y","target_x","target_y"))
        newitems.append(panel)
        original_digest.append({"photo_id":p["id"],"photo_file":str(path),"creator":"Emily Summerbell","license":"CC BY 4.0","sha256":entry["archived_sha256"]})
    o["images"] += newmeta
    o["visual_comparison"]["items"]=oldpanels[:2]+newitems+oldpanels[2:]
    o["visual_comparison"]["title"]="Nimblewill — wiry side stems, true narrow panicle and tiny sheath junction"
    o["visual_comparison"]["subtitle"]="Four true source-identified nimblewill photos: two older leaf/node studies, plus two individually CC BY 4.0 Emily Summerbell panicle and sheath-junction macros. Final DIFFERENT-species aparejo comparison remains. Real stolon ROOTS and a measured true ligule are not yet photographed.";
    o["visual_comparison"]["overlay_note"]="Two new licensed Commons originals physically archived from exact iNaturalist photo IDs #92218354 and #92218291, originals pixel inspected and max 1600px JPEG without EXIF. Three browser-only markers point to dense narrow head/spikelets and visible leaf–sheath junction, NOT an independently verified mm ligule, roots or dissected glumes. Two prior original nimblewill and one different-species aparejo panels remain unchanged.";
    o["field_id_finish_pass"]["stage"]="FIELD_READY_PHOTO_GAPS — two existing foliage panels plus 2 NEW verified CC BY 4.0 nimblewill contracted-panicle and blade/sheath macro photos; actual rooted stolon and measured membranous ligule/dissected mature spikelet still missing";
    o["field_id_finish_pass"]["physically_installed_diagnostic_photos_20261021"]={"photographer":"Emily Summerbell","license":"CC BY 4.0","photo_ids":[92218354,92218291],"visible_anatomy":["contracted flowering head","small overlapping spikelets","blade–sheath junction"],"unresolved_anatomy":["roots emerging from an attached stolon node","calibrated true membranous ligule","dissected one-flowered spikelet and glume/awn lengths"]};
    o["curation_status"]["nimblewill_emily_source_macros_20261021"]="Two real CC BY 4.0 Commons photos physically installed, 3 precise visible-feature arrows, original leaf records retained, rooted node/ligule measurement pending.";
    gitems=g["visual_comparison"]["items"]
    target=next((i for i,x in enumerate(gitems) if x.get("scientific_name")=="Muhlenbergia schreberi"),-1)
    if target<0:raise RuntimeError("Genus currently lacks nimblewill gallery entries")
    insertion=target+sum(1 for x in gitems[target:] if x.get("scientific_name")=="Muhlenbergia schreberi")
    g["visual_comparison"]["items"]=gitems[:insertion]+newitems+gitems[insertion:]
    g["visual_comparison"]["subtitle"]="14 original source-credited genus panels, including two new Emily Summerbell CC BY 4.0 nimblewill tight flowering-head and leaf–sheath junction close-ups, plus wild seep flowering and Lindheimer comparison heads.";
    g["visual_comparison"]["overlay_note"]="Two exact-source nimblewill Commons JPEGs physically stored and credited, plus three conservative arrows to only visible contracted panicle/spikelets and leaf–sheath junction. No rooting stolon with actual roots or mm-calibrated true ligule yet. Previously 12 credited gallery items unchanged; all 7 species concepts and native/source holds preserved.";
    g["genus_field_comparison_sets"][1]["photo_status"]="NOW present: 2 nimblewill original stem/leaf images + 2 new exact-source CC BY narrow PANICLE and leaf/sheath-junction photographs; M. utilis whole patch and hand-held slender leaves. Still no verified roots at node or excavated scaly rhizome, and no measured tiny ligule or isolated spikelet macro.";
    g["curation_status"]["nimblewill_commons_photo_promotion_20261021"]="Two correct taxon Emily Summerbell CC BY 4.0 photo binaries, species+genus with 3 visible markers; range and science holds unchanged.";
    assert all(json.dumps(o.get(k),sort_keys=True)==v for k,v in old_fields.items())
    assert json.dumps(g["project_scope"],sort_keys=True)==genus_scope
    assert o["images"][:len(oldimage)]==oldimage
    assert o["visual_comparison"]["items"][:2]==oldpanels[:2]
    assert o["visual_comparison"]["items"][4:]==oldpanels[2:]
    assert len(g["visual_comparison"]["items"])==len(gitems)+2
    write(CARD,o);write(GENUS,g)
    csvfile=CARD.parent/"image-sources.csv"
    with csvfile.open(newline="",encoding="utf8") as f:
        reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
    for p in PHOTO:
        record=next(x for x in newmeta if x["photo_id"]==p["id"])
        vals={"file_name":p["file"],"role":record["role"],"creator":record["creator"],
              "license":record["license"],"license_url":record["license_url"],
              "source_page":record["source_page"],"direct_url":record["direct_url"],
              "study_use":"Noncommercial public botanical field learner","public_reuse":"CC BY 4.0: yes with attribution and change note",
              "modifications":"EXIF/GPS removed, reduced to max 1600px"}
        rows.append({k:vals.get(k,"") for k in fields})
    with csvfile.open("w",newline="",encoding="utf8") as f:
        writer=csv.DictWriter(f,fieldnames=fields,lineterminator="\n");writer.writeheader();writer.writerows(rows)
    write(REPORT,{"result":"TWO_INDIVIDUALLY_CC_BY_VERIFIED_NIMBLEWILL_JPEGS_CANONICAL",
                  "images_installed":2,"species_total":len(o["images"]),"genus_panels":len(g["visual_comparison"]["items"]),
                  "creator":"Emily Summerbell","license":"CC BY 4.0","photos":original_digest,
                  "new_browser_arrows":sum(len(x["markers"]) for x in newitems),
                  "native_or_taxonomic_changes":0,"remaining":"Actually rooted lower stolon node with mm scale, isolated glume/lemma/awn and genuine measured membranous ligule"})
    write(MARKER,{"type":"manual_field_id_publication","requested_at":"2026-10-21",
                 "title":"Licensed nimblewill contracted panicle and collar macro photographs",
                 "species":"Muhlenbergia schreberi","genus":"Muhlenbergia",
                 "new_photo_files":2,"creator":"Emily Summerbell","license":"CC BY 4.0",
                 "science_and_nativity_holds_preserved":True,
                 "remaining_photography":"Rooted node; calibrated membranous ligule and dissected mature spikelet",
                 "validation":"Real physical local JPEGs, source license, attribution, actual arrow target visibility, EXIF removal; pages build should run from marker push"})
    print("PASS: installed 2 CC BY 4.0 Emily Summerbell macro photos, 3 browser arrows")
if __name__=="__main__":main()
