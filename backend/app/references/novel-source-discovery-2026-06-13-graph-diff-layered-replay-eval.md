# Static intake: graph diff recall, layered audits, possibility replay - 2026-06-13

## Boundary

This intake used public GitHub Search, public `git ls-remote`, and small public
README/LICENSE marker probes.

No upstream repository was cloned, installed, built, executed, imported, indexed,
or used as a runtime dependency. Claude Code plugins, Python scripts, package
hooks, ChromaDB/NetworkX execution, provider calls, prompt bodies, generated
demo fiction, story graph examples, compilers, and narrative journals remain
excluded.

## Sources

### Leolai6-7/write_ai_agent

- URL: https://github.com/Leolai6-7/write_ai_agent
- HEAD: `537f9223ef34a985023eee65dcae47b492bd0d06`
- License: MIT.
- Static markers reviewed: README, LICENSE.
- Posture: pattern-only.
- Absorbed gate: `three_path_graph_diff_recall_gate`.

Reusable pattern:

- Treat every accepted chapter as a source of typed narrative diffs.
- Apply chapter diffs into a story graph before writing the next chapter.
- Assemble continuation context through three paths:
  structured beat/source lookup, graph traversal, and semantic search.
- Track causal chains and foreshadowing threads as graph obligations rather
  than loose prose summaries.

Blocked surface:

- Claude Code plugin runtime, Python scripts, ChromaDB/NetworkX execution,
  semantic indexes, generated YAML diffs, provider calls, and upstream prompt
  bodies.

### giyojisan-glitch/novel-studio

- URL: https://github.com/giyojisan-glitch/novel-studio
- HEAD: `393702e1a0a616b3002962bfc2b5a99561678a75`
- License: MIT.
- Static markers reviewed: README, LICENSE.
- Posture: pattern-only.
- Absorbed gate: `layered_parallel_audit_state_machine_gate`.

Reusable pattern:

- Freeze whole-book skeleton and chapter-outline layers before downstream prose.
- Allow parallel chapter drafting only after shared upstream state is approved.
- Run independent audit heads for logic, pacing, character, and style.
- Feed specific retry hints back to the failed layer instead of regenerating the
  entire book.

Blocked surface:

- Claude Code session workflow, file-dumped prompts, provider handoff, generated
  demos, package scripts, and style-transfer examples.

### derekmerck/storytangl

- URL: https://github.com/derekmerck/storytangl
- HEAD: `b3b4bca36bef43052c3b2652004264918f719df6`
- License: MIT.
- Static markers reviewed: README, LICENSE.
- Posture: pattern-only.
- Absorbed gate: `possibility_graph_dependency_replay_gate`.

Reusable pattern:

- Represent branchable or same-type story design as a possibility graph.
- Check reachability, satisfiability, dependency closure, and role bindings
  before prose is emitted.
- Record traversal cursor, resolved bindings, effects, and journal ids so a
  selected path can be replayed.
- Keep structure, resolution process, and realized narrative separate.

Blocked surface:

- Python package runtime, compilers/loaders, docs examples, scripts, CI, and
  generated narrative journals.

### Deferred / insufficient evidence

- `Anshler/graphify-novel`
  - Search surfaced the repository, but public `git ls-remote` and raw README
    probes returned repository-not-found / 404 during this pass.
  - Deferred until a reachable original source or static artifact packet exists.

## Project changes

- Added seed URLs and GitHub queries for graph-diff recall, layered parallel
  audits, and possibility-graph deterministic replay.
- Added pattern-pack hint fields so拆书、续写、同类型仿写 can use these patterns
  without importing upstream runtime, prompts, or generated prose.
- Added front-end labels so the source discovery panel exposes the new gates.

## Verification commands

```powershell
python -m py_compile backend/app/services/source_discovery_service.py backend/app/services/source_pattern_pack_prompt.py backend/tests/services/test_source_discovery_service.py backend/tests/frontend/test_source_discovery_panel_copy.py
python -m pytest backend/tests/services/test_source_discovery_service.py::test_static_graph_diff_layered_replay_sources_are_absorbed -q
python -m pytest backend/tests/frontend/test_source_discovery_panel_copy.py -q
npm --prefix frontend run build
git diff --check
```
