# Novel source discovery: RAG technique / agent architecture catalogs (2026-06-13)

## Scope

Static source-intake only. No clone, install, notebook execution, provider call,
MCP/server launch, embedding build, dataset import, or prompt/code transplant was
performed.

## Sources

- `NirDiamant/RAG_Techniques`
  - URL: `https://github.com/NirDiamant/RAG_Techniques`
  - Observed HEAD: `7a1cdc390f0bb0556ba582c81b95e5079ae4fb37`
  - README snapshot: `sha256:26e45efe58ce7cf5b6ceecfb251e490f5fe3421f7a28d1540fd099262764ea65`
  - LICENSE snapshot: `sha256:c9877e4d8788a0bb97502348dca8fbd78a6eaa73db0638221b3cb67422d30177`
  - License posture: custom non-commercial. Pattern-only; no code or notebook import.
  - Static markers: Advanced RAG Techniques, proposition chunking,
    contextual chunk headers, semantic chunking, HyDE, query transformations,
    reranking, hierarchical indices, feedback loop, adaptive retrieval,
    GraphRAG, RAPTOR, Self-RAG, CRAG, and evaluation.

- `NirDiamant/GenAI_Agents`
  - URL: `https://github.com/NirDiamant/GenAI_Agents`
  - Observed HEAD: `e28102e913b8fea62ef357459f398a50be512819`
  - README snapshot: `sha256:394865d029e30e326592050b99ed8d4005fddc60a4f11f9b450bf15b5e339fb2`
  - LICENSE snapshot: `sha256:c9877e4d8788a0bb97502348dca8fbd78a6eaa73db0638221b3cb67422d30177`
  - License posture: custom non-commercial. Pattern-only; no code, notebook,
    prompt, or MCP config import.
  - Static markers: GenAI agent implementations, LangGraph, MCP,
    memory-enhanced conversational agents, multi-agent collaboration,
    self-improving agents, task-oriented agents, creative/content generation
    agents, and murder-mystery procedural story-generation examples.

## Absorbed gates

- `rag_technique_catalog_context_retrieval_gate`
  - Convert generic RAG techniques into explicit MuMuAINovel retrieval recipes.
  - Every recipe should declare chunking mode, query transform, reranker,
    graph/vector scope, source layer, and evaluation verdict.
  - Useful for拆书续写 because context selection must distinguish accepted
    chapters, story bible facts, summaries, style notes, relationship graph, and
    research notes.

- `agent_architecture_catalog_workflow_gate`
  - Convert agent tutorial catalogs into workflow-template inventory.
  - Every template should declare state schema, memory contract, tool/MCP
    boundary, evaluator, retry rule, and rollback artifact.
  - Useful for same-type writing because planner/reviewer/memory/collaboration
    roles can be reused as abstract duties without copying tutorial prompts or
    story examples.

## Runtime-deferred boundaries

- No upstream notebook cells, tutorial code, prompt bodies, generated examples,
  diagrams, datasets, embeddings, MCP configs, server scripts, provider snippets,
  package manifests, or non-commercial licensed content are imported.
- Runtime use would require a separate local safety contract covering source
  revision, license/provenance, selected behavior, project/corpus authority,
  provider/tool/MCP boundary, output custody, cleanup, rollback, and verifier.

## Project integration

- Added default GitHub discovery queries and seed URLs.
- Added source pattern overrides for both repositories.
- Added pattern-pack hints for:
  - retrieval recipe selection and evaluation,
  - agent workflow templates,
  - continuation state persistence,
  - inspired remap guidance,
  - copy-risk rejection.
- Added backend and frontend tests covering the new gates.
