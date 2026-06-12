# Novel Source Discovery - Narrative Memory / Canon Graph Refresh (2026-06-12)

## Scope

Static source-intake pass for narrative-memory, story-bible, canon graph,
branching timeline, RAG grounding, and multi-agent long-form fiction patterns.

No repository was cloned, installed, executed, or connected to providers. Public
`git ls-remote --symref`, raw README/LICENSE/root-marker files, and local scratch
manifests under `tmp/source-intake-20260612-narrative-memory-os/` are the only
upstream evidence used.

## Sources Reviewed

- `liwonder/NARRITIVE_OS`
  - URL: <https://github.com/liwonder/NARRITIVE_OS>
  - Observed HEAD: `168af315fcef783f0dbb6100a79406d8daf9392a`
  - Branch: `master`
  - License marker: MIT
  - Posture: `pattern-only`
  - Absorbed gate: `hierarchical_narrative_memory_os_gate`

- `project-89/narrative-canon`
  - URL: <https://github.com/project-89/narrative-canon>
  - Observed HEAD: `bc31bd74480ec903da853a8c973a66e3e960ced5`
  - Branch: `main`
  - License marker: MIT in `package.json`; root LICENSE not fetched in this pass
  - Posture: `pattern-only`
  - Absorbed gate: `narrative_canon_version_branch_graph_gate`

- `dylantneal/ai-author`
  - URL: <https://github.com/dylantneal/ai-author>
  - Observed HEAD: `60e7a6c6943bbbf2ced6ab699daf72a72ecf6302`
  - Branch: `main`
  - License marker: not observed
  - Posture: `pattern-only`
  - Absorbed gate: `planner_writer_evaluator_editor_saga_gate`

- `Shubhj8989/STORY-WEAVER-AI`
  - URL: <https://github.com/Shubhj8989/STORY-WEAVER-AI>
  - Observed HEAD: `5ab593cf4f7f98bcb74df2c4d04a4d1238777ec0`
  - Branch: `main`
  - License marker: not observed
  - Posture: `pattern-only`
  - Absorbed gate: `story_weaver_kg_bible_rag_gate`

- `Binusha123/Taleforge`
  - URL: <https://github.com/Binusha123/Taleforge>
  - Observed HEAD: `7362b99e54977afc05e95d83cdfc88d6d207005d`
  - Branch: `master`
  - License marker: not observed
  - Posture: `pattern-only`
  - Absorbed gate: `taleforge_memory_continuity_research_gate`

- `leeex1/Quillan-Ronin`
  - URL: <https://github.com/leeex1/Quillan-Ronin>
  - Observed HEAD: `e32af4f21fb1eda6629105f1c6aaf4f9d986e2eb`
  - Branch: `main`
  - License marker: Apache-2.0 text observed
  - Posture: `defer / off-lane for this project`
  - Reason: strong provider/runtime/model-hype surface and weak direct
    long-form-fiction evidence. It is retained only as a deferred candidate,
    not promoted into default MuMuAINovel discovery.

## Reusable Patterns

1. **Hierarchical narrative memory OS**
   - Keep Story Bible, append-only canon, vector memory, structured state,
     constraint graph, and world simulation as separate layers.
   - Accepted continuation must validate deltas across layers before write-back.

2. **Narrative canon branch graph**
   - Treat what-if and same-type variants as named branches with parent,
     divergence event, merge target, conflict owner, and paradox decision log.
   - Branches are review artifacts until promoted into accepted canon.

3. **Planner / Writer / Evaluator / Editor saga**
   - Split planning, drafting, critique, and revision into inspectable stages.
   - Provisional memory and graph facts become canon only during finalization.

4. **Story-Weaver KG / Bible / RAG grounding**
   - Continuity checks and story chat should cite story bible, graph edge,
     vector/RAG hit, event timeline, or universe rule.
   - Chat answers remain advisory until accepted into project canon.

5. **TaleForge memory / continuity / research lane split**
   - Living bible, continuity guardian, research assistant, and long-term memory
     should have separate provenance and promotion lanes.
   - Research notes improve realism only after source review; they do not become
     story facts by default.

## Runtime Deferred

The following remain blocked in this intake pass:

- package managers, installs, postinstall hooks, shell scripts, npm/pnpm/turbo
- provider calls, API keys, model downloads, local/vector DB startup
- backend/frontend servers, dashboards, CLI tools, Docker, MongoDB, ChromaDB
- importing generated stories, example corpora, prompt bodies, or upstream code

## MuMuAINovel Integration

Updated source-discovery pattern gates add:

- `hierarchical_narrative_memory_os_gate`
- `narrative_canon_version_branch_graph_gate`
- `planner_writer_evaluator_editor_saga_gate`
- `story_weaver_kg_bible_rag_gate`
- `taleforge_memory_continuity_research_gate`

These feed bible enrichment, whole-book analysis, continuation prompt hints,
inspired-creation remap targets, transformation hints, and copy-risk rejection
rules.
