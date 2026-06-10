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
