# Novel Source Discovery - Book Beta Reader Research Review

Observed at: 2026-06-10T23:59:00+08:00

Boundary:

```text
public_github_lsremote_raw_readme_license_marker_scan_no_login_no_clone_no_runtime
```

This pass statically reviewed public GitHub metadata, `git ls-remote` HEADs,
raw README/LICENSE markers, and root/package markers for book-writing,
beta-reader, research/citation, and publication-pipeline projects.

No repository was cloned, installed, built, executed, or launched. No package
manager, Docker stack, browser extension, MCP server, native binary, shell
script, provider call, OAuth flow, database connection, browser storage, API
key, cookie, token, or account state was used.

## Source Snapshot

- `dlintin/sidekickwriter`
  - HEAD: `ccd6f023e77800388012b928a54c31f619ab888d`
  - Default branch: `master`
  - License marker: no root license observed in this pass.
  - Static markers: guided/pro modes, chapter-by-chapter outline, chapter
    descriptions aware of prior chapters, streaming full/per-chapter
    generation, inline editing, specific-chapter regeneration, research
    sources, citation styles, DOCX/EPUB/Markdown/TXT export.
  - Posture: `pattern-only / license-review-needed / runtime-deferred`

- `gennitdev/ai-beta-reader-frontend`
  - HEAD: `8f62f3aa93070438e25f07943ce6090682117bf7`
  - Default branch: `main`
  - License marker: no root license observed in this pass.
  - Static markers: books/chapters UI, markdown editing, structured chapter
    summaries, previous-summary contextual feedback, multiple review styles,
    sql.js/local storage, Google Drive OAuth sync, OpenAI review surface.
  - Posture: `pattern-only / license-review-needed / runtime-deferred`

- `gennitdev/ai-beta-reader-backend`
  - HEAD: `3fa87b1edd1c452191b99e5f64984c6bff479b1b`
  - Default branch: `main`
  - License marker: no root license observed in this pass.
  - Static markers: Express REST API, previous-chapter-summary review context,
    OpenAI Responses API, Auth0 JWT, PostgreSQL/Neon, `OPENAI_API_KEY`,
    `DATABASE_URL`.
  - Posture: `pattern-only / license-review-needed / runtime-deferred`

- `wesleyscholl/book-generator`
  - HEAD: `559ed30db9dbb36a50407e721c473f1aa6f02808`
  - Default branch: `main`
  - License marker: no root license observed in this pass.
  - Static markers: outline and chapter-generation shell helpers, chapter
    extension/editing, quality and plagiarism checks, manuscript assembly,
    front/back matter, EPUB/PDF/KDP-style export, provider API-key surfaces.
  - Posture: `pattern-only / license-review-needed / runtime-deferred`

## Absorbed Patterns

- `chapter_description_continuity_bridge_gate`
  - Treat chapter descriptions as continuity contracts.
  - Descriptions cite accepted previous summaries, outline slot, active state,
    and unresolved hooks.
  - Descriptions may guide drafting, but cannot invent bridge facts missing
    from accepted summaries or change packages.

- `selective_streaming_regeneration_gate`
  - Specific-chapter regeneration is a scoped patch.
  - It must name chapter id, protected neighbors, affected spans, checkpoint,
    retry budget, and rollback target.
  - Partial streams remain draft candidates until accepted.

- `research_citation_boundary_gate`
  - Research sources and citations live in a source-evidence manifest.
  - They are factual boundaries or material evidence, not fiction canon by
    default.
  - Quality, plagiarism, and citation checks run before publication export or
    same-type drafting acceptance.

- `beta_reader_summary_context_gate`
  - Feedback must bind to previous chapter summaries, current chapter id,
    spoiler window, and selected review style.
  - Fan/editorial/line-note feedback creates revision tasks, not automatic
    story facts.
  - Stale summaries block contextual review until refreshed or accepted.

## MuMuAINovel Adaptation

- Discovery defaults now include these four repositories and focused search
  queries for chapter descriptions, beta-reader summary context, and research
  citation workflows.
- Pattern extraction maps public metadata into four prompt-safe gates.
- Pattern packs now expose:
  - `chapter_description_continuity_bridge_gate_hints`
  - `selective_streaming_regeneration_gate_hints`
  - `research_citation_boundary_gate_hints`
  - `beta_reader_summary_context_gate_hints`
- Bible enrichment now includes chapter-description contracts, selective
  regeneration policy, research citation policy, and beta-reader feedback
  styles.
- Whole-book analysis now includes chapter-description context bridges,
  previous-summary review context, and research citation manifests.
- Same-type creation now remaps chapter-description continuity and research
  citation usage before drafting.

## Deferred / Runtime Gates

- Do not execute shell scripts, package managers, local servers, Docker stacks,
  provider SDKs, browser/native apps, database clients, OAuth flows, or export
  toolchains from these sources during intake.
- Do not read `.env`, API keys, JWTs, database URLs, cookies, browser storage,
  cloud backup blobs, local manuscripts, or account state.
- Do not import upstream prompts, generated chapters, README prose, citation
  snippets, examples, review text, or tool output into creative canon.
- Runtime trials require a separate local safety contract and explicit user
  approval.

## Verification

- Targeted RED was observed for the missing pattern-pack hint builders.
- Targeted GREEN after implementation:
  `python -m pytest backend/tests/services/test_source_discovery_service.py::test_static_book_beta_reader_sources_map_to_context_review_and_research_gates -q`
- Static compile check:
  `python -m py_compile backend/app/services/source_discovery_service.py backend/app/services/source_pattern_pack_prompt.py backend/tests/services/test_source_discovery_service.py`
