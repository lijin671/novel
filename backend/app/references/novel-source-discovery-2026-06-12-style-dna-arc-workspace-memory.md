# Novel source discovery: style DNA, arc persistence, workspace memory

Date: 2026-06-12
Boundary: public GitHub Search/API + `git ls-remote` + public README/root-marker static review only. No clone, no checkout, no install, no package scripts, no browser/desktop control, no provider call, no uploaded novels, no API keys, no generated manuscript import.

## Sources reviewed

- `Zero-AIRI/Ainovr`
  - URL: https://github.com/Zero-AIRI/Ainovr
  - HEAD: `2d54973987b63e3f5eb39e6a605c952df83f616e`
  - License: not observed via GitHub API
  - Static markers: uploaded reference novels, unified 7-step analysis, event alignment, whole-book memory graph, engineering-reverse DNA, breakpoint recovery, 5-layer hierarchical generation, chapter review, three repair rounds, 34 configurable prompts.
  - Posture: pattern-only.

- `tianshiemo7/long-novelist-skill`
  - URL: https://github.com/tianshiemo7/long-novelist-skill
  - HEAD: `f3a6bdad6d3a6a52d9e432208aada450f5384402`
  - License: MIT
  - Static markers: million-word Chinese webnovel skill, continuation detection, major/minor/micro arc hierarchy, persistent character states, relation logs, forgotten-character checks, JSON foreshadowing ledger, writing-dynamics recovery file.
  - Posture: pattern-only; skill installation remains deferred.

- `Aaron-L945/AI-Novel-Workshop`
  - URL: https://github.com/Aaron-L945/AI-Novel-Workshop
  - HEAD: `9a4b8c76072f1a7b31a527b1597e96acf997c8c9`
  - License: Apache-2.0
  - Static markers: CrewAI director/writer/polisher/checker roles, context retrieval, world/character management, timeline tracking, ChromaDB vector memory, style analysis, consistency checks, Docker and provider-key surfaces.
  - Posture: pattern-only.

- `HenRiser/novel-generator`
  - URL: https://github.com/HenRiser/novel-generator
  - HEAD: `8c9e1270e0eac30de38c8ce28bbf0674d8f7ddc2`
  - License: not observed via GitHub API
  - Static markers: `workspace/books/{book_id}`, versioned outlines/characters/chapters, no-overwrite chapter saves, 100-word summaries, `chapter_index.md`, previous-chapter continuation context, prompt preview without API call, project config and API-key surfaces.
  - Posture: pattern-only.

- `longkuwu/CLwriter`
  - URL: https://github.com/longkuwu/CLwriter
  - HEAD: `0805abc40d7866eb66a311bc51e6f1a1b3465d5c`
  - License: MIT
  - Static markers: epic/viral dual engines, style imitator, logic guard, state tracker, reader sandbox, RAG memory, vectorized settings/characters/plot, rolling summaries, style capsules, Tauri local app surface.
  - Posture: pattern-only.

- `ocyisheng/novel-create-hermes`
  - URL: https://github.com/ocyisheng/novel-create-hermes
  - HEAD: `3665a57a9cdb0b4ba640441bf59122643c43783e`
  - License: not observed via GitHub API
  - Static markers: conversational project/outline/write/quality/style/entity routing, AI-taste quality check, state layer as storage not decision authority, `novel-context.md`, tracking scripts, 10-slot chapter context, style activation.
  - Posture: pattern-only; OpenCode/plugin/global npm surfaces remain deferred.

## Absorbed gates

- `style_dna_breakpoint_hierarchy_gate`: keeps style-DNA analysis, hierarchy generation, review dimensions, repair rounds, and breakpoint state separate from accepted drafting context.
- `arc_state_foreshadowing_persistence_gate`: treats major/minor/micro arcs, character entry/exit state, relation logs, and foreshadowing ledgers as long-run continuation custody.
- `multi_agent_vector_memory_timeline_gate`: requires role-separated agent traces plus timeline/vector-memory evidence before accepting a chapter.
- `versioned_workspace_chapter_index_gate`: preserves chapter versions, summaries, `chapter_index`, project config, and prompt-preview gates.
- `dual_engine_reader_sandbox_rag_gate`: makes epic/viral engine choice, reader-sandbox feedback, style capsules, and rolling RAG summaries explicit review signals.
- `intent_tool_quality_style_checkpoint_gate`: routes chat-like commands through explicit tools while checkpoint state stores context but does not decide canon alone.

## Deferred/runtime gates

Runtime remains blocked for package managers, npm/pip/global installs, shell/PowerShell/batch scripts, Docker/Tauri/Streamlit/Next/OpenCode/CrewAI/ChromaDB startup, uploaded novels, generated outputs, provider/model/API calls, `.env` writes, API-key handling, imported prompt bodies, skill installation, and any external project code execution.
