# Novel source discovery - 2026-06-14 Story Foundry production handoff projection

## Source

- GitHub: `mmunro3318/story-foundry`
- Public HEAD: `6a56cc7fe07ec0b3eb00b6eef16035f4bc058646`
- Default HEAD ref: `refs/heads/master`
- License: no root `LICENSE` observed from raw probe
- Intake posture: `pattern-only`

## Static evidence used

Bounded public probes only:

- `git ls-remote --symref https://github.com/mmunro3318/story-foundry.git HEAD`
- raw `README.md`
- raw `CLAUDE.md`
- raw `agent-template.md`
- raw `workflow/capture/CLAUDE.md`
- raw `workflow/distillation/CLAUDE.md`
- raw `workflow/production/CLAUDE.md`
- raw `docs/templates/scene-card-template.md`
- raw `docs/templates/story-bible.json`

No clone, checkout, install, package manager, slash-command runtime, Claude Code
runtime, provider call, browser runtime, prompt-body import, or credential read
was used.

## Reusable pattern

Story Foundry's useful pattern is not its runtime. It is the production handoff
shape:

- Capture, Distillation, and Production are separate artifact layers.
- Scene cards carry both external spine and internal rail before prose.
- Production advances through draft -> critique -> numbered fix_spec ->
  revised draft -> editor_log -> canon promotion.
- Only an archivist-style role promotes accepted artifacts into manuscript,
  bible, index, changelog, or durable canon state.
- Agent cards declare inputs, outputs, limits, QA gates, permissions, RACI,
  failure recovery, context budget, and telemetry.

## MuMuAINovel projection

This pass maps the pattern into continuation preview gates:

- `capture_distillation_production_stage_boundary`
- `scene_card_external_internal_spine`
- `draft_critique_fixspec_revision_chain`
- `archivist_canon_promotion_telemetry`
- `production_handoff_warnings`

The context preview now warns when the latest accepted chapter has no critique,
fix_spec, revision evidence, editor log, or archivist/canon-promotion evidence,
and when the current plan lacks a scene-card spine with both external and
internal pressure.

## Safety boundary

Runtime remains blocked for clone, checkout, install, slash-command execution,
Claude Code/agent launch, provider/model call, browser/MCP/desktop runtime,
prompt-body import, credential read, host/model config mutation, and remote push.
