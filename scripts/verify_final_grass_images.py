#!/usr/bin/env python3
"""Validate current Poaceae photo binaries, metadata and public-site prerequisites.
Read-only for species JSON; create report from current repository main only."""
import json,pathlib,collections,datetime,re
root=pathlib.Path(".");manifest=json.loads((root/"data/manifest.json").read_text())
summary=collections.Counter();issues=[];external=[];credit=[]
for entry in manifest["species"]:
 if "/Poaceae/" not in entry["path"]:continue
 p=root/entry["path"];d=json.loads(p.read_text());summary["species"]+=1
 for im in d.get("images",[]):
  summary["entries"]+=1;f=im.get("file","")
  if f.startswith(("https://","http://")):
   summary["external"]+=1;external.append({"species":d["id"],"url":f,"creator":im.get("creator"),"license":im.get("license"),"source":im.get("source_page")});continue
  fp=p.parent/f
  if not fp.is_file() or fp.stat().st_size<2000:
   issues.append({"species":d["id"],"file":f,"issue":"missing or too-small local file"})
  else:summary["local"]+=1
  if not im.get("creator") and not im.get("source_page"):
   credit.append({"species":d["id"],"file":f,"issue":"missing creator and source page"})
summary["missing_or_small"]=len(issues);summary["credit_review"]=len(credit)
out={"timestamp_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"summary":dict(summary),"missing":issues,"attribution_review":credit,"external_details":external,"website_note":"A confirmed GitHub Pages build plus browser image-load testing is required to certify rendering; local source checks alone cannot do this."}
path=root/"reports/grass-image-final-verification.json";path.parent.mkdir(exist_ok=True);path.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n")
print(json.dumps(out["summary"],indent=2))
