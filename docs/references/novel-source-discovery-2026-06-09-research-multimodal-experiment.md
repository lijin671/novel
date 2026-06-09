# Novel source discovery — research taxonomy, multimodal, and experiment patterns (2026-06-09)

## Scope

This intake extends MuMuAINovel's拆书续写、同类型仿写、长篇一致性和审稿能力 with public GitHub projects that are useful as patterns, not as runtime dependencies.

No project was cloned, installed, executed, or connected to a provider. Evidence is limited to public metadata, README/root-file observations, and `git ls-remote --symref ... HEAD`.

## Source snapshot

- `Picrew/awesome-llm-story-generation`
  - HEAD `46f0d41e75a25a7d8b937daaa255ef4999446f38`, branch `main`.
  - Public README describes 232 verified story/novel/script generation entries across 10 categories.
  - Posture: `index-only`.
  - Absorbed pattern: `research_taxonomy_story_map`.

- `Anning01/novelvids`
  - HEAD `5174e19f8131125b01d380a8c59e8d23a63c0f39`, branch `main`.
  - Public README describes an AI-driven novel-to-short-drama production platform.
  - Root files include `pyproject.toml`, `main.py`, `api/`, `services/`, `prompts/`, `web/`.
  - Posture: `pattern-only`; external API/video runtime surface is not executed.
  - Absorbed patterns: `novel_to_multimodal_pipeline`, `entity_to_visual_asset_pipeline`.

- `MemeCalculate/moyin-creator`
  - HEAD `8836dd9a9fdd74fa63a92843c10a93c9f2f85c9a`, branch `main`.
  - Public README describes an AI film-production chain from script to characters, scenes, director decisions, and final video.
  - License: AGPL-3.0. Root files include Electron/package surfaces.
  - Posture: `pattern-only`; Electron, postinstall, desktop runtime, and media generation are not executed.
  - Absorbed patterns: `novel_to_multimodal_pipeline`, `entity_to_visual_asset_pipeline`.

- `jncchds/abook`
  - HEAD `dbcec4370af39f9e25bce407df783a0cfdd82e57`, branch `main`.
  - Public README describes seven agents: Story Bible, Characters, Plot Threads, Chapter Outlines, Writer, Editor, Continuity Checker.
  - It also describes RAG context retrieval, full synopsis spine, anti-repetition rules, token stats, and export surfaces.
  - Root includes Docker/MCP-related surfaces, so runtime use is out of scope.
  - Posture: `pattern-only`.
  - Absorbed patterns: `agentic_book_planner_pipeline`, `rag_synopsis_spine`, `anti_repetition_prompt_rules`.

- `Prompt-And-Circumstance/StoryMode`
  - HEAD `90d6877dcdae9c42cb68b9ecc3bcffd89f8b4b0d`, branch `main`.
  - Public README describes 43 genres, story style, author style, mix-and-match settings, narrative arc, and scenario blueprint schema.
  - SillyTavern extension/browser runtime surface is not executed.
  - Posture: `pattern-only`.
  - Absorbed pattern: `narrative_arc_template_control`.

- `brianlmerritt/explore_writing`
  - HEAD `2062eaba34c19804884e6bddb074086fc2aa8d1f`, branch `main`.
  - Public README describes prompt recipes, sampling/temperature grids, write/review/top_writing phases, rubric review, and append-only resumable TSV logs.
  - License: MIT. Root includes `requirements.txt`.
  - Posture: `pattern-only`.
  - Absorbed patterns: `prompt_recipe_experiment_grid`, `append_only_generation_review_log`, `sampling_parameter_quality_sweep`.

- `forsonny/novel-master-ai`
  - HEAD `144d3d2b2c890bb96fcf71c03bf83abc4e8341a9`, branch `main`.
  - Public README describes an NRD workflow from arcs to chapters to scenes, tagged steps, revision passes, and continuity reporting.
  - CLI/MCP/runtime surfaces are not executed.
  - Posture: `pattern-only`.
  - Absorbed pattern: `nrd_task_tree_pipeline`.

- `arian-emami/NovelDreamer`
  - HEAD `100042945f0f34f5f32c47e476f20b69d1177bbc`, branch `main`.
  - Public README describes RAG from Wikiquote style/thematic samples, Hero's Journey, Freytag structure, and act/chapter pre-planning.
  - License: MIT. Root includes `requirements.txt`.
  - Posture: `pattern-only`.
  - Absorbed pattern: `story_structure_rag_planning`.

## Fusion into MuMuAINovel

- Discovery now searches for research taxonomy, continuity-checker agents, narrative arc templates, prompt experiments, story-structure RAG, novel-to-video, and NRD/task-tree projects.
- The static pattern pack now recognizes 12 new workflow patterns.
- Continuation guidance now includes:
  - method taxonomy coverage checks;
  - separate planner roles for Story Bible, Characters, Plot Threads, Chapter Outlines, Writer, Editor, and Continuity Checker;
  - a full synopsis spine for RAG retrieval;
  - anti-repetition rules before acceptance;
  - NRD-style arcs → chapters → scenes → revision passes;
  - structure-RAG scaffolds that must map to accepted facts before prose.
- Same-type creation guidance now remaps narrative arc, synopsis spine, multimodal pipeline, visual assets, prompt recipes, NRD task tree, sampling quality, and structure scaffolds while rejecting source-specific facts, names, event order, and set pieces.
- Prompt digest rendering and continuation context now expose `Research, multimodal, and experiment audit:` gates.

## Safety boundary

- `awesome-llm-story-generation` is index-only. Do not load the whole catalog into runtime context.
- `novelvids`, `moyin-creator`, `StoryMode`, and `novel-master-ai` have high-trust runtime surfaces. Do not install, run, launch extensions, start MCP servers, call providers, or execute scripts from them during source intake.
- Media/storyboard outputs are derived artifacts. They must not mutate novel canon unless a separate accepted script/scene change package says so.

## Local artifacts updated

- `backend/app/services/source_discovery_service.py`
- `backend/app/services/source_pattern_pack_prompt.py`
- `backend/app/services/book_remix_context_service.py`
- `backend/app/references/novel-source-pattern-pack-2026-06-09.json`
- `backend/tests/services/test_source_discovery_service.py`
- `backend/tests/services/test_book_remix_context_service.py`

Generated pack after this intake:

```text
source_candidate_count: 58
workflow_pattern_count: 105
```
