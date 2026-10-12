#!/usr/bin/env python3
"""Regenerate learner lesson index from actual family/genus JSON files.

Run automatically when lesson modules change; do not infer module completion from species counts.
"""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
taxa=root/"content"/"taxa"
families=sorted(p.parent.name for p in taxa.glob("*/family.json") if p.is_file())
genera=sorted(({"family":p.parent.parent.name,"genus":p.parent.name} for p in taxa.glob("*/*/genus.json") if p.is_file()),key=lambda x:(x["family"],x["genus"]))
out={"version":1,"families":families,"genera":genera}
target=root/"data"/"lesson-index.json"
target.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(f"Indexed {len(families)} family modules and {len(genera)} genus modules")
