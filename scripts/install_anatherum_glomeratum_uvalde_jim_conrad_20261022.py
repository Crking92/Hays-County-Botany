#!/usr/bin/env python3
"""One-time fail-closed Jim Conrad Dry Frio Bushy Bluestem public-domain photo installer."""
import csv,hashlib,io,json,urllib.request
from pathlib import Path
from PIL import Image,ImageOps
ROOT=Path(".");BASE=ROOT/"content/taxa/Poaceae/Anatherum";SD=BASE/"anatherum-glomeratum"
SP=SD/"species.json";GP=BASE/"genus.json";CSV=SD/"image-sources.csv"
SOURCE_PAGE="https://backyardnature.net/n/h/andropog.htm"
LICENSE_URL="https://www.backyardnature.net/j/copyrite.htm"
FILES=[
("121028an.jpg","jim-conrad-uvalde-bushy-whole-clump.jpg","Whole clump and flowering culms at Dry Frio River"),
("121028ap.jpg","jim-conrad-uvalde-bushy-open-flowering.jpg","Flowering branches opened in hand; dense head formed from separate short units"),
("121028ao.jpg","jim-conrad-uvalde-bushy-hairy-dispersal.jpg","Actual silky mature dispersal structures, not a calibrated attached pair")
]
REPORT=ROOT/"reports/anatherum-glomeratum-jim-conrad-uvalde-import-20261022.json"
MARKER=ROOT/"workflow/field-id-publication/2026-10-22-anatherum-bushy-uvalde-three-physical-pd.json"

def write(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def main():
    s=json.loads(SP.read_text());g=json.loads(GP.read_text())
    assert s["id"]=="anatherum-glomeratum" and g["name"]=="Anatherum"
    assert g["project_scope"]["species_count"]==3
    assert len(s["historical_photo_exclusions"])==3
    assert any("usgs-larry-allain-glomeratum-flowering.jpg" in x.get("file","") for x in s["images"])
    expected={k:json.dumps(s.get(k),sort_keys=True) for k in ("project_inclusion","county_occurrences_target_zone","target_zone_count","native_target_zone_calculated","taxonomic_note","historical_photo_exclusions")}
    scope=json.dumps(g["project_scope"],sort_keys=True)
    ps=[];pg=[]
    for original,name,role in FILES:
        url="https://www.backyardnature.net/n/12/"+original
        matches=[next((x for x in obj["visual_comparison"]["items"] if x.get("source_image")==url),None) for obj in (s,g)]
        if any(x is None for x in matches):raise RuntimeError("Cannot find exact prepared photo role: "+original)
        for x in matches:
            if x.get("creator")!="Jim Conrad" or "Public domain" not in x.get("license","") or x.get("source_page")!=SOURCE_PAGE:
                raise RuntimeError("Source or license metadata changed: "+original)
            if len(x.get("markers",[]))!=2:raise RuntimeError("Expected two previously visually checked markers: "+original)
        ps.append(matches[0]);pg.append(matches[1])
    if all((SD/"images"/name).exists() for _,name,_ in FILES):
        if all(p["image_url"]==str(SD/"images"/name) for (_,name,_),p in zip(FILES,ps)) and all(p["image_url"]==str(SD/"images"/name) for (_,name,_),p in zip(FILES,pg)):
            assert all(any(i.get("file")=="images/"+name for i in s["images"]) for _,name,_ in FILES)
            print("Already installed, no-op")
            return
        raise RuntimeError("Existing JPEGs without synced cards; HOLD")
    if any((SD/"images"/name).exists() for _,name,_ in FILES):raise RuntimeError("Partial import, HOLD")
    for (original,name,_),p,q in zip(FILES,ps,pg):
        url="https://www.backyardnature.net/n/12/"+original
        if p["image_url"]!=url or q["image_url"]!=url:raise RuntimeError("Prepared source changed "+name)
        if any(img.get("file")=="images/"+name for img in s["images"]):raise RuntimeError("Duplicate destination "+name)
    pending=[]
    for original,name,role in FILES:
        url="https://www.backyardnature.net/n/12/"+original
        req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyPublicDomainBotanicalImage/1.0","Accept":"image/jpeg,image/*"})
        with urllib.request.urlopen(req,timeout=35) as response:
            raw=response.read(2_000_000)
        if not (10_000<len(raw)<2_000_000):raise RuntimeError("Unexpected nonphoto or oversized image "+original)
        source_sha256=hashlib.sha256(raw).hexdigest()
        with Image.open(io.BytesIO(raw)) as p:
            p.load()
            if p.format!="JPEG" or p.width<450 or p.height<350 or max(p.size)>4000:
                raise RuntimeError("Incorrect image format or dimension "+original+" "+str(p.size))
            processed=ImageOps.exif_transpose(p).convert("RGB")
        data_buffer=io.BytesIO()
        processed.save(data_buffer,format="JPEG",quality=92,optimize=True,progressive=True)
        jpeg=data_buffer.getvalue()
        with Image.open(io.BytesIO(jpeg)) as im:
            assert im.format=="JPEG" and im.size==processed.size and not im.getexif().get(34853)
            im.verify()
        pending.append((original,name,role,url,source_sha256,hashlib.sha256(jpeg).hexdigest(),jpeg,list(processed.size)))
    # All three source requests and validations succeed BEFORE any local mutation.
    with CSV.open(newline="",encoding="utf8") as f:
        reader=csv.DictReader(f);headers=reader.fieldnames;rows=list(reader)
    assert headers and "file_name" in headers
    if any(row.get("file_name") in {n for _,n,_ in FILES} for row in rows):
        raise RuntimeError("Sources CSV already contains destination")
    for i,(original,name,role,url,original_hash,archived_hash,jpeg,dimensions) in enumerate(pending):
        dest=SD/"images"/name
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(jpeg)
        file_rel="images/"+name
        s["images"].append({"file":file_rel,"role":role,"creator":"Jim Conrad",
            "license":"Public domain (express release by Jim Conrad)",
            "license_url":LICENSE_URL,"source_page":SOURCE_PAGE,"media_source_url":url,
            "source_determination":"Andropogon glomeratus, author-identified Dry Frio River Texas plant 2012-10-28; independent herbarium voucher absent",
            "source_locality":"Dry Frio River, Uvalde County, Texas","original_sha256":original_hash,
            "archived_sha256":archived_hash,"image_dimensions":dimensions,
            "photo_review":"Visible plant/habit, opened flowering branches or silky dispersal units confirmed from original Backyard Nature site; NOT 1mm dissected sessile+pedicellate spikelet pair.",
            "public_reuse":"Original photograph by website author Jim Conrad, expressly dedicated to public domain for reuse; author credit and original source retained",
            "modifications":"EXIF/GPS stripped by RGB JPEG reencode; six teaching arrows are browser overlays, not painted onto original pixels."})
        location=str(dest)
        for panel in (ps[i],pg[i]):
            panel["image_url"]=location
            panel["photo_status"]="Physically installed and resized/exif-cleaned: Jim Conrad public-domain Uvalde source image; SHA256 retained in images metadata. Two real visible-only gross arrows; no 1mm microscopic diagnosis. Not an independently specimen-vouchered native county record."
        vals={"file_name":name,"role":role,"creator":"Jim Conrad","license":"Public domain by author",
              "license_url":LICENSE_URL,"source_page":SOURCE_PAGE,"direct_url":url,
              "study_use":"Public crew botanical education","public_reuse":"Yes — author PD",
              "modifications":"Metadata-stripped JPEG, unretouched pixels, only browser arrow overlays"}
        rows.append({h:vals.get(h,"") for h in headers})
    with CSV.open("w",newline="",encoding="utf8") as f:
        w=csv.DictWriter(f,fieldnames=headers,lineterminator="\n");w.writeheader();w.writerows(rows)
    s["curation_status"]["jim_conrad_texas_physical_20261022"]="3 Uvalde author-public-domain JPEGs physically saved, 6 visible arrows, 5 current species JPEGs; microscopic 1mm photo remains missing"
    g["curation_status"]["jim_conrad_texas_physical_20261022"]="3 Uvalde author-public-domain JPEGs physically saved; genus 9 credited panels; 8 gross visible overlay arrows total"
    s["learner_visual_status"]["status"]="field_ready_photo_gaps"
    s["learner_visual_status"]["image_count"]=len(s["images"])
    assert json.dumps(g["project_scope"],sort_keys=True)==scope
    assert all(json.dumps(s.get(k),sort_keys=True)==v for k,v in expected.items())
    assert len(s["visual_comparison"]["items"])==6 and len(g["visual_comparison"]["items"])==9
    assert sum(len(p.get("markers",[])) for p in s["visual_comparison"]["items"])==8
    assert sum(len(p.get("markers",[])) for p in g["visual_comparison"]["items"])==8
    write(SP,s);write(GP,g)
    write(REPORT,{"result":"PHYSICALLY_INSTALLED_THREE_JIM_CONRAD_UVALDE_PHOTOS",
         "files":[{"file":"content/taxa/Poaceae/Anatherum/anatherum-glomeratum/images/"+n,
                   "url":url,"original_sha256":sh1,"archived_sha256":sh2,"dimensions":dims}
                  for _,n,_,url,sh1,sh2,_,dims in pending],
         "physical_new_files":3,"species_panels":6,"genus_panels":9,"visible_browser_arrows":8,
         "creator":"Jim Conrad","license":"Public domain by photographer",
         "native_zone_status_unchanged":True,"taxon_provenance_holds_preserved":True,
         "remaining":["1mm attached spikelet pair and pedicellate position","measured true spathe and rames","collar/ligule","BONAP native county range independently verified"]})
    write(MARKER,{"type":"manual_field_id_publication","date":"2026-10-22",
          "species":"Anatherum glomeratum","genus":"Anatherum",
          "title":"Three actual Uvalde Dry Frio River public-domain bushy bluestem photographs physically installed",
          "photos":3,"species_panels":6,"genus_panels":9,
          "source_page":SOURCE_PAGE,"license":"Jim Conrad public domain",
          "publication":"Request rights-filtered GitHub Pages after commit; marker is not deployment confirmation.",
          "status":"FIELD_READY_PHOTO_GAPS","native_status_unchanged":True})
    print("PASS: 3 source-exact Uvalde Jim Conrad PD JPEG images, 8 visible arrows total, science holds intact")

if __name__=="__main__":main()
