# Novel Source Discovery - 2026-06-11 Counterfactual Graph-RAG Pass

## Scope

Static source-intake pass for projects that improve book deconstruction,
continuation, and same-type / What-if rewriting through story graphs and hybrid
retrieval.

No upstream project was cloned as a checkout, installed, executed, started, or
connected to providers. Review used public GitHub metadata, `git ls-remote`,
root tree metadata, README / LICENSE markers, and isolated scratch files under
`tmp/source-intake-20260611-graphrag-counterfactual-deconstruction/`.

## Sources

### `mert-ozdemirr/sherlock-counterfactual-modular-graph-rag`

- URL: <https://github.com/mert-ozdemirr/sherlock-counterfactual-modular-graph-rag>
- Observed HEAD: `9b6e98c4275a5a1fb4481a1955357b1cebcb8876`
- Default branch: `main`
- Stars / forks at review: 0 / 0
- License marker: no GitHub license detected; no root LICENSE observed
- Root markers: `.gitignore`, `.python-version`, `README.md`, `pyproject.toml`,
  `scripts`, `uv.lock`
- Posture: `pattern-only`

Reusable pattern:

- Source prose can first become atomic propositions rather than direct prompt
  text.
- Narrative chunks should be scene / reasoning aligned, not only fixed-size
  text chunks.
- Event graphs need to distinguish story presentation order from inferred
  realtime order.
- Counterfactual generation should start from a verified graph slice: anchor
  event, neighboring entities, evidence ids, and explicit causal links.
- Alternative storylines need a divergence card before drafting.

Runtime exclusions:

- No Python / uv runtime, scripts, Neo4j, provider calls, Sherlock text
  processing, or generated alternative storyline execution.

### `SutraMind/GraphRAG-story`

- URL: <https://github.com/SutraMind/GraphRAG-story>
- Observed HEAD: `2c470393e57c7aee68f7b6fae1afcd74e78059f5`
- Default branch: `master`
- Stars / forks at review: 0 / 0
- License marker: no GitHub license detected; no root LICENSE observed
- Root markers: `README.md`, `app`, `config`, `pipeline`, `rag`,
  `requirements.txt`
- Posture: `pattern-only`

Reusable pattern:

- Parse source stories into stable chapter / paragraph ids before graph or
  vector indexing.
- Extract entities and relationships into a graph, but keep vector retrieval for
  narrative questions.
- Route each query explicitly as graph, vector, or hybrid before assembling
  continuation context.
- Validate processed chapter counts and relationship counts before trusting the
  retrieval layer.

Runtime exclusions:

- No requirements install, Neo4j, FastAPI, scripts, embeddings, test queries, or
  model/provider calls.

## Deferred overlap signals

`BillChen-29/novel-base` and `njacknot/novelist-skill` were visible through
public metadata / raw README probes. They remain overlap signals for Chinese
novel skill packs rather than new code-fusion inputs in this pass because the
current project already has skill-orchestrated Chinese novel workflow gates,
Fanqie audit gates, and source-study isolation gates.

## Fusion into MuMuAINovel

Added source-discovery support for:

- `counterfactual_story_graph_rag_gate`
- default GitHub query for counterfactual / alternative storyline Graph-RAG
- default seeds for Sherlock counterfactual Graph-RAG and GraphRAG-story
- static pattern overrides for both sources
- pattern-pack bible targets:
  - `counterfactual_divergence_policy`
  - `verified_story_graph_context_policy`
- pattern-pack whole-book targets:
  - `counterfactual_divergence_points`
  - `narrative_vs_realtime_event_edges`
  - `verified_graph_retrieval_context`
- same-type remap target:
  - `counterfactual_graph_remap`
- prompt, copy-risk, digest, type, and UI hint surfaces

Design rule:

Same-type or What-if continuation may use source graphs as evidence maps, not as
plot rails. A draft must declare the divergence point, preserved invariants,
changed assumption, invalidated causal links, and new-story state deltas before
it can be promoted.
