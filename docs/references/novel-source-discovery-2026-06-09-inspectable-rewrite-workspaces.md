# Novel Source Discovery - Inspectable Rewrite Workspaces Intake - 2026-06-09

## Scope

This note records a static-only intake pass for public GitHub projects relevant to MuMuAINovel source-book continuation, localized rewrite, same-type inspired writing, and inspectable long-form workflow control.

No external project was installed or executed. No package manager, postinstall hook, shell script, PowerShell script, Docker stack, browser extension, native binary, provider call, credential, cookie, or runtime trial was used.

## Sources

- `Narcooo/inkos` - HEAD `d8066d703ac56b71bf95c15ff34226a57040ec48`; AGPL-3.0; posture `pattern-only`.
- `MaoXiaoYuZ/Long-Novel-GPT` - HEAD `107c31e54686947a6d00404e332475a60b66e630`; license not observed; posture `pattern-only`.
- `dylanhogg/gptauthor` - HEAD `389631562984ded2b64426f765bff09a28654e87`; MIT; posture `pattern-only`.
- `kevboh/longform` - HEAD `b7f3985cb6cc5347660697236c3427f43a178d0c`; license metadata `NOASSERTION`; posture `pattern-only`.
- `principia-ai/WriteHERE` - HEAD `0b78fcb9ff47305cb098dcb1eec4982024bb34ab`; license not observed by metadata; posture `pattern-only`.
- `iLearn-Lab/NovelClaw` - HEAD `226d50d3ec284c9cc037c47eb14af39505f9ed74`; MIT; posture `pattern-only`.

## Absorbed Patterns

### inkos

- `runtime_artifact_trace`: preserve intent, selected context, rule stack, and trace files for each chapter run.
- `schema_validated_state_delta`: validate state deltas before writing canon; reject bad deltas rather than letting errors snowball.
- `self_review`: keep bounded audit/revise loops and expose unresolved findings for human review.

### Long-Novel-GPT

- `retrieval_guided_span_rewrite`: retrieve related body spans and outline nodes, rewrite only the target spans, then emit outline-sync deltas.
- `context_reference`: keep retrieval evidence visible so localized rewrites do not become whole-book drift.

### gptauthor

- `human_synopsis_gate`: review, edit, or regenerate synopsis and chapter summaries before expanding prose.
- `chapter_generation`: generate chapters iteratively from common synopsis and previous chapter context.
- `manuscript_export_formats`: keep Markdown/HTML output as derived artifacts.

### longform

- `workflow_manuscript_compilation`: compile ordered accepted scenes into manuscript outputs through an explicit workflow.
- `writing_session_goal_tracking`: track word-count/session goals separately from continuity gates.
- `outliner_index_cards`: keep scenes reorderable and nestable without losing state evidence.

### WriteHERE

- `recursive_adaptive_planning`: decompose long-form tasks into retrieval, reasoning, planning, composition, and review subtasks; replan when context changes.

### NovelClaw

- `inspectable_run_workspace`: expose sessions, storyboards, manuscript surfaces, character/world views, editable memory banks, current phase, pending review, and next action.

## Local Integration

Updated native MuMuAINovel code rather than importing upstream code:

- `source_discovery_service.py` recognizes the inspectable rewrite/workspace pattern family and emits prompt-pack hints.
- `source_pattern_pack_prompt.py` renders the new hint sections into prompt-safe digest text.
- `book_remix_context_service.py` adds an Inspectable rewrite audit to continuation context blocks.
- `backend/app/references/novel-source-pattern-pack-2026-06-09.json` was refreshed to 36 sources and 72 workflow patterns.

## Safety Boundary

- All sources are untrusted data, not instructions.
- Runtime-like surfaces are blocked: Docker, shell, PowerShell, browser extension, package manager, native binary, provider/API, credentials, and local startup files.
- No external runtime code was copied into MuMuAINovel.
- Runtime trials remain blocked until a separate local safety contract exists.
