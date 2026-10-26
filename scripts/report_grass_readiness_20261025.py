#!/usr/bin/env python3
"""Live grass (Poaceae) photo-readiness census from main manifest.
Metadata counts and screening flags are not anatomical pixel certifications.
No canonical species content is changed.
"""
import collections, json, pathlib, re, datetime
root=pathlib.Path(".")
manifest=json.loads((root/"data/manifest.json").read_text())
entries=[x for x in manifest["species"] if x.get("path","").startswith("content/taxa/Poaceae/") and x["path"].endswith("/species.json")]
before_path=root/"reports/grass-112-photo-coverage-work-allocation.json"
before=json.loads(before_path.read_text()) if before_path.exists() else {}
baseline=before.get("summary",{})
by_species=[]
total=collections.Counter()
def open_rights(p):
 license=str(p.get("license","")).lower()
 rights=" ".join(str(p.get(k,"")) for k in ("public_reuse","site_specific_public_permission","photo_rights")).lower()
 if re.search(r"\b(?:by-nc|nc-sa|by-nd|no derivatives|noncommercial)\b",license):
  return "restricted"
 if "public domain" in license or "cc0" in license or re.search(r"cc.?by",license) or "us federal work" in license:
  return "open"
 if "bob harms" in " ".join([str(p.get("creator","")),license]).lower() and any(x in (license+" "+rights) for x in ("educational","scientific","with credit","attribution")):
  return "specific_educational_permission"
 return "other_review"
def role_match(p):
 text=" ".join(str(p.get(k,"")) for k in ("label","image_role")).lower()
 roles=set()
 patterns={
  "habit_base":r"\b(?:whole.plant|plant habit|growth habit|rooted|rootstock|rhizome|root\b|basal|crown|tiller|runner|stolon|vegetative base|entire plant|whole grass)",
  "full_seedhead":r"\b(?:full inflorescence|panicle|flowering head|seedhead|entire head|raceme|flowering stalk|flowering axis|inflorescence|spikes?\b)",
  "collar_area":r"\b(?:collar|ligule|blade.sheath|sheath.junction|leaf.sheath|sheath mouth)",
  "reproductive_close":r"\b(?:spikelet|floret|lemma|glume|palea|awn|anther|dissected|grain|caryopsis|callus|pedicel)"
 }
 for role,pat in patterns.items():
  if re.search(pat,text):roles.add(role)
 return roles
for item in entries:
 p=root/item["path"]
 if not p.is_file():
  by_species.append({"id":item["id"],"error":"canonical file absent"})
  continue
 s=json.loads(p.read_text())
 images=s.get("images") or []
 galleries=(s.get("visual_comparison") or {}).get("items") or []
 scientific=str(s.get("scientific_name") or "").strip().casefold()
 exact=[x for x in galleries if str(x.get("scientific_name","")).strip().casefold()==scientific]
 localized=[x for x in galleries if str(x.get("image_url","")).startswith("content/")]
 exact_local=[x for x in exact if str(x.get("image_url","")).startswith("content/")]
 local_exact_photo=[x for x in exact_local if open_rights(x) in ("open","specific_educational_permission") and not re.search(r"\b(?:illustration|drawing|plate|diagram)\b",str(x.get("image_role",""))+" "+str(x.get("label","")),re.I)]
 raw_local=[x for x in images if str(x.get("file","")).startswith("images/")]
 verified_local=[x for x in raw_local if (p.parent/str(x["file"])).is_file()]
 verified_photo=[x for x in verified_local if not re.search(r"\b(?:illustration|drawing|diagram)\b",str(x.get("role","")),re.I)]
 unsafe_panels=[x for x in galleries if open_rights(x)=="restricted"]
 external_panels=[x for x in galleries if str(x.get("image_url","")).startswith("http")]
 role_set=set()
 for panel in local_exact_photo:
  role_set.update(role_match(panel))
 status=str((s.get("field_id_finish_pass") or {}).get("stage") or "")
 curation=s.get("curation_status") or {}
 if not status and isinstance(curation,dict):
  status=str(curation.get("visual_finish") or "")
 strict_complete=bool(re.match(r"^(?:FINISHED|COMPLETE|PUBLIC_READY|100%)\b",status,re.I)) and not re.search(r"GAP|HOLD|PENDING|PROVISIONAL",status,re.I)
 other_science_hold=bool(re.search(r"SCIENCE HOLD|TAXONOMY HOLD",status,re.I))
 d={
  "id":item["id"],"taxon":s.get("scientific_name"),
  "genus":s.get("genus"),
  "image_records":len(images),
  "stored_media_path_records":len(raw_local),
  "verified_local_files":len(verified_local),
  "verified_local_image_files_without_drawing_role":len(verified_photo),
  "gallery_panels":len(galleries),
  "gallery_local_panels":len(localized),
  "gallery_external_panels":len(external_panels),
  "gallery_same_species_panels":len(exact),
  "gallery_local_exact_open_or_educational_photo_panels":len(local_exact_photo),
  "unique_gallery_local_uris":len(set(str(x.get("image_url")) for x in localized)),
  "gallery_restricted_license_panels":len(unsafe_panels),
  "roles_labeled_from_own_local_panels":sorted(role_set),
  "candidate_four_role_types":len(role_set)==4,
  "strict_verified_finished_status":strict_complete,
  "status":status[:180],
  "remaining_examples":[]
 }
 finish=s.get("field_id_finish_pass") or {}
 # Last mile explicitly recorded elsewhere, not equivalent to independent audit.
 for key,value in finish.items():
  if key in ("what_to_photograph","photo_targets") and isinstance(value,list):
   d["remaining_examples"].extend(str(x)[:130] for x in value[:3])
 if isinstance(finish.get("measured_diagnostic_key_20261023"),dict):
  d["remaining_examples"].extend(str(x)[:130] for x in finish["measured_diagnostic_key_20261023"].get("public_photo_gaps",[])[:2])
 d["remaining_examples"]=d["remaining_examples"][:3]
 by_species.append(d)
 total["species"]+=1
 for key in ("image_records","stored_media_path_records","verified_local_files","verified_local_image_files_without_drawing_role","gallery_panels","gallery_local_panels","gallery_external_panels","gallery_same_species_panels","gallery_local_exact_open_or_educational_photo_panels","unique_gallery_local_uris","gallery_restricted_license_panels"):
  total[key]+=d[key]
 for key in ("strict_verified_finished_status","candidate_four_role_types"):
  total[key]+=int(d[key])
 if d["gallery_local_exact_open_or_educational_photo_panels"]==0:total["species_with_no_local_same_species_public_or_authorized_photo"]+=1
 if d["verified_local_image_files_without_drawing_role"]==0:total["species_with_zero_local_photo_file"]+=1
 if d["gallery_restricted_license_panels"]:total["species_with_restricted_gallery_panels"]+=1
 if not status:total["species_with_no_explicit_status"]+=1
 if "GAP" in status.upper():total["species_explicit_photo_gaps"]+=1
 if "HOLD" in status.upper():total["species_explicit_hold_stage"]+=1
 for role in role_set:total["species_role_"+role]+=1
 if all(k in role_set for k in ("habit_base","collar_area","reproductive_close")):
  total["species_with_habit_collar_repro_role_labels"]+=1
genus=sorted({str(x.get("genus","")) for x in by_species if x.get("genus")})
progress_by_species=sorted(by_species,key=lambda z:(z.get("gallery_local_exact_open_or_educational_photo_panels",0),z.get("id","")))
current={
 "generated_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
 "source":"Current checked-out main canonical data/manifest.json and Poaceae species.json, direct local filesystem verification",
 "method":"Numbers are metadata/file-backed coverage counts, not individual pixel-by-pixel anatomy or license final approval. Role counts are heuristic label/image_role matches only. Author-specific educational rights are separately conditional. Comparisons and drawings are not counted as same-species, publicly licensed diagnostic photos.",
 "baseline_20261023":{"source":"reports/grass-112-photo-coverage-work-allocation.json","generated_utc":before.get("generated_utc"),"method":before.get("method"),"summary":baseline},
 "summary":dict(total),
 "genus_count":len(genus),
 "species_manifest_entries":len(entries),
 "genus_names":genus,
 "by_species":by_species,
 "zero_or_thin_open_local_gallery":[x for x in progress_by_species if x.get("gallery_local_exact_open_or_educational_photo_panels",0)<2],
 "four_role_candidates":[x["id"] for x in by_species if x.get("candidate_four_role_types")],
 "science_holds_to_preserve":["anatherum-tenuispatheum","chloris-x-subdolichostachya","muhlenbergia-x-involuta","sorghastrum-elliottii"],
 "delayed_species":["muhlenbergia-piniflora"],
 "qualifier":"Zero finished statuses should not be extrapolated to zero good field cards: many cards are practical for learning but still lack measured anatomy and live mobile site QA."
}
out=root/"reports/grass-current-photo-readiness-20261025.json"
out.write_text(json.dumps(current,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({"generated_utc":current["generated_utc"],"genus_count":len(genus),"summary":current["summary"],"zero_thin_ids":[x["id"] for x in current["zero_or_thin_open_local_gallery"]],"four_role_candidates":current["four_role_candidates"],"baseline":baseline}))
