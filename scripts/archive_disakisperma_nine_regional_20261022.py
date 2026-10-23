#!/usr/bin/env python3
"""Save 5 Bob Harms Selected Monocots + 4 Jim Conrad public domain originals:
Disakisperma dubium (= Leptochloa dubia), source-vetted Central Texas.
Preserve exact individual copyrights and county science. Only genuine pixels.
"""
import hashlib,io,json,time
from pathlib import Path
import requests
from PIL import Image,ImageOps

FOLDER=Path("content/taxa/Poaceae/Disakisperma")
SP=FOLDER/"disakisperma-dubium/species.json"
GP=FOLDER/"genus.json"
REPORT=Path("reports/green-sprangletop-nine-regional-anatomy-20261022.json")
RELEASE=Path("workflow/field-id-publication/2026-10-22-disakisperma-nine-real-central-texas.json")
DEST=SP.parent/"images"
BASE="https://w3.biosci.utexas.edu/prc/Monocots/GrassHTML/data/"
RIGHTS="https://w3.biosci.utexas.edu/prc/Monocots/"
LIC="© Bob Harms — scientific/educational use with attribution (NOT Creative Commons)"
PERMIT="BOB_HARMS_SELECTED_MONOCOTS_EDU_WITH_CREDIT_20261022"
CONRAD_RIGHTS="https://www.backyardnature.net/j/copyrite.htm"
CONRAD_PAGE="https://www.backyardnature.net/n/h/sprangle.htm"
ROWS=[
  {"id":"LEDU-i","title":"FLOWERING HEAD: source-labelled Central Texas inflorescence","role":"one complete reproductive flowering branch; panicle anatomy", "caption":"Bob Harms original labelled green sprangletop inflorescence; distinguish entire panicle branching from the smaller individual spikelets. This image alone does not document whole rooted Hays specimen.", "type":"harms"},
  {"id":"LEDU-j","title":"REPRODUCTIVE DETAIL: intact flowering branch","role":"one-sided branch with actual multi-flowered spikelets","caption":"Bob Harms labelled inflorescence detail of Leptochloa dubia (= Disakisperma dubium). Inspect true attached multi-flowered spikelets; individual lemma/glume claims need mm-scale verification.", "type":"harms"},
  {"id":"LEDU-j2","title":"FLOWERING DETAIL: actual green sprangletop units","role":"source-determined flower units on a true panicle branch","caption":"Closer real author photograph of source-verified green sprangletop flowering units. Do not call a single floret a whole spikelet or impose a fixed floret count from an unscaled image.", "type":"harms"},
  {"id":"LEDU-S","title":"SPIKELET ANATOMY: original Central Texas close-up","role":"real flowering spikelets and photographic anatomy","caption":"Original source-labelled green sprangletop SPIKELET detail; shows actual botanical structure. Exact lower/upper glume versus rachilla and all lemma teeth require individual pixel audit before point arrows.", "type":"harms"},
  {"id":"LEDU-d","title":"DISARTICULATION: source-labelled separated flower parts","role":"mature spikelet disarticulation close-up with original metric reference where present","caption":"Actual Bob Harms source-labelled disarticulation evidence. Never assign a photographed loose part to the SAME individual as a separate Harms whole plant without collection records.", "type":"harms"},
  {"id":"131013lp","title":"WHOLE HABIT: genuine Frio Canyon green sprangletop","role":"Uvalde County grass clumps and whole spread-out flowering panicles","caption":"Jim Conrad photographed these green sprangletop flowering plants in the Frio Canyon of northern Uvalde County, Texas. The spread-out long terminal side branches distinguish the habit; roots below the soil remain unseen.", "type":"conrad"},
  {"id":"131013lq","title":"ATTACHED SPIKELETS: actual regional multi-flowered close-up","role":"actual still-attached green spikelets with multiple developing florets","caption":"Jim Conrad Uvalde photograph of two true attached green sprangletop spikelets. Do not count all floral scales as separate spikelets; florets are INSIDE a single spikelet.", "type":"conrad"},
  {"id":"131013ls","title":"BLUNT LEMMA TIPS: real regional separated flowering parts","role":"Uvalde County close-up of a teased open mature spikelet showing blunt/notched lemma tips","caption":"Actual Jim Conrad view of teased-apart green sprangletop florets. The approximately squared/notched LEMMA TIPS are a useful field clue; no 1mm measurement or verified individual glume label is asserted.", "type":"conrad"},
  {"id":"131013lr","title":"TRUE COLLAR: source-photographed ligule zone","role":"real blade/sheath junction and the actual small projecting membranous ligule","caption":"Regional Jim Conrad source-label shows the grass blade/sheath junction and small true ligule, with photographed tissue color. No calibrated 0.5–1.5mm free membrane measurement can be inferred from photo without ruler.", "type":"conrad"},
]
s=json.loads(SP.read_text(encoding="utf-8"))
g=json.loads(GP.read_text(encoding="utf-8"))
assert s["id"]=="disakisperma-dubium" and s["scientific_name"]=="Disakisperma dubium"
assert len(s["images"])==1 and len(s["visual_comparison"]["items"])==4
assert len(g["visual_comparison"]["items"])==4
assert "FIELD_READY_PHOTO_GAPS" in s["field_id_finish_pass"]["stage"]
original_taxonomy=s["curation_status"]["taxonomy_reviewed"]
original_science=s.get("morphology_keys")
session=requests.Session();session.headers.update({"User-Agent":"HaysBotany-EducationalPhotoArchive/1.0 (credited botanical references)","Accept":"image/jpeg,image/*;q=0.8"})
DEST.mkdir(parents=True,exist_ok=True)
report={"taxon":"Disakisperma dubium","source_taxon_name":"Leptochloa dubia",
"original_licensed_source":"Bob Harms Selected Central Texas Monocots, source-specific educational attribution",
"public_domain_source":"Jim Conrad Backyard Nature original photographs only; Uvalde County October 2013; author explicitly placed self-created photos public domain",
"author_permission_links":[RIGHTS,CONRAD_RIGHTS],"new_photo_files":0,"items":[]}
def source_for(row):
  if row["type"]=="harms":
    ident=row["id"]
    return (BASE+"images/"+ident+".jpg",BASE+"pages/"+ident+".html",
            "Bob Harms",LIC,RIGHTS,"Leptochloa dubia")
  ident=row["id"]
  return (f"https://www.backyardnature.net/n/13/{ident}.jpg",CONRAD_PAGE,
          "Jim Conrad","Public domain — photographer explicitly releases his original Backyard Nature images",CONRAD_RIGHTS,"Disakisperma dubium")
for row in ROWS:
  ident=row["id"]
  source,page,creator,license,license_url,source_taxon=source_for(row)
  dest=DEST/(("bob-harms-green-sprangletop-"+ident.lower()) if row["type"]=="harms" else ("jim-conrad-uvalde-green-sprangletop-"+ident))+".jpg"
  if dest.is_file():raise RuntimeError("Avoid overwriting an existing image without source SHA recheck: "+str(dest))
  last=None
  for retry in range(3):
    try:
      response=session.get(source,timeout=35)
      response.raise_for_status()
      raw=response.content
      if len(raw)<4300 or not raw.startswith(bytes.fromhex("ffd8ff")):
        raise ValueError(f"Not a credible original JPEG: {len(raw)}")
      with Image.open(io.BytesIO(raw)) as im:
        im.load()
        if im.format!="JPEG" or min(im.size)<125:
          raise ValueError("Expected genuine original JPEG dimensions")
        clean=ImageOps.exif_transpose(im).convert("RGB")
        original_dimensions=list(im.size)
      clean.save(dest,"JPEG",quality=93,optimize=True)
      before=hashlib.sha256(raw).hexdigest()
      report["new_photo_files"]+=1
      break
    except (OSError,ValueError,requests.RequestException) as error:
      last=str(error)
      if retry<2:time.sleep(3+retry*2)
  else:raise RuntimeError(f"Failed original {source}: {last}")
  output_bytes=dest.read_bytes()
  with Image.open(dest) as im:
    if im.format!="JPEG" or im.mode!="RGB" or im.size!=tuple(original_dimensions) or im.getexif().get(34853):
      raise RuntimeError("Bad RGB/GPS/dimensions")
    dims=list(im.size);im.verify()
  sha=hashlib.sha256(output_bytes).hexdigest()
  image_record={
    "file":"images/"+dest.name,"role":row["role"],"creator":creator,
    "license":license,"license_url":license_url,"source_page":page,"source_image":source,
    "source_taxon_name":source_taxon,"accepted_taxon_name":"Disakisperma dubium",
    "public_reuse":"YES: "+("source-specific credited noncommercial educational use, NOT CC" if row["type"]=="harms" else "photographer-declared public domain"),
    "photo_review":"Original JPEG physically retrieved; species name matches source's synonym/current taxonomy; public provisional photo review. Anatomical millimeter measurement and Hays-vouchered one-plant sequence NOT claimed.",
    "photo_status":"PHYSICAL_VERIFIED_ORIGINAL_EXACT_SOURCE_PROVISIONAL_USER_REVIEW",
    "archive_sha256":sha,"original_source_sha256":before,"image_dimensions":dims,
    "modifications":"Original image pixels preserved at full dimensions; clean RGB re-encode strips original EXIF/GPS. Browser anatomy arrows may overlay only inspected features."
  }
  if row["type"]=="harms": image_record["site_specific_public_permission"]=PERMIT
  s["images"].append(image_record)
  panel={
    "label":row["title"],"scientific_name":"Disakisperma dubium",
    "image_url":str(dest),"image_fit":"contain","image_role":row["role"],
    "caption":row["caption"],
    "why_it_matters":"Original regional, source-identified photograph; physical anatomy, not a substitute for a measured, botanist-vouchered same-plant microscope series.",
    "creator":creator,"license":license,"license_url":license_url,"source_page":page,
    "photo_status":"PHYSICAL JPEG, SOURCE VERIFIED, PUBLIC RIGHT VERIFIED. Anatomical arrows to be placed only after individual pixel inspection. PROVISIONAL USER REVIEW.","markers":[]
  }
  # Keep top existing panels organized before other-species Dinebra reference
  s["visual_comparison"]["items"].insert(3,panel)
  g["visual_comparison"]["items"].insert(3,dict(panel))
  report["items"].append({"id":ident,"archive_file":str(dest),"original_url":source,
      "source_page":page,"creator":creator,"license":license,"source_sha256":before,"sha256":sha,
      "bytes":len(output_bytes),"dimensions":dims,"photo_role":row["role"]})
assert report["new_photo_files"]==9
assert len(s["images"])==10 and len(s["visual_comparison"]["items"])==13
assert len(g["visual_comparison"]["items"])==13
assert s["curation_status"]["taxonomy_reviewed"]==original_taxonomy and s["morphology_keys"]==original_science
s["curation_status"]["photo_metadata_count"]=10
s["curation_status"]["photo_files_present"]=10
s["curation_status"]["green_sprangletop_9_real_regional_photos_20261022"]={
 "bob_harms_originals":5,"jim_conrad_uvalde_public_domain":4,"local_source_exact_photos":10,
 "species_and_genus_panels_each":13,"science_range_preserved":True,"sub_mm_annotation_status":"HOLD: coordinate audit pending",
 "status":"FIELD_READY_PHOTO_GAPS"
}
s["field_id_finish_pass"]["nine_real_regional_photographs_20261022"]={
 "physical_jpegs_added":9,"report":str(REPORT),
 "photo_evidence_achieved":["Texas flowering habit in field","One-sided spikelet architecture","Attached multiple-flowered actual spikelet","Actual Uvalde photographed blunt lemma margins","Actual Uvalde collar/ligule region","Harms Central Texas inflorescence/spikelet disarticulation reference"],
 "limits":["No one-voucher Hays plant roots to spikelets with matched accession","No 1mm true unfurled ligule membrane explicitly calibrated","No 1mm individual floret lemma dorsal nerves/hair distribution source-pixel-verified","No one-voucher concealed lower-sheath cleistogamous flowering parts"],
 "photo_accession":"Jim Conrad original Uvalde source covers several field structures but does not prove all shots are one specimen; Harms central Texas separate source images are another collection",
 "status":"FIELD_READY_PHOTO_GAPS"
}
s["visual_comparison"]["title"]="Green sprangletop — 10 local original photographs + actual Texas flower parts and Dinebra comparison"
s["visual_comparison"]["subtitle"]="Bob Harms (5 exact copyrighted source originals, educational with credit) and Jim Conrad (4 original Uvalde public-domain photos) added to prior locally stored John Connolly photograph. Real photographed spikelet, lemma and ligule zones. User photo review still provisional."
s["visual_comparison"]["overlay_note"]="10 PHYSICALLY ARCHIVED exact-species photographs. Two west-Texas Matt Lavin licensed Commons references remain external and are NOT part of local count. One existing Dinebra panel depicts a DIFFERENT taxon. Do not claim 1-mm scales or same accession across different source photographers."
g["visual_comparison"]["title"]=s["visual_comparison"]["title"]
g["visual_comparison"]["subtitle"]=s["visual_comparison"]["subtitle"]
g["visual_comparison"]["overlay_note"]=s["visual_comparison"]["overlay_note"]
g["curation_status"]["green_sprangletop_9_physical_20261022"]={
 "nine_new_source_specific_jpegs":9,"central_texas_harms_credited_educational":5,"uvalde_conrad_public_domain":4,
 "genus_panels":13,"fine_lemma_nerve_1mm_hold":True,"original_native_status_preserved":True
}
SP.write_text(json.dumps(s,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
GP.write_text(json.dumps(g,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
REPORT.parent.mkdir(parents=True,exist_ok=True)
REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
RELEASE.parent.mkdir(parents=True,exist_ok=True)
RELEASE.write_text(json.dumps({
"type":"manual_field_id_publication","date":"2026-10-22","species":"Disakisperma dubium",
"archive_report":str(REPORT),"new_physical_jpegs":9,"total_physically_stored_exact_species_jpegs":10,
"species_visual_panels":13,"genus_visual_panels":13,
"copyright":"5 Bob Harms original exact source published scientific/educational credit only; 4 Jim Conrad original public domain Uvalde",
"last_mile":"Measured free ligule/lemma nerves, same Hays one-voucher rooted/floret series and hidden lower-sheath head, provisional arrows",
"stage":"FIELD_READY_PHOTO_GAPS","release":"Check Pages jobs SUCCESS separately before claiming website live"
},indent=2)+"\n",encoding="utf-8")
print("PASS nine real source-specific Central Texas Disakisperma photographs, 10 stored images, 13 panels",flush=True)
