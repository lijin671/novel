# Novel source discovery - 2026-06-14 Spec Kit fiction scene-task gates

Source: `https://github.com/adaumann/speckit-preset-fiction-book-writing`

Observed static revision: `c31b629ef8c733eb4e3af8643a5761ee9328fec0`

Local static review cache: `tmp/source-intake-speckit-fiction-20260614`

License posture: GitHub repository metadata did not expose a top-level SPDX license during intake. The reviewed preset subdirectory includes an MIT license marker. Treat this as pattern-only unless a future runtime/code import separately verifies license scope.

## Static files reviewed

- `README.md`
- `catalog.community.json`
- `fiction-book-writing/README.md`
- `fiction-book-writing/preset.yml`
- `fiction-book-writing/templates/spec-template.md`
- `fiction-book-writing/templates/tasks-template.md`
- `fiction-book-writing/templates/scene-outline-template.md`
- `fiction-book-writing/templates/pov-structure-template.md`
- `fiction-book-writing/commands/speckit.continuity.md`
- `fiction-book-writing/commands/speckit.tasks.md`
- `fiction-book-writing/commands/speckit.pacing.md`
- `fiction-book-writing/commands/speckit.polish.md`

One probed file returned 404 and was not used: `fiction-book-writing/templates/continuity-template.md`.

## Absorbed patterns

- `story_bible_constitution_source_gate`
  - Keep a constitution/story-bible authority before drafting.
  - Use it for voice, tense, audience, hard constraints, and accepted canon.

- `scene_outline_approval_status_gate`
  - Draft only from approved scene outlines.
  - Keep required context, RAG/query needs, hook, goal, obstacle, turn, and exit state visible.

- `pov_information_asymmetry_schedule_gate`
  - Track POV schedule and information asymmetry before multi-POV drafting.
  - Separate what the POV knows, what the reader knows, and what remains hidden.

- `pacing_arc_polish_pass_gate`
  - Run pacing/tension checks before polish.
  - Require checklist PASS before export or final acceptance.

## Projection into MuMuAINovel

Implemented as repo-native gates, not imported upstream code:

- Source discovery metadata now recognizes the four Spec Kit fiction gates.
- Pattern-pack output adds whole-book analysis targets, bible enrichment targets, inspired remap targets, and digest-visible hints.
- Continuation context preview now exposes `Spec Kit fiction scene-task audit`.
- Production control audit now reports `spec_kit_fiction_warnings` for missing constitution, approved scene outlines, POV/asymmetry map, or pacing/checklist evidence.
- Source Discovery UI now surfaces a dedicated `Spec Kit fiction scene-task gates` panel.

## Safety boundary

This was static intake only.

No clone, install, package execution, command execution, provider call, browser runtime, MCP runtime, or upstream prompt-body transplant was performed. Upstream files are treated as untrusted reference data. Only abstract workflow gates were reimplemented.
