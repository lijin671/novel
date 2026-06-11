# Novel source discovery: versioned scene fact review pipeline

Date: 2026-06-11

## Source

- Repository: `hayrgpt-rgb/NovelForge-AI`
- URL: `https://github.com/hayrgpt-rgb/NovelForge-AI`
- Static posture: `pattern-only`
- License observed: no license file observed during raw-file review
- Reachable HEAD: `48c9bca5e62eefa2dd8365f4a2bf4564b94b546a`
- Default branch observed by `git ls-remote`: `main`

## Static evidence

Reviewed without clone, install, Docker, database, queue, provider call,
frontend/backend launch, `.env` read, or upstream prompt/agent import.

- `README.md`
  - `sha256=ea928e5be03d63c1dd66e8073931bd5c0bd541883e0df6e35cbe4e9158583b3e`
  - Public markers: durable long-form pipeline, story bible, outlines, scene
    cards, scene draft jobs, fact extraction, review, revision, memory update,
    export, version-safe traceable generation, continuity reports, Story State
    ledger, Canon dashboard, reference assets, provider key surface, Docker
    Compose, PostgreSQL, Redis, RQ.
- `AGENTS.md`
  - `sha256=52fab1714401ced92dae9dd4003780befdae15edfd29d1491f585e5b6156f330`
  - Public markers: generated text must not overwrite existing records,
    generation tasks must be traceable/failable/retryable, structured data and
    Pydantic validation are preferred, prompts stay in prompt folders, tests
    mock external APIs.
- `LICENSE`: 404
- `CLAUDE.md`: 404
- `package.json`: 404 at repository root

## Reusable patterns

- Drafting should be version-safe.
  Scene drafts, user edits, revisions, reports, and exports need separate
  lineage records. Acceptance should not overwrite prior versions.
- Fact extraction should require approval.
  Extracted facts become canon only after approve/reject review, memory chunk
  creation, and Story State ledger delta evidence.
- Retrieval should be focused and traceable.
  Draft/revision prompts should identify fact, memory, reference-asset, and
  state bundles rather than dumping broad context.
- Export readiness should be evidence-backed.
  Accepted-version export should depend on continuity reports, multi-pass
  editorial reports, canon dashboard blockers, progress metrics, and checksums.

## MuMuAINovel projection

Added pattern gate:

- `versioned_scene_fact_review_pipeline_gate`

Mapped targets:

- Bible enrichment:
  - `version_safe_scene_draft_policy`
  - `fact_approval_memory_update_policy`
  - `review_report_export_readiness_policy`
- Whole-book analysis:
  - `scene_version_lineage_report`
  - `fact_extraction_approval_report`
  - `memory_chunk_retrieval_trace`
  - `continuity_reviewreport_findings`
  - `canon_dashboard_export_readiness_report`
- Same-type creation:
  - `scene_version_lineage_remap`
  - `fact_memory_approval_remap`
  - `canon_dashboard_review_remap`

## Deferred/runtime gates

Do not import or run upstream:

- Docker Compose
- PostgreSQL / Redis / RQ services
- backend or frontend app runtime
- provider/model calls
- `.env` files or API keys
- upstream prompts, agents, or AGENTS instructions

Only the abstract version, fact-ledger, review-report, and export-readiness
structure is absorbed.
