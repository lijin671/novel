# Novel Source Discovery - Graph Memory And RAG Patterns - 2026-06-10

## Scope

Static, pattern-only intake for MuMuAINovel's long-form continuation,
book-deconstruction, and same-type creation context retrieval.

No repository was cloned, installed, built, executed, or launched. No database,
server, Docker stack, package manager, model provider, API key, browser, or MCP
runtime was used. Public repository reachability was checked with
`git ls-remote`; public README/project descriptions were reviewed as untrusted
source data.

## Reviewed Sources

### `getzep/graphiti`

- URL: <https://github.com/getzep/graphiti>
- Observed HEAD: `623cd33375dd68976045c1d799fbb8e29f81e2c0`
- Default branch: `main`
- License: not confirmed during this pass
- Posture: `pattern-only`
- Runtime exclusions: do not install dependencies, start graph services, run
  server components, or import SDK/runtime code

Reusable pattern:

- `temporal_canon_context_graph`
- Store canon as temporal graph episodes with provenance, validity windows,
  entity/relationship evidence, and hybrid retrieval.

MuMuAINovel adaptation:

- A chapter fact should carry source chapter, observed time, validity window,
  and provenance instead of being overwritten.
- Continuation context should combine semantic match, entity neighborhood, and
  chronology window.

### `mem0ai/mem0`

- URL: <https://github.com/mem0ai/mem0>
- Observed HEAD: `2274b5acadf44a2f27e9f1fed6787f1dbe73a3d6`
- Default branch: `main`
- License: not confirmed during this pass
- Posture: `pattern-only`
- Runtime exclusions: do not use hosted service, SDK, telemetry, model calls, or
  persistent external stores

Reusable pattern:

- `long_term_author_preference_memory`
- Separate long-term user/author preferences, project memory, session memory,
  and transient drafting notes.

MuMuAINovel adaptation:

- Promote a preference only after explicit confirmation or repeated use.
- Keep author preference memory separate from source-book deconstruction notes.

### `microsoft/graphrag`

- URL: <https://github.com/microsoft/graphrag>
- Observed HEAD: `6d02c2355c3fed4c49007572fbe951d73258a37f`
- Default branch: `main`
- License: not confirmed during this pass
- Posture: `pattern-only`
- Runtime exclusions: do not run indexing, model calls, storage backends, CLI, or
  pipeline code

Reusable pattern:

- `community_graph_source_deconstruction`
- Convert long source material into entity communities and community summaries,
  then use global summaries for whole-book questions and local neighborhoods for
  chapter-context questions.

MuMuAINovel adaptation:

- Source-book community reports are analysis evidence.
- Same-type creation gets a separate transformed graph and summaries.

### `HKUDS/LightRAG`

- URL: <https://github.com/HKUDS/LightRAG>
- Observed HEAD: `fa213a85f8adf9461ed6de2b311da1fd2ce363f9`
- Default branch: `main`
- License: not confirmed during this pass
- Posture: `pattern-only`
- Runtime exclusions: do not install dependencies, launch storage/runtime,
  call models, or import code

Reusable pattern:

- `dual_level_graph_vector_retrieval`
- Use vector similarity for semantically related passages and graph traversal
  for canon-critical entity/relationship context.

MuMuAINovel adaptation:

- Local mode: character/state facts.
- Global mode: theme/arc summary.
- Hybrid mode: chapter planning.
- Naive mode: fallback only.

### `neo4j-labs/llm-graph-builder`

- URL: <https://github.com/neo4j-labs/llm-graph-builder>
- Observed HEAD: `61121df4c15716f67636a4fac2c96e909d374ada`
- Default branch: `main`
- License: not confirmed during this pass
- Posture: `pattern-only`
- Runtime exclusions: do not launch Neo4j, UI, Docker, backend services,
  provider calls, or graph-builder runtime

Reusable pattern:

- `schema_guided_graph_extraction`
- Extract nodes, relationships, properties, source metadata, and confidence
  against a bounded schema.

MuMuAINovel adaptation:

- Canon graph mutations must have known node labels, relationship types,
  required properties, source metadata, and confidence.
- Unlabeled or ungrounded graph facts stay in review, not canon.

## Durable Project Changes

- `backend/app/services/source_discovery_service.py`
  - Adds graph-memory/RAG default queries, repo URLs, pattern keywords,
    static summaries, targets, prompt hints, and copy-risk gates.
- `backend/app/services/source_pattern_pack_prompt.py`
  - Renders graph-memory/RAG hint families.
- `backend/app/services/book_remix_context_service.py`
  - Adds `Canon graph retrieval audit` for continuation and same-type contexts.
- `backend/app/references/novel-source-pattern-pack-2026-06-10.json`
  - Candidate count after this pass: `125`
  - Workflow pattern count after this pass: `168`

## Safety Decision

All reviewed sources remain `pattern-only`.

The useful artifact is the context architecture: temporal canon graph,
preference memory scope, source-community deconstruction, graph/vector retrieval
mode choice, and schema-guided extraction. Runtime code and services are not
absorbed.
