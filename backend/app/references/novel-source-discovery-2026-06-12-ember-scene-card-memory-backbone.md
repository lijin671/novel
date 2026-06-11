# EMBER static intake - 2026-06-12

## Source

- Repository: `KleinDigitalSolutions/EMBER`
- URL: `https://github.com/KleinDigitalSolutions/EMBER`
- Observed HEAD: `b3b9c0204b6002cce1cf3771a71c32680f1fe58a`
- Default branch: `main`
- License: no license observed through GitHub metadata
- Stars / forks at intake: `0 / 0`
- Observed pushed time: `2026-06-04T08:33:57Z`

## Intake posture

`pattern-only`.

Reviewed only public GitHub repository metadata, `git ls-remote`, root tree
names, and README markers. No clone, package install, runtime launch, provider
call, script execution, database setup, Supabase connection, `.env` read, or
secret read was performed.

## Static markers

The README describes EMBER as a structured long-form fiction environment built
around:

- scene-card pipeline
- persistent Memory Backbone
- stateful draft engine
- Canon Ledger
- Object Ledger
- open plot threads
- reader promises
- typed `BookStateDiff`
- human approval before canon entry
- quality audit that warns without automatic rewrite
- Human Edit Memory from accepted edits

Root tree markers include `.env.example`, `AGENTS.md`, book pipeline notes,
Next.js files, package manifests, `scripts`, and `supabase`.

## Absorbed patterns

### `scene_card_hard_soft_field_gate`

Scene cards should distinguish authority:

- hard canon fields: required facts and constraints
- soft guidance fields: tone, direction, and optional emphasis

The writer must obey hard canon. It should not copy soft guidance wording into
final prose or treat optional guidance as fact.

### `canon_object_ledger_bookstate_diff_gate`

Canon facts, object holders/locations, open plot threads, reader promises, and
knowledge reveals should be separate state surfaces.

After an accepted draft, a typed `BookStateDiff` should declare:

- facts changed
- objects moved
- knowledge revealed
- promises reinforced
- approval status

Human approval gates what enters canon. Draft text alone cannot mutate the
Canon Ledger or Object Ledger.

### `human_edit_memory_quality_warn_gate`

Quality audits should warn, explain, and route revision decisions back to the
author. They should not silently auto-rewrite accepted prose.

Human Edit Memory should store only accepted local edits as preference evidence.
Rejected edits and warning-only notes stay out of canon and out of default
style authority.

## Risks and blocked surfaces

Static markers expose model/provider, package-manager, script, Supabase, and
host-instruction surfaces.

Blocked during intake and future default runs:

- no package install
- no script execution
- no Supabase/database setup
- no provider/model call
- no `.env` or secret read
- no upstream `AGENTS.md` import as instruction
- no runtime service launch

## Project mapping

Updated artifacts:

- `NovelSourceDiscoveryService` default GitHub discovery seed
- `PATTERN_KEYWORDS`
- static repository pattern override
- source pattern pack targets and hints
- inspired same-type creation remap / prompt / transformation / copy-risk hints
- source pattern pack digest allowlist
- focused regression test

## Verification

Focused test:

```powershell
python -m pytest backend/tests/services/test_source_discovery_service.py::test_static_ember_source_adds_scene_card_ledger_diff_and_human_edit_gates -q
```

Observed result:

```text
1 passed, 3 warnings
```
