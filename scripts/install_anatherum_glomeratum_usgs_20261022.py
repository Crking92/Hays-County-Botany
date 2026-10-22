#!/usr/bin/env python3
"""One-time guarded physical archive of USGS Larry Allain true bushy-bluestem flowering photo.
Public-domain source: https://warcapps.usgs.gov/PlantID/Species/Details/2784
Exact USGS image filename: Andropogon glomeratus var. glomeratus_inflorescence 4.JPG
No taxonomic determination or Hays County provenance is claimed beyond the federal source ID.
"""
from pathlib import Path
import csv, hashlib, io, json, urllib.request
from PIL import Image, ImageOps

ROOT=Path(".")
BASE=ROOT/"content/taxa/Poaceae/Anatherum"
SP=BASE/"anatherum-glomeratum/species.json"
GP=BASE/"genus.json"
CSV=BASE/"anatherum-glomeratum/image-sources.csv"
DEST=BASE/"anatherum-glomeratum/images/usgs-larry-allain-glomeratum-flowering.jpg"
REPORT=ROOT/"reports/bushy-bluestem-usgs-physical-photo-20261022.json"
MARKER=ROOT/"workflow/field-id-publication/2026-10-22-bushy-bluestem-usgs-photo-physical.json"
SOURCE="https://warcapps.usgs.gov/PlantID/Species/Details/2784"
ORIGINAL="https://warcapps.usgs.gov/PlantID/Image/GivenFile?file=Andropogon+glomeratus+var.+glomeratus_inflorescence+4.JPG&id=2784"
LOCAL="content/taxa/Poaceae/Anatherum/anatherum-glomeratum/images/"+DEST.name
AUTHOR="Larry Allain, U.S. Geological Survey"

def write(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf8")

def main():
    s=json.loads(SP.read_text(encoding="utf8"))
    g=json.loads(GP.read_text(encoding="utf8"))
    assert s["id"]=="anatherum-glomeratum" and g["name"]=="Anatherum"
    assert g["project_scope"]["species_count"]==3
    protected={k:json.dumps(s.get(k),sort_keys=True) for k in ("project_inclusion","county_occurrences_target_zone","target_zone_count","native_target_zone_calculated","taxonomic_note")}
    gp_scope=json.dumps(g["project_scope"],sort_keys=True)
    panels=[next((x for x in obj["visual_comparison"]["items"] if x.get("source_image")==ORIGINAL),None) for obj in (s,g)]
    if any(x is None for x in panels): raise RuntimeError("Canonical original USGS provisional panels changed: HOLD")
    if DEST.exists():
        if all(p["image_url"]==LOCAL for p in panels):
            assert any(x.get("file")=="images/"+DEST.name for x in s["images"])
            with Image.open(DEST) as im: im.verify()
            print("Previously physically archived with matching canonical panels; no-op.")
            return
        raise RuntimeError("Source JPEG exists with unsynchronized photo panels; HOLD")
    if not all(p["image_url"]==ORIGINAL and p["creator"]==AUTHOR and "Public domain" in p["license"] for p in panels):
        raise RuntimeError("Source, credits or license changed while importing; HOLD")
    if any(x.get("file")=="images/"+DEST.name for x in s["images"]): raise RuntimeError("Duplicate image record; HOLD")
    req=urllib.request.Request(ORIGINAL,headers={"User-Agent":"HaysBotanyPublicDomainImageArchive/1.0","Accept":"image/jpeg,image/*"})
    with urllib.request.urlopen(req,timeout=40) as f: raw=f.read(12000000)
    if not 12000<len(raw)<12000000: raise RuntimeError("Unacceptable response size; HOLD")
    srcsha=hashlib.sha256(raw).hexdigest()
    with Image.open(io.BytesIO(raw)) as source_im:
        source_im.load()
        if source_im.format not in ("JPEG","PNG"): raise RuntimeError("Not a JPEG/PNG photograph")
        width,height=source_im.size
        if not (min(width,height)>=350 and max(width,height)<=8000):
            raise RuntimeError("Unsupported photo dimensions")
        im=ImageOps.exif_transpose(source_im).convert("RGB")
    output=io.BytesIO()
    im.save(output,format="JPEG",quality=91,optimize=True,progressive=True)
    data=output.getvalue()
    with Image.open(io.BytesIO(data)) as verify:
        assert verify.format=="JPEG" and verify.size==im.size
        assert not verify.getexif().get(34853)
        verify.verify()
    DEST.parent.mkdir(parents=True,exist_ok=True)
    DEST.write_bytes(data)
    destsha=hashlib.sha256(data).hexdigest()
    s["images"].append({
      "file":"images/"+DEST.name,
      "role":"TRUE Anatherum glomeratum (Andropogon glomeratus var. glomeratus) flowering clusters from USGS Louisiana photo: visible dense silky heads, NOT measured spikelet dissection",
      "creator":AUTHOR,"license":"Public domain — U.S. Geological Survey",
      "license_url":"https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits",
      "source_page":SOURCE,"media_source_url":ORIGINAL,"source_determination":"Andropogon glomeratus var. glomeratus (USGS title/filename)",
      "source_locality":"Louisiana (USGS Plants of Louisiana photo), NOT a Hays County occurrence",
      "original_sha256":srcsha,"archived_sha256":destsha,
      "image_dimensions":[im.width,im.height],
      "photo_review":"USGS photo visibly reviewed for three dense flowering clusters. No botanically conclusive spathe/pedicelled spikelet macro. Original USGS species identification not independently vouchered.",
      "modifications":"EXIF/GPS stripped by decoded RGB JPEG re-encoding; no pixel-drawn arrows. Browser overlays preserved.",
      "public_reuse":"USGS image is a federal public-domain photograph; original credit retained."
    })
    for panel in panels:
        panel["image_url"]=LOCAL
        panel["photo_status"]="PHYSICALLY ARCHIVED USGS public-domain photo, real JPEG bytes SHA256 validated and EXIF/GPS stripped 2026-10-22. Original source labelled Andropogon glomeratus var. glomeratus; source is Louisiana, NO Hays provenance. Two browser arrows point ONLY to visible flowering clusters, NOT paired microscopic spikelets."
    s["photo_note"]+=" USGS Larry Allain public-domain true var. glomeratus seedhead JPEG now physically archived; two gross-visible arrows; no Hays locality or internal spathe macro claimed."
    s["curation_status"]["usgs_true_glomeratus_physical_20261022"]="ONE EXIF-free public-domain USGS photo installed; source original and resized sha256 in images[], original existing herbarium photo/rights preserved; 2 gross arrows only."
    g["curation_status"]["usgs_true_glomeratus_physical_20261022"]="Genus first panel points to physical USGS photo under bushy bluestem, no new taxon claims."
    assert json.dumps(g["project_scope"],sort_keys=True)==gp_scope
    assert all(json.dumps(s.get(k),sort_keys=True)==v for k,v in protected.items())
    with CSV.open(newline="",encoding="utf8") as f:
        reader=csv.DictReader(f);fieldnames=reader.fieldnames;rows=list(reader)
    if any(x.get("file_name")==DEST.name for x in rows):raise RuntimeError("Photo already in sources CSV")
    vals={"file_name":DEST.name,"role":"Official true var. glomeratus flowering clusters","creator":AUTHOR,
      "license":"Public domain (USGS federal)", "source_page":SOURCE,"direct_url":ORIGINAL,
      "study_use":"Public educational field identification","public_reuse":"YES; U.S. federal public domain",
      "license_url":"https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits",
      "modifications":"EXIF-free JPEG re-encode; browser overlay two gross cluster arrows"}
    rows.append({k:vals.get(k,"") for k in fieldnames})
    with CSV.open("w",newline="",encoding="utf8") as f:
        writer=csv.DictWriter(f,fieldnames=fieldnames,lineterminator="\n");writer.writeheader();writer.writerows(rows)
    write(SP,s);write(GP,g)
    write(REPORT,{"stage":"PHYSICALLY_ARCHIVED_USGS_TRUE_GLOMERATUS",
      "file":str(DEST),"source":ORIGINAL,"source_original_sha256":srcsha,"archived_sha256":destsha,
      "image_dimensions":[im.width,im.height],"creator":AUTHOR,"license":"USGS public domain",
      "species_panels":len(s["visual_comparison"]["items"]),"genus_panels":len(g["visual_comparison"]["items"]),
      "gross_arrows":2,"new_physical_photos":1,"native_range_unchanged":True,
      "remaining":["Match voucher-confirmed regional var. glomeratus macro of spathe/paired-raceme structure","1-mm sessile/pedicellate spikelet pair and awn","Separate BONAP target-counties re-audit"]})
    write(MARKER,{"type":"manual_field_id_publication","requested_at":"2026-10-22",
      "species":"Anatherum glomeratum","genus":"Anatherum",
      "title":"True bushy bluestem USGS public-domain flowering JPEG physical closeout",
      "source":ORIGINAL,"creator":AUTHOR,"license":"USGS public domain",
      "new_physical_image_files":1,"public_photo_requires_publication_workflow":True,
      "native_status_preserved":True,"stage":"FIELD_READY_PHOTO_GAPS"})
    print("PASS: physically archived true var. glomeratus USGS photo, source photo/CC metadata and original range protected")
if __name__=="__main__":main()
