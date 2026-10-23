#!/usr/bin/env python3
"""Audit remaining externally hosted grass images without removing or copying any."""
import collections,json,pathlib,urllib.parse,datetime
manifest=json.loads(pathlib.Path("data/manifest.json").read_text())
records=[];summary=collections.Counter()
for item in manifest["species"]:
 if "/Poaceae/" not in item["path"]:continue
 d=json.loads(pathlib.Path(item["path"]).read_text())
 for photo in d.get("images",[]):
  link=photo.get("file","")
  if not link.startswith(("https://","http://")):continue
  host=urllib.parse.urlparse(link).netloc
  if host in ("commons.wikimedia.org","upload.wikimedia.org"):group="WIKIMEDIA_IMAGE_LEVEL_RECHECK"
  elif host=="w3.biosci.utexas.edu":group="UT_EDUCATIONAL_REUSE_PERMISSION_REVIEW"
  elif host=="inaturalist-open-data.s3.amazonaws.com":group="INAT_IMAGE_LEVEL_LICENSE_REVIEW"
  else:group="SOURCE_SPECIFIC_PERMISSION_REVIEW"
  summary[group]+=1
  license=photo.get("license","")
  note="Existing declared license is NOT independent rights verification"
  records.append({"species":d["id"],"file_url":link,"creator":photo.get("creator"),"declared_license":license,"license_url":photo.get("license_url"),"source_page":photo.get("source_page"),"role":photo.get("role"),"priority":"HIGH" if any(t in str(photo.get("role","")).lower() for t in ("ligule","lemma","spikelet","collar","awn","floret","anther")) else "NORMAL","action":group,"rights_note":note})
report={"date_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"summary":dict(summary),"external_total":len(records),"non_wikimedia":sum(v for k,v in summary.items() if k!="WIKIMEDIA_IMAGE_LEVEL_RECHECK"),"records":records,"no_images_changed":True}
out=pathlib.Path("reports/grass-external-rights-and-importance-triage.json");out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({"total":len(records),"groups":dict(summary)},indent=2))
