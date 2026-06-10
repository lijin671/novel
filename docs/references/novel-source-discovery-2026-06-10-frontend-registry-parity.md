# Novel Source Discovery - Frontend Registry Parity - 2026-06-10

## Scope

This note records a static intake maintenance pass for the MuMuAINovel book-remix source discovery surface.

The backend source discovery registry is the source of truth for GitHub seeds. The frontend keeps only a compact local fallback and hydrates the full editable seed list from the latest-artifact API when available.

## Source family

- Family: novel automation source discovery / book-remix source intake.
- Posture: pattern-only and metadata-only.
- Primary local source of truth: `backend/app/services/source_discovery_service.py`.
- Frontend surface: `frontend/src/components/book-remix/BookRemixSourceDiscoveryPanel.tsx`.

## Patterns promoted

- Server-authoritative registry gate: frontend defaults must hydrate from backend registry fields instead of duplicating the full seed list.
- Core remix kernel surfacing: foundational hints are now pinned instead of falling through the dynamic catch-all.
- Dynamic fallback preservation: newly discovered `_hints` fields still appear under the additional source-discovered gate list when not explicitly pinned.

## Runtime boundary

No repository was cloned, installed, executed, or imported.

No package manager, Docker stack, MCP server, browser extension, provider call, or external writing runtime was launched.

The change only exposes already-recorded public GitHub metadata seeds and pattern-pack hint fields in the local project UI.

## Verification targets

- Frontend static fallback remains compact while backend service tests cover representative `DEFAULT_GITHUB_REPOSITORY_URLS` entries.
- Core remix hint fields exist in both TypeScript type definitions and the panel copy.
- Dynamic fallback still retains enough unpinned hint coverage for future intake.

## API hydration addendum - 2026-06-10

The latest-artifact endpoint now returns `default_github_repository_urls` from the backend registry. The frontend hydrates its seed textarea from that backend value while preserving manual user edits after the user changes the textarea.

This keeps the backend registry as the authoritative runtime default for future GitHub intake refreshes. The frontend static list remains only as a local fallback before the latest-artifact response arrives.

## Query/RSS hydration addendum - 2026-06-10

The latest-artifact endpoint also returns `default_github_queries` and `default_linux_do_rss_urls`. The frontend now exposes both as editable source-discovery inputs.

GitHub Search queries are newline-delimited because valid GitHub qualifiers such as `in:name,description,readme` contain commas. RSS URLs keep the URL parser path and can be split by newline or comma.

Runtime boundary remains unchanged: these fields are discovery metadata controls only. They do not authorize cloning, package installation, script execution, provider calls, browser control, login bypass, or reading private feeds.


## Compact frontend fallback addendum - 2026-06-10

The backend `DEFAULT_GITHUB_REPOSITORY_URLS` registry is the authoritative seed list for source discovery. The frontend no longer duplicates the full registry into the bundle.

`BookRemixSourceDiscoveryPanel.tsx` now keeps only a compact static fallback with representative sources for AI novel tooling, workbench planning, BookNLP, long-form generation, and NarrativeQA. On load, `/api/source-discovery/latest` hydrates the textarea from `default_github_repository_urls`, `default_github_queries`, and `default_linux_do_rss_urls` when the user has not manually edited those fields.

This preserves the existing manual-edit boundary and avoids copying the full backend registry into the frontend artifact.

Runtime boundary remains unchanged: no clone, no install, no package hook, no Docker stack, no MCP server, no browser extension, no provider call, and no external project execution.
