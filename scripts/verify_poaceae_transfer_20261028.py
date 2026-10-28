#!/usr/bin/env python3
"""Verify Poaceae repository transfer against a pinned source Git-tree manifest.

READ-ONLY: never edits the source or destination. Run from any checkout with
--manifest <path> --target <destination checkout root>.
Canonical Git blob SHA-1 checks the exact bytes of each file. This is not
a photo-license/publication check; those are separate gates.
"""
import argparse
import hashlib
import json
from pathlib import Path

def git_blob_hash(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()

def run(manifest_file: Path, target_root: Path) -> dict:
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    assert manifest["schema"] == "hays-poaceae-source-baseline-v1"
    expected = {item["path"]: item for item in manifest["files"]}
    assert len(expected) == manifest["file_count"], "duplicate source path"
    missing, changed, present = [], [], 0
    for path, item in expected.items():
        if not path.startswith("content/taxa/Poaceae/") or ".." in Path(path).parts:
            raise ValueError("unsafe manifest path " + path)
        candidate = target_root / path
        if not candidate.is_file():
            missing.append(path)
            continue
        data = candidate.read_bytes()
        sha = git_blob_hash(data)
        if len(data) != item["bytes"] or sha != item["git_blob_sha"]:
            changed.append({"path":path,"expected_size":item["bytes"],
                            "found_size":len(data),"expected_git_blob_sha":item["git_blob_sha"],
                            "found_git_blob_sha":sha})
        else:
            present += 1
    family_path = target_root / "content/taxa/Poaceae"
    found_paths = {
        f.relative_to(target_root).as_posix()
        for f in family_path.rglob("*") if f.is_file()
    } if family_path.exists() else set()
    extra = sorted(found_paths - set(expected))
    result = {
        "source_snapshot_commit":manifest["snapshot_commit"],
        "expected_files":manifest["file_count"],
        "expected_bytes":manifest["total_bytes"],
        "byte_identical_files":present,
        "missing_files":len(missing),
        "changed_files":len(changed),
        "extra_files":len(extra),
        "missing":missing[:250],
        "changed":changed[:100],
        "extra":extra[:250],
        "byte_verified":not missing and not changed and not extra,
        "migration_approved":False,
        "note":"Full site links, copyrights, arrows, scientific data, UX, cross-family comparisons, publishing and final source sync require separate checks."
    }
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest",type=Path,required=True)
    parser.add_argument("--target",type=Path,required=True)
    parser.add_argument("--report",type=Path)
    args=parser.parse_args()
    result=run(args.manifest.resolve(),args.target.resolve())
    print(json.dumps({k:v for k,v in result.items() if k not in ("missing","changed","extra")},indent=2))
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    raise SystemExit(0 if result["byte_verified"] else 1)
