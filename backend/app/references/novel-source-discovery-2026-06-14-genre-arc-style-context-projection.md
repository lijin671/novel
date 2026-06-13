# Novel source projection: genre / arc / style governance

Date: 2026-06-14

Scope: repo-native projection of already absorbed GitHub pattern-only sources
into MuMuAINovel拆书续写 and同类型仿写 prompt context.

Runtime boundary: no clone, checkout, install, package manager, browser,
provider/model call, vector store, platform scrape, local manuscript import, or
upstream prompt/code execution.

## Source evidence used

- `docs/references/novel-source-discovery-2026-06-12-genre-file-timeline-volume.md`
  - `SteakWrangler/novelcraft-genre-weaver`
  - `3stythe/ai-novel-generator`
- `docs/references/novel-source-discovery-2026-06-12-style-dna-arc-workspace-memory.md`
  - `Zero-AIRI/Ainovr`
  - `tianshiemo7/long-novelist-skill`
- `docs/references/novel-source-discovery-2026-06-10-book-mining-autopilot-longrun.md`
  - `netflypsb/webnovel-mcp`
- `docs/references/novel-source-discovery-2026-06-11-deconstruction-platform-memory-codex.md`
  - `d3nnywong/qidian-mcp-server`
  - `astrapi69/bibliogon`

## Projected gates

- `genre_inspiration_budget_library_gate`
  - Same-type creation now treats genre mix, trope inspiration, target format,
    target length, chapter count, and cost estimate as an abstract option
    matrix.
  - Source inspiration libraries must not become copied premise bundles,
    chapter order, or canon facts.
- `volume_antipattern_dependency_graph_gate`
  - Continuation and同类型仿写 context now names volume plan, chapter rhythm,
    anti-pattern scan, character-arc enforcement, and event dependency graph
    before writer execution.
- `style_dna_breakpoint_hierarchy_gate`
  - Style-DNA analysis, hierarchy generation, review dimensions, repair rounds,
    and breakpoint state stay as review artifacts, not accepted story facts.
- `arc_state_foreshadowing_persistence_gate`
  - Long-form custody now keeps major/minor/micro arcs, character entry/exit
    state, relationship logs, and foreshadowing ledgers visible.
- `webnovel_genre_tracker_gate`
  - Genre-specific trackers for timeline, foreshadowing, LitRPG stats, romance
    stages, cliffhanger rotation, stale characters, and chapter gaps are prompt
    context gates.
- `platform_ranking_research_boundary_gate`
  - Platform ranking/category research can shape reader-promise pressure only.
    It cannot import titles, proprietary tags, source chapter text, or
    platform-specific book details as canon.
- `entity_mention_arc_timeline_gate`
  - Entity mentions, chapter appearances, absence gaps, and unsupported returns
    are now explicit continuity checks.
  - Same-type creation must rebuild appearance rhythm on new entities.

## MuMuAINovel integration

- `book_remix_context_service.py`
  - Adds `Genre, arc, and style governance audit` to continuation and same-type
    inspired context blocks.
  - Expands same-type independence audit with:
    - transferable axes: `genre_promise_matrix`, `trope_option_budget`,
      `style_pressure_axes`
    - required difference axes: `volume_escalation_ladder`,
      `event_dependency_edges`, `arc_id_namespace`, `appearance_rhythm`
    - copy-risk checks: `source_dependency_graph_clone`,
      `style_dna_overfit_review`, `source_arc_state_persistence_leak`
- `test_book_remix_context_service.py`
  - Adds focused coverage for rendered context and independence axes.

## Verification targets

```powershell
python -m pytest backend/tests/services/test_book_remix_context_service.py::test_build_remix_context_blocks_render_genre_arc_style_governance_audit backend/tests/services/test_book_remix_context_service.py::test_build_remix_inspired_independence_audit_expands_genre_arc_difference_axes -q
python -m pytest backend/tests/services/test_book_remix_context_service.py -q
python -m py_compile backend/app/services/book_remix_context_service.py
git diff --check
```
