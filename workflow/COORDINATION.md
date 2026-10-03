# Hays Botany Work Coordination

This file defines the shared anti-duplication protocol for all ChatGPT chats, automations, local tools, and manual project work.

## Authoritative state order

Before selecting any new work, refresh from `main` and check these sources in order:

1. `data/manifest.json` — canonical installed truth. If a taxon ID is here, do not research or install it as a new taxon.
2. `workflow/work-claims.json` — reservations for work that another chat/process has claimed but may not have written elsewhere yet.
3. `research-queue.json` — queued, reviewed, approved, held, rejected, and historical species workflow state.
4. `research-drafts/` — existing scout/research work. Reuse or improve the draft instead of creating a second draft.
5. `curation-inbox/` and current GitHub Actions — work already entering the canonical pipeline.
6. The relevant family/genus/website/video workflow files for non-species work.

If any source shows the same taxon or scope is already being worked at the same stage, skip it and choose another target unless the existing claim explicitly names the current process as a collaborator.

## Claim-before-work rule

A chat or automation must create or refresh a claim in `workflow/work-claims.json` before beginning substantial work that is not already represented by a queue record, research draft, curation-inbox batch, or other persistent workflow artifact.

Claims are especially useful during the gap between “I chose this target” and “I wrote the first durable project file.”

Use a claim for:
- species scouting/research
- deep review
- curation/package construction
- family backfill/module construction
- major website structural work
- video/species reconciliation

Do not create a second claim for work already durably reserved by the queue/draft/inbox unless a stage-specific claim is needed to prevent two workers from editing the same item simultaneously.

## Claim fields

Each claim should include:
- a stable `claim_id`
- `scope_kind`
- exact `taxa`, `families`, or `scope_key`
- `lane`
- `owner`
- `status`: `queued`, `active`, `blocked`, or `released`
- `claimed_at`
- `expires_at` for short-lived active claims when practical
- a short `release_when` rule
- notes when needed

## Lease behavior

- Manual-chat active claims should normally expire after about 6 hours unless refreshed.
- Automation active claims should normally expire after about 2 hours unless refreshed.
- A deliberately queued reservation may use `expires_at: null`, but it must be ignored automatically if the taxon becomes canonical, appears in the research queue, gains a research draft, or is otherwise durably represented.
- Expired active claims may be reclaimed, but only after checking the authoritative state order above.

## Stage handoff

Typical species flow:

`source pool → claim → research draft/queue → deep review → approval → curation claim → curation-inbox → canonical manifest`

As soon as a later durable artifact exists, the earlier claim should be released or treated as superseded.

The unattended Scout stops at research drafts. Deep Review stops at review status. Curation/install workers own the curation inbox. Website and family workers do not silently promote species.

## Backpressure

The unattended Scout must not create an unlimited backlog. It should pause when either:
- 2 or more coherent scout batches are still awaiting deep review, or
- 10 or more noncanonical species are waiting for deep review.

## Conflict rule

When two processes collide:
- canonical manifest beats everything;
- existing durable queue/draft/inbox state beats a new claim;
- an older/stale claim never authorizes overwriting newer work;
- if the same target file changed after a worker read it, refetch and rebuild or abort;
- if ownership is ambiguous, skip the target rather than overwrite another process.

## Current lane boundaries

- Species operations/curation owns canonical species installation.
- Unfinished Plant Scout owns research gathering only.
- Botany Deep Review owns independent scientific review only.
- Family Backfill owns family-level modules and audit material.
- Website/UI work owns presentation/interface files, not scientific source-of-truth data.
- Joey/video extraction and reconciliation may feed species/family research but does not bypass taxonomy/range review.

The goal is not perfect locking. The goal is to make duplicate effort and destructive overlap rare, obvious, and recoverable.
