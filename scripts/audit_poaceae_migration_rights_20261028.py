#!/usr/bin/env python3
"""Read-only Poaceae source and rights census for a SEPARATE future public repo.

Writes JSON report, never alters source, photographs, or Pages. The source
snapshot is complete and still authoritative. A 'candidate' means the
existing individual record appears reusable under explicit broad licenses;
NOT an automatic independent legal determination.
"""
from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import json
import re

from build_public_pages_snapshot import rights

PHOTO_SUFFIX={".jpg",".jpeg",".png",".webp",".gif",".tif",".tiff"}
FAMILY="content/taxa/Poaceae/"
CC_GENERAL=re.compile(r"\bcc\s*[- ]?0\b|\bcc\s*[- ]?by(?:\s*[- ]?(?:nc|sa)){0,2}\b|public domain|\bpd[- ]?mark\b",re.I)
STRICT_DENY=re.compile(r"held|not verified|not cleared|private.?study|all rights reserved|copyright|permission required|study only|no public|pending",re.I)

def classify(item: dict):
    fn=str(item.get("file") or "").strip()
    if not fn or fn.startswith(("http://","https://")):
        return "external_or_missing_local_file"
    license_text=str(item.get("license") or "")
    public_reuse=str(item.get("public_reuse") or "")
    if item.get("site_specific_public_permission"):
        return "website_specific_grant_requires_review"
    if STRICT_DENY.search(license_text+" "+public_reuse):
        return "explicit_rights_hold"
    if not CC_GENERAL.search(license_text):
        return "no_general_public_license"
    allowed,reason=rights(item,True)
    if not allowed:
        return "existing_public_rights_check_rejects: "+str(reason)[:80]
    return "general_license_candidate"

def inspect(root: Path, manifest: dict):
    files=manifest["files"]
    allowed_by_path={}
    details=[]
    totals=Counter()
    for rel in sorted(f["path"] for f in files if f["path"].endswith("/species.json")):
        doc=json.loads((root / rel).read_text(encoding="utf-8"))
        stem=Path(rel).parent
        outcomes=Counter()
        for im in doc.get("images",[]):
            file=im.get("file")
            reason=classify(im)
            if isinstance(file,str) and not file.startswith(("http://","https://")):
                source=(stem/file)
                rel_source=source.as_posix()
                if not source.is_file():
                    reason="missing_source_photo"
                elif not str(source.resolve()).startswith(str((root / FAMILY).resolve())):
                    reason="unsafe_or_cross_family_source_path"
                else:
                    if reason=="general_license_candidate":
                        allowed_by_path[rel_source]=True
            outcomes[reason]+=1
            details.append({"species":doc.get("id"),"image_record":file,"status":reason,
                  "creator":im.get("creator"),"license":im.get("license"),"public_reuse":im.get("public_reuse")})
        totals.update(outcomes)
    categories=Counter()
    file_records=[]
    for row in files:
        path=row["path"]
        if not path.startswith(FAMILY):raise RuntimeError("unexpected nonfamily manifest file "+path)
        ext=Path(path).suffix.lower()
        if ext in PHOTO_SUFFIX:
            status="general_license_candidate" if path in allowed_by_path else "not_in_reusable_source_image_set"
        else:
            status="taxon_data_or_provenance"
        categories[status]+=1
        file_records.append({"path":path,"bytes":row["bytes"],"git_blob_sha":row["git_blob_sha"],"class":status})
    assert len(file_records)==manifest["file_count"]
    assert sum(f["bytes"] for f in file_records)==manifest["total_bytes"]
    assert sum(v for v in categories.values())==manifest["file_count"]
    result={
        "status":"READ_ONLY_RIGHTS_RECONCILIATION_NOT_TRANSFER",
        "source_git_commit":manifest["snapshot_commit"],
        "source_full_file_count":manifest["file_count"],
        "source_full_bytes":manifest["total_bytes"],
        "source_species_cards":sum(r["path"].endswith("/species.json") for r in files),
        "image_record_classification":dict(totals),
        "source_file_classification":dict(categories),
        "source_file_rows":file_records,
        "image_record_details":details,
        "notes":[
           "Full 1402-file source manifest must always stay intact in original/backups.",
           "New public family repo MUST NOT contain source rights-held photos even in git history.",
           "CC BY-NC is for noncommercial use; license and creator terms must still be followed.",
           "Site-specific education grants do not automatically move to new website.",
           "Photo source classification is a conservative candidate inventory, not permission to publish without public rights preflight.",
           "Potentially redundant source files and metadata are retained until target is independently verified.",
           "No actual transfer, binary copy, main-branch change, or Pages deployment was attempted."
        ]
    }
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,default=Path("."))
    parser.add_argument("--manifest",type=Path,required=True)
    parser.add_argument("--report",type=Path,required=True)
    a=parser.parse_args()
    result=inspect(a.root.resolve(),json.loads(a.manifest.read_text(encoding="utf-8")))
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("POACEAE_RIGHTS_AUDIT",json.dumps({k:v for k,v in result.items() if k not in ("source_file_rows","image_record_details","notes")},ensure_ascii=False))
    print("SOURCE_STAYS_INTACT")
if __name__=="__main__":main()
