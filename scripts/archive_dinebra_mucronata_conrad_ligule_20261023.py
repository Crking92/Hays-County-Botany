#!/usr/bin/env python3
"""Archive exactly one Jim Conrad original ligule/sheath hair photo of
source-identified Dinebra panicea subsp. mucronata (old Leptochloa name).
Copyright: Jim Conrad's own Backyard Nature photos expressly public-domain.
Image anatomy reviewed on original page; two broad markers, not tiny individual
papilla bases, no scale claim, no Texas voucher claim. Fail closed.
"""
from pathlib import Path
from io import BytesIO
import csv,hashlib,json
import requests
from PIL import Image,ImageOps

BASE=Path("content/taxa/Poaceae/Dinebra")
SP=BASE/"dinebra-panicea-subsp-mucronata/species.json"
GN=BASE/"genus.json"
CSV=SP.parent/"image-sources.csv"
DST=SP.parent/"images/jim-conrad-dinebra-mucronata-ligule-sheath-hairs-190322lg.jpg"
REPORT=Path("reports/dinebra-mucronata-conrad-original-ligule-20261023.json")
MARK=Path("workflow/field-id-publication/2026-10-23-dinebra-mucronata-conrad-ligule-one-photo.json")
PAGE="https://www.backyardnature.net/yucatan/sprangle.htm"
SOURCE="https://www.backyardnature.net/n/19/190322lg.jpg"
RIGHTS="https://www.backyardnature.net/j/copyrite.htm"
LICENSE="Public domain — Jim Conrad expressly dedicates his original Backyard Nature photographs"
TAXON="Dinebra panicea subsp. mucronata"
REGION="2019-03-22, Rancho Regensis, north of Valladolid, Yucatan, Mexico; Jim Conrad original field determination as Leptochloa panicea ssp. mucronata; NOT Texas/Hays voucher"
MARKERS=[
 {"label":"Pale ragged membranous ligule","label_x":2,"label_y":8,"target_x":46.5,"target_y":24.0},
 {"label":"Long white hairs on SHEATH","label_x":62,"label_y":90,"target_x":28.5,"target_y":67.0}
]
def save(p,obj):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf8")

def main():
 s=json.loads(SP.read_text(encoding="utf8"))
 g=json.loads(GN.read_text(encoding="utf8"))
 if s.get("id")!="dinebra-panicea-subsp-mucronata" or g.get("name")!="Dinebra":
  raise RuntimeError("Wrong canonical ID")
 if (len(s["images"]),len(s["visual_comparison"]["items"]),len(g["visual_comparison"]["items"]),s["curation_status"]["photo_files_present"])!=(6,10,10,6):
  raise RuntimeError("Concurrent canonical updates; refresh before archive")
 if DST.exists() or REPORT.exists() or MARK.exists() or any(x.get("source_image")==SOURCE for x in s["images"]):
  raise RuntimeError("Already present; no overwritten evidence or duplicates")
 protected={key:json.dumps(s.get(key),sort_keys=True) for key in
 ("id","family","genus","species","entry_type","infraspecific_rank","infraspecific_epithet",
  "scientific_name","common_name","taxonomy_source","synonyms","photo_taxonomy_note")}
 oldscope=json.dumps(g.get("project_scope"),sort_keys=True)
 with CSV.open(newline="",encoding="utf8") as f:
  reader=csv.DictReader(f);fields=list(reader.fieldnames or []);rows=list(reader)
 if "file_name" not in fields or any(r.get("file_name")==DST.name for r in rows):
  raise RuntimeError("Source CSV unexpected/duplicate")
 response=requests.get(SOURCE,timeout=40,headers={
  "User-Agent":"Hays-County-Botany-Public-Domain-Crew-Learner/1.0"})
 response.raise_for_status()
 raw=response.content
 if not(raw.startswith(b"\xff\xd8\xff") and 9000<len(raw)<4000000):
  raise RuntimeError("No genuine source JPEG returned")
 with Image.open(BytesIO(raw)) as old:
  old.load();dims=list(old.size)
  if old.format!="JPEG" or not(500<=old.width<=850 and 400<=old.height<=750 and 1.08<old.width/old.height<1.35):
   raise RuntimeError("Photographed source aspect/dimensions changed; marker coordinates require human recheck "+repr(dims))
  image=ImageOps.exif_transpose(old).convert("RGB")
  if list(image.size)!=dims:
   raise RuntimeError("EXIF photo orientation changed; do not retain unverified arrow positions")
 out=BytesIO()
 image.save(out,"JPEG",quality=94,optimize=True)
 payload=out.getvalue()
 if len(payload)<9000: raise RuntimeError("Photo archive too small")
 with Image.open(BytesIO(payload)) as test:
  assert test.format=="JPEG" and list(test.size)==dims and not test.getexif().get(34853)
  test.verify()
 if not all(0<=m[key]<=100 for m in MARKERS for key in ("label_x","label_y","target_x","target_y")):
  raise RuntimeError("Out of bounds marker")
 role="ACTUAL photographed opened leaf junction: pale jagged membranous ligule distinctly ABOVE long white leaf SHEATH hairs; exact mucronata source, not sibling brachiata; NO ruler"
 record={
  "file":"images/"+DST.name,"role":role,"creator":"Jim Conrad",
  "license":LICENSE,"license_url":RIGHTS,"source_page":PAGE,"source_image":SOURCE,
  "source_taxon_name":TAXON,
  "original_source_label":"Leptochloa panicea ssp. mucronata",
  "source_region":REGION,"source_type":"Original Backyard Nature March 22 2019 field account",
  "source_identification_evidence":"Original author describes the photo's upward-pointing papery jagged ligule, white sheath hairs, and identifies his plant as ssp. mucronata.",
  "original_sha256":hashlib.sha256(raw).hexdigest(),
  "archived_sha256":hashlib.sha256(payload).hexdigest(),
  "source_dimensions":dims,"archived_dimensions":dims,
  "public_reuse":"YES Jim Conrad original photograph, expressly public domain, original author and publication linked.",
  "modifications":"Source photograph converted to RGB JPEG with EXIF/GPS removed; non-destructive JSON overlays label only visible white ligule and visible long white SHEATH hairs. No photograph crop, fake ruler, or unverified single papilla-base arrow.",
  "photo_review":"Original 190322lg.jpg visually inspected: pale white ragged membranous ligule at upper blade/sheath junction and numerous long white hairs below along sheath. They are separate anatomical structures. No physical scale bar, no individual papilla-base resolution.",
  "archived_locally":True
 }
 panel={
  "label":"TRUE MUCRONATA LEAF COLLAR · jagged ligule vs separate white sheath hairs (two arrows)",
  "scientific_name":TAXON,
  "image_url":str(DST),"image_fit":"contain","image_role":role,
  "caption":"REAL source-labelled D. panicea subsp. mucronata (Jim Conrad, Yucatan 2019, original Leptochloa name). The upward projecting PALE, ragged-edged membranous LIGULE lies at the true inner leaf blade–sheath junction; the conspicuous LONG WHITE HAIRS are ON THE SHEATH BELOW, not themselves the ligule. The two broad arrows distinguish those visible structures. This image has NO millimeter ruler, and does NOT independently reveal individual swollen/papilla hair insertion points. It is NOT a Hays voucher. Photographer dedicated his own images to public domain.",
  "why_it_matters":"Critical crew ID distinction: membranous ligule vs long white sheath hairs. Actually photographed on the correct subspecies, unlike older photographed brachiata comparisons.",
  "creator":"Jim Conrad","license":LICENSE,"license_url":RIGHTS,
  "source_page":PAGE,"source_image":SOURCE,"source_taxon_name":TAXON,
  "source_region":REGION,"markers":MARKERS,
  "photo_status":"ORIGINAL correct subspecies true ligule and sheath hairs visible; two genuine broad-region arrows, no fake scale, no precise papilla insertion or ligule height claim."
 }
 s["images"].append(record)
 s["visual_comparison"]["items"].insert(2,panel)
 g["visual_comparison"]["items"].insert(2,json.loads(json.dumps(panel)))
 s["curation_status"]["photo_metadata_count"]=len(s["images"])
 s["curation_status"]["photo_files_present"]=7
 s["curation_status"]["dinebra_exact_mucronata_ligule_20261023"]={
  "one_real_correct_subspecies_original":True,
  "two_visible_structure_arrows":2,
  "source_author":"Jim Conrad","public_rights":"Public domain",
  "actual_true_ligule_visible":True,
  "actual_white_sheath_hairs_visible":True,
  "individual_papilla_hair_bases_resolved":False,
  "mm_scale_in_original":False,"Hays_voucher":False,
  "stage":"FIELD_READY_PHOTO_GAPS"
 }
 g["curation_status"]["dinebra_exact_mucronata_ligule_20261023"]={
  "new_real_species_collar_original":1,"new_visible_arrows":2,
  "genus_photo_panels":11,"photo_license":"Jim Conrad public domain",
  "still_needs_calibrated_true_ligule":True,"status":"FIELD_READY_PHOTO_GAPS"
 }
 s["visual_comparison"]["title"]="MUCRONATE SPRANGLETOP — exact target scaled spikelets AND actual membranous ligule"
 s["visual_comparison"]["subtitle"]="11 labelled panels. First target near-macro shows rulered spikelets, second NEW exact target shows distinct ragged true membranous ligule and separate white sheath hairs (two new broad arrows). Four Bob Harms frames remain OTHER SUBSPECIES brachiata, and two native Disakisperma comparison panels retain original arrows. Glume microtip, individual papilla bases and Texas local vouchering still gaps."
 g["visual_comparison"]["title"]=s["visual_comparison"]["title"]
 g["visual_comparison"]["subtitle"]=s["visual_comparison"]["subtitle"]
 s["field_id_finish_pass"]["stage"]="FIELD_READY_PHOTO_GAPS — source-confirmed D. panicea subsp. mucronata true membrane ligule and separate white sheath hairs now photographed and locally archived alongside rulered attached spikelets (4 new honest arrows across 2 correct-subspecies photos). Still need measured millimeter ligule, individually resolved raised sheath hair bases, microscopic upper-glume mucro and local Hays voucher."
 s["field_id_finish_pass"]["exact_subspecies_ligule_photo_20261023"]={
  "source":PAGE,"photo":SOURCE,"installed":True,
  "original_label":"Leptochloa panicea ssp. mucronata",
  "visible_anatomy":["pale irregular membranous ligule at real blade/sheathed junction","long white hairs borne on sheath below ligule"],
  "physical_mm_scale":False,
  "individual_sheath_hair_papilla_base_resolved":False,
  "gross_anatomy_markers":MARKERS,
  "next_photo_priorities":[
   "20–40x TRUE mature upper glume tiny short point (mucro) from source-verified subspecies with attached spikelet and 1-mm ruler",
   "10–20x original same-plant correct subspecies ligule pulled open with 1-mm ruler",
   "20–40x magnification of individual raised/papilla-based sheath hairs",
   "Rooted Hays specimen/voucher directly connected to flower head"
  ],
  "stage":"FIELD_READY_PHOTO_GAPS"
 }
 if isinstance(s.get("field_id_short_tiles"),list) and len(s["field_id_short_tiles"])==4:
  s["field_id_short_tiles"][2]["photo_status"]="TRUE source-verified MUCRONATA membranous ragged ligule and long SHEATH hairs photographed; original lacks 1-mm scale and individual papilla-base view"
  s["field_id_short_tiles"][2]["details"]="NEW direct photo 190322lg by Jim Conrad from source-labelled ssp. mucronata visibly separates the whitish ragged membranous ligule at leaf blade/sheath junction from long white sheath hairs BELOW; both have explicit accurate broad arrows. This original lacks a ruler: do not infer measured ligule height or minute bulbous hair insertion."
 if isinstance(g.get("quick_field_id_tiles"),list) and len(g["quick_field_id_tiles"])==4:
  g["quick_field_id_tiles"][2]["photo_status"]=s["field_id_short_tiles"][2]["photo_status"]
  g["quick_field_id_tiles"][2]["details"]=s["field_id_short_tiles"][2]["details"]
 s["field_id_sources"]=list(dict.fromkeys((s.get("field_id_sources") or [])+[PAGE,RIGHTS]))
 g["references"]=list(dict.fromkeys((g.get("references") or [])+[PAGE,RIGHTS]))
 if any(json.dumps(s.get(k),sort_keys=True)!=v for k,v in protected.items()):
  raise RuntimeError("Protected canonical taxonomy/aliases changed")
 if json.dumps(g.get("project_scope"),sort_keys=True)!=oldscope:
  raise RuntimeError("Genus project scope changed")
 if len(s["visual_comparison"]["items"])!=11 or len(g["visual_comparison"]["items"])!=11:
  raise RuntimeError("Incorrect newly installed photo count")
 row={
 "file_name":DST.name,"role":role,"creator":"Jim Conrad",
 "license":LICENSE,"source_page":PAGE,"direct_url":SOURCE,
 "study_use":"Public educational grass identification; credit author and original source",
 "public_reuse":"YES — original Jim Conrad image is expressly public domain"
 }
 rows.append({k:row.get(k,"") for k in fields})
 DST.parent.mkdir(parents=True,exist_ok=True)
 DST.write_bytes(payload)
 with CSV.open("w",newline="",encoding="utf8") as f:
  w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n")
  w.writeheader();w.writerows(rows)
 save(SP,s);save(GN,g)
 save(REPORT,{
  "result":"ONE_PUBLIC_DOMAIN_EXACT_SUBSPECIES_LIGULE_PHOTO_ARCHIVED",
  "species":TAXON,"source":PAGE,"source_image":SOURCE,
  "original_label":"Leptochloa panicea ssp. mucronata","creator":"Jim Conrad",
  "copyright_permission":RIGHTS,"photo_file":str(DST),
  "dimensions":dims,
  "original_sha256":record["original_sha256"],
  "archive_sha256":record["archived_sha256"],
  "new_originals":1,"new_visible_structure_arrows":2,
  "visible_broad_arrow_targets":["True jagged membranous ligule","Long white hairs on leaf sheath below"],
  "total_local_images":7,"species_panels":11,"genus_panels":11,
  "true_ligule_confirmed":True,"true_ligule_mm_measured":False,
  "single_papilla_base_confirmed":False,"microscopic_upper_glume_tip_confirmed":False,
  "geographic_voucher":"Yucatan source; not Texas",
  "status":"FIELD_READY_PHOTO_GAPS"
 })
 save(MARK,{
  "type":"manual_field_id_publication","date":"2026-10-23",
  "target":TAXON,"source":PAGE,"photo_count":1,
  "photographer":"Jim Conrad","license":"Public domain, no form required",
  "annotations":["Real pale jagged membranous ligule","Real white hairs on sheath below"],
  "unproven":["Ligule 1-mm height","Individual papilla hair insertion","Microscopic upper-glume mucro","Hays voucher"],
  "report":str(REPORT),"status":"FIELD_READY_PHOTO_GAPS",
  "publication":"normal rights-filtered GitHub Pages"
 })
 print("PASS one real PUBLIC DOMAIN exact mucronata ligule / sheath photo and TWO anatomically distinct arrows; missing tiny anatomy honestly retained",flush=True)

if __name__=="__main__":main()
