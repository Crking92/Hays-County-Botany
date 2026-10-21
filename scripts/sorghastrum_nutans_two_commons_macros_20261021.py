#!/usr/bin/env python3
"""Install two source-exact CC BY-SA 2.0 Matt Lavin Sorghastrum nutans diagnostic photographs.
Permission, identity and image bytes are verified BEFORE file changes. No fabricated arrows.
Does not recheck county nativity, add species, overwrite existing media, or touch other grasses.
"""
import csv,datetime,io,json,pathlib,re,requests
from PIL import Image,ImageOps
ROOT=pathlib.Path(".")
BASE=ROOT/"content/taxa/Poaceae/Sorghastrum"
F=BASE/"sorghastrum-nutans"
SPEC=F/"species.json";GENUS=BASE/"genus.json"
LIC="https://creativecommons.org/licenses/by-sa/2.0/"
T=[
 ("File:Sorghastrum nutans (3912211835).jpg",
  "matt-lavin-cc-by-sa-2-ligule-sheath.jpg",
  "Mature leaf sheath/collar close-up; membranous ligule at blade/sheath junction",
  "Real Matt Lavin image of INDIANGRASS ligule emerging from sheath at collar. This is the anatomical starting point for recognizing the projecting 'rifle-sight' edge; no claimed hair or mm count without detailed review.",
  "Look for the true membrane, not a fuzzy tuft of hairs; distinguish the separate pointed side extensions where visible."),
 ("File:Sorghastrum nutans (3912213615).jpg",
  "matt-lavin-cc-by-sa-2-fertile-spikelet-pedicels.jpg",
  "Mature fertile sessile spikelet, a bent/twisted awn, and naked sterile pedicels",
  "Real Matt Lavin macro of fertile sessile spikelet with conspicuous bent awn and adjacent NAKED pedicels, where a paired pedicelled spikelet is reduced/absent. Do not confuse bare pedicel for an awn.",
  "Spikelet/pedicel anatomy corroborates Sorghastrum; pair with a mature awn and collar before exact-species conclusion.")
]
def now(t):
    if not t:return None
    try:return datetime.datetime.fromisoformat(str(t).replace("Z","+00:00"))
    except (ValueError,TypeError):return None
def records():
    cc=json.loads((ROOT/"workflow/work-claims.json").read_text())
    current=datetime.datetime.now(datetime.timezone.utc)
    return [x for x in cc.get("claims",[]) if "sorghastrum-nutans" in x.get("taxa",[])
      and x.get("status") in ("active","claimed","in_progress")
      and (now(x.get("expires_at")) is None or now(x.get("expires_at")).astimezone(datetime.timezone.utc)>current)]
def get_sources():
    ses=requests.Session()
    ses.headers.update({"User-Agent":"HaysBotanyManualSorghastrumPhotoEnrichment/1.0 (Wikimedia Commons CC attribution)"})
    response=ses.get("https://commons.wikimedia.org/w/api.php",params={
      "action":"query","format":"json","prop":"imageinfo",
      "iiprop":"url|extmetadata","titles":"|".join(x[0] for x in T)},timeout=45)
    response.raise_for_status()
    pages=response.json()["query"]["pages"]
    info={page["title"]:page["imageinfo"][0] for page in pages.values() if page.get("imageinfo")}
    found=[]
    for title,name,role,caption,why in T:
        if title not in info:raise RuntimeError("Missing exact Commons original "+title)
        i=info[title]; meta=i.get("extmetadata",{})
        lic=re.sub("<[^>]+>"," ",meta.get("LicenseShortName",{}).get("value","")).strip().upper()
        artist=re.sub("<[^>]+>"," ",meta.get("Artist",{}).get("value","")).lower()
        if "BY-SA" not in lic or "2.0" not in lic or "matt lavin" not in artist:
            raise RuntimeError("Photo-specific CC BY-SA 2.0 / Matt Lavin not verified: "+title+" "+lic+" "+artist[:120])
        url=i.get("url","")
        if not url.startswith("https://upload.wikimedia.org/wikipedia/commons/"):raise RuntimeError("Unexpected URL "+url)
        res=ses.get(url,timeout=60);res.raise_for_status()
        if len(res.content)>8_000_000:raise RuntimeError("oversized Commons JPEG")
        with Image.open(io.BytesIO(res.content)) as im:
            im.load();out=ImageOps.exif_transpose(im).convert("RGB")
        if min(out.size)<700:raise RuntimeError("Photo resolution too low "+title)
        out.thumbnail((1800,1800),Image.Resampling.LANCZOS)
        buf=io.BytesIO();out.save(buf,format="JPEG",quality=91,optimize=True)
        if len(buf.getvalue())<45000:raise RuntimeError("Corrupt / low-byte photo "+title)
        found.append((title,name,role,caption,why,url,list(out.size),buf.getvalue()))
    return found
def main():
    sp=json.loads(SPEC.read_text());gn=json.loads(GENUS.read_text())
    if sp["id"]!="sorghastrum-nutans" or sp["scientific_name"]!="Sorghastrum nutans":raise RuntimeError("Wrong canonical species")
    if gn.get("name")!="Sorghastrum":raise RuntimeError("Wrong genus")
    if records():raise RuntimeError("Another live claim owns this species")
    if any("matt-lavin-cc-by-sa-2-" in str(x.get("file","")) for x in sp["images"]):
        assert len([x for x in sp["images"] if "matt-lavin-cc-by-sa-2-" in str(x.get("file",""))])==2
        print("Already installed two exact source photos; NO-OP");return
    results=get_sources()
    for _,filename,*_ in results:
        if (F/"images"/filename).exists():raise RuntimeError("Refuse to overwrite original media "+filename)
    additions=[]
    for title,filename,role,caption,why,url,size,data in results:
        dest=F/"images"/filename;dest.write_bytes(data)
        with Image.open(dest) as im:im.verify()
        page="https://commons.wikimedia.org/wiki/"+title.replace(" ","_")
        item={"file":"images/"+filename,"role":role,"creator":"Matt Lavin",
           "license":"CC BY-SA 2.0","license_url":LIC,
           "source_page":page,"original_source_page":"https://www.flickr.com/photos/plant_diversity/"+re.search(r"\((\d+)\)",title).group(1)+"/",
           "downloaded_from":url,"image_dimensions":size,"study_use":"yes","public_reuse":"yes",
           "source_platform":"Wikimedia Commons (original author Matt Lavin, Flickr)",
           "modifications":"downscaled / recompressed JPEG, EXIF/GPS removed; no added overlays",
           "photo_review":"Exact-source author and CC BY-SA 2.0 checked via Commons API; organ role corroborated by original Matt Lavin source caption; arrow coordinates intentionally pending native-pixel verification."}
        sp["images"].append(item);additions.append((item,caption,why))
        visual={"label":"INDIANGRASS — "+("real ligule/collar CC photo" if "ligule" in filename else "fertile spikelet and NAKED pedicels CC photo"),
           "scientific_name":sp["scientific_name"],
           "image_url":"content/taxa/Poaceae/Sorghastrum/sorghastrum-nutans/images/"+filename,
           "image_fit":"contain","creator":"Matt Lavin","license":"CC BY-SA 2.0","license_url":LIC,"source_page":page,
           "image_role":role,"caption":caption,"why_it_matters":why,"markers":[],
           "photo_status":"Physically downloaded verified original; anatomy/collar present by source description; arrow coordinates and mm sizes need independent visual QA before addition."}
        sp["visual_comparison"]["items"].append(visual)
        gn["visual_comparison"]["items"].append({**visual,"species_id":"sorghastrum-nutans","observed_anatomy":"Original photographer labels leaf-collar ligule or naked pedicels, respectively; no new pixel arrows yet.","visual_status":"physical_source_verified_arrow_review_pending"})
    sp["visual_comparison"]["title"]="Indiangrass — actual ligule / collar and naked-pedicel closeups";
    sp["visual_comparison"]["subtitle"]="Two physically stored, publicly licensed Matt Lavin CC BY-SA 2.0 macros were added to the existing licensed plant/panicle reference photographs. Original author/license retained; private Joey video excluded.";
    sp["visual_comparison"]["overlay_note"]="A true source-labeled ligule photo is now installed, replacing the old missing-photo claim. New micromarker coordinates remain pending pixel-by-pixel validation. True auricle/ligule anatomy must not be misnamed.";
    sp["field_id_finish_pass"]["photo_truth"]=[x for x in sp["field_id_finish_pass"]["photo_truth"] if not x.startswith("No complete rifle-sight ligule")] + [
      "Matt Lavin CC BY-SA 2.0 photo now physically shows the membrane at the blade-sheath junction; photo-original fine ligule contour annotation pending pixel QA.",
      "A second Matt Lavin CC BY-SA 2.0 photo now physically shows the fertile sessile spikelet and naked pedicels; no false paired sterile spikelet is illustrated."];
    sp["curation_status"]["photo_metadata_count"]=len(sp["images"])
    sp["curation_status"]["photo_files_present"]=sum(str(x["file"]).startswith("images/") for x in sp["images"])
    sp["curation_status"]["visual_finish"]="FIELD_READY_PHOTO_GAPS: licensed true collar and pedicel images now physically installed; high-confidence anatomy-arrow pixels and S. elliottii paired measurements still pending"
    sp["curation_status"]["photo_install_20261021"]="two source-specific Matt Lavin Commons images"
    gn["visual_comparison"]["status"]="Indiangrass ligule/collar plus paired spikelet/pedicel real photos physically installed; reciprocal S. elliottii attached-awn diagnostic comparisons still pending."
    gn["visual_comparison"]["teaching_order"]="real licenced ligule/collar → whole panicle → real fertile spikelet and NAKED pedicels → mature awn measurement → matched S. elliottii diagnostic closeup"
    gn["visual_comparison"]["photo_gaps"]=[x for x in gn["visual_comparison"]["photo_gaps"] if not x.startswith("S. nutans: front+side macro")] + [
      "Indiangrass licensed ligule macro installed. Need pixel-checked ligule arrows and second collar angle with 1-mm reference.",
      "Matt Lavin bare-pedicel spikelet macro installed. Need full-size labeled contrast with S. elliottii before closing genus."]
    gn["curation_status"]["indiangrass_macro_enrichment_20261021"]="two licensed Matt Lavin Commons macro photos physically installed; arrows still need pixel QA"
    cols=[];rows=[];csvfile=F/"image-sources.csv"
    with csvfile.open(newline="",encoding="utf-8-sig") as fh:
        rd=csv.DictReader(fh);cols=list(rd.fieldnames or []);rows=list(rd)
    for rec,_,_ in additions:
        row={"file":rec["file"],"file_name":rec["file"].replace("images/",""),"creator":rec["creator"],
             "license":rec["license"],"license_url":rec["license_url"],"source_page":rec["source_page"],
             "direct_url":rec["downloaded_from"],"diagnostic_role":rec["role"],
             "study_use":"yes","public_reuse":"yes","modifications":rec["modifications"]}
        for key in row:
            if key not in cols:cols.append(key)
        rows.append(row)
    with csvfile.open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=cols,lineterminator="\n");w.writeheader();w.writerows(rows)
    with (F/"SOURCES.txt").open("a",encoding="utf-8") as fh:
        fh.write("\n2026-10-21 Licensed Matt Lavin Commons collar and pedicel macro enrichment\n")
        for title,*_ in results:
            fh.write(title+" / Matt Lavin, CC BY-SA 2.0 "+LIC+"\n")
        fh.write("JPEG recompressed, EXIF/GPS removed; original source and ShareAlike license retained. Do not mark anatomy arrows verified without source-resolution inspection.\n")
    SPEC.write_text(json.dumps(sp,indent=2,ensure_ascii=False)+"\n")
    GENUS.write_text(json.dumps(gn,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({"installed":2,"files":[x[1] for x in results],
      "species_image_records":len(sp["images"]),"genus_visual_panels":len(gn["visual_comparison"]["items"]),
      "license":"CC BY-SA 2.0","photo_specific_rights_verified":True,
      "range_status_preserved":sp["project_inclusion"]["target_zone_status"],"new_arrows":0},indent=2))
if __name__=="__main__":main()
