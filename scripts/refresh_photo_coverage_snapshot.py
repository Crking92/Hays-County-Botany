#!/usr/bin/env python3
"""Single authoritative photo-coverage snapshot after first-photo recovery.
Reports real zero-card counts separately from unresolved source/taxonomy placeholders.
No scientific or species/gallery edits.
"""
import collections,datetime,json,pathlib
ROOT=pathlib.Path(".")
data=json.loads((ROOT/"data/manifest.json").read_text(encoding="utf-8"))
records=collections.Counter();on_disk=collections.Counter();low=[];no_photo=[]
for item in data["species"]:
 p=ROOT/item["path"]
 if not p.is_file():raise SystemExit("Canonical manifest missing species file: "+str(p))
 s=json.loads(p.read_text(encoding="utf-8"))
 photos=s.get("images") or []
 count=len(photos)
 group="0" if not count else "1" if count==1 else "2" if count==2 else "3+"
 records[group]+=1
 local_files=sum(1 for row in photos if row.get("file") and
   not str(row["file"]).startswith(("http://","https://")) and
   (p.parent/row["file"]).is_file())
 on_disk["0" if not local_files else "1" if local_files==1 else "2" if local_files==2 else "3+"]+=1
 if count<=2:
  low.append({"id":item["id"],"scientific_name":s.get("scientific_name"),
    "gallery_records":count,"installed_local_files":local_files})
 if not count:
  source_concept=bool(s.get("id")=="muhlenbergia-piniflora" and
    s.get("project_inclusion",{}).get("target_zone_status")=="PROVISIONAL" and
    "source name appears erroneous" in str(s.get("look_here_first") or "").lower())
  no_photo.append({"id":item["id"],"scientific_name":s.get("scientific_name"),
    "status":"TAXON_SOURCE_CONCEPT_HOLD" if source_concept else "MISSING_FIRST_PHOTO",
    "reason":"The provisional source name is unverified; DO NOT substitute Muhlenbergia dubia media without taxonomic approval" if source_concept else "Needs exact-name, individually licensed image"})
report={"generated_at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
 "canonical_species":len(data["species"]),
 "gallery_image_record_counts":dict(records),
 "physically_installed_local_image_counts":dict(on_disk),
 "zero_one_two_photo_species":low,
 "zero_gallery_items":no_photo,
 "genuine_photo_gap_count":sum(x["status"]=="MISSING_FIRST_PHOTO" for x in no_photo),
 "unresolved_taxon_source_concept_holds":sum(x["status"]=="TAXON_SOURCE_CONCEPT_HOLD" for x in no_photo),
 "meaning":"First-photo coverage metrics are raw gallery records and physical local files. Photograph identity/anatomical diagnostic usefulness still requires expert visual verification. Source-concept holds retain their honest zero-gallery status."}
path=ROOT/"reports/photo-coverage-latest.json"
path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps({k:report[k] for k in ("generated_at_utc","canonical_species","gallery_image_record_counts","physically_installed_local_image_counts","zero_gallery_items","genuine_photo_gap_count","unresolved_taxon_source_concept_holds")},indent=2))
