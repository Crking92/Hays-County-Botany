#!/usr/bin/env python3
"""Archive ONE genuine source-determined Dinebra panicea subsp. mucronata
spikelet photo, with real ruler, from Jim Conrad's original Yucatan field
account. Conrad expressly dedicates his own Backyard Nature images to
PUBLIC DOMAIN. Fail closed; no guessed tiny glume-tip mucro arrow.
"""
from pathlib import Path
from io import BytesIO
import csv,hashlib,json
import requests
from PIL import Image,ImageOps

BASE=Path("content/taxa/Poaceae/Dinebra")
SP=BASE/"dinebra-panicea-subsp-mucronata/species.json"
GEN=BASE/"genus.json"
CSV=SP.parent/"image-sources.csv"
DEST=SP.parent/"images/jim-conrad-dinebra-mucronata-yucatan-mm-spikelets-190322ld.jpg"
REPORT=Path("reports/dinebra-mucronata-one-jim-conrad-mm-spikelet-20261023.json")
MARK=Path("workflow/field-id-publication/2026-10-23-dinebra-mucronata-one-original-mm-spikelet.json")
PAGE="https://www.backyardnature.net/yucatan/sprangle.htm"
ORIGINAL="https://www.backyardnature.net/n/19/190322ld.jpg"
PERMISSION="https://www.backyardnature.net/j/copyrite.htm"
SOURCE_IDENTIFICATION="Leptochloa panicea ssp. mucronata"
TAXON="Dinebra panicea subsp. mucronata"
LICENSE="Public domain — Jim Conrad expressly dedicates his original Backyard Nature photographs"
REGION="Rancho Regensis, near Valladolid, Yucatan, Mexico, March 22, 2019, 20.876N 88.170W; identified as ssp. mucronata by original photographer; not a Texas specimen"
MARKERS=[
 {"label":"Real attached spikelet cluster","label_x":56,"label_y":10,"target_x":40.5,"target_y":40.5},
 {"label":"Actual millimeter ruler ticks","label_x":3,"label_y":92,"target_x":24.5,"target_y":69.0}
]
def save(path,obj):
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf8")

def main():
 s=json.loads(SP.read_text(encoding="utf8"))
 g=json.loads(GEN.read_text(encoding="utf8"))
 if s.get("id")!="dinebra-panicea-subsp-mucronata" or g.get("name")!="Dinebra":
  raise RuntimeError("Incorrect canonical species or genus")
 if (len(s["images"]),len(s["visual_comparison"]["items"]),len(g["visual_comparison"]["items"]),s["curation_status"]["photo_files_present"])!=(5,9,9,5):
  raise RuntimeError("Concurrent card changes, abort")
 if any(x.get("source_image")==ORIGINAL or x.get("source_page")==PAGE for x in s["images"]) or DEST.exists() or REPORT.exists() or MARK.exists():
  raise RuntimeError("Original already archived or publication marker already present")
 protected={k:json.dumps(s.get(k),sort_keys=True) for k in
   ("id","family","genus","species","entry_type","infraspecific_rank",
    "infraspecific_epithet","scientific_name","common_name","taxonomy_source",
    "synonyms","photo_taxonomy_note")}
 scope=json.dumps(g.get("project_scope"),sort_keys=True)
 with CSV.open("r",newline="",encoding="utf8") as stream:
  rd=csv.DictReader(stream);fields=rd.fieldnames or [];rows=list(rd)
 if "file_name" not in fields or any(row.get("file_name")==DEST.name for row in rows):
  raise RuntimeError("Bad source CSV/duplicate row")
 response=requests.get(ORIGINAL,timeout=35,
    headers={"User-Agent":"Hays-County-Botany-Crew-Educational-Public-Domain-Original/1.0"})
 response.raise_for_status()
 raw=response.content
 if not raw.startswith(b"\xff\xd8\xff") or not 18000<len(raw)<3500000:
  raise RuntimeError("Original Yucatan image URL did not deliver valid substantial JPEG")
 with Image.open(BytesIO(raw)) as original:
  original.load()
  if original.format!="JPEG" or not (650<=original.width<=720 and 560<=original.height<=630):
   raise RuntimeError("Expected 679x589 original source orientation; exact arrow check blocked "+repr(original.size))
  dims=list(original.size)
  clean=ImageOps.exif_transpose(original).convert("RGB")
 out=BytesIO();clean.save(out,format="JPEG",quality=94,optimize=True)
 encoded=out.getvalue()
 if len(encoded)<16000: raise RuntimeError("Archival JPEG too small")
 with Image.open(BytesIO(encoded)) as img:
  assert img.format=="JPEG" and list(img.size)==dims
  assert not img.getexif().get(34853)
  img.verify()
 for m in MARKERS:
  for key in ("label_x","label_y","target_x","target_y"):
   if not (0<=m[key]<=100):raise RuntimeError("Bad percentage annotation")
 record={
  "file":"images/"+DEST.name,
  "role":"EXACT ssp. mucronata attached tiny mature/immature spikelets beside REAL millimeter ruler; photographed 2019 Yucatan; glume mucro NOT individually resolved",
  "creator":"Jim Conrad","license":LICENSE,"license_url":PERMISSION,
  "source_page":PAGE,"source_image":ORIGINAL,
  "source_taxon_name":TAXON,"source_original_identification":SOURCE_IDENTIFICATION,
  "source_region":REGION,"source_type":"Original photographer's field newsletter and image",
  "source_identification_evidence":"Original https://www.backyardnature.net/yucatan/sprangle.htm paragraph explicitly states 'ours being ssp. mucronata'. Photo is directly embedded in that account.",
  "original_sha256":hashlib.sha256(raw).hexdigest(),"archived_sha256":hashlib.sha256(encoded).hexdigest(),
  "source_original_dimensions":dims,"archived_dimensions":dims,
  "modifications":"Original photo RGB JPEG re-encoded with EXIF/GPS stripped. Two non-destructive annotation overlays indicate the visible attached spikelet cluster and physical millimeter ruler; no inferred glume/mucro arrow.",
  "public_reuse":"YES; original photographer expressly dedicated own Backyard Nature images to public domain; creator credited.",
  "photo_review":"Source photograph visibly shows green and pink small spikelets on branch near a physical diagonal ruler with dark mm graduation lines. The minuscule mucronate glume point is NOT resolved; photograph does not prove separate fertile lemma measurement.",
  "archived_locally":True
 }
 panel={
  "label":"TARGET MUCRONATA: actual spikelets beside real mm ruler — Jim Conrad, Yucatan (two arrows)",
  "scientific_name":TAXON,"image_url":str(DEST),"image_fit":"contain",
  "image_role":record["role"],
  "caption":"AUTHENTIC original Dinebra panicea subsp. mucronata (as Leptochloa panicea ssp. mucronata), Jim Conrad, Yucatan, March 2019. On the left is a real diagonal millimeter ruler; on the right, individual small spikelets REMAIN ATTACHED to a slender raceme branch. Two gross-region arrows point to those visible features. The original account identifies the actual subspecies, unlike the four nearby Harms comparison photos of subsp. brachiata. The actual UPPER GLUME TINY MUCRO is NOT independently resolved, and it is not a Texas voucher. Public domain by creator's express dedication.",
  "why_it_matters":"First actual published original mucronata close-up that ties the target subspecies to a real millimeter reference and individual spikelets without substituting sibling brachiata. Teaches field crew real flowering scale; next required extreme-macro is upper glume tip with a lens.",
  "creator":"Jim Conrad","license":LICENSE,"license_url":PERMISSION,
  "source_page":PAGE,"source_image":ORIGINAL,
  "source_taxon_name":TAXON,"source_region":REGION,
  "markers":MARKERS,
  "photo_status":"SOURCE-IDENTIFIED exact subspecies, genuine physical ruler and branch spikelets. No false mucronate glume tip arrow; not a locally Hays-vouchered specimen."
 }
 s["images"].append(record)
 s["visual_comparison"]["items"].insert(1,panel)
 g["visual_comparison"]["items"].insert(1,json.loads(json.dumps(panel)))
 s["curation_status"]["photo_metadata_count"]=len(s["images"])
 s["curation_status"]["photo_files_present"]=6
 s["curation_status"]["dinebra_exact_mucronata_mm_spikelet_20261023"]={
  "physically_archived_true_subspecies_photo":1,
  "author":"Jim Conrad","source_page":PAGE,"license":"PUBLIC DOMAIN",
  "actual_ruler_in_same_original_photo":True,"two_verified_visible_arrows":True,
  "mucronate_glume_tip_micro_not_resolved":True,
  "not_texas_voucher":True,"stage":"FIELD_READY_PHOTO_GAPS"
 }
 g["curation_status"]["dinebra_exact_mucronata_mm_spikelet_20261023"]={
  "new_exact_subspecies_photo":1,"species_panels":10,"genus_panels":10,
  "new_visual_arrow_count":2,
  "glume_apex_still_missing_at_20x":True,
  "license":"Jim Conrad public domain",
  "stage":"FIELD_READY_PHOTO_GAPS"
 }
 s["visual_comparison"]["title"]="MUCRONATE SPRANGLETOP — actual target ruler spikelets plus sibling brachiata comparison"
 s["visual_comparison"]["subtitle"]="TEN panels: original target seedhead + NEW genuine ssp. mucronata attached spikelets beside mm ruler (2 arrows), 2 other-grass comparisons, 4 properly labeled subsp. brachiata comparison photographs, 2 native green sprangletop diagnostic photos. The terminal upper glume MUCRO tip is NOT visibly resolved; any CC BY-NC originals remain subject to public filter."
 g["visual_comparison"]["title"]=s["visual_comparison"]["title"]
 g["visual_comparison"]["subtitle"]=s["visual_comparison"]["subtitle"]
 s["field_id_finish_pass"]["stage"]="FIELD_READY_PHOTO_GAPS — ONE authentic author-labelled D. panicea subsp. mucronata original photographed with genuine mm ruler and attached small spikelets now archived with 2 broad real arrows. Fine upper-glume mucro still not resolved. True ssp. mucronata measured inner membranous ligule, papillate-based sheath hairs, same-plant Texas rooted habit and subspecies voucher still missing."
 s["field_id_finish_pass"]["exact_subspecies_spikelet_photo_20261023"]={
  "source":PAGE,"original":ORIGINAL,
  "verified_actual_source_subspecies":"Leptochloa panicea ssp. mucronata",
  "current_taxon":TAXON,"ruler_real":True,
  "spikelet_attached_to_flowering_branch":True,
  "glume_tip_mucro_pixel_confirmed":False,
  "exact_subspecies_photograph_installed":True,
  "two_gross_visible_arrows":MARKERS,
  "next_photo_candidates":[
   "https://www.backyardnature.net/n/19/190322lf.jpg",
   "https://www.backyardnature.net/n/19/190322lg.jpg"
  ],
  "candidate_notes":"Same original labelled mucronata specimen: former shows two-floret spikelets, latter a short jagged membranous true ligule with nearby white sheath hairs; each must be separately archived, credited and annotated only after source-pixel review."
 }
 if isinstance(s.get("field_id_short_tiles"),list) and len(s["field_id_short_tiles"])==4:
  s["field_id_short_tiles"][3]["photo_status"]="NEW EXACT MUCRONATA GENUINE SPIKELETS + MM RULER now photographed; glume tiny mucro remains too small to resolve."
  s["field_id_short_tiles"][3]["details"]+=" Real Jim Conrad subspecies-determined Yucatan source photo is now archived with a TRUE ruler next to attached spikelets. Use photo panel 2 to see actual size, but do not identify an individual glume-tip mucro from that image."
 if isinstance(g.get("quick_field_id_tiles"),list) and len(g["quick_field_id_tiles"])==4:
  g["quick_field_id_tiles"][3]["photo_status"]="Actual subspecies photographed with real mm ruler! Glume mucro not resolved; source from Yucatan not Hays."
 if isinstance(s["field_id_finish_pass"].get("critical_photo_gaps"),list):
  s["field_id_finish_pass"]["critical_photo_gaps"]=[
   "MATURE UPPER GLUME MUCRONATE TIP: the installed original does not individually resolve its small point at 20–40x, and subspecies differential caryopsis remains unphotographed.",
   *[x for x in s["field_id_finish_pass"]["critical_photo_gaps"] if "SPIKELET MACRO" not in x and "UPPER GLUME MACRO" not in x]
  ]
 s["field_id_sources"]=list(dict.fromkeys((s.get("field_id_sources") or [])+[PAGE,PERMISSION]))
 g["references"]=list(dict.fromkeys((g.get("references") or [])+[PAGE,PERMISSION]))
 for k,v in protected.items():
  if json.dumps(s.get(k),sort_keys=True)!=v:
   raise RuntimeError("Protected canonical taxonomy and range altered:"+k)
 if json.dumps(g.get("project_scope"),sort_keys=True)!=scope:
  raise RuntimeError("Genus range scope changed")
 if len(s["visual_comparison"]["items"])!=10 or len(g["visual_comparison"]["items"])!=10:
  raise RuntimeError("Panel count mismatch")
 row={
 "file_name":DEST.name,"role":record["role"],"creator":"Jim Conrad",
 "license":LICENSE,"source_page":PAGE,"direct_url":ORIGINAL,
 "study_use":"Public educational visual-ID website; photographer source-credit maintained",
 "public_reuse":"YES — author's explicit public-domain dedication",
 }
 rows.append({k:row.get(k,"") for k in fields})
 DEST.parent.mkdir(parents=True,exist_ok=True);DEST.write_bytes(encoded)
 with CSV.open("w",newline="",encoding="utf8") as outcsv:
  writer=csv.DictWriter(outcsv,fieldnames=fields,lineterminator="\n")
  writer.writeheader();writer.writerows(rows)
 save(SP,s);save(GEN,g)
 save(REPORT,{
  "status":"ONE_AUTHENTIC_MUCRONATA_MM_SPIKELET_PHOTO_ARCHIVED",
  "taxon":TAXON,"original_label":SOURCE_IDENTIFICATION,
  "location":REGION,"physical_file":str(DEST),
  "source_page":PAGE,"source_image":ORIGINAL,"license_evidence":PERMISSION,
  "photo_creator":"Jim Conrad","source_dimensions":dims,
  "original_sha256":record["original_sha256"],"archived_sha256":record["archived_sha256"],
  "new_real_true_subspecies_photos":1,"new_visible_ruler_and_spikelet_arrows":2,
  "physically_stored_target_species_photos":6,
  "species_visual_panels":10,"genus_visual_panels":10,
  "fine_glume_mucro_not_claimed":True,"ligule_from_original_still_candidate":True,
  "status_remaining":"FIELD_READY_PHOTO_GAPS"
 })
 save(MARK,{
  "type":"manual_field_id_publication","date":"2026-10-23",
  "target":TAXON,"source":PAGE,
  "photo_count":1,"author":"Jim Conrad",
  "rights":"Express public-domain photographer dedication, no permission form needed",
  "only_arrows":["Real attached spikelet cluster","Real physical millimeter ruler graduations"],
  "not_claimed":"Fine glume mucro/individual lemma detail, Hays geographic voucher, or ligule as this is only a spikelet photo",
  "report":str(REPORT),
  "stage":"FIELD_READY_PHOTO_GAPS",
  "publish":"Normal rights-filtered GitHub Pages visual learner"
 })
 print("SUCCESS genuine source-identified Dinebra mucronata 1 public-domain photo, ruler + spikelet arrows; micromucro still held",flush=True)

if __name__=="__main__":main()
