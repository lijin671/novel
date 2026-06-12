# Novel Source Discovery - Context Recovery, Plot Corpus, and Relic Vault Gates (2026-06-12)

## Scope

Static source intake for MuMuAINovel long-form writing reliability, book deconstruction, continuation, and same-type creation safety.
No dependency install, provider call, script execution, dataset download, Wikipedia dump processing, Claude plugin install, memory database launch, local vault access, or generated-project execution was performed.
Static review used public `git ls-remote` and shallow scratch clones under `tmp/source-intake-2026-06-12-graph-memory-writing/repos`.

## Sources

### Doriandarko/gemini-writer

- URL: https://github.com/Doriandarko/gemini-writer
- Reachable HEAD: `5a37741948f081451d02468a2d4c67cfed55e8a9`
- License marker: MIT License with Attribution Requirement
- Static markers: Gemini Writing Agent, novels/books/short-story collections, smart context management, recovery mode, saved context summaries, token monitoring, automatic context compression, project/file tools, provider API-key setup.
- Absorbed pattern: `gemini_writer_context_recovery_gate`
- Posture: pattern-only.

Reusable lesson:

- Long autonomous writing needs explicit token-budget checkpoints and inspectable context summaries.
- Recovery should resume from named summaries and accepted state, not from hidden provider traces.
- Tool/file writes must remain separately authorized and auditable.

### markriedl/WikiPlots

- URL: https://github.com/markriedl/WikiPlots
- Reachable HEAD: `22d975c92e1ac835a412ac001d95fb86d3d37960`
- License marker: not observed
- Static markers: 112,936 story plots, English Wikipedia plot summaries, plots.zip, one sentence per line, `<EOS>` separator, title list, Wikipedia dump extraction, WikiExtractor, BeautifulSoup.
- Absorbed pattern: `wikiplots_plot_corpus_boundary_gate`
- Posture: pattern-only.

Reusable lesson:

- Plot corpora are useful for abstracting plot-shape and causal transition patterns.
- Source plot rows, titles, and sentence order must stay out of MuMuAINovel canon and drafting context.
- Same-type writing needs an explicit plot-corpus leakage review.

### the-essential/reliquery

- URL: https://github.com/the-essential/reliquery
- Reachable HEAD: `3fb6275c9a44c4859b900ef2ab5de52bb2c7d924`
- License marker: MIT
- Static markers: persistent AI memory for writers, reconstructive recall, structured markdown relics, semantic vault search, Chronicle, Memorize, Cartograph, Forget, Study, MemPalace, ChromaDB, SQLite temporal knowledge graph, relationship mapping.
- Absorbed pattern: `reliquery_reconstructive_recall_vault_gate`
- Posture: pattern-only.

Reusable lesson:

- Long-term memory should be query-driven over reviewed relics, not bulk prompt stuffing.
- Intake, indexing, relationship mapping, deletion, and study pipelines are separate writeback stages.
- Deleted or unapproved memory cannot silently re-enter continuation context.

## MuMuAINovel integration

Updated source-discovery surfaces:

- default GitHub queries for context recovery, plot-corpus boundaries, and reconstructive recall vaults
- default repository seeds for all three sources
- static repository summaries with runtime-deferred boundaries
- pattern keyword detection for three gates
- pattern-pack fields:
  - `gemini_writer_context_recovery_gate_hints`
  - `wikiplots_plot_corpus_boundary_gate_hints`
  - `reliquery_reconstructive_recall_vault_gate_hints`
- bible enrichment targets:
  - `context_recovery_summary_policy`
  - `token_budget_compression_policy`
  - `plot_corpus_boundary_policy`
  - `source_plot_import_exclusion_policy`
  - `reconstructive_recall_vault_policy`
  - `relic_memory_writeback_policy`
- whole-book analysis targets:
  - `context_recovery_summary_report`
  - `token_compression_checkpoint_trace`
  - `interrupted_work_resume_findings`
  - `plot_corpus_boundary_report`
  - `plot_summary_abstraction_findings`
  - `source_plot_leakage_review`
  - `reconstructive_recall_query_report`
  - `relic_vault_index_review`
  - `memory_graph_writeback_findings`
- same-type creation remaps:
  - `context_recovery_checkpoint_remap`
  - `plot_corpus_abstraction_remap`
  - `relic_vault_recall_remap`

## Runtime gates

Still blocked unless a separate safety contract exists:

- uv/pip/npm install, scripts, provider calls, API keys, generated project runs, or file tools
- dataset download, plot text import, Wikipedia dump processing, extractor execution, or dependency install
- Claude plugin install, skill execution, MemPalace/ChromaDB/SQLite launch, local vault reads, memory writes, or relationship graph mutation
- copying source plot sentences, titles, prompt bodies, vault snippets, or generated examples into MuMuAINovel canon

## Verification target

The corresponding regression test is:

- `test_context_recovery_plot_corpus_and_relic_vault_sources_are_static_absorbed`

