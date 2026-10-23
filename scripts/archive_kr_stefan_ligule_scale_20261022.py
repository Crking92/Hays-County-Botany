#!/usr/bin/env python3
"""Exact ONE species-level Bothriochloa ischaemum leaf-junction image from
Stefan.lefnaer CC BY-SA 4.0 on Wikimedia Commons, with original photographed
2mm reference. Austrian specimen is NOT var. songarica-vouchered Texas KR.
Provisional arrows point to real visible broad collar/ligule REGION and real
long hair tufts, not an individually proven free ligule tip.
"""
import csv,hashlib,io,json
from pathlib import Path
import requests
from PIL import Image,ImageOps

ROOT=Path(".")
BASE=ROOT/"content/taxa/Poaceae/Bothriochloa"
SP=BASE/"bothriochloa-ischaemum/species.json"
GN=BASE/"genus.json"
CSV=SP.parent/"image-sources.csv"
DST=SP.parent/"images/stefan-lefnaer-bothriochloa-ischaemum-sl1-collar-2mm.jpg"
REPORT=ROOT/"reports/kr-stefan-lefnaer-sl1-ligule-region-20261022.json"
MARK=ROOT/"workflow/field-id-publication/2026-10-22-kr-one-scaled-ligule-region-photo.json"
SOURCE="https://upload.wikimedia.org/wikipedia/commons/a/ab/Bothriochloa_ischaemum_sl1.jpg"
PAGE="https://commons.wikimedia.org/wiki/File:Bothriochloa_ischaemum_sl1.jpg"
LIC="CC BY-SA 4.0"
LIC_URL="https://creativecommons.org/licenses/by-sa/4.0/"
CREATOR="Stefan.lefnaer"
REGION="Lower Austria, Austria (19 September 2015); species-level Bothriochloa ischaemum, NOT a Texas King Ranch var. songarica voucher"
MARKERS=[
 {"label":"Collar / ligule zone (not isolated tip)","label_x":2,"label_y":16,"target_x":50,"target_y":48},
 {"label":"Real hairs beside junction","label_x":68,"label_y":10,"target_x":55,"target_y":38}
]

def save(p,obj):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def main():
 s=json.loads(SP.read_text(encoding="utf-8"))
 g=json.loads(GN.read_text(encoding="utf-8"))
 if s.get("id")!="bothriochloa-ischaemum" or g.get("name")!="Bothriochloa":
  raise RuntimeError("Incorrect canonical target")
 if (len(s["images"]),len(s["visual_comparison"]["items"]),len(g["visual_comparison"]["items"]),s["curation_status"]["photo_files_present"])!=(8,17,12,6):
  raise RuntimeError("Concurrent canonical change; refresh; no partial changes")
 if DST.exists() or REPORT.exists() or MARK.exists() or any(i.get("source_page")==PAGE for i in s["images"]):
  raise RuntimeError("Already installed; no duplicate")
 protected={k:json.dumps(s.get(k),sort_keys=True) for k in
            ("id","scientific_name","authority","synonyms","project_inclusion",
             "county_occurrences_target_zone","native_target_zone_calculated",
             "target_zone_count","native_metrics_excluded","taxonomic_note")}
 oldscope=json.dumps(g.get("project_scope"),sort_keys=True)
 with CSV.open(newline="",encoding="utf-8") as f:
  reader=csv.DictReader(f);cols=list(reader.fieldnames or []);rows=list(reader)
 if "file_name" not in cols or any(x.get("file_name")==DST.name for x in rows):
  raise RuntimeError("Unexpected photo source CSV")
 r=requests.get(SOURCE,timeout=40,headers={"User-Agent":"HaysBotanyEducationalPhotoResearch/1.0","Accept":"image/jpeg,image/*"})
 r.raise_for_status();raw=r.content
 if not (raw.startswith(b"\xff\xd8\xff") and 30000<len(raw)<7000000):
  raise RuntimeError("Real source JPEG not available")
 with Image.open(io.BytesIO(raw)) as original:
  original.load();dims=tuple(original.size)
  if original.format!="JPEG" or not (dims[0]==2568 and dims[1]==1989):
   raise RuntimeError("Original source dimensions changed; refuse inaccurate annotated arrows")
  clean=ImageOps.exif_transpose(original).convert("RGB")
 out=io.BytesIO();clean.save(out,format="JPEG",quality=92,optimize=True)
 payload=out.getvalue()
 if len(payload)<30000: raise RuntimeError("Too few archived photo bytes")
 with Image.open(io.BytesIO(payload)) as check:
  assert check.format=="JPEG" and check.size==dims
  assert not check.getexif().get(34853)
  check.verify()
 for m in MARKERS:
  for k in ("label_x","label_y","target_x","target_y"):
   if not (0<=m[k]<=100):raise RuntimeError("Invalid marker coordinates")
 role="TRUE B. ischaemum leaf junction with photographer's 2mm reference; ligule region and hairs; NO identifiable free membrane tip"
 record={
  "file":"images/"+DST.name,"role":role,
  "creator":CREATOR,"license":LIC,"license_url":LIC_URL,
  "source_page":PAGE,"source_image":SOURCE,
  "source_taxon_name":"Bothriochloa ischaemum",
  "source_determination_level":"SPECIES, photographed Austrian taxon; not local songarica",
  "source_region":REGION,"source_type":"Wikimedia Commons original author photograph",
  "original_sha256":hashlib.sha256(raw).hexdigest(),
  "archived_sha256":hashlib.sha256(payload).hexdigest(),
  "source_original_dimensions":list(dims),"archived_dimensions":list(dims),
  "modifications":"Original RGB JPEG re-encoded and EXIF/GPS removed; reversible two broad non-destructive overlay markers; no crop or invented anatomical structures",
  "photo_review":"Original full-frame source visually inspected; at 2mm reference scale collar region and hairs are visible, but opened 0.5–1.5mm ciliate free ligule edge cannot be defined pixel-exactly.",
  "anatomy_arrows":"Two broad visible real features: collar/ligule zone and long hairs, not precise free membrane edge",
  "public_reuse":"YES CC BY-SA 4.0 with creator, file source, changes & ShareAlike license credited",
  "archived_locally":True
 }
 panel={
  "label":"TRUE LEAF JUNCTION — real 2mm reference, source species (Austria), provisional arrows",
  "scientific_name":"Bothriochloa ischaemum",
  "image_url":str(DST),"image_fit":"contain","image_role":role,
  "caption":"A genuine species-determined B. ischaemum close-up from Austria. The photographer included an actual 2-mm reference bar in the image. Upper purple-green leaf/sheath margin meets a pale leaf/junction near the conspicuous cluster of translucent hairs. Arrows mark the broad collar/ligule ZONE and long hair group, NOT an exact unseen free membranous ligule edge. This is NOT a Texas var. songarica specimen, nor a calibrated lifted 0.5–1.5-mm true ligule in the same Hays plant.",
  "why_it_matters":"Demonstrates where a true ligule lives anatomically and shows real hairs near the collar at an actual photographed reference; unlike leaf-edge hairs in native little bluestem, the diagnosis still needs same-plant tissue and papilla insertions.",
  "creator":CREATOR,"license":LIC,"license_url":LIC_URL,
  "source_page":PAGE,"source_image":SOURCE,"source_taxon_name":"Bothriochloa ischaemum",
  "source_region":REGION,"markers":MARKERS,
  "photo_status":"PROVISIONAL species-level European source. 2-mm scale real; exact free ligule membrane margin obscured; two gross structure arrows validated at source full-frame orientation; site CC BY-SA 4.0 attribution and changes."
 }
 s["images"].append(record);s["visual_comparison"]["items"].append(panel);g["visual_comparison"]["items"].append(dict(panel))
 s["curation_status"]["photo_metadata_count"]=9
 s["curation_status"]["photo_files_present"]=7
 s["curation_status"]["kr_one_true_scaled_leaf_junction_20261022"]={
  "real_source_jpegs":1,"total_stored_kr_photos":7,"added_gross_arrows":2,
  "region":"Austria, not Texas", "source_scale":"photographer 2 mm", 
  "exact_tip_unresolved":True,"status":"FIELD_READY_PHOTO_GAPS"}
 g["curation_status"]["kr_species_level_scaled_ligule_region_20261022"]={
  "one_real_scaled_photo":True,"panels":13,"new_broad_anatomical_arrows":2,
  "source_region":"Austria, source species", "local_variety_not_verified":True,
  "true_free_edge_still_missing":True}
 s["visual_comparison"]["subtitle"] += " One true species-level Austrian collar photo with original 2-mm reference newly stored and broadly arrowed; still NOT a Texas verified free ligule-tip macro."
 s["field_photo_quickcheck"]["featured_photo_indices"].insert(5,17)
 steps=s["field_photo_quickcheck"]["steps"]
 if len(steps)<4 or not steps[3].startswith("4."):
  raise RuntimeError("Crew lesson steps changed, abort")
 steps[3]=(
 "4. LEAF JUNCTION & LIGULE ZONE — NEW photo 18 is a genuine B. ischaemum species-level Austrian close-up with a REAL 2-mm reference and two broad arrows to collar/ligule zone and visible translucent hairs. Contrast TRUE inner ligule membrane with outside sheath-edge hairs. The exact free ciliate membrane edge is NOT isolated or measurable here, nor is the photographed specimen a Texas songarica voucher. Hays KR same-plant rulered opened margin remains HOLD."
 )
 s["field_id_finish_pass"]["stage"]=(
 "FIELD_READY_PHOTO_GAPS — includes original Jim Conrad Uvalde KR hair tufts AND species-level Stefan.lefnaer leaf junction with real 2-mm reference, two broad arrows each. Requires actual Texas var. songarica opened free 0.5–1.5mm ciliate ligule, individually resolved papilla-based blade hairs, and same-voucher attached sessile/pedicelled spikelet pair."
 )
 s["field_id_finish_pass"]["next_photo_priority"]=[
 "Hays Texas KR var songarica 10-20x photographed pulled-open 0.5–1.5mm true short-ciliate membranous ligule free margin beside 1mm ruler",
 "Hays KR 20-40x separately visible individual raised-base stiff hairs on upper blade above collar",
 "Hays KR real attached sessile fertile and pedicelled partner and awn on same flowering raceme, source linked to rooted adult"
 ]
 s["field_id_finish_pass"]["species_level_austrian_ligule_region_one_photo_20261022"]={
  "source":PAGE,"real_scale_bar":"2 mm","exact_ligule_edge_confirmed":False,
  "original_photo_arrows":MARKERS,"status":"FIELD_READY_PHOTO_GAPS"}
 assert all(json.dumps(s.get(k),sort_keys=True)==v for k,v in protected.items())
 assert json.dumps(g.get("project_scope"),sort_keys=True)==oldscope
 newrow={"file_name":DST.name,"role":role,"creator":CREATOR,"license":LIC,
  "license_url":LIC_URL,"source_page":PAGE,"direct_url":SOURCE,
  "study_use":"Public educational learner with anatomy source caveat",
  "public_reuse":"YES CC BY-SA 4.0 with attribution and ShareAlike",
  "modifications":record["modifications"]}
 rows.append({key:newrow.get(key,"") for key in cols})
 DST.parent.mkdir(parents=True,exist_ok=True);DST.write_bytes(payload)
 with CSV.open("w",newline="",encoding="utf-8") as f:
  writer=csv.DictWriter(f,fieldnames=cols,lineterminator="\n");writer.writeheader();writer.writerows(rows)
 save(SP,s);save(GN,g)
 save(REPORT,{
  "result":"ONE_REAL_2MM_SPECIES_LEVEL_LIGULE_ZONE_PHOTO_ARCHIVED",
  "species":"Bothriochloa ischaemum","not_Texas_songarica_voucher":True,
  "source":PAGE,"original":SOURCE,"creator":CREATOR,"license":LIC,
  "physical_file":str(DST),"source_dimensions":list(dims),
  "original_sha256":record["original_sha256"],"archived_sha256":record["archived_sha256"],
  "one_photo_added":1,"two_broad_arrows":2,"species_panels":18,"genus_panels":13,
  "local_species_photo_files":7,
  "gaps":["Same-plant Texas KR 0.5–1.5mm opened free ligule edge with mm scale",
          "Raised papillose hairs on Texas KR leaf with sufficient magnification",
          "Same-local-voucher paired sessile and pedicelled spikelets"],
  "status":"FIELD_READY_PHOTO_GAPS"})
 save(MARK,{"type":"manual_field_id_publication","date":"2026-10-22",
  "species":"Bothriochloa ischaemum","scope":"One real Austrian species-level scaled ligule zone photo + two gross original-pixel arrows",
  "report":str(REPORT),"source_specific_photo":PAGE,
  "rights":"CC BY-SA 4.0 credited","stage":"FIELD_READY_PHOTO_GAPS",
  "publish":"NORMAL_RIGHTS_FILTERED_GITHUB_PAGES"})
 print("SUCCESS: one real original 2mm leaf collar source, CC BY-SA verified, 2 broad arrow markers; Texas ligule tip hold retained",flush=True)

if __name__=="__main__":main()
