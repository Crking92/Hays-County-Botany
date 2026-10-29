#!/usr/bin/env python3
"""Resolve NEW Hays Botany botanical writes to a family repository, never old hub.

Examples:
  python scripts/resolve_new_plant_write.py Poaceae Schizachyrium schizachyrium-scoparium
  python scripts/resolve_new_plant_write.py Fabaceae Senegalia senegalia-greggii
  python scripts/resolve_new_plant_write.py --audit

No commit, source edit, web publishing, media download, or automation restart.
"""
import argparse
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/"workflow/ACTIVE_NEW_PLANT_WRITE_ROUTING_20261028.json"
STAGING=ROOT/"planning/MULTI_REPO_FAMILY_ROUTING_DRAFT_20261028.json"
SLUG=re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
GENUS=re.compile(r"^[A-Z][a-zA-Z-]*$")

def load_and_validate():
    a=json.loads(REGISTRY.read_text())
    historical=json.loads(STAGING.read_text())
    assert a["policy"]=="ACTIVE_PROSPECTIVE_PLANT_DATA_WRITE_ROUTING"
    assert a["future_writes_to_original_content_taxa"] is False
    assert a["future_writes_to_original_data_manifest"] is False
    assert not a["public_site_cutover_approved"]
    routes=a["family_to_repository"]
    branches=a["repository_write_branches"]
    assert len(routes)==a["family_destinations_verified"]==146
    assert len(branches)==a["collection_count"]==10
    assert routes==historical["family_to_planned_repository"]
    assert all(v in branches for v in routes.values())
    assert all(k.endswith("aceae") for k in routes)
    assert branches["Hays-Botany-Poaceae"]=="main"
    assert all(branches[n].startswith("staging/") for n in branches if n!="Hays-Botany-Poaceae")
    return a

def main():
    p=argparse.ArgumentParser()
    p.add_argument("family",nargs="?")
    p.add_argument("genus",nargs="?")
    p.add_argument("slug",nargs="?")
    p.add_argument("--audit",action="store_true",help="Verify the complete ten-repository, 146-family registry")
    args=p.parse_args()
    a=load_and_validate()
    if args.audit:
        print(json.dumps({"status":"PASS_NEW_WRITES_ONLY","families":146,"collections":10,
            "original_hub_plant_writes_allowed":False,
            "public_site_cutover":False},sort_keys=True))
        return
    if not args.family:
        p.error("Provide family or --audit")
    if args.family not in a["family_to_repository"]:
        p.error("Unassigned family: stop for explicit route review; NEVER write to old hub")
    if bool(args.genus)!=bool(args.slug):
        p.error("Provide both genus and species slug, or family alone")
    if args.genus and not GENUS.fullmatch(args.genus):
        p.error("Genus must be an exact accepted genus token")
    if args.slug and not SLUG.fullmatch(args.slug):
        p.error("Species ID must be a lowercase hyphenated slug")
    repo=a["family_to_repository"][args.family]
    result={"action":"WRITE_NEW_PLANT_DATA_IN_FAMILY_REPO","repository":"Crking92/"+repo,
            "branch":a["repository_write_branches"][repo],
            "original_hub_writable":False,
            "live_pages_cutover_approved":False,
            "family":args.family}
    if args.genus:
        result["target_path"]="content/taxa/"+args.family+"/"+args.genus+"/"+args.slug
        result["expected_species_card"]=result["target_path"]+"/species.json"
    print(json.dumps(result,indent=2,sort_keys=True))
if __name__=="__main__":
    main()
