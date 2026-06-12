# Novel Source Discovery - 2026-06-12 Design Impact / Critic Loop / Quality Benchmark

## Purpose

This note records a static intake pass for fiction-writing sources that strengthen MuMuAINovel around source-study, continuation safety, same-type writing, and revision quality.

No upstream project was cloned deeply, installed, executed, or connected to a provider/runtime.

## Sources

- `osushi-cr/sdcoh`
  - Observed HEAD: `0cbb5206cac068a5092f87d9a227e2cac7c8ca6a`
  - License: MIT
  - Family: story design coherence / dependency impact review
  - Posture: pattern-only; runtime-deferred CLI and file hooks
- `davealaw/FictionRefine`
  - Observed HEAD: `9b3926ff8e57e6b9f9a289c92e0cfd4d5420e020`
  - License: MIT
  - Family: writer/critic iterative story refinement
  - Posture: pattern-only; runtime-deferred model calls and package execution
- `lars76/story-evaluation-llm`
  - Observed HEAD: `0cfd38760e6bf929988c84b0b7ce3e6229d2ee3e`
  - License: MIT
  - Family: creative-writing quality benchmark / story evaluation dataset
  - Posture: pattern-only; no dataset import or training

## Absorbed Patterns

### Story design dependency impact gate

- Track dependencies between character sheets, beat sheets, foreshadowing ledgers, style guides, briefs, and episode drafts.
- When an upstream design file changes, mark downstream drafts or briefs stale until reviewed.
- Treat the author as director; AI drafting cannot silently bypass stale design evidence.

### Writer/critic verify quality-cycle gate

- Use bounded `WRITE -> REVIEW -> REVISE -> VERIFY -> GATE` cycles.
- Keep writer/reviser and critic/verifier outputs separate.
- Store failed cycles, quality thresholds, verification scores, and collapse-risk findings.

### Q15 story-quality benchmark gate

- Convert public benchmark dimensions into local scorecards.
- Track grammar, narrative structure, internal consistency, character consistency, motivation, depth, interaction realism, and satisfying resolution.
- Rank weaknesses before revision so rewrite tasks stay bounded and inspectable.

## Runtime-Deferred Gates

The following remain blocked until a separate local safety contract names scope, files, provider/model, outputs, reviewer, cleanup, and rollback:

- sdcoh CLI install, scan, graph, hooks, or local manuscript mutation.
- FictionRefine package install, LM Studio connection, model calls, example runs, generated story writes, or publish output.
- Story evaluation dataset download, Hugging Face access, training/eval runs, story_text import, or model ranking use as content seed.

## MuMuAINovel Mapping

- `story_design_dependency_impact_gate`
  - Adds stale downstream design review, design-to-episode review queue, and dependency graph remap hints.
- `writer_critic_verify_quality_cycle_gate`
  - Adds bounded writer/critic revision cycles, quality-threshold gates, story-collapse prevention, and verifier-score evidence.
- `q15_story_quality_benchmark_gate`
  - Adds local story-quality scorecards, ranked weakness review, and preferred/rejected pair boundaries.

## Scratch Evidence

Static scratch artifacts were written under:

```text
tmp/source-intake-20260612-next-eval-coherence/
```

The scratch directory contains public search notes, `git ls-remote` HEAD records, and raw README/LICENSE files used for marker review.

## Verification

Expected validation:

```text
python -m py_compile backend/app/services/source_discovery_service.py backend/app/services/source_pattern_pack_prompt.py backend/tests/services/test_source_discovery_service.py backend/tests/frontend/test_source_discovery_panel_copy.py
python -m pytest backend/tests/services/test_source_discovery_service.py::test_design_dependency_writer_critic_quality_sources_are_static_absorbed -q
python -m pytest backend/tests/frontend/test_source_discovery_panel_copy.py -q
python -m pytest backend/tests/services/test_source_discovery_service.py -q
npm --prefix frontend run build
git diff --check
```
