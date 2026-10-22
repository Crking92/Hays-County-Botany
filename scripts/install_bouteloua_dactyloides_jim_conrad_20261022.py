#!/usr/bin/env python3
"""Fail-closed archiver for Jim Conrad's own public-domain Uvalde buffalograss photographs."""
import csv,hashlib,io,json,urllib.request
from pathlib import Path
from PIL import Image,ImageOps

R=Path(".")
BASE=R/"content/taxa/Poaceae/Bouteloua"
CARD=BASE/"bouteloua-dactyloides/species.json"
GENUS=BASE/"genus.json"
CSV=BASE/"bouteloua-dactyloides/image-sources.csv"
REPORT=R/"reports/bouteloua-dactyloides-jim-conrad-sex-and-ligule-20261022.json"
MARK=R/"workflow/field-id-publication/2026-10-22-buffalograss-jim-conrad-male-ligule-photos.json"
PAGE="https://www.backyardnature.net/n/h/bufgrass.htm"
RIGHTS="https://www.backyardnature.net/j/copyrite.htm"
CANDIDATES=[
    ("140601bv.jpg","jim-conrad-uvalde-male-whole-grass.jpg","Author-identified entire Texas male flowering plant, hand scale"),
    ("140601bw.jpg","jim-conrad-uvalde-male-combs.jpg","Texas male staminate flowering combs, visible pollen-bearing anthers"),
    ("140601bx.jpg","jim-conrad-uvalde-hairy-ligule.jpg","True grass collar hairs at sheath/blade junction; ligule not measured"),
]

def dump(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf8")

def main():
    s=json.loads(CARD.read_text());g=json.loads(GENUS.read_text())
    assert s["id"]=="bouteloua-dactyloides" and g["name"]=="Bouteloua"
    assert g["project_scope"]["canonical_species_count"]==7
    old_science={k:json.dumps(s.get(k),sort_keys=True) for k in ("project_inclusion","county_occurrences_target_zone","target_zone_count","native_target_zone_calculated","synonyms","taxonomic_note")}
    genus_scope=json.dumps(g["project_scope"],sort_keys=True)
    panels=[]
    for original,name,_ in CANDIDATES:
        url="https://www.backyardnature.net/n/14/"+original
        pair=[]
        for card in (s,g):
            found=[p for p in card["visual_comparison"]["items"] if p.get("source_image")==url]
            if not found: 
                if card is g and original=="140601bv.jpg":
                    pair.append(None)
                    continue
                raise RuntimeError("Expected sourced photograph not linked: "+url)
            if len(found)!=1:raise RuntimeError("Duplicate URL in one card")
            p=found[0]
            if p["creator"]!="Jim Conrad" or p["source_page"]!=PAGE or "Public domain" not in p["license"]:
                raise RuntimeError("Source attribution/rights guard failed")
            pair.append(p)
        panels.append(pair)
    destinations=[BASE/"bouteloua-dactyloides/images"/name for _,name,_ in CANDIDATES]
    already=[p.exists() for p in destinations]
    if all(already):
        if all(p[0]["image_url"]==str(dest) and (p[1] is None or p[1]["image_url"]==str(dest)) for p,dest in zip(panels,destinations)) and all(any(rec.get("file")=="images/"+dest.name for rec in s["images"]) for dest in destinations):
            print("ALREADY_ARCHIVED_NOOP");return
        raise RuntimeError("Existing binaries with different canonical references")
    if any(already):raise RuntimeError("Partial set archived elsewhere; reconcile manually")
    if any(p[0]["image_url"]!="https://www.backyardnature.net/n/14/"+file for (file,_,_),p in zip(CANDIDATES,panels)):
        raise RuntimeError("Original web source has changed; HOLD")
    with CSV.open(newline="",encoding="utf8") as f:
        reader=csv.DictReader(f);headers=reader.fieldnames;rows=list(reader)
    if not headers or "file_name" not in headers:raise RuntimeError("Unexpected photo CSV")
    if any(rec["file_name"] in {name for _,name,_ in CANDIDATES} for rec in rows):raise RuntimeError("File already tracked in CSV")
    staged=[]
    for original,name,role in CANDIDATES:
        src="https://www.backyardnature.net/n/14/"+original
        with urllib.request.urlopen(urllib.request.Request(src,headers={"User-Agent":"HaysBotanyFieldIdentificationPDSourceCheck/1.0","Accept":"image/jpeg,image/*"}),timeout=38) as response:
            raw=response.read(3000000)
        if not 10000<len(raw)<3000000:raise RuntimeError("Non-image/oversized downloaded bytes for "+src)
        digest=hashlib.sha256(raw).hexdigest()
        with Image.open(io.BytesIO(raw)) as im:
            im.load()
            if im.format!="JPEG" or min(im.size)<380:raise RuntimeError("Invalid source photo type or pixel dimensions: "+src)
            rgb=ImageOps.exif_transpose(im).convert("RGB")
        buff=io.BytesIO();rgb.save(buff,format="JPEG",quality=91,optimize=True)
        encoded=buff.getvalue()
        with Image.open(io.BytesIO(encoded)) as check:
            assert check.format=="JPEG" and not check.getexif().get(34853)
            check.verify()
        staged.append((original,name,role,src,digest,hashlib.sha256(encoded).hexdigest(),encoded,list(rgb.size)))
    # No file mutation occurs until all three sources and rights/size guards pass.
    for (original,name,role,src,orig_sha,saved_sha,data,dims),dest,pair in zip(staged,destinations,panels):
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(data)
        s["images"].append({"file":"images/"+name,"role":role,"creator":"Jim Conrad","license":"Public domain (author-original explicit release)",
          "license_url":RIGHTS,"source_page":PAGE,"media_source_url":src,
          "source_determination":"Bouteloua dactyloides (Jim Conrad Uvalde Texas 2014 male plant)",
          "source_locality":"Dry Frio River, Uvalde County, Texas; no Hays voucher claim",
          "source_original_sha256":orig_sha,"archived_image_sha256":saved_sha,"image_dimensions":dims,
          "photo_review":"Source and visible normal MALE comb/collar morphology documented by Jim Conrad. No FEMALE bur from this source; true rooting stolon and counted microscopic spikelets are NOT confirmed.",
          "public_reuse":"Yes, original photographer expressly dedicates own work to public domain; retain his name and page",
          "modifications":"Image reencoded as RGB JPEG stripping EXIF/GPS; overlay arrows are browser-added to original pixels."})
        for pane in pair:
            if pane is not None:
                pane["image_url"]=str(dest)
                pane["photo_status"]="PHYSICALLY ARCHIVED Jim Conrad author-public-domain source Uvalde male grass photograph. Actual original and archived SHA256 recorded, EXIF/GPS cleaned; annotations only to visible organs. No female structures or actual rooted stolon node alleged."
        vals={"file_name":name,"role":role,"creator":"Jim Conrad","license":"Public domain by author","license_url":RIGHTS,
          "source_page":PAGE,"direct_url":src,"study_use":"Public crew botanical field education",
          "public_reuse":"Author original public domain","modifications":"RGB re-encoded EXIF/GPS removed, no source pixels painted"}
        rows.append({k:vals.get(k,"") for k in headers})
    with CSV.open("w",newline="",encoding="utf8") as f:
        writer=csv.DictWriter(f,fieldnames=headers,lineterminator="\n");writer.writeheader();writer.writerows(rows)
    if any(json.dumps(s.get(k),sort_keys=True)!=v for k,v in old_science.items()) or json.dumps(g["project_scope"],sort_keys=True)!=genus_scope:
        raise RuntimeError("Preserved taxonomy/nativity/scope changed")
    assert len(s["visual_comparison"]["items"])==7 and len(g["visual_comparison"]["items"])==14
    assert sum(len(p.get("markers",[])) for p in s["visual_comparison"]["items"])==8
    s["curation_status"]["jim_conrad_buffalo_physically_archived_20261022"]="Three author-public-domain Texas buffalograss JPEGs physically stored with source and archive hashes; male flower and collar roles real; normal healthy female still only separately licensed comparison."
    g["curation_status"]["jim_conrad_buffalo_physically_archived_20261022"]="Two Uvalde male flower/collar images now local. Commons healthy female/male vs infected middle comparison remains EXTERNAL REVIEW photo."
    dump(CARD,s);dump(GENUS,g)
    dump(REPORT,{"result":"THREE_JIM_CONRAD_BUFFALO_PD_JPEGS_PHYSICALLY_STORED",
        "files":[{"path":"content/taxa/Poaceae/Bouteloua/bouteloua-dactyloides/images/"+name,"original_source":src,"original_sha256":orig_sha,
                  "archived_sha256":archived_sha,"dimensions":dim} for _,name,_,src,orig_sha,archived_sha,_,dim in staged],
        "new_physical_files":3,"genus_panels":14,"species_panels":7,
        "original_licenses_and_native_range_preserved":True,"source_page":PAGE,"author":"Jim Conrad",
        "remaining":["true healthy Texas female bur on intact plant","true rooting buffalograss stolon node macro","Commons triptych licensed external, center infected","same-plant leaf collar and female reproductive measurement"]})
    dump(MARK,{"type":"manual_field_id_publication","requested_at":"2026-10-22",
        "title":"Buffalograss male and collar actual three Jim Conrad public-domain Texas photos",
        "family":"Poaceae","genus":"Bouteloua","species":"Bouteloua dactyloides",
        "source_page":PAGE,"new_physical_images":3,"species_panels":7,"genus_panels":14,
        "original_species_scope_and_native_status_preserved":True,
        "stage":"FIELD_READY_PHOTO_GAPS","publication":"Trigger approved rights-filtered Pages workflow only after file bytes and image quality check."})
    print("PASS physical Jim Conrad Uvalde male and collar photos; other seven Bouteloua canonical species unchanged")

if __name__=="__main__":
    main()
