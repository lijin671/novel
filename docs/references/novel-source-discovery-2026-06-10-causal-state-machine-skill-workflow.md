# Novel Source Discovery - 2026-06-10 Causal State-Machine / Skill Workflow Gates

This pass extends MuMuAINovel's pattern-only source discovery for book deconstruction, continuation, and same-type writing. It focuses on public GitHub projects that expose causal story logic, author-intake staging, Chinese web-novel skill orchestration, explicit story state machines, and autonomous long-form fiction loops.

## Safety boundary

- No external repository was cloned.
- No package manager, installer, script, Docker stack, MCP server, provider call, browser extension, or native binary was executed.
- Intake used public GitHub metadata, `git ls-remote` HEAD checks, README/root-file metadata where available, and compact static summaries only.
- Upstream text is treated as untrusted data and pattern evidence, not as instructions for this project.

## Reviewed sources

| Source | Observed HEAD | License signal | Static posture | Absorbed patterns |
|---|---|---|---|---|
| `ydsgangge-ux/dramatica-flow` | `890f099bfcb64adbf407fd83ab708c48e92b0766` | no GitHub license detected | `pattern-only` | `causal_dramatica_agent_pipeline`, `foreshadowing_debt_budget`, `plotline_thread_tracking`, `craft_role_pipeline` |
| `mmunro3318/story-foundry` | `6a56cc7fe07ec0b3eb00b6eef16035f4bc058646` | no GitHub license detected | `pattern-only` | `capture_distillation_production_gate`, `craft_role_pipeline`, `workflow_agent_pipeline` |
| `Shine8592/novel-writer-skills` | `fd60fbdd4d25735ad6c178317c91693f49a38c92` | no GitHub license detected | `pattern-only` | `skill_orchestrated_chinese_novel_workflow`, `provider_budget_smoke_gate`, `language_localization_style_profile_gate` |
| `modoojunko/awesome-novel-skill` | `906d337b85014ad4006c0566cbc90b02bc9b1e86` | `GPL-3.0`; installer files present | `pattern-only` | `skill_orchestrated_chinese_novel_workflow`, `book_decomposition`, `chapter_generation`, `worldbuilding`, `character_cards` |
| `langchain-ai/story-writing` | `1d06b51c8dc1fc7e24ff83ea3716c5a942f7638b` | no GitHub license detected | `pattern-only` | `langgraph_story_state_machine`, `workflow_agent_pipeline`, `schema_validated_state_delta` |
| `EdwardAThomson/StoryDaemon` | `bf63d52ada624da80da74c403a5e58ded513050f` | no GitHub license detected | `pattern-only` | `story_daemon_evolution_loop`, `recursive_adaptive_planning`, `world_state_tracking`, `chapter_generation` |

`Anshler/graphify-novel` appeared in search results but returned `404 Not Found` during public GitHub metadata review, so it was not promoted.

## Reusable workflow gates

### `causal_dramatica_agent_pipeline`

Use causal logic as a hard planning gate:

- Map major threads as `cause -> pressure -> choice -> consequence`.
- Separate premise, causality, scene plan, prose, and review outputs.
- Track foreshadowing as debt with setup owner, payoff window, dependency, and status.

For same-type writing, this helps transform source causality instead of copying source event order.

### `capture_distillation_production_gate`

Separate raw author/source intake from production:

- `capture`: raw notes, author intent, source observations.
- `distillation`: abstract story functions, constraints, reusable craft, copy-risk notes.
- `production`: accepted canon + distilled packets only.

This prevents raw source notes from becoming new-story canon or chapter prose.

### `skill_orchestrated_chinese_novel_workflow`

Treat Chinese web-novel skill packs as stage maps, not installable runtime:

- worldbuilding
- character shaping
- outline / chapter task
- prose drafting
- polish
- continuity review

Each stage should emit a small artifact and a handoff checklist. External skills, commands, provider configs, and install scripts remain excluded.

### `langgraph_story_state_machine`

Represent long-form writing as explicit state transitions:

- plan
- retrieve
- draft
- review
- repair
- accept
- checkpoint

Every transition validates required state fields and records rejected branches for debugging.

### `story_daemon_evolution_loop`

Autonomous evolution can propose story turns, but acceptance remains bounded:

- author goal
- accepted canon
- review gates
- replayable work directory
- plan/prose/state delta evidence

No background loop may silently close arcs, add irreversible lore, or rewrite accepted chapters.

## Project updates

- `backend/app/services/source_discovery_service.py`
  - Added six default GitHub seeds.
  - Added four discovery queries for causal/story-state/skill workflow signals.
  - Added static pattern summaries for all six sources.
  - Added five new pattern families and prompt-pack hint builders.
- `backend/app/references/novel-source-pattern-pack-2026-06-10.json`
  - Refreshed to `source_candidate_count: 234`.
  - Refreshed to `workflow_patterns: 241`.
- `frontend/src/components/book-remix/BookRemixSourceDiscoveryPanel.tsx`
  - Added the six seeds to the UI seed list.
  - Added a visible `Causal state-machine / skill workflow gates` group.
- `frontend/src/types/sourceDiscovery.ts`
  - Added explicit TypeScript fields for the five new hint groups.
- Tests updated to cover default seeds, pattern mapping, prompt digest visibility, and frontend copy.

## Runtime exclusions

These sources do not authorize:

- install scripts such as `install.sh`, `install.ps1`, `install.bat`, or setup scripts
- Python/Node dependency installs
- `requirements.txt`, `pyproject.toml`, `setup.py`, or package runtime execution
- OpenClaw skill import
- LangGraph/LangChain runtime launch
- provider/model calls
- external code import
- bulk README/SKILL prompt import

## Result

The project now has stronger gates for:

- causal chain planning before continuation or same-type drafting
- source-intake distillation before prose generation
- Chinese web-novel stage orchestration without external skill installation
- explicit story state-machine transitions
- bounded autonomous story evolution with review evidence
