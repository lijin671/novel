# Novel source discovery - 2026-06-10 fresh-context agent pipeline

This note records a static-only source-intake pass for MuMuAINovel book
deconstruction, continuation, and same-type inspired writing.

No repository was cloned, installed, or executed. Review used public GitHub
metadata, reachable `HEAD`, root file names, README, and license-file checks
only.

## Sources

| Source | Observed HEAD | License file | Posture | Absorbed value |
|---|---|---|---|---|
| `dorakingx/novelpilot` | `56722ab3cda363853bd981ff2d010e089f7726b7` | no license file observed | `pattern-only` | nine-agent story pipeline, typed JSON outputs, Story Bible, Foreshadowing Tracker, Continuity Detective, reader/export bundle |
| `heaversm/ralph-storywriter` | `a1634c3640a79d243484d90a7575fc008d004f5e` | no license file observed | `pattern-only` | fresh-context chapter loop, `prd.json` next-incomplete detection, `STORY_BIBLE.md`, `progress.txt`, Plan -> Write -> Review -> Revise |
| `Anshler/graphify-novel` | not reachable | n/a | `defer` | GitHub returned repository-not-found during public metadata and `git ls-remote` checks |

## Reusable patterns

- `fresh_context_chapter_iteration_gate`
  - Each chapter pass should start from a file-backed packet:
    story bible, chapter manifest, progress log, previous accepted chapter, and
    explicit next-chapter brief.
  - The next incomplete chapter is detected from the manifest before writing.
    Chat history is not an authority for completion state.
  - Progress and chapter status are updated only after review/revise accepts
    text into canon.

- Existing pattern reuse from `novelpilot`
  - `craft_role_pipeline`: split premise, cast, world, plot, chapter, prose,
    style, continuity, and publish roles.
  - `setup_payoff_tracking`: treat foreshadowing tracker entries as setup/payoff
    evidence, not prose instructions.
  - `canon_drift_continuity_qa_gate`: continuity detective findings become
    review evidence before acceptance.
  - `structured_generation_schema`: typed JSON outputs are useful for
    inspectable handoffs.

## Local adaptation

- Added default GitHub Search queries for:
  - `nine-agent pipeline`, `Continuity Detective`, `Foreshadowing Tracker`
  - `fresh context`, `no memory fatigue`, `next incomplete chapter`,
    `progress.txt`
- Added `dorakingx/novelpilot` and `heaversm/ralph-storywriter` as default
  repository seeds.
- Added fresh-context chapter iteration hints to the source discovery pattern
  pack and frontend panel.

## Runtime exclusions

- `novelpilot` is a Next.js/provider-backed app; do not run the app or call
  providers during intake.
- `ralph-storywriter` ships shell scripts and assumes Claude Code
  authentication; do not execute scripts or authenticate providers during
  intake.
- Missing license files keep both sources pattern-only unless a future review
  establishes usable license terms for code reuse.

## Verification

- Backend pattern mapping test:
  `test_fresh_context_story_pipeline_sources_feed_prompt_pack`
- Frontend copy/type coverage:
  `test_source_discovery_panel_surfaces_inspired_pattern_pack_fields`
