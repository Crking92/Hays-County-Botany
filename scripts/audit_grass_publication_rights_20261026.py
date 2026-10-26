#!/usr/bin/env python3
"""Non-mutating evidence screen for 112 Poaceae gallery rights.
Noncommercial CC licenses are conditional per public learner policy, not automatic bans.
"""
import collections,datetime,json,pathlib,re
R=pathlib.Path(".")
manifest=json.loads((R/"data/manifest.json").read_text())
strong=set(json.loads((R/"reports/grass-current-photo-readiness-20261025.json").read_text())["four_role_candidates"])
joey=json.loads((R/"workflow/JOEY_PHOTO_CREDITED_PUBLIC_PERMISSION_20261021.json").read_text())
whitelist=set(joey.get("authorized_images",[]))
lanes={}
for n in range(1,6):
 txt=(R/f"workflow/grass-five-chat-split-20261023/CHAT_{n}.md").read_text()
 lanes[str(n)]=set(re.findall(r"^\|\s*P[0-3]\s*\|\s*"+chr(96)+r"([a-z0-9-]+)"+chr(96),txt,re.M))
allcards=[i for i in manifest["species"] if i["path"].startswith("content/taxa/Poaceae/") and i["path"].endswith("/species.json")]
rights=[];bob=[];cards=[];counts=collections.Counter()
def lane(id):return next((n for n,ids in lanes.items() if id in ids),None)
for o in allcards:
 id=o["id"];path=R/o["path"];data=json.loads(path.read_text())
 scientific=str(data.get("scientific_name","")).casefold()
 gallery=data.get("visual_comparison",{}).get("items",[]) or []
 images=data.get("images",[]) or []
 mine=[]
 for panel in gallery:
  lic=str(panel.get("license") or "")
  up=lic.upper()
  if not ("BY-NC" in up or "BY NC" in up or "NONCOMMERCIAL" in up):continue
  source=panel.get("source_page") or panel.get("source_url") or ""
  creator=panel.get("creator") or panel.get("photographer") or ""
  rel=id+"/images/"+str(panel.get("image_url","")).rsplit("/",1)[-1]
  rec={
    "id":id,"lane":lane(id),"strong_candidate":id in strong,
    "label":panel.get("label"),"scientific_name":panel.get("scientific_name"),
    "same_species":str(panel.get("scientific_name","")).casefold()==scientific,
    "license":lic,"license_url":panel.get("license_url"),
    "creator":creator,"source_page":source,"image_url":panel.get("image_url"),
    "has_creator_and_source":bool(creator and source),
    "has_license_url":bool(panel.get("license_url")),
    "locally_linked":str(panel.get("image_url","")).startswith("content/"),
    "is_joey_whitelisted_video_frame":rel in whitelist and "Joey Santore" in creator and ("youtube.com" in source or "youtu.be" in source),
    "decision":"SITE_CONDITIONALLY_POSSIBLE_IF_IMAGE_LEVEL_LICENSE_AND_CREDIT_VALID_NONCOMMERCIAL; NOT COMMERCIALLY_UNRESTRICTED"
  }
  rights.append(rec);mine.append(rec)
  counts["NC_panels"]+=1
  if rec["has_creator_and_source"]:counts["NC_creator_and_source"]+=1
  if rec["has_license_url"]:counts["NC_license_url"]+=1
  if rec["same_species"]:counts["NC_same_species"]+=1
  if rec["locally_linked"]:counts["NC_local"]+=1
  if "joey" in str(creator).lower():counts["NC_Joey"]+=1
  if id in strong:counts["NC_in_31"]+=1
 for image in images:
  who=str(image.get("creator",""))+" "+str(image.get("license",""))
  if "bob harms" not in who.lower():continue
  rel=image.get("file") or ""
  exists=bool(rel and (path.parent/rel).is_file())
  bob.append({"id":id,"file":rel,"physically_present":exists,"creator":image.get("creator"),
    "source_page":image.get("source_page"),"license":image.get("license"),
    "warning":"Specific 2026-10-22 Bob Harms permission memo explicitly authorizes sourced external display for reviewed Selected Monocots images, not copying or annotating pixels. Reconcile any locally stored copy against independently documented permission."})
  counts["bob_record"]+=1
  if exists:counts["bob_local"]+=1
 cards.append({"id":id,"lane":lane(id),"candidate_four_roles":id in strong,
   "NC_panels":len(mine),"NC_same_species":sum(x["same_species"] for x in mine),
   "NC_creator_and_source":sum(x["has_creator_and_source"] for x in mine),
   "NC_license_url":sum(x["has_license_url"] for x in mine)})
 if mine:counts["species_with_NC"]+=1
lane_rollup={}
for n in range(1,6):
 group=[c for c in cards if c["lane"]==str(n)]
 cand=[c for c in group if c["candidate_four_roles"]]
 lane_rollup[str(n)]={
  "assigned":len(lanes[str(n)]),"31_candidate_ids":[c["id"] for c in cand],
  "candidate_count":len(cand),"candidate_NC_panels":sum(c["NC_panels"] for c in cand),
  "NC_gallery_panels":sum(c["NC_panels"] for c in group),
  "species_with_NC":[c["id"] for c in group if c["NC_panels"]]}
by_creator=collections.Counter(x["creator"] or "[unknown]" for x in rights)
report={
 "created_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
 "scope":"Main canonical 112 Poaceae species, image-level license/creator/source metadata screen only",
 "policy":"workflow/PUBLIC_PHOTO_REUSE_POLICY_20261019.md — permits properly attributed and photo-specific CC BY-NC/NC-SA on genuinely noncommercial standalone educational site conditionally",
 "joey_permission":"workflow/JOEY_PHOTO_CREDITED_PUBLIC_PERMISSION_20261021.json — narrow enumerated video-frame overlay, not general relicense",
 "harms_permission":"workflow/photo-source-permissions/bob-harms-selected-monocots-educational-20261022.json — copyrighted scientific/educational use, enumerated external display only; not a general CC license",
 "warning":"Neither gallery label nor site noncommercial intent alone verifies photographer identity, exact photo rights, science ID, or whether live Pages actually publishes the image. Do not auto-remove or automatically republish.",
 "summary":{"grass_species":len(allcards),"gallery_panels":sum(len((json.loads((R/o["path"]).read_text()).get("visual_comparison") or {}).get("items") or []) for o in allcards),
  "NC_gallery_panels":counts["NC_panels"],"NC_panels_with_creator_and_source":counts["NC_creator_and_source"],
  "NC_panels_with_license_url":counts["NC_license_url"],
  "NC_same_species_panels":counts["NC_same_species"],"NC_locally_linked_panels":counts["NC_local"],
  "NC_in_31_candidate_panels":counts["NC_in_31"],"NC_Joey_panels":counts["NC_Joey"],
  "species_with_NC_gallery":counts["species_with_NC"],
  "Bob_Harms_local_media_records_needing_permission_scope_reconciliation":counts["bob_local"],
  "Bob_Harms_all_canonical_media_records":counts["bob_record"]},
 "lanes":lane_rollup,
 "candidate_NC_species":[c for c in cards if c["candidate_four_roles"] and c["NC_panels"]],
 "top_NC_creators":by_creator.most_common(),
 "NC_panel_records":rights,
 "Bob_Harms_media_records":bob,
 "species_rollup":cards
}
out=R/"reports/grass-publication-rights-check-20261026.json"
out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({"summary":report["summary"],"lanes":lane_rollup,"top_creators":by_creator.most_common(15),"candidate_nc_species":report["candidate_NC_species"]}))
