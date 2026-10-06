# Hays Botany Approval Dashboard

The Approvals tab records learner-admission decisions and exceptional overrides. During Learner Fast-Fill, taxa in Calvin's approved source pools / derived Master Plant Pool already have standing learner admission approval; the dashboard must not make native-range certification a second admission gate.

## Where it works

### Static / Cloudflare site
The page reads `research-queue.json` and shows the current queue, but it is read-only.

### Local project
Run `RUN_LOCAL_SERVER.bat` and open:

`http://localhost:8000`

The local Python server exposes a loopback-only approval API. The browser receives a SHA-256 revision of the queue. Every write must send that exact revision back. If another curation chat or process changed the queue first, the server returns a conflict and requires a refresh instead of overwriting newer work.

## Decision mapping

| Dashboard action | Queue result |
| --- | --- |
| Approve | learner admission approved; `status=approved_pending_curation`, `approval_status=user_approved`; existing native-range status is preserved |
| Needs more review | `status=needs_manual_review`, `approval_status=needs_manual_review` |
| Keep as comparison | learner admission approved; comparison learner role retained/normalized, native metrics excluded |
| Approve exception | legacy/backward-compatible action only; unresolved range evidence remains preserved |
| Reject | rejects the current learner/curation path |

**PASS, FAIL, UNRESOLVED, and CONFLICT are range metadata, not learner-admission states.** Normal Approve is allowed regardless of range status. A separate canonical card can still be blocked when the durable record says `approved_taxonomy_mapping_needed` or `represented_existing_no_new_card`; those cases must map to the correct accepted concept instead of creating a duplicate/misnamed page.

## Audit trail

Every successful local decision appends one JSON object to:

`workflow/approval-audit.jsonl`

Each record stores the item, batch, decision, note, before/after states, and queue revisions.

## Optional local automation

Automatic local Git commits are off by default.

To enable them for a session:

`set HAYS_BOTANY_APPROVAL_AUTO_COMMIT=1`

The server commits the queue and audit log after each successful decision. It does **not** push.

A future/local Google-Sheet sync helper may be connected without storing credentials in this repository by setting:

`HAYS_BOTANY_APPROVAL_SYNC_COMMAND`

The command is optional. If it is not configured, the project's standing ChatGPT-to-Google-Sheet sync workflow continues to mirror approved decisions.

## Safety constraints

- Server binds to `127.0.0.1` only.
- POST requests reject non-local browser origins.
- Request bodies are size-limited.
- Decisions are validated against an allow-list.
- Queue writes are atomic.
- A process-level lock serializes decisions.
- Optimistic revision checking prevents stale-page overwrites.
- No API keys, tokens, or Google credentials are stored in the repository.
