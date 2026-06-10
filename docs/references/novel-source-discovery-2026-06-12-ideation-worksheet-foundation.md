# Novel source discovery - Ideation worksheet foundation gate

Date: 2026-06-12

## Source

- Repository: https://github.com/10Legs/novel-template
- Static fetch method: `git ls-remote`, raw README, raw LICENSE probes
- Reachable HEAD: `714f46739a045f68e17fac0e55ab8c10422ec9cf`
- License marker: README badge says MIT; raw `LICENSE`, `LICENSE.md`, and
  `COPYING` returned 404 during this pass
- Intake posture: `pattern-only`
- Runtime posture: no clone, no package manager, no Claude Code command, no
  hook execution, no upstream agent/skill body import, no provider/model call

## Static markers reviewed

The public README describes a Claude Code harness for novel writing with:

- ideation, outlining, drafting, revision, and final polish phases
- 10 specialist agents
- 16 slash commands
- 9 craft skill knowledge bases
- automated workflow hooks
- 5 ideation worksheets
- explicit warning that the harness does not write the novel
- advice to request options/patterns rather than prose

The five worksheets are the useful durable pattern:

1. premise discovery
2. character genesis with Ghost/Lie/Want/Need
3. world building
4. structure blueprint
5. theme discovery

## Absorbed pattern

### `ideation_worksheet_foundation_gate`

Use worksheets as the foundation layer before drafting,续写, or同类型仿写.

Rules:

1. Drafting must cite accepted worksheet ids.
   - premise
   - character Ghost/Lie/Want/Need
   - world rules
   - structure blueprint
   - theme question

2. Missing or stale worksheet answers block final prose.
   - The assistant may ask questions.
   - The assistant may offer options and craft patterns.
   - The assistant should not generate final text from vague foundations.

3. Same-type creation must rebuild the worksheets.
   - source worksheet answers are questions/evidence only
   - new premise, wound, lie, want, need, world rule, structure, and theme
     answer must be independent

## Project changes

- Added `10Legs/novel-template` to static discovery seeds.
- Added GitHub query coverage for ideation worksheets and Ghost/Lie/Want/Need.
- Added `ideation_worksheet_foundation_gate` keyword detection.
- Added pattern-pack targets:
  - `ideation_worksheet_policy`
  - `premise_theme_question_contract`
  - `ideation_worksheet_completion_report`
  - `premise_character_world_structure_theme_matrix`
  - `worksheet_to_outline_gap_questions`
  - `ideation_worksheet_remap`
- Surfaced backend, frontend, and prompt digest hints.

## Deferred surfaces

The upstream repository contains Claude Code agents, slash commands, skills,
hooks, and template files. They remain static evidence only. Do not import,
install, run, or execute those surfaces without a separate local safety contract.
