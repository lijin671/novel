# Novel source discovery: state/current reviewer loop

Date: 2026-06-11

## Source

- Repository: `ThomasHoussin/Claude-Book`
- URL: `https://github.com/ThomasHoussin/Claude-Book`
- Static posture: `pattern-only`
- License observed: MIT
- Reachable HEAD: `3fdebbb576b1be6d123b48258d2310c5dff013c4`
- Default branch observed by `git ls-remote`: `main`

## Static evidence

Reviewed without clone, install, runtime launch, provider call, shell execution,
PowerShell execution, symlink mutation, or credential access.

- `README.md`
  - `sha256=4206c98e5fd4794d26ec6922ebe1a79c1f015d92c500e54b95c017da43454bee`
  - Public markers: book analyzer, bible merger, story ideator,
    perplexity improver, permanent bible, transient `state/current`,
    `state/template`, `state/chapter-NN`, timeline history, reviewer agents.
- `LICENSE`
  - `sha256=4cbc59e65760a377b69b3d3c78bae3843bed67c21979f53414da4e2f43a6d90b`
  - MIT text observed.
- `CLAUDE.md`
  - `sha256=f6c6263a69e3097f8e1e819f5df5341e073e7c3fdf8ceb6d5cccad2d28d3c739`
  - Public markers: orchestrator loads `state/current/situation.md`,
    delegates to planner and writer, then runs cliche/perplexity improvement,
    style lint, character review, continuity review, bounded repair loop, and
    state updater.
- `package.json`: 404
- `AGENTS.md`: 404

## Reusable patterns

- Split permanent bible from transient chapter state.
  Source-derived style, structure, characters, and universe rules stay stable;
  chapter-local situation and deltas live in a current-state packet.
- Treat every chapter as a state transition.
  A continuation turn needs input checksum, accepted chapter id, new snapshot,
  and timeline append evidence.
- Use specialized post-chapter reviewers.
  Cliche/perplexity, style, character, and continuity checks should produce
  distinct reports before text can be accepted.
- Bound repair loops.
  Failed reviews feed a limited repair pass instead of infinite regeneration or
  silent acceptance.

## MuMuAINovel projection

Added pattern gate:

- `state_current_reviewer_loop_gate`

Mapped targets:

- Bible enrichment:
  - `permanent_bible_transient_state_policy`
  - `state_current_chapter_snapshot_policy`
  - `post_chapter_reviewer_loop_policy`
- Whole-book analysis:
  - `state_current_continuity_report`
  - `chapter_snapshot_delta_report`
  - `perplexity_cliche_style_lint_report`
  - `character_continuity_reviewer_loop_report`
  - `timeline_history_append_report`
- Same-type creation:
  - `bible_state_boundary_remap`
  - `chapter_reviewer_loop_remap`
  - `timeline_snapshot_delta_remap`

## Deferred/runtime gates

Do not import or run upstream:

- Claude Code skills and agents
- `.claude` orchestration files
- PowerShell ebook build scripts
- symlink creation or mutation
- source-book analysis over private text
- provider/model calls

Only the abstract bible/state boundary and reviewer-loop structure is absorbed.
