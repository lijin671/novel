# Novel Source Discovery - Author Control / Webnovel Handbook Gates - 2026-06-10

## Scope

Static source-intake pass for public GitHub repositories that can improve
MuMuAINovel's ???? and ????? flow.

Boundary: public metadata, reachable HEAD, README markers, root-file/license
surface only. No clone, no install, no package manager, no provider call, no
MCP/browser/desktop runtime, no scripts, and no private data.

## Reviewed sources

- `fopearcano/storyplanner`
  - HEAD: `80440fda504578d0292c89504640f1b41bf05f06`
  - License: no license file observed through public license endpoint
  - Posture: pattern-only
  - Reusable value: narrative engines for Novel/Screenplay/Stage/Graphic Novel,
    PSYKE Story Bible, Story Grid, Multi-Plot, timeline, motif/causality and
    continuity graph, and propose-then-confirm assistant actions.

- `giapnguyen74/xnovelist`
  - HEAD: `7abd8c1252fdf65120feeef3c977fc3283c08bfc`
  - License: MIT
  - Posture: pattern-only
  - Reusable value: local-first manuscript ownership, AI off by default,
    workspace-level AI authority ceiling, Story Bible entity capture,
    automatic snapshots, line-level diff, and draft-awaiting-review boundary.

- `waylean/plotrail`
  - HEAD: `93e2a45e4986741e5ef67ccb5e2ef96f604efa40`
  - License: MIT
  - Posture: pattern-only
  - Reusable value: canon-aware long-form fiction skill with approved chapter
    contracts, canon files, drafts/reviews/research folders, memory ledgers,
    story bible before drafting, and continuity review on every chapter.

- `XINGANLIU/web-novel-writing-skill`
  - HEAD: `73920a45ad51bc0399553b87132657b55bd3f65c`
  - License: MIT
  - Posture: pattern-only
  - Reusable value: Chinese web-novel workflow with 10-stage pipeline, expert
    roles, anti-hallucination layers, state-sync memory, golden-three-chapters
    strategy, and anti-AI-pattern quality gates.

- `miserylee/webnovel-handbook`
  - HEAD: `acc3f7f2bc676f441ba6ac6d77a5b3fea8daac0f`
  - License: MIT
  - Posture: pattern-only
  - Reusable value: agent-readable Chinese webnovel handbook. The retained
    lesson is not to load the whole knowledge base; route through README,
    AGENTS, `docs/00-index.md`, then task-specific drafting, beta review,
    review, and revision workflows.

- `ungden/truyencity2`
  - HEAD: `376c3f8df60c3ac7222cde715c879f6f2fb7c56b`
  - License: Apache-2.0
  - Posture: pattern-only / runtime-deferred
  - Reusable value: Story Engine v2 long-serial architecture with canon, plan,
    state, memory, quality, context, and pipeline layers; 1000-chapter Story
    Factory workflow; genre state trackers; batch/autopilot and prompt-cache
    cost boundary vocabulary.

## Absorbed patterns

- `author_candidate_canon_confirmation_gate`
  - AI suggestions, scene cards, and style alternatives stay candidates until
    previewed, confirmed, and applied.
  - Same-type drafts must use a new transformed canon and cannot inherit source
    workspace levels, progress status, or draft-acceptance state.

- `local_first_novel_workspace` / `review_queue_staging`
  - Treat local manuscript ownership, snapshots, line-level diff, and
    accept/edit/reject queues as core author-control surfaces.

- `story_contract_commit_chain` / `canon_drift_continuity_qa_gate`
  - Continuation should draft from approved chapter contracts and block chapter
    acceptance on continuity drift.

- `progressive_disclosure_skill_protocol_gate`
  - Handbook-style knowledge should be routed by task. Do not bulk-load an
    entire external writing handbook into prompts.

- `webnovel_genre_tracker_gate` / `multi_book_autopilot_studio_gate`
  - Long serials need explicit genre trackers, stop conditions, and periodic
    full-book checks before any unattended continuation loop.

- `provider_budget_smoke_gate`
  - Prompt cache and longrun cost claims remain planning vocabulary only unless
    a local provider-runtime safety contract exists.

## Local implementation

- Added the six reviewed repositories to backend default source-discovery seeds.
- Added targeted GitHub Search queries for AI authority ceilings, chapter
  contracts, webnovel handbooks, PSYKE story bible, and 1000-chapter Story
  Engine signals.
- Extended existing pattern keywords instead of creating a duplicate global
  route.
- Added static source summaries so prompt packs can classify these projects
  without cloning or running them.
- Added regression coverage for the new repository defaults and mapped gates.

## Runtime exclusions

- No external code, AGENTS/CLAUDE/plugin content, skill files, package scripts,
  Supabase/edge functions, local APIs, provider calls, or handbook bodies were
  imported or executed.
- License clarity affects code reuse only. This pass imports no code, so the
  retained artifacts are pattern-only summaries and project-native tests.
