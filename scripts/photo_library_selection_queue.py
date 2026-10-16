#!/usr/bin/env python3
"""Prepare a manual, library-first image REVIEW queue without installing anything."""
import collections,csv,datetime,json,pathlib
R=pathlib.Path(".");L=R/"workflow/photo-library"
OUT=R/"reports/photo-library-selection-queue-latest.json"
MD=R/"reports/photo-library-selection-queue-latest.md"
HOLD={"muhlenbergia-piniflora"}
# Curated source-name aliases: these two historical determinations are already documented
# in their canonical species records. Allow REVIEW only; identity still needs human validation.
REVIEW_SOURCE_ALIASES={"anatherum-glomeratum":{"andropogon glomeratus"},
                       "opuntia-engelmannii-var-lindheimeri":{"opuntia lindheimeri"}}
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def key(s):return " ".join(str(s or "").strip().lower().replace("×","x ").split())
def local_count(p,images):
    n=0
    for a in images:
        f=a.get("file") or ""
        if f and not f.startswith(("http://","https://")):
            loc=(p.parent/f).resolve()
            if loc.is_relative_to(R.resolve()) and loc.is_file():n+=1
    return n
def library():
    rows=collections.defaultdict(list); batches=[]; stats=collections.Counter()
    for path in sorted((L/"batches").glob("*/archive.json")):
        a=read(path)
        if a.get("persistent_release") is not True:continue
        csvfile=path.parent/"candidates.csv"
        if not csvfile.is_file():continue
        batches.append({"batch":a["batch_id"],"tag":a["private_release_tag"],
                        "asset":a["asset_name"],"checksum":a["asset_sha256"]})
        with csvfile.open(newline="",encoding="utf-8-sig") as f:
            for x in csv.DictReader(f):
                stats["rows"]+=1
                if not x.get("staged_file"):continue
                if x.get("photo_license_status")!="supported" or x.get("license_basis")!="media":continue
                if x.get("identity_status")!="exact_name_metadata_only_review_image":continue
                if x.get("license") not in {"CC0","CC0 1.0","CC BY","CC BY-SA","CC BY-NC","CC BY-NC-SA"}:continue
                item={"scientific_name":x.get("scientific_name",""),
                      "image_url":x.get("image_url",""),"source_page":x.get("source_page",""),
                      "observation_id":x.get("observation_id",""),"creator":x.get("creator",""),
                      "license":x.get("license",""),"source":x.get("source",""),
                      "archive_tag":a["private_release_tag"],"asset_name":a["asset_name"],
                      "archive_file":x["staged_file"],"status":"ARCHIVED_PROVISIONAL_VISUAL_REVIEW_REQUIRED"}
                rows[x.get("canonical_id","")].append(item)
                stats["archived_individually_licensed_candidates"]+=1
    return rows,batches,dict(stats)
def claims_now():
    p=R/"workflow/work-claims.json"
    if not p.exists():return {}
    now=datetime.datetime.now(datetime.timezone.utc)
    res=collections.defaultdict(list)
    for c in read(p).get("claims",[]):
        if c.get("status") not in ("active","queued","blocked"):continue
        expire=c.get("expires_at")
        if expire:
            try:
                dt=datetime.datetime.fromisoformat(expire.replace("Z","+00:00"))
                if dt.tzinfo is None:dt=dt.replace(tzinfo=datetime.timezone.utc)
                if dt<now:continue
            except ValueError:pass
        for id in c.get("taxa") or []:res[id].append(c.get("claim_id","unknown"))
    return res
def main():
    manifest=read(R/"data/manifest.json")
    sources,batches,stats=library()
    claims=claims_now()
    inbox=set()
    for p in (R/"curation-inbox").rglob("species.json"):
        try:inbox.add(read(p)["id"])
        except (KeyError,ValueError,OSError):pass
    groups=collections.Counter(); physical=collections.Counter()
    available=[]; no_candidate=[]; holds=[]
    for row in manifest["species"]:
        id=row["id"];p=R/row["path"];s=read(p)
        photos=s.get("images") or []; n=len(photos); disk=local_count(p,photos)
        groups["0" if n==0 else "1" if n==1 else "2" if n==2 else "3+"]+=1
        physical["0" if disk==0 else "1" if disk==1 else "2" if disk==2 else "3+"]+=1
        if n>1 and disk>0:continue
        used=set()
        for ph in photos:
            used.update(ph.get(k) for k in ("source_page","media_source_url","downloaded_from","direct_url") if ph.get(k))
        seen=set(); candidates=[]
        for x in sources.get(id,[]):
            if key(x["scientific_name"])!=key(s.get("scientific_name")) and key(x["scientific_name"]) not in REVIEW_SOURCE_ALIASES.get(id,set()):continue
            if x["image_url"] in used:continue
            unique=x["image_url"] or (x["archive_tag"],x["archive_file"])
            if unique in seen:continue
            seen.add(unique);candidates.append(x)
        observations=len(set(c["observation_id"] for c in candidates if c["observation_id"]))
        item={"id":id,"scientific_name":s.get("scientific_name"),
              "gallery_records":n,"local_files":disk,
              "archived_choices":len(candidates),"source_observations":observations,
              "creators":len(set(c["creator"] for c in candidates if c["creator"])),
              "review_prompt":str(s.get("look_here_first") or "")[:280],
              "candidate_images":candidates[:8],
              "pending_visual_identity_and_diagnostic_validation":True}
        if id in HOLD or id in claims or id in inbox:
            item["blocker"]="taxon_hold" if id in HOLD else ("active_or_queued_claim" if id in claims else "curation_inbox")
            holds.append(item)
        elif candidates:available.append(item)
        else:no_candidate.append(item)
    available.sort(key=lambda x:(0 if x["gallery_records"]<=1 and x["local_files"]==0 else 1 if x["gallery_records"]<=1 else 2,
                                 -min(x["archived_choices"],8),-x["source_observations"],x["id"]))
    stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
    idx=read(L/"species-index.json")
    report={"generated_at_utc":stamp,"canonical_species":len(manifest["species"]),
            "gallery_image_record_counts":dict(groups),"physically_installed_local_image_counts":dict(physical),
            "library_index_generated_at":idx.get("last_rebuilt_utc"),
            "library_photos_stored":idx.get("stored_images"),
            "library_distinct_species":idx.get("distinct_species_with_candidates"),
            "archive_batches":batches,"archive_screen":stats,
            "ready_for_manual_visual_review_count":len(available),
            "no_usable_archived_image_count":len(no_candidate),
            "hold_or_owned_count":len(holds),
            "review_shortlist":available[:20],
            "more_review_candidates":available[20:],
            "needs_more_source_photos":no_candidate,"blocked_by_claim_or_hold":holds,
            "installed_new_images":0,
            "notes":"No photos installed. Individual media license and exact source-name metadata are only preliminary gates; inspect archive JPEGs and diagnostic parts before choosing."}
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    md=["# Library-first manual photo selection queue","",
        "Updated: "+stamp,"",
        "No photos were installed. Verify real image content, taxon identity and anatomical roles before selection.","",
        f"Canonical species: **{len(manifest['species'])}**; galleries: 0={groups['0']}, 1={groups['1']}, 2={groups['2']}, 3+={groups['3+']}.",
        f"Local photo files per card: 0={physical['0']}, 1={physical['1']}, 2={physical['2']}, 3+={physical['3+']}.",
        f"Ready for manual image review: **{len(available)}**; need more archived candidates: **{len(no_candidate)}**; held/claimed: **{len(holds)}**.",
        "","## First 20 library-backed review targets","",
        "| Plant | Gallery / locally saved | Saved candidate photos | Source observations |",
        "|---|---:|---:|---:|"]
    for x in available[:20]:
        md.append(f"| *{x['scientific_name']}* | {x['gallery_records']} / {x['local_files']} | {x['archived_choices']} | {x['source_observations']} |")
    md+=["","## Install only after manual photo review","",
         "Check the actual archive images and licensing, select complementary anatomical views rather than repetitive overviews, then apply existing vetted installer. Preserve science and original credits.",
         "Existing automations continue unchanged. Collection and installation are separate lanes.",
         "Full reviewed-candidate metadata, release names, missing-source and hold lists: reports/photo-library-selection-queue-latest.json.",""]
    MD.write_text("\n".join(md),encoding="utf-8")
    print(json.dumps({"species":len(manifest["species"]),"gallery":dict(groups),"local":dict(physical),
       "review_targets":len(available),"needs_sources":len(no_candidate),"blocked":len(holds),
       "first_10":[x["id"] for x in available[:10]]},indent=2))
if __name__=="__main__":main()
