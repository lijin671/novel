# Novel Source Discovery 2026-06-14 — Slima MCP beta-reader file gate projection

## Source

- Repository: https://github.com/slima-ai/slima-mcp
- Static HEAD: `9bbaf6f30ac6f1ff36ca9fbf81035a9f6b72e042`
- Default branch: `main`
- License signal: MIT badge / public README marker
- Local static packet: `tmp/source-intake-slima-readme-20260614.md`
- Intake posture: pattern-only / runtime-deferred

## Static Evidence

The README describes an MCP server for the Slima AI Writing IDE for novel
authors. Static markers cover book management, file/folder structure, writing
statistics, read/edit/write/create/delete/append/search file tools, and AI beta
reader feedback from virtual reader personas.

The same README also exposes runtime and auth surfaces: local `npx slima-mcp@0`,
remote HTTP MCP, OAuth login, API token configuration, Cloudflare-hosted remote
sessions, and token/credential storage paths. Those are runtime surfaces, not
absorbed implementation.

## Absorbed Pattern

### `slima_book_mcp_beta_reader_file_gate`

For 拆书续写 and same-type 仿写, beta-reader feedback can be useful only when its
file scope and mutation custody are explicit:

```text
book_id
file_path
chapter_scope
allowed_read_search_scope
forbidden_write_delete_append_scope
persona
reader_lens
finding
severity
affected_chapter_or_span
suggested_action
review_state: proposed | accepted | dismissed
mutation_boundary
runtime_boundary
```

This gate blocks three failure modes:

1. treating external book files as implicitly writable project state
2. letting beta-reader notes silently mutate canon or progress records
3. reusing source-story reader findings as target-story facts in same-type writing

## MuMuAINovel Projection

- `book_remix_context_service.py`
  - Adds `book_file_scope_envelope` and `beta_reader_persona_feedback_custody`
    to continuation control axes when the Slima gate is active.
  - Adds `verify_beta_reader_feedback_review_state` to acceptance steps.
  - Renders a continuation context section for file scope, beta-reader feedback,
    mutation custody, current chapter/file boundary, and runtime exclusion.
  - Renders a same-type context section that allows source feedback to define
    review axes only; the target story must use fresh personas, target-owned
    files, and independent findings.

## Runtime Boundary

Do not run or install Slima runtime during static intake:

- no `npx`, `npm`, package install, postinstall, or MCP/server launch
- no hosted/remote MCP connection
- no OAuth login or API token creation
- no credential/token/cookie read
- no Cloudflare worker/session interaction
- no live book file read/write/edit/delete/append/search
- no generated beta-reader feedback import as canon

The absorbed value is the custody pattern, not Slima's runtime behavior or code.
