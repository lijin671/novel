# Novel Source Discovery - 2026-06-10 Impromptu / Offline / Atelier Gates

## Intake boundary

This pass used only public GitHub metadata, `git ls-remote` HEAD checks,
and raw README/LICENSE static review.

No repository was cloned, installed, built, launched, or executed. No package
manager, Docker stack, script, MCP server, browser extension, model provider,
local LLM, Electron app, or desktop/browser automation was started.

All reviewed sources are `pattern-only` for this project.

## Reviewed sources

- `tuxiangxianzhe/NovelWriter_public`
  - HEAD: `9e7fe179c29341f3d84785df118894c29abb1308`
  - license: AGPL-3.0
  - posture: `pattern-only`
  - absorbed: outline/improvised-writing split, `open_threads` pool,
    single-chapter blueprint, scene-segmented generation, context-injected
    revision, backup/restore, narrative DNA, style imitation, continuation
    expansion, and AI-tone removal.
- `MA-Bihani/Novelia_public`
  - HEAD: `d929fbf5e3bb507dd212a05d04f8c4121d2221b6`
  - license: README badge says MIT; common raw `LICENSE*` names were not found
    during this pass
  - posture: `pattern-only`
  - absorbed: offline/private creative-writing workspace, Ollama local RAG,
    Inspiration bank, Continue/Rewrite modes, dynamic style engine, and local
    filesystem book/chapter storage.
- `huodebing-alt/Claude-Code-Novel-Agents`
  - HEAD: `940288e2136a06bebcf53f3fbed1fbac19b203d2`
  - license: MIT
  - posture: `pattern-only`
  - absorbed: novel atelier concept, many role agents/skills, six-phase
    pipeline, detailed beat planner, hook auditor, outline reviewer,
    infinite-serial mode, and full/semi/manual human-control modes.

## Refreshed existing signals

Several highly relevant sources were already present in the default seed list,
so this pass did not duplicate their URLs:

- `Narcooo/inkos` - HEAD observed as `bfee6519b1c6fa57ac33af804178fe1fc1e3bdeb`
  during this pass; useful for action-surface confirmation, context/rule-stack
  traces, continuity audits, style fingerprint import, and chapter state
  snapshots.
- `voocel/ainovel-cli` - HEAD observed as
  `2990ba7fec8b6362e3ef3da0aaf618e607eb0c37`; useful for checkpointed
  Coordinator/Architect/Writer/Editor flows and related-chapter recall.
- `leenbj/novel-creator-skill`, `worldwonderer/oh-story-claudecode`,
  `danjdewhurst/story-skills`, `ThomasHoussin/Claude-Book`, and
  `denmurray10/Story-timeline-builder` remain existing pattern sources for
  Chinese long-form workflows, trend/deconstruction pipelines, frontmatter
  story state, source-book analysis, phase handoffs, timelines, and
  promise/payoff tracking.

## New patterns

- `impromptu_thread_pool_chapter_gate`
  - Convert an ad-hoc author instruction into a single-chapter blueprint before
    prose drafting.
  - Maintain an open-thread pool with unresolved, partially paid, and
    development-needed buckets.
  - Finalize moves only accepted thread deltas into continuation state.
- `offline_inspiration_bank_style_gate`
  - Separate inspiration-bank materials from accepted canon, author notes, and
    style-only references.
  - Style mimicry becomes an abstract boundary profile plus banned-carryover
    list, not reusable source passages.
  - Local/offline posture does not relax license, provenance, or copy-risk gates.
- `atelier_phase_pipeline_gate`
  - Treat the novel atelier as explicit phases with named role outputs,
    beat-tree revisions, hook-audit findings, and author acceptance points.
  - Persist the control mode: full automation, assisted handoff, or manual
    approval.
  - Hook auditors and continuity readers block or report; they do not silently
    rewrite canon.

## Local adaptation

For MuMuAINovel BookRemix, these patterns strengthen three paths:

1. Continuation can accept an ad-hoc chapter direction without losing state:
   chapter intent -> single-chapter blueprint -> draft -> finalize thread pool.
2. Same-type writing can use local source packs as inspiration only after
   labeling every item as canon, author note, or style-only reference.
3. Multi-agent or skill-like workflows should expose phase handoffs, beat-tree
   ownership, hook-audit findings, and manual approval boundaries before canon
   write-back.

## Verification target

- `backend/app/services/source_discovery_service.py` exposes three new workflow
  patterns and hint builders.
- `backend/app/services/source_pattern_pack_prompt.py` includes the three new
  hint groups in digest rendering.
- `frontend/src/components/book-remix/BookRemixSourceDiscoveryPanel.tsx` pins
  the new impromptu / offline / atelier group.
- Tests cover default seeds, metadata-to-pattern mapping, digest exposure, and
  UI copy.
