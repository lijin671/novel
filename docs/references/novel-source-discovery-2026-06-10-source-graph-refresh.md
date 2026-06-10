# Novel Source Discovery - Source Graph Refresh - 2026-06-10

## Scope

Static source-intake refresh for book deconstruction, continuation, and same-type creation graph support in MuMuAINovel.

No external repository was cloned, installed, imported, or executed. Public GitHub metadata, `git ls-remote` HEAD checks, and selected raw README text were used only as static evidence.

## Source snapshot

- `https://github.com/IDSIA/novel2graph`
  - Observed HEAD: `ef014805f1a8bdd10d501e651f69235e64d853a4` on `master`.
  - License: no root `LICENSE` fetched in this pass.
  - Family: literary text to knowledge graph / source-book deconstruction.
  - Posture: pattern-only; runtime-deferred.
  - Reusable pattern: receive a book as input, discover main characters and relations, produce graph material, chapter slices, relation reports, and an inspection interface.

- `https://github.com/Drwei3155/story-graph`
  - Observed HEAD: `3693bf5abeeee339ff051f5fce9d681b028f74d3` on `main`.
  - License: README declares MIT; no separate root `LICENSE` fetched in this pass.
  - Family: Chinese novel relationship graph workbench.
  - Posture: pattern-only; runtime-deferred.
  - Reusable pattern: visual character relationship graph, natural-language graph search, relationship-path explanation, event timeline, multi-book comparison, manual graph edits, statistics, and export surface.

## Absorbed patterns

- Add both repositories to the backend `DEFAULT_GITHUB_REPOSITORY_URLS` registry.
- Add graph-oriented GitHub Search defaults for `novel2graph`, novel-to-graph, character relationship graph, event graph, and natural-language graph search.
- Add static pattern summaries so the discovery ledger can map these sources to:
  - `book_decomposition`
  - `relationship_graph_global_replace_gate`
  - `character_interaction_network_gate`
  - `narrative_event_evolution_graph_gate`
  - `schema_guided_graph_extraction`

## Runtime boundary

The graph projects remain source-intake references only.

Do not run Stanford NLP downloads, Python graph scripts, GUI dashboards, Node/Express servers, package managers, hosted demos, browser session storage flows, provider calls, API keys, or scraping flows during intake.
