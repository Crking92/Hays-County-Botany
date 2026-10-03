#!/usr/bin/env python3
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
import hashlib
import json
import os
import shlex
import subprocess
import threading

PORT = int(os.environ.get("HAYS_BOTANY_PORT", "8000"))
ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "research-queue.json"
AUDIT_PATH = ROOT / "workflow" / "approval-audit.jsonl"
MAX_BODY = 64 * 1024
WRITE_LOCK = threading.Lock()

ALLOWED_DECISIONS = {
    "approve_for_curation",
    "needs_more_review",
    "hold_unresolved",
    "approve_as_comparison",
    "approve_with_range_exception",
    "reject",
}
COMPARISON_ROLES = {
    "LOOKALIKE_COMPARISON",
    "INVASIVE_COMPARISON",
    "NON_NATIVE_COMPARISON",
    "COMMON_WEED_COMPARISON",
}


def now_iso():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def revision_for(raw):
    return hashlib.sha256(raw).hexdigest()


def read_queue():
    raw = QUEUE_PATH.read_bytes()
    return json.loads(raw.decode("utf-8")), revision_for(raw)


def write_queue(queue):
    text = json.dumps(queue, indent=2, ensure_ascii=False) + "\n"
    raw = text.encode("utf-8")
    tmp = QUEUE_PATH.with_name(QUEUE_PATH.name + ".tmp")
    tmp.write_bytes(raw)
    os.replace(tmp, QUEUE_PATH)
    return revision_for(raw)


def range_status(item):
    explicit = (
        item.get("native_range_status")
        or item.get("range_status")
        or item.get("target_zone_status")
        or (item.get("project_inclusion") or {}).get("target_zone_status")
    )
    if explicit:
        return str(explicit).upper()
    notes = str(item.get("notes") or "").upper()
    if "UNRESOLVED" in notes:
        return "UNRESOLVED"
    if (
        "RANGE FAIL" in notes
        or "NATIVE-STATUS FAIL" in notes
        or "TARGET-ZONE FAIL" in notes
        or "STRICT TARGET-ZONE FAIL" in notes
    ):
        return "FAIL"
    if "PASS" in notes:
        return "PASS"
    return "UNKNOWN"


def recommended_comparison_role(item):
    role = str(item.get("learner_role") or "").upper()
    if role.endswith("_RECOMMENDED"):
        role = role[: -len("_RECOMMENDED")]
    if role in COMPARISON_ROLES:
        return role
    notes = str(item.get("notes") or "").upper()
    if "INVASIVE" in notes:
        return "INVASIVE_COMPARISON"
    if "NON-NATIVE" in notes or "INTRODUCED" in notes:
        return "NON_NATIVE_COMPARISON"
    return "LOOKALIKE_COMPARISON"


def artifact_index(queue):
    root = ROOT / "research-drafts"
    if not root.exists():
        return {}
    files = [
        p for p in root.rglob("*")
        if p.is_file() and p.suffix.lower() in {".json", ".txt", ".md", ".csv"}
    ]
    result = {}
    for item in queue.get("items", []):
        item_id = str(item.get("id") or "").lower()
        if not item_id:
            continue
        matches = []
        for path in files:
            rel = path.relative_to(ROOT).as_posix()
            if item_id in rel.lower():
                matches.append(rel)
        if matches:
            result[item_id] = sorted(matches)[:12]
    return result


def audit_tail(limit=40):
    if not AUDIT_PATH.exists():
        return []
    rows = []
    for line in AUDIT_PATH.read_text(encoding="utf-8").splitlines()[-limit:]:
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def append_audit(record):
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def maybe_git_commit(item_id):
    if os.environ.get("HAYS_BOTANY_APPROVAL_AUTO_COMMIT") != "1":
        return {"enabled": False}
    try:
        subprocess.run(
            ["git", "add", "research-queue.json", "workflow/approval-audit.jsonl"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        result = subprocess.run(
            ["git", "commit", "-m", f"botany: approval decision {item_id}"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return {
            "enabled": True,
            "ok": result.returncode == 0,
            "message": (result.stdout or result.stderr).strip()[-1200:],
        }
    except Exception as exc:
        return {"enabled": True, "ok": False, "message": str(exc)}


def maybe_sync_tracker():
    command = os.environ.get("HAYS_BOTANY_APPROVAL_SYNC_COMMAND", "").strip()
    if not command:
        return {"enabled": False}
    try:
        result = subprocess.run(
            shlex.split(command),
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
        return {
            "enabled": True,
            "ok": result.returncode == 0,
            "message": (result.stdout or result.stderr).strip()[-1200:],
        }
    except Exception as exc:
        return {"enabled": True, "ok": False, "message": str(exc)}


def decision_note(decision, note):
    if note:
        return note
    defaults = {
        "approve_for_curation": "Approved in the local Hays Botany approval dashboard.",
        "needs_more_review": "Held for additional review in the local Hays Botany approval dashboard.",
        "hold_unresolved": "Explicitly held unresolved in the local Hays Botany approval dashboard.",
        "approve_as_comparison": "Approved as an encounter/comparison taxon in the local Hays Botany approval dashboard.",
        "approve_with_range_exception": "Explicitly approved as a documented range-evidence exception in the local Hays Botany approval dashboard.",
        "reject": "Rejected from the current curation path in the local Hays Botany approval dashboard.",
    }
    return defaults[decision]


def apply_decision(item, decision, note):
    rng = range_status(item)
    if decision == "approve_for_curation":
        if rng in {"FAIL", "UNRESOLVED"}:
            raise ValueError(
                f"{rng} records cannot use normal approval. Use comparison retention, more review, rejection, or an explicit unresolved exception."
            )
        item["status"] = "approved_pending_curation"
        item["approval_status"] = "user_approved"
    elif decision == "needs_more_review":
        item["status"] = "needs_manual_review"
        item["approval_status"] = "needs_manual_review"
    elif decision == "hold_unresolved":
        item["status"] = "needs_manual_review"
        item["approval_status"] = "needs_manual_review"
    elif decision == "approve_as_comparison":
        item["status"] = "approved_comparison_pending_curation"
        item["approval_status"] = "user_approved_comparison_retention"
        item["learner_role"] = recommended_comparison_role(item)
        item["native_metrics_excluded"] = True
    elif decision == "approve_with_range_exception":
        if rng != "UNRESOLVED":
            raise ValueError("Range exceptions are only allowed for UNRESOLVED records.")
        item["status"] = "approved_pending_curation"
        item["approval_status"] = "approved_with_range_exception"
        item["range_exception"] = {
            "approved": True,
            "approved_at": now_iso(),
            "reason": "Explicit human approval; unresolved county evidence remains preserved.",
        }
    elif decision == "reject":
        item["status"] = "rejected"
        item["approval_status"] = "user_rejected"
    else:
        raise ValueError("Unsupported decision.")

    item["user_decision"] = {
        "decision": decision,
        "decided_at": now_iso(),
        "note": decision_note(decision, note),
    }


class BotanyHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()

    def send_json(self, status, payload):
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def origin_ok(self):
        origin = self.headers.get("Origin")
        if not origin:
            return True
        return origin in {
            f"http://127.0.0.1:{PORT}",
            f"http://localhost:{PORT}",
        }

    def approval_payload(self, queue, revision):
        return {
            "queue": queue,
            "revision": revision,
            "write_enabled": True,
            "artifacts": artifact_index(queue),
            "audit_tail": audit_tail(),
        }

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/health":
            self.send_json(200, {"ok": True, "write_enabled": True})
            return
        if path == "/api/approvals":
            try:
                queue, revision = read_queue()
                self.send_json(200, self.approval_payload(queue, revision))
            except Exception as exc:
                self.send_json(500, {"error": str(exc)})
            return
        super().do_GET()

    def do_POST(self):
        path = urlparse(self.path).path
        if path != "/api/approvals/decision":
            self.send_json(404, {"error": "Unknown API path."})
            return
        if not self.origin_ok():
            self.send_json(403, {"error": "Origin not allowed."})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if length <= 0 or length > MAX_BODY:
            self.send_json(413, {"error": "Invalid request size."})
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:
            self.send_json(400, {"error": "Request body must be valid JSON."})
            return

        item_id = str(payload.get("item_id") or "").strip()
        decision = str(payload.get("decision") or "").strip()
        expected_revision = str(payload.get("expected_revision") or "").strip()
        note = str(payload.get("note") or "").strip()[:2000]

        if not item_id or decision not in ALLOWED_DECISIONS:
            self.send_json(400, {"error": "Invalid item_id or decision."})
            return
        if not expected_revision:
            self.send_json(409, {"error": "Missing queue revision. Refresh the approval page before saving."})
            return

        with WRITE_LOCK:
            try:
                queue, current_revision = read_queue()
                if expected_revision != current_revision:
                    self.send_json(
                        409,
                        {
                            "error": "The queue changed after this page loaded. Refresh before making this decision.",
                            "revision": current_revision,
                        },
                    )
                    return

                item = next((x for x in queue.get("items", []) if x.get("id") == item_id), None)
                if item is None:
                    self.send_json(404, {"error": "Approval item not found."})
                    return

                before = {
                    "status": item.get("status"),
                    "approval_status": item.get("approval_status"),
                    "learner_role": item.get("learner_role"),
                    "user_decision": item.get("user_decision"),
                }
                apply_decision(item, decision, note)
                new_revision = write_queue(queue)
                audit_record = {
                    "timestamp": now_iso(),
                    "item_id": item_id,
                    "scientific_name": item.get("scientific_name"),
                    "batch_id": item.get("batch_id"),
                    "decision": decision,
                    "note": item["user_decision"]["note"],
                    "revision_before": current_revision,
                    "revision_after": new_revision,
                    "before": before,
                    "after": {
                        "status": item.get("status"),
                        "approval_status": item.get("approval_status"),
                        "learner_role": item.get("learner_role"),
                        "user_decision": item.get("user_decision"),
                    },
                }
                audit_warning = None
                try:
                    append_audit(audit_record)
                except Exception as exc:
                    audit_warning = str(exc)

                git_result = maybe_git_commit(item_id)
                sync_result = maybe_sync_tracker()
                response = self.approval_payload(queue, new_revision)
                response.update(
                    {
                        "decision": audit_record,
                        "git_commit": git_result,
                        "sheet_sync": sync_result,
                    }
                )
                if audit_warning:
                    response["audit_warning"] = audit_warning
                self.send_json(200, response)
            except ValueError as exc:
                self.send_json(400, {"error": str(exc)})
            except Exception as exc:
                self.send_json(500, {"error": str(exc)})


if __name__ == "__main__":
    print(f"Hays Botany learner + approval server: http://localhost:{PORT}")
    print("Browser caching is disabled so interface updates appear immediately.")
    print("Approval writes are accepted only on this local server and use optimistic revision checks.")
    ThreadingHTTPServer(("127.0.0.1", PORT), BotanyHandler).serve_forever()
