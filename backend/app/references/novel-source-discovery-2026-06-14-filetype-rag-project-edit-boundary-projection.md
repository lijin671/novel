# Novel Source Discovery 2026-06-14 — fileType RAG × direct project edit boundary projection

## Sources

### Dialogoi

- Repository: https://github.com/cedretaber/dialogoi
- Static HEAD: `ab188a8912562337168464f3067d091ab6ada051`
- Default branch: `master`
- License: no root license observed / `NOASSERTION`
- Local static README: `tmp/source-intake-dialogoi-readme-20260614.md`
- README SHA256: `98390918E594018DC9501484B9974F979F4609EABBF4D9399E3EC56B3BF8C172`
- Local static package: `tmp/source-intake-dialogoi-package-20260614.json`
- Package SHA256: `BC592D8620EFBF0EC0D46D40929255F6600113D1C213162036345F54F56B404F`
- Intake posture: pattern-only / runtime-deferred

### Scrivener MCP

- Repository: https://github.com/dcondrey/scrivener-mcp
- Static HEAD: `c2ae9ebe30ba9bdd11ebc0036186972d3d767b89`
- Default branch: `main`
- License signal: README/package license marker, with commercial-license surface; treat as runtime-deferred
- Local static README: `tmp/source-intake-scrivener-mcp-readme-20260614.md`
- README SHA256: `32B1F969E960D4905B4ED906528BDBA8E6A71C13392847B24CD579818A70720E`
- Local static package: `tmp/source-intake-scrivener-mcp-package-20260614.json`
- Package SHA256: `617B5067490F22865DC48A3392DDA8E50760A96C7D0A33DE46E9EFA72C572F40`
- Intake posture: pattern-only / runtime-deferred

## Static Evidence

Dialogoi's README/package markers describe an MCP server for novel projects with
`novel.json`, separate settings/content/instruction file classes, regex
full-text search, semantic RAG search, `fileType` filters for `content`,
`settings`, and `both`, Qdrant, multilingual-e5-small, smart chunking, file
watchers, Docker auto-start, npm scripts, and test scripts.

Scrivener MCP's README/package markers describe MCP access to `.scriv` projects:
open/read/edit/analyze/search, binder structure, read/write/create/move/trash,
full-text and semantic search, readability/pacing/style/emotion analysis, RTF
parsing, word counts, persistent character/plot/style memory, npm/npx/Smithery/
Homebrew/Docker installs, setup scripts, postinstall/uninstall hooks, Neo4j,
Redis/BullMQ, OpenAI/LangChain, and optional provider keys.

## Fused Pattern

### `filetype_rag_project_edit_boundary_gate`

When `dialogoi_filetype_rag_novel_project_gate` or
`scrivener_mcp_direct_project_edit_boundary_gate` is active, continuation and
same-type creation need explicit custody before retrieved/project evidence can
influence writing:

```text
filetype_retrieval_scope
hybrid_search_evidence
source_file_class_custody
direct_project_boundary_report
accepted_patch_scope
continuation_or_same_type_boundary
runtime_boundary
```

The gate prevents four failures:

1. mixing settings, instructions, and manuscript chunks into one undifferentiated prompt context
2. treating missing or stale vector indexes as if retrieval is complete
3. allowing direct project bridge diagnostics to mutate canon or manuscripts
4. copying external binder structure, `.scriv` content, RTF text, or source file classes into same-type target canon

## MuMuAINovel Projection

- `book_remix_context_service.py`
  - Adds `filetype_scoped_retrieval_evidence` and
    `hybrid_search_source_file_custody` to continuation control axes for
    Dialogoi-style scoped RAG.
  - Adds `direct_project_edit_boundary_report` to continuation control axes for
    Scrivener-style direct project access.
  - Adds `verify_filetype_retrieval_scope` and
    `verify_direct_project_patch_scope` acceptance steps.
  - Renders continuation and same-type context sections for retrieval scope,
    hybrid search evidence, file-class custody, direct-project boundary reports,
    accepted patch envelopes, independence boundaries, and runtime exclusions.

## Runtime Boundary

Do not run or install upstream runtimes during static intake:

- no MCP launch, npm/npx/package manager, Docker/Qdrant, file watcher, model
  download, vector index build, or test/integration script
- no `.scriv` project open/read/write/edit/analyze/search
- no RTF manuscript read, binder traversal, synopsis/notes mutation, trash/recover action, or import/export
- no postinstall/uninstall hook, setup wizard, Claude Desktop auto-config,
  Neo4j/Redis/BullMQ/OpenAI/LangChain runtime, provider key use, or assistant edit trace
- no copying upstream README examples, prompt-like text, manuscript fragments,
  project structure, or generated analysis into MuMuAINovel canon

The absorbed value is the custody pattern, not upstream code, runtime behavior,
or external manuscript access.
