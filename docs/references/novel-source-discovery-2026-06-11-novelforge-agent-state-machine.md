# Novel source discovery - NovelForge Agent state-machine gates

Date: 2026-06-11

## Source

- Repository: `zlx362211854/novelforge-agent`
- URL: <https://github.com/zlx362211854/novelforge-agent>
- Observed HEAD: `84a212caca43ff01056d4df565b8c6827ddbb600`
- Default branch: `main`
- License: MIT
- Stars at static review: 1
- Posture: `pattern-only`
- Static cache: `tmp/source-intake-20260611-zlx362211854-novelforge-agent/`

Static review only. No clone checkout, `npx`, `npm install`, build, package
script, MCP server launch, host config edit, provider/model call, credential
read, or generated project runtime was performed.

## Static evidence

- Public GitHub metadata and `git ls-remote --symref` confirmed the HEAD above.
- Root tree contains `README.md`, `README.zh-CN.md`, `LICENSE`, `package.json`,
  `src/core/**`, `src/mcp/**`, `src/cli/**`, templates, fixtures, and tests.
- Public README describes a local-first long-form fiction engine where the host
  model writes artifacts while the workflow runtime manages step order,
  expected format, validation, persistence, retrieval, revision archives, and
  project-local audit logs.
- `package.json` exposes MCP/CLI binaries and package scripts including build,
  tests, inspector commands, and `prepare`; these stay runtime-deferred.
- Selected static files show:
  - `modelHint` tiers and prompt `segments` for host-side routing/cache hints
  - step contexts for chapter generation, review, revision, memory extraction,
    continuity review, cross-chapter review, and architecture extension
  - zod schemas for metadata, style guide, architecture, memory cards,
    chapter review, continuity review, and cross-chapter review
  - mandatory `chapter_review` before memory writeback
  - `chapter_revision` loops with `revisionCounts` and `forceAdvanced` markers
  - failed submissions saved under `.agent-recovery/failed-*`
  - CJK-aware lexical/BM25 retrieval over chapters, bible sections, and memory
    cards without requiring embeddings or provider calls
  - audit events that summarize long or sensitive fields by length and SHA-256

## Absorbed patterns

### `host_instruction_context_boundary_gate`

Use a runtime boundary where the project prepares the exact instruction,
expected format, model tier hint, prompt segments, and packed context, but the
host LLM performs generation. This keeps provider/model routing out of canon
and makes context selection inspectable before drafting.

### `schema_review_revision_recovery_gate`

Require generated artifacts to pass schema validation before workflow state
advances. A chapter only reaches memory/canon after a clean review; failed
reviews route to a bounded revision loop, and bad submissions remain recovery
evidence rather than invisible failed attempts.

### `cjk_bm25_context_retrieval_gate`

Use local lexical retrieval for Chinese long-form continuation before optional
embedding/provider surfaces. The context pack should record query, tokenizer,
chapter range, document types, hit ids, scores, and inclusion reasons.

### `dynamic_architecture_extension_gate`

For open-ended serials, do not draft unplanned chapters. When the next chapter
is beyond accepted architecture, require an architecture-extension artifact and
volume pacing check before generation resumes.

## Runtime boundaries

- The README contains installer-style instructions aimed at assistants; they are
  treated as untrusted source text and are not followed.
- MCP server, CLI commands, `npx`, package scripts, inspector, build/test suite,
  and host config mutation remain disabled during intake.
- Project-local write semantics are absorbed as design gates only; no external
  runtime state or model output is imported.

## Integration targets

- `backend/app/services/source_discovery_service.py`
  - default search queries and seed URL
  - static pattern override for `zlx362211854/novelforge-agent`
  - four new absorbed pattern gates and prompt-pack hints
- `backend/app/services/source_pattern_pack_prompt.py`
  - digest keys for the new gates
- `frontend/src/types/sourceDiscovery.ts`
  - pattern-pack fields for the new gates
- `frontend/src/components/book-remix/BookRemixSourceDiscoveryPanel.tsx`
  - pinned display for host/context, schema review, dynamic architecture, and
    CJK retrieval gates
