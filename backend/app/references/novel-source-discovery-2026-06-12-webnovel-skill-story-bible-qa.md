# Novel Source Discovery - Webnovel Skill and Story Bible QA Gates (2026-06-12)

## Scope

Static source intake for MuMuAINovel book deconstruction, continuation, same-type creation, and local continuity review.
No dependency install, script execution, Claude Code plugin install, provider call, browser launch, local manuscript import, package hook, or user data access was performed.
A shallow static clone was used only under `tmp/source-intake-2026-06-12-webnovel-skill-qa/repos` for README/tree inspection after GitHub API rate limiting.

## Sources

### Beat1ngHeart/novel-writing-toolkit

- URL: https://github.com/Beat1ngHeart/novel-writing-toolkit
- Reachable HEAD: `3cb764c17dbec6548cc1ccc9454db194b7de981a`
- License: not observed
- Static markers: Claude Code custom commands, `/novel`, `/novel-plan`, `/novel-topic`, seven writing laws, anti-AI trace cleanup, platform adaptation, topic/ranking score tables, data closed loop.
- Absorbed pattern: `seven_law_platform_closed_loop_gate`
- Posture: pattern-only.

Reusable lesson:

- Turn prose quality into explicit acceptance gates rather than one vague polish prompt.
- Track platform-fit and reader-follow assumptions as review metadata.
- Keep command prompt bodies and upstream examples outside MuMuAINovel drafting context.

### TulanCN/vibe-noveling

- URL: https://github.com/TulanCN/vibe-noveling
- Reachable HEAD: `b7987517d869d50735891cb0341437c24f9e35fe`
- License: MIT
- Static markers: Chinese web-novel workflow, 13 Skills, 4 Agents, Save the Cat 15 beats, `/novel-discuss`, `/novel-bookplan`, `booming`, `fuck-it`, `consistency-guard`, `/novel-sync`, snapshots, progress tracking, knowledge graph synchronization.
- Absorbed pattern: `vibe_noveling_skill_agent_save_cat_gate`
- Posture: pattern-only.

Reusable lesson:

- Separate book / volume / chapter planning with explicit beat intent.
- Keep skill contracts, agent roles, consistency checks, snapshots, progress, and graph sync as separate handoff records.
- Knowledge graph sync should happen after author acceptance, not as a hidden drafting side effect.

### sadasdfsaf/story-bible-qa

- URL: https://github.com/sadasdfsaf/story-bible-qa
- Reachable HEAD: `66d8876b3bf2d09e8ff55a21a3dc6dbe88e57aab`
- License: not observed
- Static markers: Story Bible QA, local-first continuity console, long-form fiction, Story Bible / POV / location / lore-rule review, React + TypeScript + Vite UI.
- Absorbed pattern: `story_bible_qa_pov_lore_rule_gate`
- Posture: pattern-only.

Reusable lesson:

- Continuity QA should check POV holder, location state, and lore-rule applicability before generation.
- QA findings need source field, target scene id, severity, proposed fix, and mutation boundary.
- UI continuity consoles are review surfaces only unless a separate runtime safety contract exists.

## MuMuAINovel integration

Updated source-discovery surfaces:

- default GitHub queries for seven-law prose gates, Vibe Noveling-style skill-agent planning, and Story Bible QA continuity review
- default repository seeds for the three sources
- static repository summaries with runtime-deferred boundaries
- pattern keyword detection for three gates
- pattern-pack fields:
  - `seven_law_platform_closed_loop_gate_hints`
  - `vibe_noveling_skill_agent_save_cat_gate_hints`
  - `story_bible_qa_pov_lore_rule_gate_hints`
- bible enrichment targets:
  - `seven_law_prose_policy`
  - `platform_feedback_closed_loop_policy`
  - `save_the_cat_multilevel_planning_policy`
  - `skill_agent_role_boundary_policy`
  - `story_bible_pov_location_lore_rule_policy`
  - `local_continuity_qa_console_policy`
- whole-book analysis targets:
  - `seven_law_prose_audit_report`
  - `platform_topic_score_findings`
  - `anti_ai_trace_revision_log`
  - `save_the_cat_beat_alignment_report`
  - `skill_agent_handoff_trace`
  - `knowledge_graph_sync_readiness_findings`
  - `story_bible_qa_report`
  - `pov_location_lore_rule_findings`
  - `continuity_console_review_trace`
- same-type creation remaps:
  - `platform_feedback_law_remap`
  - `save_the_cat_skill_agent_remap`
  - `pov_location_lore_rule_remap`

## Runtime gates

Still blocked unless a separate safety contract exists:

- Claude Code plugin/skill install or command execution
- importing upstream prompt bodies, command files, agent prompts, or examples
- npm install/build/test, package hooks, browser launch, or UI runtime
- reading local manuscripts, story bible data, browser storage, or provider credentials
- writing knowledge graph updates before author acceptance

## Verification target

The corresponding regression test is:

- `test_webnovel_skill_and_story_bible_qa_sources_are_static_absorbed`

