#!/usr/bin/env python3
"""Physically archive seven EXACT iNaturalist research-grade public-licensed
Tridens buckleyanus photos under accepted Tridentopsis buckleyana. Preserves
existing source photo NC hold, county native decisions, comparisons and arrows.
Observed structures only; no inferred lemma hair, lengths, specimen accession.
"""
from pathlib import Path
import io,json,hashlib,requests,time
from PIL import Image,ImageOps

ROOT=Path("content/taxa/Poaceae/Tridentopsis")
SP=ROOT/"tridentopsis-buckleyana/species.json"
GP=ROOT/"genus.json"
SOURCE=Path("reports/buckley-tridens-inat-original-photo-scout-20261023/index.json")
REPORT=Path("reports/buckley-tridens-seven-source-public-photos-20261023.json")
RELEASE=Path("workflow/field-id-publication/2026-10-23-buckley-tridens-seven-source-photos.json")
LIC="CC BY 4.0"
LURL="https://creativecommons.org/licenses/by/4.0/"
ROWS=[
 (102622491,63893287,"Eric Knight","OPEN BRANCHING PANICLE against a hand",
  "Texas research-grade original shows the OPEN, widely separated terminal flowering branches over a hand. A hand gives only approximate size, not millimeters; no fertile floret number or vein hairs are resolved.",
  "Long separate branches and distantly attached spikelets; open-panicle first clue"),
 (174189386,103996436,"Eric Knight","LEAF SHEATH JUNCTION: real stem and blade macro",
  "Travis County research-grade original shows a real blade, sheath and culm node next to a finger. It is NOT an opened, measured free ligule margin. Teach where to separate blade/sheath for future 1 mm lens examination.",
  "Actual sheath and leaf/culm junction, not proven free ciliate ligule"),
 (174189373,103996436,"Eric Knight","ATTACHED MATURE SPIKELETS: Central Texas photo",
  "Travis County genuine photograph shows an attached narrow multi-flowered spikelet on one branching seedhead, with finger for informal scale. Countable glume/lemma boundaries need 10–20× and a true mm ruler.",
  "Attached mature spikelet and its lateral panicle branch, not dissected glumes"),
 (174189357,103996436,"Eric Knight","LOOSE SPIKELET: separate true dry specimen",
  "Travis County research-grade photo shows an isolated small, seed-bearing, flattened reproductive unit on skin. This is useful for finding a removable SPIKELET; photo does not demonstrate which tiny tip is the lower/upper glume or all 3–5 fertile florets.",
  "Detached dry individual spikelet (source-determined plant), no glume identities certified"),
 (240395559,140437400,"Eric Knight","FLOWERING BRANCH: distinct attached multifloret units",
  "Texas original shows a slender panicle branch carrying separate, narrow flattened spikelets. Note the ACTUAL attachment to the branch, rather than a fuzzy compact plume. Avoid claiming one apparent scale equals one spikelet.",
  "Branch-attached flowering spikelets and spaced branching pattern"),
 (173616239,103698173,"Sam Kieschnick","ROOTED TUFT HABIT: Texas clump with flowering plant",
  "San Antonio research-grade photo shows an in-situ perennial grass tuft with narrow upright leaves and flowering culms. Actual underground roots are NOT exposed; it is a photographed basal tuft, not root dissection.",
  "Source-reported Texas clump and basal thin leaves, plant-in-place habit"),
 (157748934,95049825,"Cleveland Powell","MATURE SPIKELET MACRO: long compressed fertile unit",
  "Texas research-grade close-up shows elongated narrow, overlapping spikelets against fingers. This strengthens recognition of mature floret scales but does not confirm glume lengths, dorsal lemma three nerves or microscopic margin hairs.",
  "Mature multi-floret-looking terminal structures on lateral flowering branch (original taxon label)")
]
sp=json.loads(SP.read_text(encoding="utf-8"))
g=json.loads(GP.read_text(encoding="utf-8"))
src=json.loads(SOURCE.read_text(encoding="utf-8"))
assert sp["id"]=="tridentopsis-buckleyana" and sp["scientific_name"]=="Tridentopsis buckleyana"
assert len(sp["images"])==1 and sp["curation_status"]["photo_files_present"]==1
assert len(sp["visual_comparison"]["items"])==4 and len(g["visual_comparison"]["items"])==4
assert sp["images"][0]["license"]=="CC BY-NC"
assert "FIELD_READY_PHOTO_GAPS" in sp["field_id_finish_pass"]["stage"]
assert src["inat_taxon_id"]==169947
prior_taxon={k:sp.get(k) for k in ("county_occurrences_target_zone","target_zone_count","native_target_zone_calculated",
 "native_metrics_excluded","project_inclusion","taxonomy_source","comparisons","morphology_keys","synonyms")}
old_first_sp=sp["visual_comparison"]["items"][0].copy()
old_first_genus=g["visual_comparison"]["items"][0].copy()
sesh=requests.Session()
sesh.headers.update({"User-Agent":"HaysBotany-BuckleyTridens-SourceExactEducationalPhotoArchive/1.0",
 "Accept":"image/jpeg,image/*;q=0.9"})
report={"species":"Tridentopsis buckleyana","observed_name":"Tridens buckleyanus",
 "accepted_name_authority":"https://powo.science.kew.org/taxon/77160904-1",
 "old_name_source_taxon_id":src["inat_taxon_id"],
 "license":"Individual photo CC BY 4.0; each photographer explicitly attributed; EXIF and GPS removed",
 "original_cc_by_nc_study_photo":"PRESERVED with its existing legal rights, NOT silently cleared",
 "photos":[],"installed_originals":0,
 "high_resolution_limits":"True three-veined hairy lemma, lower>upper glumes and measured 0.4–1mm ligule still require same-voucher magnification"}
for pid,oid,creator,label,caption,role in ROWS:
 matches=[p for p in src["candidates"] if p["photo_id"]==pid and p["observation_id"]==oid and p["license"]=="cc-by" and p["quality"]=="research" and p["taxon"]=="Tridens buckleyanus"]
 assert len(matches)==1,("Source, original license, source taxon and research-grade",pid)
 c=matches[0]
 assert creator in c["creator"],(pid,creator,c["creator"])
 original=c["original_url"]
 assert original.startswith("https://inaturalist-open-data.s3.amazonaws.com/photos/") and f"/{pid}/" in original
 outfile=SP.parent/"images"/f"buckley-tridens-inat-{pid}-cc-by-original.jpg"
 if outfile.exists():raise RuntimeError("Original already archived; fail safely "+str(outfile))
 last=None
 for t in range(3):
  try:
   response=sesh.get(original,timeout=40);response.raise_for_status()
   raw=response.content
   if len(raw)<14000 or not raw.startswith(bytes.fromhex("ffd8ff")):raise ValueError("Original must be JPEG with substantial real bytes")
   with Image.open(io.BytesIO(raw)) as im:
    im.load()
    if im.format!="JPEG" or min(im.size)<600:raise ValueError(f"Not proper full original, dims {im.size}")
    pixels=ImageOps.exif_transpose(im).convert("RGB")
    dims=list(pixels.size)
   outfile.parent.mkdir(parents=True,exist_ok=True)
   pixels.save(outfile,format="JPEG",quality=93,optimize=True)
   source_sha=hashlib.sha256(raw).hexdigest()
   break
  except (requests.RequestException,ValueError,OSError) as e:
   last=str(e)
   if t<2:time.sleep(4*(t+1))
 else:raise RuntimeError(f"Could not verify actual original {pid}: {last}")
 data=outfile.read_bytes()
 with Image.open(outfile) as im:
  assert im.format=="JPEG" and im.mode=="RGB" and list(im.size)==dims and not im.getexif().get(34853)
  im.verify()
 digest=hashlib.sha256(data).hexdigest()
 photo={
  "file":"images/"+outfile.name,"role":role,"creator":creator,"license":LIC,"license_url":LURL,
  "source_page":c["photo_url"],"source_observation":c["observation_url"],"source_image":original,
  "original_source_taxon_name":"Tridens buckleyanus","accepted_taxon_name":"Tridentopsis buckleyana",
  "original_taxon_determination":"Source research-grade Tridens buckleyanus, synonym of accepted Tridentopsis buckleyana",
  "photo_source_id":str(pid),"source_observation_id":str(oid),
  "public_reuse":"YES: exact licensed CC BY 4.0 original; preserve creator/source/attribution and modifications",
  "photo_review":"Original full-resolution source photo archived and confirmed original research-grade taxon ID. Broad structure annotated only after pixel review. No micro source voucher or exact 1mm hair count claimed. PROVISIONAL — USER PHOTO REVIEW PENDING.",
  "archive_sha256":digest,"original_source_sha256":source_sha,"image_dimensions":dims,
  "modifications":"EXIF/GPS removed in full-size RGB JPEG re-encode, no crop or inaccurate species label addition"
 }
 panel={
  "label":label,"scientific_name":"Tridentopsis buckleyana",
  "image_url":str(outfile),"image_fit":"contain","image_role":role,
  "caption":caption,
  "why_it_matters":"Real taxon-labelled Central Texas grass anatomy photographs, more specific than repeated distant field-habit shots; compare separately with the narrow Tridentopsis mutica seedhead and later confirm actual lemma hairs.",
  "creator":creator,"license":LIC,"license_url":LURL,
  "source_page":c["photo_url"],
  "photo_status":"Original real high-resolution research-grade CC BY 4.0 photo physically archived. Narrow and coarse structure arrows must be source-pixel verified. PROVISIONAL — USER PHOTO REVIEW PENDING.",
  "markers":[]
 }
 sp["images"].append(photo)
 sp["visual_comparison"]["items"].insert(len(sp["visual_comparison"]["items"])-3,panel)
 g["visual_comparison"]["items"].insert(len(g["visual_comparison"]["items"])-3,dict(panel))
 report["photos"].append({"photo_id":pid,"observation_id":oid,"creator":creator,"license":LIC,
  "original_url":original,"source_page":c["photo_url"],"source_observation":c["observation_url"],
  "file":str(outfile),"dims":dims,"bytes":len(data),"original_sha256":source_sha,"saved_sha256":digest})
 report["installed_originals"]+=1
assert report["installed_originals"]==7
assert len(sp["images"])==8 and len(sp["visual_comparison"]["items"])==11 and len(g["visual_comparison"]["items"])==11
assert sp["visual_comparison"]["items"][0]==old_first_sp and g["visual_comparison"]["items"][0]==old_first_genus
assert all(sp.get(k)==v for k,v in prior_taxon.items()),"Native county or taxonomic evidence changed unexpectedly"
sp["curation_status"]["photo_metadata_count"]=8
sp["curation_status"]["photo_files_present"]=8
sp["curation_status"]["buckley_tridens_7_cc_originals_20261023"]={
 "new_public_cc_by_full_originals":7,"local_total_images_including_legacy_nc":8,
 "original_nc_image_unchanged":True,"species_panels":11,"genus_panels":11,
 "taxonomy_and_native_status_unchanged":True,"truly_measured_lemma_hairs":False,
 "status":"FIELD_READY_PHOTO_GAPS"
}
sp["field_id_finish_pass"]["buckley_seven_ccby_diagnostic_20261023"]={
 "true_original_jpegs_added":7,"photo_report":str(REPORT),"old_name":"Tridens buckleyanus",
 "actual_source_image_roles":[d[3] for d in ROWS],
 "still_missing":["Same voucher verified complete local plant with measured 10–28 cm mature open panicle and documented Hays source",
 "1 mm ruler on three ripe 3–5-floret spikelets, number EACH actual fertile floret, record lower vs upper persistent glume",
 "True exposed 3-veined lemma dorsal surface under 20×, photographic verification of pubescence along lower nerve/margin",
 "Actual ciliate membranous ligule free edge opened at leaf sheath, mm reference beside it"],
 "status":"FIELD_READY_PHOTO_GAPS"
}
sp["visual_comparison"]["title"]="Buckley tridens — true open panicle, attached and detached spikelets, leaf collar and mutica comparison"
sp["visual_comparison"]["subtitle"]="Eight physically stored photos: seven new individual CC BY 4.0 research-grade Tridens buckleyanus exact synonym originals (open branches, collar, spikelets, basal clump), plus historical CC BY-NC source-labelled image, whose NC restrictions remain. Three native Tridentopsis mutica comparison photos unchanged."
sp["visual_comparison"]["overlay_note"]="Source old name Tridens buckleyanus correctly maps to accepted Tridentopsis buckleyana, never a duplicate. New original JPEG source/license/photographer/EXIF policy preserved. Do not claim all detached details same accession across observations, or measured glume/lemma hair from these pictures."
g["visual_comparison"]["title"]="TRIDENTOPSIS — Buckley open panicle versus slim contracted heads"
g["visual_comparison"]["subtitle"]=sp["visual_comparison"]["subtitle"]
g["visual_comparison"]["overlay_note"]=sp["visual_comparison"]["overlay_note"]
g["curation_status"]["buckley_7_public_originals_20261023"]={
 "new_public_ccby_research_grade_exact_photos":7,"genus_panels":11,"existing_mutica_photos_preserved":3,
 "source_taxon":"Tridens buckleyanus","accepted":"Tridentopsis buckleyana",
 "hold": "Measured three-veined lemma hairs, free 1mm collar, original source County nativity unchanged"
}
SP.write_text(json.dumps(sp,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
GP.write_text(json.dumps(g,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
REPORT.parent.mkdir(parents=True,exist_ok=True)
REPORT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
RELEASE.parent.mkdir(parents=True,exist_ok=True)
RELEASE.write_text(json.dumps({
 "type":"manual_field_id_publication","species":"Tridentopsis buckleyana","date":"2026-10-23",
 "new_original_files":7,"total_local_files":8,"original_legacy_nc_rights_unchanged":True,
 "genus_panels":11,"species_panels":11,"new_photo_license":"seven individual photographer CC BY 4.0",
 "source_original_report":str(REPORT),"status":"FIELD_READY_PHOTO_GAPS",
 "publication":"Run main Pages quality build+deployment checks; do not claim site live until both succeed"
},indent=2)+"\n",encoding="utf-8")
print("SUCCESS: 7 real original researcher-labelled public licensed Buckley tridens photos archived; preserve old NC original",flush=True)
