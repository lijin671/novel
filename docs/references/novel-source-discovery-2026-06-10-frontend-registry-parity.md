# Novel Source Discovery - Frontend Registry Parity - 2026-06-10

## Scope

This note records a static intake maintenance pass for the MuMuAINovel book-remix source discovery surface.

The backend source discovery registry already carried a larger GitHub seed set than the frontend textarea default. The frontend now mirrors the backend `DEFAULT_GITHUB_REPOSITORY_URLS` list so a manual refresh starts from the same public GitHub source universe that the service uses.

## Source family

- Family: novel automation source discovery / book-remix source intake.
- Posture: pattern-only and metadata-only.
- Primary local source of truth: `backend/app/services/source_discovery_service.py`.
- Frontend surface: `frontend/src/components/book-remix/BookRemixSourceDiscoveryPanel.tsx`.

## Patterns promoted

- Registry parity gate: frontend default GitHub seeds must match the backend registry exactly.
- Core remix kernel surfacing: foundational hints are now pinned instead of falling through the dynamic catch-all.
- Dynamic fallback preservation: newly discovered `_hints` fields still appear under the additional source-discovered gate list when not explicitly pinned.

## Runtime boundary

No repository was cloned, installed, executed, or imported.

No package manager, Docker stack, MCP server, browser extension, provider call, or external writing runtime was launched.

The change only exposes already-recorded public GitHub metadata seeds and pattern-pack hint fields in the local project UI.

## Verification targets

- Frontend seed registry equals backend `DEFAULT_GITHUB_REPOSITORY_URLS`.
- Core remix hint fields exist in both TypeScript type definitions and the panel copy.
- Dynamic fallback still retains enough unpinned hint coverage for future intake.

## API hydration addendum - 2026-06-10

The latest-artifact endpoint now returns `default_github_repository_urls` from the backend registry. The frontend hydrates its seed textarea from that backend value while preserving manual user edits after the user changes the textarea.

This keeps the backend registry as the authoritative runtime default for future GitHub intake refreshes. The frontend static list remains only as a local fallback before the latest-artifact response arrives.

## Query/RSS hydration addendum - 2026-06-10

The latest-artifact endpoint also returns `default_github_queries` and `default_linux_do_rss_urls`. The frontend now exposes both as editable source-discovery inputs.

GitHub Search queries are newline-delimited because valid GitHub qualifiers such as `in:name,description,readme` contain commas. RSS URLs keep the URL parser path and can be split by newline or comma.

Runtime boundary remains unchanged: these fields are discovery metadata controls only. They do not authorize cloning, package installation, script execution, provider calls, browser control, login bypass, or reading private feeds.
