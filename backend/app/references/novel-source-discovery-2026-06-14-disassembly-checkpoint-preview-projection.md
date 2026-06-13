# Novel source discovery - 2026-06-14 disassembly checkpoint preview projection

## Source

- GitHub: `novel-writer-pro/novel_disassembly_agent_mini`
- Public HEAD: `83d3f8c5da09cd1461f38ddfe77028233e3d4b0e`
- Default HEAD ref: `refs/heads/v0.1.1`
- License: no root `LICENSE` observed from raw probe
- Intake posture: `pattern-only`

## Static evidence used

Bounded public probes only:

- `git ls-remote --symref https://github.com/novel-writer-pro/novel_disassembly_agent_mini.git HEAD`
- raw `README.md` from `v0.1.1`
- raw `pyproject.toml` from `v0.1.1`

No clone, checkout, install, package manager, PostgreSQL, Alembic, LangGraph,
SkillKit, embedding, API/web app, provider call, local corpus, prompt body, or
generated analysis was executed or imported.

## Reusable pattern

The durable pattern is not its runtime. The reusable part is a source-book
analysis gate:

- chapter-progressive import/normalization
- chapter job/checkpoint ledger
- raw output separate from accepted analysis
- JSON-first analysis before Markdown/export
- QA context with chapter citation/jump evidence
- missing coverage blocks full-scope continuation

## MuMuAINovel projection

This pass projects the pattern into the actual continuation context preview:

- `source_chapter_analysis_coverage`
- `disassembly_checkpoint_ledger`
- `qa_citation_jump_trace`
- `source_analysis_coverage_percent`
- `missing_source_analysis_chapters`
- `disassembly_checkpoint_warnings`

The continuation context block now renders a dedicated
`Chapter-progressive disassembly checkpoint audit` section when
`chapter_progressive_disassembly_checkpoint_gate` is active.

## Safety boundary

Runtime remains blocked for clone, checkout, install, package manager,
PostgreSQL/Alembic, app launch, SkillKit/LangGraph runtime, embedding/model
runtime, provider API calls, local novel/corpus reads, prompt body import,
secret reads, host/model config mutation, and remote push.
