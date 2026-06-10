# Novel source discovery - CharacterArc skill loop and knowledge trace

Date: 2026-06-11

## Source

- Repository: `uu201/character-arc`
- URL: <https://github.com/uu201/character-arc>
- Observed HEAD: `4fb9f3fd8cd8bb2f9bd4b383ef62b1976ca0ca87`
- Default branch: `main`
- License: MIT
- Stars at static review: 241
- Posture: `pattern-only`

Static review only. No clone checkout, install, package-manager command,
Electron launch, provider call, embedding call, desktop runtime, or API-key
inspection was performed.

## Static evidence

- GitHub metadata and `git ls-remote` confirmed the public HEAD above.
- Public README describes a desktop novel workbench with:
  - local SQLite project isolation
  - project settings, relationship graph, outline timeline, and chapter editor
  - knowledge center for facts, flow documents, references, and style analysis
  - built-in and project-level Skill packages
  - Agent Loop mode and task progress panel
  - chapter versions, rollback, `.txt` / `.docx` export, and JSON workspace snapshot
- Selected static files under `electron/main/ai/**` show:
  - task handlers for chapter first draft, chapter analysis, reference deep analysis,
    and style fingerprint extraction
  - `skill_load`, skill index/tool registry use, and capped Agent Loop behavior
  - `knowledge_save_document` writeback for deconstruction/style output
  - run meta with task, chapter id, provider/model, status, usage,
    `usedKnowledge`, and `usedSkills`
  - prompt/response/selection logs as AI run evidence
- `electron/main/archive/project-archive.ts` static review shows project archive
  modules for chapters, chapter versions, knowledge documents, reference works,
  and reference assets.

## Absorbed patterns

### `project_skill_agent_loop_gate`

Use task-scoped skills as a visible method router:

- record task name, required capabilities, selected built-in/project skills,
  max loop steps, tool registry, retry count, and stop reason
- keep Skill bodies as method inputs, not canon state
- require downstream chapter, knowledge, or review artifacts to prove what changed

### `knowledge_document_writeback_trace_gate`

Use typed knowledge documents as the bridge between deconstruction and drafting:

- classify documents by source type such as `reference-summary`,
  `reference-chunk`, `workflow-document`, `canon-fact`, and `chapter-summary`
- keep produced knowledge documents as drafts until reviewed or merged
- trace each generation run to task, chapter id, provider/model, usage,
  `usedKnowledge`, `usedSkills`, status, and produced document ids

## Runtime boundaries

- Electron/Vue desktop runtime is not launched.
- `pnpm`, build scripts, package hooks, and installers are not run.
- Provider, embedding, API-key, model, image-generation, and desktop surfaces are
  treated as runtime-deferred.
- The source contributes only task-skill routing, knowledge writeback, and AI
  traceability gates.

## Integration targets

- `backend/app/services/source_discovery_service.py`
  - default search query and default repository seed
  - static pattern override for `uu201/character-arc`
  - `project_skill_agent_loop_gate`
  - `knowledge_document_writeback_trace_gate`
- `backend/app/services/source_pattern_pack_prompt.py`
  - pattern-pack digest keys for the two gates
- `frontend/src/types/sourceDiscovery.ts`
  - new pattern-pack hint fields
- `frontend/src/components/book-remix/BookRemixSourceDiscoveryPanel.tsx`
  - pinned display under Source deconstruction / memory glossary gates
