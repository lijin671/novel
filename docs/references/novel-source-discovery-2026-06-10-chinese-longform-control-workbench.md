# Novel Source Discovery - 2026-06-10 Chinese Longform Control Workbench

## Scope

Static source-intake pass for Chinese long-form writing workbench patterns that
can improve MuMuAINovel's source-book continuation, same-type original writing,
chapter revision, and long-run canon control.

This pass used only public GitHub metadata, reachable HEAD checks, and small
README/LICENSE/package metadata probes. No repository was cloned, installed, or
executed.

## Safety boundary

- Posture: `pattern-only` for every source in this pass.
- No package manager, app server, worker, Streamlit service, vector database,
  MCP server, browser extension, Docker stack, skill runtime, marathon script,
  or model/provider call was launched.
- Missing or unclear license surfaces stay as metadata/trust-review flags.
- Runtime trials require a separate local safety contract covering file scope,
  provider calls, secrets, network, cleanup, rollback, and verification.

## Source snapshot

- [PenglongHuang/chinese-novelist-skill](https://github.com/PenglongHuang/chinese-novelist-skill)
  - HEAD: `eb1185649437f2aaaa765f02be024132ea83d82d`
  - License surface: README badge says MIT; root LICENSE was not confirmed in this pass.
  - Prior absorbed value: preference memory, interrupted continuation,
    bounded validation/rewrite, conflict-driven chapters, and anti-AI polish.

- [WENZIZZHENG/story-spec](https://github.com/WENZIZZHENG/story-spec)
  - HEAD: `3cc23add07a929c628a4d71c5df56cdde2cce309`
  - License surface: MIT.
  - Absorbed value: candidate-not-canon, preview/confirm/apply, rollback, and
    author decision records.

- [KKKenChow/ai-novel-writer](https://github.com/KKKenChow/ai-novel-writer)
  - HEAD: `7900b751c29e09f03a230f0fe4ebead09b3896ff`
  - License surface: MIT.
  - Absorbed value: staged Chinese novel workflow, spoiler filtering,
    future-chapter range validation, relationship graphs, global replacement,
    and consistency checks.

- [papysans/Morpheus](https://github.com/papysans/Morpheus)
  - HEAD: `234c238a9a92d1bbd6499f9b03fea9f34b134f6d`
  - License surface: no root license observed.
  - Absorbed value: trace replay, chapter workbench rewrites, memory layers,
    context packs, review dashboard, and downstream impact review.

- [jingtai123/Novel-Control-Station-Skill](https://github.com/jingtai123/Novel-Control-Station-Skill)
  - HEAD: `68d14aa6137efe60f93a4c87a0eccef8c654464b`
  - License surface: MIT.
  - Absorbed value: chapter control cards, dynamic state write-back,
    document-driven truth layer, title/hook control, and continuation scripts
    as non-executed pattern references.

- [xindoo/sumeru](https://github.com/xindoo/sumeru)
  - HEAD: `2f3a692a12b0f2fe1cb8896b99c04fe01004a818`
  - License surface: no root license observed.
  - Absorbed value: webnovel skill workflow, continuation/rewrite, batch review,
    final validation, interrupted resume, and intermediate state discipline.

- [AI-Practical-Lab/ai-novel](https://github.com/AI-Practical-Lab/ai-novel)
  - HEAD: `9c47d035d32e0d5e5bf133aff0074ba81f4761a0`
  - License surface: MIT.
  - Absorbed value: structured world/character/outline/chapter management,
    smart context from previous chapters and setting collections, and local data
    boundaries.

## Absorbed patterns

### `author_candidate_canon_confirmation_gate`

AI suggestions, source-derived ideas, candidate outlines, and scene cards remain
non-canon until the system records preview, confirmation, apply status, decision
reason, and rollback path.

For MuMuAINovel:

- continuation prompts can use only confirmed canon or explicit craft notes
- same-type creation must transform candidates before acceptance
- unconfirmed candidates cannot silently enter bible, plan, chapter prompts, or
  memory packs

### `progressive_spoiler_context_window_gate`

Context selection must follow the current story stage. Early chapters should not
receive late-source spoilers, ending facts, or future payoff wording.

Track per chapter:

- allowed chapter range
- spoiler level
- future-context count
- range-validation findings
- rejected future-context items

### `chapter_control_card_writeback_gate`

Before drafting, each chapter needs a control card that states what must change,
which line advances, what debt returns, the conflict, title intent, and ending
hook.

After acceptance, write back:

- event deltas
- character and relationship deltas
- foreshadow and world-rule deltas
- emotional debt changes
- next-chapter pressure

### `trace_replay_revision_workspace_gate`

Chapter rewrites should preserve the selected context, blueprint, rewrite
direction, review findings, impact scope, and accepted text version.

When later chapters already exist, a rewrite must record downstream consistency
risk before canon write-back.

### `relationship_graph_global_replace_gate`

Relationship graphs are derived review surfaces, not independent canon.

Global replacement must preview affected bible, outline, chapter, vector-memory,
and graph entries before acceptance, then run consistency checks.

## MuMuAINovel integration

Updated artifacts:

- `backend/app/services/source_discovery_service.py`
- `backend/app/services/source_pattern_pack_prompt.py`
- `backend/app/services/book_remix_context_service.py`
- `backend/app/references/novel-source-pattern-pack-2026-06-10.json`
- `backend/tests/services/test_source_discovery_service.py`
- `backend/tests/services/test_book_remix_context_service.py`

Pattern pack refresh:

- generated_at: `2026-06-10T21:40:00+08:00`
- source_candidate_count: 207
- workflow_patterns: 221

## Verification

Targeted verification added for:

- classification of the Chinese long-form control projects
- pattern-pack bible targets, whole-book targets, hints, digest rendering, and
  same-type remap guidance
- continuation and inspired context blocks rendering the control audit section
- default repository URLs and GitHub discovery queries
