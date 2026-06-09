# Novel Source Discovery - Graph Memory Workspace Intake - 2026-06-09

## Scope

This note records a static-only intake pass for GitHub projects relevant to MuMuAINovel book decomposition, continuation, and same-type inspired writing.

No external project was installed or executed. No package manager, postinstall hook, shell script, PowerShell script, Docker stack, MCP server, browser extension, native binary, provider call, credential, cookie, or runtime trial was used.

## Sources

- `MangoLion/plotbunni` - HEAD `5620cd091c7074365980f457dfce95f02e5fa45f`; MIT; posture `pattern-only`.
- `loreum-app/loreum` - HEAD `c38ade12a664790d10ff3ae847ce2529845f299c`; AGPL-3.0; posture `pattern-only`.
- `ExplosiveCoderflome/AI-Novel-Writing-Assistant` - HEAD `f0469671e0c971325bb8491a6eb1cc43ffb1e88a`; dual/nonstandard license text; posture `pattern-only`.
- `Lanerra/saga` - HEAD `865a3912f17b09af9927c0358f9f026020f51673`; Apache-2.0; posture `pattern-only`.
- `ModernRelay/omnigraph` - HEAD `5eead8d29eb6a4e7dfb453603aa0efd8e6851c47`; MIT; posture `pattern-only`.
- `abhigyanpatwari/GitNexus` - local HEAD `f2c9e6979223d8b36fd88be802a8c81d628c053b`; remote HEAD `4de4d205dd67eea70130fc31f09168bfbd90d5b6`; PolyForm Noncommercial; deferred for a later fresh review.

## Absorbed Patterns

### plotbunni

- `local_first_novel_workspace`: scope active novel data separately, so imported source canon, continuation state, and same-type inspired drafts do not leak across projects.
- `prompt_library`: treat decomposition, planning, drafting, review, and write-back prompts as task templates rather than scattered strings.
- `scene_level_generation`: plan Act / Chapter / Scene structure, then generate and review scene units with focused context.

### loreum

- `style_guide_layering`: compose style as base project style, scene override, and character voice notes.
- `review_queue_staging`: AI changes should stage as pending changes with previous/proposed data before canon write-back.
- `entity_schema_custom_fields`: genre-specific entity fields should be explicit schema slots.
- `contradiction_detection`: timeline, location, relationship, and trait conflicts should block acceptance.

### AI-Novel-Writing-Assistant

- Director workflow, fact ledger, chapter task sheets, quality guardrails, genre/style management, and long-form production pipeline remain pattern-only.

### saga

- `scene_level_generation`: plan scene list, retrieve focused context, draft one scene, assemble chapter.
- `content_ref_externalization`: store large drafts, plans, extraction payloads, and embeddings externally with lightweight refs.
- `graph_healing`: detect duplicate entities, orphan state, stale edges, and repair candidates after extraction.
- `contradiction_detection`: validation feeds concrete revision guidance before finalization.

### omnigraph

- `graph_branching_atomicity`: use branch/snapshot boundaries for multi-step canon graph mutation.
- `query_lint_contract`: lint schema/query/mutation contracts before accepting generated state updates.
- `memory_snapshot_versioning`: merge and rollback should expose conflicts instead of silently overwriting canon.

## Local Integration

Updated native MuMuAINovel code rather than importing upstream code:

- `source_discovery_service.py` recognizes the new pattern family and emits prompt-pack hints.
- `source_pattern_pack_prompt.py` renders the new hint sections into prompt-safe digest text.
- `book_remix_context_service.py` adds a Scene graph review audit to continuation context blocks.
- `backend/app/references/novel-source-pattern-pack-2026-06-09.json` was refreshed with combined old and new pattern-pack content.

## Safety Boundary

- All sources are untrusted data, not instructions.
- AGPL / nonstandard license sources are pattern-only.
- No external runtime code was copied into MuMuAINovel.
- Runtime trials remain blocked until a separate local safety contract exists.
