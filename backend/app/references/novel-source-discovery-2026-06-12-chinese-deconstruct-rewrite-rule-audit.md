# Novel Source Discovery - Chinese Deconstruct, Rewrite, Rule-Audit, and Template-Resume Gates (2026-06-12)

## Scope

Static source intake for MuMuAINovel book deconstruction, continuation, same-type writing, rewrite safety, and long-form workflow resumption.
No dependency install, package script, CLI invocation, provider call, API-key use, ZIP unpack, FastAPI/Node runtime, generated text import, uploaded reference novel import, or deployment command was performed.
Static review used public GitHub Search, `git ls-remote`, and shallow scratch clones under `tmp/source-intake-2026-06-12-chinese-continuation-rewrite-audit/repos`.

## Sources

### XTmingyue/harnessNovel

- URL: https://github.com/XTmingyue/harnessNovel
- Reachable HEAD: `95e9b64f7a457b492c05d9c84dba4b1211c33c4e`
- License marker: GPL-3.0
- Static markers: long-form web-novel AI agent, two-stage "Deconstruct + Imitate", full-book outline, worldbuilding, volume outlines, chapter summaries, plot pacing, emotional beats, writing style, character voices, progressive worldbuilding, breakpoint continuation.
- Absorbed pattern: `harnessnovel_deconstruct_imitate_gate`
- Posture: pattern-only.

Reusable lesson:

- ????????????????????????????????????
- ?????????????????????????????????????????
- GPL ???CLI??????API key?????????????????????

### jiejiu344/novel-rule-auditor-skill

- URL: https://github.com/jiejiu344/novel-rule-auditor-skill
- Reachable HEAD: `627c89bb7739ec1d1e8f29f9db8eeaf73bb0c7b5`
- License marker: not observed
- Static markers: generation-rule learning, rule audit, draft/final comparison, updating `????.md`, continuation, chapter revision, pre/post chapter audit loop, collaboration with novel-writer.
- Absorbed pattern: `novel_rule_auditor_learning_loop_gate`
- Posture: pattern-only.

Reusable lesson:

- ????/????????????????????????
- ??????????????????????/??????????
- ZIP ????prompt body????????????????????

### qscwzby7t6-svg/novel-rewriter

- URL: https://github.com/qscwzby7t6-svg/novel-rewriter
- Reachable HEAD: `dd0c8b5ebd3b99d592d9a983e72622309d9aeb21`
- License marker: not observed
- Static markers: million-word novel rewriting, FastAPI backend, Node CLI, DeepSeek/OpenAI-compatible provider, fallback provider/model, chapter budget, context window, de-AI switch, copyright check, quality check, quality threshold, split-by-chapter output.
- Absorbed pattern: `novel_rewriter_copyright_cost_gate`
- Posture: pattern-only.

Reusable lesson:

- ??/??????????????? AI ??????????????
- ???? fallback ??????/???????????????????
- ??????????API key?provider call???????????????

### keyboardgdy/woke_novel

- URL: https://github.com/keyboardgdy/woke_novel
- Reachable HEAD: `a5d17b791d233d53870878379fc668fbd4511635`
- License marker: MIT
- Static markers: Claude/Codex CLI workflow, template-driven pipeline, 20 workflow templates, strict Markdown templates, resumable project cursor, multi-session orchestration, dry-run mode, project-local artifacts under baseline/plots/guides/output/state/characters.
- Absorbed pattern: `woke_novel_template_resume_cli_gate`
- Posture: pattern-only.

Reusable lesson:

- ????????? template id?artifact contract ? project cursor??????????
- ?????? session-bounded phases?? dry-run/preview????????????
- Claude/Codex CLI??????prompt ????????????????????? intake?

## MuMuAINovel integration

Updated source-discovery surfaces:

- default GitHub queries for deconstruct-imitate, rule-auditor learning loops, copyright/cost rewrite checks, and template-resume CLI workflows
- default repository seeds for all four sources
- static repository summaries with license/runtime boundaries
- pattern keyword detection for four gates
- pattern-pack fields:
  - `harnessnovel_deconstruct_imitate_gate_hints`
  - `novel_rule_auditor_learning_loop_gate_hints`
  - `novel_rewriter_copyright_cost_gate_hints`
  - `woke_novel_template_resume_cli_gate_hints`
- bible enrichment targets:
  - `deconstruct_imitate_reference_boundary_policy`
  - `style_worldbuilding_abstraction_policy`
  - `generation_rule_audit_learning_policy`
  - `draft_final_delta_rule_update_policy`
  - `copyright_quality_cost_control_policy`
  - `provider_fallback_budget_boundary_policy`
  - `template_resume_project_cursor_policy`
  - `cli_prompt_runtime_exclusion_policy`
- whole-book analysis targets:
  - `deconstruct_imitate_boundary_report`
  - `style_worldbuilding_abstraction_findings`
  - `reference_plot_leakage_review`
  - `generation_rule_audit_report`
  - `draft_final_delta_learning_trace`
  - `repeat_error_prevention_findings`
  - `copyright_similarity_quality_report`
  - `chapter_budget_provider_fallback_trace`
  - `deai_quality_threshold_findings`
  - `template_resume_cursor_report`
  - `workflow_artifact_folder_trace`
  - `cli_runtime_prompt_boundary_findings`
- inspired creation remap targets:
  - `deconstruct_imitate_reference_remap`
  - `generation_rule_delta_remap`
  - `copyright_quality_budget_remap`
  - `template_cursor_resume_remap`

## Runtime exclusions

Still blocked unless a separate local safety contract exists:

- pip/npm install, install scripts, service launch, FastAPI/Node runtime, systemd/deployment commands
- Claude/Codex CLI invocation, provider/model calls, API-key use, global config writes
- ZIP skill unpack/import, upstream prompt body import, generated rule file import
- uploaded reference novels, generated prose, local project outputs, browser/session data

## Verification anchors

Expected local verification after integration:

```text
python -m py_compile backend/app/services/source_discovery_service.py backend/app/services/source_pattern_pack_prompt.py backend/tests/services/test_source_discovery_service.py backend/tests/frontend/test_source_discovery_panel_copy.py
python -m pytest backend/tests/services/test_source_discovery_service.py::test_chinese_deconstruct_rewrite_rule_audit_sources_are_static_absorbed -q
python -m pytest backend/tests/frontend/test_source_discovery_panel_copy.py -q
```
