# Novel Source Discovery - InkOS confirmed action audit recovery

Date: 2026-06-12
Source: https://github.com/Narcooo/inkos
Observed HEAD: bfee6519b1c6fa57ac33af804178fe1fc1e3bdeb
License: AGPL-3.0
Posture: pattern-only / no runtime import

## Static intake boundary

Reviewed public GitHub metadata, `git ls-remote HEAD`, root tree metadata,
`package.json`, and public README markers only.

Not performed: npm/pnpm install, ClawHub install, Studio/TUI/CLI launch,
provider/model call, secret/API-key read, sample project execution, or generated
project import.

## Reusable pattern

InkOS adds one low-overlap gate for MuMuAINovel:

`confirmed_action_audit_recovery_gate`

The durable lesson is not the InkOS runtime. The useful pattern is the chapter
action contract:

- heavy write/rewrite/continue actions need explicit action labels and
  confirmation before generation;
- completion is proven by tool/file artifacts, not model prose;
- each chapter action has pre-write checklist, post-write settlement, snapshot,
  audit verdicts, revision count, unresolved critical findings, state delta,
  and rollback pointer;
- automatic revision is limited, so unresolved critical findings stay visible
  for human review instead of being buried by repeated rewrites;
- state updates are schema-validated immutable deltas rather than free-form
  silent overwrites.

## Local adaptation

For 拆书续写:

- before drafting, record source refs, chapter scope, context slice, accepted
  canon, recovery snapshot, and action label;
- after drafting, require settlement table and audit dimensions before chapter
  promotion;
- keep unresolved critical findings in continuation context until a later action
  resolves them with evidence.

For 同类型仿写:

- rebuild the action/audit contract around the new story;
- do not copy InkOS prompt bodies, audit wording, style lists, project state, or
  runtime traces;
- reject drafts where missing confirmation, hidden revision debt, dropped
  unresolved findings, or source audit wording becomes new-story authority.

## Implemented artifacts

- `confirmed_action_audit_recovery_gate` pattern detection
- default GitHub query and repository seed
- pattern pack hints for continuation prompts, continuation state, bible targets,
  whole-book analysis targets, and same-type copy-risk review
- frontend type and panel surface
- backend and frontend copy tests

## Deferred/runtime gates

Runtime remains blocked for npm package execution, ClawHub/OpenClaw skill
installation, Studio/TUI/CLI launch, provider/model calls, `.env` or API-key
reads, file watchers, generated book imports, and any upstream script.
