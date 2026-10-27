#!/usr/bin/env python3
"""Source-verifiable real rooted crown specimens for Bothriochloa torreyana.

ONLY two GBIF PRESERVED_SPECIMEN records whose specific media are CC0 are
eligible. The University of Texas sheets have a visibly conflicting
"copyright reserved" legend despite GBIF BY metadata: DO NOT archive them.
Use the original image's photographed structures, not simulated roots.
"""
import hashlib,io,json
from pathlib import Path
import requests
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parents[1]
REL="content/taxa/Poaceae/Bothriochloa/bothriochloa-torreyana"
CARD=ROOT/REL/"species.json"
REPORT=ROOT/"reports/silver-real-vouchered-roots-20261027.json"
MARKER=ROOT/"workflow/field-id-publication/2026-10-27-silver-rooted-vouchers-public-photos.json"
SOURCE=[
 {"gbif":2242356292,"inst":"DBG","catalog":"KHD00064634",
  "file":"silver-denver-gardens-vouchered-roots-cc0-20261027.jpg",
  "creator":"Denver Botanic Gardens, Kathryn Kalmbach Herbarium (KHD)",
  "locale":"Haswell Cemetery, Kiowa County, Colorado, USA",
  "title":"TRUE ROOTED SILVER — herbarium plant with actual crown and fibrous roots",
  "caption":"Genuine photo of a preserved B. torreyana specimen with an attached basal crown and visibly exposed fibrous roots. The specimen is labeled KHD00064634 from Kiowa County, Colorado. The roots remain physically connected to the shoots; this is not just a dense clump in the field. Herbarium scale bar present on the full sheet, but the root close-up is not itself a 1-mm microdissection. Do NOT claim rhizomes or underground runners from this photo.",
  "markers":[{"label":"Attached basal crown","label_x":57,"label_y":63,"target_x":49,"target_y":78},{"label":"Exposed fibrous roots","label_x":8,"label_y":89,"target_x":48,"target_y":84}]},
 {"gbif":4976689107,"inst":"US","catalog":"US 3759758",
  "file":"silver-smithsonian-nm-vouchered-roots-cc0-20261027.jpg",
  "creator":"Ingrid P. Lin / Smithsonian National Museum of Natural History",
  "locale":"McGregor Range, Otero County, New Mexico, USA",
  "title":"TRUE ROOTED SILVER — Smithsonian verified taxon and connected roots",
  "caption":"Genuine Smithsonian preserved specimen B. laguroides subsp. torreyana, US 3759758, New Mexico: basal shoots meet at a photographed crown with attached excavated roots. Some stems on the sheet are folded and taped; the crown and true roots are not a stylized drawing. An independently confirmed local living Texas rhizome arrangement is still needed, and this is NOT a ligule or reproductive microdissection.",
  "markers":[{"label":"Rooted basal crown","label_x":66,"label_y":76,"target_x":53,"target_y":85},{"label":"Attached true roots","label_x":14,"label_y":95,"target_x":56,"target_y":91}]}
]
UA={"User-Agent":"Hays-County-Botany-photo-archive/1.0 (CC0 herbarium educational)"}
def main():
    sess=requests.Session();sess.headers.update(UA)
    s=json.loads(CARD.read_text(encoding="utf-8"))
    assert s["id"]=="bothriochloa-torreyana"
    result={"date":"2026-10-27","species":"Bothriochloa torreyana","before":len(s["images"]),
            "excluded_UT_license_mismatch":"GBIF CC BY media vs physical sheet legend copyright reserved; NOT downloaded or republished",
            "specimens":[]}
    added=[]
    for spec in SOURCE:
      try:
        d=sess.get(f"https://api.gbif.org/v1/occurrence/{spec['gbif']}",timeout=25)
        d.raise_for_status();r=d.json()
        if r.get("basisOfRecord")!="PRESERVED_SPECIMEN" or "torreyana" not in r.get("scientificName","").lower():raise RuntimeError("not a torreyana preserved specimen")
        if r.get("institutionCode")!=spec["inst"] or r.get("catalogNumber")!=spec["catalog"]:raise RuntimeError("specimen institution/catalog changed")
        media=[x for x in r.get("media",[]) if "creativecommons.org/publicdomain/zero/" in str(x.get("license",""))]
        if not media:raise RuntimeError("no exact CC0 photo media")
        if not ("creativecommons.org/publicdomain/zero/" in str(r.get("license",""))):raise RuntimeError("record itself is not CC0")
        origin=media[0]["identifier"]
        if not origin.startswith("https://"):raise RuntimeError("source host not HTTPS")
        resp=sess.get(origin,timeout=45)
        if resp.status_code==429:raise RuntimeError("rate limited original source")
        resp.raise_for_status()
        if len(resp.content)>24_000_000 or len(resp.content)<150_000:raise RuntimeError("binary size unusual")
        with Image.open(io.BytesIO(resp.content)) as original:
          rgb=ImageOps.exif_transpose(original).convert("RGB")
          rgb.load()
        if rgb.width<1300 or rgb.height<1800:raise RuntimeError("source not high-resolution full sheet")
        if max(rgb.size)>3000:rgb.thumbnail((3000,3000),Image.Resampling.LANCZOS)
        dest=ROOT/REL/"images"/spec["file"]
        dest.parent.mkdir(parents=True,exist_ok=True)
        rgb.save(dest,"JPEG",quality=89,optimize=True,subsampling=0)
        with Image.open(dest) as again:
          if again.getexif():raise RuntimeError("EXIF/GPS still present")
          again.verify()
        sha=hashlib.sha256(dest.read_bytes()).hexdigest()
        lic="CC0 1.0 (individual GBIF media; no copyright restrictions)"
        licenseurl="https://creativecommons.org/publicdomain/zero/1.0/"
        gbifurl=f"https://www.gbif.org/occurrence/{spec['gbif']}"
        relative="images/"+spec["file"]
        data={"file":relative,"role":"Actual physically attached fibrous roots and perennial crown on voucher specimen",
            "creator":spec["creator"],"license":lic,"license_url":licenseurl,
            "source_page":gbifurl,"source_media_url":origin,
            "public_reuse":"yes, source image individually CC0 public-domain; institutional attribution retained",
            "study_use":"yes","photo_status":"PHYSICALLY ARCHIVED CC0, source-specific voucher, original real photographed crown and roots. Nonlocal dried sheet; no inference of rhizome/ligule.",
            "source_voucher":spec["catalog"],"source_institution":spec["inst"],"source_locality":spec["locale"],
            "source_scientific_name":r["scientificName"],"source_gbif_id":spec["gbif"],
            "archive_sha256":sha,"image_dimensions":list(rgb.size),
            "modifications":"JPEG downsampled, EXIF/GPS stripped; original authentic voucher background retained"}
        panel={"label":spec["title"],"scientific_name":"Bothriochloa torreyana",
            "image_url":REL+"/"+relative,"image_fit":"contain",
            "image_role":"Preserved specimen original, actual rooted base and flowering shoots",
            "caption":spec["caption"],"why_it_matters":"The basal shoots and ACTUAL exposed roots now connect on the same botanically cataloged plant; useful to field learners distinguishing clump bases from unrooted stems.",
            "creator":spec["creator"],"license":lic,"license_url":licenseurl,"source_page":gbifurl,
            "source_gbif_id":spec["gbif"],"markers":spec["markers"],
            "photo_status":"ACTUAL PHOTO. Two broad real visible root/crown arrows; no underground rhizome claim. Original specimen CC0."}
        if not any(x.get("file")==relative for x in s["images"]):s["images"].append(data)
        if not any(x.get("source_gbif_id")==spec["gbif"] for x in s["visual_comparison"]["items"]):s["visual_comparison"]["items"].append(panel)
        result["specimens"].append({"gbif":spec["gbif"],"result":"ARCHIVED","file":str(dest.relative_to(ROOT)),
            "original":origin,"license":lic,"sha256":sha,"pixels":list(rgb.size),"arrows":2})
        added.append(spec["gbif"])
      except Exception as e:
        result["specimens"].append({"gbif":spec["gbif"],"result":"HOLD","reason":str(e)[:400]})
    if added:
      s["curation_status"]["photo_metadata_count"]=len(s["images"])
      s["curation_status"]["photo_files_present"]=len(s["images"])
      s["curation_status"]["visual_finish"]="FIELD_READY_PHOTO_GAPS — genuine connected basal crown and roots now photographed on individually CC0 archived voucher sheets; true opened free ligule and 1-mm fully attached paired spikelet dissection still missing."
      s["silver_public_domain_rooted_vouchers_20261027"]={
        "archived_gbif_ids":added,"real_attached_exposed_roots":True,
        "nonlocal_real_preserved_specimen_not_living_local":True,
        "license":"Individual media verified CC0 (Denver Botanic Gardens, Smithsonian)",
        "ut_sheets_rights_conflict_hold":True,
        "new_verified_visible_arrows":2*len(added),
        "still_missing":["Opened 1-mm free ligule on source-verified silver","Actual calibrated microscopic attached sessile and pedicelled spikelet pair"],
        "status":"FIELD_READY_PHOTO_GAPS"}
      if s.get("silver_six_role_photo_score_20261027",{}).get("total")==4:
        roles=s["silver_six_role_photo_score_20261027"]
        roles["roles"][0]["score"]=1
        roles["roles"][0]["reason"]="Max Licher shows flowering bunch; genuine Denver/Smithsonian cataloged source-identified silver herbarium originals now also visibly show attached crown and exposed root system. Preserved nonlocal specimens, not living Texas dug roots or an independently proven rhizome trait."
        roles["total"]=4.5;roles["pct"]=75;roles["remaining_pct"]=25
        roles["target_70pct_needed_additional_role_points"]=0
        roles["target_80pct_needed_additional_role_points"]=0.3
        roles["target_90pct_needed_additional_role_points"]=0.9
        roles["status"]="4.5/6 verified public photo role equivalents (75%). True measured free ligule and intact paired-spikelet microstructure remain missing."
      s["learner_visual_status"]["public_photographs_physically_archived"]=9+len(added)
      s["learner_visual_status"]["image_count"]=len(s["images"])
      s["learner_visual_status"]["public_gallery_panels"]=len(s["visual_comparison"]["items"])
      s["learner_visual_status"]["total_photo_arrows"]=sum(len(p.get("markers",[])) for p in s["visual_comparison"]["items"])
      s["learner_visual_status"]["note"]="New source-verified CC0 actual rooted specimen photography from Colorado and NM: leafy flowering stems with true attached crown and root system. Distinct from local live plant rhizome questions. Actual measured free ligule and paired reproductive microdissection still missing."
      s["field_id_short_tiles"][1]["details"]="Finally, physical CC0 Denver Botanic Gardens and Smithsonian source-vouchered silver herbarium photographs show actual EXPOSED ROOTS attached to BASAL SHOOT CROWNS, unlike the earlier Arizona standing clump with its roots hidden. The complete real specimens are from Colorado and New Mexico respectively; do NOT claim verified Hays County live rhizomes or stolons from preserved-root pictures. Trace upper flowering shoots down through the shared shoot base into attached roots. Native silver is typically bunch-forming; short rhizome reports vary among regional floras."
      s["field_id_short_tiles"][1]["status"]="ROOTED PHOTO ROLE NOW COVERED: two CC0 cataloged true plant-root sheets plus original Arizona flowering clump; local living rhizome form still unresolved"
      s["field_id_short_tiles"][1]["photo_panel_indices"]=list(range(len(s["visual_comparison"]["items"])-len(added),len(s["visual_comparison"]["items"])))+[6]
      s["field_photo_quickcheck"]["steps"][1]="2 · CONFIRM A REAL CONNECTED CROWN: new Denver Botanic Gardens and Smithsonian preserved-silver specimen photographs show attached actual basal roots, unlike an undug roadside clump. Compare the Arizona living flowering bunch. This does not settle whether a local Texas stand has any short rhizomes."
      s["field_photo_quickcheck"]["warning"]="CC0 real herbarium vouchers now complete the uprooted/rooted-base learning PHOTO role. The free 1–3 mm INNER ligule membrane and a true attached sessile/pedicelled spikelet pair with 1-mm measurements are STILL not photographed in cleared macros. CC BY-NC and external restricted rights remain source-specific."
      CARD.write_text(json.dumps(s,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
      MARKER.parent.mkdir(parents=True,exist_ok=True)
      MARKER.write_text(json.dumps({"date":"2026-10-27","taxon":"bothriochloa-torreyana","archived_real_root_vouchers":added,
        "photographic_score":s["silver_six_role_photo_score_20261027"]["pct"],
        "original_exif_removed":True,"visible_root_markers":2*len(added),
        "UT_media_use_hold":"Printed copyright reserved conflicts with metadata; no use",
        "site_release":"Run standard noncommercial site photo and width QA"},indent=2)+"\n")
    result["installed_count"]=len(added);result["archive_count_after"]=len(s["images"])
    result["panels_after"]=len(s["visual_comparison"]["items"])
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
