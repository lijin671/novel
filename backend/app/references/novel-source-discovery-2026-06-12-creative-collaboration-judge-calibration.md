# Novel Source Discovery - Creative Collaboration and Judge Calibration (2026-06-12)

## Scope

Static source intake for MuMuAINovel book deconstruction, continuation, and same-type creation.
No clone, install, dependency install, benchmark run, provider call, dataset import, script execution, or local manuscript access was performed.

## Sources

### google-deepmind/tell_me_a_story

- URL: https://github.com/google-deepmind/tell_me_a_story
- Reachable HEAD: `e4910ea1d2bae82efcaf8ba9fde50ab3a419320e`
- License: Apache-2.0
- Observed metadata: 47 stars, 6 forks, updated 2026-06-11T20:12:01Z
- Static markers: Tell Me A Story dataset, Agents' Room, multi-step collaboration, complex writing prompts, human-written stories, specialized narrative subtasks, long-narrative evaluation.
- Absorbed pattern: `agents_room_multistep_story_collaboration_gate`
- Posture: pattern-only.

Reusable lesson:

- Treat long narrative generation as staged collaboration: plot construction, character development, language pass, synthesis, and evaluation.
- Keep intermediate subtask outputs inspectable before final prose synthesis.
- Benchmark prompts and human stories are evidence for workflow design only; they are not drafting context.

### EQ-bench/Judgemark-v2

- URL: https://github.com/EQ-bench/Judgemark-v2
- Reachable HEAD: `2388448a0401c4d6ed5502ff18953adba944a255`
- License: MIT
- Observed metadata: 28 stars, 5 forks, updated 2026-06-08T01:16:25Z
- Static markers: Judgemark V2.1, creative-writing judge benchmark, numeric literary criteria, Nuanced Characters, Overwrought, Emotionally Engaging, consistency, discriminativeness, ensemble judge scoring.
- Absorbed pattern: `judgemark_literary_criteria_calibration_gate`
- Posture: pattern-only.

Reusable lesson:

- Chapter review should use explicit literary criteria rather than one opaque quality score.
- Judge criteria versions, numeric scores, consistency notes, and accepted/rejected decisions should be persisted with chapter records.
- Benchmark criteria and leaderboard outputs remain evaluator-design references only.

## MuMuAINovel integration

Updated source-discovery surfaces:

- default GitHub queries for Agents' Room / Tell Me A Story and Judgemark-style literary judge discovery
- default repository seeds for both source projects
- static repository summaries with runtime-deferred boundaries
- pattern keyword detection for two new gates
- pattern-pack fields:
  - `agents_room_multistep_story_collaboration_gate_hints`
  - `judgemark_literary_criteria_calibration_gate_hints`
- bible enrichment targets:
  - `multi_step_story_collaboration_policy`
  - `human_prompt_dataset_boundary_policy`
  - `literary_judge_criteria_policy`
  - `judge_consistency_calibration_policy`
- whole-book analysis targets:
  - `agents_room_story_decomposition_report`
  - `specialized_agent_subtask_trace`
  - `human_story_prompt_boundary_findings`
  - `literary_judge_criteria_calibration_report`
  - `judge_consistency_discrimination_findings`
  - `ensemble_judge_score_notes`
- same-type creation remaps:
  - `multi_step_story_collaboration_remap`
  - `literary_judge_criteria_remap`

## Runtime gates

Still blocked unless a separate safety contract exists:

- importing dataset bodies, keys.zip, prompts, generated stories, benchmark outputs, or leaderboard data
- installing Python/Node dependencies
- running benchmark scripts or notebooks
- calling judge/model providers
- using upstream prompts as hidden drafting context
- promoting source story arcs into target canon

## Verification target

The corresponding regression test is:

- `test_agents_room_and_judgemark_sources_are_static_absorbed`

