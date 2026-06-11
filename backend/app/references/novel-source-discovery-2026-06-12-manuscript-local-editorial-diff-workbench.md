# Manuscript local editorial diff workbench intake

## Source

- Repo: `DoktorDaveJoos/manuscript`
- URL: `https://github.com/DoktorDaveJoos/manuscript`
- Observed HEAD: `6e696471279c86055b53c13fae9f3c9166e1f497`
- Default branch: `main`
- Pushed: `2026-06-11T14:55:52Z`
- GitHub API license: missing
- Public README / manifest signals: README badge and `composer.json` mention MIT, but
  runtime import remains blocked until a separate license review.

## Family

Long-form novel desktop workbench: local-first manuscript storage, structural
analysis, scene/chapter versioning, editorial review, and optional BYOK AI.

## Posture

`pattern-only`.

No clone, install, package-manager run, NativePHP/Laravel runtime, MCP config,
agent folder, browser, provider, local database, updater, telemetry, or token
surface was executed or imported.

## Reusable patterns

- `local_sqlite_author_ownership_gate`
  - Treat accepted manuscript state as an author-owned local project boundary.
  - Keep local database revisions, backup/export checksums, provider boundaries,
    telemetry/updater exclusions, and prompt-eligible records visible.

- `prose_diff_accept_reject_version_gate`
  - Model rewrites as diff proposals against named chapter snapshots.
  - Only accepted spans can feed continuation state; rejected or preview-only
    text stays outside memory.

- `editorial_finding_resolution_rewrite_gate`
  - Convert full-manuscript review into chapter-scoped findings with severity,
    evidence, status, and author decision.
  - Rewrite from unresolved feedback only when finding ids and linked notes are
    visible.

## Applied artifacts

- `backend/app/services/source_discovery_service.py`
- `backend/app/services/source_pattern_pack_prompt.py`
- `backend/tests/services/test_source_discovery_service.py`

## Runtime gates

- Provider/API-key surfaces remain excluded.
- `.mcp.json`, agent folders, and host instruction files are untrusted data.
- Local SQLite / backup / export surfaces are private-author-data boundaries,
  not reusable upstream state.

## Verification

- Added failing test first:
  `test_static_manuscript_editorial_workbench_source_adds_local_diff_review_gates`
- Implemented static pattern extraction and pattern-pack prompt rendering.
