#!/usr/bin/env python3
"""ONE original Bob Harms *Selected Monocots* KR bluestem spikelet detail.
Educational/scientific reuse with prominent author credit; COPYRIGHTED, NOT CC.
Not the separately licensed DigFlora ligule image. Does not close ligule gap.
"""
from pathlib import Path
import csv,hashlib,io,json,requests
from PIL import Image,ImageOps
P=Path("content/taxa/Poaceae/Bothriochloa")
SP=P/"bothriochloa-ischaemum/species.json";GN=P/"genus.json";CSV=SP.parent/"image-sources.csv"
PATH=SP.parent/"images/bob-harms-kr-songarica-boiss-9-selected-monocots.jpg"
REPORT=Path("reports/kr-bob-harms-selected-monocots-boiss9-one-photo-20261022.json")
MARK=Path("workflow/field-id-publication/2026-10-22-kr-one-harms-licensed-spikelet-photo.json")
SOURCE="https://w3.biosci.utexas.edu/prc/Monocots/GrassHTML/data/images/BOISS-9.jpg"
PAGE="https://w3.biosci.utexas.edu/prc/Monocots/GrassHTML/data/pages/BOISS-9.html"
PERM="https://w3.biosci.utexas.edu/prc/Monocots/"
LIC="© Bob Harms — scientific/educational use with attribution (NOT Creative Commons)"
SITEPERM="BOB_HARMS_SELECTED_MONOCOTS_EDU_WITH_CREDIT_20261022"
def save(path,content):
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(content,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
def main():
 s=json.loads(SP.read_text(encoding="utf8"));g=json.loads(GN.read_text(encoding="utf8"))
 assert s.get("id")=="bothriochloa-ischaemum" and g.get("name")=="Bothriochloa"
 if len(s["visual_comparison"]["items"])!=18 or len(g["visual_comparison"]["items"])!=13 or s["curation_status"]["photo_files_present"]!=7:raise RuntimeError("Concurrent update")
 if PATH.exists() or MARK.exists() or REPORT.exists() or any(x.get("source_page")==PAGE for x in s["images"]):raise RuntimeError("Duplicate / committed already")
 protected={n:json.dumps(s.get(n),sort_keys=True) for n in ("id","scientific_name","authority","synonyms","project_inclusion","native_target_zone_calculated","county_occurrences_target_zone","native_metrics_excluded","tags","taxonomic_note")}
 with CSV.open(newline="",encoding="utf8") as f:
  rd=csv.DictReader(f);header=rd.fieldnames;rows=list(rd)
 if not header or "file_name" not in header:raise RuntimeError("Missing source CSV")
 r=requests.get(SOURCE,timeout=40,headers={"User-Agent":"Hays-Botany-Learner/1.0 educational science with creator attribution"});r.raise_for_status()
 raw=r.content
 if not(raw.startswith(b"\xff\xd8\xff") and 25000<len(raw)<6000000):raise RuntimeError("Not an original source JPEG")
 with Image.open(io.BytesIO(raw)) as im:
  im.load();w,h=im.size
  if im.format!="JPEG" or not(650<=w<=2000 and 320<=h<=1600):raise RuntimeError("Original unexpected size")
  pic=ImageOps.exif_transpose(im).convert("RGB")
 out=io.BytesIO();pic.save(out,format="JPEG",quality=94,optimize=True);payload=out.getvalue()
 with Image.open(io.BytesIO(payload)) as verify:
  assert verify.format=="JPEG" and not verify.getexif().get(34853)
  verify.verify()
 record={
 "file":"images/"+PATH.name,"role":"Actual North Hays King Ranch bluestem matured isolated awned spikelet group; three displayed original groups and printed source scale — exact partner attachment not independently proven",
 "creator":"Bob Harms","license":LIC,"license_url":PERM,
 "site_specific_public_permission":SITEPERM,
 "source_taxon_name":"Bothriochloa ischaemum var. songarica",
 "source_page":PAGE,"source_image":SOURCE,"public_reuse":"YES: credited educational/scientific use on author's own Selected Monocots collection; COPYRIGHTED NOT CC/general reuse",
 "source_region":"Bob Harms Selected Central Texas Monocots (northern Hays / Travis area)",
 "original_sha256":hashlib.sha256(raw).hexdigest(),
 "archived_sha256":hashlib.sha256(payload).hexdigest(),"image_dimensions":[w,h],
 "modifications":"Color original resized/reencoded JPEG with EXIF/GPS stripped, broad visible structure overlay arrows in gallery JSON; copyright and author rights retained",
 "photo_review":"Visually verified three source-authenticated detached awned reproductive units and original scale strip in frame; no physical ruler calibration asserted from cropped scale alone; true attached fertile sessile/pedicelled pair remains unresolved.",
 "archived_locally":True
 }
 panel={
 "label":"CENTRAL TEXAS KR — actual Bob Harms awned spikelets, scale strip and visible bent awns",
 "scientific_name":"Bothriochloa ischaemum",
 "image_url":str(PATH),"image_fit":"contain","image_role":record["role"],
 "caption":"Real Selected Monocots BOISS-9 photograph by Bob Harms identified as King Ranch bluestem var. songarica. Three isolated groups of actual spikelets and long, bent/twisted awns on a dark background; source scale strip appears near bottom. LEFT gross arrow shows photographed spikelet-bearing group and TOP gross arrow long bent awn. The isolated arrangement does not prove an intact SAME-voucher sessile-fertile and pedicelled-companion pair with a measurable 1 mm bar. This photo is NOT a ligule photograph.",
 "why_it_matters":"A legitimate original Central Texas species/variety reproductive macro for crews to learn awn shape before the same-plant sessile and pedicelled pair is clearly photographed.",
 "creator":"Bob Harms","license":LIC,"license_url":PERM,
 "source_page":PAGE,"source_image":SOURCE,
 "source_taxon_name":"Bothriochloa ischaemum var. songarica",
 "site_specific_public_permission":SITEPERM,
 "public_reuse":record["public_reuse"],
 "markers":[
  {"label":"Awned spikelet group","label_x":1,"label_y":67,"target_x":20,"target_y":71},
  {"label":"Long bent awn","label_x":8,"label_y":10,"target_x":50,"target_y":7}
 ],
 "photo_status":"Credited educational original specifically listed by author in Selected Monocots; broad verified visible photo arrows, NOT exact free ligule or attached pair anatomy; reuse limited to educational/scientific with credit."
 }
 s["images"].append(record)
 s["visual_comparison"]["items"].append(panel);g["visual_comparison"]["items"].append(dict(panel))
 s["curation_status"]["photo_metadata_count"]=len(s["images"])
 s["curation_status"]["photo_files_present"]=8
 s["curation_status"]["kr_one_harms_educational_photo_boiss9_20261022"]={
  "new_physical_photo":1,"new_broad_photo_arrows":2,"site_permission":SITEPERM,
  "source_page":PAGE,"not_a_ligule_photo":True,
  "ligule_high_resolution_texas_rights_gap_remains":True,"stage":"FIELD_READY_PHOTO_GAPS"}
 g["curation_status"]["kr_harms_selected_monocots_spikelets_one_20261022"]={
  "new_physical_photo":1,"two_gross_arrows":2,"copyrighted_education_with_credit":True,
  "source":PAGE,"ligule_gap_unchanged":True}
 s["visual_comparison"]["subtitle"]+=" One additional real North Hays/Travis-region Bob Harms original labelled KR var. songarica with visible awns, COPYRIGHTED for credited educational use; not a ligule macro."
 s["field_photo_quickcheck"]["featured_photo_indices"].append(18)
 s["field_photo_quickcheck"]["steps"].append("17. VERIFIED CENTRAL TEXAS KR MATURE SPIKELETS — NEW photo 19 by Bob Harms (Selected Monocots; explicitly free for scientific/educational credited uses). Label left detached awned spikelet group and visible bent awn with two broad arrows, but DO NOT label an exact attached partner or actual mm measurements without a fully attached source. This is NOT a ligule photo. The true Texas open free membrane remains an unresolved separate target.")
 s["field_id_finish_pass"]["stage"]="FIELD_READY_PHOTO_GAPS — one credited educational Central Texas KR isolated awned spikelet macro archived, but exact Texas true ligule with free 0.5–1.5mm ciliate rim remains WITHOUT reusable detailed source; same-voucher attached fertile/pedicelled pair also missing."
 s["field_id_finish_pass"]["permission_free_ligule_hunt_20261022"]={
  "finding":"No newly discovered exact licensed fully opened Texas KR ligule",
  "already_installed_reusable_photo":"Stefan.lefnaer Bothriochloa ischaemum sl1, CC BY-SA 4.0, 2-mm source scale, European species-level partial collar photo",
  "original_Hays_ligule":"Bob Harms DigFlora BOISS-LX-21Jul-A.JPG; rights for this separate collection not established; remains LINK ONLY",
  "selected_monocots_scope":"KR Selected Monocots has habitat, flowering details and BOISS-9 spikelet closeup, NOT a ligule photo",
  "source_hunt":["https://commons.wikimedia.org/wiki/Category:Ligule","https://w3.biosci.utexas.edu/prc/Monocots/GrassHTML/data/Bothriochloa-text.html",PAGE],
  "copyright_free_educational_alternate_installed":PAGE
 }
 if any(json.dumps(s.get(n),sort_keys=True)!=v for n,v in protected.items()):raise RuntimeError("Protected taxon changed")
 row={"file_name":PATH.name,"role":record["role"],"creator":"Bob Harms","license":LIC,"license_url":PERM,"source_page":PAGE,"direct_url":SOURCE,"study_use":"Noncommercial public scientific and educational visual learner","public_reuse":"Author expressly permits scientific/educational with credit, NOT CC","modifications":record["modifications"]}
 rows.append({key:row.get(key,"") for key in header})
 PATH.parent.mkdir(parents=True,exist_ok=True);PATH.write_bytes(payload)
 with CSV.open("w",newline="",encoding="utf8") as f:
  wr=csv.DictWriter(f,fieldnames=header,lineterminator="\n");wr.writeheader();wr.writerows(rows)
 save(SP,s);save(GN,g)
 save(REPORT,{"status":"REAL_HAYS_KR_ONE_EDUCATIONAL_REUSABLE_SPIKELET_ORIGINAL_ARCHIVED","photo":str(PATH),
 "source":PAGE,"source_image":SOURCE,"rights":PERM,"creator":"Bob Harms","license":LIC,
 "sha256":record["archived_sha256"],"dims":[w,h],"new_reusable_photo_count":1,
 "new_gross_arrows":2,"total_kr_stored_photos":8,"species_panels":19,"genus_panels":14,
 "ligule_exact_edge_gap":"OPEN; one previously installed CC BY-SA Austrian partial ligule-zone photo already present",
 "local_specimen_attached_spikelet_pair_gap":"OPEN; dark detached photo not proof of attachment",
 "permission_for_separate_DigFlora_ligule":"NOT_ESTABLISHED; NO COPY"})
 save(MARK,{"type":"manual_field_id_publication","date":"2026-10-22","species":"Bothriochloa ischaemum",
 "photo_count":1,"source":PAGE,"rights":"Credited educational use per Selected Monocots original author statement, NOT CC",
 "report":str(REPORT),"status":"FIELD_READY_PHOTO_GAPS","publish":"NORMAL_RIGHTS_FILTERED_GITHUB_PAGES"})
 print("SUCCESS one actually source-vouched North Hays-region KR awned spikelet original; exact ligule photo still missing",flush=True)
if __name__=="__main__":main()
