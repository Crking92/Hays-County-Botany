#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import copy
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "research-queue.json"
BACKUP_DIR = ROOT / "local-backups"

DECISION_FIELDS = (
    "user_decision",
    "status",
    "approval_status",
    "learner_role",
    "native_metrics_excluded",
    "range_exception",
)


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        list(args),
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if check and result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise RuntimeError(detail or f"Command failed: {' '.join(args)}")
    return result


def changed_tracked_files() -> set[str]:
    names = set()
    for cmd in (
        ("git", "diff", "--name-only"),
        ("git", "diff", "--cached", "--name-only"),
    ):
        result = run(*cmd)
        names.update(x.strip().replace("\\", "/") for x in result.stdout.splitlines() if x.strip())
    return names


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def decision_time(item: dict) -> str:
    decision = item.get("user_decision") or {}
    return str(decision.get("decided_at") or "")


def merge_local_approvals(local_queue: dict, fresh_queue: dict) -> tuple[dict, int, int]:
    local_items = {
        str(item.get("id")): item
        for item in local_queue.get("items", [])
        if item.get("id")
    }
    merged = copy.deepcopy(fresh_queue)
    restored = 0
    skipped_newer_remote = 0

    for item in merged.get("items", []):
        item_id = str(item.get("id") or "")
        local = local_items.get(item_id)
        if not local or not local.get("user_decision"):
            continue

        local_time = decision_time(local)
        remote_time = decision_time(item)
        if remote_time and local_time and remote_time >= local_time:
            skipped_newer_remote += 1
            continue

        for field in DECISION_FIELDS:
            if field in local:
                item[field] = copy.deepcopy(local[field])
        restored += 1

    return merged, restored, skipped_newer_remote


def main() -> int:
    print()
    print("Hays Botany - safe update")
    print("-------------------------")

    try:
        inside = run("git", "rev-parse", "--is-inside-work-tree").stdout.strip()
        if inside != "true":
            raise RuntimeError("This folder is not a Git repository.")

        changed = changed_tracked_files()
        unrelated = sorted(x for x in changed if x != "research-queue.json")
        if unrelated:
            print()
            print("Update stopped because these tracked files have local edits:")
            for path in unrelated:
                print(f"  - {path}")
            print()
            print("Nothing was changed. Ask ChatGPT to reconcile these files before updating.")
            return 2

        local_queue = None
        if "research-queue.json" in changed and QUEUE.exists():
            local_queue = load_json(QUEUE)
            BACKUP_DIR.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            backup = BACKUP_DIR / f"research-queue-{stamp}.json"
            write_json(backup, local_queue)
            print(f"Saved local approval backup: {backup.relative_to(ROOT)}")
            run("git", "restore", "--staged", "--worktree", "research-queue.json")

        print("Fetching latest GitHub changes...")
        run("git", "fetch", "origin", "main")
        print("Updating local files...")
        run("git", "pull", "--ff-only", "origin", "main")

        if local_queue is not None and QUEUE.exists():
            fresh_queue = load_json(QUEUE)
            merged, restored, skipped = merge_local_approvals(local_queue, fresh_queue)
            write_json(QUEUE, merged)
            print(f"Restored {restored} local approval decision(s) onto the fresh queue.")
            if skipped:
                print(f"Kept {skipped} newer/equal remote approval decision(s).")

        head = run("git", "rev-parse", "--short", "HEAD").stdout.strip()
        print()
        print(f"Ready. Local site is on Git commit {head}.")
        print("Starting the visual learner...")
        return 0

    except Exception as exc:
        print()
        print(f"SAFE UPDATE FAILED: {exc}")
        print("No destructive reset was performed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
