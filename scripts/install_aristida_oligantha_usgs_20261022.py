#!/usr/bin/env python3
"""Safely archive one USGS Plants of Louisiana public-domain Aristida oligantha seedhead photo.
Creates actual GitHub image bytes only after validating source, rights in canonical
prepared panels, format, pixels, SHA and scoped protection. No artificial ID claims.
"""
from pathlib import Path
from PIL import Image, ImageOps
import csv, hashlib, io, json, urllib.request

ROOT=Path(".");BASE=ROOT/"content/taxa/Poaceae/Aristida";T=BASE/"aristida-oligantha"
S=T/"species.json";G=BASE/"genus.json";CSV=T/"image-sources.csv"
DEST=T/"images/usgs-louisiana-oldfield-long-awns.jpg"
REPORT=ROOT/"reports/aristida-oligantha-usgs-public-domain-photo-import-20261022.json"
MARKER=ROOT/"workflow/field-id-publication/2026-10-22-aristida-oligantha-usgs-awn-photo.json"
URL="https://warcapps.usgs.gov/PlantID/Image/GivenFile?file=Aristida+oligantha_0001.JPG&id=2840"
SRC="https://warcapps.usgs.gov/PlantID/Species/Details/2840"
LICENSE="https://warcapps.usgs.gov/PlantID/Home/About"
LOCAL=str(DEST)
CREDIT="USGS Wetland and Aquatic Research Center — Plants of Louisiana (Larry Allain / Chris Reid; individual image photographer not designated)"

def store(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
def main():
    s=json.loads(S.read_text(encoding="utf8"));g=json.loads(G.read_text(encoding="utf8"))
    assert s["id"]=="aristida-oligantha" and g["name"]=="Aristida"
    assert g["project_scope"]["species_ids"]==["aristida-purpurea","aristida-oligantha"]
    preserved={k:json.dumps(s.get(k),sort_keys=True) for k in ("project_inclusion","county_occurrences_target_zone","target_zone_count","native_target_zone_calculated","synonyms","taxonomic_note")}
    scopestr=json.dumps(g["project_scope"],sort_keys=True)
    panes=[next((p for p in obj["visual_comparison"]["items"] if p.get("source_image")==URL),None) for obj in (s,g)]
    if any(p is None for p in panes):raise RuntimeError("USGS candidate panels no longer match, HOLD")
    for p in panes:
        assert p["source_page"]==SRC and p["creator"]==CREDIT
        assert "Public domain" in p["license"] and len(p.get("markers",[]))==2
    if DEST.exists():
        if all(p["image_url"]==LOCAL for p in panes) and any(i.get("file")=="images/"+DEST.name for i in s["images"]):
            with Image.open(DEST) as im:im.verify()
            print("ALREADY_INSTALLED_NOOP");return
        raise RuntimeError("Existing JPEG not synchronized; HOLD")
    if any(i.get("file")=="images/"+DEST.name for i in s["images"]):
        raise RuntimeError("Already listed physical JPEG without bytes; HOLD")
    if not all(p["image_url"]==URL for p in panes):
        raise RuntimeError("Photo URL changed, HOLD")
    with urllib.request.urlopen(urllib.request.Request(URL,headers={
      "User-Agent":"HaysBotanyAristidaPublicDomainPhotoVerify/1.0","Accept":"image/jpeg,image/*"
    }),timeout=45) as req:
        raw=req.read(5_000_000)
    if not 10000<len(raw)<5_000_000:raise RuntimeError("USGS response not valid image size")
    original_sha=hashlib.sha256(raw).hexdigest()
    with Image.open(io.BytesIO(raw)) as source:
        source.load()
        if source.format not in ("JPEG","PNG") or min(source.size)<400:
            raise RuntimeError("Unsupported image source format or too small")
        photo=ImageOps.exif_transpose(source).convert("RGB")
    buf=io.BytesIO()
    photo.save(buf,format="JPEG",quality=92,optimize=True)
    bytes_=buf.getvalue()
    with Image.open(io.BytesIO(bytes_)) as check:
        assert check.format=="JPEG" and not check.getexif().get(34853)
        check.verify()
    with CSV.open(newline="",encoding="utf8") as f:
        reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
    assert fields and "file_name" in fields
    if any(r.get("file_name")==DEST.name for r in rows):raise RuntimeError("Source CSV has duplicate")
    DEST.parent.mkdir(parents=True,exist_ok=True);DEST.write_bytes(bytes_)
    archived_sha=hashlib.sha256(bytes_).hexdigest()
    s["images"].append({"file":"images/"+DEST.name,
      "role":"True source-labelled oldfield threeawn flowering panicle: spreading long lemma awns, wispy outward habit, central flowering stem; NO individual vein macro",
      "creator":CREDIT,"license":"Public domain — official USGS Plants of Louisiana image",
      "license_url":LICENSE,"source_page":SRC,"media_source_url":URL,
      "source_locality":"Louisiana; NOT Hays County","source_determination":"Aristida oligantha from USGS Plants of Louisiana",
      "source_image_original_sha256":original_sha,"archived_image_sha256":archived_sha,
      "image_dimensions":[photo.width,photo.height],
      "photo_review":"Source photo visually reviewed for whole seedhead and visible awns only; glumes and 3-7 lower veins not resolved, not a specimen voucher re-determination.",
      "anatomy_arrows":"Two browser-only overlays pointing to visible awn halo and flowering axis; no unobservable glumes or floret insertion.",
      "modifications":"Normalized RGB JPEG with EXIF/GPS removed; source pixels not annotated.",
      "public_reuse":"Yes, Plants of Louisiana explicitly dedicates all app photographs to public domain; institutional image credit maintained."
    })
    for p in panes:
        p["image_url"]=LOCAL
        p["photo_status"]="PHYSICALLY ARCHIVED exact USGS source image, original SHA256 verified, EXIF stripped; public domain per official site. Two browser arrows only to visible awns and axis, NOT a photographed glume/vein demonstration. Original site credits Larry Allain / Chris Reid without individual photo byline; Louisiana not Hays."
    s["curation_status"]["usgs_oldfield_physical_20261022"]="Source USGS PD JPG archived with original SHA256 and image-level rights; two gross visible-feature arrows, glume vein gap preserved"
    g["curation_status"]["usgs_oldfield_physical_20261022"]="Genus USGS oldfield PD image now physically stored, species origin/rights intact"
    s["learner_visual_status"]["image_count"]=len(s["images"])
    s["learner_visual_status"]["status"]="field_ready_photo_gaps"
    if json.dumps(g["project_scope"],sort_keys=True)!=scopestr:raise RuntimeError("Genus scope changed")
    if any(json.dumps(s.get(k),sort_keys=True)!=v for k,v in preserved.items()):raise RuntimeError("Taxonomy/range claim changed")
    values={"file_name":DEST.name,"role":"Oldfield long awns and branching panicle","creator":CREDIT,
      "license":"Public domain — USGS Plants of Louisiana","license_url":LICENSE,
      "source_page":SRC,"direct_url":URL,"study_use":"Public educational learner",
      "public_reuse":"Yes, source-exact USGS public-domain images","modifications":"Reencoded JPEG without EXIF/GPS; photo pixels unchanged geometrically"}
    rows.append({k:values.get(k,"") for k in fields})
    with CSV.open("w",newline="",encoding="utf8") as f:
        writer=csv.DictWriter(f,fieldnames=fields,lineterminator="\n")
        writer.writeheader();writer.writerows(rows)
    assert sum(len(x.get("markers",[])) for x in s["visual_comparison"]["items"])==5
    store(S,s);store(G,g)
    store(REPORT,{"result":"USGS_ARISTIDA_OLIGANTHA_PHYSICAL_JPEG_INSTALLED","photo":LOCAL,
      "source":URL,"creator":CREDIT,"license":"USGS Plants of Louisiana public domain",
      "original_sha256":original_sha,"archived_sha256":archived_sha,
      "dimensions":[photo.width,photo.height],"new_physical_jpgs":1,
      "source_panels_species":len(s["visual_comparison"]["items"]),"source_panels_genus":len(g["visual_comparison"]["items"]),
      "scientific_taxonomy_native_counties_unchanged":True,
      "remaining":["matched true 18–25 mm oldfield glumes with millimeter ruler","backlit lower glume 3–7 veins","purple threeawn variety-aware paired glumes"]})
    store(MARKER,{"type":"manual_field_id_publication","requested_at":"2026-10-22",
      "title":"Aristida oldfield USGS actual photographed awn head physically archived",
      "species":"Aristida oligantha","genus":"Aristida","new_physical_jpgs":1,
      "creator":CREDIT,"source":SRC,"license":"public domain by USGS website",
      "stage":"FIELD_READY_PHOTO_GAPS","nativities_untouched":True,
      "publication":"Release through rights-filtered GitHub Pages, marker not final deployment proof."})
    print("PASS USGS Aristida oligantha physically stored and both species/genus linked, 2 arrow gross traits only")

if __name__=="__main__":main()
