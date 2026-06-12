# Novel Source Discovery - 2026-06-12 Editor Diagnostic / State Record / Observability

## Purpose

This note records a static intake pass for long-form fiction tooling patterns that improve MuMuAINovel book-remix, continuation, and same-type writing support.

No upstream project was installed, executed, cloned deeply, or connected to a provider/runtime.

## Sources

- `HarishDvs/Grizzly`
  - Observed HEAD: `7d5d1f3afb9893c71092bf5436f4b1848b91b12a`
  - License: MIT
  - Family: fiction editor skill / diagnostic codex
  - Posture: pattern-only
- `aihxp/scriveno`
  - Observed HEAD: `e135a8601098aea159ac43dcd2e81ebb2c8855fa`
  - License: MIT
  - Family: spec-driven writing / publishing / translation workflow
  - Posture: pattern-only; runtime-deferred publishing and translation
- `ayermac/novelos`
  - Observed HEAD: `3208717776e94c926289f3653a770067f04ddf36`
  - License: MIT
  - Family: local-first desktop long-form fiction workbench
  - Posture: pattern-only; runtime-deferred desktop/LangGraph sidecar

## Absorbed Patterns

### Author-keeps-the-pen diagnostic codex

- Put diagnosis, structure, memory, continuity, and voice-spec evidence before rewrite suggestions.
- Build extractive cards for chapters, arcs, characters, threads, and accepted facts.
- Keep side-by-side fixes as candidates until the author accepts them.

### Spec-driven state / outline / record separation

- Separate workflow position (`STATE`), story structure (`OUTLINE`), and established content (`RECORD`).
- Track open threads, reader promises, payoffs, continuity facts, and progress ledger separately.
- Route polish, prepublish review, continuity merge checks, publishing, and translation through explicit gates.

### Desktop workflow memory observability

- Treat planner, screenwriter, author, polisher, editor, memory curator, and publisher as auditable workflow stages.
- Record node events, artifacts, retries, recovery, memory backfill, provider/token boundaries, and run status.
- Add publish-safety checks for continuity, memory readiness, malformed/truncated chapter titles, and style bible readiness.

## Runtime-Deferred Gates

The following remain blocked until a separate local safety contract names scope, files, providers, outputs, reviewer, cleanup, and rollback:

- PowerShell skill execution or upstream prompt-body import.
- npm package install, generated skill execution, publishing/export commands, or translation pipelines.
- Electron/FastAPI sidecar launch, LangGraph execution, local workspace indexing, provider routing, or publish actions.

## MuMuAINovel Mapping

- `author_keeps_pen_diagnostic_codex_gate`
  - Adds diagnostic card codex, author-control checkpoint, voice-spec findings, and side-by-side fix review hints.
- `spec_driven_state_record_publish_gate`
  - Adds state/outline/record separation, promise/payoff ledger, and publish/translation boundary hints.
- `desktop_langgraph_memory_observability_gate`
  - Adds inspectable agent handoffs, run artifact trace, memory backfill, recovery, and publish safety hints.

## Verification

Expected validation:

```text
python -m py_compile backend/app/services/source_discovery_service.py backend/app/services/source_pattern_pack_prompt.py backend/tests/services/test_source_discovery_service.py backend/tests/frontend/test_source_discovery_panel_copy.py
python -m pytest backend/tests/services/test_source_discovery_service.py::test_editor_diagnostic_state_observability_sources_are_static_absorbed -q
python -m pytest backend/tests/frontend/test_source_discovery_panel_copy.py -q
python -m pytest backend/tests/services/test_source_discovery_service.py -q
npm --prefix frontend run build
git diff --check
```
