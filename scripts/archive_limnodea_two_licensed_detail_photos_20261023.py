#!/usr/bin/env python3
"""Archive two photo-license verified and original-pixel-preview inspected,
exactly identified iNaturalist research-grade Ozarkgrass images for public
species + genus lessons. These DO NOT prove 0.5mm lemma teeth or true ligule.
"""
from pathlib import Path
import io,json,hashlib,time,requests
from PIL import Image,ImageOps

ROOT=Path("content/taxa/Poaceae/Limnodea")
SPECIES=ROOT/"limnodea-arkansana/species.json"
GENUS=ROOT/"genus.json"
REPORT=Path("reports/limnodea-two-ccby-collar-spikelet-originals-20261023.json")
RELEASE=Path("workflow/field-id-publication/2026-10-23-limnodea-two-ccby-closeups.json")
SRC="reports/limnodea-photo-shortlist-20261023/contact-index.json"
rows=[
 (655661278,359373339,"Linda Jo Conn","linda-jo-conn-655661278-green-awned-spikelets.jpg",
   "ATTACHED SPIKELETS — green and awned, fingers for scale",
   "The original Ozarkgrass research-grade observation shows slender seed-bearing branches held over the observer's fingertips. Individual green spikelets and long awns are visible. Fingers are not a calibrated 1-mm ruler, and the TWO tiny lemma teeth cannot be reliably resolved here.",
   "Attached awned flowering head, several narrow spikelets, informal hand scale; not detached calibrated glumes or lemma"),
 (647543191,354995431,"Chet Burrier","chet-burrier-647543191-leaf-collar-macro.jpg",
   "LEAF COLLAR MACRO — pale membrane region, exact free ligule not measured",
   "An original Ozarkgrass research-grade observation shows the blade passing into its enclosing sheath near a pale tissue projection. The leaf-collar junction is visible; without peeling the sheath fully open or a 1-mm ruler this does NOT prove the free ligule apex, membrane hairs, or ligule dimensions.",
   "Blade/sheath junction and pale collar tissue, but true free ligule edge unverified")
]
s=json.loads(SPECIES.read_text(encoding="utf-8"))
g=json.loads(GENUS.read_text(encoding="utf-8"))
prev=json.loads(Path(SRC).read_text(encoding="utf-8"))
assert s["id"]=="limnodea-arkansana" and s["scientific_name"]=="Limnodea arkansana"
assert s["curation_status"]["taxonomy_reviewed"]==False
assert len(s["images"])==7 and len(s["visual_comparison"]["items"])==10 and len(g["visual_comparison"]["items"])==10
assert "FIELD_READY_PHOTO_GAPS" in s["field_id_finish_pass"]["stage"]
original_status=s["curation_status"]["taxonomy_reviewed"]
original_science=s.get("morphology_keys")
original_ref=s.get("field_id_sources")
client=requests.Session();client.headers.update({"User-Agent":"HaysBotanyLicensedOzarkgrassMacroArchive/1.0","Accept":"image/jpeg,image/*;q=0.9"})
report={"species":"Limnodea arkansana","date":"2026-10-23","candidate_index":SRC,
 "exact_taxon_source":"iNaturalist research-grade observations, per-photo original CC BY license","installed_new":0,"photos":[],
 "limits":"Actual 0.5mm lemma teeth, precise awn insertion, isolated glume veins and free 1mm ligule remain unproven"}
for ident, obs, creator,fn,label,caption,role in rows:
 cands=[p for p in prev["photos"] if p["photo_id"]==ident and p["observation_id"]==obs]
 assert len(cands)==1 and cands[0]["license"]=="cc-by",(ident,cands)
 candidate=cands[0]
 file=SPECIES.parent/"images"/fn
 if file.exists():raise RuntimeError("Image exists, do not overwrite: "+str(file))
 url=candidate["original_url"]
 response=None
 for attempt in range(3):
  try:
   response=client.get(url,timeout=38)
   response.raise_for_status()
   raw=response.content
   if len(raw)<10000 or not raw.startswith(bytes.fromhex("ffd8ff")): raise ValueError("not original JPG")
   with Image.open(io.BytesIO(raw)) as i:
    i.load()
    if i.format!="JPEG" or min(i.size)<650:raise ValueError("insufficient original dimension for diagnostic closeup")
    clear=ImageOps.exif_transpose(i).convert("RGB")
   file.parent.mkdir(parents=True,exist_ok=True)
   clear.save(file,"JPEG",quality=93,optimize=True)
   srchash=hashlib.sha256(raw).hexdigest()
   break
  except (requests.RequestException,ValueError,OSError) as e:
   if attempt==2:raise RuntimeError(f"Exact source JPEG {ident} fetch unavailable: {e}")
   time.sleep(4+attempt)
 data=file.read_bytes()
 with Image.open(file) as im:
  assert im.format=="JPEG" and im.mode=="RGB" and not im.getexif().get(34853)
  dimensions=list(im.size)
  im.verify()
 sha=hashlib.sha256(data).hexdigest()
 sourcepage=f"https://www.inaturalist.org/photos/{ident}"
 record={
  "file":"images/"+fn,"role":role,"creator":creator,"license":"CC BY 4.0",
  "license_url":"https://creativecommons.org/licenses/by/4.0/",
  "source_page":sourcepage,"source_observation":candidate["observation_url"],
  "source_photo_id":str(ident),"source_taxon_name":"Limnodea arkansana",
  "source_determination":"iNaturalist research-grade Limnodea arkansana, original photographer photo with individual cc-by license code",
  "source_image":url,"public_reuse":"yes — individual original CC BY 4.0 with visible creator, source and original license",
  "photo_review":"Actual source preview visually inspected at 320px; original JPEG integrity checked. PROVISIONAL — USER PHOTO REVIEW PENDING. Fine 0.5mm tooth, source voucher dissection and true 1mm membrane NOT certified.",
  "image_dimensions":dimensions,"archive_sha256":sha,"original_image_sha256":srchash,
  "modifications":"EXIF/GPS removed with full-size RGB JPEG re-encode. Attribution/license/source preserved. No crop."
 }
 panel={
  "label":label,"scientific_name":"Limnodea arkansana",
  "image_url":str(file),"image_fit":"contain","image_role":role,
  "caption":caption,
  "why_it_matters":"Real observation-derived anatomy improves field teachability; do not misread hand scale as precise millimeter measurements.",
  "creator":creator,"license":"CC BY 4.0","license_url":"https://creativecommons.org/licenses/by/4.0/",
  "source_page":sourcepage,"markers":[],
  "photo_status":"Exact licensed CC BY 4.0 original, research-grade determined Limnodea, archived and original JPEG integrity verified. Anatomical arrows pending original-pixel inspection. PROVISIONAL — USER PHOTO REVIEW PENDING."
 }
 s["images"].append(record)
 s["visual_comparison"]["items"].insert(1,panel)
 g["visual_comparison"]["items"].insert(1,dict(panel))
 report["photos"].append({"photo_id":ident,"observation_id":obs,"creator":creator,"source_page":sourcepage,
  "original_url":url,"physical_path":str(file),"dimensions":dimensions,
  "archived_sha256":sha,"source_sha256":srchash,"bytes":len(data)})
 report["installed_new"]+=1
assert len(s["images"])==9 and len(s["visual_comparison"]["items"])==12 and len(g["visual_comparison"]["items"])==12
assert s["curation_status"]["taxonomy_reviewed"]==original_status and s.get("morphology_keys")==original_science and s.get("field_id_sources")==original_ref
s["curation_status"]["photo_metadata_count"]=9
s["curation_status"]["photo_files_present"]=9
s["curation_status"]["ozarkgrass_two_licensed_detail_jpegs_20261023"]={
  "new_source_verified_jpegs":2,"total_local_originals":9,"species_and_genus_panels_each":12,
  "creator_license":"Linda Jo Conn CC BY 4.0; Chet Burrier CC BY 4.0",
  "teeth_and_glume_mm_resolved":False,"fine_ligule_membrane_resolved":False,
  "native_status_taxonomy_untouched":True,"stage":"FIELD_READY_PHOTO_GAPS"}
s["field_id_finish_pass"]["licensed_closeup_source_recovery_20261023"]={
 "photo_proven":["Awned narrow reproductive branches in hand with informal scale","Actual blade-sheath collar region from separate research-grade observation"],
 "photo_unproven":["0.5mm pair of lemma apical teeth and awn origin between them with real mm scale",
                  "Dissected ~3mm glumes paired with one fertile floret and scale",
                  "TRUE 1-2mm membrane of ligule opened and measured with mm ruler",
                  "Same rooted and reproductive local Hays voucher"],
 "citation_for_morphology":"https://w3.biosci.utexas.edu/prc/K12/pdf/Limnodea%20arkansana",
 "photo_rights":"Both exact photos individual iNaturalist CC BY 4.0; originals archived after metadata removal",
 "stage":"FIELD_READY_PHOTO_GAPS"
}
s["visual_comparison"]["title"]="Ozarkgrass — seven original Central Texas photo views, two new close-ups, and native-grass contrasts"
s["visual_comparison"]["subtitle"]="Nine physically stored original species photographs (six credited Bob Harms; two CC BY detailed iNaturalist; one original CC BY-NC). Two new macro study panels show reproductive branches and collar. Still missing photographed actual 0.5mm two-toothed lemma tips and calibrated ligule."
g["visual_comparison"]["title"]=s["visual_comparison"]["title"]
g["visual_comparison"]["subtitle"]=s["visual_comparison"]["subtitle"]
g["curation_status"]["limnodea_two_ccby_detail_20261023"]={"new_real_originals":2,"genus_panels":12,"important_1mm_macro_hold":True}
SPECIES.write_text(json.dumps(s,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
GENUS.write_text(json.dumps(g,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
REPORT.parent.mkdir(parents=True,exist_ok=True)
REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
RELEASE.parent.mkdir(parents=True,exist_ok=True)
RELEASE.write_text(json.dumps({
 "type":"manual_field_id_publication","date":"2026-10-23","species":"Limnodea arkansana",
 "report":str(REPORT),"new_real_originals":2,"local_species_jpegs":9,
 "species_teaching_panels":12,"genus_teaching_panels":12,
 "rights":"individual original CC BY 4.0 two; original other photo licenses retained",
 "last_mile":"Actual 0.5mm lemma two teeth + between-teeth awn, true measured ligule and same-vouchered glume dissection",
 "status":"FIELD_READY_PHOTO_GAPS","site_publication":"Source marker only, need separate build+deploy success"
},indent=2)+"\n",encoding="utf-8")
print("Installed 2 new licensed regional true Ozarkgrass images, no false mm anatomical certification")
