# Novel Source Discovery - 2026-06-12 State Contract / Living Documents / Continuity Engine

## Purpose

This note records a static intake pass for long-form fiction workflow projects that can improve MuMuAINovel's book-remix, continuation, and same-type writing behavior.

No upstream project was cloned deeply, installed, executed, or connected to a provider/runtime.

## Sources

- `mrigankad/Novel-OS`
  - Observed HEAD: `5f950095aaf397e82297e62423635b2f41edcc57`
  - License: MIT
  - Family: multi-agent fiction writing framework / persistent story state
  - Posture: pattern-only; runtime-deferred provider and agent execution
- `third-order-labs/longform-plugin`
  - Observed HEAD: `1623bed717e07b2625d430feaf8c70dd21a05a2b`
  - License: MIT
  - Family: long-form fiction methodology plugin / living documents
  - Posture: pattern-only; runtime-deferred plugin commands
- `danjdewhurst/story-skills`
  - Observed HEAD: `c482d48f4eb9b488f033a77a51f9fae55cc0d75f`
  - License: MIT
  - Family: Agent Skills markdown fiction project contract / deterministic continuity checker
  - Posture: pattern-only; runtime-deferred CLI and skill installation

## Absorbed Patterns

### StoryState output contract gate

- Split multi-agent chapter work into inspectable role handoffs.
- Require machine-parseable state-update blocks before updating persistent memory.
- Keep deterministic continuity and quality gates ahead of prose acceptance.

### Living document plan/log/verify gate

- Use `Plan -> Draft -> Log -> Verify -> Repeat` as the continuation loop.
- Update scene logs, continuity records, glossary, thread tracking, and foreshadowing after accepted chapters.
- Treat accepted canon as the conflict winner when living documents disagree.

### Markdown frontmatter continuity engine gate

- Store story contracts in markdown plus YAML frontmatter.
- Make continuity errors deterministic and file-addressed.
- Track dead-character appearances, payoff-before-setup, unfired Chekhov guns, stale state, and explicit mention-only exceptions.

## Runtime-Deferred Gates

The following remain blocked until a separate local safety contract names files, scope, provider, output custody, reviewer, cleanup, and rollback:

- Python agent runtime, provider calls, prompt execution, generated chapter writing, and local state parsing from Novel-OS.
- Cowork/Claude Code plugin command execution or manuscript document mutation from longform-plugin.
- Agent Skills installation, CLI execution, example import, or upstream skill-body import from story-skills.

## MuMuAINovel Mapping

- `story_state_output_contract_gate`
  - Adds state-update block parsing expectations, role-handoff reports, quality gate status, and state parser policy hints.
- `living_document_plan_log_verify_gate`
  - Adds plan/draft/log/verify continuation discipline, living-document update traces, and canon conflict policy hints.
- `markdown_frontmatter_continuity_engine_gate`
  - Adds frontmatter story contract, deterministic continuity reports, promise/payoff order findings, and mention-exception checks.

## Scratch Evidence

Static scratch artifacts were written under:

```text
tmp/source-intake-20260612-next-story-workflow/
```

The scratch directory contains public search notes, `git ls-remote` HEAD records, and raw README/LICENSE files used for marker review.

## Verification

Expected validation:

```text
python -m py_compile backend/app/services/source_discovery_service.py backend/app/services/source_pattern_pack_prompt.py backend/tests/services/test_source_discovery_service.py backend/tests/frontend/test_source_discovery_panel_copy.py
python -m pytest backend/tests/services/test_source_discovery_service.py::test_state_contract_living_document_frontmatter_sources_are_static_absorbed -q
python -m pytest backend/tests/frontend/test_source_discovery_panel_copy.py -q
python -m pytest backend/tests/services/test_source_discovery_service.py -q
npm --prefix frontend run build
git diff --check
```
