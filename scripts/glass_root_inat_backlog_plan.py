#!/usr/bin/env python3
"""Read actual canonical gallery and owner's iNaturalist photo metadata to prioritize next images.
Does not install, copy, change or approve photographs, and never changes scientific state.
"""
import argparse,csv,json,pathlib,collections,math,datetime
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--photos",default="workflow/glass-root-inat/batch-005/metadata/photo-candidates.csv")
 p.add_argument("--manifest",default="data/manifest.json")
 p.add_argument("--claims",default="workflow/work-claims.json")
 p.add_argument("--out",default="workflow/glass-root-inat/backlog-plan")
 p.add_argument("--batch-size",type=int,default=4)
 a=p.parse_args()
 manifest=json.loads(pathlib.Path(a.manifest).read_text())
 claims=json.loads(pathlib.Path(a.claims).read_text())
 busy=set()
 for c in claims.get("claims",[]):
  if c.get("status") in ("active","queued","blocked") and c.get("lane")!="glass-root-owner-photo-review":
   busy.update(c.get("taxa") or [])
 with open(a.photos,newline="",encoding="utf-8-sig") as f:photos=list(csv.DictReader(f))
 pool=collections.defaultdict(list)
 for photo in photos:
  if photo.get("canonical_id") and any(s in (photo.get("source_attribution") or "").lower() for s in ("calvin king","calvinking","glass root garden")):
   pool[photo["canonical_id"]].append(photo)
 candidates=[]
 for ref in manifest["species"]:
  sid=ref["id"]
  if sid not in pool:continue
  f=pathlib.Path(ref["path"])
  if not f.is_file():continue
  j=json.loads(f.read_text())
  gallery=j.get("images") or []
  owned_ids={str(v.get("photo_id")) for v in gallery if v.get("photo_id")}
  # No assumption that number of photos equals diagnostic quality; these are first-pass candidate counts only.
  local=sum(1 for v in gallery if str(v.get("file") or "").startswith("images/"))
  external=len(gallery)-local
  available=[v for v in pool[sid] if str(v.get("photo_id")) not in owned_ids]
  if not available:continue
  count=len(gallery)
  observations=len({v.get("observation_id") for v in available})
  ready_owner=len(available)
  label=(j.get("project_inclusion") or {}).get("target_zone_status","")
  is_non_native="NON_NATIVE" in label or label in ("FAIL","EXOTIC","INVASIVE","COMPARISON_NON_NATIVE")
  claimed=sid in busy
  # Prioritize actual missing images, then one or two-photo cards; suppress low urgency 3+ in first pass.
  urgency=100 if count==0 else 70 if count==1 else 40 if count==2 else 6 if count==3 else 0
  score=urgency+min(30,observations*3)+min(8,ready_owner//4)+(5 if external and local==0 else 0)
  if is_non_native:score-=15
  if claimed:score=-999
  candidates.append({
   "id":sid,"scientific_name":j.get("scientific_name") or sid,
   "canonical_path":str(f),"installed_images":count,"local_files":local,"external_links":external,
   "owner_iNat_photos_not_installed":ready_owner,"observations":observations,
   "target_status_existing":label,"is_non_native_comparison":is_non_native,
   "claim_conflict":claimed,"priority_score":score,
   "sample_photo_ids":";".join(x["photo_id"] for x in available[:5]),
   "sample_observation_url":available[0].get("observation_url","")
  })
 candidates.sort(key=lambda x:(-x["priority_score"],x["installed_images"],-x["observations"],x["id"]))
 out=pathlib.Path(a.out);out.mkdir(parents=True,exist_ok=True)
 cols=list(candidates[0]) if candidates else []
 with (out/"priority-queue.csv").open("w",newline="",encoding="utf-8") as f:
  if cols:
   w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(candidates)
 eligible=[x for x in candidates if not x["claim_conflict"] and x["installed_images"]<=2]
 eligible3=[x for x in candidates if not x["claim_conflict"] and x["installed_images"]<=3]
 already3=sum(x["installed_images"]>=3 for x in candidates)
 counts=collections.Counter(str(x["installed_images"]) for x in candidates)
 summary={
  "created_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
  "installed_species_in_manifest":len(manifest["species"]),
  "owner_inat_taxa_with_direct_installed_match":len(pool),
  "owner_matched_species_with_additional_uninstalled_photos":len(candidates),
  "gallery_counts_for_these_species":dict(sorted(counts.items(),key=lambda x:int(x[0]))),
  "zero_one_two_photo_species_in_owner_coverage":len(eligible),
  "up_to_three_photo_species_in_owner_coverage":len(eligible3),
  "estimated_batches_to_cover_all_zero_to_two_photo_matches_at_"+str(a.batch_size)+"_species":math.ceil(len(eligible)/a.batch_size),
  "batches_with_three_photo_species_at_"+str(a.batch_size)+"_species":math.ceil(len(eligible3)/a.batch_size),
  "species_currently_claimed_elsewhere":sum(x["claim_conflict"] for x in candidates),
  "first_12_targets":eligible[:12],
  "cautions":[
   "An iNaturalist observation is not automatically a true species confirmation; exact identity must be checked.",
   "Counts are based on installed images, not quality or diagnostic coverage. More photos may not be necessary.",
   "Non-native comparison records remain non-native; no native label is inferred.",
   "Photo licensing is based on owner's direct grant with original iNaturalist recorded license retained.",
   "Pending or claimed taxa from other workflows should be skipped until available."]
 }
 (out/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
 print(json.dumps(summary,indent=2),flush=True)
if __name__=="__main__":main()
